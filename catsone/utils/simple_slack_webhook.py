"""
Simple Slack Webhook Integration
No bot tokens needed - just webhook URLs

This uses Slack INCOMING webhooks to POST messages TO Slack.
Works from localhost - no ngrok needed for sending notifications!
"""

import os
import json
import httpx
import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleSlackWebhook:
    """Simple webhook-based Slack notifications"""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url or self.webhook_url == "your_slack_webhook_url_here":
            logger.warning("SLACK_WEBHOOK_URL not configured")
    
    async def send_notification(self, 
                               candidate_info: Dict, 
                               analysis_result: Dict,
                               job_info: Dict) -> bool:
        """Send formatted notification via webhook"""
        
        if not self.webhook_url:
            logger.error("No Slack webhook URL configured")
            return False
        
        try:
            # Build the message
            message = self._format_message(candidate_info, analysis_result, job_info)
            
            # Send to Slack
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json={"text": message},
                    timeout=10.0
                )
            
            if response.status_code == 200:
                logger.info("Successfully sent Slack notification")
                return True
            else:
                logger.error(f"Slack webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _format_message(self, candidate_info: Dict, analysis_result: Dict, job_info: Dict) -> str:
        """Format a simple but effective notification"""
        
        candidate_name = f"{candidate_info.get('first_name', '')} {candidate_info.get('last_name', '')}".strip()
        job_title = job_info.get('title', 'Unknown Position')
        match_score = analysis_result.get('match_score', 'N/A')
        
        # Score indicator
        if isinstance(match_score, (int, float)):
            if match_score >= 90:
                score_indicator = "🔥"
            elif match_score >= 75:
                score_indicator = "✅"
            else:
                score_indicator = "📊"
        else:
            score_indicator = "📊"
        
        message = f"""
{score_indicator} *New Candidate Alert*

*Candidate:* {candidate_name}
*Position:* {job_title}
*Match Score:* {match_score}%

*Key Qualifications:*"""
        
        # Add top qualifications
        if 'key_qualifications' in analysis_result:
            for qual in analysis_result['key_qualifications'][:3]:
                message += f"\n• {qual}"
        
        # Add equipment if relevant
        if 'equipment_brands' in analysis_result and analysis_result['equipment_brands']:
            brands = ", ".join(analysis_result['equipment_brands'][:5])
            message += f"\n\n*Equipment:* {brands}"
        
        # Add CATS link
        if candidate_info.get('id'):
            message += f"\n\n<https://app.catsone.com/candidates/{candidate_info['id']}|View in CATS →>"
        
        return message
    
    async def send_batch_summary(self, processed_count: int, high_match_candidates: List[Dict]) -> bool:
        """Send daily/batch processing summary"""
        
        if not self.webhook_url:
            return False
        
        try:
            message = f"""
📋 *Batch Processing Complete*

*Total Processed:* {processed_count} candidates
*High Matches (80%+):* {len(high_match_candidates)}
"""
            
            if high_match_candidates:
                message += "\n*Top Candidates:*"
                for candidate in high_match_candidates[:5]:
                    name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
                    score = candidate.get('match_score', 'N/A')
                    position = candidate.get('position', 'Unknown')
                    message += f"\n• {name} - {position} ({score}%)"
            
            message += f"\n\n_Processed at {datetime.now().strftime('%Y-%m-%d %H:%M')}_"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json={"text": message}
                )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to send batch summary: {e}")
            return False


# Singleton instance
slack_webhook = SimpleSlackWebhook()