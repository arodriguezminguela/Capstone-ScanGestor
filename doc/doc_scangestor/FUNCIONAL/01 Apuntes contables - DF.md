# ESPECIFICACIÓN FUNCIONAL DETALLADA (FDS)
**Proyecto:** App de Gestión de Gastos "ScanGasto"
**Cliente:** Gestoría Future S.L.
**Versión:** 2.0 (Detalle Funcional y UI)
**Fecha:** 15 de Octubre de 2025
**Autor:** Equipo de Desarrollo (Loreto Martínez, Ana Gómez)

---

## 1. MAPA DE NAVEGACIÓN
La aplicación contará con la siguiente estructura de pantallas:

1.  **Login / Splash Screen**
2.  **Dashboard (Pantalla Principal)**
    * Listado de últimos gastos.
    * Gráfico mensual.
3.  **Módulo de Captura (Cámara/Galería)**
4.  **Pantalla de Verificación y Edición (Detalle del Gasto)**
5.  **Histórico y Filtros**

---

## 2. ESPECIFICACIÓN DETALLADA DE PANTALLAS (UI/UX)

A continuación se detalla la funcionalidad y los datos de cada interfaz.

### 2.1 Pantalla Principal (Dashboard)
**Objetivo:** Ofrecer un resumen rápido del estado de los gastos del mes y acceso rápido a la acción principal.

**Elementos de Interfaz:**
* **Header:** Saludo al usuario ("Hola, {Nombre}") y botón de Configuración/Logout.
* **Widget Resumen:** Tarjeta que muestra "Total Gastado este Mes".
    * *Dato:* Suma de importes con `fecha_gasto` = mes actual.
* **Botón de Acción Flotante (FAB):** Icono de cámara (+) grande y visible en la esquina inferior derecha.
    * *Acción:* Lleva a la pantalla 2.2.
* **Listado "Últimos Movimientos":** Muestra los últimos 5 registros.

### 2.2 Pantalla de Captura y Pre-procesado
**Objetivo:** Obtener la imagen del ticket con la calidad suficiente para el OCR.

**Funcionalidad:**
* **Visor de Cámara:** Ocupa el 80% de la pantalla.
* **Guías de encuadre:** Rectángulo superpuesto para ayudar al usuario a centrar el ticket.
* **Disparador:** Botón circular central.
* **Selector Galería:** Opción secundaria para subir fotos antiguas.
* **Comportamiento Post-Captura:**
    1.  Se muestra la foto congelada.
    2.  Se muestra un *spinner* de carga con el texto: *"Analizando ticket con IA..."*.
    3.  El sistema envía la imagen a la API de OCR.
    4.  Si la API responde OK, se navega a la pantalla 2.3.

---

### 2.3 Pantalla de Verificación y Edición (CORE DE LA APP)
**Objetivo:** El usuario debe validar los datos que el OCR ha leído y categorizar el gasto. Es la pantalla más crítica.

**Diseño:**
* **Mitad Superior:** Recorte de la imagen del ticket (con capacidad de *Zoom* y *Pan*) para consultar el original.
* **Mitad Inferior:** Formulario de datos (Scrollable).

**Tabla de Campos y Validaciones:**

| Campo | Tipo de Dato | Widget UI | Obligatorio | Validaciones / Comportamiento |
| :--- | :--- | :--- | :--- | :--- |
| **Fecha** | Date | DatePicker | SÍ | Pre-rellenado por OCR. No puede ser fecha futura. |
| **Proveedor** | String (50) | Input Text | NO | Nombre del comercio. Si el OCR falla, permite escritura libre. |
| **CIF/NIF** | String (9) | Input Text | NO | Validación de formato regex para DNI/CIF español. |
| **Base Imponible**| Decimal | Numeric Pad | NO | Se calcula aut. si se mete Total e IVA, pero editable. |
| **% IVA** | Enum | Dropdown | SÍ | Valores: 21%, 10%, 4%, 0%. Default: 21%. |
| **Cuota IVA** | Decimal | Read Only | - | Calculado automáticamente: (Base * %IVA). |
| **TOTAL** | Decimal | Numeric Pad | SÍ | **Crítico.** Debe coincidir con lo que pone en la foto. |
| **Categoría** | Enum | Select Box | SÍ | Opciones: *Comidas, Transporte, Alojamiento, Material, Otros*. |
| **Proyecto** | String | Search Box | NO | Vincula el gasto a un cliente/proyecto específico. |
| **Comentarios** | Text Area | Text Area | NO | Máx 250 caracteres. |

**Botones de Acción:**
* **"Guardar Gasto":** Valida el formulario. Si hay error, marca campos en rojo. Si OK, envía a BBDD.
* **"Reintentar Foto":** Vuelve a la cámara si la imagen era ilegible.

---

### 2.4 Pantalla de Histórico e Informes
**Objetivo:** Consultar gastos pasados.

**Funcionalidad:**
* **Filtros de Búsqueda:** Por rango de fechas (Desde/Hasta) y por Categoría.
* **Estado del Gasto:** Cada ítem en la lista tendrá un indicador visual (badge):
    * 🟢 *Aprobado* (Ya revisado por contabilidad).
    * 🟡 *Pendiente* (Recién subido).
    * 🔴 *Rechazado* (La foto no se ve o datos incorrectos).

---

## 3. CASO DE USO PRÁCTICO (Happy Path)

**Actor:** Juan (Comercial).
**Escenario:** Juan acaba de poner gasolina y pagar una comida de empresa.

1.  **Inicio:** Juan abre la app en la gasolinera.
2.  **Captura:** Pulsa el botón "+". Enfoca el ticket de la gasolinera "Repsol". Hace la foto.
3.  **Procesado:** La app tarda 3 segundos procesando.
4.  **Verificación:** Se abre la pantalla de edición.
    * El campo **Fecha** marca correctamente "15/10/2025".
    * El campo **Total** marca "50.00€".
    * El campo **Categoría** está vacío. Juan selecciona "Transporte/Gasolina".
    * El OCR leyó mal el proveedor y puso "Repso". Juan toca el campo y corrige a "Repsol".
5.  **Cierre:** Juan pulsa "Guardar".
6.  **Feedback:** Aparece un mensaje "Gasto guardado con éxito" y vuelve al Dashboard. El total del mes sube 50€.

---

## 4. REQUISITOS DE RENDIMIENTO Y ERRORES


1. Error de Red: Si al pulsar "Guardar" no hay internet, la app debe guardar el JSON en una base de datos local (SQLite/Realm) y marcarlo como "Sincronización Pendiente". Un worker en segundo plano intentará subirlo cada 15 minutos.

2. Timeout: Si el OCR tarda más de 10 segundos, se debe permitir al usuario rellenar todo manualmente sin esperar más.




