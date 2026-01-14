# PLAN DE GESTIÓN DEL PROYECTO (PMP)
**Proyecto:** App Móvil "ScanGasto"
**Cliente:** Gestoría Future S.L.
**Proveedor:** DevSolutions S.L.
**Fecha de Creación:** 16 de Octubre de 2025
**Versión:** 1.0

---

## 1. ORGANIGRAMA Y PERSONAS DE CONTACTO

Para garantizar una comunicación fluida, se establece la siguiente matriz de interlocutores válidos:

### 1.1 Por parte del Cliente (Gestoría Future)
| Rol | Nombre | Email | Responsabilidad |
| :--- | :--- | :--- | :--- |
| **Product Owner (PO)** | Carlos Financiero | c.financiero@future.com | Definición de requisitos y validación final (Aprobador). |
| **Responsable IT** | Laura Sistemas | l.sistemas@future.com | Accesos a servidores, validación de seguridad y despliegue. |
| **Usuario Clave** | María Contable | m.contable@future.com | Beta tester principal. Valida la usabilidad. |

### 1.2 Por parte del Proveedor (DevSolutions)
| Rol | Nombre | Email | Responsabilidad |
| :--- | :--- | :--- | :--- |
| **Jefe de Proyecto (PM)**| Ana Manager | ana.m@devsolutions.com | Gestión de alcance, plazos, costes e interlocución única. |
| **Tech Lead** | David Arquitecto | david.a@devsolutions.com | Decisiones técnicas, diseño de API y supervisión de código. |

---

## 2. EQUIPO DE TRABAJO, CATEGORÍAS Y TARIFAS

El proyecto se ejecutará bajo la modalidad de **Precio Cerrado** basado en una estimación de horas, pero con control interno de imputaciones para asegurar la rentabilidad.

### 2.1 Composición del Equipo (Recursos Humanos)

| Perfil / Categoría | Cantidad | Tarifa (€/h) | Dedicación | Funciones Principales |
| :--- | :--- | :--- | :--- | :--- |
| **Project Manager** | 1 | 65,00 € | 20% | Planificación, reuniones de seguimiento, gestión de riesgos. |
| **Senior Backend Dev** | 1 | 55,00 € | 100% | Desarrollo de API Python, Integración con Google Vision, BBDD. |
| **Senior Mobile Dev** | 1 | 55,00 € | 100% | Desarrollo Flutter (iOS/Android), lógica offline, UI. |
| **Junior Dev / QA** | 1 | 35,00 € | 50% | Tests unitarios, documentación técnica y apoyo en desarrollo. |
| **UX/UI Designer** | 1 | 45,00 € | 15% (Inicio) | Prototipado en Figma, diseño de pantallas y assets gráficos. |

### 2.2 Estimación de Esfuerzo y Coste (Presupuesto)

* **Duración Total Estimada:** 14 semanas (3.5 meses).
* **Total Horas Estimadas:** 720 horas.
* **Presupuesto Total del Proyecto:** 35.500 € + IVA (Aprox).

---

## 3. CONTROL DE GESTIÓN E IMPUTACIÓN INTERNA

### 3.1 Herramienta de Imputación
El equipo técnico imputará sus horas diariamente en la herramienta corporativa **Jira Time Tracking** (o Clockify).

### 3.2 Criterio de Imputación
* **Código de Proyecto:** `PRJ-2025-SCANGASTO`
* **Unidad de Medida:** Fracciones de 15 minutos (0.25h).
* **Conceptos Imputables:** Desarrollo, reuniones internas, reuniones con cliente, diseño, pruebas y despliegue.
* **No Imputables:** Formación interna no relacionada, descansos, desplazamientos (salvo aprobación previa).

---

## 4. PLANIFICACIÓN Y CRONOGRAMA (Roadmap)

El proyecto se divide en 5 fases secuenciales.

### Fase 1: Inception y Diseño (Semanas 1-2)
* Reunión de Kick-off.
* Elaboración de Wireframes y Diseño UI (Figma).
* Aprobación del diseño por parte de Carlos Financiero.

