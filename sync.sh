#!/bin/bash
# sync.sh - Simple device deployment script
# MISSION: Device identity switching + whole src folder sync! 🚀⚡

set -e  # Exit on any error

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
echo "🎯 Deploying device type: $DEVICE_TYPE"

case "$DEVICE_TYPE" in
    master|"")
        SERIAL_DEVICE="$SERIAL_MASTER"
        echo "🎮 Master mode selected"
        ;;
    target_*)
        SERIAL_DEVICE="$SERIAL_TARGET" 
        echo "🎯 Target mode selected: $DEVICE_TYPE"
        ;;
    *)
        echo "Usage: $0 [master|target_1|target_2|...]"
        echo "Default: master (when no arguments provided)"
        exit 1
        ;;
esac

echo "🎯 Deploying $DEVICE_TYPE to $SERIAL_DEVICE"

# Step 1: Generate device identity file
echo "⚙️ Setting device identity to: $DEVICE_TYPE"
cat > src/device_id.json << EOF
{
    "node_id": "$DEVICE_TYPE"
}
EOF

# Step 2: Deploy entire src folder to device
echo "🚀 Deploying src folder to device..."
cd src
mpremote connect "$SERIAL_DEVICE" cp -r . :
cd ..

echo "✅ $DEVICE_TYPE deployed successfully!"
echo "🎯 Device identity: $DEVICE_TYPE"