import os
import json

class Settings:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), 'settings.json')
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)
    
    def get_language(self):
        return self.data.get("language", "en")
    
    def set_language(self, language):
        self.data["language"] = language
        self._save()