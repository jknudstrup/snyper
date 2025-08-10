# from client import Client

# print("Running main.py for client")
# client = Client()
# client.start()
from client import Client

print("Running main.py for client")

try:
    client = Client()
    client.start()
except KeyboardInterrupt:
    print("\nInterrupted - cleaning up...")
    if 'client' in locals():
        client.cleanup()
except Exception as e:
    print(f"Error: {e}")
    if 'client' in locals():
        client.cleanup()
    raise