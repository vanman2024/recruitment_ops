#!/usr/bin/env python3
"""
Main entry point for candidate processing
Usage: python3 process.py <candidate_id> [job_id]
"""

import subprocess
import sys

# Run the actual script
subprocess.run([sys.executable, "scripts/process_candidate.py"] + sys.argv[1:])