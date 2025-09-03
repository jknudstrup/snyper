# MasterController/MasterServer Architecture Refactor Plan

## Problem Analysis

**CRITICAL ISSUE**: Circular dependency between MasterController and MasterServer
- Controller creates server instance and passes `self` as parameter
- Server stores reference to controller as `self.controller`
- This creates a circular reference that's confusing and error-prone
- Current architecture violates single responsibility and clear hierarchy

## Current Problematic Architecture

```python
# master_controller.py:43
self.master_server = MasterServer(self)  # Passes controller to server

# master_server.py:12
def __init__(self, controller):
    self.controller = controller  # Server stores controller reference
```

## Target Architecture

**CLEAR HIERARCHY**: Controller owns server, server communicates back via callbacks/events

```
MasterController (owns)
└── MasterServer (contained within)
    ├── HTTP Routes (handle requests)
    └── Callback System (communicate back to controller)
```

## Phase 1: Server Creation Refactor
**Goal**: Move server instantiation inside controller
**Risk Level**: Low
**Status**: Pending

### Changes Required:

1. **MasterController.py**:
   - Remove `controller` parameter from `MasterServer()` instantiation
   - Rename `self.master_server` → `self.server` for conciseness
   - Move server creation from `start_server()` to `__init__()`

2. **MasterServer.py**:
   - Remove `controller` parameter from `__init__()`
   - Remove all `self.controller` references

3. **master.py**:
   - Update to call `controller.start_server()` for WiFi + HTTP startup

## Phase 2: Communication Architecture Design
**Goal**: Replace `self.controller` references with proper communication pattern
**Risk Level**: Medium
**Status**: Pending

### Communication Patterns to Evaluate:

**Option A: Callback Functions**
```python
class MasterServer:
    def __init__(self, on_target_register=None, on_target_hit=None):
        self.on_target_register = on_target_register
        self.on_target_hit = on_target_hit
    
    # In routes:
    if self.on_target_register:
        self.on_target_register(client_id, client_ip)
```

**Option B: Event System** (If events module exists)
```python
# In server routes:
emit_event(EventTypes.TARGET_REGISTERED, {"client_id": client_id, "ip": client_ip})
```

**Option C: Return Value + Controller Polling**
```python
# Server stores pending actions, controller retrieves them
class MasterServer:
    def __init__(self):
        self.pending_registrations = []
    
    def get_pending_registrations(self):
        # Return and clear pending items
```

### Current `self.controller` References to Replace:

1. **Registration**: `self.controller.register_target(client_id, client_ip)` (line 43)
2. **Game State Access**: 
   - `self.controller.game_state.active_targets` (line 54)
   - `self.controller.game_state.score` (lines 56, 59)
3. **System State Access**: 
   - `self.controller.system_state` (line 19)
   - `self.controller.system_state.server_ip/port` (lines 65, 67)

## Phase 3: WiFi Access Point Integration
**Goal**: Move WiFi AP management into server startup
**Risk Level**: Medium  
**Status**: Pending

### Current Issue:
- `start_ap()` method references `self.controller.system_state`
- Need to pass system state or make AP management part of controller

### Solution Options:

**Option A: Pass SystemState to Server**
```python
class MasterServer:
    def __init__(self, system_state):
        self.system_state = system_state
```

**Option B: Controller Manages AP, Server Only HTTP**
```python
# In MasterController:
async def start_server(self):
    await self.start_ap()  # Controller handles AP
    return self.server.start_http_server()  # Server only does HTTP
```

## Phase 4: Method Cleanup and Testing
**Goal**: Clean up method signatures and test integration
**Risk Level**: Low
**Status**: Pending

### Tasks:
1. Remove unused parameters from server methods
2. Update all route handlers to use new communication pattern
3. Test target registration flow
4. Test game state updates
5. Verify WiFi AP + HTTP server startup sequence

## Implementation Notes

### Critical Considerations:
- **Memory fragmentation**: Maintain current import order (server before GUI)
- **Async compatibility**: Ensure callback/event system works with GUI event loop
- **Error handling**: Preserve current error logging patterns
- **State management**: Don't break existing SystemState/GameState separation

### Testing Strategy:
1. **Unit**: Test each phase independently
2. **Integration**: Test controller + server startup sequence
3. **System**: Test full target registration and game flow
4. **Hardware**: Deploy to device and verify WiFi AP + HTTP functionality

## Success Criteria

- ✅ No circular dependencies between controller and server
- ✅ Clear hierarchical relationship: Controller owns Server  
- ✅ Server can communicate state changes back to controller
- ✅ All existing functionality preserved (registration, game state, WiFi AP)
- ✅ Clean, maintainable code with single responsibility principle
- ✅ Memory allocation patterns preserved

## Rollback Plan

If refactor fails:
1. Revert to git commit before refactor started
2. Document specific failure points for future attempts
3. Consider alternative approaches (dependency injection, mediator pattern)