import os
import json
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - used by Vercel cron"""
        try:
            # Get environment variables
            CATS_API_KEY = os.environ.get('CATS_API_KEY')
            SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            
            if not CATS_API_KEY:
                self.send_error(500, "CATS_API_KEY not configured")
                return
            
            # Check for candidates with completed questionnaires
            results = self.check_questionnaires(CATS_API_KEY, SLACK_WEBHOOK_URL)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def check_questionnaires(self, api_key, slack_webhook):
        """Check for candidates with completed questionnaires"""
        headers = {"Authorization": f"Token {api_key}"}
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=48)
        
        # Search for candidates
        params = {
            "updated_after": start_date.isoformat(),
            "per_page": 100
        }
        
        response = requests.get(
            "https://api.catsone.com/v3/candidates",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"CATS API error: {response.status_code}")
        
        candidates = response.json()
        processed = []
        
        for candidate in candidates:
            # Get candidate tags
            tag_response = requests.get(
                f"https://api.catsone.com/v3/candidates/{candidate['id']}/tags",
                headers=headers
            )
            
            if tag_response.status_code == 200:
                tags = [tag['name'] for tag in tag_response.json()]
                
                # Check if questionnaire completed but not processed
                if "Questionnaire Completed" in tags and "ai_notes_generated" not in tags:
                    # Process this candidate
                    self.process_candidate(candidate['id'], headers, slack_webhook)
                    processed.append({
                        'id': candidate['id'],
                        'name': candidate.get('first_name', '') + ' ' + candidate.get('last_name', '')
                    })
        
        return {
            'checked': len(candidates),
            'processed': len(processed),
            'candidates': processed,
            'timestamp': datetime.now().isoformat()
        }
    
    def process_candidate(self, candidate_id, headers, slack_webhook):
        """Process a single candidate"""
        # This is a simplified version - in production, you'd call your full processor
        # For now, just send a Slack notification
        
        if slack_webhook:
            message = {
                "text": f"New questionnaire completed for candidate {candidate_id}. Please process manually or wait for next batch run."
            }
            requests.post(slack_webhook, json=message)
        
        # Add the ai_notes_generated tag
        tag_data = {"name": "ai_notes_generated"}
        requests.post(
            f"https://api.catsone.com/v3/candidates/{candidate_id}/tags",
            headers=headers,
            json=tag_data
        )