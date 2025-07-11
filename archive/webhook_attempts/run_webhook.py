#!/usr/bin/env python3
"""
Reliable webhook runner that ensures environment is loaded
"""

import os
import sys
from pathlib import Path

# CRITICAL: Load environment variables FIRST before ANY imports
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    print(f"Loading environment from: {env_path}")
    # Manual loading to ensure it works
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
                print(f"✓ Set {key}: {value[:20]}...")

# Verify critical keys
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
if not anthropic_key or 'your-api-key' in anthropic_key:
    print("ERROR: Valid ANTHROPIC_API_KEY not found!")
    sys.exit(1)

print(f"\n✅ Environment loaded successfully!")
print(f"ANTHROPIC_API_KEY: {anthropic_key[:20]}...")
print(f"CATS_API_KEY: {os.getenv('CATS_API_KEY', 'NOT SET')[:20]}...")

# Now import and run
sys.path.insert(0, str(Path(__file__).parent))

# Run the webhook handler directly
import uvicorn
from catsone.scripts.webhook_handler import app

if __name__ == "__main__":
    print("\nStarting webhook handler...")
    uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info')