# Centralized AI Configuration Manager

class AIConfigManager:
    def __init__(self, config):
        self.config = config

    def get_setting(self, key):
        return self.config.get(key, None)

    def set_setting(self, key, value):
        self.config[key] = value

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.config, f)

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, 'r') as f:
            config = json.load(f)
        return cls(config)