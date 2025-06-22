from data.db import Database
class Settings:
    def __init__(self):
        self.db = Database()

    def get_language(self):
        return self.db.get_setting("language", "English")
    
    def set_language(self, language):
        self.db.set_setting("language", language)
