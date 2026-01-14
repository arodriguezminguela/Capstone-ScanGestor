"""Sistema RAG Multi-Agente con Búsqueda Híbrida (Semántica y Léxica)

Este módulo implementa un sistema de Retrieval-Augmented Generation (RAG) 
especializado para la aplicación ScanGasto. El sistema utiliza una arquitectura
multi-agente con capacidades de búsqueda híbrida:

- Búsqueda Semántica: Utiliza embeddings y ChromaDB para búsquedas conceptuales
- Búsqueda Léxica: Realiza búsquedas literales en archivos markdown

Componentes principales:
    - Agente Orquestador: Clasifica preguntas por categoría y tipo de búsqueda
    - Agentes Especializados: Funcional, Técnico y Gestión
    - Agente Sintetizador: Fusiona respuestas de múltiples agentes
    - Interfaz Gradio: UI web interactiva con opciones configurables

Autor: Equipo Capstone IIA
Versión: 2.0
Fecha: Diciembre 2025
"""

import os
import re
import glob
import gradio as gr
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Cargar variables de entorno
load_dotenv()

# Verificar API KEY
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("❌ No se encontró la variable OPENAI_API_KEY. Configura tu archivo .env")

# Configuración de ChromaDB
DB_PATH = './bbdd'
COLLECTION_NAME = "documentacion_openai"
MODEL_NAME = "text-embedding-3-small"

# Regex compilados para extraer información de clasificación
CATEGORIA_PATTERN = re.compile(r'Categoría:\s*(FUNCIONAL|TECNICA|GESTION)', re.IGNORECASE)
TIPO_BUSQUEDA_PATTERN = re.compile(r'Tipo de búsqueda:\s*(SEMANTICA|LEXICA)', re.IGNORECASE)

# Cliente LangChain global (reutilizable)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=API_KEY
)

# Cache de la colección ChromaDB
_collection_cache = None

def get_chroma_collection():
    """Obtiene la colección de ChromaDB con patrón Singleton.
    
    Implementa un patrón de caché para evitar reconexiones innecesarias
    a la base de datos vectorial ChromaDB. La colección se inicializa
    una sola vez y se reutiliza en llamadas posteriores.
    
    Returns:
        chromadb.Collection: Colección de ChromaDB configurada con
            función de embeddings de OpenAI (text-embedding-3-small)
    
    Note:
        Utiliza la variable global _collection_cache para persistencia
    """
    global _collection_cache
    
    if _collection_cache is None:
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=API_KEY,
            model_name=MODEL_NAME
        )
        _collection_cache = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=openai_ef
        )
    
    return _collection_cache

