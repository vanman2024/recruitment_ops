from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "name": "Recruitment Ops API",
            "version": "1.0.0",
            "endpoints": {
                "/api/questionnaire-monitor": "Monitors and processes questionnaire completions (called by cron)",
                "/api/webhook": "Webhook endpoint for CATS notifications"
            },
            "status": "operational"
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())