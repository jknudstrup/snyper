# Debug Screen Enhancement Plan

## Mission Orders

### Phase 1: Screen Simplification and Dropdown Implementation
**Status**: Ready to Execute

#### Task 1: Rename Screen Title
- Change title from "Debug & Diagnostics" to "Debug"

#### Task 2: Remove Unnecessary Buttons
- Keep: "PING Targets" button
- Keep: Back button (CloseButton)
- Remove: "Network Info" button
- Remove: "System Stats" button

#### Task 3: Add Dropdown Component
- Implement dropdown list containing all target names
- Reference: `.extra/micropython-micro-gui/gui/widgets/dropdown.py`
- Consult: micropython-micro-gui README for dropdown usage
- Populate dropdown with target names from game_state.target_ips

**Torpedo Status**: Armed and ready to fire! ⚡🎯

## Technical Notes

### Dropdown Widget Implementation
- **Import**: `from gui.widgets import Dropdown`
- **Constructor**: `Dropdown(writer, row, col, elements=list, dlines=3, bdcolor=GREEN, callback=function)`
- **Elements format**: Simple list of strings `['target1', 'target2', 'target3']`
- **Callback signature**: `def callback(dropdown_instance)`
- **Get selection**: `dropdown.textvalue()` returns currently selected string
- **Reference**: `.extra/micropython-micro-gui/gui/demos/dropdown.py` for implementation pattern

### Key Requirements
- Do NOT edit library code - only modify our screen implementation
- Follow existing micropython-micro-gui patterns from demos
- Populate dropdown with target names from `game_state.target_ips.keys()`
