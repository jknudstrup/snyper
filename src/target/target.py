import asyncio
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
        await target_server.start_server()
    except KeyboardInterrupt:
        print("🛑 Target system shutdown requested")
    except Exception as e:
        print(f"💥 Target system error: {e}")
        raise
    
if __name__ == "__main__":
    asyncio.run(run_target())