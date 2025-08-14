import asyncio

class Event:
    """An event carrying intelligence across our digital theatre of operations"""
    
    def __init__(self, event_type, source=None, data=None):
        self.event_type = event_type
        self.source = source
        self.data = data or {}
        self.timestamp = None  # Could add time.time() if needed
    
    def __repr__(self):
        return f"Event(type='{self.event_type}', source='{self.source}', data={self.data})"

class EventBus:
    """Our central command for coordinating communications between forces"""
    
    def __init__(self):
        # Subscribers organized by event type - like military units assigned to sectors
        self._subscribers = {}  # Manual dictionary instead of defaultdict
        # Event queues for async processing - our message dispatch system
        self._event_queues = {}
        # Debug mode for monitoring communications
        self._debug = False
    
    def enable_debug(self, enabled=True):
        """Enable or disable debug monitoring of all communications"""
        self._debug = enabled
    
    def subscribe(self, event_type, handler, task_name=None):
        """Register a handler for specific intelligence reports"""
        if task_name:
            print(f"📡 Task '{task_name}' subscribing to '{event_type}' events")
        
        # Manual defaultdict behavior - create list if not exists
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type, handler):
        """Remove a handler from the intelligence network"""
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
    
    async def publish(self, event):
        """Broadcast intelligence to all interested parties"""
        if self._debug:
            print(f"🚨 EVENT DISPATCH: {event}")
        
        # Send to all subscribers of this event type
        handlers = self._subscribers.get(event.event_type, [])  # Get handlers or empty list
        if handlers:
            # Execute all handlers concurrently - maximum efficiency!
            await asyncio.gather(*[
                self._safe_call_handler(handler, event) 
                for handler in handlers
            ], return_exceptions=True)
        elif self._debug:
            print(f"⚠️  No handlers registered for event type: {event.event_type}")
    
    async def _safe_call_handler(self, handler, event):
        """Execute a handler with proper error containment"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            print(f"💥 Handler error for {event.event_type}: {e}")
    
    def create_queue_subscriber(self, task_name):
        """Create a queue-based subscriber for a task that processes events in sequence"""
        queue = asyncio.Queue()
        self._event_queues[task_name] = queue
        return EventQueueSubscriber(queue, task_name, self)

class EventQueueSubscriber:
    """A specialized subscriber that processes events through a queue - perfect for sequential operations"""
    
    def __init__(self, queue, task_name, event_bus):
        self.queue = queue
        self.task_name = task_name
        self.event_bus = event_bus
    
    def subscribe_to(self, event_type):
        """Subscribe this queue to receive specific types of intelligence"""
        async def queue_handler(event):
            await self.queue.put(event)
        
        self.event_bus.subscribe(event_type, queue_handler, self.task_name)
    
    async def get_event(self):
        """Wait for the next piece of intelligence"""
        return await self.queue.get()
    
    async def process_events(self, handler):
        """Continuously process events as they arrive"""
        while True:
            event = await self.get_event()
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"💥 Event processing error in {self.task_name}: {e}")

# Our central command post - the nerve centre of operations
event_bus = EventBus()

# Convenience functions for rapid deployment
async def emit_event(event_type, source=None, **data):
    """Rapidly dispatch intelligence to all interested parties"""
    event = Event(event_type, source, data)
    await event_bus.publish(event)

def subscribe_to_event(event_type, handler, task_name=None):
    """Quickly establish a listening post for specific intelligence"""
    event_bus.subscribe(event_type, handler, task_name)

# Standard event types - our operational codes
class EventTypes:
    # Game state events
    GAME_STARTED = "game_started"
    GAME_STOPPED = "game_stopped"
    SCORE_CHANGED = "score_changed"
    
    # Target events  
    TARGET_HIT = "target_hit"
    TARGET_SPAWNED = "target_spawned"
    TARGET_REMOVED = "target_removed"
    
    # Client events
    CLIENT_CONNECTED = "client_connected"
    CLIENT_DISCONNECTED = "client_disconnected"
    
    # Debug/Control events
    DEBUG_COMMAND = "debug_command"
    TARGET_CONTROL = "target_control"  # For your debug screen example
    
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_SHUTDOWN = "system_shutdown"