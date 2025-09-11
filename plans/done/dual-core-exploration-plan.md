# Dual-Core Exploration Plan

## Objective

Test and evaluate dual-core parallelism on Raspberry Pi Pico W for SNYPER game performance improvements.

## Research Findings

**RP2040 Dual-Core Capabilities:**
- **2 ARM Cortex-M0+ cores** - True hardware parallelism
- **MicroPython `_thread` module** - Access to second core
- **Shared memory space** - Global variables accessible from both cores
- **Hardware limitations** - Thread1 has WiFi communication issues on Pico W

**Key Constraints:**
- **Maximum 2 threads** - One per core only
- **Experimental status** - `_thread` API not fully stable
- **Resource contention** - Requires manual locking with `_thread.allocate_lock()`
- **WiFi issues** - Core 1 cannot reliably control WiFi/onboard LED
- **Stability concerns** - Reports of crashes after extended operation

## VERY BASIC Test Plan

### Phase 1: Basic Threading Test (30 min)
**Goal**: Verify `_thread` works in SNYPER environment

**Test 1: Simple Parallel Execution**
```python
import _thread
import time

def background_task():
    for i in range(10):
        print(f"Background: {i}")
        time.sleep(1)

def main_task():
    for i in range(10):
        print(f"Main: {i}")
        time.sleep(1)

# Start background thread on Core 1
_thread.start_new_thread(background_task, ())
# Run main task on Core 0
main_task()
```

**Success criteria:** Both tasks print interleaved without crashes

### Phase 2: Resource Sharing Test (20 min)
**Goal**: Test shared state management

**Test 2: Shared Counter with Lock**
```python
import _thread

counter = 0
lock = _thread.allocate_lock()

def increment_worker(name, iterations):
    global counter
    for i in range(iterations):
        with lock:
            counter += 1
            print(f"{name}: {counter}")

_thread.start_new_thread(increment_worker, ("Core1", 5))
increment_worker("Core0", 5)
```

**Success criteria:** Counter reaches 10 without race conditions

### Phase 3: SNYPER Integration Test (45 min)
**Goal**: Test parallel execution with SNYPER components

**Test 3: Background Ping Handler**
```python
import _thread

def background_ping_handler():
    """Run continuous target pinging on Core 1"""
    while True:
        # Ping all registered targets
        # Update target status
        # Sleep briefly
        pass

def main_gui_loop():
    """Main GUI on Core 0"""
    # Normal SNYPER GUI operation
    pass

# Start ping handler on Core 1  
_thread.start_new_thread(background_ping_handler, ())
# Run GUI on Core 0
main_gui_loop()
```

**Success criteria:** GUI responsive while background pinging operates

## Risk Assessment

**HIGH RISK factors:**
- **WiFi conflicts** - Core 1 cannot control WiFi reliably
- **Experimental API** - `_thread` may have undocumented issues  
- **Memory corruption** - Improper locking could crash system
- **GUI interference** - Threading might disrupt micropython-micro-gui event loop

**MEDIUM RISK factors:**
- **Performance overhead** - Locking/synchronization costs
- **Debugging difficulty** - Thread-related bugs harder to trace
- **Code complexity** - Error-prone shared state management

## Alternative Approaches to Consider

**If threading proves problematic:**

1. **Async optimization** - Better uasyncio task scheduling
2. **PIO utilization** - Use Programmable IO for parallel operations  
3. **Interrupt-driven** - Hardware interrupts for time-critical tasks
4. **Timer-based** - Precise timing without threading complexity

## Success Criteria

**Phase 1 Success**: Basic threading works without crashes
**Phase 2 Success**: Resource sharing works reliably  
**Phase 3 Success**: SNYPER components can run in parallel safely

**Overall Success**: Measurable performance improvement without stability loss

## Failure Exit Strategy

If any phase fails or shows instability:
1. **Document specific failure modes**
2. **Revert to single-core async approach**
3. **Consider alternative optimization strategies**
4. **Update CLAUDE.md with findings**

## Implementation Notes

- **Test in isolation first** - Minimal test scripts before SNYPER integration
- **Monitor for memory leaks** - Use `gc.mem_free()` extensively  
- **WiFi limitation workaround** - Keep all network operations on Core 0
- **Graceful degradation** - Fallback to single-core if threading fails