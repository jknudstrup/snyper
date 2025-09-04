import asyncio

class TargetEvent:
    """Event object for target system communication"""
    def __init__(self, event_type, data=None):
        self.type = event_type
        self.data = data or {}
    
    def __repr__(self):
        return f"TargetEvent(type='{self.type}', data={self.data})"

# Event Types - Server → Controller Events
HTTP_COMMAND_UP = "http_command_up"
HTTP_COMMAND_DOWN = "http_command_down"  
HTTP_COMMAND_ACTIVATE = "http_command_activate"

# Global event queue for target system
target_event_queue = asyncio.Queue()