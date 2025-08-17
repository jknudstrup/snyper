#!/bin/bash
# sync.sh - Ultimate device deployment script
# MISSION: Device identity switching + minimal file syncing! 🚀⚡

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
        FILE_PROFILE="master"
        echo "🎮 Master mode selected"
        ;;
    target_*)
        SERIAL_DEVICE="$SERIAL_TARGET" 
        FILE_PROFILE="target"
        echo "🎯 Target mode selected: $DEVICE_TYPE"
        ;;
    *)
        echo "Usage: $0 [master|target_1|target_2|...]"
        echo "Default: master (when no arguments provided)"
        exit 1
        ;;
esac

echo "🎯 Deploying $DEVICE_TYPE to $SERIAL_DEVICE"

# Device identity generation function
generate_device_id() {
    local device_type="$1"
    
    echo "⚙️ Setting device identity to: $device_type"
    cat > src/device_id.json << EOF
{
    "node_id": "$device_type"
}
EOF
}

# File copying functions
copy_master_files() {
    local dest="$1"
    
    echo "📦 Copying master file set..."
    
    # Core entry points
    cp src/main.py "$dest/"
    cp src/master.py "$dest/"
    cp src/master_server.py "$dest/"
    
    # Support modules
    cp src/events.py "$dest/"
    cp src/helpers.py "$dest/"
    cp src/config.py "$dest/"
    cp src/hardware_setup.py "$dest/"
    
    # GUI framework (selective)
    mkdir -p "$dest/gui/core" "$dest/gui/widgets" "$dest/gui/fonts"
    cp src/gui/core/ugui.py "$dest/gui/core/"
    cp src/gui/core/writer.py "$dest/gui/core/"
    cp src/gui/core/colors.py "$dest/gui/core/"
    cp src/gui/widgets/__init__.py "$dest/gui/widgets/"
    cp src/gui/fonts/arial10.py "$dest/gui/fonts/"
    
    # Display driver
    mkdir -p "$dest/drivers"
    cp src/drivers/st7789.py "$dest/drivers/"
    
    # HTTP server
    cp -r src/microdot "$dest/"
}

copy_target_files() {
    local dest="$1"
    
    echo "📦 Copying target file set..."
    
    # Core entry points  
    cp src/main.py "$dest/"
    cp src/target_server.py "$dest/"
    
    # Support modules
    cp src/events.py "$dest/"
    cp src/helpers.py "$dest/"
    cp src/config.py "$dest/"
    
    # HTTP server
    cp -r src/microdot "$dest/"
}

copy_minimal_files() {
    local profile="$1"
    local dest="$2"
    
    case "$profile" in
        master)
            copy_master_files "$dest"
            ;;
        target)
            copy_target_files "$dest"
            ;;
        *)
            echo "💥 Unknown file profile: $profile"
            exit 1
            ;;
    esac
}

# Create temp staging area
TEMP_DIR=".sync_temp_$(date +%s)"
mkdir -p "$TEMP_DIR"

echo "🚀 Starting sync process..."

# Step 1: Generate device identity file
generate_device_id "$DEVICE_TYPE"
cp src/device_id.json "$TEMP_DIR/"

# Step 2: Copy minimal file set based on profile
copy_minimal_files "$FILE_PROFILE" "$TEMP_DIR"

# Step 3: Deploy to device
echo "🚀 Deploying to device..."
cd "$TEMP_DIR"

# Clean existing Python files on device
echo "🧹 Cleaning existing files on device..."
mpremote connect "$SERIAL_DEVICE" exec "import os; [os.remove(f) for f in os.listdir('.') if f.endswith('.py')]" || true

# Copy new files
echo "📤 Copying files to device..."
mpremote connect "$SERIAL_DEVICE" mount . cp -r . :

# Step 4: Cleanup  
cd ..
rm -rf "$TEMP_DIR"

echo "✅ $DEVICE_TYPE deployed successfully!"
echo "📊 File set: $FILE_PROFILE profile"
echo "🎯 Device identity: $DEVICE_TYPE"