import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import pyperclip
import os
import json

class IndexGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Índice para SCH")

        tk.Label(root, text="Nombre del Proyecto:").pack(pady=5)
        self.project_name_entry = tk.Entry(root, width=40)
        self.project_name_entry.pack(pady=5)

        tk.Label(root, text="Versión:").pack(pady=5)
        self.version_entry = tk.Entry(root, width=40)
        self.version_entry.pack(pady=5)

        tk.Label(root, text="Distancia entre columnas:").pack(pady=5)
        self.spacing_entry = tk.Entry(root, width=10)
        self.spacing_entry.pack(pady=5)
        self.spacing_entry.insert(0, "150")  # Valor base

        self.language_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Idioma en Inglés", variable=self.language_var).pack(pady=5)

        # Nuevo checkbox para decidir si se guarda en un archivo nuevo
        self.new_file_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Guardar en archivo nuevo (no sobrescribir)", variable=self.new_file_var).pack(pady=5)

        self.pages_listbox = tk.Listbox(root, width=50, height=10)
        self.pages_listbox.pack(pady=5)
        # Se activa la edición al hacer doble click en un ítem
        self.pages_listbox.bind("<Double-Button-1>", self.modify_page)

        tk.Button(root, text="Añadir Página", command=self.add_page).pack(pady=5)
        tk.Button(root, text="Generar Índice", command=self.generate_index).pack(pady=5)
        tk.Button(root, text="Cargar Archivo", command=self.load_file).pack(pady=5)

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

    def generate_index(self):
        project_name = self.project_name_entry.get()
        version = self.version_entry.get()
        try:
            spacing = int(self.spacing_entry.get())
        except ValueError:
            messagebox.showerror("Error", "La distancia entre columnas debe ser un número entero.")
            return

        # Definir posiciones en el dibujo
        col_left = 150
        col_right = col_left + spacing
        line_right = col_right + 30  # margen para la línea
        name_box_width = spacing - 30
        if name_box_width < 30:
            name_box_width = int(spacing * 0.7)

        language = "Content" if self.language_var.get() else "Contenido"
        sheet_text = "Sheet" if self.language_var.get() else "Hoja"

        # Construcción del texto KiCad
        index_text = f"""
(text "{project_name}"
 (at {col_left} 20 0)
 (effects (font (size 10 10) (bold yes)) (justify left)))
"""
        index_text += f"""
(text "v{version}"
 (at {col_right} 20 0)
 (effects (font (size 10 10) (bold yes)) (justify left)))
"""
        index_text += f"(polyline (pts (xy {col_left} 30) (xy {line_right} 30)) (stroke (width 0.5) (type solid)))\n"
        index_text += f"""
(text "{language}"
 (at {col_left} 40 0)
 (effects (font (size 5 5) (bold yes)) (justify left)))
"""
        index_text += f"""
(text "{sheet_text}"
 (at {col_right} 40 0)
 (effects (font (size 5 5) (bold yes)) (justify left)))
"""
        index_text += f"(polyline (pts (xy {col_left} 45) (xy {line_right} 45)) (stroke (width 0.5) (type solid)))\n"

        y_offset = 55
        for i in range(self.pages_listbox.size()):
            entry = self.pages_listbox.get(i)
            try:
                page_name, page_number = entry.rsplit(" # ", 1)
            except ValueError:
                continue
            index_text += f"""
(text_box "{page_name}"
  (exclude_from_sim no) (at {col_left} {y_offset} 0) (size {name_box_width} 6.35)
  (stroke (width -0.0001) (type solid))
  (fill (type none))
  (effects (font (size 4 4)) (justify left) (href "#{page_number}")))
"""
            index_text += f"""
(text_box "# {page_number}"
  (exclude_from_sim no) (at {col_right} {y_offset} 0) (size 20 6.35)
  (stroke (width -0.0001) (type solid))
  (fill (type none))
  (effects (font (size 4 4)) (justify left) (href "#{page_number}")))
"""
            y_offset += 8

        # Guardamos también la configuración original para poder recargarla
        config = {
            "project_name": project_name,
            "version": version,
            "spacing": spacing,
            "language": "en" if self.language_var.get() else "es",
            "pages": []
        }
        for i in range(self.pages_listbox.size()):
            entry = self.pages_listbox.get(i)
            try:
                page_name, page_number = entry.rsplit(" # ", 1)
                config["pages"].append({"name": page_name, "number": page_number})
            except ValueError:
                continue

        # La primera línea del archivo será un comentario con la configuración en JSON
        config_comment = f";;CONFIG:{json.dumps(config)}\n"
        final_text = config_comment + index_text

        # Guardar el archivo:
        if self.new_file_var.get():
            # Si se seleccionó "guardar en archivo nuevo", preguntamos al usuario
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
            # Si no, se guarda en un archivo fijo (se sobrescribe)
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "indice_generado.sch")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_text)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
            return

        # Se copia al portapapeles solo el índice sin la línea de configuración
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

        # Actualizar los campos de la interfaz con la configuración cargada
        self.project_name_entry.delete(0, tk.END)
        self.project_name_entry.insert(0, config_data.get("project_name", ""))
        self.version_entry.delete(0, tk.END)
        self.version_entry.insert(0, config_data.get("version", ""))
        self.spacing_entry.delete(0, tk.END)
        self.spacing_entry.insert(0, str(config_data.get("spacing", "150")))
        lang = config_data.get("language", "es")
        self.language_var.set(True if lang == "en" else False)

        # Actualizar la lista de páginas
        self.pages_listbox.delete(0, tk.END)
        for page in config_data.get("pages", []):
            self.pages_listbox.insert(tk.END, f"{page.get('name', '')} # {page.get('number', '')}")

        messagebox.showinfo("Éxito", "Archivo cargado exitosamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = IndexGeneratorApp(root)
    root.mainloop()
