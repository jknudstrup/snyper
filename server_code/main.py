import asyncio
from server import WebServer

class GameState:
    """Shared game state - the heart of Hulkamania!"""
    def __init__(self):
        self.score = 0
        self.active_targets = []
        self.connected_clients = set()
        self.game_running = False

# Global game state that gets shared between all components
game_state = GameState()

async def display_task():
    """Task to manage the ST7789 display - whatcha gonna do when this display runs wild on you!"""
    print("🎪 Display task starting, brother!")
    last_score = -1  # Track changes to reduce spam
    last_target_count = -1
    
    while True:
        # Only print when something actually changes - no more spam, dude!
        current_score = game_state.score
        current_targets = len(game_state.active_targets)
        
        if current_score != last_score or current_targets != last_target_count:
            print(f"📺 Display update: Score={current_score}, Active targets={current_targets}")
            last_score = current_score
            last_target_count = current_targets
        
        # This is where you'd update your ST7789 display
        # Slower refresh rate - displays don't need crazy updates
        await asyncio.sleep(2.0)

async def game_loop_task():
    """Main game logic - the heart and soul of Hulkamania!"""
    print("🎯 Game loop starting, dude!")
    
    while True:
        if game_state.game_running:
            # This is where your game logic goes
            print("🎮 Game tick - checking targets, updating score...")
            
            # Example: Pop up a target every 3 seconds during game
            if len(game_state.active_targets) < 3:  # Max 3 targets
                target_id = f"target_{len(game_state.active_targets)}"
                game_state.active_targets.append(target_id)
                print(f"🎯 Target {target_id} popped up!")
        
        await asyncio.sleep(1.0)  # Game tick rate

async def web_server_task():
    """Initialize and run the web server - this is where the magic happens, dude!"""
    web_server = WebServer(game_state)  # Pass the shared state
    await web_server.start_server(host='0.0.0.0', port=80, debug=True)

async def main():
    """Main function that runs all tasks concurrently - the ultimate tag team match!"""
    print("🎪 Carnival Shooter Server starting up - BROTHER!")
    
    # Create all tasks - this is your wrestling stable!
    tasks = [
        asyncio.create_task(display_task()),
        asyncio.create_task(game_loop_task()),
        asyncio.create_task(web_server_task())
    ]
    
    try:
        # Run all tasks concurrently - let the chaos begin!
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down - until next time, Hulkamaniacs!")
    except Exception as e:
        print(f"\n💥 Unexpected error, brother: {e}")
    finally:
        # Clean shutdown - make sure we can get out of this ring!
        print("🔧 Cleaning up tasks...")
        for task in tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass  # Expected when cancelling
        print("✅ All tasks cleaned up - see ya later, Hulkamaniacs!")

if __name__ == "__main__":
    # Let's get this party started, brother!
    asyncio.run(main())