def agente_orquestador(pregunta):
    """Agente Orquestador: Clasifica preguntas en dos dimensiones.
    
    Este agente es el punto de entrada del sistema multi-agente. Utiliza
    GPT-4o-mini para realizar una doble clasificación de la pregunta del usuario:
    
    1. Categoría de dominio:
       - FUNCIONAL: Funcionalidades, características, comportamiento de usuario
       - TECNICA: Implementación, código, arquitectura, tecnologías
       - GESTION: Procesos, organización, documentación, planificación
    
    2. Tipo de búsqueda:
       - SEMANTICA: Búsquedas conceptuales que requieren comprensión contextual
       - LEXICA: Búsquedas literales de términos, campos o variables específicas
    
    Args:
        pregunta (str): Pregunta del usuario a clasificar
    
    Returns:
        str: Texto con la clasificación en formato estructurado:
             "Categoría: [CATEGORIA]\nTipo de búsqueda: [TIPO]\nJustificación: [TEXTO]"
             En caso de error, retorna mensaje de error con el detalle
    
    Example:
        >>> agente_orquestador("¿Cómo funciona el sistema de QR?")
        "Categoría: FUNCIONAL\nTipo de búsqueda: SEMANTICA\n..."
    """
    template = """Eres un agente clasificador experto. Tu tarea es analizar preguntas y hacer dos clasificaciones:

**CATEGORÍA (elige una):**
1. FUNCIONAL: Preguntas sobre cómo funciona algo, características, comportamiento de usuario, casos de uso, flujos de trabajo.
2. TECNICA: Preguntas sobre implementación, código, arquitectura, tecnologías, APIs, bases de datos, desarrollo.
3. GESTION: Preguntas sobre procesos, organización, documentación, planificación, administración, procedimientos.

**TIPO DE BÚSQUEDA (elige uno):**
- SEMANTICA: Preguntas conceptuales, de comprensión, que requieren entender el significado y contexto. Ejemplos: "¿cómo funciona X?", "¿qué hace Y?", "¿para qué sirve Z?"
- LEXICA: Búsquedas de términos específicos, nombres exactos de campos, variables, strings, o ubicaciones de código. Ejemplos: "¿dónde aparece el campo X?", "¿en qué archivo está la variable Y?", "busca el string Z"

Responde ÚNICAMENTE con el formato:
Categoría: [FUNCIONAL/TECNICA/GESTION]
Tipo de búsqueda: [SEMANTICA/LEXICA]
Justificación: [Breve explicación]

Pregunta: {pregunta}"""

    try:
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        response = chain.invoke({"pregunta": pregunta})
        return response.content
    except Exception as e:
        return f"❌ Error al clasificar la pregunta: {str(e)}"

def extraer_categoria(clasificacion_texto):
    """Extrae la categoría del texto de clasificación usando regex.
    
    Args:
        clasificacion_texto (str): Texto con formato "Categoría: [CATEGORIA]"
    
    Returns:
        str: Categoría extraída en mayúsculas (FUNCIONAL/TECNICA/GESTION)
             o "DESCONOCIDA" si no se encuentra patrón válido
    """
    match = CATEGORIA_PATTERN.search(clasificacion_texto)
    if match:
        return match.group(1).upper()
    return "DESCONOCIDA"

def extraer_tipo_busqueda(clasificacion_texto):
    """Extrae el tipo de búsqueda del texto de clasificación usando regex.
    
    Args:
        clasificacion_texto (str): Texto con formato "Tipo de búsqueda: [TIPO]"
    
    Returns:
        str: Tipo de búsqueda extraído (SEMANTICA/LEXICA)
             Por defecto retorna "SEMANTICA" si no se encuentra patrón
    """
    match = TIPO_BUSQUEDA_PATTERN.search(clasificacion_texto)
    if match:
        return match.group(1).upper()
    return "SEMANTICA"  # Por defecto, asumimos búsqueda semántica

def buscar_documentos_relevantes(pregunta, categoria, n_results=3):
    """Busca documentos relevantes en ChromaDB según la pregunta y categoría."""
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[pregunta],
        n_results=n_results,
        where={"category": categoria} if categoria != "DESCONOCIDA" else None
    )
    return results

def construir_contexto(documentos, metadatas):
    """Construye el contexto a partir de documentos y metadatos."""
    contexto_partes = [
        f"[Documento {i} - {meta.get('source_file', 'Desconocido')}]\n{doc}"
        for i, (doc, meta) in enumerate(zip(documentos, metadatas), 1)
    ]
    return "\n\n---\n\n".join(contexto_partes)

def formatear_respuesta_con_fuentes(contenido, metadatas, mostrar_fuentes=True):
    """Formatea la respuesta incluyendo opcionalmente las fuentes consultadas."""
    if not mostrar_fuentes:
        return contenido
    
    fuentes_unicas = list(dict.fromkeys(
        meta.get('source_file', 'Desconocido') for meta in metadatas
    ))
    fuentes_str = "\n".join(f"- {fuente}" for fuente in fuentes_unicas)
    return f"{contenido}\n\n📚 **Fuentes consultadas:**\n{fuentes_str}"

