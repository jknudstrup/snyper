#!/bin/bash

# Development script for Snyper project
# Usage: 
#   ./dev.sh       - Run master mode
#   ./dev.sh -m    - Run master mode
#   ./dev.sh -t    - Run target mode

# Check if config.conf exists
if [ ! -f "config.conf" ]; then
    echo "Error: config.conf not found"
    exit 1
fi

# Source the config file to load variables
source config.conf

# Function to run master mode
run_master() {
    if [ -z "$SERIAL_MASTER" ]; then
        echo "Error: SERIAL_MASTER not defined in config.conf"
        exit 1
    fi
    echo "Running master mode with device: $SERIAL_MASTER"
    cd src
    mpremote connect "$SERIAL_MASTER" mount . run master.py
}

# Function to run target mode
run_target() {
    if [ -z "$SERIAL_TARGET" ]; then
        echo "Error: SERIAL_TARGET not defined in config.conf"
        exit 1
    fi
    echo "Running target mode with device: $SERIAL_TARGET"
    cd src
    mpremote connect "$SERIAL_TARGET" mount . run target.py
}

# Parse command line arguments
case "${1:-}" in
    ""|"-m")
        run_master
        ;;
    "-t")
        run_target
        ;;
    *)
        echo "Usage: $0 [-m|-t]"
        echo "  -m or no args: Run master mode"
        echo "  -t: Run target mode"
        exit 1
        ;;
esac