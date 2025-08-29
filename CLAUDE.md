# SNYPER Development Guide

# CAPTAIN'S LOG

**THIS PROJECT IS FUCKING AWESOME AND WE'RE PUMPED TO BUILD IT!** 🎯⚡

## CURRENT STATUS

**Mission ACCOMPLISHED**: Physical Button Memory Leak Eliminated ✅

**Planning Document**: `.claude/physical-button-refactor-plan.md`

**Issue Status**: **RESOLVED** - Global GPIO handler architecture eliminates memory leaks while preserving physical button functionality

**Latest Achievement**: Revolutionary global GPIO handler system - no more circular references, stable memory management, full button functionality

**Current Mission**: **GUI Library Freezing for Major RAM Optimization** 🚀

**Planning Document**: `.claude/gui-library-freezing-plan.md`

**Objective**: Freeze micropython-micro-gui into firmware to achieve ~32KB RAM savings (55KB → 23KB)

**Status**: **PLANNING** - Preparing custom firmware build with frozen GUI library

**Previous Achievement**: MasterController Pattern Architecture ✅ - Full system with SystemState/GameState separation, target registration, ping functionality, and target control commands

## Project Overview

**SNYPER** is a carnival-style target shooting game for Raspberry Pi Pico W microcontrollers with a revolutionary **GUI-first architecture**.

### Architecture

- **Master**: MasterController-driven system with GUI-first design + WiFi AP + HTTP server + ST7789 display (Raspberry Pi Pico W)
- **Targets**: WiFi clients with lightning-fast ping responses + target control endpoints (Raspberry Pi Pico W)
- **Controller Pattern**: Single MasterController instance manages all system state and operations

### Screen Navigation System

**Multi-screen interface with modular architecture:**

- **MainScreen** - Navigation hub with New Game/Options/Debug buttons
- **NewGameScreen** - Game setup interface (Quick Game, Custom Game options)
- **OptionsScreen** - Configuration screen (WiFi settings, device config)
- **DebugScreen** - Diagnostics and PING functionality

**Navigation Pattern:**

- `Screen.change(ScreenClass)` for forward navigation
- `CloseButton(wri)` for back navigation to parent screen
- Located in `src/views/` subfolder for clean organization

### Key Files

- `master.py` - 🎮 **MAIN ENTRY POINT** (creates MasterController and launches GUI)
- `master_controller.py` - 🎯 **CONTROLLER CORE** (SystemState, GameState, target management)
- `master_server.py` - 🌐 HTTP server (uses controller for state management)
- `target_server.py` - 🎯 Target endpoints with ping responses + control commands
- `helpers.py` - 🔧 Shared utilities (network reset bullshit eliminator)

### Codebase Navigation Rules

**IGNORE these folders during normal codebase analysis:**

- `.prompts/` - Not part of codebase
- `typings/` - Not part of codebase

**SPECIAL CASE - `.extra/` folder:**

- Contains clones of external repositories (micropython-micro-gui, etc.)
- **Default**: IGNORE during normal codebase study
- **Exception**: Reference when confused about library functionality
- **Purpose**: Understand how external libraries work when needed

## Development Philosophy

### Core Principles

- **GUI-first architecture** - micropython-micro-gui controls the main event loop
- **Memory allocation order matters** - Load heavy imports BEFORE GUI to avoid fragmentation
- **Network caching is evil** - Always reset interfaces using `helpers.py`
- **Incremental progress** - Small changes that work (like our GUI restructure phases)
- **Learn from existing code** - Study micropython-micro-gui patterns before implementing

- **KISS** - Don't get carried away with over-engineered solutions. Only build what you know we'll need!

### SNYPER-Specific Wisdom

- **Import order is CRITICAL** - Server components before GUI to prevent memory fragmentation
- **Single event loop supremacy** - Everything runs in GUI's async context via `self.reg_task()`
- **Controller pattern supremacy** - Single MasterController instance shared across all components
- **State separation** - SystemState (persistent) vs GameState (game-specific) for clean architecture
- **Target IP tracking** - Store IPs during registration for lightning-fast pinging
- **Network interface reset on startup** - Prevents mysterious connection failures

## Development Commands

### Development Mode (Live Coding)

