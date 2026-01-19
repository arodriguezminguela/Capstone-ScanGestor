# Sistema RAG Multi-Agente con Búsqueda Híbrida - ScanGasto

**Proyecto Capstone - RAG Híbrido Multi-Agente de documentación**  
**Fecha:** Enero 2026  
**Versión:** 2.2

---

## 📋 Descripción General

Sistema de Retrieval-Augmented Generation (RAG) especializado para responder preguntas sobre la aplicación **ScanGasto** (aplicación de gestión de tickets y gastos para gestorías). El sistema implementa una arquitectura multi-agente inteligente con capacidades de búsqueda híbrida que combina técnicas semánticas y léxicas.

### Características Principales

🤖 **Arquitectura Multi-Agente**
- Agente Orquestador: Clasificación inteligente de preguntas (categoría + tipo de búsqueda)
- Agentes Especializados: Funcional, Técnico y Gestión (enrutamiento vía AGENTES_DISPATCH)
- Agente Sintetizador: Fusión inteligente de respuestas múltiples en búsquedas léxicas

🔍 **Búsqueda Híbrida**
- **Semántica**: Búsquedas conceptuales usando embeddings y ChromaDB
- **Léxica**: Búsquedas literales de términos específicos en archivos markdown

🎨 **Interfaz Interactiva**
- UI web con Gradio
- Opciones configurables (mostrar categoría, mostrar fuentes)
- Ejemplos predefinidos

⚡ **Optimizaciones**
- Patrón Singleton para ChromaDB (get_chroma_collection)
- Cache de colecciones vectoriales
- Regex compilados (CATEGORIA_PATTERN, TIPO_BUSQUEDA_PATTERN)
- Funciones auxiliares: construir_contexto, formatear_respuesta_con_fuentes, formatear_resultados_lexicos
- Diccionario AGENTES_DISPATCH para enrutamiento dinámico

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **LLM** | OpenAI GPT-4o-mini | Latest | Generación y clasificación |
| **Framework RAG** | LangChain | Latest | Orquestación de prompts y cadenas |
| **Base de Datos Vectorial** | ChromaDB | Latest | Almacenamiento de embeddings |
| **Embeddings** | OpenAI text-embedding-3-small | Latest | Generación de vectores semánticos |
| **UI** | Gradio | Latest | Interfaz web interactiva |
| **Lenguaje** | Python | 3.11+ | Desarrollo principal |

---

## 📁 Estructura del Proyecto

```
Capstone/
├── bbdd/                                    # Base de datos vectorial ChromaDB
│   ├── d6658c68-7d89-46aa-8b5c-a1fc03b02a9d/  # Carpeta interna de ChromaDB
│   └── chroma.sqlite3                       # Base de datos SQLite de ChromaDB
├── doc/                                     # Documentación del proyecto
│   ├── doc_capstone/                        # Documentación del proyecto Capstone
│   │   ├── ARQUITECTURA_TECNICA.md          # Documentación de arquitectura del sistema
│   │   ├── DOCUMENTACION_CODIGO.md          # Documentación técnica del código fuente
│   │   ├── HERRAMIENTA_DOC_TO_MD.md         # Documentación de la herramienta doc_to_md
│   │   ├── Proyecto Capstone - Memoria final.pdf  # Memoria final del proyecto
│   │   └── Proyecto Capstone - Presentación.mp4   # Presentación en vídeo del proyecto
│   ├── doc_scangestor/                      # Documentación fuente para RAG de ScanGasto
│   │   ├── 00 General __exclude/            # Recursos generales excluidos del RAG
│   │   │   ├── ScanGasto - Infografía.png   # Infografía visual de ScanGasto
│   │   │   ├── ScanGasto - Resumen.md       # Resumen general de ScanGasto
│   │   │   └── ScanGasto - Video explicativo.mp4  # Vídeo explicativo de ScanGasto
│   │   ├── FUNCIONAL/                       # Documentación funcional
│   │   │   ├── 01 Apuntes contables - DF.md # Diseño funcional de apuntes contables
│   │   │   ├── 02 QR - DF.md                # Diseño funcional del módulo QR
│   │   │   └── 03 Consultas - DF.md         # Diseño funcional del módulo de consultas
│   │   ├── GESTION/                         # Documentación de gestión
│   │   │   ├── 01 Apuntes contables - Gestión.md  # Gestión del módulo de apuntes
│   │   │   ├── 02 QR - Gestión.md           # Gestión del módulo QR
│   │   │   └── 03 Consultas - Gestion.md    # Gestión del módulo de consultas
│   │   └── TECNICA/                         # Documentación técnica
│   │       ├── 01 Apuntes contables - DT.md # Diseño técnico de apuntes contables
│   │       ├── 02 QR - DT.md                # Diseño técnico del módulo QR
│   │       └── 03 Consultas - DT.md         # Diseño técnico del módulo de consultas
│   └── doc_to_md/                           # Herramienta de conversión de documentos
│       ├── 01_entrada/                      # Carpeta de documentos origen (DOCX, PDF)
│       │   └── .gitkeep                     # Archivo para mantener la carpeta en Git
│       ├── 02_salida/                       # Carpeta de documentos convertidos (MD)
│       │   └── .gitkeep                     # Archivo para mantener la carpeta en Git
│       ├── doc_to_md.py                     # Script principal de conversión
│       └── requirements.txt                 # Dependencias de la herramienta
├── .env                                     # Variables de entorno (API keys de OpenAI)
├── .gitignore                               # Archivos excluidos del control de versiones
├── bbdd.py                                  # Módulo de utilidades para ChromaDB (get_chroma_collection)
├── ingest.py                                # Script de ingesta/carga de documentos a ChromaDB
├── main.py                                  # Código principal del sistema RAG multi-agente
├── README.md                                # Documentación principal del proyecto (este archivo)
└── requirements.txt                         # Dependencias del proyecto principal
```

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.11 o superior
- Cuenta de OpenAI con API key
- 2GB de espacio en disco (para ChromaDB)

