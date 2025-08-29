# GUI Library Freezing Plan

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

**Selective freezing strategy**:

- ✅ **Freeze**: GUI framework (`gui/core/`, `gui/widgets/`, `gui/fonts/`)
- ❌ **Keep unfrozen**: `hardware_setup.py` (frequent changes expected)
- ❌ **Keep unfrozen**: Display drivers (potential freeze compatibility issues per docs)

### Phase 3: Build and Deploy Custom Firmware

**Goal**: Create and deploy SNYPER-specific firmware with frozen GUI library

**Build process**:

```bash
cd micropython/ports/rp2
MANIFEST='/path/to/snyper/.claude/rp2_snyper_manifest.py'
make clean
make -j 8 BOARD=PICO_W FROZEN_MANIFEST=$MANIFEST
```

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
