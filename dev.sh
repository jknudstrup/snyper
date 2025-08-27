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

# Parse command line - DEFAULT TO MASTER IF NO ARGS
DEVICE_TYPE="${1:-master}"  # 🎯 DEFAULT = master when no arguments
echo "🎯 Running device type: $DEVICE_TYPE"

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
        echo "Usage: $0 [master|target_1|target_2|...|disable]"
        echo "Default: master (when no arguments provided)"
        echo "  disable: Set device to disabled state (no auto-start)"
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

# Step 2: Run via mount instead of deploy
echo "🚀 Running via mount on device..."
cd src
mpremote connect "$SERIAL_DEVICE" mount . run main.py
cd ..