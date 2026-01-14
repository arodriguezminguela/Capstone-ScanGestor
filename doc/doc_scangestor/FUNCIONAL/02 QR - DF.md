# ANEXO I: DISEÑO FUNCIONAL - MÓDULO DE LECTURA QR
**Proyecto:** ScanGasto - Fase de Mejora
**Funcionalidad:** Captura de datos mediante Códigos QR (TicketBAI / Factura-e)
**Fecha:** 17 de Octubre de 2025
**Estado:** Pendiente de Aprobación

---

## 1. INTRODUCCIÓN Y JUSTIFICACIÓN
### 1.1 Necesidad Detectada
Los usuarios reportan que un porcentaje creciente de tickets (supermercados, gasolineras, restaurantes de franquicia) incluyen un código QR. El sistema actual de OCR, aunque efectivo, requiere validación manual y depende de la calidad de la foto y la iluminación.

### 1.2 Objetivo de la Mejora
Implementar un lector de códigos QR nativo en la cámara de la App que permita:
1.  **Lectura Instantánea:** Obtener los datos (Fecha, Importe, NIF, ID Factura) directamente del código QR.
2.  **Precisión Total:** Eliminar los errores de lectura del OCR (confusión de 1 con I, 8 con B, etc.).
3.  **Descarga Digital:** Si el QR contiene una URL a la factura digital, descargar el documento automáticamente, eximiendo al usuario de tomar la fotografía física.

---

## 2. NUEVO FLUJO DE USUARIO (User Journey)

El flujo de captura se modifica para ser híbrido (Inteligente).

1.  **Apertura:** El usuario pulsa el botón "+" (Capturar Gasto).
2.  **Detección Automática:**
    * La cámara se abre. El sistema busca simultáneamente **bordes de documento** (para foto estándar) y **códigos QR**.
    * *Feedback UI:* Si detecta un QR, aparece un marco verde sobre el código y vibra suavemente.
3.  **Captura QR:** El usuario no necesita pulsar el disparador; al estabilizarse el QR, la app lo lee automáticamente.
4.  **Decisión del Sistema (Lógica de Negocio):**
    * **CASO A (QR con URL de descarga):** El sistema accede a la URL, descarga el PDF del ticket y extrae los metadatos.
        * *Resultado:* El usuario ve el formulario rellenado y el PDF adjunto. **No hace falta foto.**
    * **CASO B (QR solo con datos):** El sistema rellena el formulario (Importe, Fecha, CIF) pero detecta que falta la imagen de soporte.
        * *Resultado:* La app muestra el mensaje: *"Datos leídos con éxito. Por favor, toma la foto del ticket para el archivo fiscal"* y vuelve a la cámara para hacer la foto del papel.

---

## 3. REQUISITOS FUNCIONALES DETALLADOS

### 3.1 RF-QR-01: Detección y Lectura
* **Descripción:** El módulo de cámara debe ser capaz de escanear códigos QR estándar y códigos DataMatrix (usados en algunos tickets farmacéuticos).
* **Comportamiento:** La lectura debe realizarse en menos de 200ms una vez enfocado.

### 3.2 RF-QR-02: Parsing de Formatos Estándar
El sistema debe incluir un "Parser" (analizador) capaz de interpretar las cadenas de texto de los QR más comunes en España:

* **Formato TicketBAI:** `TBAI-Código-Fecha-Importe...`
* **Formato URL Simple:** `https://portal-cliente.repsol.com/factura?id=12345&total=50.00`
* **Formato Texto Plano:** `20251017|B12345678|50.00|EUR`

### 3.3 RF-QR-03: Descarga de Documento (Headless Browser)
* Si el QR es una URL, el backend intentará hacer un `GET` a dicha dirección.
* Si la respuesta es un archivo (`application/pdf` o `image/jpeg`), se guardará automáticamente como justificante del gasto.
* Si la URL lleva a una web que requiere navegación, el sistema marcará el gasto como "Datos obtenidos, requiere foto manual".

### 3.4 RF-QR-04: Prioridad de Datos
Si se escanea un QR, los datos obtenidos de este tendrán **prioridad absoluta** sobre el OCR. El campo "Importe Total" será inamovible (read-only) por defecto, salvo que el usuario active un modo de "Forzar Edición" (para casos de propinas no incluidas en el QR).

---

## 4. IMPACTO EN INTERFAZ DE USUARIO (UI)

### 4.1 Pantalla de Cámara
* **Overlay:** Se añade un recuadro translúcido en el centro con el icono de QR parpadeando.
* **Toggle Manual:** Un interruptor "Modo Escáner" / "Modo Foto" (aunque por defecto será automático).

### 4.2 Pantalla de Validación (Formulario)
Se añaden indicadores de origen del dato para dar confianza al usuario:

* Al lado del campo "Importe Total", aparecerá un icono de escudo verde ✅ con el texto *"Dato certificado por QR"*.
* Si se descargó el PDF, en lugar de la foto recortada, se mostrará un icono de PDF con el nombre del archivo y un botón "Visualizar documento original".

---

## 5. IMPACTO EN MODELO DE DATOS Y PERSISTENCIA

Es necesario modificar la base de datos para diferenciar gastos digitalizados por foto vs. gastos por QR.

### 5.1 Nuevos Campos en Tabla `gastos`

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `origen_dato` | ENUM | Valores: `OCR`, `QR_DATA`, `QR_URL`, `MANUAL`. |
| `cadena_qr_raw` | TEXT | Texto crudo leído del QR (para auditoría). |
| `tipo_archivo` | VARCHAR | `JPG` (foto) o `PDF` (descarga digital). |

---

## 6. CASOS DE USO ESPECÍFICOS

### Caso 1: Ticket de Gasolinera (QR Enlace)
1.  Usuario escanea QR.
2.  App detecta URL: `https://gasolinera.com/ticket/v123`.
3.  App descarga el PDF de esa URL en segundo plano.
4.  App parsea los parámetros de la URL para sacar el importe (45.00€).
5.  Usuario ve: Formulario relleno y PDF adjunto. **Acción: Solo pulsar "Guardar".**

### Caso 2: Ticket de Supermercado (QR TicketBAI - Solo Datos)
1.  Usuario escanea QR TBAI.
2.  App extrae: Fecha, Hora, CIF comercio e Importe exacto.
3.  App comprueba que NO hay URL de descarga de imagen.
4.  App muestra alerta: *"Datos capturados. Por favor, fotografía el ticket físico"*.
5.  Usuario hace la foto (ya no importa que salga borrosa la letra, solo se necesita la imagen general, los datos ya están metidos).

---

