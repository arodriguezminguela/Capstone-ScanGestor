# DOCUMENTO DE DISEÑO TÉCNICO (TDD) - PROYECTO SCANGASTO
**Cliente:** Gestoría Future S.L.
**Fecha:** 16 de Octubre de 2025
**Versión:** 2.1 (Technical Deep Dive)
**Autor:** Equipo de Arquitectura de Software

---

## 1. RESUMEN EJECUTIVO Y ALCANCE TÉCNICO
Este documento detalla la implementación de la solución **ScanGasto**. El sistema se construirá bajo una arquitectura de microservicios monolíticos (Modular Monolith) para facilitar el despliegue inicial, separando claramente el Frontend (App Móvil) del Backend (API REST). La solución prioriza la **disponibilidad offline** y la **precisión del dato contable**.

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Diagrama de Componentes
El sistema se compone de cuatro bloques fundamentales:

1.  **Cliente Móvil (Presentation Layer):** Aplicación nativa compilada, responsable de la captura, compresión de imagen y persistencia local.
2.  **API Gateway & Backend (Logic Layer):** Punto de entrada único, gestión de seguridad, orquestación del OCR y lógica de negocio.
3.  **Servicios Externos (Infrastructure Layer):** Google Cloud Vision (OCR) y AWS S3 (Almacenamiento de Blobs).
4.  **Persistencia (Data Layer):** Motor de base de datos relacional.

### 2.2 Estrategia de Despliegue
Todo el backend se contenerizará utilizando **Docker**. Esto asegura que el entorno de desarrollo sea idéntico al de producción.

---

## 3. STACK TECNOLÓGICO DETALLADO

Se han seleccionado las siguientes tecnologías basándose en criterios de mantenibilidad, rendimiento y coste:

### 3.1 Frontend (Aplicación Móvil)
* **Framework:** Flutter (v3.13 o superior) con lenguaje Dart.
* **Gestión de Estado:** BLoC (Business Logic Component) para separar la UI de la lógica de negocio.
* **Persistencia Local:** `sqflite` (SQLite) para guardar metadatos y `path_provider` para guardar imágenes en caché localmente.
* **Red:** `Dio` (Cliente HTTP avanzado con interceptores para gestionar tokens JWT automáticamente).
* **Cámara:** `camera` plugin con configuración de resolución media (1080p) para optimizar el peso sin perder legibilidad.

### 3.2 Backend (Servidor)
* **Lenguaje:** Python 3.11.
* **Framework Web:** FastAPI (Asíncrono, alto rendimiento y generación automática de documentación Swagger).
* **ORM:** SQLAlchemy (Gestión de la BBDD).
* **Validación de Datos:** Pydantic (Garantiza que los JSON de entrada y salida cumplen el esquema estricto).
* **Servidor WSGI:** Uvicorn con Gunicorn como gestor de procesos.

### 3.3 Base de Datos
* **Motor:** PostgreSQL 15.
* **Justificación:** Soporte nativo para tipos JSONB (para guardar la respuesta cruda del OCR) y transacciones ACID robustas.

---

## 4. DESARROLLOS A MEDIDA (CUSTOM LOGIC)

A diferencia de usar soluciones "enlatadas", se desarrollarán módulos específicos para la lógica de negocio de la Gestoría.

### 4.1 Módulo "Intelligent Parser" (Algoritmo de Extracción)
El OCR de Google devuelve "texto bruto". Hemos diseñado un algoritmo de post-procesado en Python que funciona así:

> **Pseudocódigo del Algoritmo de Parsing:**
>
> \# 1. Recibe la lista de líneas de texto de Google Vision
> \# 2. Búsqueda de FECHA:
> \#    - Aplica Regex: (\d{2}[/-]\d{2}[/-]\d{4})
> \#    - Valida que la fecha no sea > FECHA_ACTUAL
>
> \# 3. Búsqueda de IMPORTE TOTAL:
> \#    - Busca palabras clave: "TOTAL", "SUMA", "EUR", "PAGAR"
> \#    - Busca el número decimal más grande que esté en la misma línea vertical (eje Y) que la palabra clave.
>
> \# 4. Búsqueda de NIF/CIF:
> \#    - Aplica algoritmo de validación (Módulo del dígito de control español) para descartar falsos positivos.

### 4.2 Módulo "SyncManager" (Sincronización Offline)
Desarrollo en Flutter que gestiona la cola de subida:
1.  Escucha cambios en la conectividad (`connectivity_plus`).
2.  Cuando hay red, consulta la tabla local `pending_uploads`.
3.  Implementa un patrón de **Reintento Exponencial** (Exponential Backoff): Si falla la subida, espera 2s, luego 4s, luego 8s...

---

## 5. DISEÑO DE BASE DE DATOS (ESQUEMA FÍSICO)

