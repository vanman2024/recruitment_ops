#!/bin/bash
# Load environment and start webhook handler

cd /home/gotime2022/recruitment_ops
source venv/bin/activate

# Export all environment variables from .env
export $(grep -v '^#' .env | xargs)

# Verify API key is loaded
echo "API Key loaded: ${ANTHROPIC_API_KEY:0:20}..."

# Start webhook handler
python catsone/scripts/webhook_handler.py