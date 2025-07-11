from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Test environment variables
            cats_key = os.environ.get('CATS_API_KEY', '')
            slack_url = os.environ.get('SLACK_WEBHOOK_URL', '')
            
            response = {
                "status": "ok",
                "env_vars": {
                    "CATS_API_KEY_exists": bool(cats_key),
                    "CATS_API_KEY_length": len(cats_key),
                    "CATS_API_KEY_has_newline": '\n' in cats_key,
                    "CATS_API_KEY_stripped_length": len(cats_key.strip()),
                    "SLACK_WEBHOOK_exists": bool(slack_url),
                    "SLACK_WEBHOOK_length": len(slack_url)
                },
                "test": "Environment variable check"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())