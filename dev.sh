#!/bin/bash
# dev.sh - Development script with device identity switching 🚀⚡
# MISSION: Same control flow as sync.sh but run via mount instead of deploy!

set -e  # Exit on any error

# Activate Python virtual environment
source snyper_env/bin/activate

# Load device configs
if [ -f "config.conf" ]; then
    source config.conf
else
    echo "⚠️  config.conf not found, using defaults"
    SERIAL_MASTER="/dev/cu.usbmodem*"
    SERIAL_TARGET="/dev/cu.usbmodem*"
fi

# Parse command line arguments
DEVICE_TYPE="${1:-master}"  # 🎯 DEFAULT = master when no arguments
ON_DEVICE=false

# Check for -o flag in any position
for arg in "$@"; do
    if [ "$arg" = "-o" ]; then
        ON_DEVICE=true
        break
    fi
done

echo "🎯 Running device type: $DEVICE_TYPE"
if [ "$ON_DEVICE" = true ]; then
    echo "📱 On-device execution mode"
else
    echo "💾 Mount execution mode"
    mpremote reset
fi

case "$DEVICE_TYPE" in
    master|"")
        SERIAL_DEVICE="$SERIAL_MASTER"
        echo "🎮 Master mode selected"
        ;;
    target_*)
        SERIAL_DEVICE="$SERIAL_TARGET" 
        echo "🎯 Target mode selected: $DEVICE_TYPE"
        ;;
    disable)
        SERIAL_DEVICE="$SERIAL_MASTER"  # Default to master device for disable
        echo "🚫 Disable mode selected - device will not auto-start"
        ;;
    *)
        echo "Usage: $0 [master|target_1|target_2|...|disable] [-o]"
        echo "Default: master (when no arguments provided)"
        echo "  -o: Run on-device (exec mode) instead of mount mode"
        echo "  disable: Set device to disabled state (no auto-start)"
        echo "Examples:"
        echo "  $0 master      # Mount and run master.py"
        echo "  $0 master -o   # Execute master.py on device"
        echo "  $0 target_1 -o # Execute target.py on device"
        exit 1
        ;;
esac

echo "🎯 Running $DEVICE_TYPE on $SERIAL_DEVICE"

# Step 1: Generate device identity file
echo "⚙️ Setting device identity to: $DEVICE_TYPE"
cat > src/device_id.json << EOF
{
    "node_id": "$DEVICE_TYPE"
}
EOF

# Step 2: Execute based on mode
if [ "$ON_DEVICE" = true ]; then
    # On-device execution mode - run already deployed code
    echo "🚀 Executing on-device code..."
    
    # Determine which file to execute based on device type
    if [[ "$DEVICE_TYPE" == target_* ]]; then
        EXEC_FILE="target/target.py"
    else
        EXEC_FILE="master/master.py"
    fi
    
    echo "📱 Running $EXEC_FILE on device..."
    mpremote connect "$SERIAL_DEVICE" exec "exec(open('$EXEC_FILE').read())"
else
    # Mount execution mode - run from host filesystem
    echo "🚀 Running via mount on device..."
    
    # Determine which file to run based on device type
    if [[ "$DEVICE_TYPE" == target_* ]]; then
        RUN_FILE="target/target.py"
    else
        RUN_FILE="master/master.py"
    fi
    
    echo "💾 Mounting and running $RUN_FILE..."
    cd src
    mpremote connect "$SERIAL_DEVICE" mount . run "$RUN_FILE"
    cd ..
fi