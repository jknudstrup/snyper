import asyncio
from master_server import MasterServer
from display import start_display
from events import event_bus, emit_event, subscribe_to_event, EventTypes

class GameState:
    """Shared game state - the backbone of our operation!"""
    def __init__(self):
        self.score = 0
        self.active_targets = []
        self.connected_clients = set()
        self.game_running = False
        # Reference to our central command - ensuring unified communications
        self.event_bus = event_bus

# Global game state that gets shared between all components
game_state = GameState()

async def game_loop_task():
    """Main game logic - our strategic command centre!"""
    print("🎯 Game loop starting, old chap!")
    
    # Subscribe to events that affect game logic
    subscribe_to_event(EventTypes.GAME_STARTED, handle_game_start, "game_loop")
    subscribe_to_event(EventTypes.GAME_STOPPED, handle_game_stop, "game_loop") 
    subscribe_to_event(EventTypes.TARGET_HIT, handle_target_hit, "game_loop")
    
    while True:
        if game_state.game_running:
            # This is where your game logic goes
            print("🎮 Game tick - maintaining operational readiness...")
            
            # Example: Pop up a target every 3 seconds during game
            if len(game_state.active_targets) < 3:  # Max 3 targets
                target_id = f"target_{len(game_state.active_targets)}"
                game_state.active_targets.append(target_id)
                print(f"🎯 Target {target_id} deployed!")
                
                # Broadcast intelligence about new target
                await emit_event(EventTypes.TARGET_SPAWNED, "game_loop", 
                               target_id=target_id, position=len(game_state.active_targets))
        
        await asyncio.sleep(1.0)  # Strategic pause between operations

# Event handlers for game loop - our intelligence officers
async def handle_game_start(event):
    """Respond to game start orders"""
    print("🚀 Game loop received START command!")
    game_state.game_running = True

async def handle_game_stop(event):
    """Respond to game stop orders"""
    print("🛑 Game loop received STOP command!")
    game_state.game_running = False

async def handle_target_hit(event):
    """Process target elimination reports"""
    target_id = event.data.get('target_id')
    if target_id and target_id in game_state.active_targets:
        game_state.active_targets.remove(target_id)
        old_score = game_state.score
        game_state.score += 10
        print(f"💥 Target {target_id} eliminated! Score: {old_score} -> {game_state.score}")
        
        # Broadcast score change intelligence
        await emit_event(EventTypes.SCORE_CHANGED, "game_loop",
                        old_score=old_score, new_score=game_state.score, target_id=target_id)

async def master_server_task():
    """Initialize and run the master server - our communications headquarters!"""
    master_server = MasterServer(game_state)  # Pass the shared state
    await master_server.start_server(debug=True)  # Uses config values now!

async def run_master():
    """Main function that coordinates all operations - our supreme command centre!"""
    print("🎪 Carnival Shooter Server deploying forces - FOR KING AND COUNTRY!")
    
    # Deploy the display unit first, synchronously, as per operational doctrine
    start_display()
    
    # Deploy our async task forces - the backbone of operations!
    tasks = [
        asyncio.create_task(game_loop_task()),
        asyncio.create_task(master_server_task())
    ]
    
    try:
        # Run all operations concurrently - coordinated strategic deployment!
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down operations - God save the King!")
    except Exception as e:
        print(f"\n💥 Unexpected tactical situation: {e}")
    finally:
        # Strategic withdrawal - proper military order maintained!
        print("🔧 Organizing tactical withdrawal...")
        for task in tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass  # Expected during withdrawal
        print("✅ All forces withdrawn successfully - mission accomplished!")

if __name__ == "__main__":
    # Deploy all forces for the main operation!
    asyncio.run(run_master())