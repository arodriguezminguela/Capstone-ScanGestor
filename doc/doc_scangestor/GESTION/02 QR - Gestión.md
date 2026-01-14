# ANEXO PMP: GESTIÓN DE AMPLIACIÓN (LECTURA QR)
**Proyecto Principal:** App "ScanGasto"
**Referencia:** Change Request CR-001 (Módulo QR)
**Cliente:** Gestoría Future S.L.
**Proveedor:** DevSolutions S.L.
**Fecha:** 18 de Octubre de 2025

---

## 1. RESUMEN EJECUTIVO
Este documento detalla la planificación, costes y recursos necesarios para acometer la **Fase de Ampliación de Funcionalidad: Lectura de Códigos QR**.
Esta funcionalidad no estaba contemplada en el alcance inicial y se gestionará como un **Sprint Adicional** de 2 semanas de duración, paralelo o posterior a la Fase 3 del proyecto principal.

---

## 2. EQUIPO DE TRABAJO Y ESTIMACIÓN DE ESFUERZO

Para esta ampliación se requiere activar perfiles específicos del equipo original. No se incorporan nuevas personas, pero se aumentan las horas contratadas.

### 2.1 Desglose de Tareas y Perfiles

| Perfil | Tareas en el Módulo QR | Horas Estimadas | Tarifa (€/h) | Coste Parcial |
| :--- | :--- | :--- | :--- | :--- |
| **Project Manager** | Gestión del cambio, re-planificación y demo final. | 6 h | 65,00 € | 390,00 € |
| **UX/UI Designer** | Diseño del overlay de cámara y nuevos iconos (PDF/QR). | 8 h | 45,00 € | 360,00 € |
| **Senior Mobile Dev** | Implementación librería `mobile_scanner`, lógica UI híbrida. | 25 h | 55,00 € | 1.375,00 € |
| **Senior Backend Dev** | Lógica de descarga de PDFs, parsers (TicketBAI) y seguridad. | 30 h | 55,00 € | 1.650,00 € |
| **QA Tester** | Pruebas de campo con tickets reales y QRs corruptos. | 10 h | 35,00 € | 350,00 € |
| **TOTAL** | | **79 Horas** | | **4.125,00 €** |

> *Nota: El coste total se facturará como un hito adicional independiente al contrato principal.*

---

## 3. PLANIFICACIÓN (CRONOGRAMA DETALLADO)

La implementación se realizará mediante un **Sprint Único de 10 días laborables**.

### Semana 1: Desarrollo del Núcleo (Core)
* **Lunes-Martes:** (Backend) Desarrollo del servicio "Downloader" seguro y parser de URLs. (Diseño) Mockups finales de la cámara.
* **Miércoles-Jueves:** (Mobile) Integración de la librería de escaneo y permisos de cámara.
* **Viernes:** (Integración) Conexión inicial App-Backend. Primera lectura exitosa de un QR estándar.

### Semana 2: Casos de Uso y QA
* **Lunes:** (Backend) Implementación específica de lógica TicketBAI y VeriFactu.
* **Martes:** (Mobile) Gestión de errores (¿Qué pasa si el QR no se lee?) y feedback visual.
* **Miércoles:** (QA) Batería de pruebas: Tickets sin cobertura, QRs rotos, PDFs pesados.
* **Jueves:** Corrección de bugs (Bugfixing).
* **Viernes:** **Despliegue a Entorno de Test** y Demo al cliente.

---

## 4. CONTROL DE GESTIÓN

### 4.1 Imputación Interna
Para evitar mezclar costes con el proyecto principal, se habilita un nuevo código de imputación en Jira/Clockify.

* **Código Principal:** `PRJ-2025-SCANGASTO`
* **Código Ampliación:** `CR-01-QR-READER` (Todas las horas de esta ampliación deben ir aquí).

### 4.2 Repositorio de Documentación
La documentación técnica específica de este módulo se alojará en una carpeta separada para facilitar su mantenimiento.
* **Ruta GitLab:** `/docs/modules/qr_reader/`
* **Wiki Confluence:** Página hija "Especificaciones Módulo QR".

---

## 5. INTERLOCUTORES Y COMUNICACIÓN

Se mantienen los contactos del proyecto principal, con una reunión específica para este módulo.

### 5.1 Matriz de Contacto (Sin cambios)
* **Cliente:** Carlos Financiero (Validación funcional), Laura Sistemas (Seguridad descargas).
* **Proveedor:** Ana Manager (Gestión), David Arquitecto (Seguridad técnica).

### 5.2 Reuniones Específicas
| Reunión | Fecha Aprox. | Asistentes | Objetivo |
| :--- | :--- | :--- | :--- |
| **Kick-off QR** | Día 1 | PM, Tech Lead, Carlos F. | Confirmar requisitos de TicketBAI y formatos esperados. |
| **Demo Funcional** | Día 10 | PM, Equipo, Carlos F. | Mostrar la descarga automática de facturas en tiempo real. |

---

## 6. GESTIÓN DE RIESGOS ESPECÍFICOS (QR)

Se añaden los siguientes riesgos a la matriz general del proyecto:

| Riesgo | Probabilidad | Impacto | Plan de Mitigación |
| :--- | :--- | :--- | :--- |
| **Bloqueo por Seguridad** | Media | Alto | Los servidores de algunos proveedores (ej: Repsol) podrían bloquear al bot de descarga. **Solución:** Implementar rotación de User-Agents o pedir al usuario login manual (fallback). |
| **Cámaras de gama baja** | Media | Medio | Móviles antiguos pueden tardar en enfocar el QR. **Solución:** Permitir "Zoom manual" en la interfaz de escaneo. |
| **Formatos no estándar** | Alta | Bajo | Aparición de QRs con codificación extraña. **Solución:** El sistema derivará automáticamente al flujo de "Hacer Foto" si falla el parseo. |

---

## 7. POLÍTICA DE VACACIONES Y DISPONIBILIDAD

Al tratarse de un **Sprint Intensivo (2 semanas)**, se aplican condiciones especiales:
1.  **Congelación de Vacaciones:** Se solicita al equipo asignado (Mobile y Backend Senior) que eviten tomar días libres durante estas 2 semanas críticas para garantizar la entrega.
2.  **Soporte Prioritario:** Durante la semana 2 (QA y cierre), el Tech Lead estará disponible al 100% para resolver bloqueos de arquitectura relacionados con la seguridad de descarga de archivos.