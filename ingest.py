import re
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from dotenv import load_dotenv
import uuid
import os

# Cargar variables de entorno (.env)
load_dotenv()

# --- CONFIGURACIÓN ---
INPUT_FOLDER = './doc/doc_scangestor'  # Carpeta raíz donde buscar los .md
DB_PATH = './bbdd'    # Dónde guardar la BBDD Chroma
COLLECTION_NAME = "documentacion_openai"
MODEL_NAME = "text-embedding-3-small"

# Verificar API KEY
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("❌ No se encontró la variable OPENAI_API_KEY. Configura tu archivo .env")

def get_chroma_collection():
    """Configura el cliente y la función de embedding de OpenAI."""
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Usamos la función nativa de Chroma para OpenAI
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=MODEL_NAME
    )
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=openai_ef
    )
    return collection

def split_text_by_markdown_paragraphs(text, max_chunk_size=2000, min_chunk_size=100):
    """
    Divide el texto en chunks por párrafos de Markdown.
    Los párrafos se separan por líneas en blanco (doble salto de línea).
    Agrupa párrafos pequeños y divide párrafos muy grandes.
    """
    # Dividir por párrafos (doble salto de línea)
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        para_size = len(paragraph)
        
        # Si el párrafo es muy grande, dividirlo
        if para_size > max_chunk_size:
            # Guardar el chunk actual si existe
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            # Dividir el párrafo grande por oraciones
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            temp_chunk = []
            temp_size = 0
            
            for sentence in sentences:
                if temp_size + len(sentence) > max_chunk_size and temp_chunk:
                    chunks.append(' '.join(temp_chunk))
                    temp_chunk = [sentence]
                    temp_size = len(sentence)
                else:
                    temp_chunk.append(sentence)
                    temp_size += len(sentence)
            
            if temp_chunk:
                chunks.append(' '.join(temp_chunk))
        
        # Si agregar este párrafo excede el tamaño máximo, guardar el chunk actual
        elif current_size + para_size > max_chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_size = para_size
        
        # Agregar el párrafo al chunk actual
        else:
            current_chunk.append(paragraph)
            current_size += para_size
    
    # Guardar el último chunk si existe
    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk)
        if len(chunk_text) >= min_chunk_size:
            chunks.append(chunk_text)
        elif chunks:
            # Si es muy pequeño, agregarlo al último chunk
            chunks[-1] += '\n\n' + chunk_text
        else:
            # Si es el único chunk, guardarlo aunque sea pequeño
            chunks.append(chunk_text)
    
    return chunks if chunks else [text]

def file_exists_in_db(collection, source_file_path):
    """
    Consulta si ya existen vectores asociados a este fichero.
    Devuelve True si encuentra al menos uno.
    """
    # Buscamos en metadatos usando el filtro 'where'
    results = collection.get(
        where={"source_file": source_file_path},
        limit=1
    )
    # Si la lista de IDs devuelta no está vacía, es que existe
    return len(results['ids']) > 0

def delete_file_from_db(collection, source_file_path):
    """
    Elimina todos los vectores asociados a un fichero específico.
    """
    # Buscar todos los IDs asociados al archivo
    results = collection.get(
        where={"source_file": source_file_path}
    )
    
    if results['ids']:
        collection.delete(ids=results['ids'])
        print(f"   🗑️  Eliminados {len(results['ids'])} vectores anteriores")
        return len(results['ids'])
    return 0

def process_directory(root_folder, collection):
    root_path = Path(root_folder)
    
    if not root_path.exists():
        print(f"⚠️ La carpeta {root_folder} no existe.")
        return

    print(f"🔍 Escaneando '{root_folder}' recursivamente...\n")

    # rglob('*') busca recursivamente cualquier archivo
    files = list(root_path.rglob('*.md'))
    
    if not files:
        print("⚠️ No se encontraron archivos .md")
        return

    processed_count = 0
    skipped_count = 0

    for file_path in files:
        # Verificar que el archivo sea .md (seguridad adicional)
        if file_path.suffix.lower() != '.md':
            print(f"🚫 Ignorando: {file_path.name} (no es archivo .md)")
            skipped_count += 1
            continue
        
        # Excluir archivos en carpetas que terminan con "__exclude"
        if any(part.endswith("__exclude") for part in file_path.parts):
            print(f"🚫 Excluyendo: {file_path.name} (carpeta con '__exclude')")
            skipped_count += 1
            continue
        
        # Manejar archivos con sufijo __ACT.md (actualización)
        is_update = file_path.stem.endswith("__ACT")
        if is_update:
            # Calcular la ruta sin __ACT
            original_stem = file_path.stem[:-5]  # Quitar "__ACT"
            original_path = file_path.parent / (original_stem + ".md")
            str_path = original_path.as_posix()
            
            # Comprobar si existe la versión anterior en la BBDD
            if file_exists_in_db(collection, str_path):
                print(f"🔄 Actualizando: {file_path.name} -> {original_path.name}")
                delete_file_from_db(collection, str_path)
            else:
                print(f"➕ Nuevo archivo (con __ACT): {file_path.name} -> {original_path.name}")
            
            # Renombrar el archivo físico
            try:
                file_path.rename(original_path)
                print(f"   📝 Archivo renombrado físicamente: {original_path.name}")
                file_path = original_path  # Actualizar la referencia para el procesamiento
            except Exception as e:
                print(f"   ⚠️ No se pudo renombrar el archivo físicamente: {e}")
                str_path = file_path.as_posix()  # Usar la ruta original si falla el renombrado
        else:
            # Definir ruta estándar
            str_path = file_path.as_posix()
            
            # Comprobar existencia (Idempotencia)
            if file_exists_in_db(collection, str_path):
                print(f"⏭️  Saltando (ya existe): {file_path.name}")
                skipped_count += 1
                continue
        
        # Mostrar que se está procesando el archivo
        print(f"⚡ Procesando: {file_path.name}")
        
        # category: nombre de la carpeta padre inmediata
        category_name = file_path.parent.name

        try:
            # Leer contenido
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                print("   ⚠️ Archivo vacío, omitiendo.")
                skipped_count += 1
                continue

            # Trocear texto (Chunking) por párrafos de Markdown
            chunks = split_text_by_markdown_paragraphs(content)
            
            # Preparar datos para Chroma
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{
                "source_file": str_path,
                "category": category_name,
                "chunk_index": i
            } for i in range(len(chunks))]

            # Insertar (Aquí es donde Chroma llama a OpenAI automáticamente)
            collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            processed_count += 1
            print(f"   ✅ Guardados {len(chunks)} vectores.")

        except Exception as e:
            print(f"   ❌ Error procesando {file_path.name}: {e}")
            skipped_count += 1

    print("\n" + "="*40)
    print(f"📊 RESUMEN:")
    print(f"   - Procesados y vectorizados: {processed_count}")
    print(f"   - Omitidos (existen o fueron excluidos): {skipped_count}")
    print("="*40)

if __name__ == "__main__":
    collection = get_chroma_collection()
    process_directory(INPUT_FOLDER, collection)