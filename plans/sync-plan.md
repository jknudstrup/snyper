# 🚀 ULTIMATE SYNC PLAN - Device Identity + Minimal Files

**MISSION**: Create the BADASS sync script that handles device identity switching AND minimal file syncing! 🎯⚡

## The Big Picture

**TWO-PART SYNC MAGIC:**
1. **Device Identity Management** - Configure what the device thinks it is
2. **Minimal File Syncing** - Only copy essential files to save space

**Current Reality Check:**
- ✅ `master.py` is the real master entry point (not master_gui.py)
- ✅ `main.py` is the universal entry that reads `node_id` from config.json
- ✅ Currently requires manual config.json editing (brute force but works)
- ✅ Need automated device identity switching during sync

## Device Identity System Analysis

### Current main.py Logic

**How device selection works NOW:**
```python
# main.py reads config.json
config = load_config()
node_id = config.get('node_id')

if node_id == 'master':
    # Run master code
elif node_id.startswith('target_'):
    # Run target code
```

**Current workflow (manual):**
1. Edit config.json to set `"node_id": "master"` or `"node_id": "target_1"`
2. Run dev.sh to deploy
3. Device runs main.py which reads config and branches accordingly

### Proposed Auto-Switching

**New sync.sh workflow:**
```bash
./sync.sh                # Deploy as master (DEFAULT - no args = master)
./sync.sh master         # Deploy as master (explicit)
./sync.sh target_1       # Deploy as target_1 
./sync.sh target_2       # Deploy as target_2
```

**What sync.sh will do:**
1. **Generate appropriate config.json** with correct node_id
2. **Select minimal file set** based on device type (master vs target)
3. **Stage files in temp directory** 
4. **Deploy to specified device** via mpremote

## Complete Sync Strategy

### Phase 1: Device Identity Generation

**BRILLIANT APPROACH: device_id.json overlay system!**

**Why this is GENIUS:**
- ✅ **Clean JSON format** - Consistent with config.json
- ✅ **Zero source control noise** - device_id.json is gitignored
- ✅ **Simple shell generation** - Easy to create from bash
- ✅ **Config merging** - Device identity overlays base config

```bash
generate_device_id() {
    local device_type="$1"
    
    echo "⚙️ Setting device identity to: $device_type"
    cat > device_id.json << EOF
{
    "node_id": "$device_type"
}
EOF
}

# Usage:
generate_device_id "master"    # Creates device_id.json with master
generate_device_id "target_1"  # Creates device_id.json with target_1
```

**Enhanced config.py loading:**
```python
def load_config(self):
    """Load config from file with device_id overlay"""
    try:
        # Load main config (source controlled)
        with open(self.config_file) as f:
            self.config = json.load(f)
            print("✅ Loaded config.json")
            
        # Try to load device_id.json overlay (gitignored)
        try:
            with open("device_id.json") as f:
                device_config = json.load(f)
                self.config.update(device_config)  # Merge device identity
                print(f"✅ Loaded device identity: {device_config.get('node_id')}")
        except OSError:
            print("ℹ️  No device_id.json found, using config.json node_id")
            
        print(self.config)
    except OSError:
        self._set_defaults()
```

**Add to .gitignore:**
```
device_id.json
```

### Phase 2: Minimal File Selection

**File sets by device type:**

**MASTER file set** (main.py → master.py path):
```
Essential files:
├── main.py (universal entry point)
├── master.py (GUI-first master logic)  
├── master_server.py (HTTP server)
├── events.py (event bus)
├── helpers.py (network reset)
├── config.py (config loading)
├── hardware_setup.py (display pins)
├── config.json (generated for master)
├── gui/ (essential GUI framework)
│   ├── core/ (ugui, writer, colors)
│   ├── widgets/ (Label, Button, CloseButton)
│   └── fonts/arial10.py (only font we use)
├── drivers/st7789.py (display driver)
└── microdot/ (HTTP server library)
```

**TARGET file set** (main.py → target_server.py path):
```
Essential files:
├── main.py (universal entry point)
├── target_server.py (target HTTP endpoints)
├── events.py (event bus)
├── helpers.py (network reset)
├── config.py (config loading) 
├── config.json (generated for target_X)
└── microdot/ (HTTP server library)
```

### Phase 3: Unified sync.sh Implementation

**Complete sync.sh architecture:**

