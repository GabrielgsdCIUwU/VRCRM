import tkinter as tk
from tkinter import ttk, messagebox

class Login:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
       
        # Cargar traducciones
        from translations.language import Language as lg
        self.translations = lg().load_translations()

        # Variables para los campos de entrada
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Título
        self.title_label = ttk.Label(
            self.frame, 
            text=self.translations["login"]["title"], 
            font=('Helvetica', 16, 'bold')
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Campo de usuario
        ttk.Label(
            self.frame, 
            text=self.translations["login"]["username_label"]
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Campo de contraseña
        ttk.Label(
            self.frame, 
            text=self.translations["login"]["password_label"]
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Botón de inicio de sesión
        self.login_button = ttk.Button(
            self.frame, 
            text=self.translations["login"]["login_button"], 
            command=self.check_login
        )
        self.login_button.grid(row=5, column=0, columnspan=2, pady=20)

    def check_login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror(
                "Error", 
                self.translations["login"]["error_empty_fields"]
            )
            return

    def get_frame(self):
        return self.frame