A continuación se presenta el DDL (Data Definition Language).
*Nota: Se usan comentarios (--) para proteger el formato.*

> -- TABLA DE USUARIOS (Seguridad)
> -- CREATE TABLE users (
> --     id SERIAL PRIMARY KEY,
> --     email VARCHAR(255) UNIQUE NOT NULL,
> --     hashed_password VARCHAR(255) NOT NULL,
> --     role VARCHAR(50) DEFAULT 'EMPLOYEE',
> --     created_at TIMESTAMP DEFAULT NOW()
> -- );
>
> -- TABLA DE GASTOS (Core del Negocio)
> -- CREATE TABLE expenses (
> --     id UUID PRIMARY KEY,
> --     user_id INTEGER REFERENCES users(id),
> --     merchant_name VARCHAR(150),
> --     merchant_tax_id VARCHAR(20), -- CIF
> --     total_amount DECIMAL(10, 2) NOT NULL,
> --     tax_amount DECIMAL(10, 2),
> --     category VARCHAR(50) NOT NULL,
> --     expense_date DATE NOT NULL,
> --     image_url VARCHAR(500), -- URL en S3
> --     ocr_raw_data JSONB, -- Respuesta completa del OCR para auditoría futura
> --     status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
> --     sync_status VARCHAR(20) DEFAULT 'SYNCED',
> --     created_at TIMESTAMP DEFAULT NOW()
> -- );
>
> -- TABLA DE AUDITORÍA (Logs)
> -- CREATE TABLE audit_logs (
> --     id SERIAL PRIMARY KEY,
> --     expense_id UUID REFERENCES expenses(id),
> --     action VARCHAR(50), -- EJ: 'OCR_CORRECTION'
> --     old_value TEXT,
> --     new_value TEXT,
> --     timestamp TIMESTAMP DEFAULT NOW()
> -- );

---

## 6. DEFINICIÓN DE INTERFACES (API REST)

El backend expondrá los siguientes endpoints documentados vía OpenAPI.

### Endpoint: Procesar Imagen (OCR)
Analiza la imagen pero NO guarda el gasto definitivamente.

> **Método:** POST
> **Ruta:** /api/v1/ocr/scan
> **Headers:** Authorization: Bearer <token_jwt>
> **Body:** Form-Data (file: binary_image)

**Respuesta Técnica (JSON):**
> // {
> //   "success": true,
> //   "data": {
> //     "detected_date": "2025-10-15",
> //     "detected_total": 12.50,
> //     "detected_merchant": "STARBUCKS COFFEE",
> //     "confidence_score": 0.98,
> //     "temp_image_id": "temp_8823_xhz.jpg"
> //   }
> // }

### Endpoint: Crear Gasto (Persistencia)
Guarda el gasto validado por el humano.

> **Método:** POST
> **Ruta:** /api/v1/expenses
> **Body:** JSON Raw

**Payload de Entrada:**
> // {
> //   "temp_image_id": "temp_8823_xhz.jpg",
> //   "confirmed_total": 12.50,
> //   "confirmed_date": "2025-10-15",
> //   "category": "DIETAS",
> //   "notes": "Desayuno cliente proyecto Alpha"
> // }

---

## 7. PARAMETRIZACIÓN Y CONFIGURACIÓN

El sistema no debe tener "números mágicos" ni credenciales en el código fuente. Se utilizará un archivo `.env` que se inyectará en tiempo de ejecución.

### Variables de Entorno (Backend)

| Variable | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `DB_HOST` | Host de PostgreSQL | `db-prod.scangasto.internal` |
| `DB_PORT` | Puerto de conexión | `5432` |
| `SECRET_KEY` | Semilla para firmar JWT | `v3ry_s3cr3t_k3y_99!` |
| `AWS_ACCESS_KEY` | Credencial S3 | `AKIAIOSFODNN7EXAMPLE` |
| `OCR_PROVIDER` | Selector de motor | `GOOGLE_VISION_V1` |
| `MAX_UPLOAD_SIZE`| Límite en Megabytes | `5` |

### Configuraciones de la App Móvil
Se usará un archivo `config.dart` excluido del repositorio git para:
* `API_BASE_URL`: `https://api.scangasto.com`
* `TIMEOUT_MS`: `15000` (15 segundos de espera máxima).

---

## 8. SEGURIDAD

1.  **Cifrado en reposo:** La base de datos PostgreSQL tendrá activado el cifrado de disco (TDE).
2.  **Cifrado en tránsito:** Uso forzoso de TLS 1.2+.
3.  **URLs Firmadas:** Las imágenes en S3 no serán públicas. El backend generará una "Pre-signed URL" válida solo por 10 minutos cuando el usuario quiera ver la foto del ticket.
4.  **Sanitización:** Uso de Pydantic para evitar inyección SQL e inyección de comandos en los campos de texto libre.