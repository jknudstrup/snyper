import asyncio
from config import config

"""Target Controller class. Tracks target state and handles interactions with the target hardware components. Interacts with target_server via event bus."""

class TargetController:
    def __init__(self):
        self.id = config.get('node_id')
        self.hit_value = config.get('hit_value')
        
    def stand_up(self):
        # TODO: Send command to servo to stand up target.
        pass
    
    def lay_down(self):
        # TODO: Send command to servo to lay down target.
        pass
    
    def activate_target(self, duration):
        """TODO: Stands up target. If the target registers a hit before duration expires, send a POST to the /target_hit endpoint with the target's ID and hit value. Otherwise, sends a message to the same point, but with a hit value of 0."""
        pass
    
def run_target():
    print("Target code coming soon!")
    
if __name__ == "__main__":
    asyncio.run(run_target())