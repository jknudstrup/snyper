#!/bin/bash

# SNYPER Custom Firmware Builder
# Builds MicroPython firmware with frozen GUI library for major RAM savings

set -e  # Exit on any error

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

# Source the configuration file
source "$CONFIG_FILE"

echo "🚀 SNYPER Custom Firmware Builder"
echo "================================="

# Validate paths exist
if [ ! -d "$MICROPYTHON_DIR" ]; then
    echo "❌ Error: MicroPython directory not found at $MICROPYTHON_DIR"
    exit 1
fi

if [ ! -f "$MANIFEST_FILE" ]; then
    echo "❌ Error: Manifest file not found at $MANIFEST_FILE"
    exit 1
fi

if [ ! -d "$PROJECT_DIR/src/gui" ]; then
    echo "❌ Error: GUI source directory not found at $PROJECT_DIR/src/gui"
    echo "   The GUI library must exist for freezing into firmware"
    exit 1
fi

echo "✅ Validation complete"
echo "📁 Project: $PROJECT_DIR"
echo "🔧 Manifest: $MANIFEST_FILE"
echo "📦 GUI Source: $PROJECT_DIR/src/gui"

# Navigate to MicroPython build directory
cd "$BUILD_DIR"
echo "📂 Changed to build directory: $BUILD_DIR"

# Clean previous build
echo "🧹 Cleaning previous build..."
make clean BOARD=RPI_PICO_W

# Build firmware with custom manifest
echo "🔨 Building custom firmware with frozen GUI library..."
echo "⏱️  This will take 3-4 minutes on Apple Silicon..."

make -j 8 BOARD=RPI_PICO_W FROZEN_MANIFEST="$MANIFEST_FILE"

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Copy firmware to project root with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FIRMWARE_NAME="snyper_firmware_$TIMESTAMP.uf2"
FIRMWARE_PATH="$PROJECT_DIR/$FIRMWARE_NAME"

cp "build-RPI_PICO_W/firmware.uf2" "$FIRMWARE_PATH"

echo ""
echo "🎯 SUCCESS! Custom firmware built successfully!"
echo "==============================================="
echo "📄 Firmware: $FIRMWARE_PATH"
echo "📊 Size: $(ls -lh "$FIRMWARE_PATH" | awk '{print $5}')"
echo ""
echo "🔥 Frozen components:"
echo "   • GUI library (gui/core/, gui/widgets/, gui/fonts/)"
echo "   • Networking bundle (urequests, ssl, json, etc.)"
echo "   • Standard RP2 board components"
echo ""
echo "💾 Deployment:"
echo "   1. Put Pico W in BOOTSEL mode (hold BOOTSEL while powering on)"
echo "   2. Copy $FIRMWARE_NAME to the USB mass storage device"
echo "   3. Device will reboot with custom firmware"
echo ""
echo "⚡ Expected benefits:"
echo "   • ~32KB RAM savings (GUI library runs from ROM)"
echo "   • Faster GUI imports (pre-compiled bytecode)"
echo "   • Smaller deployment (GUI embedded in firmware)"
echo ""
echo "🧪 Test imports in REPL:"
echo "   >>> import gui.core.ugui    # Should work!"
echo "   >>> import gc; gc.mem_free()  # Check available RAM"

# Also create a symlink to latest firmware for convenience
ln -sf "$FIRMWARE_NAME" "$PROJECT_DIR/snyper_firmware_latest.uf2"
echo "🔗 Symlink created: snyper_firmware_latest.uf2 -> $FIRMWARE_NAME"