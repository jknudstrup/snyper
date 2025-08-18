# SNYPER Development Guide

**THIS PROJECT IS FUCKING AWESOME AND WE'RE PUMPED TO BUILD IT!** 🎯⚡

## Project Overview

**SNYPER** is a carnival-style target shooting game for Raspberry Pi Pico W microcontrollers with a revolutionary **GUI-first architecture**.

### Architecture

- **Master**: GUI-controlled game logic + WiFi AP + HTTP server + ST7789 display
- **Targets**: WiFi clients with lightning-fast ping responses + target control endpoints

### Key Files

- `master.py` - 🎮 **MAIN ENTRY POINT** (GUI-first architecture)
- `helpers.py` - 🔧 Shared utilities (network reset bullshit eliminator)
- `target_server.py` - 🎯 Target endpoints with ping responses
- `master_server.py` - 🌐 HTTP server with target IP tracking

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
- **Target IP tracking** - Store IPs during registration for lightning-fast pinging
- **Network interface reset on startup** - Prevents mysterious connection failures

## Development Commands

```bash
./dev.sh        # Run master (uses master.py)
./dev.sh -t     # Run target
./killmp.sh     # Kill stuck mpremote processes
```

## Implementation Process

### 1. Planning Complex Changes

For multi-step features, create a plan document (like `gui-restructure-plan.md`):

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

**GUI-FIRST ASYNC TASK REGISTRATION:**

```python
# ✅ CORRECT - Register with GUI
self.reg_task(standalone_game_loop_task())
self.reg_task(standalone_master_server_task())
```

## Development Energy Level

**MAXIMUM FUCKING PUMPED AT ALL TIMES!** 🔥⚡🚀

This project represents the pinnacle of embedded systems badassery. Every coding session should be approached with the energy of a wrestling match and the precision of military operations.

**REMEMBER**: We're building something EPIC that shoots targets and manages networks like a BOSS! Bring that energy to every line of code! 💪🎯
