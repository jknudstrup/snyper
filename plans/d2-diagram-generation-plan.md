# D2 Diagram Generation Plan

CURRENT PHASE: 1

## Phase List

- **Phase 1**: Project Analysis and Diagram Planning
- **Phase 2**: Master Architecture Diagrams
- **Phase 3**: Target Architecture Diagrams
- **Phase 4**: Network Communication Diagrams
- **Phase 5**: GUI Flow Diagrams
- **Phase 6**: Complete System Integration Diagram

## Phase 1: Project Analysis and Diagram Planning ⏳
**Goal**: Analyze codebase structure and define comprehensive diagram strategy
**Risk Level**: Low
**Status**: In Progress

**Tasks**:
1. ✅ Document all Python modules and their relationships
2. ✅ Identify key architectural patterns (MasterController, event queues, GUI screens)
3. ✅ Define D2 diagram types needed for complete system documentation
4. 🔄 Create planning document with incremental implementation approach

**Discovered Architecture Patterns**:
- **MasterController Pattern**: Central controller managing all system state (`master_controller.py`)
- **Event-Driven Target System**: Async event queue processing (`target_events.py`, `target_controller.py`)
- **GUI-First Architecture**: micropython-micro-gui controls main event loop
- **Multiplexed Communication**: Parallel async communication with all targets
- **Screen Navigation System**: Modular screen architecture with navigation helpers

**Key Modules Identified**:

**Master Side**:
- `master.py` - Entry point and GUI integration
- `master_controller.py` - Central controller with SystemState/GameState
- `master_server.py` - HTTP server and WiFi AP functionality
- `views/` - GUI screen modules (MainScreen, NewGameScreen, OptionsScreen, DebugScreen)

**Target Side**:
- `target.py` - Entry point
- `target_controller.py` - Executive component managing target state
- `target_server.py` - HTTP endpoints and response handling
- `peripheral_controller.py` - Hardware control (servo, sensors)
- `target_events.py` - Event queue system

**Shared**:
- `config/config.py` - Configuration management
- `utils/socket_protocol.py` - Network communication utilities
- `display/` - Hardware display and GPIO handling

## Phase 2: Master Architecture Diagrams 📋
**Goal**: Create detailed diagrams for master device architecture
**Risk Level**: Low
**Status**: Pending

**Sub-diagrams**:
1. **Master Component Architecture** - Core classes and their relationships
2. **Master Control Flow** - MasterController operations and async task management
3. **Master Server Architecture** - HTTP endpoints and WiFi AP functionality
4. **GUI Screen Hierarchy** - MainScreen, NewGameScreen, OptionsScreen, DebugScreen relationships

**Key Relationships to Document**:
- MasterController → MasterServer (composition)
- GUI Screens → MasterController (dependency injection)
- MasterController → Target tracking (self.targets dict)
- Async task registration via GUI framework

## Phase 3: Target Architecture Diagrams 🎯
**Goal**: Create detailed diagrams for target device architecture
**Risk Level**: Low
**Status**: Pending

**Sub-diagrams**:
1. **Target Component Architecture** - TargetController, PeripheralController, event system
2. **Target Event Flow** - Event queue processing and command handling
3. **Target Server Architecture** - HTTP endpoints and response handling
4. **Target State Machine** - Standing/down/active states and transitions

**Key Relationships to Document**:
- TargetController → PeripheralController (composition)
- TargetController → TargetServer (collaboration)
- Event queue system (target_events.py)
- State transitions (is_active, is_standing, hit_detected)

## Phase 4: Network Communication Diagrams 🌐
**Goal**: Document inter-device communication patterns
**Risk Level**: Medium
**Status**: Pending

**Sub-diagrams**:
1. **Registration Sequence** - Target registration with master
2. **Command Flow** - Master sending commands to targets (ping, raise, lower, activate)
3. **Multiplexed Communication** - Parallel target communication architecture
4. **Socket Protocol** - Low-level communication patterns

**Communication Patterns Identified**:
- WiFi AP on master, targets connect as clients
- HTTP-based command protocol
- Async multiplexed target communication (`_message_all()`)
- Target registration callback system

## Phase 5: GUI Flow Diagrams 🖥️
**Goal**: Document user interface navigation and interactions
**Risk Level**: Low
**Status**: Pending

**Sub-diagrams**:
1. **Screen Navigation Flow** - User journey through GUI screens
2. **Button Interaction Flow** - Physical button handling and GPIO integration
3. **Display Rendering Flow** - ST7789 display driver and GUI framework integration

**GUI Architecture Identified**:
- Screen.change() for forward navigation
- CloseButton for back navigation
- ButtonY for visual selection indication
- Font14/freesans20 font usage patterns

## Phase 6: Complete System Integration Diagram 🎮
**Goal**: Create comprehensive system overview showing all components
**Risk Level**: Low
**Status**: Pending

**Tasks**:
1. Integrate all previous diagrams into system overview
2. Show master-target relationships at high level
3. Include hardware components (ST7789 display, GPIO, WiFi)
4. Document deployment differences (dev vs device mode)

## Implementation Approach

**File Organization**:
- Create `docs/diagrams/` directory for D2 source files
- Separate files for each diagram type (`master-architecture.d2`, `target-architecture.d2`, etc.)
- Generated SVG outputs alongside source files

**D2 Syntax Strategy**:
- Use containers for logical grouping
- Use arrows for relationships and data flow
- Use different shapes for different component types
- Use colors to distinguish master vs target components

**Incremental Development**:
- Start with simple component diagrams
- Add complexity gradually (relationships, data flow, state machines)
- Test each diagram renders correctly before moving to next
- Document any D2 syntax discoveries for future reference

**Success Criteria**:
- All major system components documented visually
- Clear representation of async task flows and event handling
- Network communication patterns clearly illustrated
- GUI navigation flows easy to follow
- Complete system overview provides high-level understanding

## Notes

**Critical Architecture Insights for Diagrams**:
- GUI-first architecture means all async tasks must be registered via `self.reg_task()`
- Memory allocation order matters: server imports before GUI
- Single event loop supremacy: everything runs in GUI's async context
- Controller pattern with dependency injection throughout GUI screens
- Multiplexed communication enables parallel target operations