def busqueda_lexica_en_archivos(pregunta, carpeta_docs):
    """Realiza una búsqueda léxica (texto literal) en archivos markdown."""
    # Extraer posibles términos de búsqueda de la pregunta
    terminos = []
    
    # 1. Buscar texto entre comillas
    quoted = re.findall(r'["\'""]([^"\'\'"]+)["\'""]', pregunta)
    terminos.extend(quoted)
    
    # 2. Si no hay texto entre comillas, buscar palabras específicas/técnicas
    if not terminos:
        # Palabras comunes a excluir
        palabras_excluidas = {
            'el', 'la', 'los', 'las', 'un', 'una', 'de', 'en', 'y', 'o', 'que', 'se', 
            'donde', 'como', 'cual', 'este', 'esta', 'es', 'son', 'aparece', 
            'esta', 'hay', 'tiene', 'busca', 'encuentra', 'campo', 'variable',
            'string', 'funcion', 'metodo', 'archivo', 'documento', 'codigo', 
            'documentación', 'documentacion'
        }
        
        palabras = re.findall(r'\b\w+\b', pregunta.lower())
        candidatos = [p for p in palabras if len(p) > 3 and p not in palabras_excluidas]
        
        # Priorizar términos técnicos (con _, -, o camelCase)
        terminos_tecnicos = [c for c in candidatos if '_' in c or '-' in c]
        
        if terminos_tecnicos:
            # Si hay términos técnicos, usar solo el más largo (más específico)
            terminos = [max(terminos_tecnicos, key=len)]
        elif candidatos:
            # Si no hay términos técnicos, usar el más largo
            terminos = [max(candidatos, key=len)]
    
    if not terminos:
        return None, []
    
    # Buscar en archivos markdown
    patron_archivos = os.path.join(carpeta_docs, '*.md')
    archivos = glob.glob(patron_archivos)
    
    resultados = []
    for archivo in archivos:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                lineas = contenido.split('\n')
                
                # Buscar coincidencias
                for i, linea in enumerate(lineas, 1):
                    for termino in terminos:
                        if termino.lower() in linea.lower():
                            # Contexto: línea anterior y siguiente
                            contexto_inicio = max(0, i - 2)
                            contexto_fin = min(len(lineas), i + 1)
                            contexto = '\n'.join(lineas[contexto_inicio:contexto_fin])
                            
                            resultados.append({
                                'archivo': os.path.basename(archivo),
                                'linea': i,
                                'termino': termino,
                                'contexto': contexto
                            })
                            break  # Solo una coincidencia por línea
        except Exception as e:
            continue
    
    return terminos, resultados

def formatear_resultados_lexicos(terminos, resultados, mostrar_fuentes):
    """Formatea los resultados de una búsqueda léxica."""
    if not resultados:
        return f"⚠️ No se encontraron coincidencias para los términos buscados: {', '.join(terminos)}"
    
    # Agrupar por archivo
    por_archivo = {}
    for r in resultados:
        archivo = r['archivo']
        if archivo not in por_archivo:
            por_archivo[archivo] = []
        por_archivo[archivo].append(r)
    
    # Formatear respuesta
    respuesta = f"🔍 **Búsqueda léxica de:** {', '.join(terminos)}\n\n"
    respuesta += f"Se encontraron **{len(resultados)} coincidencias** en **{len(por_archivo)} archivos**:\n\n"
    
    for archivo, coincidencias in por_archivo.items():
        respuesta += f"### 📄 {archivo}\n"
        for c in coincidencias[:3]:  # Limitar a 3 coincidencias por archivo
            respuesta += f"\n**Línea {c['linea']}:**\n```\n{c['contexto']}\n```\n"
        
        if len(coincidencias) > 3:
            respuesta += f"\n_... y {len(coincidencias) - 3} coincidencias más en este archivo_\n"
        respuesta += "\n"
    
    if mostrar_fuentes:
        fuentes = list(por_archivo.keys())
        respuesta += f"\n📚 **Archivos consultados:**\n"
        respuesta += "\n".join(f"- {f}" for f in fuentes)
    
    return respuesta

