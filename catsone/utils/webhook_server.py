#!/usr/bin/env python3
"""
CATS Webhook Server for Candidate Processing
Handles webhook events when candidates enter "manager review needed" status
"""

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
import os
from threading import Thread
import queue
from typing import Dict, Optional

from cats_integration import CATSClient
from process_candidate import process_single_candidate
from slack_notifier import SlackNotifier
from config import (
    WEBHOOK_SECRET, 
    MANAGER_REVIEW_STATUS_ID,
    QUESTIONNAIRE_FIELD_ID,
    SLACK_CHANNEL_ID
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Processing queue
processing_queue = queue.Queue()

# Initialize clients
cats_client = CATSClient()
slack_notifier = SlackNotifier()


def verify_webhook_signature(request_data, signature):
    """Verify webhook signature if CATS provides one"""
    # TODO: Implement signature verification once CATS provides details
    # For now, we'll check for a shared secret in headers
    if WEBHOOK_SECRET:
        provided_secret = request.headers.get('X-CATS-Secret')
        return provided_secret == WEBHOOK_SECRET
    return True


def is_manager_review_status(webhook_data: Dict) -> bool:
    """Check if the webhook indicates a candidate moved to manager review status"""
    
    # Check for pipeline status change event
    if webhook_data.get('event') == 'candidate.pipeline_status_changed':
        new_status_id = webhook_data.get('new_status_id')
        return str(new_status_id) == str(MANAGER_REVIEW_STATUS_ID)
    
    # Alternative: Check embedded pipeline data
    if '_embedded' in webhook_data and 'pipelines' in webhook_data['_embedded']:
        for pipeline in webhook_data['_embedded']['pipelines']:
            if str(pipeline.get('status_id')) == str(MANAGER_REVIEW_STATUS_ID):
                return True
    
    return False


def extract_candidate_info(webhook_data: Dict) -> Dict:
    """Extract candidate information from webhook payload"""
    
    candidate_info = {
        'id': webhook_data.get('candidate_id'),
        'webhook_event': webhook_data.get('event'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Extract embedded candidate data if available
    if '_embedded' in webhook_data and 'candidate' in webhook_data['_embedded']:
        candidate = webhook_data['_embedded']['candidate']
        candidate_info.update({
            'first_name': candidate.get('first_name'),
            'last_name': candidate.get('last_name'),
            'email': candidate.get('emails', {}).get('primary'),
            'phone': candidate.get('phones', {}).get('cell'),
            'notes': candidate.get('notes', '')
        })
        
        # Check for questionnaire in custom fields
        if 'custom_fields' in candidate.get('_embedded', {}):
            for field in candidate['_embedded']['custom_fields']:
                if str(field.get('id')) == str(QUESTIONNAIRE_FIELD_ID):
                    candidate_info['questionnaire_url'] = field.get('value')
                    break
    
    # Extract job information if available
    if '_embedded' in webhook_data and 'job' in webhook_data['_embedded']:
        job = webhook_data['_embedded']['job']
        candidate_info['job'] = {
            'id': job.get('id'),
            'title': job.get('title'),
            'company': job.get('company', {}).get('name')
        }
    
    return candidate_info


def process_candidate_async(candidate_info: Dict):
    """Process candidate in background thread"""
    
    try:
        logger.info(f"Processing candidate {candidate_info['id']}: {candidate_info.get('first_name')} {candidate_info.get('last_name')}")
        
        # Get full candidate details from CATS
        candidate_details = cats_client.get_candidate_details(candidate_info['id'])
        if not candidate_details:
            logger.error(f"Failed to get candidate details for ID {candidate_info['id']}")
            return
        
        # Process candidate documents
        analysis_result = process_single_candidate(
            candidate_id=candidate_info['id'],
            candidate_data=candidate_details,
            questionnaire_url=candidate_info.get('questionnaire_url')
        )
        
        if not analysis_result:
            logger.error(f"Failed to analyze candidate {candidate_info['id']}")
            return
        
        # Update candidate notes in CATS
        summary = analysis_result.get('summary', '')
        updated = cats_client.update_candidate_notes(
            candidate_id=candidate_info['id'],
            notes=f"{candidate_details.get('notes', '')}\n\n--- AI Analysis ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n{summary}"
        )
        
        if not updated:
            logger.error(f"Failed to update candidate notes for ID {candidate_info['id']}")
        
        # Send Slack notification
        slack_message = slack_notifier.format_manager_notification(
            candidate_info=candidate_info,
            analysis_result=analysis_result,
            job_info=candidate_info.get('job', {})
        )
        
        slack_result = slack_notifier.send_notification(
            channel_id=SLACK_CHANNEL_ID,
            message=slack_message
        )
        
        if slack_result:
            logger.info(f"Slack notification sent for candidate {candidate_info['id']}")
        else:
            logger.error(f"Failed to send Slack notification for candidate {candidate_info['id']}")
        
        # Log activity in CATS
        cats_client.create_activity(
            candidate_id=candidate_info['id'],
            activity_type="AI Analysis",
            notes=f"Automated analysis completed. Match score: {analysis_result.get('match_score', 'N/A')}%",
            job_id=candidate_info.get('job', {}).get('id')
        )
        
    except Exception as e:
        logger.error(f"Error processing candidate {candidate_info['id']}: {str(e)}", exc_info=True)


def process_queue_worker():
    """Worker thread to process candidates from queue"""
    while True:
        try:
            candidate_info = processing_queue.get()
            if candidate_info is None:  # Shutdown signal
                break
            
            process_candidate_async(candidate_info)
            processing_queue.task_done()
            
        except Exception as e:
            logger.error(f"Queue worker error: {str(e)}", exc_info=True)


@app.route('/webhook/cats', methods=['POST'])
def handle_cats_webhook():
    """Handle incoming CATS webhooks"""
    
    try:
        # Verify webhook signature
        if not verify_webhook_signature(request.data, request.headers.get('X-CATS-Signature')):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 403
        
        # Parse webhook data
        webhook_data = request.get_json()
        logger.info(f"Received webhook event: {webhook_data.get('event')}")
        
        # Log full payload for debugging
        logger.debug(f"Full webhook payload: {json.dumps(webhook_data, indent=2)}")
        
        # Check if this is a manager review status change
        if is_manager_review_status(webhook_data):
            candidate_info = extract_candidate_info(webhook_data)
            logger.info(f"Candidate {candidate_info['id']} moved to manager review status")
            
            # Add to processing queue
            processing_queue.put(candidate_info)
            
            return jsonify({
                'status': 'queued',
                'candidate_id': candidate_info['id'],
                'message': 'Candidate queued for processing'
            }), 200
        else:
            logger.info(f"Ignoring event {webhook_data.get('event')} - not a manager review status change")
            return jsonify({
                'status': 'ignored',
                'message': 'Event not relevant for processing'
            }), 200
            
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'queue_size': processing_queue.qsize(),
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/webhook/test', methods=['POST'])
def test_webhook():
    """Test endpoint for webhook development"""
    
    # Sample test payload
    test_payload = {
        "event": "candidate.pipeline_status_changed",
        "candidate_id": 12345,
        "new_status_id": MANAGER_REVIEW_STATUS_ID,
        "_embedded": {
            "candidate": {
                "id": 12345,
                "first_name": "Test",
                "last_name": "Candidate",
                "emails": {"primary": "test@example.com"},
                "_embedded": {
                    "custom_fields": [
                        {
                            "id": QUESTIONNAIRE_FIELD_ID,
                            "value": "https://cats.com/files/questionnaire.pdf"
                        }
                    ]
                }
            },
            "job": {
                "id": 67890,
                "title": "Heavy Equipment Technician",
                "company": {"name": "Test Mining Co"}
            }
        }
    }
    
    # Process as if it were a real webhook
    return handle_cats_webhook()


if __name__ == '__main__':
    # Start worker thread
    worker = Thread(target=process_queue_worker, daemon=True)
    worker.start()
    
    # Get port from environment or default
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    logger.info(f"Starting webhook server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)