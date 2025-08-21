# helpers.py - Shared utility functions for SNYPER

import network
import time

def reset_network_interface():
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
            time.sleep(0.5)  # Give it time to disconnect
        except:
            pass
        
        try:
            wlan.active(False)
            time.sleep(1)  # Important: give it time to fully deactivate
        except:
            pass
    
    # Also ensure AP interface is off (in case it was used before)
    if ap.active():
        try:
            ap.active(False)
            time.sleep(0.5)
        except:
            pass
        
    print("🔄 Network interfaces reset - ready for clean connection!")
    return wlan, ap