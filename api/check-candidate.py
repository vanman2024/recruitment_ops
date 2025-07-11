from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get environment variables
            CATS_API_KEY = os.environ.get('CATS_API_KEY', '').strip()
            SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '').strip()
            
            if not CATS_API_KEY:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "CATS_API_KEY not configured"}).encode())
                return
            
            headers = {"Authorization": f"Token {CATS_API_KEY}"}
            
            # Check specific candidate
            candidate_id = 398063905
            
            # Get candidate details
            candidate_response = requests.get(
                f"https://api.catsone.com/v3/candidates/{candidate_id}",
                headers=headers
            )
            
            if candidate_response.status_code != 200:
                raise Exception(f"Failed to get candidate: {candidate_response.status_code}")
            
            candidate = candidate_response.json()
            
            # Get tags
            tag_response = requests.get(
                f"https://api.catsone.com/v3/candidates/{candidate_id}/tags",
                headers=headers
            )
            
            tags = []
            if tag_response.status_code == 200:
                tag_data = tag_response.json()
                if isinstance(tag_data, dict) and '_embedded' in tag_data:
                    tag_list = tag_data['_embedded'].get('tags', [])
                    for tag in tag_list:
                        if isinstance(tag, dict) and 'title' in tag:
                            tags.append(tag['title'])
            
            # Check if should send notification
            should_notify = "Questionnaire Completed" in tags and "AI Notes Generated" not in tags
            
            if should_notify and SLACK_WEBHOOK_URL:
                candidate_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
                message = {
                    "text": f"📋 New questionnaire completed for candidate: {candidate_name} (ID: {candidate_id})\n✅ Ready for AI processing"
                }
                slack_response = requests.post(SLACK_WEBHOOK_URL, json=message)
                slack_sent = slack_response.status_code == 200
            else:
                slack_sent = False
            
            result = {
                "candidate_id": candidate_id,
                "name": f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip(),
                "tags": tags,
                "has_questionnaire_completed": "Questionnaire Completed" in tags,
                "has_ai_notes": "AI Notes Generated" in tags,
                "should_notify": should_notify,
                "slack_sent": slack_sent
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = {"error": str(e), "type": type(e).__name__}
            self.wfile.write(json.dumps(error_msg).encode())