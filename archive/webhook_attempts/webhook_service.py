#!/usr/bin/env python3
"""
Reliable webhook service with proper environment handling
"""

import os
import sys
from pathlib import Path

# FIRST: Load environment variables BEFORE any other imports
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    print(f"Loading environment from: {env_path}")
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                if key == 'ANTHROPIC_API_KEY':
                    print(f"✓ Loaded {key}: {value[:20]}...")

# Verify we have the API key
if not os.getenv('ANTHROPIC_API_KEY') or 'your-api-key' in os.getenv('ANTHROPIC_API_KEY', ''):
    print("ERROR: Valid ANTHROPIC_API_KEY not found!")
    sys.exit(1)

# Now import and run the webhook handler
sys.path.append(str(Path(__file__).parent))

# Import FastAPI app directly
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import our processors
from catsone.integration.cats_integration import CATSClient
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients with verified environment
cats_client = CATSClient()
processor = IntelligentCandidateProcessor()

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

@app.post('/webhook/candidate')
async def handle_candidate_webhook(request: Request):
    """Handle candidate webhooks with tag detection"""
    try:
        data = await request.json()
        logger.info(f"Received webhook: {json.dumps(data, indent=2)}")
        
        candidate_id = data.get('candidate_id') or data.get('id')
        if not candidate_id:
            return JSONResponse({'error': 'No candidate ID found'}, status_code=400)
        
        # Check for questionnaire completed tag
        has_tag = await check_for_questionnaire_tag_async(candidate_id)
        
        if has_tag:
            logger.info(f"Questionnaire tag found for candidate {candidate_id}")
            
            # Process immediately in background
            asyncio.create_task(process_candidate_async(candidate_id))
            
            return JSONResponse({
                'status': 'processing',
                'candidate_id': candidate_id,
                'message': 'Processing questionnaire in background'
            })
        else:
            return JSONResponse({
                'status': 'skipped',
                'reason': 'No questionnaire completed tag found'
            })
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

async def check_for_questionnaire_tag_async(candidate_id):
    """Check for questionnaire tag asynchronously"""
    try:
        import requests
        url = f"{cats_client.base_url}/candidates/{candidate_id}/tags"
        response = await asyncio.get_event_loop().run_in_executor(
            executor, 
            lambda: requests.get(url, headers=cats_client.headers)
        )
        
        if response.status_code == 200:
            data = response.json()
            tags = data.get('_embedded', {}).get('tags', [])
            
            # Check for the specific tag
            target_tags = [
                'application status: questionnaire completed',
                'questionnaire completed'
            ]
            
            for tag in tags:
                tag_name = tag.get('title', '').lower()
                if any(target in tag_name for target in target_tags):
                    logger.info(f"Found questionnaire tag: {tag.get('title')}")
                    return True
        return False
    except Exception as e:
        logger.error(f"Error checking tags: {e}")
        return False

async def process_candidate_async(candidate_id):
    """Process candidate asynchronously for faster response"""
    try:
        logger.info(f"Starting async processing for candidate {candidate_id}")
        
        # Get job ID
        job_id = await get_candidate_job_id_async(candidate_id)
        
        if job_id:
            # Process in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                executor,
                processor.process_candidate_for_job,
                candidate_id,
                job_id
            )
            
            if result.get('success'):
                logger.info(f"✅ Successfully processed candidate {candidate_id}")
            else:
                logger.error(f"❌ Failed to process: {result.get('error')}")
        else:
            logger.warning(f"No job ID found for candidate {candidate_id}")
            
    except Exception as e:
        logger.error(f"Error in async processing: {e}")

async def get_candidate_job_id_async(candidate_id):
    """Get job ID asynchronously"""
    try:
        import requests
        url = f"{cats_client.base_url}/candidates/{candidate_id}/pipelines"
        response = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: requests.get(url, headers=cats_client.headers)
        )
        
        if response.status_code == 200:
            data = response.json()
            pipelines = data.get('_embedded', {}).get('pipelines', [])
            if pipelines:
                return pipelines[0].get('job_id')
    except Exception as e:
        logger.error(f"Error getting job ID: {e}")
    return None

@app.get('/webhook/test')
@app.post('/webhook/test')
async def test_webhook():
    """Test endpoint to verify webhook is working"""
    return JSONResponse({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'Webhook handler is running',
        'env_loaded': bool(os.getenv('ANTHROPIC_API_KEY'))
    })

if __name__ == "__main__":
    print("Starting webhook service with environment loaded...")
    print(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")
    print(f"CATS_API_KEY: {os.getenv('CATS_API_KEY')[:20]}...")
    
    port = int(os.getenv('WEBHOOK_PORT', 8080))
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')