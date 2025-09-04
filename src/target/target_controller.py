import asyncio
from config.config import config
import time

class TargetController:
    """Target Controller class. Tracks target state and handles interactions with the target hardware components. Interacts with target_server via event bus."""
    
    def __init__(self, target_server, peripheral_controller):
        self.id = config.get('node_id', 'target_unknown')
        self.hit_value = config.get('hit_value', 10)
        self.target_server = target_server
        self.peripheral_controller = peripheral_controller
        self.is_active = False
        self.is_standing = False
        self.hit_detected = False
        self._setup_event_handlers()
        
    def _setup_event_handlers(self):
        """Subscribe to events from the target server"""
        subscribe_to_event(EventTypes.TARGET_CONTROL, self._handle_target_control, 'target_controller')
        
    async def _handle_target_control(self, event):
        """Handle target control events from the server"""
        action = event.data.get('action')
        
        if action == 'stand_up':
            await self.stand_up()
        elif action == 'lay_down':
            await self.lay_down()
        elif action == 'activate':
            duration = event.data.get('duration', 5)
            await self.activate_target(duration)
        else:
            print(f"⚠️  Unknown target control action: {action}")
    
    async def stand_up(self):
        """Stand up target - hardware servo control would go here"""
        print(f"🎯 Target {self.id} standing up - servo moving to UP position!")
        self.is_standing = True
        await emit_event(EventTypes.TARGET_SPAWNED, 'target_controller', target_id=self.id)
        
    async def lay_down(self):
        """Lay down target - hardware servo control would go here"""
        print(f"🎯 Target {self.id} laying down - servo moving to DOWN position!")
        self.is_standing = False
        await emit_event(EventTypes.TARGET_REMOVED, 'target_controller', target_id=self.id)
    
    async def activate_target(self, duration):
        """Stands up target. If the target registers a hit before duration expires, send hit report to master."""
        print(f"🎯 Target {self.id} activated for {duration} seconds - let the games begin!")
        
        self.is_active = True
        self.hit_detected = False
        
        await self.stand_up()
        
        start_time = time.time()
        
        while time.time() - start_time < duration and not self.hit_detected:
            if self._check_for_hit():
                self.hit_detected = True
                print(f"💥 HIT DETECTED on target {self.id}!")
                await self.target_server.report_hit(self.hit_value)
                await emit_event(EventTypes.TARGET_HIT, 'target_controller', 
                               target_id=self.id, hit_value=self.hit_value)
                break
            
            await asyncio.sleep(0.1)
        
        if not self.hit_detected:
            print(f"⏰ Target {self.id} timeout - no hit detected")
            await self.target_server.report_hit(0)
        
        await self.lay_down()
        self.is_active = False
        print(f"🎯 Target {self.id} deactivated")
    
    def _check_for_hit(self):
        """Check if target has been hit - hardware sensor reading would go here"""
        return False
    
    async def simulate_hit(self):
        """Simulate a hit for testing purposes"""
        if self.is_active and not self.hit_detected:
            print(f"🎯 Simulating hit on target {self.id}")
            self.hit_detected = True