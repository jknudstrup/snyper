#!/bin/bash
# sync.sh - Simple device deployment script
# MISSION: Device identity switching + whole src folder sync! 🚀⚡

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
CLEAN_MODE=false

# Check for -clean flag in any position
for arg in "$@"; do
    if [ "$arg" = "-clean" ]; then
        CLEAN_MODE=true
        break
    fi
done

echo "🎯 Deploying device type: $DEVICE_TYPE"
if [ "$CLEAN_MODE" = true ]; then
    echo "🧹 Clean mode enabled - device will be wiped before deployment"
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
        echo "Usage: $0 [master|target_1|target_2|...|disable] [-clean]"
        echo "Default: master (when no arguments provided)"
        echo "  disable: Set device to disabled state (no auto-start)"
        echo "  -clean: Wipe device completely before deployment (removes all files)"
        exit 1
        ;;
esac

echo "🎯 Deploying $DEVICE_TYPE to $SERIAL_DEVICE"

# Step 1: Generate device identity file
echo "⚙️ Setting device identity to: $DEVICE_TYPE"
cat > src/config/device_id.json << EOF
{
    "node_id": "$DEVICE_TYPE"
}
EOF

# Step 2: Clean device if requested
if [ "$CLEAN_MODE" = true ]; then
    echo "🧹 Wiping device completely..."
    mpremote connect "$SERIAL_DEVICE" rm -r :
    echo "✅ Device wiped clean"
fi

# Step 3: Deploy entire src folder to device
echo "🚀 Deploying src folder to device..."
cd src
mpremote connect "$SERIAL_DEVICE" cp -r . :
cd ..

echo "✅ $DEVICE_TYPE deployed successfully!"
echo "🎯 Device identity: $DEVICE_TYPE"

# Reset device after disable deployment
if [ "$DEVICE_TYPE" = "disable" ]; then
    echo "🔄 Resetting device after disable deployment..."
    mpremote connect "$SERIAL_DEVICE" reset
    echo "🚫 Device reset complete - disabled mode active"
fi