import os
import re
import mammoth
from markdownify import markdownify as md
from pathlib import Path
import pymupdf4llm
import pandas as pd

# --- CONFIGURACIÓN ---
INPUT_FOLDER = './01_entrada'
OUTPUT_FOLDER = './02_salida'

def setup_folders():
    """Crea las carpetas si no existen."""
    Path(INPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

def clean_markdown_content(text):
    """
    Aquí es donde aplicas tu lógica de limpieza y análisis.
    Recibe el string Markdown crudo y devuelve el limpio.
    """
    
    # 1. Eliminar índices automáticos (tabla de contenidos)
    # Detecta patrones típicos de índices como líneas con números de página
    # Patrón: busca secciones con múltiples líneas que terminan en números (páginas)
    text = re.sub(r'(?:^.*?\.{3,}.*?\d+\s*$\n?)+', '', text, flags=re.M)
    # Eliminar también patrones tipo "1.1 Título .......... 5"
    text = re.sub(r'^[\d.]+\s+[^\n]+\.{2,}\s*\d+\s*$', '', text, flags=re.M)
    # Eliminar títulos comunes de índices
    text = re.sub(r'^(Índice|Table of Contents|Tabla de contenidos|ÍNDICE|Contents)[\s\n]*', '', text, flags=re.M | re.I)
    
    # 2. Eliminar múltiples saltos de línea (más de 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 3. Eliminar espacios al final de las líneas
    text = re.sub(r'[ \t]+$', '', text, flags=re.M)
    
    # 4. Ejemplo: Eliminar marcas de agua o textos comunes (Personalizable)
    text = text.replace("CONFIDENCIAL", "")
    
    # 5. Corregir posibles errores de conversión en listas
    # (A veces queda pegado el guion)
    text = re.sub(r'\n-([^\s])', r'\n- \1', text)

    return text.strip()

def convert_docx_to_md(docx_path):
    """Convierte un fichero individual."""
    print(f"🔄 Procesando: {docx_path.name}...")
    
    try:
        # Paso 1: Usar Mammoth para leer docx -> HTML
        # style_map define cómo mapear estilos de Word a etiquetas HTML
        style_map = """
        p[style-name='Heading 1'] => h1:fresh
        p[style-name='Heading 2'] => h2:fresh
        p[style-name='Heading 3'] => h3:fresh
        p[style-name='Heading 4'] => h4:fresh
        p[style-name='Heading 5'] => h5:fresh
        p[style-name='Heading 6'] => h6:fresh
        p[style-name='Título 1'] => h1:fresh
        p[style-name='Título 2'] => h2:fresh
        p[style-name='Título 3'] => h3:fresh
        p[style-name='Título 4'] => h4:fresh
        p[style-name='Título 5'] => h5:fresh
        p[style-name='Título 6'] => h6:fresh
        """
        
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file, style_map=style_map)
            html = result.value
            messages = result.messages # Avisos de conversión (opcional)

        # Paso 2: Convertir HTML -> Markdown
        # heading_style="ATX" asegura que use # en lugar de subrayados
        # strip=['img'] elimina las imágenes del resultado
        markdown_text = md(html, heading_style="ATX", strip=['img'])
        
        # Paso 3: Limpieza personalizada
        final_text = clean_markdown_content(markdown_text)
        
        return final_text

    except Exception as e:
        print(f"❌ Error al convertir {docx_path.name}: {e}")
        return None

def convert_pdf_to_md(pdf_path):
    """Convierte un fichero PDF a Markdown."""
    print(f"🔄 Procesando: {pdf_path.name}...")
    
    try:
        # Usar pymupdf4llm para convertir PDF directamente a Markdown
        markdown_text = pymupdf4llm.to_markdown(str(pdf_path))
        
        # Limpieza personalizada
        final_text = clean_markdown_content(markdown_text)
        
        return final_text

    except Exception as e:
        print(f"❌ Error al convertir {pdf_path.name}: {e}")
        return None

def convert_excel_to_md(excel_path):
    """Convierte un fichero Excel a Markdown."""
    print(f"🔄 Procesando: {excel_path.name}...")
    
    try:
        # Leer todas las hojas del archivo Excel
        excel_file = pd.ExcelFile(excel_path)
        markdown_parts = []
        
        for sheet_name in excel_file.sheet_names:
            # Leer cada hoja
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # Si la hoja no está vacía
            if not df.empty:
                # Añadir título de la hoja
                markdown_parts.append(f"## {sheet_name}\n")
                # Convertir DataFrame a tabla Markdown
                markdown_parts.append(df.to_markdown(index=False))
                markdown_parts.append("\n")
        
        markdown_text = "\n".join(markdown_parts)
        
        # Limpieza personalizada
        final_text = clean_markdown_content(markdown_text)
        
        return final_text

    except Exception as e:
        print(f"❌ Error al convertir {excel_path.name}: {e}")
        return None

def main():
    setup_folders()
    
    input_path = Path(INPUT_FOLDER)
    docx_files = list(input_path.glob('*.docx'))
    pdf_files = list(input_path.glob('*.pdf'))
    xls_files = list(input_path.glob('*.xls'))
    xlsx_files = list(input_path.glob('*.xlsx'))
    excel_files = xls_files + xlsx_files
    
    total_files = len(docx_files) + len(pdf_files) + len(excel_files)
    
    if total_files == 0:
        print(f"⚠️ No se encontraron archivos .docx, .pdf, .xls o .xlsx en '{INPUT_FOLDER}'")
        return

    print(f"📂 Encontrados {len(docx_files)} Word, {len(pdf_files)} PDFs y {len(excel_files)} Excel. Iniciando conversión...\n")

    # Procesar archivos DOCX
    for file_path in docx_files:
        # Generar contenido
        md_content = convert_docx_to_md(file_path)
        
        if md_content:
            # Definir nombre de salida
            output_filename = file_path.stem + ".md"
            output_path = Path(OUTPUT_FOLDER) / output_filename
            
            # Guardar fichero
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            print(f"✅ Guardado: {output_filename}")
    
    # Procesar archivos PDF
    for file_path in pdf_files:
        # Generar contenido
        md_content = convert_pdf_to_md(file_path)
        
        if md_content:
            # Definir nombre de salida
            output_filename = file_path.stem + ".md"
            output_path = Path(OUTPUT_FOLDER) / output_filename
            
            # Guardar fichero
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            print(f"✅ Guardado: {output_filename}")
    
    # Procesar archivos Excel
    for file_path in excel_files:
        # Generar contenido
        md_content = convert_excel_to_md(file_path)
        
        if md_content:
            # Definir nombre de salida
            output_filename = file_path.stem + ".md"
            output_path = Path(OUTPUT_FOLDER) / output_filename
            
            # Guardar fichero
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            print(f"✅ Guardado: {output_filename}")

    print("\n🚀 Proceso finalizado.")

if __name__ == "__main__":
    main()