# MicroPython Manifest Files Reference

## Purpose and Benefits

Manifest files enable "freezing" Python code directly into MicroPython firmware:

- **Pre-compile bytecode** - Improve memory usage and load performance
- **ROM execution** - Load code directly from ROM/flash memory
- **More available RAM** - Bytecode stored in flash instead of RAM
- **Filesystem-less deployment** - Useful for devices without filesystems

## Key Concepts

**Freezing Process:**
- Python source code → compiled bytecode → embedded in firmware
- Pre-compiled bytecode loads faster than runtime compilation
- Code executes directly from ROM, freeing up RAM

**Best Use Cases:**
- Rarely-changing dependencies and libraries
- Stable code that doesn't need frequent updates
- Systems with RAM constraints

## Manifest File Structure

Manifest files are Python scripts containing special function calls:

```python
# Basic manifest structure
include("$(BOARD_DIR)/manifest.py")  # Include board defaults
module("mymodule.py")                # Freeze single module
package("mypackage")                 # Freeze entire package
require("library-name")              # Include from micropython-lib
```

## Available Variables

Use these variables in manifest paths:

- `$(MPY_DIR)` - MicroPython repository path
- `$(MPY_LIB_DIR)` - micropython-lib repository path
- `$(PORT_DIR)` - Current port directory path
- `$(BOARD_DIR)` - Current board directory path

## High-Level Functions

### 1. `include(manifest_path)`
Include another manifest file:
```python
include("$(BOARD_DIR)/manifest.py")  # Include board's default manifest
include("shared_manifest.py")        # Include custom shared manifest
```

### 2. `module(module_path, base_path='.')`
Freeze a single Python file:
```python
module("mydriver.py")                # Freeze mydriver.py
module("drivers/sensor.py")          # Freeze from subdirectory
```

### 3. `package(package_path, files=None, base_path='.')`
Freeze entire package directory:
```python
package("mylib")                     # Freeze entire mylib package
package("drivers", files=["gpio.py", "spi.py"])  # Freeze specific files only
```

### 4. `require(name, library=None)`
Import package from micropython-lib:
```python
require("aiorepl")                   # Add async REPL
require("requests")                  # Add HTTP requests library
require("logging")                   # Add logging support
```

### 5. `add_library(library, library_path, prepend=False)`
Register external library paths:
```python
add_library("mylib", "/path/to/mylib")
```

### 6. `metadata(description, version, license, author)`
Define manifest metadata:
```python
metadata(
    description="My custom firmware",
    version="1.0.0",
    license="MIT",
    author="Developer Name"
)
```

## Practical Examples

### Basic Custom Manifest
```python
# Include board defaults (essential)
include("$(BOARD_DIR)/manifest.py")

# Add custom driver
module("hardware_driver.py")

# Add networking utilities
require("urequests")
require("umqtt.simple")

# Add custom GUI library
package("gui")
```

### Advanced Project Manifest
```python
# Include defaults
include("$(BOARD_DIR)/manifest.py")

# Add networking bundle
require("bundle-networking")

# Freeze custom packages
package("drivers")
package("utilities") 
package("gui", files=["core.py", "widgets.py"])  # Selective files

# Add metadata
metadata(
    description="SNYPER Game Firmware", 
    version="2.0.0",
    license="MIT",
    author="SNYPER Team"
)
```

## Build Process

### 1. Create Manifest File
Save manifest as `manifest.py` outside MicroPython repo:
```bash
/path/to/project/custom_manifest.py
```

### 2. Build Firmware with Manifest
```bash
cd micropython/ports/rp2
make BOARD=RPI_PICO_W FROZEN_MANIFEST=/path/to/project/custom_manifest.py
```

### 3. Deploy Firmware
```bash
# Copy resulting firmware.uf2 to device in BOOTSEL mode
cp build-RPI_PICO_W/firmware.uf2 /path/to/project/
```

## Workflow Recommendations

### Development Phase
- **Don't freeze during active development** - Use normal file deployment
- Test code stability before freezing
- Keep manifest simple initially

### Production Phase  
- **Freeze stable dependencies** - Libraries that rarely change
- Keep hardware setup files unfrozen for flexibility
- Test thoroughly after freezing

### File Organization
```
project/
├── manifest.py              # Custom manifest
├── src/
│   ├── main.py             # Keep unfrozen for development
│   ├── hardware_setup.py   # Keep unfrozen per recommendations  
│   ├── stable_lib/         # Good candidate for freezing
│   └── gui/                # Good candidate for freezing
└── firmware.uf2            # Resulting custom firmware
```

## Common Patterns

### GUI Library Freezing
```python
include("$(BOARD_DIR)/manifest.py")
require("bundle-networking")
package("gui")  # Freeze entire GUI library
# Keep hardware_setup.py unfrozen
```

### Selective Freezing
```python
include("$(BOARD_DIR)/manifest.py")
package("core")              # Freeze stable core
module("utilities.py")       # Freeze stable utilities  
# Leave main.py, config.py unfrozen for easy changes
```

### Library-Heavy Projects  
```python
include("$(BOARD_DIR)/manifest.py")
require("aiorepl")
require("logging") 
require("urequests")
package("mylib")
metadata(description="Feature-rich firmware", version="1.0.0")
```

## Troubleshooting Tips

- **Build failures**: Check file paths and syntax in manifest
- **Import errors**: Verify frozen modules can be imported normally
- **Memory issues**: Some components (like display drivers) may have freezing problems
- **Path issues**: Use absolute paths or proper base_path parameters
- **Missing dependencies**: Include all required files and libraries in manifest