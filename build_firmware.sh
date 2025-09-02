#!/bin/bash

# SNYPER Custom Firmware Builder
# Builds MicroPython firmware with frozen Python modules for major RAM savings
# 
# Usage: ./build_firmware.sh [module1] [module2] [folder1] ...
# Examples:
#   ./build_firmware.sh gui                    # Freeze gui folder
#   ./build_firmware.sh microdot               # Freeze microdot folder  
#   ./build_firmware.sh gui helpers.py         # Freeze gui folder + helpers.py file
#   ./build_firmware.sh                        # Build standard firmware (no custom freezing)

set -e  # Exit on any error

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

# Source the configuration file and set PROJECT_DIR to script directory
source "$CONFIG_FILE"
PROJECT_DIR="$SCRIPT_DIR"

# Convert relative paths to absolute paths based on PROJECT_DIR
MICROPYTHON_DIR="$PROJECT_DIR/$MICROPYTHON_DIR"
PORT_DIR="$PROJECT_DIR/$PORT_DIR"

# Parse command line arguments
FREEZE_TARGETS=("$@")

echo "🚀 SNYPER Custom Firmware Builder"
echo "================================="

if [ ${#FREEZE_TARGETS[@]} -eq 0 ]; then
    echo "📦 Building standard firmware (no custom modules frozen)"
    BUILD_TYPE="standard"
else
    echo "📦 Building custom firmware with frozen modules:"
    BUILD_TYPE="custom"
    for target in "${FREEZE_TARGETS[@]}"; do
        echo "   • $target"
    done
fi

# Validate paths exist
if [ ! -d "$MICROPYTHON_DIR" ]; then
    echo "❌ Error: MicroPython directory not found at $MICROPYTHON_DIR"
    exit 1
fi

# Validate freeze targets exist
VALIDATED_TARGETS=()
if [ "$BUILD_TYPE" = "custom" ]; then
    echo ""
    echo "🔍 Validating freeze targets..."
    
    for target in "${FREEZE_TARGETS[@]}"; do
        TARGET_PATH="$PROJECT_DIR/src/$target"
        
        if [ -f "$TARGET_PATH" ]; then
            echo "✅ File found: $target"
            VALIDATED_TARGETS+=("$target")
        elif [ -d "$TARGET_PATH" ]; then
            echo "✅ Folder found: $target"
            VALIDATED_TARGETS+=("$target") 
        else
            echo "❌ Error: Target not found at $TARGET_PATH"
            echo "   Available in src/:"
            ls -la "$PROJECT_DIR/src/" | grep -E '^d|\.py$' | awk '{print "     " $9}' || true
            exit 1
        fi
    done
    
    if [ ${#VALIDATED_TARGETS[@]} -eq 0 ]; then
        echo "❌ Error: No valid freeze targets found"
        exit 1
    fi
fi

echo "✅ Validation complete"
echo "📁 Project: $PROJECT_DIR"

# Generate dynamic manifest file
TEMP_MANIFEST="/tmp/snyper_manifest_$$.py"

echo "🔧 Generating manifest file..."

cat > "$TEMP_MANIFEST" << 'EOF'
# SNYPER Dynamic Manifest - Auto-generated
# Include default RP2 board manifest (essential firmware components)  
include("$(MPY_DIR)/ports/rp2/boards/manifest.py")

# Add networking bundle (includes urequests, json, ssl, requests, etc.)
require("bundle-networking")

EOF

# Add freeze directives for each target
if [ "$BUILD_TYPE" = "custom" ]; then
    echo "📦 Adding freeze directives to manifest:"
    
    for target in "${VALIDATED_TARGETS[@]}"; do
        TARGET_PATH="$PROJECT_DIR/src/$target"
        
        if [ -f "$TARGET_PATH" ]; then
            # Single file - use module() directive
            MODULE_NAME=$(basename "$target" .py)
            echo "   • module: $target"
            echo "module(\"$target\", base_path=\"$PROJECT_DIR/src\")" >> "$TEMP_MANIFEST"
        elif [ -d "$TARGET_PATH" ]; then
            # Directory - use package() directive  
            echo "   • package: $target"
            echo "package(\"$target\", base_path=\"$PROJECT_DIR/src\")" >> "$TEMP_MANIFEST"
        fi
    done
else
    echo "📦 Standard manifest (no custom freezing)"
fi

echo "📄 Generated manifest: $TEMP_MANIFEST"
if [ "$BUILD_TYPE" = "custom" ]; then
    echo "📋 Manifest contents:"
    cat "$TEMP_MANIFEST" | grep -E "(module|package|freeze)" | sed 's/^/   /'
fi

# Navigate to MicroPython port directory
cd "$PORT_DIR"
echo "📂 Changed to port directory: $PORT_DIR"

# Clean previous build
echo "🧹 Cleaning previous build..."
make clean BOARD=RPI_PICO_W

# Build firmware with dynamic manifest
if [ "$BUILD_TYPE" = "custom" ]; then
    echo "🔨 Building custom firmware with frozen modules..."
    echo "⏱️  This will take 3-4 minutes on Apple Silicon..."
    make -j 8 BOARD=RPI_PICO_W FROZEN_MANIFEST="$TEMP_MANIFEST"
else
    echo "🔨 Building standard firmware..."
    echo "⏱️  This will take 3-4 minutes on Apple Silicon..."
    make -j 8 BOARD=RPI_PICO_W
fi

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Copy firmware to project root with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

if [ "$BUILD_TYPE" = "custom" ]; then
    # Create descriptive name based on frozen modules
    MODULES_SUFFIX=$(printf "%s_" "${VALIDATED_TARGETS[@]}" | sed 's/_$//')
    FIRMWARE_NAME="snyper_firmware_${MODULES_SUFFIX}_$TIMESTAMP.uf2"
else
    FIRMWARE_NAME="snyper_firmware_standard_$TIMESTAMP.uf2"
fi

FIRMWARE_PATH="$PROJECT_DIR/$FIRMWARE_NAME"
cp "build-RPI_PICO_W/firmware.uf2" "$FIRMWARE_PATH"

echo ""
echo "🎯 SUCCESS! Firmware built successfully!"
echo "========================================"
echo "📄 Firmware: $FIRMWARE_PATH"
echo "📊 Size: $(ls -lh "$FIRMWARE_PATH" | awk '{print $5}')"
echo ""

if [ "$BUILD_TYPE" = "custom" ]; then
    echo "🔥 Frozen components:"
    for target in "${VALIDATED_TARGETS[@]}"; do
        TARGET_PATH="$PROJECT_DIR/src/$target"
        if [ -f "$TARGET_PATH" ]; then
            echo "   • Module: $target"
        elif [ -d "$TARGET_PATH" ]; then
            echo "   • Package: $target"
        fi
    done
    echo "   • Networking bundle (urequests, ssl, json, etc.)"
    echo "   • Standard RP2 board components"
    
    echo ""
    echo "⚡ Expected benefits:"
    echo "   • RAM savings (frozen modules run from ROM)"
    echo "   • Faster imports (pre-compiled bytecode)" 
    echo "   • Smaller deployment (modules embedded in firmware)"
    
    echo ""
    echo "🧪 Test imports in REPL:"
    for target in "${VALIDATED_TARGETS[@]}"; do
        TARGET_PATH="$PROJECT_DIR/src/$target"
        if [ -f "$TARGET_PATH" ]; then
            MODULE_NAME=$(basename "$target" .py)
            echo "   >>> import $MODULE_NAME    # Should work!"
        elif [ -d "$TARGET_PATH" ]; then
            # Show example import for packages
            EXAMPLE_MODULE=$(find "$TARGET_PATH" -name "*.py" -not -name "__init__.py" | head -1)
            if [ -n "$EXAMPLE_MODULE" ]; then
                REL_PATH=$(echo "$EXAMPLE_MODULE" | sed "s|$PROJECT_DIR/src/||" | sed 's|\.py$||' | tr '/' '.')
                echo "   >>> import $REL_PATH    # Should work!"
            fi
        fi
    done
else
    echo "📦 Standard MicroPython firmware with networking bundle"
    echo "   • No custom modules frozen"
    echo "   • Networking bundle (urequests, ssl, json, etc.)"
    echo "   • Standard RP2 board components"
fi

echo ""
echo "💾 Deployment:"
echo "   1. Put Pico W in BOOTSEL mode (hold BOOTSEL while powering on)"
echo "   2. Copy $FIRMWARE_NAME to the USB mass storage device"  
echo "   3. Device will reboot with custom firmware"

# Also create a symlink to latest firmware for convenience
ln -sf "$FIRMWARE_NAME" "$PROJECT_DIR/snyper_firmware_latest.uf2"
echo "🔗 Symlink created: snyper_firmware_latest.uf2 -> $FIRMWARE_NAME"

# Move frozen code to backup location
if [ "$BUILD_TYPE" = "custom" ]; then
    echo ""
    echo "📦 Moving frozen code to backup location..."
    
    # Create src_frozen directory if it doesn't exist
    BACKUP_DIR="$PROJECT_DIR/src_frozen"
    mkdir -p "$BACKUP_DIR"
    
    # Create timestamp subdirectory for this build
    BACKUP_SUBDIR="$BACKUP_DIR/${MODULES_SUFFIX}_$TIMESTAMP"
    mkdir -p "$BACKUP_SUBDIR"
    
    echo "📁 Backup directory: $BACKUP_SUBDIR"
    
    for target in "${VALIDATED_TARGETS[@]}"; do
        SOURCE_PATH="$PROJECT_DIR/src/$target"
        BACKUP_PATH="$BACKUP_SUBDIR/$target"
        
        if [ -f "$SOURCE_PATH" ]; then
            # Move single file
            echo "   📄 Moving file: $target"
            mv "$SOURCE_PATH" "$BACKUP_PATH"
        elif [ -d "$SOURCE_PATH" ]; then
            # Move entire directory
            echo "   📁 Moving package: $target"
            mv "$SOURCE_PATH" "$BACKUP_PATH"
        fi
    done
    
    # Create a reference file linking this backup to the firmware
    echo "# Frozen code backup for firmware: $FIRMWARE_NAME" > "$BACKUP_SUBDIR/BUILD_INFO.txt"
    echo "# Build timestamp: $TIMESTAMP" >> "$BACKUP_SUBDIR/BUILD_INFO.txt"
    echo "# Frozen modules:" >> "$BACKUP_SUBDIR/BUILD_INFO.txt"
    for target in "${VALIDATED_TARGETS[@]}"; do
        echo "#   - $target" >> "$BACKUP_SUBDIR/BUILD_INFO.txt"
    done
    echo "# Firmware file: $FIRMWARE_PATH" >> "$BACKUP_SUBDIR/BUILD_INFO.txt"
    
    echo "✅ Frozen code moved to backup location"
    echo "📝 Build info saved: $BACKUP_SUBDIR/BUILD_INFO.txt"
    echo ""
    echo "⚠️  IMPORTANT:"
    echo "   • Frozen modules are now embedded in firmware"
    echo "   • Original source moved to: $BACKUP_SUBDIR"
    echo "   • Deploy scripts will no longer sync these modules"
    echo "   • To restore modules to src/, copy from backup location"
fi

# Clean up temporary manifest
rm -f "$TEMP_MANIFEST"