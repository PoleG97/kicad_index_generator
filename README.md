>![WARNING]
README work in progress

# Generador de Índice para KiCad

Este proyecto es una herramienta en Python que permite generar de forma automatizada un índice (o tabla de contenido) para esquemáticos de KiCad. Incluye opciones para personalizar tamaños de fuente, idioma, distancias entre columnas y más, de manera que puedas ajustar el índice a tus necesidades.

## ¿Para qué sirve?

- Facilita la creación de un índice de páginas dentro de un proyecto de KiCad.
- Permite añadir y editar páginas desde una interfaz gráfica (Tkinter).
- Genera el texto en el formato correcto para KiCad (versión 7 o superior).
- Ofrece la posibilidad de copiar el resultado al portapapeles para pegarlo directamente en KiCad.
- Permite guardar la configuración y el índice en un archivo `.sch`, así como recargarlo en cualquier momento.

## Características

- **Interfaz gráfica sencilla**: Añade, edita o elimina páginas mediante cuadros de diálogo.
- **Ajuste de fuentes**: Cambia el tamaño del texto para el título, la versión, los encabezados y el contenido de las páginas.
- **Guardado en archivo**:  
  - Puedes sobrescribir siempre el mismo archivo `indice_generado.sch` (por defecto).  
  - O bien seleccionar un archivo nuevo cada vez que generes el índice.
- **Carga de índice**: Si ya tenías un índice generado, puedes cargarlo y seguir editándolo.
- **Archivo de configuración `config.ini`**: Todos los valores por defecto (tamaños de fuente, idioma, etc.) están centralizados en un archivo `config.ini`, lo que facilita su modificación sin tocar el código.

## Requisitos

- **Python 3.7+** (o versión posterior).
- **Librerías estándar**: `tkinter`, `configparser`, `json`, `os`, `sys` (vienen incluidas con Python).
- **Pyperclip**: Para copiar el texto al portapapeles. Puedes instalarlo con:
  ```bash
  pip install pyperclip
  ```

## Instalación y uso

1. **Clona o descarga este repositorio** en tu máquina local.
2. Asegúrate de tener instalado Python 3 y la librería `pyperclip`.
3. Si no existe un archivo `config.ini`, el script creará uno automáticamente con valores por defecto al ejecutarse.

Para **ejecutar** la aplicación:

```bash
python index_generator.py
```

*(Asumiendo que el archivo principal se llama `index_generator.py`.)*

### Pasos en la aplicación

1. **Nombre del Proyecto**: Rellena el campo con el nombre que quieras mostrar en el índice.  
2. **Versión**: Indica la versión (por ejemplo, `v2.3`).  
3. **Distancia entre columnas**: Ajusta la separación horizontal entre la columna de contenido y la de número de página (por defecto 150).  
4. **Idioma en Inglés**: Marca esta casilla si quieres que los encabezados aparezcan como `Content` y `Sheet` en vez de `Contenido` y `Hoja`.  
5. **Guardar en archivo nuevo (no sobrescribir)**: Si se marca, al generar el índice te preguntará dónde guardarlo. De lo contrario, usará (y sobrescribirá) el archivo `indice_generado.sch`.  
6. **Añadir Página**: Abre un cuadro de diálogo para añadir una nueva entrada (nombre de página y número de hoja).  
7. **Generar Índice**: Crea el índice con las entradas listadas, lo guarda en el archivo elegido y copia el texto al portapapeles.  
8. **Cargar Archivo**: Permite abrir un `.sch` previamente generado y recuperar sus páginas para editarlas de nuevo.  
9. **Ajustar Tamaño de Textos**: Abre una ventana donde puedes cambiar el tamaño de la fuente para el título, versión, encabezados y páginas.

## Archivo de configuración `config.ini`

El archivo `config.ini` contiene los valores por defecto para la aplicación. Por ejemplo:

```ini
[DEFAULTS]
font_size_title = 10
font_size_version = 10
font_size_header = 5
font_size_page = 4
default_spacing = 150
default_language = es
save_in_new_file = false
```

- `font_size_title` / `font_size_version` / `font_size_header` / `font_size_page`: Tamaños de fuente por defecto.  
- `default_spacing`: Distancia entre columnas por defecto.  
- `default_language`: `es` para español o `en` para inglés.  
- `save_in_new_file`: `true` para que, por defecto, se guarde siempre en un archivo nuevo; `false` para sobrescribir.

Puedes editar estos valores sin necesidad de modificar el código Python. La próxima vez que ejecutes la aplicación, tomará en cuenta los cambios del `config.ini`.

## Contribución

Si deseas contribuir a este proyecto, puedes:

- **Crear un fork** de este repositorio y enviar tus mejoras mediante pull requests.
- **Reportar problemas** o sugerir nuevas funcionalidades en la sección de [Issues](../../issues).

¡Toda ayuda es bienvenida! 
