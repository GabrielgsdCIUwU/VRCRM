import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from translations.language import Language

class SettingsView(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.lang = Language()
        self.translations = self.lang.load_translations()
        self.title(self.translations["settings"]["title"])
        self.geometry("400x200")
        self.create_widgets()
    
    def create_widgets(self):
        notebook = ttk.Notebook(self)
        self.tabs = {}

        for tab in ["users", "roles", "profiles", "messages", "language"]:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=self.translations["settings"]["tabs"][tab])
            self.tabs[tab] = frame

        notebook.pack(expand=True, fill="both")
        self.language_tab()

        
        

    def language_tab(self):
        language_tab = self.tabs["language"]
        label = ttk.Label(language_tab, text=self.translations["settings"]["language_label"])
        label.pack(pady=(20,5))

        language_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations', 'languages')
        name_languages = [f[:-5] for f in os.listdir(language_dir) if f.endswith('.json')]
        self.language_var = tk.StringVar(value=self.lang.get_language())

        combo = ttk.Combobox(language_tab, textvariable=self.language_var, values=name_languages, state="readonly")
        combo.pack(pady=5)
    
        btn = ttk.Button(language_tab, text=self.translations["settings"]["save_button"], command=self.save_language)
        btn.pack(pady=20)

    def save_language(self):
        selected = self.language_var.get()
        self.lang.set_language(selected)

        self.translations = self.lang.load_translations()
        msg = self.translations["settings"]["success_message"].format(language=selected)
        messagebox.showinfo(self.translations["settings"]["title"], msg)

        self.destroy()

        # Reboot after saving the data
        self.after(100, lambda: os.execl(sys.executable, sys.executable, *sys.argv))

