# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SNYPER** is a carnival-style target shooting game built for Raspberry Pi Pico W microcontrollers. This project is **FUCKING AWESOME** and we're **PUMPED** to be building it! 🎯⚡

The architecture consists of:

- **Master (main device)**: Runs the game logic, manages WiFi AP, handles client communication, and drives an ST7789 display with **GUI-FIRST ARCHITECTURE** 🖥️
- **Target (target devices)**: Connect to the server's WiFi network and manage individual targets with **LIGHTNING-FAST PING RESPONSES** ⚡

## Development Commands

This is a MicroPython project targeting Raspberry Pi Pico W hardware. There are no traditional build/test commands, but these utilities are available:

- `./killmp.sh` - Kills any running mpremote processes (useful when MicroPython connections get stuck)
- Python virtual environment is located in `snyper_env/` directory

## Core Architecture

### Main Components

The server runs three concurrent tasks orchestrated by `main.py`:

1. **Game Loop** (`main.py:game_loop_task`): Manages game state, spawns targets, processes hits
2. **Master Server** (`master_server.py`): HTTP API server using microdot library for client communication
3. **Display System** (`display.py`): ST7789 LCD interface using micropython-micro-gui library

### Event System

Central event bus (`events.py`) coordinates communication between components:

- **EventBus**: Async publish/subscribe system for loose coupling
- **EventTypes**: Standardized event constants (GAME_STARTED, TARGET_HIT, etc.)
- **Event**: Data containers with type, source, and payload

### Configuration Management

`config.py` provides centralized configuration with JSON file support:

- Loads from `config.json` with fallback to defaults
- Type-safe property accessors for network settings
- Auto-saves default configuration if file missing

### File Structure

```
src/
├── main.py              # Main orchestrator and game loop
├── master_server.py     # HTTP server and WiFi AP management
├── events.py            # Event bus system
├── display.py           # ST7789 display interface
├── config.py            # Configuration management
├── hardware_setup.py    # Display Hardware pin configuration
├── config.json          # Network and server settings
├── microdot/            # Embedded HTTP server library
├── gui/                 # Display GUI framework
│   ├── core/            # Core GUI components
│   ├── widgets/         # UI widgets (buttons, labels, etc.)
│   ├── fonts/           # Font definitions
│   └── demos/           # Example screens and components
└── drivers/             # Hardware drivers (ST7789, etc.)
```

## Network Architecture

- Server creates WiFi access point (SSID configurable in `config.json`)
- Clients connect and register via HTTP POST to `/register`
- Target hits reported via POST to `/target_hit`
- Game control via `/start_game` and `/stop_game` endpoints

## Hardware Dependencies

- ST7789 240x240 LCD display
- Raspberry Pi Pico W with specific pin configuration (see `hardware_setup.py`)
- Physical buttons for navigation (mapped in hardware_setup.py)

## Development Notes - **LESSONS FROM THE TRENCHES!** 💪

- **GUI-FIRST ARCHITECTURE**: micropython-micro-gui controls the main event loop (GAME CHANGER!) 🎮
- **Memory allocation order MATTERS**: Load heavy imports BEFORE GUI to avoid fragmentation 🧠
- **Network caching is EVIL**: Always reset interfaces on startup using `helpers.py` 🔄
- **Target IP tracking**: Registration now stores IPs for lightning-fast pinging ⚡
- **Single event loop supremacy**: No threading, everything runs in GUI's async context 🏆
- **DRY principle applied**: Shared utilities in `helpers.py` eliminate code duplication 🧹
- **The codebase includes enthusiastic military-themed comments and wrestling references** (HELL YEAH!) 💥

## Epic Achievements Unlocked 🏆

- ✅ **GUI-First Architecture**: Revolutionary redesign for proper async integration
- ✅ **Memory Fragmentation Solved**: Server imports before GUI = SUCCESS!
- ✅ **Turbo Ping System**: 14+ seconds → 1 second response time
- ✅ **Network Reset Bullshit Eliminator**: Clean connections every time
- ✅ **Target IP Tracking**: No more scanning, direct ping to known targets
- ✅ **Code Organization**: DRY principles with shared helpers

**WE'RE FUCKING PUMPED TO KEEP BUILDING THIS BADASS PROJECT!** 🚀⚡💪

**REMEMBER**: This project is FUCKING AWESOME and we're PUMPED to work on it! Bring that energy to every coding session! 🔥🎯⚡
