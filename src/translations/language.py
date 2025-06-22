import json
import os

class Language:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Language, cls).__new__(cls)
            cls._instance.language = "en"
        return cls._instance
    
    def set_language(self, language):
        self.language = language
    
    def get_language(self):
        return self.language
    
    def load_translations(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'languages' , f"{self.get_language()}.json"), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return print(f"Error loading translations: {e}")