### Fase 2: Configuración Backend y OCR (Semanas 3-6)
* Configuración de servidores AWS y BBDD PostgreSQL.
* Desarrollo de la API de Autenticación.
* Implementación del algoritmo de OCR y parsing de tickets.

### Fase 3: Desarrollo Móvil (Semanas 6-11)
* Maquetación de pantallas en Flutter.
* Integración con la cámara y galería.
* Desarrollo de la lógica Offline (SQLite) y Sincronización.

### Fase 4: QA y UAT (Semanas 12-13)
* Pruebas internas (Unit Testing & Integration).
* Despliegue en entorno de Test (TestFlight / Firebase).
* **UAT (User Acceptance Testing):** El cliente prueba la app real.

### Fase 5: Despliegue y Cierre (Semana 14)
* Subida a Apple Store y Google Play Store.
* Entrega de documentación y código fuente.
* Reunión de Cierre.

---

## 5. GESTIÓN DE LA DOCUMENTACIÓN Y HERRAMIENTAS

Para asegurar que no se pierda información, se establece el siguiente repositorio centralizado:

| Tipo de Info | Herramienta | Ubicación / Acceso | Responsable |
| :--- | :--- | :--- | :--- |
| **Código Fuente** | GitLab | `git.devsolutions.com/scangasto` | Tech Lead |
| **Doc. Funcional** | Confluence | Espacio: `ScanGasto / Documentación` | Project Manager |
| **Diseños UI** | Figma | Enlace compartido al proyecto | UX Designer |
| **Gestión Tareas** | Jira Software | Tablero Kanban `SCANGASTO` | Todo el equipo |
| **Actas Reunión** | SharePoint | Carpeta `Actas y Acuerdos` | Project Manager |

---

## 6. MODELO DE GOBERNANZA (Reuniones)

### 6.1 Reuniones de Seguimiento (Cliente - Proveedor)
* **Frecuencia:** Quincenal (Cada dos viernes a las 10:00).
* **Objetivo:** Demo de avances, validación de dudas funcionales y revisión de riesgos.
* **Formato:** Teams/Zoom (30-45 mins).
* **Entregable:** Acta de reunión enviada por email antes de 24h.

### 6.2 Daily Standup (Interna)
* **Frecuencia:** Diaria (09:15).
* **Objetivo:** ¿Qué hice ayer? ¿Qué haré hoy? ¿Tengo bloqueos?
* **Duración:** Máximo 15 minutos.

---

## 7. POLÍTICA DE VACACIONES Y DISPONIBILIDAD

Dado que el proyecto dura 3.5 meses, es probable que coincida con periodos vacacionales.

### 7.1 Calendario Laboral
Se sigue el calendario laboral de **Madrid**. Los festivos locales del cliente se respetarán (no habrá reuniones esos días), pero el equipo de desarrollo trabajará si no es festivo en su localidad.

### 7.2 Gestión de Ausencias del Equipo
* **Preaviso:** Cualquier vacaciones planificada del equipo técnico debe comunicarse al PM con 15 días de antelación.
* **Backup:**
    * Si el **Senior Backend** falta > 3 días, el **Tech Lead** asumirá sus tareas críticas.
    * Si el **PM** falta, el **Tech Lead** será el interlocutor temporal con el cliente.
* **Protocolo de Handover:** Antes de irse de vacaciones, el recurso debe dejar su código subido (commit & push), las tareas de Jira actualizadas y una breve nota de estado a su backup.

---

## 8. GESTIÓN DE RIESGOS PRELIMINAR

| Riesgo Detectado | Probabilidad | Impacto | Plan de Mitigación |
| :--- | :--- | :--- | :--- |
| Retraso en aprobación de Apple Store | Alta | Medio | Iniciar el proceso de validación de cuenta de desarrollador en la Semana 2. |
| El OCR falla con tickets arrugados | Media | Alto | Implementar botón de "Edición Manual" obligatoria para evitar bloqueos. |
| Cambios de requisitos a mitad de proyecto | Media | Alto | Cualquier cambio fuera del alcance inicial requerirá una **CR (Change Request)** presupuestada aparte. |