# helpers.py - Shared utility functions for SNYPER

import network
import asyncio
import time

async def reset_network_interface():
    """Properly reset the network interface to handle soft resets
    
    This clears network caching bullshit that causes mysterious connection issues.
    Should be called at startup for both master and target devices.
    """
    # Get both interfaces
    wlan = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    
    # Force disconnect and deactivate station interface
    if wlan.active():
        try:
            wlan.disconnect()
            await asyncio.sleep_ms(500)  # Give it time to disconnect
        except:
            pass
        
        try:
            wlan.active(False)
            await asyncio.sleep_ms(1000)  # Important: give it time to fully deactivate
        except:
            pass
    
    # Also ensure AP interface is off (in case it was used before)
    if ap.active():
        try:
            ap.active(False)
            await asyncio.sleep_ms(500)
        except:
            pass
        
    print("🔄 Network interfaces reset - ready for clean connection!")

async def initialize_access_point(ssid, password, reset=False):
    """Initialize WiFi Access Point with optional network reset
    
    Args:
        ssid: Network name for the access point
        password: Password for the access point  
        reset: If True, reset network interfaces first (default: True)
    
    Returns:
        ap: Configured and active AP interface
    """
    print(f"🌐 Initializing WiFi AP: {ssid}")
    
    if reset:
        # Reset network interfaces to clear cached state
        await reset_network_interface()
    
    # Get AP interface and configure
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)

    while not ap.active():
        print("⏳ Waiting for AP to activate...")
        time.sleep(0.1)

    print(f"✅ WiFi AP '{ssid}' ACTIVE at {ap.ifconfig()[0]}")
    return ap