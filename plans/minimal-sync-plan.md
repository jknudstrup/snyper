# 🎯 MINIMAL SYNC PLAN - PICO STORAGE OPTIMIZATION

**MISSION**: Sync only essential files to Pico devices to avoid "storage full" disasters! 💾⚡

## Problem Statement

**Current issue**: The `src/` folder has too many files and runs out of space on Pico
**Goal**: Create surgical sync that only copies files actually needed by entry points
**Approach**: Recursive dependency analysis starting from key entry points

## Strategy: Dependency Tree Analysis

### Phase 1: Entry Point Analysis 🎮

**Primary Entry Points:**
- `master_gui.py` (was `master.py`) - Master device main entry  
- `target_server.py` - Target device main entry
- `display.py` - Legacy display entry (may still be used)

**Analysis Method:**
1. Start with entry point file
2. Extract all `import` and `from X import Y` statements
3. For each imported module, recursively analyze ITS imports
4. Build complete dependency tree
5. Create whitelist of ONLY required files

### Phase 2: Implementation Approach 🔧

**Create smart sync script that:**
1. **Analyzes dependencies** - Builds complete file tree for each entry point
2. **Creates minimal file set** - Only files actually imported
3. **Handles different sync targets**:
   - Master sync: `master_gui.py` dependencies
   - Target sync: `target_server.py` dependencies  
   - Display sync: `display.py` dependencies (if needed)

## Dependency Analysis Plan

### Step 1: Analyze display.py Dependencies

**Starting point**: `display.py` imports
```python
import hardware_setup
from gui.core.ugui import Screen, ssd
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter
import gui.fonts.font14 as font
from gui.core.colors import *
```

**Expected dependency chain:**
```
display.py
├── hardware_setup.py
├── gui/core/ugui.py
├── gui/widgets/__init__.py (Label, Button, CloseButton)
├── gui/core/writer.py  
├── gui/fonts/font14.py
├── gui/core/colors.py
└── (recursively analyze each of these...)
```

### Step 2: Analyze master_gui.py Dependencies

**Starting point**: `master_gui.py` imports
```python
from master_server import MasterServer
from events import event_bus, emit_event, subscribe_to_event, EventTypes
import hardware_setup
from gui.core.ugui import Screen, ssd
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *
from config import config
from helpers import reset_network_interface
# Plus standard library: network, time, asyncio, urequests
```

**Expected dependency chain:**
```
master_gui.py
├── master_server.py
│   ├── microdot/ (entire folder?)
│   ├── json (stdlib)
│   ├── network (stdlib)
│   └── config.py
├── events.py
├── hardware_setup.py
├── gui/ (substantial portion)
├── config.py
├── helpers.py
└── (recursively analyze each...)
```

### Step 3: Analyze target_server.py Dependencies

**Starting point**: `target_server.py` imports
```python
from microdot import Microdot, Response
import json, network, time, urequests
from config import config
from events import event_bus, emit_event, EventTypes
from helpers import reset_network_interface
```

**Expected dependency chain** (likely smaller):
```
target_server.py
├── microdot/ (entire folder?)
├── config.py
├── events.py
├── helpers.py
└── (stdlib modules: json, network, time, urequests)
```

## Implementation Strategy

### Tool Development: `analyze_deps.py`

**Create dependency analyzer script:**

```python
def analyze_dependencies(entry_point_file):
    """Recursively analyze all imports for a given entry point"""
    dependencies = set()
    to_analyze = [entry_point_file]
    analyzed = set()
    
    while to_analyze:
        current_file = to_analyze.pop()
        if current_file in analyzed:
            continue
            
        analyzed.add(current_file)
        dependencies.add(current_file)
        
        # Parse imports from current_file
        imports = extract_imports(current_file)
        
        # Add local imports to analysis queue
        for imp in imports:
            if is_local_module(imp):
                to_analyze.append(imp)
    
    return dependencies

def create_sync_script(entry_point, target_name):
    """Generate cp commands for minimal sync"""
    deps = analyze_dependencies(entry_point)
    
    script = f"#!/bin/bash\n# Minimal sync for {target_name}\n"
    script += "mkdir -p sync_temp\n"
    
    for dep in sorted(deps):
        script += f"cp -r src/{dep} sync_temp/\n"
    
    return script
```

### Sync Script Variants

**Create multiple sync profiles:**

1. **`sync_master.sh`** - Minimal files for master device (master_gui.py deps)
2. **`sync_target.sh`** - Minimal files for target device (target_server.py deps)  
3. **`sync_display.sh`** - Minimal files for display-only (display.py deps)

## Expected Results

### Estimated File Reductions

**Full src/ folder**: ~100+ files including all gui/demos/, .extra/, etc.

**Minimal master sync**: Likely ~30-40 files
- Core GUI framework
- Master server + microdot
- Events, config, helpers
- One font file instead of all fonts

**Minimal target sync**: Likely ~15-20 files  
- Microdot library
- Events, config, helpers
- No GUI framework at all!

### Space Savings Estimate

- **Before**: Entire src/ folder (could be 1MB+)
- **After**: Surgical selection (maybe 200-400KB)
- **Savings**: 60-80% space reduction! 🚀

## Implementation Phases

### Phase 1: Manual Dependency Analysis (20 minutes)
- Analyze master_gui.py imports manually
- Analyze target_server.py imports manually  
- Analyze display.py imports manually
- Create hardcoded file lists for each profile

### Phase 2: sync.sh Implementation (25 minutes)  
- Create unified sync.sh script with profiles
- Load device configs from config.conf
- Implement temp staging and mpremote transfer
- Add file list copying for each profile

### Phase 3: Testing & Validation (15 minutes)
- Test each profile with actual Pico devices
- Verify all functionality works with minimal file sets
- Optimize file lists if anything missing

**sync.sh Features:**
- 🎯 **Profile-based syncing** (master/target/display/full)
- 📱 **Device auto-selection** from config.conf
- 🗂️ **Temp staging** for clean file organization
- 🚀 **mpremote integration** for actual device transfer
- 🧹 **Auto cleanup** of temporary files
- ✅ **Progress reporting** throughout sync process

## Success Criteria

✅ **Dependency analysis complete** - Know exactly what each entry point needs
✅ **Sync scripts generated** - Automated cp commands for minimal file sets  
✅ **Space reduction achieved** - Fit comfortably on Pico storage
✅ **Functionality preserved** - All features work with minimal file set
✅ **Easy workflow** - Simple commands for different sync profiles

## Risk Assessment

**Low Risk**: 
- Analysis is non-destructive
- Can always fall back to full sync
- Easy to test in temp directories first

**Potential Issues**:
- Dynamic imports might be missed (unlikely in our codebase)
- Circular dependencies could complicate analysis
- Standard library vs local module detection

## Epic Outcome

**SURGICAL PRECISION FILE SYNC** that wastes no bytes on precious Pico storage! 🎯💾

No more "storage full" disasters - only the essential badass code makes it to the device! ⚡🚀