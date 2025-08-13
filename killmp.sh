#!/bin/bash

# Find and kill any 'mpremote' tasks
# This script will list all running processes, filter for 'mpremote',
# extract their Process IDs (PIDs), and then attempt to terminate them.

echo "Searching for 'mpremote' processes..."

# Use 'pgrep' to find PIDs of 'mpremote' processes
# 'pgrep -f mpremote' searches for processes where the full command line matches 'mpremote'
PIDS=$(pgrep -f mpremote)

if [ -z "$PIDS" ]; then
  echo "No 'mpremote' processes found."
else
  echo "Found 'mpremote' processes with PIDs: $PIDS"
  echo "Attempting to kill these processes..."
  # Loop through each PID and kill the process
  for PID in $PIDS; do
    echo "Killing process $PID..."
    kill "$PID"
    # Check if the process was successfully killed
    if kill -0 "$PID" > /dev/null 2>&1; then
      echo "Failed to kill process $PID. It might require 'kill -9'."
    else
      echo "Process $PID killed successfully."
    fi
  done
fi
