import tkinter as tk
from tkinter import ttk
from views.login import Login
from translations.language import Language
from views.settings import SettingsView

class MainApp:
    def __init__(self):

        self.ventana = tk.Tk()
        self.lang = Language()
        self.translations = self.lang.load_translations()
        self.ventana.title("VRChat CRM")
        self.ventana.geometry("400x500")
        self.ventana.configure(bg='#f0f0f0') 

        
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(0, weight=1)


        self.settings_button = ttk.Button(
            self.ventana,
            text=self.translations["settings"]["tabs"]["language"],
            command=self.open_settings
        )
        self.settings_button.grid(row=1, column=0, pady=10)

    def init_login(self):
        self.login_view = Login(self.ventana)
        self.login_frame = self.login_view.get_frame()
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def open_settings(self):
        SettingsView(self.ventana)
    

    def iniciar(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.iniciar()