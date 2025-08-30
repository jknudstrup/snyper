# SNYPER Custom Manifest for Raspberry Pi Pico W
# Freezes GUI library while keeping hardware components unfrozen for flexibility

# Include default RP2 board manifest (essential firmware components)  
include("$(MPY_DIR)/ports/rp2/boards/manifest.py")

# Add networking bundle (includes urequests, json, ssl, requests, etc.)
require("bundle-networking")

# Freeze GUI library from our trimmed src/gui directory
# This achieves major RAM savings (55KB → 23KB according to library docs)
freeze("/Users/jimknudstrup/Documents/Projects/snyper/src/gui")