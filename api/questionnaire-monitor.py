from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get environment variables and strip whitespace
            CATS_API_KEY = os.environ.get('CATS_API_KEY', '').strip()
            SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '').strip()
            
            if not CATS_API_KEY:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "CATS_API_KEY not configured"}).encode())
                return
            
            # Check for candidates
            results = self.check_questionnaires(CATS_API_KEY, SLACK_WEBHOOK_URL)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = {"error": str(e), "type": type(e).__name__}
            self.wfile.write(json.dumps(error_msg).encode())
    
    def check_questionnaires(self, api_key, slack_webhook):
        """Check for candidates with completed questionnaires"""
        # Ensure API key is clean
        clean_api_key = api_key.strip()
        headers = {"Authorization": f"Token {clean_api_key}"}
        
        # Calculate date range - reduce to 24 hours for faster processing
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=24)
        
        # Search for candidates - limit to 20 for Vercel timeout
        params = {
            "updated_after": start_date.isoformat(),
            "per_page": 20
        }
        
        response = requests.get(
            "https://api.catsone.com/v3/candidates",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"CATS API error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        # Handle embedded response format
        if isinstance(data, dict) and '_embedded' in data:
            candidates = data['_embedded'].get('candidates', [])
        else:
            candidates = data if isinstance(data, list) else []
        
        processed = []
        
        for candidate in candidates:
            candidate_id = candidate.get('id')
            if not candidate_id:
                continue
                
            # Get candidate tags
            tag_response = requests.get(
                f"https://api.catsone.com/v3/candidates/{candidate_id}/tags",
                headers=headers
            )
            
            if tag_response.status_code == 200:
                tag_data = tag_response.json()
                
                # Handle embedded format for tags
                tags = []
                if isinstance(tag_data, dict) and '_embedded' in tag_data:
                    tag_list = tag_data['_embedded'].get('tags', [])
                    for tag in tag_list:
                        if isinstance(tag, dict):
                            # Check for 'title' field (CATS uses 'title' not 'name')
                            if 'title' in tag:
                                tags.append(tag['title'])
                            elif 'name' in tag:
                                tags.append(tag['name'])
                elif isinstance(tag_data, list):
                    for tag in tag_data:
                        if isinstance(tag, dict):
                            if 'title' in tag:
                                tags.append(tag['title'])
                            elif 'name' in tag:
                                tags.append(tag['name'])
                        elif isinstance(tag, str):
                            tags.append(tag)
                
                # Check if questionnaire completed but not processed
                if "Questionnaire Completed" in tags and "AI Notes Generated" not in tags:
                    # Send Slack notification
                    if slack_webhook and slack_webhook != "your_slack_webhook_here":
                        candidate_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
                        message = {
                            "text": f"📋 New questionnaire completed for candidate: {candidate_name} (ID: {candidate_id})"
                        }
                        try:
                            requests.post(slack_webhook, json=message)
                        except:
                            pass  # Don't fail if Slack is down
                    
                    processed.append({
                        'id': candidate_id,
                        'name': f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
                    })
        
        return {
            'checked': len(candidates),
            'processed': len(processed),
            'candidates': processed,
            'timestamp': datetime.now().isoformat(),
            'message': f"Found {len(processed)} candidates with completed questionnaires"
        }