def agente_funcional(pregunta, categoria, tipo_busqueda, mostrar_fuentes=True):
    """
    Agente funcional que busca documentos relevantes en la BBDD vectorial (semántica)
    o realiza búsqueda léxica en archivos markdown según el tipo de búsqueda.
    
    Args:
        pregunta: La pregunta del usuario
        categoria: Categoría de la pregunta (FUNCIONAL/TECNICA/GESTION)
        tipo_busqueda: Tipo de búsqueda (SEMANTICA/LEXICA)
        mostrar_fuentes: Si se deben mostrar las fuentes consultadas
    """
    try:
        # Manejo de búsqueda léxica
        if tipo_busqueda == "LEXICA":
            carpeta_funcional = './doc/doc_scangestor/FUNCIONAL'
            terminos, resultados = busqueda_lexica_en_archivos(pregunta, carpeta_funcional)
            
            if terminos is None:
                return "⚠️ No se pudieron extraer términos de búsqueda de tu pregunta. Inténtalo de nuevo especificando claramente el término que buscas."
            
            return formatear_resultados_lexicos(terminos, resultados, mostrar_fuentes)
        
        # Manejo de búsqueda semántica (comportamiento original)
        # 1. Buscar documentos relevantes
        results = buscar_documentos_relevantes(pregunta, categoria)
        
        # 2. Verificar si hay resultados
        if not results['documents'] or not results['documents'][0]:
            return "⚠️ No se encontraron documentos relevantes en la base de datos para responder tu pregunta."
        
        # 3. Construir contexto
        documentos = results['documents'][0]
        metadatas = results['metadatas'][0]
        contexto = construir_contexto(documentos, metadatas)
        
        # 4. Crear prompt especializado para preguntas funcionales
        template = """Eres un asistente experto en la aplicación ScanGasto. 
Utiliza el siguiente contexto de documentación para responder la pregunta del usuario de forma precisa y detallada.

Categoría de la pregunta: {categoria}
Tipo de búsqueda: {tipo_busqueda}

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA: Proporciona una respuesta clara, estructurada y basada únicamente en el contexto proporcionado. Si lo ves necesario incluye ejemplos prácticos o pasos a seguir.
Si el contexto no contiene información suficiente, indícalo claramente. Puedes proponer cambios en base a las preguntas realizadas para incorporar funcionalidades nuevas."""
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        
        response = chain.invoke({
            "categoria": categoria,
            "tipo_busqueda": tipo_busqueda,
            "contexto": contexto,
            "pregunta": pregunta
        })
        
        # 5. Formatear respuesta con fuentes
        return formatear_respuesta_con_fuentes(response.content, metadatas, mostrar_fuentes)
        
    except Exception as e:
        return f"❌ Error en el agente funcional: {str(e)}"

