import uasyncio

class TargetEvent:
    """Event object for target system communication"""
    def __init__(self, event_type, data=None):
        self.type = event_type
        self.data = data or {}
    
    def __repr__(self):
        return f"TargetEvent(type='{self.type}', data={self.data})"

class SimpleQueue:
    """Simple async queue implementation for MicroPython"""
    def __init__(self):
        self._queue = []
        self._event = uasyncio.Event()
    
    async def put(self, item):
        """Put an item into the queue"""
        self._queue.append(item)
        self._event.set()
        self._event.clear()
    
    async def get(self):
        """Get an item from the queue, waiting if necessary"""
        while not self._queue:
            await self._event.wait()
        return self._queue.pop(0)
    
    def task_done(self):
        """Compatibility method - no-op for our simple implementation"""
        pass

# Event Types - Server → Controller Events
HTTP_COMMAND_UP = "http_command_up"
HTTP_COMMAND_DOWN = "http_command_down"  
HTTP_COMMAND_ACTIVATE = "http_command_activate"

# Global event queue for target system
target_event_queue = SimpleQueue()