# Documentación del Código - Sistema RAG Multi-Agente

**Guía Detallada de Funciones y Módulos**  
**Proyecto Capstone IIA - ScanGasto**  
**Versión:** 2.0 - Diciembre 2025

---

## 📋 Índice

1. [Estructura del Módulo](#estructura-del-módulo)
2. [Variables Globales y Configuración](#variables-globales-y-configuración)
3. [Funciones de Utilidad](#funciones-de-utilidad)
4. [Agentes del Sistema](#agentes-del-sistema)
5. [Funciones de Búsqueda](#funciones-de-búsqueda)
6. [Funciones de Formateo](#funciones-de-formateo)
7. [Interfaz de Usuario](#interfaz-de-usuario)
8. [Ejemplos de Uso](#ejemplos-de-uso)

---

## 1. Estructura del Módulo

### Docstring del Módulo

```python
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
```

### Importaciones

```python
import os          # Gestión de rutas y variables de entorno
import re          # Expresiones regulares para parsing
import glob        # Búsqueda de archivos por patrón
import gradio      # Interfaz web interactiva
from dotenv import load_dotenv  # Carga de variables de entorno
import chromadb    # Base de datos vectorial
from chromadb.utils import embedding_functions  # Funciones de embeddings
from langchain_core.prompts import ChatPromptTemplate  # Templates de prompts
from langchain_openai import ChatOpenAI  # Cliente LLM de OpenAI
```

---

## 2. Variables Globales y Configuración

### Constantes de ChromaDB

```python
DB_PATH = './bbdd'
```
**Descripción:** Ruta al directorio donde ChromaDB almacena los datos  
**Tipo:** `str`  
**Uso:** Configuración de persistencia de la base de datos vectorial

```python
COLLECTION_NAME = "documentacion_openai"
```
**Descripción:** Nombre de la colección en ChromaDB  
**Tipo:** `str`  
**Uso:** Identificador único de la colección de documentos

```python
MODEL_NAME = "text-embedding-3-small"
```
**Descripción:** Modelo de embeddings de OpenAI  
**Tipo:** `str`  
**Uso:** Generación de vectores semánticos (1536 dimensiones)

### Patrones Regex Compilados

```python
CATEGORIA_PATTERN = re.compile(r'Categoría:\s*(FUNCIONAL|TECNICA|GESTION)', re.IGNORECASE)
```
**Descripción:** Regex para extraer categoría de la clasificación  
**Tipo:** `re.Pattern`  
**Optimización:** Compilado una sola vez a nivel de módulo

```python
TIPO_BUSQUEDA_PATTERN = re.compile(r'Tipo de búsqueda:\s*(SEMANTICA|LEXICA)', re.IGNORECASE)
```
**Descripción:** Regex para extraer tipo de búsqueda  
**Tipo:** `re.Pattern`  
**Optimización:** Compilado una sola vez a nivel de módulo

### Cliente LLM Global

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=API_KEY
)
```
**Descripción:** Instancia global de ChatOpenAI  
**Tipo:** `ChatOpenAI`  
**Parámetros:**
- `model`: Modelo GPT-4o-mini (equilibrio costo/rendimiento)
- `temperature`: 0.3 (respuestas consistentes pero no deterministas)
- `api_key`: Clave API de OpenAI desde variable de entorno

### Cache de Colección

```python
_collection_cache = None
```
**Descripción:** Cache global para la colección de ChromaDB  
**Tipo:** `Optional[chromadb.Collection]`  
**Patrón:** Singleton para evitar reconexiones

---

## 3. Funciones de Utilidad

### 3.1 `get_chroma_collection()`

```python
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
```

**Flujo de ejecución:**
1. Verifica si `_collection_cache` es `None`
2. Si es `None`:
   - Crea cliente persistente de ChromaDB
   - Configura función de embeddings OpenAI
   - Obtiene o crea colección
   - Almacena en cache
3. Retorna colección cacheada

**Complejidad:** O(1) después de primera llamada  
**Beneficio:** Reduce latencia de ~500ms a ~5ms

### 3.2 `extraer_categoria()`

```python
def extraer_categoria(clasificacion_texto):
    """Extrae la categoría del texto de clasificación usando regex.
    
    Args:
        clasificacion_texto (str): Texto con formato "Categoría: [CATEGORIA]"
    
    Returns:
        str: Categoría extraída en mayúsculas (FUNCIONAL/TECNICA/GESTION)
             o "DESCONOCIDA" si no se encuentra patrón válido
    """
```

**Ejemplo de entrada:**
```
"Categoría: FUNCIONAL\nTipo de búsqueda: SEMANTICA\n..."
```

**Ejemplo de salida:**
```
"FUNCIONAL"
```

**Casos edge:**
- Sin patrón válido → `"DESCONOCIDA"`
- Case-insensitive → `"funcional"` → `"FUNCIONAL"`

### 3.3 `extraer_tipo_busqueda()`

```python
def extraer_tipo_busqueda(clasificacion_texto):
    """Extrae el tipo de búsqueda del texto de clasificación usando regex.
    
    Args:
        clasificacion_texto (str): Texto con formato "Tipo de búsqueda: [TIPO]"
    
    Returns:
        str: Tipo de búsqueda extraído (SEMANTICA/LEXICA)
             Por defecto retorna "SEMANTICA" si no se encuentra patrón
    """
```

**Valor por defecto:** `"SEMANTICA"` (asunción conservadora)

---

## 4. Agentes del Sistema

### 4.1 `agente_orquestador()`

```python
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
```

**Prompt del sistema:**
```python
template = """Eres un agente clasificador experto. Tu tarea es analizar preguntas y hacer dos clasificaciones:

**CATEGORÍA (elige una):**
1. FUNCIONAL: Preguntas sobre cómo funciona algo, características, comportamiento de usuario, casos de uso, flujos de trabajo.
2. TECNICA: Preguntas sobre implementación, código, arquitectura, tecnologías, APIs, bases de datos, desarrollo.
3. GESTION: Preguntas sobre procesos, organización, documentación, planificación, administración, procedimientos.

**TIPO DE BÚSQUEDA (elige uno):**
- SEMANTICA: Preguntas conceptuales, de comprensión, que requieren entender el significado y contexto. 
  Ejemplos: "¿cómo funciona X?", "¿qué hace Y?", "¿para qué sirve Z?"
- LEXICA: Búsquedas de términos específicos, nombres exactos de campos, variables, strings, o ubicaciones de código. 
  Ejemplos: "¿dónde aparece el campo X?", "¿en qué archivo está la variable Y?", "busca el string Z"

Responde ÚNICAMENTE con el formato:
Categoría: [FUNCIONAL/TECNICA/GESTION]
Tipo de búsqueda: [SEMANTICA/LEXICA]
Justificación: [Breve explicación]

Pregunta: {pregunta}"""
```

**Decisiones de diseño:**
- Ejemplos específicos para cada tipo de búsqueda ayudan a la clasificación
- Formato estructurado facilita parsing con regex
- Justificación útil para debugging y auditoría
- Instrucciones explícitas ("ÚNICAMENTE") previenen respuestas adicionales

**Manejo de errores:**
```python
except Exception as e:
    return f"❌ Error al clasificar la pregunta: {str(e)}"
```

### 4.2 `agente_funcional()`

```python
def agente_funcional(pregunta, categoria, tipo_busqueda, mostrar_fuentes=True):
    """Agente funcional que busca documentos relevantes en la BBDD vectorial (semántica)
    o realiza búsqueda léxica en archivos markdown según el tipo de búsqueda.
    
    Args:
        pregunta (str): La pregunta del usuario
        categoria (str): Categoría de la pregunta (FUNCIONAL/TECNICA/GESTION)
        tipo_busqueda (str): Tipo de búsqueda (SEMANTICA/LEXICA)
        mostrar_fuentes (bool): Si se deben mostrar las fuentes consultadas
    
    Returns:
        str: Respuesta formateada con o sin fuentes según configuración
    """
```

**Flujo de decisión:**

**Si `tipo_busqueda == "LEXICA"`:**
1. Define carpeta: `./doc/doc_scangestor/FUNCIONAL`
2. Llama a `busqueda_lexica_en_archivos()`
3. Formatea resultados léxicos
4. **Return temprano** (evita búsqueda semántica)

**Si `tipo_busqueda == "SEMANTICA"`:**
1. Busca documentos relevantes en ChromaDB
2. Verifica resultados
3. Construye contexto
4. Genera prompt especializado para dominio funcional
5. Invoca LangChain
6. Formatea respuesta con fuentes

**Prompt funcional:**
```python
template = """Eres un asistente experto en la aplicación ScanGasto. 
Utiliza el siguiente contexto de documentación para responder la pregunta del usuario de forma precisa y detallada.

Categoría de la pregunta: {categoria}
Tipo de búsqueda: {tipo_busqueda}

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA: Proporciona una respuesta clara, estructurada y basada únicamente en el contexto proporcionado. 
Si lo ves necesario incluye ejemplos prácticos o pasos a seguir.
Si el contexto no contiene información suficiente, indícalo claramente. 
Puedes proponer cambios en base a las preguntas realizadas para incorporar funcionalidades nuevas."""
```

**Características del prompt:**
- Instrucción de ser "experto en ScanGasto" establece contexto
- Inclusión de categoría y tipo de búsqueda para mejor contexto
- Énfasis en ejemplos prácticos y pasos a seguir
- Fallback explícito si contexto es insuficiente
- Permite sugerencias de mejora basadas en preguntas
- Respuesta estructurada y clara como objetivo

**Manejo de respuestas sin resultados:**
```python
if not results['documents'] or not results['documents'][0]:
    return "⚠️ No se encontraron documentos relevantes en la base de datos para responder tu pregunta."
```

**Manejo de búsqueda léxica sin términos:**
```python
if terminos is None:
    return "⚠️ No se pudieron extraer términos de búsqueda de tu pregunta. Inténtalo de nuevo especificando claramente el término que buscas."
```

### 4.3 `agente_tecnico()`

```python
def agente_tecnico(pregunta, categoria, tipo_busqueda, mostrar_fuentes=True):
    """Agente técnico que busca documentos relevantes en la BBDD vectorial (semántica)
    o realiza búsqueda léxica en archivos markdown según el tipo de búsqueda.
    
    Args:
        pregunta (str): La pregunta del usuario
        categoria (str): Categoría de la pregunta (FUNCIONAL/TECNICA/GESTION)
        tipo_busqueda (str): Tipo de búsqueda (SEMANTICA/LEXICA)
        mostrar_fuentes (bool): Si se deben mostrar las fuentes consultadas
    
    Returns:
        str: Respuesta formateada con detalles técnicos
    """
```

**Diferencias con agente funcional:**
- Carpeta léxica: `./doc/doc_scangestor/TECNICA`
- Prompt técnico: Énfasis en arquitectura, APIs, tecnologías, patrones de implementación
- Incluye contacto de soporte técnico: `soporte@scangasto.com`

**Prompt técnico:**
```python
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
```

**Características diferenciales:**
- Énfasis en "detalles técnicos relevantes, arquitectura, APIs, tecnologías y patrones"
- Permite preguntar por más información si es necesario
- Incluye contacto de soporte en la respuesta

### 4.4 `agente_gestion()`

```python
def agente_gestion(pregunta, categoria, tipo_busqueda, mostrar_fuentes=True):
    """Agente de gestión que busca documentos relevantes en la BBDD vectorial (semántica)
    o realiza búsqueda léxica en archivos markdown según el tipo de búsqueda.
    
    Args:
        pregunta (str): La pregunta del usuario
        categoria (str): Categoría de la pregunta (FUNCIONAL/TECNICA/GESTION)
        tipo_busqueda (str): Tipo de búsqueda (SEMANTICA/LEXICA)
        mostrar_fuentes (bool): Si se deben mostrar las fuentes consultadas
    
    Returns:
        str: Respuesta formateada con información de gestión
    """
```

**Diferencias:**
- Carpeta léxica: `./doc/doc_scangestor/GESTION`
- Prompt de gestión: Énfasis en procesos, procedimientos, responsabilidades, administración
- Incluye contacto del jefe de proyecto: `angel@scangasto.com`

**Prompt de gestión:**
```python
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
Comenta que el correo del jefe de proyecto es angel@scangasto.com."""
```

**Características diferenciales:**
- Enfoque en procesos, procedimientos, organizaciones, responsabilidades
- Orientado a preguntas administrativas y de gestión
- Contacto del jefe de proyecto en lugar de soporte técnico

### 4.5 `agente_sintetizador()`

```python
def agente_sintetizador(pregunta, respuesta_funcional, respuesta_tecnica, respuesta_gestion):
    """Agente sintetizador que fusiona las respuestas de múltiples agentes
    en una salida coherente y estructurada.
    
    Args:
        pregunta (str): La pregunta original del usuario
        respuesta_funcional (str): Respuesta del agente funcional
        respuesta_tecnica (str): Respuesta del agente técnico
        respuesta_gestion (str): Respuesta del agente de gestión
    
    Returns:
        str: Una respuesta sintetizada y coherente
    """
```

**Responsabilidad:** Fusión inteligente de 3 respuestas en 1

**Instrucciones de síntesis:**
1. Ignorar respuestas sin resultados
2. Si todas vacías → Informar que no hay información
3. Organizar por categorías si hay múltiples resultados
4. Eliminar redundancias y duplicados
5. Mantener referencias a archivos/líneas
6. Crear respuesta fluida (no copiar/pegar literal)
7. Si solo 1 categoría tiene resultados → Presentar directamente

**Fallback:** Si falla síntesis, retorna respuestas organizadas manualmente

---

## 5. Funciones de Búsqueda

### 5.1 `buscar_documentos_relevantes()`

```python
def buscar_documentos_relevantes(pregunta, categoria, n_results=3):
    """Busca documentos relevantes en ChromaDB según la pregunta y categoría.
    
    Args:
        pregunta (str): Pregunta del usuario
        categoria (str): Categoría para filtrar (FUNCIONAL/TECNICA/GESTION)
        n_results (int): Número de documentos a recuperar (default: 3)
    
    Returns:
        dict: Resultados de ChromaDB con estructura:
            {
                'documents': [[doc1, doc2, doc3]],
                'metadatas': [[meta1, meta2, meta3]],
                'distances': [[dist1, dist2, dist3]]
            }
    """
```

**Proceso:**
1. Obtiene colección de ChromaDB (con cache)
2. ChromaDB convierte `pregunta` a embedding automáticamente
3. Busca por similitud coseno en espacio vectorial
4. Filtra por metadata `category == categoria`
5. Retorna top-N documentos más similares

**Parámetros de tuning:**
- `n_results`: Más documentos = más contexto pero más tokens
- Filtro de metadata: Opcional (si categoria == "DESCONOCIDA", sin filtro)

### 5.2 `busqueda_lexica_en_archivos()`

```python
def busqueda_lexica_en_archivos(pregunta, carpeta_docs):
    """Realiza una búsqueda léxica (texto literal) en archivos markdown.
    
    Args:
        pregunta (str): Pregunta del usuario con término a buscar
        carpeta_docs (str): Ruta a la carpeta con archivos markdown
    
    Returns:
        tuple: (terminos, resultados)
            - terminos (list): Lista de términos extraídos
            - resultados (list): Lista de diccionarios con coincidencias:
                {
                    'archivo': str,
                    'linea': int,
                    'termino': str,
                    'contexto': str
                }
    """
```

**Algoritmo de extracción de términos:**

**Paso 1: Buscar texto entre comillas**
```python
quoted = re.findall(r'["\'""]([^"\'\'"]+)["\'""]', pregunta)
```
Ejemplo: `"¿Dónde está 'qr_raw_string'?"` → `['qr_raw_string']`

**Paso 2: Si no hay comillas, buscar términos técnicos**
```python
palabras_excluidas = {'el', 'la', 'los', 'donde', 'campo', 'variable', ...}
candidatos = [palabra for palabra in pregunta if len(palabra) > 3 and no_excluida]
terminos_tecnicos = [c for c in candidatos if '_' in c or '-' in c]
```

**Paso 3: Seleccionar término más específico**
```python
terminos = [max(terminos_tecnicos, key=len)]
```

**Búsqueda en archivos:**
```python
patron_archivos = os.path.join(carpeta_docs, '*.md')
archivos = glob.glob(patron_archivos)

for archivo in archivos:
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
        lineas = contenido.split('\n')
        
        for i, linea in enumerate(lineas, 1):
            if termino.lower() in linea.lower():
                # Contexto: 2 líneas antes, actual, 1 después
                contexto = '\n'.join(lineas[i-2:i+1])
                resultados.append({...})
```

**Complejidad:** O(n * m) donde n=archivos, m=líneas por archivo  
**Optimización futura:** Indexación previa con motor de búsqueda

---

## 6. Funciones de Formateo

### 6.1 `construir_contexto()`

```python
def construir_contexto(documentos, metadatas):
    """Construye el contexto a partir de documentos y metadatos.
    
    Args:
        documentos (list): Lista de textos de documentos
        metadatas (list): Lista de metadatos correspondientes
    
    Returns:
        str: Contexto consolidado con formato:
             [Documento 1 - archivo.md]
             texto...
             ---
             [Documento 2 - archivo.md]
             texto...
    """
```

**Formato de salida:**
```
[Documento 1 - 01 Apuntes contables - DT.md]
FastAPI es el framework web...

---

[Documento 2 - 02 QR - DT.md]
El sistema de QR utiliza...

---

[Documento 3 - 03 Consultas - DT.md]
Las consultas se realizan...
```

**Optimización:** List comprehension para construcción eficiente

### 6.2 `formatear_respuesta_con_fuentes()`

```python
def formatear_respuesta_con_fuentes(contenido, metadatas, mostrar_fuentes=True):
    """Formatea la respuesta incluyendo opcionalmente las fuentes consultadas.
    
    Args:
        contenido (str): Contenido de la respuesta generada
        metadatas (list): Lista de metadatos de los documentos fuente
        mostrar_fuentes (bool): Si se deben incluir las fuentes
    
    Returns:
        str: Respuesta formateada con o sin sección de fuentes
    """
```

**Lógica:**
- Si `mostrar_fuentes == False`: Retorna solo contenido
- Si `mostrar_fuentes == True`: Añade sección de fuentes

**Formato con fuentes:**
```
[Respuesta del LLM aquí]

📚 **Fuentes consultadas:**
- 01 Apuntes contables - DT.md
- 02 QR - DT.md
- 03 Consultas - DT.md
```

**Deduplicación:** Usa `dict.fromkeys()` para eliminar archivos duplicados

### 6.3 `formatear_resultados_lexicos()`

```python
def formatear_resultados_lexicos(terminos, resultados, mostrar_fuentes):
    """Formatea los resultados de una búsqueda léxica.
    
    Args:
        terminos (list): Lista de términos buscados
        resultados (list): Lista de coincidencias encontradas
        mostrar_fuentes (bool): Si se deben mostrar los archivos consultados
    
    Returns:
        str: Resultados formateados con ubicaciones y contexto
    """
```

**Formato de salida:**
```
🔍 **Búsqueda léxica de:** qr_raw_string

Se encontraron **5 coincidencias** en **2 archivos**:

### 📄 01 Apuntes contables - DT.md

**Línea 123:**
```
...contexto anterior...
    ocr_raw_data JSONB, -- Respuesta completa del OCR
...contexto posterior...
```

**Línea 145:**
```
...otro contexto...
```

_... y 1 coincidencias más en este archivo_

📚 **Archivos consultados:**
- 01 Apuntes contables - DT.md
- 02 QR - DT.md
```

**Limitación:** Máximo 3 coincidencias por archivo (evita respuestas excesivas)

---

## 7. Interfaz de Usuario

### 7.1 `chat_response()`

```python
def chat_response(message, history, mostrar_categoria, mostrar_fuentes):
    """Función principal del chat que procesa los mensajes.
    
    Args:
        message (str): El mensaje del usuario
        history (list): Historial de mensajes (manejado por Gradio)
        mostrar_categoria (bool): Si se debe mostrar la categoría identificada
        mostrar_fuentes (bool): Si se deben mostrar las fuentes consultadas
    
    Returns:
        str: Respuesta formateada para el usuario
    """
```

**Flujo principal:**

**1. Validación de entrada**
```python
if not message.strip():
    return "Por favor, escribe una pregunta."
```

**2. Clasificación**
```python
clasificacion = agente_orquestador(message)
categoria = extraer_categoria(clasificacion)
tipo_busqueda = extraer_tipo_busqueda(clasificacion)
```

**3. Bifurcación por tipo de búsqueda**

**Si LEXICA:**
```python
# Invocar 3 agentes en paralelo
respuesta_funcional = agente_funcional(message, "FUNCIONAL", tipo_busqueda, mostrar_fuentes)
respuesta_tecnica = agente_tecnico(message, "TECNICA", tipo_busqueda, mostrar_fuentes)
respuesta_gestion = agente_gestion(message, "GESTION", tipo_busqueda, mostrar_fuentes)

# Sintetizar
respuesta_agente = agente_sintetizador(message, respuesta_funcional, respuesta_tecnica, respuesta_gestion)
```

**Si SEMANTICA:**
```python
# Invocar agente de la categoría específica
agente = AGENTES_DISPATCH.get(categoria)
respuesta_agente = agente(message, categoria, tipo_busqueda, mostrar_fuentes)
```

**4. Formateo final**
```python
if mostrar_categoria:
    tipo_busqueda_label = "🔍 Léxica" if tipo_busqueda == "LEXICA" else f"📚 Semántica - {categoria}"
    return f"🤖 **Tipo de búsqueda:** {tipo_busqueda_label}\n---\n{respuesta_agente}"
else:
    return respuesta_agente
```

### 7.2 Diccionario de Dispatch

```python
AGENTES_DISPATCH = {
    "FUNCIONAL": agente_funcional,
    "TECNICA": agente_tecnico,
    "GESTION": agente_gestion
}
```

**Propósito:** Mapeo dinámico de categoría a función de agente  
**Beneficio:** Evita if/elif/else repetitivo, facilita extensión

### 7.3 Interfaz Gradio

```python
with gr.Blocks(title="IIA Capstone - ScanGasto") as demo:
    gr.Markdown("""...""")  # Descripción
    
    # Checkboxes
    mostrar_categoria_check = gr.Checkbox(
        label="Mostrar categoría",
        value=False
    )
    mostrar_fuentes_check = gr.Checkbox(
        label="Mostrar fuentes",
        value=False
    )
    
    # Chat
    chatbot = gr.ChatInterface(
        fn=chat_response,
        additional_inputs=[mostrar_categoria_check, mostrar_fuentes_check],
        examples=[...],
        cache_examples=False
    )
```

**Parámetros clave:**
- `additional_inputs`: Pasa checkboxes a la función
- `examples`: Lista de listas (cada sublista = [mensaje])
- `cache_examples=False`: Usa valores actuales de checkboxes

**Lanzamiento:**
```python
if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
```

---

## 8. Ejemplos de Uso

### Ejemplo 1: Búsqueda Semántica Funcional

**Input:**
```python
message = "¿Cómo funciona el sistema de QR?"
mostrar_categoria = True
mostrar_fuentes = True
```

**Output:**
```
🤖 **Tipo de búsqueda:** 📚 Semántica - FUNCIONAL
---
El sistema de QR en ScanGasto funciona mediante...
[Explicación contextualizada]

📚 **Fuentes consultadas:**
- 02 QR - DF.md
- 01 Apuntes contables - DF.md
```

### Ejemplo 2: Búsqueda Léxica Técnica

**Input:**
```python
message = "¿Dónde aparece el campo qr_raw_string?"
mostrar_categoria = True
mostrar_fuentes = True
```

**Output:**
```
🤖 **Tipo de búsqueda:** 🔍 Léxica (búsqueda en todos los documentos)
---
🔍 **Búsqueda léxica de:** qr_raw_string

Se encontraron **1 coincidencias** en **1 archivos**:

### 📄 01 Apuntes contables - DT.md

**Línea 123:**
```
-- CREATE TABLE expenses (
--     ocr_raw_data JSONB, -- Respuesta completa del OCR
```

📚 **Archivos consultados:**
- 01 Apuntes contables - DT.md
```

### Ejemplo 3: Búsqueda Semántica con Opciones Desactivadas

**Input:**
```python
message = "¿Qué perfiles desarrollaron el módulo?"
mostrar_categoria = False
mostrar_fuentes = False
```

**Output:**
```
El módulo de consultas fue desarrollado por el equipo técnico...
[Sin encabezado de categoría]
[Sin sección de fuentes]
```

---

## 📊 Resumen de Funciones

| Función | Propósito | Entrada | Salida |
|---------|-----------|---------|--------|
| `get_chroma_collection()` | Obtener colección ChromaDB | - | Collection |
| `agente_orquestador()` | Clasificar pregunta | pregunta | clasificación |
| `extraer_categoria()` | Extraer categoría | texto | FUNCIONAL/TECNICA/GESTION |
| `extraer_tipo_busqueda()` | Extraer tipo | texto | SEMANTICA/LEXICA |
| `buscar_documentos_relevantes()` | Búsqueda semántica | pregunta, categoría | resultados |
| `busqueda_lexica_en_archivos()` | Búsqueda léxica | pregunta, carpeta | terminos, coincidencias |
| `construir_contexto()` | Consolidar docs | documentos, metadatas | contexto |
| `formatear_respuesta_con_fuentes()` | Formatear respuesta | contenido, metadatas | respuesta |
| `formatear_resultados_lexicos()` | Formatear léxica | terminos, resultados | respuesta |
| `agente_funcional()` | Agente funcional | pregunta, params | respuesta |
| `agente_tecnico()` | Agente técnico | pregunta, params | respuesta |
| `agente_gestion()` | Agente gestión | pregunta, params | respuesta |
| `agente_sintetizador()` | Fusionar respuestas | 3 respuestas | respuesta única |
| `chat_response()` | Función principal | mensaje, config | respuesta |

---

## 🔧 Guía de Mantenimiento

### Añadir nueva categoría

1. Añadir al prompt del orquestador
2. Crear nuevo agente `agente_[nueva]()`
3. Actualizar `AGENTES_DISPATCH`
4. Crear carpeta `./doc/doc_scangestor/[NUEVA]`

### Cambiar modelo LLM

```python
llm = ChatOpenAI(
    model="gpt-4-turbo",  # Cambiar aquí
    temperature=0.3,
    api_key=API_KEY
)
```

### Ajustar número de documentos

```python
def buscar_documentos_relevantes(pregunta, categoria, n_results=5):  # Cambiar aquí
```

### Modificar prompt de agente

Editar el `template` dentro de la función del agente correspondiente.

---

**Documento preparado para evaluación académica**  
**Proyecto Capstone - RAG Híbrido Multi-Agente de documentación**  
**Diciembre 2025**
