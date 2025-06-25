import tkinter as tk
from tkinter import ttk
from views.settings import SettingsView
from translations.language import Language
from data.db import Database

class MainView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.lang = Language()
        self.translations = self.lang.load_translations()
        self.current_page = 0

        self.frame = ttk.Frame(parent)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.setup_layout()
        self.create_left_panel()
        self.create_log_table()
        self.create_right_panel()
    
    def setup_layout(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=5)
        self.frame.columnconfigure(2, weight=2)
        self.frame.rowconfigure(0, weight=1)
    
    def create_left_panel(self):
        left_panel = ttk.Frame(self.frame, padding=10)
        left_panel.grid(row=0, column=0, sticky="ns")

        logs_btn = ttk.Button(left_panel, text=self.translations["main"]["logs_button"], command=self.show_logs)
        logs_btn.pack(pady=(0, 10))

        config_btn = ttk.Button(left_panel, text=self.translations["settings"]["title"], command=self.open_settings)
        config_btn.pack()
    
    def create_right_panel(self):
        right_panel = ttk.Frame(self.frame, padding=10, relief="groove")
        right_panel.grid(row=0, column=2, sticky="nsew")

        title = ttk.Label(right_panel, text=self.translations["main"]["users_title"], font=("Helvetica", 12, "bold"))
        title.pack(anchor="w")

        self.users_list = tk.Listbox(right_panel)
        self.users_list.pack(expand=True, fill="both")

    def create_log_table(self):
        center_panel = ttk.Frame(self.frame, padding=10)
        center_panel.grid(row=0, column=1, sticky="nsew")

        title = ttk.Label(center_panel, text=self.translations["main"]["logs_title"], font=("Helvetica", 12, "bold"))
        title.pack(anchor="w")

        columns = ("name", "invitation_type", "time", "details")
        self.tree = ttk.Treeview(center_panel, columns=columns, show="headings")

        for header in columns:
            self.tree.heading(f"{header}", text=self.translations["main"][f"column_{header}"])
        
        self.tree.pack(expand=True, fill="both")

        pagination_frame = ttk.Frame(center_panel)
        pagination_frame.pack(fill="x", pady=5)

        self.page_size = tk.IntVar(value=10)
        ttk.Label(pagination_frame, text=self.translations["main"]["logs_per_page"]).pack(side="left")


        page_selector =ttk.Combobox(
            pagination_frame,
            textvariable=self.page_size,
            values=[5, 10, 20, 50, 100], # type: ignore
            state="readonly",
            width=5
        )
        page_selector.pack(side="left", padx=5)
        page_selector.bind("<<ComboboxSelected>>", lambda e: self.change_page(0))

        nav = ttk.Frame(pagination_frame)
        nav.pack(side="right")

        prev_btn = ttk.Button(nav, text=self.translations["main"]["prev"], command=self.prev_page)
        prev_btn.pack(side="left", padx=2)

        next_btn = ttk.Button(nav, text=self.translations["main"]["next"], command=self.next_page)
        next_btn.pack(side="left", padx=2)

        self.load_logs()
    
    def show_logs(self):
        self.change_page(0)
    
    def open_settings(self):
        SettingsView(self.parent)

    def load_logs(self):
        offset = self.current_page * self.page_size.get()
        logs = self.db.get_logs(limit=self.page_size.get(), offset=offset)
        self.populate_table(logs)
    
    def add_log_entry(self, log: dict):
        if self.current_page == 0:
            sender_user_name = log.get("username")
            invitation_type = log.get("type")
            notification_time = log.get("date")
            message = log.get("message")
            self.tree.insert("", 0, values=(sender_user_name, invitation_type, notification_time, message))
            if len(self.tree.get_children()) > self.page_size.get():
                last = self.tree.get_children()[-1]
                self.tree.delete(last)
    
    def populate_table(self, logs):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for log in logs:
            self.tree.insert("", "end", values=log)
    
    def change_page(self, page_number):
        self.current_page = page_number
        self.load_logs()
    
    def next_page(self):
        total = self.db.count_logs()
        
        if (self.current_page + 1) * self.page_size.get() < total:
            self.current_page +=1
            self.load_logs()
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -=1
            self.load_logs()
    
    def get_frame(self):
        return self.frame

