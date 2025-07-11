#!/usr/bin/env python3
"""
Pipeline Status-based Webhook Handler
Triggers processing when candidates move to specific pipeline statuses
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse

# Load environment
load_dotenv('/home/gotime2022/recruitment_ops/.env')

# Add project to path
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('status_webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Define which status changes should trigger processing
TRIGGER_STATUSES = [
    "Questionnaire Completed",
    "Ready for Processing", 
    "Questionnaire Review",
    "Hiring Manager Approved",  # Use this as trigger since questionnaire status doesn't exist
    "Submitted to Hiring Manager"  # Or this one
]

def process_candidate_async(candidate_id: int, job_id: int, status: str):
    """Process candidate in background"""
    try:
        logger.info(f"Processing candidate {candidate_id} for job {job_id} (triggered by status: {status})")
        
        processor = IntelligentCandidateProcessor()
        result = processor.process_candidate_for_job(candidate_id, job_id)
        
        if result.get('success'):
            logger.info(f"✅ Successfully processed candidate {candidate_id}")
        else:
            logger.error(f"❌ Failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Error processing candidate {candidate_id}: {e}")

@app.post('/webhook/pipeline')
async def handle_pipeline_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle pipeline status change webhooks"""
    try:
        data = await request.json()
        
        logger.info(f"Received pipeline webhook: {json.dumps(data, indent=2)[:500]}...")
        
        # Extract event type and data
        event = data.get('event', '')
        
        if event != 'pipeline.status_changed':
            logger.info(f"Ignoring event type: {event}")
            return JSONResponse({'status': 'ignored', 'reason': 'not a status change'})
        
        # Get pipeline data
        pipeline_data = data.get('_embedded', {}).get('pipeline', {})
        if not pipeline_data:
            pipeline_data = data.get('pipeline', {})
        
        # Extract key information
        candidate_id = pipeline_data.get('candidate_id')
        job_id = pipeline_data.get('job_id')
        new_status = pipeline_data.get('status', {}).get('name', '')
        
        logger.info(f"Status change detected: Candidate {candidate_id}, Job {job_id}, New Status: '{new_status}'")
        
        # Check if this status should trigger processing
        if new_status in TRIGGER_STATUSES:
            logger.info(f"🎯 TRIGGER STATUS MATCHED: '{new_status}' - Processing candidate {candidate_id}")
            
            if candidate_id and job_id:
                # Process in background
                background_tasks.add_task(process_candidate_async, candidate_id, job_id, new_status)
                return JSONResponse({
                    'status': 'processing',
                    'candidate_id': candidate_id,
                    'job_id': job_id,
                    'triggered_by': new_status
                })
            else:
                logger.error(f"Missing required data: candidate_id={candidate_id}, job_id={job_id}")
                return JSONResponse({'status': 'error', 'reason': 'missing data'}, status_code=400)
        else:
            logger.info(f"Status '{new_status}' not in trigger list")
            return JSONResponse({
                'status': 'ignored',
                'reason': f"status '{new_status}' not configured for processing",
                'configured_statuses': TRIGGER_STATUSES
            })
            
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post('/webhook/activity')
async def handle_activity_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle activity webhooks (emails, notes, etc)"""
    try:
        data = await request.json()
        
        logger.info(f"Received activity webhook: {json.dumps(data, indent=2)[:500]}...")
        
        # Check if activity is related to questionnaire
        activity_data = data.get('_embedded', {}).get('activity', {})
        if not activity_data:
            activity_data = data.get('activity', {})
        
        activity_type = activity_data.get('type', '')
        activity_notes = activity_data.get('notes', '').lower()
        
        # Check for questionnaire-related activities
        if 'questionnaire' in activity_notes and 'completed' in activity_notes:
            candidate_id = activity_data.get('candidate_id')
            
            # Try to find job ID from activity
            job_id = activity_data.get('job_id')
            if not job_id:
                # Default to a known job
                job_id = 16702578
            
            logger.info(f"🎯 Questionnaire activity detected for candidate {candidate_id}")
            
            if candidate_id:
                background_tasks.add_task(process_candidate_async, candidate_id, job_id, "activity trigger")
                return JSONResponse({
                    'status': 'processing',
                    'candidate_id': candidate_id,
                    'triggered_by': 'questionnaire activity'
                })
        
        return JSONResponse({'status': 'ignored', 'reason': 'not questionnaire related'})
        
    except Exception as e:
        logger.error(f"Error handling activity webhook: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'time': datetime.now().isoformat(),
        'configured_statuses': TRIGGER_STATUSES
    }

@app.post('/webhook/test')
async def test_webhook():
    """Test endpoint"""
    logger.info("Test endpoint called")
    return {'status': 'ok', 'time': datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting status-based webhook handler...")
    logger.info(f"Configured trigger statuses: {TRIGGER_STATUSES}")
    logger.info(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")
    logger.info(f"CATS_API_KEY: {os.getenv('CATS_API_KEY')[:20]}...")
    
    uvicorn.run(app, host='0.0.0.0', port=8080)