### Paso 1: Clonar/Descargar el Proyecto

```bash
cd c:\IA\Capstone
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=tu-api-key-aqui
```

### Paso 4: Preparar la Base de Datos Vectorial

Si es la primera vez, ejecutar el script de carga:

```bash
python ingest.py
```

Este script:
- Lee los archivos markdown de `./doc/doc_scangestor/`
- Genera embeddings con OpenAI (text-embedding-3-small)
- Almacena en ChromaDB con metadatos de categoría y fuente

---

## 💻 Uso del Sistema

### Iniciar la Aplicación

```bash
python main.py
```

La interfaz Gradio se abrirá en: `http://127.0.0.1:7860`

### Interfaz de Usuario

1. **Checkboxes de Configuración:**
   - ☑️ Mostrar categoría identificada
   - ☑️ Mostrar fuentes de documentación

2. **Área de Chat:**
   - Escribe tu pregunta
   - Presiona Enter o botón "Submit"
   - Visualiza la respuesta clasificada

3. **Ejemplos Predefinidos:**
   - ¿Cómo puedo registrar un ticket?
   - ¿Qué tecnología se utiliza para comprobar un ticket con QR?
   - ¿Qué perfiles han desarrollado el módulo de consultas?

### Tipos de Preguntas

**Búsqueda Semántica** (conceptual):
```
¿Cómo funciona el sistema de QR?
¿Para qué sirve el módulo de consultas?
¿Qué tecnologías usa el backend?
```

**Búsqueda Léxica** (literal):
```
¿Dónde aparece el campo qr_raw_string?
¿En qué archivo está la función agente_orquestador?
Busca el término "FastAPI"
```

---

## 📊 Flujo de Funcionamiento

### 1. Búsqueda Semántica (por categoría)
1. Usuario hace pregunta conceptual
2. Orquestador clasifica como SEMANTICA + categoría (FUNCIONAL/TECNICA/GESTION)
3. Se invoca solo el agente de esa categoría
4. Agente busca en ChromaDB los documentos relevantes
5. LangChain genera respuesta contextualizada

### 2. Búsqueda Léxica (en todos los dominios)
1. Usuario busca término específico (ej: "merchant_tax_id", "FastAPI")
2. Orquestador clasifica como LEXICA
3. Se invocan los 3 agentes simultáneamente (funcional + técnico + gestión)
4. Cada agente ejecuta busqueda_lexica_en_archivos() en su carpeta de docs
5. Resultados incluyen archivo, línea y contexto (±2 líneas)
6. Agente Sintetizador analiza las 3 respuestas:
   - Elimina duplicados y respuestas vacías
   - Organiza por categoría si hay múltiples resultados
   - Genera respuesta coherente y estructurada

---

## 🎯 Casos de Uso

### Caso 1: Evaluador académico consultando arquitectura

```
Pregunta: "¿Qué arquitectura técnica usa ScanGasto?"
Tipo: Semántica - TECNICA
Respuesta: Información sobre Flutter, FastAPI, PostgreSQL, etc.
```

### Caso 2: Desarrollador buscando un campo específico

```
Pregunta: "¿Dónde aparece merchant_tax_id?"
Tipo: Léxica
Respuesta: Ubicaciones exactas en docs TECNICA con líneas y contexto
```

### Caso 3: Manager consultando procesos

```
Pregunta: "¿Cómo se gestiona la aprobación de gastos?"
Tipo: Semántica - GESTION
Respuesta: Flujo de aprobación con roles y responsabilidades
```

