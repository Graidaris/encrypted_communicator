import os
import json

DEFAULT_CONFIGS = {"FOLDERS": {"LOGING": "Logs",
                            "DOWNLOAD": "Downloads",
                            "PRIVAT_KEY": "priv_key",
                            "PUBLIC_KEYS": "pub_keys"},
                "SIZE_RSA_KEY": 3072,
                "BUFFER_SIZE": 1024}

DEFAULT_FILENAME = "config.json"


class ConfigManager:
    def __init__(self):
        self.config = {}

    def load_config(self, path=DEFAULT_FILENAME) -> None:
        """Load the config file.
        Params:
            param 1: path = path to the config, default path = DEFAULT_FILENAME
        
        """
        
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.config = json.load(f)
                
    def integrity(self) -> None:
        """Check the config for integrity."""
        ConfigManager.check_integrity(self.config, DEFAULT_CONFIGS)
        
    def save_config(self, path=DEFAULT_FILENAME):
        path, filename = os.path.split(path)
        if path != "":
            if not os.path.exists(path):
                os.makedirs(path)
            
        with open(filename, 'w') as f:
            json.dump(self.config, f)
    
    @staticmethod
    def check_integrity(a:dict, b:dict) -> None:
        """Check if everything necessary is present in the config. 
        Comparing a and b dictionary.
        
        """
        
        for key_b in b:
            if not key_b in a:
                a[key_b] = b[key_b]                
            elif type(b[key_b]) is dict:
                ConfigManager.check_integrity(a[key_b], b[key_b])
            elif type(a[key_b]) is not type(b[key_b]):
                raise TypeError(f"type of key:{key_b} = {type(b[key_b])} and {type(a[key_b])}  ")
    
