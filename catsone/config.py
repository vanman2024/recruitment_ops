"""
Configuration settings for the Candidate Processor application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CATS_API_KEY = os.getenv("CATS_API_KEY", "23ff55bbce3778ac88d702eafab1d06a")
CATS_API_URL = os.getenv("CATS_API_URL", "https://api.catsone.com/v3")

# File paths
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

# Create directories if they don't exist
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Processing settings
IMAGE_DPI = 300  # High quality for checkbox detection
GEMINI_MODEL = "gemini-2.5-pro"  # Latest and most powerful model
GEMINI_BATCH_MODEL = "gemini-2.5-flash"  # Fast model for batch processing
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "candidate_processor.log"

# CATS API Settings
CATS_COMPANY_ID = os.getenv("CATS_COMPANY_ID")
CATS_SITE_ID = os.getenv("CATS_SITE_ID")

# Webhook Configuration
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # Shared secret for webhook verification
MANAGER_REVIEW_STATUS_ID = os.getenv("MANAGER_REVIEW_STATUS_ID", "")  # CATS status ID for "manager review needed"
QUESTIONNAIRE_FIELD_ID = os.getenv("QUESTIONNAIRE_FIELD_ID", "")  # Custom field ID for questionnaire PDF

# Slack Configuration
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")  # Channel ID for manager notifications
SLACK_THREAD_NOTIFICATIONS = os.getenv("SLACK_THREAD_NOTIFICATIONS", "true").lower() == "true"

# Gemini Temperature for analysis
GEMINI_TEMPERATURE = 0.3  # Lower for more consistent analysis