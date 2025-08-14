import asyncio

from config import config
from master import run_master
from target import run_target

def main():
    if config.node_id == "master":
        asyncio.run(run_master())
    else:
        asyncio.run(run_target())
    

if __name__ == "__main__":
    # Deploy all forces for the main operation!
    asyncio.run(main())