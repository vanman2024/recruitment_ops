#!/usr/bin/env python3
"""
CATS Webhook Server for Candidate Processing (FastAPI version)
Handles webhook events when candidates enter "manager review needed" status
"""

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime
import os
from typing import Dict, Optional
import asyncio
from contextlib import asynccontextmanager

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integration.cats_integration import CATSClient
from processors.process_candidate import process_single_candidate
from utils.simple_slack_webhook import slack_webhook
from config import (
    WEBHOOK_SECRET, 
    MANAGER_REVIEW_STATUS_ID,
    QUESTIONNAIRE_FIELD_ID
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Processing queue
processing_queue = asyncio.Queue()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - start background processor"""
    # Start background processor
    task = asyncio.create_task(background_processor())
    yield
    # Cleanup
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

# Initialize FastAPI app
app = FastAPI(
    title="CATS Recruitment Webhook Server",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize clients
cats_client = CATSClient()

async def background_processor():
    """Process candidates from queue in background"""
    while True:
        try:
            webhook_data = await processing_queue.get()
            await process_webhook_async(webhook_data)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in background processor: {e}")
            await asyncio.sleep(1)

async def handle_candidate_created(candidate_id: int, webhook_data: Dict):
    """Handle new candidate creation - check for questionnaire linking"""
    try:
        # Get candidate details from CATS
        candidate = cats_client.get_candidate_details(candidate_id)
        if not candidate:
            logger.error(f"Could not fetch details for new candidate {candidate_id}")
            return
        
        candidate_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}"
        logger.info(f"New candidate: {candidate_name} (ID: {candidate_id})")
        
        # Check for pending questionnaires that match this candidate
        await check_pending_questionnaires(candidate_id, candidate_name)
        
    except Exception as e:
        logger.error(f"Error handling candidate creation: {e}")

async def handle_candidate_updated(candidate_id: int, webhook_data: Dict):
    """Handle candidate updates - check if questionnaire was attached"""
    try:
        # Check if a questionnaire was attached to this candidate
        candidate = cats_client.get_candidate_details(candidate_id)
        if not candidate:
            return
        
        # Check attachments for new questionnaire PDFs
        attachments = candidate.get('attachments', [])
        for attachment in attachments:
            if attachment.get('name', '').lower().endswith('.pdf'):
                # Check if this looks like a questionnaire
                filename = attachment.get('name', '').lower()
                if any(word in filename for word in ['questionnaire', 'form', 'application']):
                    logger.info(f"Questionnaire PDF detected for candidate {candidate_id}: {filename}")
                    # Queue for immediate processing
                    await processing_queue.put({
                        'candidate_id': candidate_id,
                        'event_type': 'questionnaire.attached',
                        'data': webhook_data
                    })
                    break
        
    except Exception as e:
        logger.error(f"Error handling candidate update: {e}")

async def check_pending_questionnaires(candidate_id: int, candidate_name: str):
    """Check for questionnaires waiting to be linked to this candidate"""
    try:
        import os
        import glob
        
        # Check for questionnaire files in processing directory
        questionnaire_dir = "/home/gotime2022/recruitment_ops/questionnaire_images"
        if os.path.exists(questionnaire_dir):
            # Look for processed questionnaire results
            result_files = glob.glob(f"{questionnaire_dir}/*_analysis.json")
            
            for result_file in result_files:
                try:
                    import json
                    with open(result_file, 'r') as f:
                        analysis = json.load(f)
                    
                    # Check if this questionnaire matches the new candidate
                    questionnaire_name = analysis.get('candidate_profile', {}).get('candidate_info', {}).get('name', '')
                    
                    if questionnaire_name and candidate_name:
                        # Simple name matching (can be enhanced)
                        if questionnaire_name.lower() in candidate_name.lower() or candidate_name.lower() in questionnaire_name.lower():
                            logger.info(f"Found matching questionnaire for {candidate_name}: {result_file}")
                            
                            # Process this candidate with the linked questionnaire
                            await processing_queue.put({
                                'candidate_id': candidate_id,
                                'event_type': 'questionnaire.linked',
                                'questionnaire_analysis': analysis,
                                'data': {'auto_linked': True}
                            })
                            
                            # Remove the processed file
                            os.remove(result_file)
                            break
                            
                except Exception as e:
                    logger.error(f"Error processing questionnaire file {result_file}: {e}")
        
    except Exception as e:
        logger.error(f"Error checking pending questionnaires: {e}")

async def process_webhook_async(data: Dict):
    """Process webhook data asynchronously"""
    try:
        candidate_id = data.get('candidate_id')
        event_type = data.get('event_type')
        
        logger.info(f"Processing {event_type} for candidate {candidate_id}")
        
        # Handle questionnaire linking events
        if event_type in ['questionnaire.linked', 'questionnaire.attached']:
            # Process with linked questionnaire
            questionnaire_analysis = data.get('questionnaire_analysis')
            if questionnaire_analysis:
                # Update CATS notes directly
                from ..processors.cats_notes_updater import CATSNotesUpdater
                notes_updater = CATSNotesUpdater(cats_client.api_key, cats_client.base_url)
                result = notes_updater.update_candidate_with_analysis(candidate_id, questionnaire_analysis)
                
                if result.get('success'):
                    logger.info(f"Successfully updated notes for candidate {candidate_id}")
                else:
                    logger.error(f"Failed to update notes: {result.get('error')}")
                return
        
        # Regular processing
        result = await asyncio.to_thread(
            process_single_candidate, 
            candidate_id
        )
        
        if result and result.get('success'):
            # Send Slack notification
            await slack_webhook.send_notification(
                result.get('candidate_info', {}),
                result.get('analysis_result', {}),
                result.get('job_info', {})
            )
            logger.info(f"Successfully processed candidate {candidate_id}")
        else:
            logger.error(f"Failed to process candidate {candidate_id}")
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "queue_size": processing_queue.qsize()
    }

@app.post("/webhook/candidate")
async def handle_candidate_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle CATS webhook for candidate events"""
    
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature if secret is configured
        if WEBHOOK_SECRET:
            signature = request.headers.get('X-CATS-Signature')
            if not verify_webhook_signature(body, signature, WEBHOOK_SECRET):
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON
        data = await request.json()
        
        # Log the webhook
        logger.info(f"Received webhook: {data.get('event_type', 'unknown')}")
        
        # Extract relevant data
        event_type = data.get('event_type')
        candidate_id = data.get('candidate', {}).get('id')
        
        if not candidate_id:
            raise HTTPException(status_code=400, detail="Missing candidate ID")
        
        # Handle different webhook events
        if event_type == 'candidate.created':
            # New candidate added - check for pending questionnaires
            logger.info(f"New candidate created: {candidate_id}")
            await handle_candidate_created(candidate_id, data)
            
            return JSONResponse({
                "status": "processed",
                "candidate_id": candidate_id,
                "message": "New candidate processed for questionnaire linking"
            })
        
        elif event_type == 'candidate.updated':
            # Candidate updated - check if questionnaire was attached
            logger.info(f"Candidate updated: {candidate_id}")
            await handle_candidate_updated(candidate_id, data)
            
            return JSONResponse({
                "status": "processed", 
                "candidate_id": candidate_id,
                "message": "Candidate update processed"
            })
        
        elif event_type == 'pipeline.status_changed':
            # Status change to "manager review needed"
            new_status = data.get('pipeline', {}).get('status_id')
            if new_status == MANAGER_REVIEW_STATUS_ID:
                # Queue for processing
                await processing_queue.put({
                    'candidate_id': candidate_id,
                    'event_type': event_type,
                    'data': data
                })
                
                return JSONResponse({
                    "status": "queued",
                    "candidate_id": candidate_id,
                    "message": "Candidate queued for AI analysis"
                })
        
        # For other events, just acknowledge
        return JSONResponse({
            "status": "acknowledged",
            "event_type": event_type,
            "candidate_id": candidate_id
        })
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/job")
async def handle_job_webhook(request: Request):
    """Handle CATS webhook for job events"""
    
    try:
        data = await request.json()
        event_type = data.get('event_type')
        
        logger.info(f"Received job webhook: {event_type}")
        
        # TODO: Implement job event handling
        # - job.created: New job posted
        # - job.updated: Job requirements changed
        
        return JSONResponse({
            "status": "acknowledged",
            "event_type": event_type
        })
        
    except Exception as e:
        logger.error(f"Job webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def verify_webhook_signature(body: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    import hmac
    import hashlib
    
    if not signature:
        return False
    
    expected = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

@app.get("/queue/status")
async def queue_status():
    """Get processing queue status"""
    return {
        "queue_size": processing_queue.qsize(),
        "status": "active"
    }

@app.post("/manual/process/{candidate_id}")
async def manual_process_candidate(candidate_id: int):
    """Manually trigger candidate processing for existing candidates"""
    
    try:
        # Get candidate details to verify they exist
        candidate = cats_client.get_candidate_details(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
        
        candidate_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}"
        logger.info(f"Manual processing requested for: {candidate_name} (ID: {candidate_id})")
        
        # Check for pending questionnaires
        await check_pending_questionnaires(candidate_id, candidate_name)
        
        # Also queue for regular processing
        await processing_queue.put({
            'candidate_id': candidate_id,
            'event_type': 'manual.trigger',
            'data': {'manually_triggered': True}
        })
        
        return JSONResponse({
            "status": "queued",
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "message": "Candidate queued for manual processing"
        })
        
    except Exception as e:
        logger.error(f"Error in manual processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/manual/link/{candidate_id}")
async def manual_link_questionnaire(candidate_id: int, request: Request):
    """Manually link a questionnaire to a specific candidate"""
    
    try:
        # Get the questionnaire analysis from request body
        data = await request.json()
        questionnaire_analysis = data.get('questionnaire_analysis')
        
        if not questionnaire_analysis:
            raise HTTPException(status_code=400, detail="Missing questionnaire_analysis")
        
        # Verify candidate exists
        candidate = cats_client.get_candidate_details(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
        
        candidate_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}"
        logger.info(f"Manual questionnaire link for: {candidate_name} (ID: {candidate_id})")
        
        # Process immediately
        await processing_queue.put({
            'candidate_id': candidate_id,
            'event_type': 'questionnaire.linked',
            'questionnaire_analysis': questionnaire_analysis,
            'data': {'manually_linked': True}
        })
        
        return JSONResponse({
            "status": "linked",
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "message": "Questionnaire manually linked and queued for processing"
        })
        
    except Exception as e:
        logger.error(f"Error in manual linking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("WEBHOOK_PORT", "8080"))
    
    logger.info(f"Starting CATS Webhook Server on port {port}")
    logger.info(f"Webhook endpoint: http://localhost:{port}/webhook/candidate")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )