# GUI Library Freezing Plan

**📚 REFERENCE DOCS**: When working on freezing issues, consult these docs in `.claude/freeze/`:
- `appendix2_freezing_bytecode.md` - GUI library author's freezing recommendations
- `micropython_manifest_reference.md` - Complete manifest file syntax and examples  
- `rp2_port_readme.md` - Official RP2 build instructions and deployment

## Objective

Freeze micropython-micro-gui library into firmware to achieve major RAM savings (~32KB reduction from 55KB to 23KB according to library docs).

## Benefits

- **Major RAM reduction**: 55KB → 23KB (32KB savings)
- **Faster imports**: Pre-compiled bytecode loads instantly
- **Smaller deployment**: GUI library embedded in firmware
- **Better performance**: No runtime compilation overhead

## Implementation Process

### Phase 1: MicroPython Build Environment Setup

**Goal**: Establish custom firmware build capability for Raspberry Pi Pico W

**Steps**:

1. ✅ **Clone MicroPython repository** locally  
2. ✅ **Build mpy-cross** - MicroPython bytecode compiler:
   ```bash
   cd micropython
   make -C mpy-cross
   ```
3. **Install ARM embedded toolchain** (required for C compilation):
   - Missing standard C library headers (stdlib.h, stdint.h)
   - Current blocker: Need complete embedded toolchain with newlib
4. **Alternative approach**: Use .mpy files instead of firmware freezing

### Alternative: .mpy Bytecode Compilation (Recommended)

**Goal**: Achieve RAM savings without custom firmware complexity

**Process**:
1. **Compile GUI library** to .mpy bytecode files using mpy-cross
2. **Deploy .mpy files** alongside regular Python code  
3. **Faster imports + RAM savings** without firmware rebuild complexity

### Phase 2: Create Freezing Manifest

**Goal**: Create manifest file to freeze GUI library while preserving flexibility

**Manifest file structure** (`rp2_snyper_manifest.py`):

```python
# Include default RP2 board manifest (essential firmware components)
include("$(MPY_DIR)/ports/rp2/boards/manifest.py")

# Freeze GUI library from our trimmed src/gui directory  
freeze('/path/to/snyper/src/gui')
```

**Directory requirements**:

- Use `src/gui/` directory (contains only code we actually need)
- Maintains proper directory structure (gui/core/, gui/widgets/, gui/fonts/)
- No extra demos, examples, or unused widgets from upstream repository

**Selective freezing strategy** (from Appendix 2):

- ✅ **Freeze**: GUI framework (`gui/core/`, `gui/widgets/`, `gui/fonts/`)
- ❌ **Keep unfrozen**: `hardware_setup.py` ("for ease of making changes" - per author)
- ❌ **Keep unfrozen**: Display drivers ("problems freezing display drivers" - per author)
- ✅ **Use symlink**: Author uses symlink to gui directory (validates our src/gui approach)

### Phase 3: Build and Deploy Custom Firmware

**Goal**: Create and deploy SNYPER-specific firmware with frozen GUI library

## Complete Custom Firmware Build Instructions

### Prerequisites (One-time Setup)

1. **ARM Cross-Compilation Toolchain**:
   ```bash
   brew install --cask gcc-arm-embedded
   ```
   (Requires sudo - installs complete ARM embedded toolchain with newlib)

2. **MicroPython Repository** (already cloned):
   ```bash
   # Location: .extra/micropython
   ```

3. **Build mpy-cross** (already built):
   ```bash
   cd .extra/micropython
   make -C mpy-cross
   ```

### Custom Firmware Build Process

**Location**: `/Users/jimknudstrup/Documents/Projects/snyper/.extra/micropython/ports/rp2`

**Step 1: Prepare Build Environment**
```bash
cd /Users/jimknudstrup/Documents/Projects/snyper/.extra/micropython/ports/rp2
```

**Step 2: Clean Previous Build**
```bash
make clean BOARD=RPI_PICO_W
```

**Step 3: Build Custom Firmware with Frozen GUI**
```bash
make -j 8 BOARD=RPI_PICO_W FROZEN_MANIFEST=/Users/jimknudstrup/Documents/Projects/snyper/.claude/rp2_snyper_manifest.py
```

**Step 4: Copy Firmware to Project Root**
```bash
cp build-RPI_PICO_W/firmware.uf2 /Users/jimknudstrup/Documents/Projects/snyper/snyper_firmware.uf2
```

### Manifest File Details

**Location**: `/Users/jimknudstrup/Documents/Projects/snyper/.claude/rp2_snyper_manifest.py`

**Contents**:
```python
# Include default RP2 board manifest (essential firmware components)  
include("$(MPY_DIR)/ports/rp2/boards/manifest.py")

# Add networking bundle (includes urequests, json, ssl, requests, etc.)
require("bundle-networking")

# Freeze GUI library from our trimmed src/gui directory
freeze("/Users/jimknudstrup/Documents/Projects/snyper/src/gui")
```

**Key Features**:
- **Standard RP2 components**: Essential Pico W functionality preserved
- **Networking bundle**: All HTTP/network modules (urequests, ssl, json, etc.) 
- **Frozen GUI library**: src/gui directory embedded for 32KB RAM savings

### Build Results

**Firmware Size**: 1.9MB (vs 1.7MB standard)
- **Size increase**: ~200KB for embedded GUI + networking modules
- **RAM savings**: ~32KB during runtime (GUI library pre-compiled)

**Build Time**: ~3-4 minutes on Apple Silicon Mac

**Deployment**:

1. **Copy firmware.uf2** to device in BOOTSEL mode
2. **Delete src/gui/ folder** from project (now frozen in firmware)
3. **Update sync.sh** to exclude gui/ folder from deployment
4. **Test SNYPER startup** - should boot normally with frozen GUI
5. **Verify functionality** - all screens, buttons, navigation should work
6. **Measure RAM improvement** - document before/after memory usage

### Phase 4: Validation and Documentation

**Testing checklist**:

- [ ] Device boots with custom firmware
- [ ] All screens render correctly (MainScreen, NewGameScreen, OptionsScreen, DebugScreen)
- [ ] Physical buttons work (A/B/X hardware, Y select)
- [ ] Screen navigation functions properly
- [ ] HTTP server and game loop start correctly
- [ ] Target registration and ping functionality works
- [ ] RAM usage shows expected 32KB improvement

**Documentation updates**:

- Update CLAUDE.md with firmware build instructions
- Document manifest file location and contents
- Add deployment process to development workflow

## Technical Considerations

### Build Environment

- **Platform**: Requires Linux/macOS with ARM cross-compilation tools
- **Dependencies**: CMake, ARM GCC toolchain, Python 3
- **Build time**: Several minutes for full firmware compilation

### Deployment Process

- **Current**: Copy Python files via mpremote/sync.sh
- **With freezing**: Flash entire firmware.uf2 (replaces MicroPython itself)
- **Development impact**: Code changes require firmware rebuild vs simple file sync

### Risk Assessment

- **Low risk**: GUI library is stable, well-tested
- **Medium risk**: Build environment setup complexity
- **Mitigation**: Keep hardware_setup.py unfrozen for easy hardware changes

## Success Criteria

1. **Functional equivalence**: All current SNYPER features work identically
2. **Performance improvement**: Measurable RAM savings (target: 30+ KB)
3. **Development workflow**: Reasonable build/deploy cycle for ongoing development
4. **Stability**: No regression in memory leak fixes or navigation functionality
