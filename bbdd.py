import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from collections import defaultdict

# Cargar variables de entorno (.env)
load_dotenv()

# --- CONFIGURACIÓN ---
DB_PATH = './bbdd'    # Ruta a la BBDD Chroma
COLLECTION_NAME = "documentacion_openai"
MODEL_NAME = "text-embedding-3-small"

# Verificar API KEY
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("❌ No se encontró la variable OPENAI_API_KEY. Configura tu archivo .env")

def get_chroma_collection():
    """Configura el cliente y la colección de ChromaDB."""
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

def show_database_content():
    """Muestra el contenido de la base de datos vectorial."""
    print("\n" + "="*70)
    print("📚 CONTENIDO DE LA BASE DE DATOS VECTORIAL")
    print("="*70 + "\n")
    
    try:
        collection = get_chroma_collection()
        
        # Obtener todos los vectores de la colección
        results = collection.get()
        
        if not results['ids']:
            print("⚠️  La base de datos está vacía.\n")
            return
        
        total_vectors = len(results['ids'])
        print(f"🔢 Total de vectores: {total_vectors}\n")
        print("-"*70 + "\n")
        
        # Agrupar por archivo para mejor visualización usando defaultdict
        files_dict = defaultdict(lambda: {'category': 'N/A', 'vectors': []})
        categories = defaultdict(lambda: {'files': 0, 'vectors': 0})
        
        for vector_id, metadata in zip(results['ids'], results['metadatas']):
            source_file = metadata.get('source_file', 'N/A')
            category = metadata.get('category', 'N/A')
            chunk_index = metadata.get('chunk_index', 'N/A')
            
            # Agregar al diccionario de archivos
            if not files_dict[source_file]['vectors']:  # Primera vez que vemos este archivo
                files_dict[source_file]['category'] = category
            
            files_dict[source_file]['vectors'].append({
                'id': vector_id,
                'chunk_index': chunk_index
            })
        
        # Mostrar información detallada por archivo
        print("📋 LISTA DE VECTORES POR ARCHIVO:\n")
        
        for idx, (source_file, data) in enumerate(sorted(files_dict.items()), 1):
            num_vectors = len(data['vectors'])
            category = data['category']
            
            # Actualizar estadísticas de categoría
            categories[category]['files'] += 1
            categories[category]['vectors'] += num_vectors
            
            print(f"{idx}. 📄 Archivo: {source_file}")
            print(f"   📂 Categoría: {category}")
            print(f"   🔢 Número de vectores/chunks: {num_vectors}")
            
            # Mostrar los primeros vectores con sus IDs
            print(f"   🆔 Vector IDs:")
            for vec in data['vectors'][:5]:  # Mostrar los primeros 5
                print(f"      - {vec['id']} (chunk #{vec['chunk_index']})")
            
            if num_vectors > 5:
                print(f"      ... (+{num_vectors - 5} vectores más)")
            
            print()
        
        print("="*70)
        print(f"📊 RESUMEN:")
        print(f"   - Total de archivos únicos: {len(files_dict)}")
        print(f"   - Total de vectores/chunks: {total_vectors}")
        print(f"   - Promedio de chunks por archivo: {total_vectors / len(files_dict):.1f}")
        print("="*70 + "\n")
        
        print("📊 DISTRIBUCIÓN POR CATEGORÍA:")
        for cat, stats in sorted(categories.items()):
            print(f"   - {cat}: {stats['files']} archivos, {stats['vectors']} vectores")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error al consultar la base de datos: {e}\n")

if __name__ == "__main__":
    show_database_content()
