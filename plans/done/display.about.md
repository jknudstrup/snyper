# Display System Analysis - micropython-micro-gui

## Key Findings from Repository Documentation

### Asyncio Integration

1. **Internal Asyncio Usage**: The micro-gui library uses asyncio internally but presents a conventional callback-based interface. Knowledge of asyncio is not required for basic usage.

2. **Non-Blocking Behavior**: Contrary to initial assumptions, `Screen.change()` does NOT block the asyncio event loop. The library is designed to work with async applications.

3. **Async Task Creation**: Within Screen classes, you can create async tasks using `asyncio.create_task()` in the `__init__` method. This allows running background tasks alongside the GUI.

### Patterns from Demo Analysis

From examining `/gui/demos/tbox.py` and other examples:

```python
class TBCScreen(Screen):
    def __init__(self):
        super().__init__()
        self.tb = Textbox(wri, *pargs, clip=True, **tbargs)
        CloseButton(wri)
        # This is the key pattern - create async tasks within the screen
        asyncio.create_task(self.main())

    async def main(self):
        # Background async work happens here
        await some_async_function()
```

### Screen Management

1. **Screen.change()**: Takes a class (not instance) and activates it. Can be called from within callback functions to switch screens.

2. **Navigation Modes**: 
   - Tree-like structure where screens retain state
   - Replacement mode for arbitrary navigation

3. **Callback-Based Interface**: Uses conventional callbacks rather than requiring direct asyncio knowledge.

### Hardware Setup Requirements

1. **Early Initialization**: Display hardware must be set up early due to RAM usage considerations.

2. **Frame Buffer**: The library handles frame buffer management internally.

3. **Button Mapping**: Requires specific button pin assignments for navigation (next, select, previous, increase, decrease).

### Implications for Our Application

**The blocking issue is NOT caused by Screen.change()** - the micro-gui library is designed to work with asyncio applications. The problem in our master.py is likely:

1. **Hardware initialization failure** - Display hardware not responding
2. **Memory issues** - Insufficient RAM for frame buffer allocation
3. **Pin configuration problems** - Incorrect hardware setup
4. **Silent exceptions** - Errors in display initialization not being caught

**Recommended Approach**: `Screen.change()` should work fine in our async master application. We need to investigate hardware/configuration issues rather than architectural problems.

## Next Steps

1. Add error handling around `Screen.change()` to catch any hardware failures
2. Verify hardware setup and pin configurations match actual hardware
3. Check RAM usage and memory allocation
4. Consider adding debug output to identify where exactly the blocking occurs