---

## ⚙️ Configuración Avanzada

### Parámetros del LLM

En [main.py](main.py#L49):

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",      # Modelo de OpenAI
    temperature=0.3,          # Creatividad (0-1)
    api_key=API_KEY
)
```

### Configuración de ChromaDB

```python
DB_PATH = './bbdd'                          # Ruta de la BD
COLLECTION_NAME = "documentacion_openai"    # Nombre de colección
MODEL_NAME = "text-embedding-3-small"       # Modelo de embeddings
```

### Número de Documentos Recuperados

En función `buscar_documentos_relevantes(pregunta, categoria, n_results=3)`:

```python
n_results=3  # Por defecto 3 documentos
# Ajustable por parámetro según necesidad:
# - Más documentos = más contexto pero más tokens y costo
# - Menos documentos = respuestas más rápidas pero menos contexto
```

**Nota:** Este parámetro se puede modificar al llamar la función si se requiere más o menos contexto.

---

## 🔧 Funciones Auxiliares Clave

El sistema incluye funciones helper que mejoran la modularidad y reutilización:

### `get_chroma_collection()`
Patrón Singleton para obtener la colección ChromaDB. Evita reconexiones innecesarias usando caché global.

### `extraer_categoria(texto)` y `extraer_tipo_busqueda(texto)`
Usan regex compilados (CATEGORIA_PATTERN, TIPO_BUSQUEDA_PATTERN) para parsear la clasificación del orquestador.

### `construir_contexto(documentos, metadatas)`
Formatea los documentos recuperados en un string estructurado para el prompt del LLM.

### `formatear_respuesta_con_fuentes(contenido, metadatas, mostrar_fuentes)`
Añade lista de fuentes consultadas al final de la respuesta si el usuario lo solicita.

### `busqueda_lexica_en_archivos(pregunta, carpeta_docs)`
Implementa búsqueda literal en archivos markdown:
- Extrae términos de la pregunta (prioriza texto entre comillas)
- Busca coincidencias en archivos .md
- Retorna archivo, línea y contexto (±2 líneas)

### `formatear_resultados_lexicos(terminos, resultados, mostrar_fuentes)`
Formatea los resultados léxicos agrupados por archivo con límite de 3 coincidencias por archivo.

### `AGENTES_DISPATCH`
Diccionario que mapea categorías a funciones de agentes:
```python
AGENTES_DISPATCH = {
    "FUNCIONAL": agente_funcional,
    "TECNICA": agente_tecnico,
    "GESTION": agente_gestion
}
```
Permite enrutamiento dinámico sin condicionales if/elif.

---

## 🧪 Evaluación y Métricas

### Criterios de Evaluación para Capstone

✅ **Funcionalidad del Sistema RAG**
- Recuperación correcta de documentos relevantes
- Generación de respuestas coherentes y precisas

✅ **Innovación: Arquitectura Multi-Agente**
- Clasificación dual (categoría + tipo búsqueda)
- Especialización por dominios
- Síntesis de respuestas múltiples

✅ **Búsqueda Híbrida**
- Semántica: Embeddings y similitud vectorial
- Léxica: Búsqueda literal con regex optimizado

✅ **Optimizaciones Técnicas**
- Singleton pattern para ChromaDB
- Regex precompilados
- Funciones auxiliares DRY

✅ **Interfaz y UX**
- UI intuitiva con Gradio
- Configuraciones visibles al usuario
- Feedback claro (categoría, fuentes)

---

## 📝 Limitaciones Conocidas

1. **Búsqueda léxica básica**: No soporta regex complejos del usuario
2. **Sin historial persistente**: El chat no guarda conversaciones entre sesiones
3. **Dependencia de OpenAI**: Requiere conexión a internet y API key válida
4. **Sin evaluación de calidad**: No hay métricas automáticas de precisión

---

## 🔮 Mejoras Futuras

- [ ] Implementar sistema de feedback del usuario (thumbs up/down)
- [ ] Añadir métricas de evaluación automática (precisión, recall)
- [ ] Soporte para más formatos de documentos (PDF, DOCX)
- [ ] Sistema de caché de respuestas frecuentes
- [ ] Interfaz multiidioma
- [ ] Historial de conversaciones persistente
- [ ] Fine-tuning del modelo con datos específicos de ScanGasto

---

## 👥 Créditos

**Proyecto Capstone - RAG Híbrido Multi-Agente de documentación**  

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico para fines educativos.

---

## 📞 Soporte

Para preguntas sobre el proyecto:
- 📧 Email: angelrodriguezminguela@gmail.com
- 📂 Repositorio: https://github.com/arodriguezminguela/Capstone-ScanGestor

---

**¡Gracias por revisar este proyecto!** 🎓
