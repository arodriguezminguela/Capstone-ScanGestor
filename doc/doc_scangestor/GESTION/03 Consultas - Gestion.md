# ANEXO PMP II: GESTIÓN DE AMPLIACIÓN (MÓDULO BI & REPORTING)
**Proyecto Principal:** App "ScanGasto"
**Referencia:** Change Request CR-002 (Analítica)
**Cliente:** Gestoría Future S.L.
**Proveedor:** DevSolutions S.L.
**Fecha:** 19 de Octubre de 2025

---

## 1. RESUMEN EJECUTIVO
Este documento define el alcance, costes y plazos para la implementación del **Módulo de Inteligencia de Negocio (BI)**.
Esta funcionalidad transformará la aplicación de una herramienta de captura a una herramienta de gestión. Debido a la carga de diseño visual y lógica de generación de PDFs, se gestionará como un **Paquete de Trabajo (WP)** de 3 semanas.

---

## 2. EQUIPO DE TRABAJO Y ESTIMACIÓN ECONÓMICA

Para este módulo, el perfil de **UX/UI Designer** cobra especial relevancia, ya que la visualización de datos requiere un diseño cuidadoso para ser legible en pantallas móviles.

### 2.1 Desglose de Esfuerzo

| Perfil | Tareas Clave (Módulo BI) | Horas | Tarifa (€/h) | Coste |
| :--- | :--- | :--- | :--- | :--- |
| **Project Manager** | Definición de KPIs con cliente, revisión de maquetas. | 8 h | 65,00 € | 520,00 € |
| **UX/UI Designer** | Diseño de Dashboard, paleta de colores para gráficos, diseño de plantilla PDF. | 12 h | 45,00 € | 540,00 € |
| **Senior Mobile Dev** | Implementación de librería de gráficos, animaciones y filtros. | 35 h | 55,00 € | 1.925,00 € |
| **Senior Backend Dev** | Consultas SQL complejas (Agregación), Motor de PDF (WeasyPrint). | 40 h | 55,00 € | 2.200,00 € |
| **QA Tester** | Validación numérica (que los gráficos sumen bien) y revisión visual del PDF. | 10 h | 35,00 € | 350,00 € |
| **TOTAL** | | **105 Horas** | | **5.535,00 €** |

---

## 3. PLANIFICACIÓN (CRONOGRAMA DE 3 SEMANAS)

A diferencia del módulo QR (que era muy técnico), este módulo tiene una fuerte carga visual y de "backend pesado".

### Semana 1: Diseño y Datos (Cimientos)
* **Lunes:** Reunión de definición de KPIs. ¿Qué métricas exactas quiere ver el Director Financiero?
* **Martes-Miércoles:** (Diseño) Maquetación del Dashboard y del PDF corporativo. (Backend) Creación de índices en BBDD y consultas SQL de prueba.
* **Jueves-Viernes:** Aprobación de diseños. Inicio de implementación de endpoints API.

### Semana 2: Implementación Core
* **Lunes-Miércoles:** (Backend) Desarrollo del motor de generación de PDF con inyección de imágenes.
* **Jueves-Viernes:** (Mobile) Integración de la librería de gráficos (`fl_chart`). Conexión con API para pintar datos reales.

### Semana 3: Refinamiento y Entrega
* **Lunes:** Implementación de interactividad (Drill-down: tocar gráfico para filtrar lista).
* **Martes:** (QA) Pruebas de estrés: Generar PDFs con +100 tickets para verificar tiempos de respuesta.
* **Miércoles:** Corrección de errores visuales (ajustes de márgenes, colores).
* **Jueves:** Despliegue en entorno de PRE-Producción.
* **Viernes:** Sesión de **UAT (User Acceptance Testing)** con el cliente.

---

## 4. CONTROL DE GESTIÓN

### 4.1 Imputación Interna
Se crea una nueva línea de proyecto para aislar la rentabilidad de este módulo.

* **Código de Imputación:** `CR-02-ANALYTICS`
* **Concepto en Factura:** "Desarrollo de Módulo de Visualización de Datos y Exportación Documental".

### 4.2 Entregables Documentales
* **Manual de Interpretación:** Breve guía (PDF) explicando cómo se calculan los KPIs (ej: aclarar que el IVA mostrado es la suma de cuotas devengadas).
* **Plantilla HTML:** Se entregará al cliente el código fuente de la plantilla del reporte (`report_template.html`) por si desean cambiar el logo en el futuro.

---

## 5. INTERLOCUTORES Y COMUNICACIÓN

Se requiere una validación extra por parte del departamento de Marketing/Branding del cliente, ya que el PDF generado llevará la imagen corporativa.

### 5.1 Reuniones Específicas
| Reunión | Fecha | Asistentes | Objetivo |
| :--- | :--- | :--- | :--- |
| **Definición de KPIs** | Inicio Sem 1 | PM, Carlos F. (Cliente) | Cerrar la lista de métricas. |
| **Revisión de PDF** | Fin Sem 1 | PM, Designer, Laura Mkt. | Validar que el PDF cumple el manual de marca. |
| **Cierre y Demo** | Fin Sem 3 | Todos | Entrega funcional. |

---

## 6. GESTIÓN DE RIESGOS (Módulo BI)

Los riesgos aquí son principalmente de rendimiento y coherencia de datos.

| Riesgo | Probabilidad | Impacto | Plan de Mitigación |
| :--- | :--- | :--- | :--- |
| **Lentitud en PDF** | Alta | Medio | Si el usuario tiene muchos tickets, el PDF puede tardar 30s en generarse. **Mitigación:** Implementar una cola asíncrona (Celery) si tarda >10s, enviando el PDF por email en vez de descarga directa. |
| **Datos Incoherentes** | Media | Alto | Que el gráfico diga "100€" y la lista sume "99€" por redondeos. **Mitigación:** Usar siempre tipos `DECIMAL` en BBDD y aplicar la misma lógica de redondeo en Backend y Frontend. |
| **Gráficos "Feos"** | Media | Bajo | Si hay muchas categorías pequeñas, el gráfico de tarta se vuelve ilegible. **Mitigación:** Agrupar automáticamente categorías menores en "Otros" si superan el número de 5. |

---

## 7. HITOS DE FACTURACIÓN (Pago)

Al ser un cambio con un presupuesto considerable (>5.000€), se acuerda un plan de pagos específico para este anexo:

1.  **50% a la firma** de este documento (Inicio de los trabajos).
2.  **50% a la entrega** y aceptación en la reunión de UAT.