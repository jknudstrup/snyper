import json

class Config:
    """Configuration manager with type hints and error handling - BROTHER!"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load config from file with device_id overlay"""
        try:
            # Load main config (source controlled)
            with open(self.config_file) as f:
                self.config = json.load(f)
                print("✅ Loaded config.json")
                
            # Try to load device_id.json overlay (gitignored)
            try:
                with open("device_id.json") as f:
                    device_config = json.load(f)
                    self.config.node_id = device_config.node_id
                    # self.config.update(device_config)  # Merge device identity
                    # print(f"✅ Loaded device identity: {device_config.get('node_id')}")
            except OSError:
                print("ℹ️  No device_id.json found, using config.json node_id")
                
            print(self.config)
        except OSError:
            print(f"⚠️  Config file {self.config_file} not found, using defaults")
            self._set_defaults()
        except ValueError as e:
            print(f"💥 Error parsing config file: {e}")
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default configuration values"""
        self.config = {
            "node_id": "master",
            "ssid": "PICO_AP_DEFAULT",
            "password": "micropython123",
            "server_ip": "192.168.4.1",
            "port": 80
        }
        print("🔧 Using default configuration")
        self.save_config()  # Save defaults for next time
    
    def get(self, key, default=None):
        """Get a config value with optional default"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a config value"""
        self.config[key] = value
        
    def save_config(self):
        """Save current config to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            print(f"💾 Config saved to {self.config_file}")
        except OSError as e:
            print(f"💥 Failed to save config: {e}")
    
    # Type-safe property accessors - the fancy stuff!
    @property
    def ssid(self) -> str:
        return self.get("ssid", "PICO_AP_DEFAULT")
    
    @property 
    def password(self) -> str:
        return self.get("password", "micropython123")
    
    @property
    def server_ip(self) -> str:
        return self.get("server_ip", "192.168.4.1")
    
    @property
    def port(self) -> int:
        return int(self.get("port", 80))
    
    @ssid.setter
    def ssid(self, value: str):
        self.set("ssid", value)
    
    @password.setter  
    def password(self, value: str):
        self.set("password", value)
    
    @server_ip.setter
    def server_ip(self, value: str):
        self.set("server_ip", value)
    
    @port.setter
    def port(self, value: int):
        self.set("port", value)

# Global config instance - the one true champion!
config = Config()