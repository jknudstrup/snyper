import uasyncio
from target.target_server import TargetServer
from target.target_controller import TargetController
from target.peripheral_controller import peripheral_controller


async def run_target():
    """Main target application - coordinates target server and controller"""
    print("🎯 Starting Target System - ready to rumble!")
    
    target_server = TargetServer()
    target_controller = TargetController(target_server, peripheral_controller)
    
    print(f"🎯 Target {target_controller.id} system initialized")
    
    try:
        # Start both the server loop and controller event processing loop concurrently
        await uasyncio.gather(
            target_server.start_server(),          # HTTP server loop
            target_controller.process_events(),    # Event processing loop
        )
    except KeyboardInterrupt:
        print("🛑 Target system shutdown requested")
    except Exception as e:
        print(f"💥 Target system error: {e}")
        raise
    
if __name__ == "__main__":
    uasyncio.run(run_target())