import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import pyperclip
import os
import json
import configparser  # <-- to read config.ini

class IndexGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SCH Index Generator")

        # ==============================
        # 1. Load config.ini file
        # ==============================
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

        # Create a default config if it doesn't exist
        if not os.path.exists(self.config_path):
            self.create_default_config()

        # Read the config file
        self.config.read(self.config_path)

        # Extract values (with fallback if missing)
        self.font_size_title = self.config.getint('DEFAULTS', 'font_size_title', fallback=10)
        self.font_size_version = self.config.getint('DEFAULTS', 'font_size_version', fallback=10)
        self.font_size_header = self.config.getint('DEFAULTS', 'font_size_header', fallback=5)
        self.font_size_page = self.config.getint('DEFAULTS', 'font_size_page', fallback=4)
        default_spacing = self.config.get('DEFAULTS', 'default_spacing', fallback="150")
        default_lang = self.config.get('DEFAULTS', 'default_language', fallback="en")
        save_new_file_str = self.config.get('DEFAULTS', 'save_in_new_file', fallback="false").lower()

        # ==============================
        # 2. Create GUI elements
        # ==============================
        tk.Label(root, text="Project Name:").pack(pady=5)
        self.project_name_entry = tk.Entry(root, width=40)
        self.project_name_entry.pack(pady=5)

        tk.Label(root, text="Version:").pack(pady=5)
        self.version_entry = tk.Entry(root, width=40)
        self.version_entry.pack(pady=5)

        tk.Label(root, text="Spacing between columns:").pack(pady=5)
        self.spacing_entry = tk.Entry(root, width=10)
        self.spacing_entry.pack(pady=5)
        self.spacing_entry.insert(0, default_spacing)

        self.language_var = tk.BooleanVar()
        self.language_var.set(True if default_lang.lower() == "en" else False)
        tk.Checkbutton(root, text="Language in English", variable=self.language_var).pack(pady=5)

        self.new_file_var = tk.BooleanVar()
        self.new_file_var.set(True if save_new_file_str == "true" else False)
        tk.Checkbutton(root, text="Save in new file (don't overwrite)", variable=self.new_file_var).pack(pady=5)

        self.pages_listbox = tk.Listbox(root, width=50, height=10)
        self.pages_listbox.pack(pady=5)
        self.pages