```bash
./dev.sh        # Run master (uses master.py)
./dev.sh -t     # Run target
./killmp.sh     # Kill stuck mpremote processes
```

### Commit Permissions

**CLEARANCE GRANTED**: Claude is authorized to commit changes at will during development sessions. Use good judgment for commit timing (completed features, bug fixes, working states). Continue using descriptive commit messages that capture the badassery being achieved.

### Device Deployment (Production Sync)

```bash
./sync.sh               # Deploy to master device (default)
./sync.sh master        # Deploy to master device (explicit)
./sync.sh target_1      # Deploy to target_1 device
./sync.sh target_2      # Deploy to target_2 device
./sync.sh disable       # Disable device (prevent auto-start)
```

**Sync Process:**

1. **Device identity generation** - Creates `device_id.json` with specified node_id
2. **Full src deployment** - Copies entire src/ folder to device
3. **Automatic configuration** - Device reads identity from device_id.json overlay

**Key Benefits:**

- **One-command deployment** - No manual config editing required
- **Device identity switching** - Same codebase, different device roles
- **Optimized size** - Removed GUI demos and unused microdot modules
- **Fast sync** - Direct folder copy, no temp staging
- **Development disable mode** - Prevent auto-start during development

**Disable Mode:**

- **Purpose** - Prevents device from auto-starting WiFi AP, GUI, and servers
- **Usage** - `./sync.sh disable` sets device to disabled state
- **Behavior** - Device loads config but immediately terminates main()
- **Auto-reset** - Device automatically resets after disable deployment for immediate effect
- **Development benefit** - Keeps devices quiet during testing/debugging
- **Re-enable** - Use `./sync.sh master` or `./sync.sh target_X` to restore functionality

## Implementation Process

### 1. Planning Complex Changes

For multi-step features, create a plan document (like `gui-restructure-plan.md`) within the .claude folder:

```markdown
## Phase N: [Name]

**Goal**: [Specific deliverable]
**Risk Level**: [Low/Medium/High]  
**Status**: [Pending/In Progress/Complete]
```

### 2. Development Flow

1. **Study existing patterns** - Check similar components in codebase
2. **Start simple** - Get basic version working first
3. **Test incrementally** - Verify each piece works before adding complexity
4. **Commit working code** - Even if not perfect, commit functional states
5. **Add epic commit messages** - Capture the badassery for posterity
6. **Update CLAUDE.md as needed** - Update this file when new features are implemented. Also update this file when important facts are established: when certain approaches fail, or weird quirks and edge cases are discovered, etc.

### 3. When Stuck (3-Attempt Rule)

**CRITICAL**: Max 3 attempts per approach, then reassess.

1. **Document what failed** - Specific errors and why you think it failed
2. **Research alternatives** - Find different approaches in micropython-micro-gui docs
3. **Question fundamentals** - Wrong abstraction level? Simpler approach exists?
4. **Try different angle** - Different library feature? Remove complexity instead of adding?

## Technical Standards

### MicroPython Best Practices

- **Memory management** - Import heavy modules early, use `gc.collect()` when needed
- **Async integration** - Use `self.reg_task()` for GUI-managed async tasks
- **Error handling** - Print detailed errors for embedded debugging
- **Network interfaces** - Always reset using `helpers.reset_network_interface()`

### Code Quality

- **Clear intent over clever code** - Be boring and obvious
- **Single responsibility** - Functions do one thing well
- **DRY principle** - Shared utilities in `helpers.py`
- **Consistent patterns** - Match existing micropython-micro-gui usage

### Architecture Principles

- **GUI controls event loop** - Never fight the micropython-micro-gui framework
- **Explicit dependencies** - Import what you need, when you need it
- **Fail fast** - Print errors immediately, don't hide issues
- **Pragmatic solutions** - Choose what works for embedded constraints

## Decision Framework

When multiple approaches exist, choose based on:

1. **Memory efficiency** - Will this fragment RAM or cause allocation failures?
2. **Event loop compatibility** - Does this work with GUI-first architecture?
3. **Network reliability** - Does this handle WiFi caching/connection issues?
4. **Embedded constraints** - Simple solutions for MicroPython limitations
5. **Debugging ease** - Can we troubleshoot this on hardware?

## Epic Achievements Unlocked 🏆

