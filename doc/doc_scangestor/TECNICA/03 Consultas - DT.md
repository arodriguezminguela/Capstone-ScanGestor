# ANEXO TÉCNICO II: MÓDULO DE ANALÍTICA Y REPORTING
**Proyecto:** ScanGasto
**Referencia:** Addendum al TDD v2.2
**Componentes:** BI Engine, Charting UI, PDF Generator
**Fecha:** 19 de Octubre de 2025
**Autor:** Equipo de Arquitectura y Datos

---

## 1. ESTRATEGIA DE ARQUITECTURA: SERVER-SIDE AGGREGATION

Para la implementación de los gráficos, se descarta realizar los cálculos matemáticos en el dispositivo móvil. Se adopta una estrategia de **Agregación en el Servidor**.

### 1.1 Justificación Técnica
1.  **Eficiencia de Red:** En lugar de enviar 500 registros de gastos completos al móvil para que este los sume, el servidor ejecuta una consulta `GROUP BY` y envía solo 5 o 6 puntos de datos (ej: `{"Transporte": 150}`). Esto reduce el payload JSON en un 95%.
2.  **Consistencia:** Garantiza que el total que ve el usuario es exactamente el mismo (al céntimo) que se reporta en el PDF, ya que ambos usan la misma lógica centralizada en Python.
3.  **Batería:** Reduce el consumo de CPU en el cliente móvil al evitar iteraciones sobre listas grandes.

### 1.2 Flujo de Datos (Data Flow)
1.  **App:** Solicita métricas para un rango de fechas (`start_date`, `end_date`).
2.  **API:** Recibe la petición y valida el rango.
3.  **DB:** Ejecuta consultas de agregación (SUM, AVG, COUNT) sobre la tabla `gastos`.
4.  **API:** Estructura los datos en formato compatible con la librería de gráficos.
5.  **App:** Renderiza los vectores visuales.

---

## 2. STACK TECNOLÓGICO (ESPECÍFICO DEL MÓDULO)

### 2.1 Frontend (Visualización)
* **Librería Gráfica:** `fl_chart` (Paquete oficial de Flutter para gráficos vectoriales).
    * *Uso:* `PieChart` para categorías y `BarChart` para evolución diaria.
* **Gestión de Estado:** `Bloc` específico (`AnalyticsBloc`) que mantiene en memoria el mes seleccionado y el filtro activo (drill-down).

### 2.2 Backend (Procesamiento y Exportación)
* **Motor de Reportes:** `Jinja2` + `WeasyPrint`.
    * *Flujo:* Se diseña el reporte en HTML/CSS (fácil de maquetar) usando plantillas Jinja2, y WeasyPrint lo renderiza a PDF con calidad de impresión. Es superior a librerías de dibujo "pixel a pixel" como ReportLab por su mantenibilidad.
* **Manipulación de Datos:** `Pandas` (Python Data Analysis Library).
    * *Uso:* Opcional, pero recomendado si se requiere realizar cálculos complejos de proyecciones o medias móviles en el futuro. Para la fase actual, SQL nativo es suficiente.

---

## 3. DISEÑO DE BASE DE DATOS (OPTIMIZACIÓN)

Las consultas de analítica son pesadas. Para asegurar que la pantalla cargue en < 1 segundo, se requieren índices específicos.

### 3.1 Índices Compuestos
Se deben crear índices que cubran las columnas de filtrado (fecha, usuario) y agrupación (categoría).

> -- ÍNDICE DE RENDIMIENTO PARA REPORTES
> -- CREATE INDEX idx_analytics_fast_access
> -- ON gastos (id_usuario, fecha_ticket, estado_validacion);
> --
> -- Explicación: Permite al motor de BBDD filtrar rápidamente los gastos de UN usuario
> -- en UN mes específico que NO estén rechazados, sin escanear toda la tabla.

### 3.2 Vista SQL Materializada (Opcional para alto volumen)
Si el volumen de datos crece (> 1 millón de filas), se propone el uso de una **Vista Materializada** que se actualice cada noche. Para el alcance actual (trabajo universitario), bastará con consultas directas.

---

## 4. ESPECIFICACIÓN API REST (ENDPOINTS DE BI)

Se definen dos nuevos endpoints de lectura.

### 4.1 Endpoint: Obtener Datos del Dashboard
Devuelve toda la información necesaria para pintar la pantalla de una sola vez (Patrón *Composite Response*).