```bash
#!/bin/bash
# sync.sh - Ultimate device deployment script

# Load device configs
source config.conf

# Parse command line - DEFAULT TO MASTER IF NO ARGS
DEVICE_TYPE="${1:-master}"  # 🎯 DEFAULT = master when no arguments
echo "🎯 Deploying device type: $DEVICE_TYPE"

case "$DEVICE_TYPE" in
    master|"")
        SERIAL_DEVICE="$SERIAL_MASTER"
        FILE_PROFILE="master"
        echo "🎮 Master mode selected"
        ;;
    target_*)
        SERIAL_DEVICE="$SERIAL_TARGET" 
        FILE_PROFILE="target"
        echo "🎯 Target mode selected: $DEVICE_TYPE"
        ;;
    *)
        echo "Usage: $0 [master|target_1|target_2|...]"
        echo "Default: master (when no arguments provided)"
        exit 1
        ;;
esac

echo "🎯 Deploying $DEVICE_TYPE to $SERIAL_DEVICE"

# Create temp staging area
TEMP_DIR=".sync_temp_$(date +%s)"
mkdir -p "$TEMP_DIR"

# Step 1: Generate device identity file
echo "⚙️ Setting device identity to $DEVICE_TYPE..."
generate_device_id "$DEVICE_TYPE"
cp device_id.json "$TEMP_DIR/"

# Step 2: Copy minimal file set based on profile
echo "📦 Copying $FILE_PROFILE file set..."
copy_minimal_files "$FILE_PROFILE" "$TEMP_DIR"

# Step 3: Deploy to device
echo "🚀 Deploying to device..."
cd "$TEMP_DIR"
mpremote connect "$SERIAL_DEVICE" mount . exec "import os; [os.remove(f) for f in os.listdir('.') if f.endswith('.py')]"
mpremote connect "$SERIAL_DEVICE" mount . cp -r . :

# Step 4: Cleanup  
cd ..
rm -rf "$TEMP_DIR"
echo "✅ $DEVICE_TYPE deployed successfully!"
```

## File Copying Functions

**Master file set:**
```bash
copy_master_files() {
    local dest="$1"
    
    # Core entry points
    cp src/main.py "$dest/"
    cp src/master.py "$dest/"
    cp src/master_server.py "$dest/"
    
    # Support modules
    cp src/events.py "$dest/"
    cp src/helpers.py "$dest/"
    cp src/config.py "$dest/"
    cp src/hardware_setup.py "$dest/"
    
    # GUI framework (selective)
    mkdir -p "$dest/gui/core" "$dest/gui/widgets" "$dest/gui/fonts"
    cp src/gui/core/ugui.py "$dest/gui/core/"
    cp src/gui/core/writer.py "$dest/gui/core/"
    cp src/gui/core/colors.py "$dest/gui/core/"
    cp src/gui/widgets/__init__.py "$dest/gui/widgets/"
    cp src/gui/fonts/arial10.py "$dest/gui/fonts/"
    
    # Display driver
    mkdir -p "$dest/drivers"
    cp src/drivers/st7789.py "$dest/drivers/"
    
    # HTTP server
    cp -r src/microdot "$dest/"
}
```

**Target file set:**
```bash
copy_target_files() {
    local dest="$1"
    
    # Core entry points  
    cp src/main.py "$dest/"
    cp src/target_server.py "$dest/"
    
    # Support modules
    cp src/events.py "$dest/"
    cp src/helpers.py "$dest/"
    cp src/config.py "$dest/"
    
    # HTTP server
    cp -r src/microdot "$dest/"
}
```

## Implementation Phases

### Phase 1: Enhanced Config System Implementation (20 minutes)
- Enhance config.py with device_id.json overlay loading
- Create device_id.json generation functions
- Test device identity overlay system
- Add device_id.json to .gitignore

### Phase 2: File Set Definition (25 minutes)
- Manually analyze master.py dependencies
- Manually analyze target_server.py dependencies
- Create copy functions for each file set
- Test minimal file sets in temp directories

### Phase 3: sync.sh Implementation (30 minutes)
- Create unified sync.sh with device identity + file selection
- Integrate config.conf device selection
- Add mpremote deployment logic
- Test with actual devices

### Phase 4: Validation & Optimization (15 minutes)
- Test master deployment: `./sync.sh master`
- Test target deployment: `./sync.sh target_1`
- Verify functionality with minimal file sets
- Optimize file lists if anything missing

## Success Criteria

✅ **Device identity switching** - `./sync.sh target_1` auto-generates target config
✅ **Minimal file syncing** - Only essential files copied (60-80% space savings)
✅ **Zero manual editing** - No more manual config.json modifications
✅ **Clean workflow** - Simple commands for any device deployment
✅ **Robust deployment** - Handles device selection and file staging automatically

## Expected Results

**Space Savings:**
- **Master**: ~40 files instead of 100+ (GUI + server essentials)
- **Target**: ~15 files instead of 100+ (server only, no GUI!)
- **Storage**: 60-80% reduction (1MB+ → 200-400KB)

**Workflow Improvement:**
- **Before**: Edit config.json → run dev.sh → hope it works
- **After**: `./sync.sh target_1` → DONE! 🚀

**Device Management:**
- **Master deploy**: `./sync.sh` or `./sync.sh master`
- **Target deploy**: `./sync.sh target_1`, `./sync.sh target_2`, etc.
- **Auto-identity**: device_id.json automatically generated during sync
- **Clean source control**: config.json stays pristine, device_id.json is gitignored

## Epic Outcome

**ULTIMATE DEPLOYMENT WEAPON** that combines:
- 🎯 **Surgical file selection** (only essential code)
- ⚙️ **Auto device identity** (no manual config editing)
- 📱 **Smart device targeting** (reads config.conf like dev.sh)
- 🚀 **One-command deployment** (from idea to running device)

**THE PICO STORAGE CRISIS + DEPLOYMENT HASSLE = BOTH ELIMINATED!** 💪⚡🎯