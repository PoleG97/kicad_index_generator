import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import pyperclip
import os
import json
import configparser  # <-- para leer el config.ini

class IndexGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Índice para SCH")

        # ==============================
        # 1. Cargar archivo config.ini
        # ==============================
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

        # Si no existe, lo creamos con valores por defecto
        if not os.path.exists(self.config_path):
            self.create_default_config()

        # Leemos el archivo de configuración
        self.config.read(self.config_path)

        # Extraemos valores (con fallback por si faltara alguno)
        self.font_size_title   = self.config.getint('DEFAULTS', 'font_size_title',   fallback=10)
        self.font_size_version = self.config.getint('DEFAULTS', 'font_size_version', fallback=10)
        self.font_size_header  = self.config.getint('DEFAULTS', 'font_size_header',  fallback=5)
        self.font_size_page    = self.config.getint('DEFAULTS', 'font_size_page',    fallback=4)
        default_spacing        = self.config.get('DEFAULTS', 'default_spacing',      fallback="150")
        default_lang           = self.config.get('DEFAULTS', 'default_language',     fallback="es")
        save_new_file_str      = self.config.get('DEFAULTS', 'save_in_new_file',     fallback="false").lower()

        # ==============================
        # 2. Crear elementos de la GUI
        # ==============================
        tk.Label(root, text="Nombre del Proyecto:").pack(pady=5)
        self.project_name_entry = tk.Entry(root, width=40)
        self.project_name_entry.pack(pady=5)

        tk.Label(root, text="Versión:").pack(pady=5)
        self.version_entry = tk.Entry(root, width=40)
        self.version_entry.pack(pady=5)

        tk.Label(root, text="Distancia entre columnas:").pack(pady=5)
        self.spacing_entry = tk.Entry(root, width=10)
        self.spacing_entry.pack(pady=5)
        # Insertamos el valor de 'default_spacing' leído del config
        self.spacing_entry.insert(0, default_spacing)

        self.language_var = tk.BooleanVar()
        # Si default_lang es "en", ponemos True, si no, False
        self.language_var.set(True if default_lang.lower() == "en" else False)
        tk.Checkbutton(root, text="Idioma en Inglés", variable=self.language_var).pack(pady=5)

        # Checkbox para decidir si se guarda en un archivo nuevo
        self.new_file_var = tk.BooleanVar()
        self.new_file_var.set(True if save_new_file_str == "true" else False)
        tk.Checkbutton(root, text="Guardar en archivo nuevo (no sobrescribir)", variable=self.new_file_var).pack(pady=5)

        self.pages_listbox = tk.Listbox(root, width=50, height=10)
        self.pages_listbox.pack(pady=5)
        self.pages_listbox.bind("<Double-Button-1>", self.modify_page)

        tk.Button(root, text="Añadir Página", command=self.add_page).pack(pady=5)
        tk.Button(root, text="Generar Índice", command=self.generate_index).pack(pady=5)
        tk.Button(root, text="Cargar Archivo", command=self.load_file).pack(pady=5)
        tk.Button(root, text="Ajustar Tamaño de Textos", command=self.open_font_settings).pack(pady=5)

    def create_default_config(self):
        """
        Crea un config.ini por defecto si no existe.
        """
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

    def add_page(self):
        page_name = simpledialog.askstring("Añadir Página", "Ingrese el nombre de la página:")
        if page_name:
            page_number = simpledialog.askstring("Número de Página", "Ingrese el número de la página:")
            if page_number:
                self.pages_listbox.insert(tk.END, f"{page_name} # {page_number}")

    def modify_page(self, event):
        try:
            index = self.pages_listbox.curselection()[0]
        except IndexError:
            index = self.pages_listbox.nearest(event.y)
        item = self.pages_listbox.get(index)
        try:
            page_name, page_number = item.rsplit(" # ", 1)
        except ValueError:
            return

        new_page_name = simpledialog.askstring("Modificar Página", "Ingrese el nuevo nombre de la página:", initialvalue=page_name)
        if new_page_name is not None:
            new_page_number = simpledialog.askstring("Modificar Número de Página", "Ingrese el nuevo número de la página:", initialvalue=page_number)
            if new_page_number is not None:
                new_entry = f"{new_page_name} # {new_page_number}"
                self.pages_listbox.delete(index)
                self.pages_listbox.insert(index, new_entry)

    def open_font_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Ajustar Tamaño de Textos")

        tk.Label(settings_window, text="Tamaño del Título:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        title_spinbox = tk.Spinbox(settings_window, from_=1, to=100, width=5)
        title_spinbox.grid(row=0, column=1, padx=5, pady=5)
        title_spinbox.delete(0, tk.END)
        title_spinbox.insert(0, str(self.font_size_title))

        tk.Label(settings_window, text="Tamaño de la Versión:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        version_spinbox = tk.Spinbox(settings_window, from_=1, to=100, width=5)
        version_spinbox.grid(row=1, column=1, padx=5, pady=5)
        version_spinbox.delete(0, tk.END)
        version_spinbox.insert(0, str(self.font_size_version))

        tk.Label(settings_window, text="Tamaño de los Encabezados:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        header_spinbox = tk.Spinbox(settings_window, from_=1, to=100, width=5)
        header_spinbox.grid(row=2, column=1, padx=5, pady=5)
        header_spinbox.delete(0, tk.END)
        header_spinbox.insert(0, str(self.font_size_header))

        tk.Label(settings_window, text="Tamaño del Texto de Página:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        page_spinbox = tk.Spinbox(settings_window, from_=1, to=100, width=5)
        page_spinbox.grid(row=3, column=1, padx=5, pady=5)
        page_spinbox.delete(0, tk.END)
        page_spinbox.insert(0, str(self.font_size_page))

        def save_settings():
            try:
                self.font_size_title = int(title_spinbox.get())
                self.font_size_version = int(version_spinbox.get())
                self.font_size_header = int(header_spinbox.get())
                self.font_size_page = int(page_spinbox.get())
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa números válidos.")
                return
            settings_window.destroy()

        tk.Button(settings_window, text="Guardar", command=save_settings).grid(row=4, column=0, columnspan=2, pady=10)

    def generate_index(self):
        project_name = self.project_name_entry.get()
        version = self.version_entry.get()

        # Validamos el spacing
        try:
            spacing = int(self.spacing_entry.get())
        except ValueError:
            messagebox.showerror("Error", "La distancia entre columnas debe ser un número entero.")
            return

        # Posiciones
        col_left = 150
        col_right = col_left + spacing
        line_right = col_right + 30
        name_box_width = spacing - 30
        if name_box_width < 30:
            name_box_width = int(spacing * 0.7)

        language = "Content" if self.language_var.get() else "Contenido"
        sheet_text = "Sheet" if self.language_var.get() else "Hoja"

        # Construimos el texto
        index_text = f"""
(text "{project_name}"
 (at {col_left} 20 0)
 (effects (font (size {self.font_size_title} {self.font_size_title}) (bold yes)) (justify left)))
"""
        index_text += f"""
(text "v{version}"
 (at {col_right} 20 0)
 (effects (font (size {self.font_size_version} {self.font_size_version}) (bold yes)) (justify left)))
"""
        index_text += f"(polyline (pts (xy {col_left} 30) (xy {line_right} 30)) (stroke (width 0.5) (type solid)))\n"

        index_text += f"""
(text "{language}"
 (at {col_left} 40 0)
 (effects (font (size {self.font_size_header} {self.font_size_header}) (bold yes)) (justify left)))
"""
        index_text += f"""
(text "{sheet_text}"
 (at {col_right} 40 0)
 (effects (font (size {self.font_size_header} {self.font_size_header}) (bold yes)) (justify left)))
"""
        index_text += f"(polyline (pts (xy {col_left} 45) (xy {line_right} 45)) (stroke (width 0.5) (type solid)))\n"

        y_offset = 55
        for i in range(self.pages_listbox.size()):
            entry = self.pages_listbox.get(i)
            try:
                page_name, page_number = entry.rsplit(" # ", 1)
            except ValueError:
                continue

            # Nombre
            index_text += f"""
(text "{page_name}"
 (at {col_left} {y_offset} 0)
 (effects (font (size {self.font_size_page} {self.font_size_page})) (justify left) (href "#{page_number}")))
"""
            # Número
            index_text += f"""
(text "# {page_number}"
 (at {col_right} {y_offset} 0)
 (effects (font (size {self.font_size_page} {self.font_size_page})) (justify left) (href "#{page_number}")))
"""
            y_offset += 8

        # Creamos el bloque de configuración para poder recargar
        config_data = {
            "project_name": project_name,
            "version": version,
            "spacing": spacing,
            "language": "en" if self.language_var.get() else "es",
            "pages": []
        }
        for i in range(self.pages_listbox.size()):
            entry = self.pages_listbox.get(i)
            try:
                p_name, p_num = entry.rsplit(" # ", 1)
                config_data["pages"].append({"name": p_name, "number": p_num})
            except ValueError:
                continue

        config_comment = f";;CONFIG:{json.dumps(config_data)}\n"
        final_text = config_comment + index_text

        # Guardar
        if self.new_file_var.get():
            file_path = filedialog.asksaveasfilename(
                initialdir=os.path.dirname(os.path.abspath(__file__)),
                title="Guardar índice",
                defaultextension=".sch",
                filetypes=[("KiCad Files", "*.sch"), ("Todos los archivos", "*.*")]
            )
            if not file_path:
                messagebox.showinfo("Información", "Guardado cancelado.")
                return
        else:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "indice_generado.sch")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_text)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
            return

        # Copiar al portapapeles
        pyperclip.copy(index_text)
        messagebox.showinfo("Éxito", f"Índice copiado al portapapeles y guardado en:\n{file_path}")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title="Cargar archivo de índice",
            defaultextension=".sch",
            filetypes=[("KiCad Files", "*.sch"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
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
            messagebox.showerror("Error", "El archivo no contiene información de configuración válida.")
            return

        # Rellenar interfaz
        self.project_name_entry.delete(0, tk.END)
        self.project_name_entry.insert(0, config_data.get("project_name", ""))
        self.version_entry.delete(0, tk.END)
        self.version_entry.insert(0, config_data.get("version", ""))
        self.spacing_entry.delete(0, tk.END)
        self.spacing_entry.insert(0, str(config_data.get("spacing", "150")))
        lang = config_data.get("language", "es")
        self.language_var.set(True if lang == "en" else False)

        self.pages_listbox.delete(0, tk.END)
        for page in config_data.get("pages", []):
            self.pages_listbox.insert(tk.END, f"{page.get('name', '')} # {page.get('number', '')}")

        messagebox.showinfo("Éxito", "Archivo cargado exitosamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = IndexGeneratorApp(root)
    root.mainloop()
