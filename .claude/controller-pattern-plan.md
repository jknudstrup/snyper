# MasterController Pattern Implementation Plan

## Goal
Replace event-driven architecture with simple Controller pattern for shared state management.

## Phase 1: Create MasterController Class
**Status**: Pending

### Task 1: Design MasterController
- Create new file `master_controller.py`
- Create `SystemState` class for persistent state (config values, connected_clients)
- Create `GameState` class for game-specific state (score, active_targets, game_running)
- Create `MasterController` class containing both state objects and server instance
- Methods: `start_server()`, `register_target()`, `get_targets()`, `ping_targets()`

### Task 2: Integrate with master.py
- Instantiate `MasterController` in `run_master()`
- Pass controller instance to MainScreen instead of game_state
- Start server through controller

### Task 3: Update Screen Constructors
- MainScreen receives controller instance
- Pass same controller to DebugScreen
- DebugScreen uses `controller.get_targets()` for dropdown

## Phase 2: Fix Target Registration
**Status**: Pending

### Task 4: Update MasterServer
- MasterServer receives controller instead of game_state
- Registration calls `controller.register_target(id, ip)` 
- Updates controller.system_state.connected_clients and target_ips
- Direct method calls instead of attribute mutation

### Task 5: Test Dropdown Fix
- Verify targets appear in dropdown after registration
- Test real-time updates work correctly

## Benefits
- ✅ Single source of truth (controller instance)
- ✅ Direct method calls (no event complexity)
- ✅ GUI-friendly (all same thread, shared references)
- ✅ Simple debugging and testing

## Key Files to Modify
- `master_controller.py` - **NEW FILE** - MasterController, SystemState, GameState classes
- `master.py` - Import controller, create instance, start services
- `master_server.py` - Use controller for registration (system_state updates)
- `views/main_screen.py` - Accept controller, pass to children
- `views/debug_screen.py` - Use controller.get_targets() from system_state

## State Management Design

### SystemState Class
**Purpose**: Persistent state that survives across game sessions
**Contains**:
- All config values (ssid, password, server_ip, port, node_id)
- connected_clients (moved from GameState)  
- target_ips dictionary (for ping functionality)

### GameState Class  
**Purpose**: Game-specific state that resets between games
**Contains**:
- score
- active_targets
- game_running flag

### Benefits of Separation
- ✅ Clear distinction between system vs game state
- ✅ Game resets don't affect client connections
- ✅ Config changes don't affect current game
- ✅ Better organization and maintainability

## Architecture Overview
```
master.py → imports MasterController from master_controller.py
    ↓
MasterController → {SystemState, GameState, MasterServer}
    ↓                             ↓
MainScreen → DebugScreen → controller.get_targets()
```

## File Structure
```
src/
├── master.py              # Entry point, creates controller
├── master_controller.py   # NEW - Controller class
├── master_server.py       # HTTP server, uses controller
├── helpers.py             # Utility functions only
└── views/
    ├── main_screen.py     # Receives controller
    └── debug_screen.py    # Uses controller methods
```