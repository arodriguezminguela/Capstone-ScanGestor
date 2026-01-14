# ANEXO TÉCNICO I: IMPLEMENTACIÓN DE LECTURA QR Y FACTURA DIGITAL
**Proyecto:** ScanGasto
**Referencia:** Addendum al TDD v2.1
**Módulo:** QR Parser & Digital Fetcher
**Fecha:** 17 de Octubre de 2025
**Autor:** Equipo de Arquitectura

---

## 1. ARQUITECTURA DE LA SOLUCIÓN HÍBRIDA

La inclusión de la lectura QR introduce un nuevo flujo de entrada de datos que convive con el OCR. A nivel arquitectónico, desplazamos la carga de procesamiento:
* **En OCR:** La carga está en el post-procesado de imagen (Computer Vision).
* **En QR:** La carga está en la lógica de conexión y *scraping* (Obtención de documentos remotos).

### 1.1 Diagrama de Flujo de Datos (Data Flow)



1.  **Mobile App:** Detecta patrón QR en el stream de video.
2.  **Mobile App:** Envía la cadena cruda (`raw_string`) al Backend.
3.  **Backend (Router):** Analiza la cadena:
    * ¿Es URL? -> Invoca al **Downloader Service**.
    * ¿Es Texto Estructurado (TicketBAI)? -> Invoca al **Parser Service**.
4.  **Downloader Service:** Intenta descargar el PDF/JPG desde la URL del proveedor.
5.  **Backend:** Devuelve al móvil el JSON con los datos + el estado del archivo (¿Descargado o requiere foto?).

---

## 2. MODIFICACIONES EN EL STACK TECNOLÓGICO

Para soportar esta funcionalidad, se añaden las siguientes librerías y componentes:

### 2.1 Frontend (Flutter)
* **Librería de Escaneo:** `mobile_scanner` (Versión 3.x+).
    * *Justificación:* Utiliza la API nativa `MLKit` (Android) y `Vision` (iOS) para una detección ultrarrápida sin congelar la UI.
* **Feedback Háptico:** `vibration` (Para confirmar lectura sin sonido).

### 2.2 Backend (Python)
* **Cliente HTTP Asíncrono:** `httpx`.
    * *Justificación:* Necesario para descargar los PDFs de las URLs de los QR de forma no bloqueante. Soporta HTTP/2.
* **Generación de QR (Opcional):** `qrcode` (En caso de querer exportar datos).
* **Librería PDF:** `PyPDF2` o `pdfminer`.
    * *Justificación:* Si descargamos un PDF digital, podemos leer el texto interno directamente (mucho más fiable que OCR de imagen).

---

## 3. LÓGICA DEL "SMART PARSER" (Backend)

Este es el núcleo de la nueva funcionalidad. El backend debe decidir qué hacer con el texto que le llega del QR.

> **Pseudocódigo del Algoritmo de Decisión:**
>
> // def process_qr_data(raw_data: str):
> //    # CASO 1: ES TICKETBAI (País Vasco)
> //    # Formato: TBAI-CIF-Fecha-Hora-Firma-Importe...
> //    if raw_data.startswith("TBAI") or "ticketbai" in raw_data.lower():
> //        return parse_ticketbai(raw_data)
> //
> //    # CASO 2: ES UNA URL (Factura Web)
> //    elif validators.url(raw_data):
> //        # Intentar descargar el archivo (Headless)
> //        file_blob = download_file(raw_data)
> //        if file_blob.is_pdf():
> //            data = extract_text_from_pdf(file_blob)
> //            return {"type": "DIGITAL_DOWNLOAD", "file": file_blob, "data": data}
> //        else:
> //            # Es una URL pero no devuelve archivo directo (ej: Login requerido)
> //            # Extraemos parámetros de la URL (?total=50&date=2025...)
> //            data = extract_params_from_url(raw_data)
> //            return {"type": "DATA_ONLY", "data": data} # Requiere foto manual
> //
> //    # CASO 3: TEXTO DESCONOCIDO
> //    else:
> //        return {"error": "Format not supported", "action": "FORCE_PHOTO"}

