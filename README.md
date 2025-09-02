# SNYPER - Carnival Target Shooting Game

**SNYPER** is a carnival-style target shooting game built for Raspberry Pi Pico W microcontrollers with a revolutionary GUI-first architecture.

## Architecture Overview

The system consists of networked Raspberry Pi Pico W devices:

- **Master Device**: Runs the game controller with ST7789 display, WiFi AP, HTTP server, and game logic
- **Target Devices**: WiFi clients that control individual targets with fast ping responses and target control endpoints

### Key Features

- **GUI-First Architecture**: Built with micropython-micro-gui controlling the main event loop
- **Multi-Screen Interface**: Navigation hub with New Game, Options, and Debug screens
- **Network Management**: WiFi access point with HTTP-based target communication
- **Target Control**: Lightning-fast ping responses and raise/lower target commands
- **Device Identity System**: Single codebase deployed with different device roles

## Quick Start

### 1. Initialize Configuration

Create `config.conf` with your device serial ports. Here's an example, you can modify it by replacing the ports to match your setup:

```bash
SERIAL_MASTER="/dev/tty.usbmodem11301"
SERIAL_TARGET="/dev/tty.usbmodem11401"
```

**Finding Device Ports:**

- Connect your Pico W devices via USB
- Run `ls /dev/tty.usbmodem*` to find available ports
- Update `config.conf` with the correct port paths

### 2. Development Mode (Live Coding)

Run code directly from your development machine:

```bash
# Run master device (default)
./dev.sh
or
./dev.sh master

# Run target devices
./dev.sh target_1
./dev.sh target_2

# Test disable mode. This ensures that the device, when rebooting,
# doesn't execute its startup code. Useful for dev testing
./dev.sh disable
```

### 3. Production Deployment

The sync script is invoked as follows:
`sh .sync.sh <device_name>`

Deploy code to device storage for standalone operation:

```bash
# Deploy to master device (default)
./sync.sh
./sync.sh master

# Deploy to target devices (the argument will set the target name)
./sync.sh target_1
./sync.sh target_2

# Disable device (prevent auto-start. Note: not super functional at the moment)
./sync.sh disable
```

## Device Identity System

Both scripts use the same device identity switching mechanism:

1. **Device Identity Generation**: Creates `src/device_id.json` with specified node_id
2. **Automatic Configuration**: Device reads identity and configures role accordingly
3. **Single Codebase**: Same code deployed with different device roles

**Development vs Production:**

- **dev.sh**: Mounts code from host filesystem, runs via `mpremote mount`
- **sync.sh**: Copies code to device storage, runs standalone after deployment

## Project Structure

```
src/
├── master.py              # Main entry point for master device
├── target.py              # Main entry point for target device
├── master_controller.py   # Controller core with SystemState/GameState
├── master_server.py       # HTTP server using controller
├── target_server.py       # Target endpoints with ping/control
├── helpers.py             # Shared utilities and network reset
├── views/                 # Screen modules (MainScreen, DebugScreen, etc.)
├── device_id.json         # Generated device identity (created by scripts)
└── config.json            # Base device configuration
```

## Development Commands

```bash
./dev.sh                   # Run master (development mode)
./dev.sh target_1          # Run target (development mode)
./sync.sh master           # Deploy to master device
./sync.sh target_1         # Deploy to target device
./killmp.sh                # Kill stuck mpremote processes
```

## Hardware Requirements

- **Raspberry Pi Pico W**: WiFi-enabled microcontroller
- **ST7789 240x240 LCD**: 4-bit color mode for optimal RAM usage
- **Physical Buttons**: GPIO-connected controls
- **Target Mechanisms**: Servo or motor-controlled pop-up targets

## Network Architecture

- **Master Device**: Creates WiFi access point and HTTP server
- **Target Devices**: Connect to master's WiFi network
- **Communication**: HTTP requests using microdot library
- **Target Registration**: Automatic discovery and IP tracking
- **Ping System**: Sub-second response times for real-time control

## Development Philosophy

- **GUI-first architecture**: micropython-micro-gui controls the event loop
- **Memory allocation order matters**: Load heavy imports before GUI
- **Network caching elimination**: Always reset interfaces using helpers.py
- **Controller pattern**: Single MasterController manages all system state
- **Incremental progress**: Small changes that work, committed frequently

## Troubleshooting

**Import Path Issues:**

- Development mode uses mounted filesystem
- Device mode uses copied files with different sys.path behavior
- Always test actual device deployment, not just mounted dev mode

**Network Connection Problems:**

- Use `helpers.reset_network_interface()` on startup
- Check `config.conf` has correct serial ports
- Verify devices are properly connected via USB

**Memory Fragmentation:**

- Import server components before GUI initialization
- Use `gc.collect()` when needed
- Follow established import order patterns

## Contributing

1. Study existing patterns in the codebase
2. Start with simple implementations that work
3. Test incrementally on actual hardware
4. Commit functional states with descriptive messages
5. Update documentation when adding features

---

**Build something EPIC!** 🎯⚡🚀
