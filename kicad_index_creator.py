import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pyperclip
import os
import json
import configparser


class IndexGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KiCad Index Generator")
        self.root.resizable(False, False)

        self._load_config()
        self._build_ui()

    def _load_config(self):
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        if not os.path.exists(self.config_path):
            self._create_default_config()
        self.config.read(self.config_path)

        self.font_size_title   = self.config.getint('DEFAULTS', 'font_size_title',   fallback=10)
        self.font_size_version = self.config.getint('DEFAULTS', 'font_size_version', fallback=10)
        self.font_size_header  = self.config.getint('DEFAULTS', 'font_size_header',  fallback=5)
        self.font_size_page    = self.config.getint('DEFAULTS', 'font_size_page',    fallback=4)
        self.default_spacing   = self.config.get('DEFAULTS', 'default_spacing',      fallback="150")
        self.default_lang      = self.config.get('DEFAULTS', 'default_language',     fallback="es")
        save_new_str           = self.config.get('DEFAULTS', 'save_in_new_file',     fallback="false").lower()
        self.default_save_new  = save_new_str == "true"

    def _create_default_config(self):
        default_content = """[DEFAULTS]
font_size_title = 10
font_size_version = 10
font_size_header = 5
font_size_page = 4
default_spacing = 150
default_language = es
save_in_new_file = false
"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(default_content)

    def _save_config(self):
        self.config['DEFAULTS']['font_size_title']   = str(self.font_size_title)
        self.config['DEFAULTS']['font_size_version'] = str(self.font_size_version)
        self.config['DEFAULTS']['font_size_header']  = str(self.font_size_header)
        self.config['DEFAULTS']['font_size_page']    = str(self.font_size_page)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def _build_ui(self):
        PAD = {"padx": 10, "pady": 4}

        # Project Settings
        proj_frame = ttk.LabelFrame(self.root, text="Project Settings", padding=10)
        proj_frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(proj_frame, text="Project Name:").grid(row=0, column=0, sticky="w", **PAD)
        self.project_name_entry = ttk.Entry(proj_frame, width=35)
        self.project_name_entry.grid(row=0, column=1, sticky="w", **PAD)

        ttk.Label(proj_frame, text="Version:").grid(row=1, column=0, sticky="w", **PAD)
        self.version_entry = ttk.Entry(proj_frame, width=35)
        self.version_entry.grid(row=1, column=1, sticky="w", **PAD)

        # Layout Settings
        layout_frame = ttk.LabelFrame(self.root, text="Layout Settings", padding=10)
        layout_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(layout_frame, text="Column Spacing:").grid(row=0, column=0, sticky="w", **PAD)
        self.spacing_entry = ttk.Entry(layout_frame, width=8)
        self.spacing_entry.grid(row=0, column=1, sticky="w", **PAD)
        self.spacing_entry.insert(0, self.default_spacing)

        self.language_var = tk.BooleanVar(value=self.default_lang.lower() == "en")
        ttk.Checkbutton(layout_frame, text="English language", variable=self.language_var).grid(
            row=1, column=0, columnspan=2, sticky="w", **PAD)

        self.new_file_var = tk.BooleanVar(value=self.default_save_new)
        ttk.Checkbutton(layout_frame, text="Save in a new file (do not overwrite)", variable=self.new_file_var).grid(
            row=2, column=0, columnspan=2, sticky="w", **PAD)

        # Pages
        pages_frame = ttk.LabelFrame(self.root, text="Pages", padding=10)
        pages_frame.pack(fill="both", expand=True, padx=10, pady=5)

        list_frame = ttk.Frame(pages_frame)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.pages_listbox = tk.Listbox(list_frame, width=52, height=8, yscrollcommand=scrollbar.set,
                                        selectmode=tk.SINGLE)
        self.pages_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.pages_listbox.yview)
        self.pages_listbox.bind("<Double-Button-1>", self.modify_page)

        btn_frame = ttk.Frame(pages_frame)
        btn_frame.pack(fill="x", pady=(6, 0))

        ttk.Button(btn_frame, text="Add",    command=self.add_page).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Edit",   command=self.modify_page).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_page).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="▲", width=3, command=self.move_up).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="▼", width=3, command=self.move_down).pack(side="left", padx=2)

        # Action buttons
        action_frame = ttk.Frame(self.root, padding=(10, 5, 10, 10))
        action_frame.pack(fill="x")

        ttk.Button(action_frame, text="Load File",        command=self.load_file).pack(side="left", padx=4)
        ttk.Button(action_frame, text="Adjust Text Sizes", command=self.open_font_settings).pack(side="left", padx=4)
        ttk.Button(action_frame, text="Generate Index",   command=self.generate_index).pack(side="right", padx=4)

    # --- Page list operations ---

    def add_page(self):
        page_name = simpledialog.askstring("Add Page", "Enter the page name:")
        if not page_name:
            return
        page_number = simpledialog.askstring("Add Page", "Enter the page number:")
        if page_number:
            self.pages_listbox.insert(tk.END, f"{page_name} # {page_number}")

    def delete_page(self):
        try:
            index = self.pages_listbox.curselection()[0]
        except IndexError:
            return
        self.pages_listbox.delete(index)

    def move_up(self):
        try:
            index = self.pages_listbox.curselection()[0]
        except IndexError:
            return
        if index == 0:
            return
        item = self.pages_listbox.get(index)
        self.pages_listbox.delete(index)
        self.pages_listbox.insert(index - 1, item)
        self.pages_listbox.selection_set(index - 1)

    def move_down(self):
        try:
            index = self.pages_listbox.curselection()[0]
        except IndexError:
            return
        if index >= self.pages_listbox.size() - 1:
            return
        item = self.pages_listbox.get(index)
        self.pages_listbox.delete(index)
        self.pages_listbox.insert(index + 1, item)
        self.pages_listbox.selection_set(index + 1)

    def modify_page(self, event=None):
        try:
            index = self.pages_listbox.curselection()[0]
        except IndexError:
            if event:
                index = self.pages_listbox.nearest(event.y)
            else:
                return
        item = self.pages_listbox.get(index)
        try:
            page_name, page_number = item.rsplit(" # ", 1)
        except ValueError:
            return

        new_name = simpledialog.askstring("Edit Page", "Page name:", initialvalue=page_name)
        if new_name is None:
            return
        new_number = simpledialog.askstring("Edit Page", "Page number:", initialvalue=page_number)
        if new_number is None:
            return

        self.pages_listbox.delete(index)
        self.pages_listbox.insert(index, f"{new_name} # {new_number}")
        self.pages_listbox.selection_set(index)

    # --- Font settings ---

    def open_font_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Adjust Text Sizes")
        win.resizable(False, False)
        win.grab_set()

        fields = [
            ("Title Size:",     self.font_size_title),
            ("Version Size:",   self.font_size_version),
            ("Header Size:",    self.font_size_header),
            ("Page Text Size:", self.font_size_page),
        ]
        spinboxes = []
        for row, (label, value) in enumerate(fields):
            ttk.Label(win, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            sb = ttk.Spinbox(win, from_=1, to=100, width=5)
            sb.grid(row=row, column=1, padx=10, pady=5)
            sb.delete(0, tk.END)
            sb.insert(0, str(value))
            spinboxes.append(sb)

        def save_settings():
            try:
                self.font_size_title   = int(spinboxes[0].get())
                self.font_size_version = int(spinboxes[1].get())
                self.font_size_header  = int(spinboxes[2].get())
                self.font_size_page    = int(spinboxes[3].get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")
                return
            self._save_config()
            win.destroy()

        ttk.Button(win, text="Save", command=save_settings).grid(
            row=len(fields), column=0, columnspan=2, pady=10)

    # --- Core logic ---

    def _get_pages(self):
        pages = []
        for i in range(self.pages_listbox.size()):
            entry = self.pages_listbox.get(i)
            try:
                name, number = entry.rsplit(" # ", 1)
                pages.append({"name": name, "number": number})
            except ValueError:
                continue
        return pages

    def generate_index(self):
        project_name = self.project_name_entry.get()
        version      = self.version_entry.get()

        try:
            spacing = int(self.spacing_entry.get())
        except ValueError:
            messagebox.showerror("Error", "The column spacing must be an integer.")
            return

        col_left   = 150
        col_right  = col_left + spacing
        line_right = col_right + 30

        language   = "Content" if self.language_var.get() else "Contenido"
        sheet_text = "Sheet"   if self.language_var.get() else "Hoja"

        fs_t = self.font_size_title
        fs_v = self.font_size_version
        fs_h = self.font_size_header
        fs_p = self.font_size_page

        index_text = (
            f'\n(text "{project_name}"\n'
            f' (at {col_left} 20 0)\n'
            f' (effects (font (size {fs_t} {fs_t}) (bold yes)) (justify left)))\n'
            f'\n(text "v{version}"\n'
            f' (at {col_right} 20 0)\n'
            f' (effects (font (size {fs_v} {fs_v}) (bold yes)) (justify left)))\n'
            f'\n(polyline (pts (xy {col_left} 30) (xy {line_right} 30)) (stroke (width 0.5) (type solid)))\n'
            f'\n(text "{language}"\n'
            f' (at {col_left} 40 0)\n'
            f' (effects (font (size {fs_h} {fs_h}) (bold yes)) (justify left)))\n'
            f'\n(text "{sheet_text}"\n'
            f' (at {col_right} 40 0)\n'
            f' (effects (font (size {fs_h} {fs_h}) (bold yes)) (justify left)))\n'
            f'\n(polyline (pts (xy {col_left} 45) (xy {line_right} 45)) (stroke (width 0.5) (type solid)))\n'
        )

        y_offset = 55
        for page in self._get_pages():
            n, num = page["name"], page["number"]
            index_text += (
                f'\n(text "{n}"\n'
                f' (at {col_left} {y_offset} 0)\n'
                f' (effects (font (size {fs_p} {fs_p})) (justify left) (href "#{num}")))\n'
                f'\n(text "# {num}"\n'
                f' (at {col_right} {y_offset} 0)\n'
                f' (effects (font (size {fs_p} {fs_p})) (justify left) (href "#{num}")))\n'
            )
            y_offset += 8

        config_data = {
            "project_name": project_name,
            "version": version,
            "spacing": spacing,
            "language": "en" if self.language_var.get() else "es",
            "pages": self._get_pages(),
        }
        final_text = f";;CONFIG:{json.dumps(config_data)}\n{index_text}"

        if self.new_file_var.get():
            file_path = filedialog.asksaveasfilename(
                initialdir=os.path.dirname(os.path.abspath(__file__)),
                title="Save index",
                defaultextension=".sch",
                filetypes=[("KiCad Files", "*.sch"), ("All files", "*.*")]
            )
            if not file_path:
                messagebox.showinfo("Information", "Save canceled.")
                return
        else:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index_gen.sch")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_text)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save the file:\n{e}")
            return

        pyperclip.copy(index_text)
        messagebox.showinfo("Success", f"Index copied to clipboard and saved in:\n{file_path}")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title="Load index file",
            defaultextension=".sch",
            filetypes=[("KiCad Files", "*.sch"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open the file:\n{e}")
            return

        config_data = None
        for line in lines:
            if line.startswith(";;CONFIG:"):
                try:
                    config_data = json.loads(line[len(";;CONFIG:"):].strip())
                    break
                except json.JSONDecodeError:
                    continue

        if not config_data:
            messagebox.showerror("Error", "The file does not contain valid configuration information.")
            return

        self.project_name_entry.delete(0, tk.END)
        self.project_name_entry.insert(0, config_data.get("project_name", ""))
        self.version_entry.delete(0, tk.END)
        self.version_entry.insert(0, config_data.get("version", ""))
        self.spacing_entry.delete(0, tk.END)
        self.spacing_entry.insert(0, str(config_data.get("spacing", "150")))
        self.language_var.set(config_data.get("language", "es") == "en")

        self.pages_listbox.delete(0, tk.END)
        for page in config_data.get("pages", []):
            self.pages_listbox.insert(tk.END, f"{page.get('name', '')} # {page.get('number', '')}")

        messagebox.showinfo("Success", "File loaded successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = IndexGeneratorApp(root)
    root.mainloop()
