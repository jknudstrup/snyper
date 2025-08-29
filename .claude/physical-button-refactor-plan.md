# Physical Button Refactor Plan

## Objective
Replace the complex PhysicalButtonOverlay singleton system with individual button classes to eliminate memory leaks and simplify the API.

## Current Problems
- **Memory Leak**: PhysicalButtonOverlay singleton pattern prevents proper garbage collection (~1.4KB leak per navigation cycle)
- **Complex API**: Requires configuration dictionaries and overlay management
- **Singleton Issues**: Class-level references prevent Screen.REPLACE from properly cleaning up objects
- **OOM Crashes**: Creating multiple Pushbutton objects for same GPIO pins causes resource conflicts

## CONFIRMED ROOT CAUSE (2025-08-29)
**MEMORY LEAK IS DEFINITELY FROM BUTTON IMPLEMENTATION, NOT SCREEN NAVIGATION**

Testing confirmed:
- ✅ **Navigation with normal buttons**: RAM stabilizes, no leak
- ❌ **Navigation with display.py buttons**: Memory leak persists
- **Conclusion**: The issue is specifically in our ButtonA/B/X/Y implementation in display.py

**NOT the navigation callbacks** - screen_helpers.py navigate_to_screen() is clean

## Proposed Solution
Create individual ButtonA, ButtonB, ButtonX, ButtonY classes inheriting from PassiveButton, each managing their own hardware and positioning.

## Implementation Plan

### Phase 1: Create Individual Button Classes

Create four new button classes in display.py:

```python
class ButtonA(PassiveButton):
    """Physical A button (typically Back/Cancel) - Red circle at standard position"""
    def __init__(self, wri, callback=None, **kwargs):
        # Standard A button positioning and appearance
        super().__init__(wri, row=15, col=208, shape=CIRCLE, height=25, width=25,
                        text='D', fgcolor=WHITE, bgcolor=RED, callback=callback or self._default_callback, **kwargs)
        
        # Create hardware binding for GPIO pin 15
        self.keyA = Pushbutton(Pin(15, Pin.IN, Pin.PULL_UP))
        self.keyA.release_func(self._on_physical_press)
    
    def _on_physical_press(self):
        """Handle physical button press - trigger visual feedback and callback"""
        self.trigger()  # PassiveButton method for visual feedback + callback
    
    def _default_callback(self, button):
        """Default behavior if no callback provided"""
        pass

class ButtonB(PassiveButton):
    """Physical B button (typically Skip/Next) - Blue circle"""
    # Similar implementation for GPIO pin 17, row=75

class ButtonX(PassiveButton):
    """Physical X button (typically New/Action) - Dark blue circle"""  
    # Similar implementation for GPIO pin 19, row=135

class ButtonY(PassiveButton):
    """Physical Y button (typically Select indicator) - Green circle"""
    # No hardware binding - handled by GUI system as 'sel' button
    # Just visual indicator at row=195
```

### Phase 2: Update Screen Classes

Replace PhysicalButtonOverlay usage with individual button instantiation:

**MainScreen:**
```python
# Before:
button_config = {'Y': {'icon': 'F', 'color': DARKGREEN, 'callback': lambda b: None}}
self.button_overlay = PhysicalButtonOverlay(wri, button_config)

# After:
self.button_y = ButtonY(wri)  # Just visual indicator
```

**NewGameScreen:**
```python
# Before:
button_config = {
    'A': {'icon': 'D', 'color': RED, 'callback': self._back_to_main},
    'Y': {'icon': 'F', 'color': DARKGREEN, 'callback': lambda b: None}
}
self.button_overlay = PhysicalButtonOverlay(wri, button_config)

# After:
self.button_a = ButtonA(wri, callback=self._back_to_main)
self.button_y = ButtonY(wri)
```

**DebugScreen:**
```python
# After:
self.button_a = ButtonA(wri, callback=self._navigate_to_main)
self.button_b = ButtonB(wri, callback=lambda b: print("⏭️ Debug: Skip"))
self.button_x = ButtonX(wri, callback=lambda b: print("🆕 Debug: New"))
self.button_y = ButtonY(wri, callback=lambda b: print("▶️ Debug: Play"))
```

### Phase 3: Test and Cleanup

1. **Remove PhysicalButtonOverlay class entirely**
2. **Test memory stability during navigation** - should eliminate 1.4KB leak per cycle
3. **Verify physical button functionality** - hardware buttons should still trigger callbacks
4. **Test OOM resistance** - no more crashes from GPIO pin conflicts

## Benefits

### Memory Management
- **Natural garbage collection**: Buttons are regular screen widgets
- **No singleton references**: Screen.REPLACE can properly clean up all objects
- **No circular references**: Each button manages its own lifecycle

### API Simplification
- **Intuitive instantiation**: `ButtonA(wri, callback=self.method)` vs complex config dicts
- **Selective usage**: Create only the buttons each screen needs
- **Type safety**: Each button class has specific purpose and appearance

### Modularity
- **Independent buttons**: Each button class is self-contained
- **Standard positioning**: Consistent placement across screens
- **Flexible callbacks**: Easy to specify different behaviors per screen

## Migration Strategy

1. **Implement new button classes** alongside existing PhysicalButtonOverlay
2. **Update one screen at a time** to use new buttons
3. **Test each screen individually** to ensure functionality
4. **Remove PhysicalButtonOverlay** once all screens are migrated
5. **Verify memory leak is eliminated** through navigation testing

## Expected Outcome

- **Zero memory leaks** during screen navigation
- **No OOM crashes** from resource conflicts  
- **Cleaner, more maintainable code** with simpler API
- **Same physical button functionality** with better performance