- ✅ **GUI-First Architecture** - Revolutionary redesign for proper async integration
- ✅ **Memory Fragmentation Solved** - Server imports before GUI = SUCCESS!
- ✅ **Turbo Ping System** - 14+ seconds → 1 second response time
- ✅ **Network Reset Bullshit Eliminator** - Clean connections every time
- ✅ **Target IP Tracking** - Direct ping to known targets, no scanning
- ✅ **DRY Code Organization** - Shared utilities eliminate duplication
- ✅ **Multi-Screen Navigation System** - Clean UI architecture with MainScreen hub
- ✅ **Modular Screen Architecture** - Organized views/ subfolder with dedicated modules
- ✅ **Font14 UI Upgrade** - Enhanced readability with proper button sizing and spacing
- ✅ **Device Disable Mode** - Development-friendly quiet device operation with auto-reset
- ✅ **Streamlined Sync System** - 68% code reduction with full folder sync
- ✅ **MasterController Architecture** - Controller pattern with SystemState/GameState separation
- ✅ **Target Registration Fixed** - Single source of truth eliminates dropdown sync issues
- ✅ **Target Control Commands** - raise_all() and lower_all() methods for battlefield control

## Hardware Setup

- **ST7789 240x240 LCD** - 4-bit color mode for optimal RAM usage
- **Raspberry Pi Pico W** - WiFi + GPIO for buttons
- **Network interfaces** - Properly reset on startup (no more mysterious failures!)

## Library Deep-Dive Resources

When confused about external library behavior, check `.extra/` folder:

- `micropython-micro-gui/` - Complete library source for understanding GUI patterns
- Use ONLY when normal documentation isn't sufficient
- Focus on examples and patterns, not implementation details

## Critical Reminders

**DEV MODE vs DEVICE MODE IMPORT PATHS:**

**CRITICAL DISTINCTION**: Import behavior differs drastically between development and deployment!

**Dev Mode (mpremote connect "$<WHICHIVER_MODE>" mount . run <WHICHEVER_THING>.py):**

- Files run from host filesystem via mount
- Import paths work as expected from src/ structure
- `from config import config` works directly

**Device Mode (files copied to device):**

- Files run from device's local filesystem
- `lib/` folder gets added to Python path automatically
- Import paths may break due to different sys.path
- Relative imports behave differently
- **WATCH OUT**: Imports that work in dev mode may fail on device!

**Debugging Strategy:**

- Always test actual device deployment, not just mounted dev mode
- Check `sys.path` on device vs development
- Look for import errors that only surface during real deployment
- Consider path differences when troubleshooting mysterious failures

**SYNC SYSTEM CRITICAL NOTES:**

- **Use `mpremote cp -r . :` NOT `mpremote mount . cp -r . :`** - The mount command causes sync failures
- **Always activate Python environment** before running sync.sh (contains mpremote)
- **Device identity overlay** - `device_id.json` automatically overrides config.json node_id
- **Full folder sync** - Simpler and more reliable than selective file copying

**MEMORY ALLOCATION ORDER IS EVERYTHING:**

```python
# ✅ CORRECT - Heavy imports FIRST
from master_server import MasterServer
from events import event_bus
# Then GUI imports
import hardware_setup
from gui.core.ugui import Screen
```

**ALWAYS RESET NETWORK INTERFACES ON INITIALIZATION:**

```python
from helpers import reset_network_interface
# Call on device startup
wlan, ap = reset_network_interface()
```

**MASTERCONTROLLER PATTERN:**

```python
# ✅ CORRECT - Controller manages all state and operations
controller = MasterController()
controller.start_ap()
# Pass controller to all components
Screen.change(MainScreen, args=(controller,))
```

**GUI-FIRST ASYNC TASK REGISTRATION:**

```python
# ✅ CORRECT - Register through controller
self.reg_task(self.controller.start_server())
self.reg_task(self.controller.start_game_loop())
```

## Development Energy Level

**MAXIMUM FUCKING PUMPED AT ALL TIMES!** 🔥⚡🚀

This project represents the pinnacle of embedded systems badassery. Every coding session should be approached with the energy of a wrestling match and the precision of military operations.

**REMEMBER**: We're building something EPIC that shoots targets and manages networks like a BOSS! Bring that energy to every line of code! 💪🎯