def agente_tecnico(pregunta, categoria, tipo_busqueda, mostrar_fuentes=True):
    """
    Agente técnico que busca documentos relevantes en la BBDD vectorial (semántica)
    o realiza búsqueda léxica en archivos markdown según el tipo de búsqueda.
    
    Args:
        pregunta: La pregunta del usuario
        categoria: Categoría de la pregunta (FUNCIONAL/TECNICA/GESTION)
        tipo_busqueda: Tipo de búsqueda (SEMANTICA/LEXICA)
        mostrar_fuentes: Si se deben mostrar las fuentes consultadas
    """
    try:
        # Manejo de búsqueda léxica
        if tipo_busqueda == "LEXICA":
            carpeta_tecnica = './doc/doc_scangestor/TECNICA'
            terminos, resultados = busqueda_lexica_en_archivos(pregunta, carpeta_tecnica)
            
            if terminos is None:
                return "⚠️ No se pudieron extraer términos de búsqueda de tu pregunta. Inténtalo de nuevo especificando claramente el término que buscas."
            
            return formatear_resultados_lexicos(terminos, resultados, mostrar_fuentes)
        
        # Manejo de búsqueda semántica (comportamiento original)
        # 1. Buscar documentos relevantes
        results = buscar_documentos_relevantes(pregunta, categoria)
        
        # 2. Verificar si hay resultados
        if not results['documents'] or not results['documents'][0]:
            return "⚠️ No se encontraron documentos relevantes en la base de datos para responder tu pregunta."
        
        # 3. Construir contexto
        documentos = results['documents'][0]
        metadatas = results['metadatas'][0]
        contexto = construir_contexto(documentos, metadatas)
        
        # 4. Crear prompt especializado para preguntas técnicas
        template = """Eres un asistente técnico experto en la aplicación ScanGasto. 
Utiliza el siguiente contexto de documentación técnica para responder la pregunta del usuario de forma precisa y detallada.

Categoría de la pregunta: {categoria}
Tipo de búsqueda: {tipo_busqueda}

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA: Proporciona una respuesta técnica clara, estructurada y basada únicamente en el contexto proporcionado. 
Incluye detalles técnicos relevantes, arquitectura, APIs, tecnologías y patrones de implementación cuando sea necesario.
Si el contexto no contiene información suficiente, indícalo claramente. Si necesitas más información puedes preguntarla.
Indica que el correo de soporte es soporte@scangasto.com."""
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        
        response = chain.invoke({
            "categoria": categoria,
            "tipo_busqueda": tipo_busqueda,
            "contexto": contexto,
            "pregunta": pregunta
        })
        
        # 5. Formatear respuesta con fuentes
        return formatear_respuesta_con_fuentes(response.content, metadatas, mostrar_fuentes)
        
    except Exception as e:
        return f"❌ Error en el agente técnico: {str(e)}"

def agente_gestion(pregunta, categoria, tipo_busqueda, mostrar_fuentes=True):
    """
    Agente de gestión que busca documentos relevantes en la BBDD vectorial (semántica)
    o realiza búsqueda léxica en archivos markdown según el tipo de búsqueda.
    
    Args:
        pregunta: La pregunta del usuario
        categoria: Categoría de la pregunta (FUNCIONAL/TECNICA/GESTION)
        tipo_busqueda: Tipo de búsqueda (SEMANTICA/LEXICA)
        mostrar_fuentes: Si se deben mostrar las fuentes consultadas
    """
    try:
        # Manejo de búsqueda léxica
        if tipo_busqueda == "LEXICA":
            carpeta_gestion = './doc/doc_scangestor/GESTION'
            terminos, resultados = busqueda_lexica_en_archivos(pregunta, carpeta_gestion)
            
            if terminos is None:
                return "⚠️ No se pudieron extraer términos de búsqueda de tu pregunta. Inténtalo de nuevo especificando claramente el término que buscas."
            
            return formatear_resultados_lexicos(terminos, resultados, mostrar_fuentes)
        
        # Manejo de búsqueda semántica (comportamiento original)
        # 1. Buscar documentos relevantes
        results = buscar_documentos_relevantes(pregunta, categoria)
        
        # 2. Verificar si hay resultados
        if not results['documents'] or not results['documents'][0]:
            return "⚠️ No se encontraron documentos relevantes en la base de datos para responder tu pregunta."
        
        # 3. Construir contexto
        documentos = results['documents'][0]
        metadatas = results['metadatas'][0]
        contexto = construir_contexto(documentos, metadatas)
        
        # 4. Crear prompt especializado para preguntas de gestión
        template = """Eres un asistente experto en gestión de la aplicación ScanGasto. 
Utiliza el siguiente contexto de documentación sobre procesos y organización para responder la pregunta del usuario de forma precisa y detallada.

Categoría de la pregunta: {categoria}
Tipo de búsqueda: {tipo_busqueda}

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA: Proporciona una respuesta clara, estructurada y basada únicamente en el contexto proporcionado. 
Incluye información sobre procesos, procedimientos, organizaciones, responsabilidades, documentación y administración cuando sea relevante.
Si el contexto no contiene información suficiente, indícalo claramente.
Comenta que el correo del jefe de proyecto es angel@scangasto.com.
"""
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        
        response = chain.invoke({
            "categoria": categoria,
            "tipo_busqueda": tipo_busqueda,
            "contexto": contexto,
            "pregunta": pregunta
        })
        
        # 5. Formatear respuesta con fuentes
        return formatear_respuesta_con_fuentes(response.content, metadatas, mostrar_fuentes)
        
    except Exception as e:
        return f"❌ Error en el agente de gestión: {str(e)}"

