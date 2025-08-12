import json
from machine import Pin
from time import sleep

# load the config file from flash
with open("config.json") as f:
    config = json.load(f)

# init LED and button
# led = Pin(2, Pin.OUT)
# btn = Pin(0)

def save_config():
    """function to save the config dict to the JSON file"""
    with open("config.json", "w") as f:
        json.dump(config, f)