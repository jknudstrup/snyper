# Target Architecture Refactor Plan
CURRENT PHASE: 1

## Phase List
- Phase 1: Interface Specification and Design
- Phase 2: Create Global Event Queue System
- Phase 3: Refactor TargetController as Executive
- Phase 4: Convert Server to Subordinate
- Phase 5: Convert Peripheral to Subordinate
- Phase 6: Implement Three-Loop Coordination

## Architecture Overview

**Executive/Subordinate Model:**
- **TargetController**: Executive - commands subordinates, processes incoming events, maintains state
- **TargetServer**: Subordinate - executes controller commands, listens for HTTP requests → queue
- **PeripheralController**: Subordinate - executes controller commands, listens for sensor readings → queue
- **Global Queue**: Single channel for all external events → TargetController

**Async Loop Structure:**
```python
asyncio.gather(
    server.listen_for_requests(),      # HTTP server loop
    peripheral.monitor_sensors(),      # Sensor reading loop  
    controller.process_events()        # Event processing loop
)
```

---

## Phase 1: Interface Specification and Design

**Goal**: Define clear interfaces and contracts before implementation
**Risk Level**: Low
**Status**: Pending

**Deliverables:**
1. Event message types and structure specification
2. TargetController command interface definition
3. Subordinate component interface contracts
4. Global queue implementation specification
5. Error handling and shutdown protocols

**Event Types:**
- `HttpRequestEvent`: Incoming HTTP commands from master
- `SensorHitEvent`: Hit detection from piezo sensor
- `SystemEvent`: Startup, shutdown, error conditions

**Command Interface (Controller → Subordinates):**
- Server: `start_server()`, `stop_server()`, `send_response()`
- Peripheral: `raise_target()`, `lower_target()`, `start_monitoring()`, `stop_monitoring()`

**Event Interface (Subordinates → Controller):**
- Global queue with structured event objects
- Single `controller.process_events()` consumer

---

## Phase 2: Create Global Event Queue System

**Goal**: Implement simple global queue for external events
**Risk Level**: Low
**Status**: Pending

**Tasks:**
- Create global asyncio.Queue instance
- Define event base class and specific event types
- Add queue-based event bubbling utilities
- Test basic queue producer/consumer pattern

---

## Phase 3: Refactor TargetController as Executive

**Goal**: Convert controller to executive that commands subordinates
**Risk Level**: Medium
**Status**: Pending

**Tasks:**
- Implement `process_events()` main event loop
- Add direct command methods for server and peripheral control
- Centralize all target state management in controller
- Remove broken event system dependencies

---

## Phase 4: Convert Server to Subordinate

**Goal**: Make server subordinate to controller with queue-based event bubbling
**Risk Level**: Medium
**Status**: Pending

**Tasks:**
- Modify server endpoints to emit events to global queue
- Implement direct command interface from controller
- Remove direct peripheral_controller calls from server
- Test HTTP request → queue → controller flow

---

## Phase 5: Convert Peripheral to Subordinate

**Goal**: Make peripheral subordinate with proper sensor monitoring
**Risk Level**: High
**Status**: Pending

**Tasks:**
- Add sensor monitoring loop with queue event emission
- Implement direct command interface for controller
- Integrate hit detection with proper async sensor reading
- Test sensor → queue → controller → action flow

---

## Phase 6: Implement Three-Loop Coordination

**Goal**: Coordinate all async loops with proper error handling
**Risk Level**: Medium
**Status**: Pending

**Tasks:**
- Set up `asyncio.gather()` for server, sensor, and controller loops
- Test concurrent operation and event flow
- Add proper error handling and graceful shutdown
- Performance testing and optimization