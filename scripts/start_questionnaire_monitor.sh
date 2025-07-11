#!/bin/bash
# Start the questionnaire monitor in the background

cd /home/gotime2022/recruitment_ops

# Kill any existing monitor
pkill -f questionnaire_monitor_simple.py

# Start new monitor
echo "Starting questionnaire monitor..."
nohup python3 scripts/questionnaire_monitor_simple.py > logs/questionnaire_monitor_live.log 2>&1 &

echo "Monitor started with PID $!"
echo "View logs: tail -f logs/questionnaire_monitor_live.log"
echo "Stop monitor: pkill -f questionnaire_monitor_simple.py"