"""
Basic Dual-Core Threading Test for SNYPER
Tests parallel execution on RP2040's dual ARM Cortex-M0+ cores
"""

import _thread
import time
import gc

# Shared counter for testing thread safety
shared_counter = 0
counter_lock = _thread.allocate_lock()

def core1_task():
    """Task to run on Core 1"""
    global shared_counter
    
    print("[CORE1] Starting Core 1 task...")
    
    for i in range(10):
        print(f"[CORE1] Count: {i}")
        
        # Test shared counter with locking
        with counter_lock:
            shared_counter += 1
            current = shared_counter
        
        print(f"[CORE1] Shared counter: {current}")
        time.sleep_ms(300)  # 300ms delay
    
    print("[CORE1] Core 1 task completed!")

def core0_task():
    """Task to run on Core 0 (main thread)"""
    global shared_counter
    
    print("[CORE0] Starting Core 0 task...")
    
    for i in range(15):
        print(f"[CORE0] Count: {i}")
        
        # Test shared counter with locking
        with counter_lock:
            shared_counter += 10
            current = shared_counter
        
        print(f"[CORE0] Shared counter: {current}")
        time.sleep_ms(200)  # 200ms delay
        
        # Show memory usage periodically
        if i % 5 == 0:
            free_mem = gc.mem_free()
            print(f"[CORE0] Free memory: {free_mem} bytes")
    
    print("[CORE0] Core 0 task completed!")

def test_dual_core():
    """Main dual-core test function"""
    print("=" * 50)
    print("🚀 SNYPER Dual-Core Threading Test")
    print("=" * 50)
    print("Testing parallel execution on RP2040 dual cores...")
    print("Expected: Interleaved output from both cores")
    print()
    
    # Show initial memory
    print(f"Initial free memory: {gc.mem_free()} bytes")
    print()
    
    # Start Core 1 thread
    try:
        _thread.start_new_thread(core1_task, ())
        print("✅ Successfully started Core 1 thread")
    except Exception as e:
        print(f"❌ Failed to start Core 1 thread: {e}")
        return False
    
    # Run Core 0 task (main thread)
    core0_task()
    
    # Wait a bit for Core 1 to finish
    time.sleep(2)
    
    print()
    print("=" * 50)
    print("🎯 Test Results")
    print("=" * 50)
    print(f"Final shared counter value: {shared_counter}")
    print(f"Final free memory: {gc.mem_free()} bytes")
    
    # Expected results analysis
    expected_counter = (10 * 1) + (15 * 10)  # Core1: 10*1, Core0: 15*10
    print(f"Expected counter value: {expected_counter}")
    
    if shared_counter == expected_counter:
        print("✅ Shared counter test PASSED - Thread synchronization working!")
    else:
        print(f"⚠️  Shared counter test WARNING - Expected {expected_counter}, got {shared_counter}")
        print("   This could indicate race conditions or timing issues")
    
    print()
    print("If you see interleaved [CORE0] and [CORE1] messages above,")
    print("dual-core threading is working correctly! 🎉")
    print()
    
    return True

if __name__ == "__main__":
    test_dual_core()