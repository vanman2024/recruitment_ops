#!/usr/bin/env python3
"""
SIMPLE webhook that just WORKS
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post('/webhook/candidate')
async def handle_webhook(request: Request):
    """Just receive the webhook and log it"""
    try:
        data = await request.json()
        candidate_id = data.get('candidate_id') or data.get('id')
        
        logger.info(f"🎯 WEBHOOK RECEIVED for candidate {candidate_id}")
        logger.info(f"Event: {data.get('event')}")
        logger.info(f"Time: {datetime.now()}")
        
        # For now, just return success
        return JSONResponse({
            'status': 'received',
            'candidate_id': candidate_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.get('/health')
async def health():
    return {'status': 'healthy', 'time': datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("Starting SIMPLE webhook on port 8080...")
    uvicorn.run(app, host='0.0.0.0', port=8080)