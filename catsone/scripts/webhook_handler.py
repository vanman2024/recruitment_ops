#!/usr/bin/env python3
"""
Simple webhook handler for CATS events
Processes candidates when questionnaires are added or status changes
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import uvicorn

# CRITICAL: Force load environment variables
from pathlib import Path
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path, override=True)

# Verify critical environment variables
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_KEY or 'your-api-key' in ANTHROPIC_KEY:
    print("ERROR: No valid ANTHROPIC_API_KEY found in environment")
    print(f"Looking for .env at: {env_path}")
    sys.exit(1)
else:
    print(f"✓ Loaded ANTHROPIC_API_KEY: {ANTHROPIC_KEY[:20]}...")

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
cats_client = CATSClient()
processor = IntelligentCandidateProcessor()

@app.post('/webhook/candidate')
async def handle_candidate_webhook(request: Request):
    """Handle candidate.updated and candidate.created webhooks"""
    
    try:
        data = await request.json()
        logger.info(f"Received webhook: {json.dumps(data, indent=2)}")
        
        event_type = data.get('event')
        candidate_id = data.get('candidate_id') or data.get('id')
        
        if not candidate_id:
            return JSONResponse({'error': 'No candidate ID found'}, status_code=400)
        
        # Check if webhook is tag-related
        if 'tag' in str(data).lower() or 'tags' in data:
            logger.info("Tag-related webhook detected")
        
        # Check if candidate has questionnaire tag or attachment
        has_questionnaire_tag = check_for_questionnaire_tag(candidate_id)
        has_questionnaire = has_questionnaire_tag or check_for_questionnaire(candidate_id)
        
        if has_questionnaire:
            logger.info(f"Questionnaire found for candidate {candidate_id} (tag: {has_questionnaire_tag})")
            
            # Get job ID (might be in webhook data or need to fetch)
            job_id = data.get('job_id') or get_candidate_job_id(candidate_id)
            
            if job_id:
                # Process the candidate
                result = processor.process_candidate_for_job(candidate_id, job_id)
                
                if result.get('success'):
                    logger.info(f"Successfully processed candidate {candidate_id}")
                    return JSONResponse({
                        'status': 'success',
                        'candidate_id': candidate_id,
                        'message': 'Candidate processed successfully'
                    })
                else:
                    logger.error(f"Failed to process: {result.get('error')}")
                    return JSONResponse({
                        'status': 'error',
                        'error': result.get('error')
                    }, status_code=500)
            else:
                logger.warning(f"No job ID found for candidate {candidate_id}")
                return JSONResponse({
                    'status': 'skipped',
                    'reason': 'No job associated with candidate'
                })
        else:
            logger.info(f"No questionnaire found for candidate {candidate_id}")
            return JSONResponse({
                'status': 'skipped',
                'reason': 'No questionnaire attachment or tag found'
            })
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post('/webhook/pipeline')
async def handle_pipeline_webhook(request: Request):
    """Handle pipeline status changes"""
    
    try:
        data = await request.json()
        logger.info(f"Pipeline webhook: {json.dumps(data, indent=2)}")
        
        # Extract candidate and new status/list
        candidate_id = data.get('candidate_id')
        new_status = data.get('status') or data.get('stage')
        
        # Define which statuses trigger processing
        trigger_statuses = [
            'questionnaire_review',     # Primary trigger when questionnaire uploaded
            'questionnaire review',     # Handle with or without underscore
            'ready_for_review',
            'manager_review',
            'questionnaire_complete'
        ]
        
        # Check if status matches our triggers (case-insensitive)
        status_lower = new_status.lower() if new_status else ''
        trigger_statuses_lower = [s.lower() for s in trigger_statuses]
        
        if status_lower in trigger_statuses_lower:
            logger.info(f"Status '{new_status}' matches trigger - processing candidate {candidate_id}")
            
            # Check and process if has questionnaire
            if check_for_questionnaire(candidate_id):
                logger.info(f"Questionnaire found for candidate {candidate_id}")
                job_id = get_candidate_job_id(candidate_id)
                
                if job_id:
                    logger.info(f"Processing candidate {candidate_id} for job {job_id}")
                    result = processor.process_candidate_for_job(candidate_id, job_id)
                    
                    if result.get('success'):
                        logger.info(f"✅ Successfully processed candidate {candidate_id}")
                    else:
                        logger.error(f"❌ Failed to process candidate {candidate_id}: {result.get('error')}")
                    
                    return JSONResponse({
                        'status': 'processed' if result.get('success') else 'failed',
                        'candidate_id': candidate_id,
                        'message': result.get('notes', '') if result.get('success') else result.get('error')
                    })
                else:
                    logger.warning(f"No job ID found for candidate {candidate_id}")
                    return JSONResponse({
                        'status': 'error',
                        'message': 'No job associated with candidate'
                    })
            else:
                logger.info(f"No questionnaire found for candidate {candidate_id}")
                return JSONResponse({
                    'status': 'skipped',
                    'message': 'No questionnaire attachment found'
                })
        
        return JSONResponse({'status': 'no_action_needed'})
        
    except Exception as e:
        logger.error(f"Pipeline webhook error: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

def check_for_questionnaire(candidate_id):
    """Check if candidate has questionnaire attachment"""
    try:
        attachments = cats_client.get_candidate_attachments(candidate_id)
        
        for attachment in attachments:
            filename = attachment.get('filename', '').lower()
            # Check for "Recruiting - Dayforce" pattern
            if 'recruiting' in filename and 'dayforce' in filename:
                return True
            # Also check for other questionnaire patterns
            if any(keyword in filename for keyword in ['questionnaire', 'form', 'assessment']):
                return True
        return False
    except:
        return False

def check_for_questionnaire_tag(candidate_id):
    """Check if candidate has questionnaire-related tag"""
    try:
        # Tags are in a separate endpoint
        import requests
        url = f"{cats_client.base_url}/candidates/{candidate_id}/tags"
        response = requests.get(url, headers=cats_client.headers)
        
        if response.status_code == 200:
            data = response.json()
            tags = data.get('_embedded', {}).get('tags', [])
            
            # Check for questionnaire-related tags
            questionnaire_tags = [
                'questionnaire ready', 
                'has questionnaire', 
                'questionnaire uploaded',
                'application status: questionnaire completed',
                'questionnaire completed'
            ]
            
            for tag in tags:
                tag_name = tag.get('title', '').lower()
                # Check exact matches
                if tag_name in questionnaire_tags:
                    logger.info(f"Found questionnaire tag: {tag.get('title')}")
                    return True
                # Check partial matches
                if any(q_tag in tag_name for q_tag in questionnaire_tags):
                    logger.info(f"Found questionnaire tag: {tag.get('title')}")
                    return True
        return False
    except Exception as e:
        logger.error(f"Error checking tags: {e}")
        return False

def get_candidate_job_id(candidate_id):
    """Get job ID from candidate's applications"""
    try:
        # Check pipeline entries
        import requests
        url = f"{cats_client.base_url}/candidates/{candidate_id}/pipelines"
        response = requests.get(url, headers=cats_client.headers)
        
        if response.status_code == 200:
            data = response.json()
            pipelines = data.get('_embedded', {}).get('pipelines', [])
            if pipelines:
                # Return the first job ID found
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
        'message': 'Webhook handler is running'
    })

if __name__ == '__main__':
    port = int(os.getenv('WEBHOOK_PORT', 8080))
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')