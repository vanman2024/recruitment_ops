#!/usr/bin/env python3
"""
Stable webhook handler with comprehensive logging
"""

import os
import sys
from pathlib import Path
import logging

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/gotime2022/recruitment_ops/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    logger.info(f"Loading environment from: {env_path}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
                if key in ['ANTHROPIC_API_KEY', 'CATS_API_KEY']:
                    logger.info(f"✓ Loaded {key}: {value[:20]}...")

# Verify environment
if not os.getenv('ANTHROPIC_API_KEY'):
    logger.error("ANTHROPIC_API_KEY not found!")
    sys.exit(1)

# Now import FastAPI and create simple webhook
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import asyncio
from datetime import datetime

app = FastAPI()

# Import processors after environment is loaded
sys.path.insert(0, str(Path(__file__).parent))
from catsone.integration.cats_integration import CATSClient
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

# Initialize once
cats_client = CATSClient()
processor = IntelligentCandidateProcessor()

@app.post('/webhook/candidate')
async def handle_webhook(request: Request):
    """Handle CATS webhooks"""
    try:
        data = await request.json()
        logger.info(f"Received webhook: {json.dumps(data, indent=2)[:500]}...")
        
        # Get candidate ID
        candidate_id = data.get('candidate_id') or data.get('id')
        if not candidate_id:
            logger.error("No candidate ID in webhook")
            return JSONResponse({'error': 'No candidate ID'}, status_code=400)
        
        logger.info(f"Processing candidate {candidate_id}")
        
        # Check for questionnaire tag
        has_tag = await check_questionnaire_tag(candidate_id)
        
        if has_tag:
            logger.info(f"Questionnaire tag found! Processing candidate {candidate_id}")
            
            # Process in background
            asyncio.create_task(process_candidate_background(candidate_id))
            
            return JSONResponse({
                'status': 'processing',
                'candidate_id': candidate_id,
                'message': 'Processing questionnaire'
            })
        else:
            logger.info(f"No questionnaire tag for candidate {candidate_id}")
            return JSONResponse({
                'status': 'skipped',
                'candidate_id': candidate_id
            })
    
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return JSONResponse({'error': str(e)}, status_code=500)

async def check_questionnaire_tag(candidate_id):
    """Check if candidate has questionnaire completed tag"""
    try:
        import requests
        url = f"{cats_client.base_url}/candidates/{candidate_id}/tags"
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.get(url, headers=cats_client.headers)
        )
        
        if response.status_code == 200:
            data = response.json()
            tags = data.get('_embedded', {}).get('tags', [])
            
            for tag in tags:
                tag_title = tag.get('title', '').lower()
                if 'questionnaire completed' in tag_title:
                    logger.info(f"Found tag: {tag.get('title')}")
                    return True
        else:
            logger.error(f"Failed to get tags: {response.status_code}")
    except Exception as e:
        logger.error(f"Error checking tags: {e}")
    return False

async def process_candidate_background(candidate_id):
    """Process candidate in background"""
    try:
        logger.info(f"Background processing started for candidate {candidate_id}")
        
        # Get job ID
        job_id = await get_job_id(candidate_id)
        if not job_id:
            logger.error(f"No job ID found for candidate {candidate_id}")
            return
        
        logger.info(f"Processing candidate {candidate_id} for job {job_id}")
        
        # Process
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            processor.process_candidate_for_job,
            candidate_id,
            job_id
        )
        
        if result.get('success'):
            logger.info(f"✅ Successfully processed candidate {candidate_id}")
            logger.info(f"Notes updated: {len(result.get('notes', ''))} characters")
        else:
            logger.error(f"❌ Failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Background processing error: {e}", exc_info=True)

async def get_job_id(candidate_id):
    """Get job ID for candidate - try multiple methods"""
    try:
        import requests
        
        # Method 1: Check pipelines
        url = f"{cats_client.base_url}/candidates/{candidate_id}/pipelines"
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.get(url, headers=cats_client.headers)
        )
        
        if response.status_code == 200:
            data = response.json()
            pipelines = data.get('_embedded', {}).get('pipelines', [])
            if pipelines:
                job_id = pipelines[0].get('job_id')
                logger.info(f"Found job ID from pipeline: {job_id}")
                return job_id
        
        # Method 2: Check applications
        url = f"{cats_client.base_url}/candidates/{candidate_id}/applications"
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.get(url, headers=cats_client.headers)
        )
        
        if response.status_code == 200:
            data = response.json()
            applications = data.get('_embedded', {}).get('applications', [])
            if applications:
                job_id = applications[0].get('job_id')
                logger.info(f"Found job ID from applications: {job_id}")
                return job_id
        
        # Method 3: Check activities for job association
        url = f"{cats_client.base_url}/candidates/{candidate_id}/activities"
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.get(url, headers=cats_client.headers)
        )
        
        if response.status_code == 200:
            data = response.json()
            activities = data.get('_embedded', {}).get('activities', [])
            for activity in activities:
                if activity.get('job_id'):
                    job_id = activity['job_id']
                    logger.info(f"Found job ID from activities: {job_id}")
                    return job_id
        
        # Method 4: Use a default job ID if configured
        default_job = os.getenv('DEFAULT_JOB_ID', '16702578')
        logger.warning(f"No job ID found, using default: {default_job}")
        return default_job
        
    except Exception as e:
        logger.error(f"Error getting job ID: {e}")
    return None

@app.get('/webhook/test')
@app.post('/webhook/test')
async def test_webhook():
    """Test endpoint"""
    logger.info("Test endpoint called")
    return JSONResponse({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'env_loaded': bool(os.getenv('ANTHROPIC_API_KEY'))
    })

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting stable webhook handler...")
    logger.info(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")
    logger.info(f"CATS_API_KEY: {os.getenv('CATS_API_KEY')[:20]}...")
    uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info')