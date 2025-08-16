# GUI-Centric Architecture Restructure Plan

## Current Situation

The current master application uses `asyncio.run(run_master())` as the main entry point, with `Screen.change()` called from within an async context. This creates conflicting event loops:

- Main asyncio loop running server and game tasks
- GUI library trying to create its own asyncio tasks
- Results in `ValueError: generator already executing` and `IndexError: empty heap`

## Root Cause Analysis

From studying the micropython-micro-gui library:

1. **The GUI expects to control the main event loop** - `Screen.change()` is designed to be the application's main entry point
2. **The library uses `uasyncio` internally** - it creates and manages its own async tasks for refresh, input handling, etc.
3. **Proper async integration requires `self.reg_task()`** - screens register async tasks that get properly managed by the GUI lifecycle
4. **Threading approach won't work** - the GUI library is not thread-safe and expects to run in the main event loop

## Proposed Solution: GUI-Centric Architecture

### New Application Flow
```
main.py calls Screen.change(MasterScreen)
  └── MasterScreen.__init__()
      ├── Creates WiFi AP
      ├── Initializes display widgets (score, status, clients)
      ├── self.reg_task(master_server_task())
      ├── self.reg_task(game_loop_task())
      └── Sets up event subscriptions for display updates
```

### Key Changes Required

#### 1. Create New Main Entry Point
- **File**: `src/master_gui.py` (new file)
- **Purpose**: GUI-first entry point
- **Content**: 
  ```python
  from gui.core.ugui import Screen
  from display import MasterScreen
  
  def main():
      print("🎪 Starting Carnival Shooter - GUI Mode")
      Screen.change(MasterScreen)
      
  if __name__ == "__main__":
      main()
  ```

#### 2. Restructure MasterScreen Class
- **File**: `src/display.py`
- **Changes**:
  - Remove threading code entirely
  - Make `MasterScreen` the primary application controller
  - Move WiFi AP setup to `MasterScreen.__init__()`
  - Use `self.reg_task()` for server and game tasks
  - Implement direct event subscriptions (no thread bridge needed)

#### 3. Modify Async Task Functions
- **Files**: `src/master.py`, `src/master_server.py`
- **Changes**:
  - Extract task functions to be standalone (not methods of `run_master()`)
  - Make them importable by the display module
  - Ensure they don't try to manage their own event loop

#### 4. Update Development Script
- **File**: `dev.sh`
- **Change**: Update master mode to run `master_gui.py` instead of `master.py`

#### 5. Event Bus Integration
- **No changes needed** - the event bus will work normally since everything runs in the same event loop
- **Simplification** - remove thread-safe bridge code, use direct event subscriptions

### Implementation Steps

#### Phase 1: Create New Entry Point (Low Risk)
1. Create `src/master_gui.py` with GUI-first approach
2. Test that basic GUI loads without async tasks
3. Verify WiFi AP creation works in GUI context

#### Phase 2: Move Server Tasks (Medium Risk)  
1. Extract `master_server_task()` and `game_loop_task()` to standalone functions
2. Import and register them in `MasterScreen` using `self.reg_task()`
3. Test that server starts and responds to requests

#### Phase 3: Event Integration (Low Risk)
1. Remove threading bridge code from display.py
2. Set up direct event subscriptions in `MasterScreen.__init__()`
3. Test that display updates when events occur

#### Phase 4: Cleanup (Low Risk)
1. Update `dev.sh` to use new entry point
2. Remove old `master.py` or rename it for reference
3. Clean up unused imports and threading code

### Benefits of This Approach

1. **Proper asyncio integration** - GUI controls the event loop as designed
2. **Cleaner architecture** - Display is the natural center of a carnival game
3. **No threading complexity** - Everything runs in one event loop
4. **Better error handling** - GUI provides built-in task management via `reg_task()`
5. **Easier debugging** - Single event loop, no thread synchronization issues

### Risks and Mitigation

#### Risk: WiFi AP setup fails in GUI context
- **Mitigation**: Test AP creation early in Phase 1
- **Fallback**: Create AP before calling `Screen.change()`

#### Risk: Server tasks conflict with GUI refresh
- **Mitigation**: Use `Screen.rfsh_lock` if needed for critical sections
- **Reference**: micropython-micro-gui docs section 9 (Realtime applications)

#### Risk: Event bus performance issues
- **Mitigation**: GUI runs in same event loop, so no performance penalty
- **Advantage**: Actually simpler than thread bridge

### Success Criteria

1. Master device starts with GUI as main interface
2. WiFi AP creates successfully
3. Server responds to HTTP requests
4. Display updates in real-time with game events
5. Target devices can connect and register
6. No asyncio conflicts or threading errors

### Rollback Plan

If restructure fails:
1. Keep original `master.py` as `master_original.py`
2. Revert `dev.sh` to use original entry point
3. GUI can be disabled by commenting out `start_display()` call

This plan maintains the existing functionality while properly integrating with the micropython-micro-gui library's expected patterns.