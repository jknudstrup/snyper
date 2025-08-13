import asyncio
from typing import Set, List
from server import WebServer

class GameState:
    """Shared game state - the heart of Hulkamania!"""
    def __init__(self) -> None:
        self.score: int = 0
        self.active_targets: List[str] = []
        self.connected_clients: Set[str] = set()
        self.game_running: bool = False

# Global game state that gets shared between all components
game_state = GameState()

async def display_task() -> None:
    """Task to manage the ST7789 display - whatcha gonna do when this display runs wild on you!"""
    print("🎪 Display task starting, brother!")
    
    while True:
        # This is where you'd update your ST7789 display
        print(f"📺 Display update: Score={game_state.score}, Active targets={len(game_state.active_targets)}")
        
        # Simulate display refresh rate
        await asyncio.sleep(0.5)

async def game_loop_task() -> None:
    """Main game logic - the heart and soul of Hulkamania!"""
    print("🎯 Game loop starting, dude!")
    
    while True:
        if game_state.game_running:
            # This is where your game logic goes
            print("🎮 Game tick - checking targets, updating score...")
            
            # Example: Pop up a target every 3 seconds during game
            if len(game_state.active_targets) < 3:  # Max 3 targets
                target_id: str = f"target_{len(game_state.active_targets)}"
                game_state.active_targets.append(target_id)
                print(f"🎯 Target {target_id} popped up!")
        
        await asyncio.sleep(1.0)  # Game tick rate

async def web_server_task() -> None:
    """Initialize and run the web server - this is where the magic happens, dude!"""
    web_server = WebServer(game_state)  # Pass the shared state
    await web_server.start_server(host='0.0.0.0', port=80, debug=True)

async def main() -> None:
    """Main function that runs all tasks concurrently - the ultimate tag team match!"""
    print("🎪 Carnival Shooter Server starting up - BROTHER!")
    
    # Create all tasks - this is your wrestling stable!
    tasks: List[asyncio.Task[None]] = [
        asyncio.create_task(display_task()),
        asyncio.create_task(game_loop_task()),
        asyncio.create_task(web_server_task())
    ]
    
    try:
        # Run all tasks concurrently - let the chaos begin!
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down - until next time, Hulkamaniacs!")
    finally:
        # Clean shutdown
        task: asyncio.Task[None]
        for task in tasks:
            if not task.done():
                task.cancel()

if __name__ == "__main__":
    # Let's get this party started, brother!
    asyncio.run(main())