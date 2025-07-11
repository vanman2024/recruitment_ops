from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get environment variables
            CATS_API_KEY = os.environ.get('CATS_API_KEY', '').strip()
            
            if not CATS_API_KEY:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "CATS_API_KEY not configured"}).encode())
                return
            
            headers = {"Authorization": f"Token {CATS_API_KEY}"}
            
            # Test with a specific candidate
            candidate_id = 398063905
            debug_info = {"candidate_id": candidate_id}
            
            # Get tags for this candidate
            tag_url = f"https://api.catsone.com/v3/candidates/{candidate_id}/tags"
            tag_response = requests.get(tag_url, headers=headers)
            
            debug_info["tag_request"] = {
                "url": tag_url,
                "status_code": tag_response.status_code
            }
            
            if tag_response.status_code == 200:
                tag_data = tag_response.json()
                debug_info["tag_response_type"] = type(tag_data).__name__
                debug_info["tag_response_keys"] = list(tag_data.keys()) if isinstance(tag_data, dict) else "not a dict"
                
                # Show sample of response
                if isinstance(tag_data, dict):
                    debug_info["tag_response_sample"] = {
                        k: v for k, v in list(tag_data.items())[:3]
                    }
                    # Check _embedded section
                    if '_embedded' in tag_data:
                        debug_info["_embedded_content"] = tag_data['_embedded']
                else:
                    debug_info["tag_response_sample"] = str(tag_data)[:200]
            else:
                debug_info["tag_error"] = tag_response.text
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(debug_info, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = {"error": str(e), "type": type(e).__name__}
            self.wfile.write(json.dumps(error_msg).encode())