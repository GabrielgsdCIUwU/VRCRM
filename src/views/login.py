import tkinter as tk
from tkinter import ttk, messagebox
from vrchat.vrchat import VRChatAPI
from translations.language import Language as lg

class Login:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
       
        # Cargar traducciones
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
        
        api = VRChatAPI()

        try:
            result = api.login(username, password)

            if "requiresTwoFactorAuth" in result: # type: ignore
                code = self.ask_2fa_code()
                if not code:
                    return
                result = api.login(username, password, totp_code=code)
            
            display_name = result.get("displayName", username)
            messagebox.showinfo("Login", self.translations["login"]["login_success"].format(display_name))
        except Exception as e:
            messagebox.showerror("Error", f"{self.translations["login"]["login_error"]} {str(e)}")

    def ask_2fa_code(self):
        popup = tk.Toplevel(self.parent)
        popup.title(f"{self.translations["login"]["two_factor"]}").grid(row=0, column=0, padx=10, pady=10)
        code_var =tk.StringVar()
        entry = ttk.Entry(popup, textvariable=code_var)
        entry.grid(row=1, column=0, padx=10, pady=5)
        entry.focus()
        
        def submit():
            popup.destroy()
        
        ttk.Button(popup, text="Submit", command=submit).grid(row=2, column=0, pady=10)
        popup.grab_set()
        self.parent.wait_window(popup)

        return code_var.get().strip()

    def get_frame(self):
        return self.frame