---

## 4. ESPECIFICACIÓN API REST (Nuevos Endpoints)

Se añade un endpoint específico para el análisis de QR, separado del análisis de imagen OCR.

### Endpoint: Analizar QR
`POST /api/v1/qr/analyze`

**Request (JSON):**
> // {
> //   "raw_content": "https://www.repsol.com/facturas?id=A123&amount=45.50&date=20251017",
> //   "geolocation": {"lat": 40.416, "lng": -3.703}
> // }

**Response A (Éxito - Documento Descargado):**
> // {
> //   "status": "COMPLETE",
> //   "message": "Factura digital descargada con éxito.",
> //   "data": {
> //     "merchant": "Repsol S.A.",
> //     "total": 45.50,
> //     "date": "2025-10-17",
> //     "file_url": "https://s3.aws.../factura_digital_123.pdf"
> //   },
> //   "action_required": "REVIEW_ONLY" // No pide foto
> // }

**Response B (Éxito Parcial - Solo Datos):**
> // {
> //   "status": "PARTIAL",
> //   "message": "Datos leídos. Se requiere foto del ticket.",
> //   "data": {
> //     "merchant": "Restaurante Desconocido",
> //     "total": 12.00,
> //     "date": "2025-10-17"
> //   },
> //   "action_required": "TAKE_PHOTO" // Abre cámara
> // }

---

## 5. ACTUALIZACIÓN DEL MODELO DE DATOS (SQL)

Se modifica la tabla `gastos` para asegurar la trazabilidad del origen del dato (Auditoría Fiscal).

> -- ALTER TABLE expenses ADD COLUMN data_source VARCHAR(20) DEFAULT 'OCR';
> -- -- Valores posibles: 'OCR', 'QR_URL', 'QR_DATA', 'MANUAL'
>
> -- ALTER TABLE expenses ADD COLUMN qr_raw_string TEXT;
> -- -- Para guardar la cadena original en caso de inspección
>
> -- ALTER TABLE expenses ADD COLUMN document_type VARCHAR(10) DEFAULT 'IMAGE';
> -- -- Valores posibles: 'IMAGE' (Foto), 'PDF' (Digital)

---

## 6. SEGURIDAD Y MANEJO DE RIESGOS EN DESCARGAS

Al permitir que el servidor descargue archivos de URLs arbitrarias (las que vienen en el QR), debemos protegernos contra ataques SSRF (Server-Side Request Forgery) y archivos maliciosos.

### 6.1 Validaciones de Seguridad (Downloader Service)
1.  **Límite de Tamaño:** El servidor abortará cualquier descarga que supere los 5MB (`Content-Length > 5*1024*1024`).
2.  **Timeout Estricto:** Máximo 5 segundos para conectar y 10 para descargar. Si tarda más, se aborta y se pide foto manual al usuario.
3.  **Validación de Mime-Type:** Solo se procesarán cabeceras `Content-Type` que sean `application/pdf`, `image/jpeg` o `image/png`. Se rechazarán `.exe`, `.zip`, etc.
4.  **User-Agent Personalizado:** Se configurará la petición con un User-Agent `ScanGasto-Bot/1.0` para identificarnos ante los servidores de los proveedores.

---

## 7. DETALLES DE IMPLEMENTACIÓN FLUTTER (Snippets)

Lógica para la gestión del escáner en el móvil.

> **Configuración del controlador:**
> // MobileScannerController controller = MobileScannerController(
> //   detectionSpeed: DetectionSpeed.normal,
> //   facing: CameraFacing.back,
> //   torchEnabled: false,
> // );
>
> **Callback de Detección:**
> // onDetect: (capture) {
> //   final List<Barcode> barcodes = capture.barcodes;
> //   if (barcodes.isNotEmpty) {
> //      controller.stop(); // Importante: Parar cámara para no enviar 50 peticiones
> //      _sendQrToBackend(barcodes.first.rawValue);
> //   }
> // }