def agente_sintetizador(pregunta, respuesta_funcional, respuesta_tecnica, respuesta_gestion):
    """    Agente sintetizador que fusiona las respuestas de múltiples agentes
    en una salida coherente y estructurada.
    
    Args:
        pregunta: La pregunta original del usuario
        respuesta_funcional: Respuesta del agente funcional
        respuesta_tecnica: Respuesta del agente técnico
        respuesta_gestion: Respuesta del agente de gestión
    
    Returns:
        Una respuesta sintetizada y coherente
    """
    try:
        template = """Eres un agente sintetizador experto en consolidar información de múltiples fuentes.

Tu tarea es analizar las respuestas de tres agentes especializados (Funcional, Técnico y Gestión) y crear una ÚNICA respuesta coherente, bien estructurada y completa para el usuario.

PREGUNTA ORIGINAL: {pregunta}

---

**RESPUESTA DEL AGENTE FUNCIONAL:**
{respuesta_funcional}

---

**RESPUESTA DEL AGENTE TÉCNICO:**
{respuesta_tecnica}

---

**RESPUESTA DEL AGENTE DE GESTIÓN:**
{respuesta_gestion}

---

INSTRUCCIONES PARA LA SÍNTESIS:
1. Si alguna respuesta indica "No se encontraron coincidencias", ignórala y enfócate en las que sí tienen resultados.
2. Si todas las respuestas indican que no hay resultados, informa claramente que no se encontró información.
3. Organiza la información por categorías (Funcional, Técnica, Gestión) SOLO si hay resultados en múltiples categorías.
4. Elimina redundancias y duplicados.
5. Mantén las referencias a archivos y líneas cuando estén disponibles.
6. Crea una respuesta fluida y natural, no copies y pegues literalmente.
7. Si solo hay resultados en una categoría, presenta esa información directamente sin mencionar las otras categorías.

RESPUESTA SINTETIZADA:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        
        response = chain.invoke({
            "pregunta": pregunta,
            "respuesta_funcional": respuesta_funcional,
            "respuesta_tecnica": respuesta_tecnica,
            "respuesta_gestion": respuesta_gestion
        })
        
        return response.content
        
    except Exception as e:
        # Si falla la síntesis, devolver las respuestas organizadas manualmente
        return f"""## Resultados de búsqueda léxica

### 📋 Área Funcional
{respuesta_funcional}

### 🔧 Área Técnica
{respuesta_tecnica}

### 📊 Área de Gestión
{respuesta_gestion}

