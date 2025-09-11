# Async UI Blocking Debug Plan

CURRENT PHASE: 2

## Problem Statement

Master device server requests are causing UI to freeze during response waiting. Need to isolate whether this is:
1. Improper async/await usage in server code
2. Blocking I/O operations not yielding control
3. Event loop integration issues with GUI framework

## Phase List

- Phase 1: Create Test Async Button and Function
- Phase 2: Analyze Server Request Code for Blocking Operations
- Phase 3: Compare Working vs Broken Async Patterns
- Phase 4: Fix Identified Blocking Issues

## Phase 1: Create Test Async Button and Function

**Goal**: Establish baseline async behavior test
**Risk Level**: Low
**Status**: COMPLETE ✅

**Implementation**:
1. ✅ Add "Test Async" button to MainScreen
2. ✅ Create async test function with 3-second uasyncio.sleep_ms(3000)
3. ✅ Function should print result after delay
4. ✅ Verify UI remains responsive during 3-second wait

**Success Criteria**:
- ✅ Button appears on MainScreen
- ✅ Clicking button triggers 3-second async operation
- ✅ UI navigation remains functional during wait
- ✅ Result prints after 3 seconds

**Results**: Test confirmed that GUI async integration works correctly. UI remains responsive during async operations when properly implemented.

## Phase 2: Analyze Server Request Code for Blocking Operations

**Goal**: Identify specific blocking patterns in master server
**Risk Level**: Medium
**Status**: COMPLETE ✅

**Investigation Points**:
- ✅ Review master_server.py request handling
- ✅ Check for synchronous HTTP requests
- ✅ Identify non-async I/O operations
- ✅ Look for missing await keywords

**BLOCKING ISSUE IDENTIFIED**: 

**Location**: `master_controller.py:117` in `ping_targets()` method

**Problem**: Synchronous HTTP requests in async function
```python
async def ping_targets(self):  # ❌ Marked async but...
    for target_name, target_info in self.targets.items():
        response = urequests.get(target_url, timeout=10)  # ❌ BLOCKS HERE!
```

**Root Cause**: 
- `urequests.get()` is **synchronous** and blocks the entire event loop
- 10-second timeout per target can freeze UI for extended periods
- Sequential processing compounds blocking time with multiple targets

**Impact**: Even though debug screen uses `reg_task()` correctly and controller method is marked `async`, the synchronous HTTP call inside the async function blocks the GUI event loop.

## Phase 3: Compare Working vs Broken Async Patterns

**Goal**: Document correct vs incorrect async usage
**Risk Level**: Low
**Status**: COMPLETE ✅

**Analysis**:
- ✅ Compare test function (working) vs server requests (broken)
- ✅ Document proper uasyncio integration patterns
- ✅ Identify GUI event loop best practices

**WORKING PATTERN** (Test Async Button):
```python
async def _test_async_function(self):
    print("⏳ Starting 3-second async test...")
    await uasyncio.sleep_ms(3000)  # ✅ Yields control to event loop
    print("✅ Async test completed!")
```

**BROKEN PATTERN** (Ping Function):
```python
async def ping_targets(self):
    for target_name, target_info in self.targets.items():
        response = urequests.get(target_url, timeout=10)  # ❌ Blocks event loop
```

**Key Difference**: Working pattern uses `await uasyncio.sleep_ms()` which yields control back to the event loop, while broken pattern uses synchronous `urequests.get()` which blocks everything.

## Phase 4: Fix Identified Blocking Issues

**Goal**: Implement non-blocking server operations
**Risk Level**: Medium
**Status**: READY FOR TESTING ✅

**Implementation Options**:
1. **Add Event Loop Yields**: Insert `await uasyncio.sleep_ms(0)` between HTTP requests
2. **Reduce Timeouts**: Change from 10 seconds to 2-3 seconds per request
3. **Implement Async HTTP**: Use async HTTP library or raw sockets (if available)
4. **Concurrent Requests**: Use `uasyncio.gather()` for parallel pinging

**Implemented Approach**: Option 1 (yields) + Option 2 (reduced timeouts) for immediate fix.

**Changes Made**:
- ✅ `master_controller.py` - Added `await uasyncio.sleep_ms(0)` before each `urequests.get()` call
- ✅ `master_controller.py` - Reduced timeout from 10s to 3s for all HTTP requests  
- ✅ `target_server.py` - Added 3-second test delay to /ping endpoint (marked for cleanup)

**Files Modified**:
- `src/master/master_controller.py` - Fixed `ping_targets()` method
- `src/target/target_server.py` - Added test delay to ping endpoint

**Test Setup**: Target server now delays 3 seconds on ping responses to simulate slow network conditions and test UI responsiveness.