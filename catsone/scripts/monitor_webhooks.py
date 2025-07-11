#!/usr/bin/env python3
"""
Monitor all webhook activity in real-time
"""

import time
import subprocess
import json

print("Monitoring webhook activity...")
print("="*60)

last_size = 0
while True:
    try:
        # Get file size
        result = subprocess.run(['wc', '-l', 'webhook_live.log'], capture_output=True, text=True)
        current_size = int(result.stdout.split()[0])
        
        if current_size > last_size:
            # New lines added
            new_lines = current_size - last_size
            result = subprocess.run(['tail', f'-n{new_lines}', 'webhook_live.log'], capture_output=True, text=True)
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    # Highlight important lines
                    if 'Received webhook' in line:
                        print(f"\n🔔 {line}")
                    elif 'candidate_id' in line:
                        print(f"   📋 {line}")
                    elif 'POST /webhook/' in line:
                        endpoint = line.split('POST ')[1].split(' ')[0]
                        print(f"\n📮 Webhook hit: {endpoint}")
                    elif 'ERROR' in line:
                        print(f"   ❌ {line}")
                    elif 'Successfully processed' in line:
                        print(f"   ✅ {line}")
                    else:
                        print(f"   {line}")
            
            last_size = current_size
        
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)