* **Método:** `GET`
* **Ruta:** `/api/v1/analytics/dashboard`
* **Query Params:** `?month=10&year=2025`

**Respuesta JSON (Estructura optimizada para UI):**

> // {
> //   "meta": {
> //     "currency": "EUR",
> //     "period": "2025-10"
> //   },
> //   "kpis": {
> //     "total_spend": 1250.50,
> //     "total_vat": 210.00,
> //     "avg_ticket": 45.00
> //   },
> //   "chart_data": {
> //     "by_category": [
> //       {"label": "Transporte", "value": 450.00, "color": "#FF5733", "id": 1},
> //       {"label": "Comida", "value": 300.00, "color": "#33FF57", "id": 2},
> //       {"label": "Otros", "value": 500.50, "color": "#3357FF", "id": 99}
> //     ],
> //     "daily_evolution": [
> //       {"day": 1, "amount": 0},
> //       {"day": 2, "amount": 50.00},
> //       // ... hasta día 31
> //     ]
> //   },
> //   "raw_list_subset": [
> //      // Lista ligera de gastos del mes para el listado inferior
> //      {"id": "uuid...", "merchant": "Repsol", "amount": 50.00, "cat_id": 1}
> //   ]
> // }

### 4.2 Endpoint: Descargar Informe PDF
Genera el binario al vuelo.

* **Método:** `GET`
* **Ruta:** `/api/v1/analytics/export/pdf`
* **Query Params:** `?month=10&year=2025`
* **Response Header:** `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="reporte_oct_2025.pdf"`

---

## 5. LÓGICA DE AGREGACIÓN (BACKEND)

Implementación de las consultas SQL usando SQLAlchemy.

### 5.1 Consulta de Distribución por Categoría

> -- Pseudocódigo SQL para el gráfico de Donut
> -- SELECT
> --     c.nombre as categoria,
> --     SUM(g.importe_total) as total
> -- FROM gastos g
> -- JOIN categorias c ON g.id_categoria = c.id
> -- WHERE
> --     g.id_usuario = :user_id
> --     AND g.fecha_ticket BETWEEN :start_date AND :end_date
> --     AND g.estado_validacion != 'RECHAZADO' -- Importante: Excluir rechazados
> -- GROUP BY c.nombre
> -- ORDER BY total DESC;

### 5.2 Lógica de "Unificación de Orígenes"
Tal como se definió en el funcional, esta consulta **ignora** la columna `origen_dato` (OCR o QR). Al hacer el `SUM(importe_total)`, suma indistintamente si el gasto vino de una foto o de un escaneo digital, cumpliendo el requisito de unificación transparente.

---

## 6. GENERACIÓN DE PDF (DETALLE TÉCNICO)

Para cumplir con el requisito de incluir las fotos en el PDF, el backend debe realizar una orquestación compleja:

1.  **Fetch Data:** Obtener los datos de gastos de la BBDD.
2.  **Fetch Assets:** Descargar temporalmente las imágenes de los tickets desde AWS S3 (usando las URLs firmadas) a una carpeta temporal `/tmp` del servidor.
3.  **Render HTML:** Inyectar los datos y las rutas de las imágenes locales en la plantilla HTML (`report_template.html`).
4.  **Convert to PDF:** WeasyPrint toma el HTML y genera el PDF.
5.  **Cleanup:** Borrar las imágenes temporales de `/tmp`.
6.  **Serve:** Enviar el PDF al usuario.

---

## 7. PLAN DE PRUEBAS DEL MÓDULO (QA)

### 7.1 Pruebas de Datos (Backend)
* **Test de Frontera:** Pedir reporte de un mes que aún no ha empezado (debe devolver array vacío, no error 500).
* **Test de Precisión:** Crear manualment 3 gastos de 10€, 20€ y 30€. Verificar que el endpoint `dashboard` devuelve `total_spend: 60.00` exactos.
* **Test de Exclusión:** Marcar el gasto de 20€ como "RECHAZADO". Verificar que el total baja a 40.00€.

### 7.2 Pruebas de Interfaz (Frontend)
* **Test de Drill-down:** Tocar la sección "Comida" y verificar que la lista inferior reduce su número de elementos.
* **Test de Estrés Gráfico:** Cargar un mes con 500 tickets para verificar que la animación del gráfico no "congela" la pantalla (debe mantener 60 FPS).