---
⚠️ Nota: Error al sintetizar respuestas: {str(e)}"""

# Diccionario de dispatch para selección de agentes
AGENTES_DISPATCH = {
    "FUNCIONAL": agente_funcional,
    "TECNICA": agente_tecnico,
    "GESTION": agente_gestion
}

def chat_response(message, history, mostrar_categoria, mostrar_fuentes):
    """
    Función principal del chat que procesa los mensajes.
    
    Args:
        message: El mensaje del usuario
        history: Historial de mensajes
        mostrar_categoria: Si se debe mostrar la categoría identificada
        mostrar_fuentes: Si se deben mostrar las fuentes consultadas
    """
    if not message.strip():
        return "Por favor, escribe una pregunta."
    
    # 1. Clasificar pregunta (categoría y tipo de búsqueda)
    clasificacion = agente_orquestador(message)
    categoria = extraer_categoria(clasificacion)
    tipo_busqueda = extraer_tipo_busqueda(clasificacion)
    
    # 2. Manejo diferenciado según tipo de búsqueda
    if tipo_busqueda == "LEXICA":
        # Para búsquedas léxicas: llamar a los 3 agentes y sintetizar
        respuesta_funcional = agente_funcional(message, "FUNCIONAL", tipo_busqueda, mostrar_fuentes)
        respuesta_tecnica = agente_tecnico(message, "TECNICA", tipo_busqueda, mostrar_fuentes)
        respuesta_gestion = agente_gestion(message, "GESTION", tipo_busqueda, mostrar_fuentes)
        
        # Sintetizar las tres respuestas en una sola
        respuesta_agente = agente_sintetizador(message, respuesta_funcional, respuesta_tecnica, respuesta_gestion)
        
    else:
        # Para búsquedas semánticas: usar el agente de la categoría específica (comportamiento original)
        agente = AGENTES_DISPATCH.get(categoria)
        
        if agente:
            respuesta_agente = agente(message, categoria, tipo_busqueda, mostrar_fuentes)
        else:
            # Para categorías desconocidas
            categoria_header = f"🤖 **Categoría identificada:** {categoria}\n\n---\n\n" if mostrar_categoria else ""
            return f"""{categoria_header}⚠️ Lo siento, no he podido clasificar correctamente tu pregunta. 

Inténtalo de nuevo con una pregunta relacionada con:
- **FUNCIONAL**: Funcionalidades, características, comportamiento de usuario, casos de uso o flujos de trabajo.
- **TÉCNICA**: Implementación, código, arquitectura, tecnologías, APIs, bases de datos o desarrollo.
- **GESTIÓN**: Procesos, organización, documentación, planificación, administración o procedimientos."""
    
    # 3. Formatear respuesta completa (con o sin categoría según el checkbox)
    if mostrar_categoria:
        tipo_busqueda_label = "🔍 Léxica (búsqueda en todos los documentos)" if tipo_busqueda == "LEXICA" else f"📚 Semántica - {categoria}"
        return f"""🤖 **Tipo de búsqueda:** {tipo_busqueda_label}
---
{respuesta_agente}"""
    else:
        return respuesta_agente

# Crear interfaz de Gradio
with gr.Blocks(title="IIA Capstone - ScanGasto") as demo:
    gr.Markdown("""
    # 💬 ScanGasto - Aplicación de gestión de tickets
    
    Puedes realizar preguntas relacionadas con la aplicación ScanGasto. El agente clasificará tu pregunta en una de las siguientes categorías:
    - **FUNCIONAL**: Preguntas sobre funcionalidades y casos de uso
    - **TÉCNICA**: Preguntas sobre implementación y desarrollo
    - **GESTIÓN**: Preguntas sobre procesos y organización
    Después, otro agente especializado en cada categoría analizará la pregunta y proporcionará una respuesta detallada.
    """)
    
    # Checkboxes para opciones de visualización
    mostrar_categoria_check = gr.Checkbox(
        label="Mostrar categoría",
        value=False
    )
    
    mostrar_fuentes_check = gr.Checkbox(
        label="Mostrar fuentes",
        value=False
    )
    
    chatbot = gr.ChatInterface(
        fn=chat_response,
        additional_inputs=[mostrar_categoria_check, mostrar_fuentes_check],
        title="",
        description="Escribe tu pregunta abajo:",
        examples=[
            ["¿Cómo puedo registrar un ticket?"],
            ["¿Qué tecnología se utiliza para comprobar un ticket con QR?"],
            ["¿Qué perfiles han desarrollado el módulo de consultas?"]
        ],
        cache_examples=False
    )

if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
