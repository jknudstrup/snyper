import json

class Config:
    def __init__(self):
        with open("config.json") as f:
            self.config = json.load(f)
            print("Loaded config.json")
            print(self.config)
        
    def get(self, key):
        return self.config[key]
    
    def set(self, key, value):
        self.config[key] = value
        
    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f)
            
config = Config()