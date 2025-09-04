import uasyncio
from config.config import config
import time
from target.target_events import target_event_queue, HTTP_COMMAND_UP, HTTP_COMMAND_DOWN, HTTP_COMMAND_ACTIVATE

class TargetController:
    """Target Controller class. Executive component that manages target state and coordinates subordinate components."""
    
    def __init__(self, target_server, peripheral_controller):
        self.id = config.get('node_id', 'target_unknown')
        self.hit_value = config.get('hit_value', 10)
        self.target_server = target_server
        self.peripheral_controller = peripheral_controller
        self.is_active = False
        self.is_standing = False
        self.hit_detected = False
        
    async def process_events(self):
        """Main event processing loop - executive brain"""
        while True:
            event = await target_event_queue.get()
            await self._handle_event(event)
            target_event_queue.task_done()
    
    async def _handle_event(self, event):
        """Route events to appropriate handlers"""
        if event.type == HTTP_COMMAND_UP:
            await self.peripheral_controller.raise_target()
            self.is_standing = True
            print(f"🎯 Target {self.id} standing up - ready for action!")
        elif event.type == HTTP_COMMAND_DOWN:
            await self.peripheral_controller.lower_target()
            self.is_standing = False
            print(f"🎯 Target {self.id} laying down - taking cover!")
        elif event.type == HTTP_COMMAND_ACTIVATE:
            duration = event.data.get('duration', 5)
            await self.activate(duration)
        else:
            print(f"⚠️  Unknown event type: {event.type}")
    
    
    async def activate(self, duration):
        """Activate target with hit detection polling"""
        print(f"🎯 Target {self.id} activated for {duration} seconds - let the games begin!")
        
        self.is_active = True
        self.hit_detected = False
        
        # Raise target
        await self.peripheral_controller.raise_target()
        self.is_standing = True
        
        start_time = time.time()
        
        # Poll for hits until timeout or hit detected
        while time.time() - start_time < duration and not self.hit_detected:
            if self.peripheral_controller.hit_was_detected():
                self.hit_detected = True
                print(f"💥 HIT DETECTED on target {self.id}!")
                break
            await uasyncio.sleep_ms(10)  # 100Hz polling
        
        # Lower target and report result
        await self.peripheral_controller.lower_target()
        self.is_standing = False
        
        hit_value = 1 if self.hit_detected else 0
        if self.hit_detected:
            print(f"🎯 Target {self.id} hit! Reporting success.")
        else:
            print(f"⏰ Target {self.id} timeout - no hit detected")
            
        await self.target_server.report_result(hit_value)
        
        self.is_active = False
        print(f"🎯 Target {self.id} deactivated")
    
    async def simulate_hit(self):
        """Simulate a hit for testing purposes"""
        if self.is_active and not self.hit_detected:
            print(f"🎯 Simulating hit on target {self.id}")
            self.hit_detected = True