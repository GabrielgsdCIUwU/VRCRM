import tkinter as tk
from tkinter import ttk
from views.login import Login
from translations.language import Language
from views.settings import SettingsView
from views.main import MainView
from vrchat.vrchat import VRChatAPI
import threading
from data.db import Database

class MainApp:
    def __init__(self):
        self.vrchatApi = VRChatAPI()
        self.ventana = tk.Tk()
        self.lang = Language()
        self.translations = self.lang.load_translations()
        self.ventana.title("VRChat CRM")
        self.ventana.geometry("400x500")
        self.ventana.configure(bg='#f0f0f0') 

        
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(0, weight=1)




        self.check_is_logged_in()

    def init_login(self):
        self.login_view = Login(self.ventana)
        self.login_frame = self.login_view.get_frame()
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def open_settings(self):
        SettingsView(self.ventana, custom_tabs=["language"])
    
    def open_main_page(self):
        self.main_view = MainView(self.ventana)

        def background_tasks():
            # Crear nueva instancia para poder usar en distinto hilo
            db = Database()

            """
            message: Message during a normal invite
            response: Message when replying to a message
            request: Message when requesting an invite
            requestResponse: Message when replying to a request for invite
            """
            message_types = ["message", "response", "request", "requestResponse"]
            for type in message_types:
                try:
                    self.main_view.db.ensure_vrchat_messages(self.vrchatApi, message_type=type)
                except Exception as e:
                    print(f"Ensure VRChat messages: {e}")
                    continue

            # Add id (owner account) for self-invites
            for user_id in self.vrchat_user_data["friends"] + [self.vrchat_user_data["id"]]:
                try:
                    if not db.user_exists(user_id):
                        db.insert_user(user_id=user_id, name=self.vrchatApi.get_user_by_id(user_id)["displayName"])
                except Exception as e:
                    print(f"Insert user_id to db Exception: {e}")
                    continue
            db.close()
            self.vrchatApi.connect_pipeline(on_event=self.handle_event)
        
        threading.Thread(target=background_tasks, daemon=True).start()
            
    
    def handle_event(self, notification):
        print(f"handle: {notification}")
        def update_ui():
            try:
                if self.main_view:
                    self.main_view.add_log_entry(notification)
            except Exception as e:
                print(f"update_ui Exception: {e}")
        
        self.ventana.after(0, update_ui)
    
    
    def check_is_logged_in(self):
        try:
            logged_in, user_data = self.vrchatApi.is_logged_in()
            self.vrchat_user_data = user_data

            print(logged_in)
            if logged_in:
                self.open_main_page()
            
            else:
                self.init_login()
        except Exception as e:
            print(f"Check is logged in Exception: {e}")
            self.init_login()

    def iniciar(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.iniciar()