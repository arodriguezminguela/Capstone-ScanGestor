# ANEXO II: DISEÑO FUNCIONAL - MÓDULO DE ANALÍTICA Y REPORTES
**Proyecto:** ScanGasto - Fase de Valor Añadido
**Funcionalidad:** Dashboard de Visualización de Datos y Gráficos
**Fecha:** 19 de Octubre de 2025
**Estado:** Definición
**Referencia:** Change Request CR-002

---

## 1. INTRODUCCIÓN Y OBJETIVOS

### 1.1 Propósito
El objetivo de este módulo es proporcionar al usuario una visión gráfica e inmediata de su situación de gastos. Actualmente, el sistema almacena datos (OCR y QR), pero no ofrece información consolidada. Este módulo permitirá responder preguntas como: *"¿Cuánto he gastado en gasolina este mes?"* o *"¿Qué día tuve más gastos?"*.

### 1.2 Alcance
La funcionalidad se integrará como una nueva pestaña en la barra de navegación principal ("Estadísticas"). Incluirá selectores temporales, tarjetas de resumen (KPIs), gráficos interactivos y capacidad de filtrar la lista de gastos al tocar los gráficos (**Drill-down**).

---

## 2. DISEÑO DE INTERFAZ (UI/UX)

La pantalla de "Estadísticas" se divide en tres secciones verticales claramente diferenciadas:



### 2.1 Sección Superior: Control y KPIs
* **Selector de Periodo:** Un control central que muestra "Octubre 2025" con flechas `<` y `>` para cambiar de mes rápidamente, y un icono de calendario para saltar a una fecha específica.
* **Tarjetas Resumen (KPIs):** Carrusel horizontal con 3 datos clave:
    1.  **Total Gastado:** Importe total (con IVA).
    2.  **IVA Recuperable:** Suma de las cuotas de IVA (Dato clave para la gestoría).
    3.  **Ticket Medio:** Promedio de gasto por ticket.

### 2.2 Sección Central: Visualización Gráfica
Un área deslizable que permite alternar entre dos vistas:
* **Vista 1 (Por Categoría):** Gráfico de Donut (Rosco) donde cada color es una categoría (Transporte, Dietas, Alojamiento).
* **Vista 2 (Evolución Diaria):** Gráfico de Barras verticales mostrando el gasto acumulado por día del mes (eje X: días 1-31, eje Y: €).

### 2.3 Sección Inferior: Desglose Detallado
Lista de gastos que alimenta los gráficos.
* **Comportamiento Dinámico:** Si el usuario no toca nada, muestra todos los gastos del mes. Si el usuario toca la sección "Comida" en el gráfico, esta lista se filtra automáticamente para mostrar solo los tickets de comida.

---

## 3. REQUISITOS FUNCIONALES DETALLADOS

### 3.1 RF-REP-01: Filtrado Temporal
* **Descripción:** El sistema cargará por defecto los datos del mes en curso.
* **Validación:** No se pueden seleccionar fechas futuras. Si se selecciona un mes sin datos, se mostrará una ilustración de "Estado Vacío" (Empty State) animando al usuario a subir gastos.

### 3.2 RF-REP-02: Gráfico de Distribución (Categorías)
* **Tipo:** Gráfico Circular (Donut Chart).
* **Datos:** Agrupación de `importe_total` sumado por `categoria_id`.
* **Visualización:**
    * Debe mostrar los porcentajes (%) dentro de cada sección.
    * Debe tener una leyenda debajo con el nombre y el importe absoluto (ej: 🔵 Transporte: 150€).
* **Lógica de "Otros":** Si hay más de 5 categorías con gastos, las menos relevantes se agruparán automáticamente en un segmento gris llamado "Otros" para no saturar el gráfico.

### 3.3 RF-REP-03: Gráfico de Tendencia (Barras)
* **Tipo:** Histograma / Barras Verticales.
* **Datos:** Suma de gastos agrupados por `fecha_ticket`.
* **Interacción:** Al mantener pulsada una barra (Long Press), debe aparecer un *Tooltip* (bocadillo) indicando la fecha exacta y el importe de ese día.

### 3.4 RF-REP-04: Interactividad (Drill-Down)
* **Requisito:** Los gráficos deben actuar como filtros.
* **Acción:** Al tocar el segmento "Hoteles" en el gráfico circular:
    1.  El segmento se separa visualmente del centro (efecto *explode*).
    2.  La lista inferior se actualiza vía animación para mostrar solo los registros de Hoteles.
    3.  Aparece un botón "X Borrar Filtro" flotante.

### 3.5 RF-REP-05: Unificación de Orígenes
* **Regla de Negocio:** El módulo de reportes es "agnóstico" al origen del dato. Debe sumar y graficar indistintamente los gastos que provienen del **OCR** (fotos procesadas) y los que provienen del módulo **QR** (datos digitales).
* **Exclusión:** Los gastos con estado `RECHAZADO` o `BORRADOR` no deben sumar en las gráficas para no falsear la contabilidad.

---

## 4. FUNCIONALIDAD DE EXPORTACIÓN (Reportes PDF)

Dado que es una app para gestoría, el usuario necesita sacar los datos de la app.

### 4.1 RF-REP-06: Generación de Informe Mensual
* **Ubicación:** Botón "Exportar" en la esquina superior derecha.
* **Formato:** PDF multipágina.
* **Contenido del PDF:**
    1.  **Portada:** Logo de la empresa, nombre del empleado, mes y año.
    2.  **Resumen Ejecutivo:** Los mismos gráficos que se ven en pantalla.
    3.  **Tabla Detallada:** Filas con Fecha, Proveedor, CIF, Base, IVA y Total.
    4.  **Anexo Fotográfico:** Miniaturas de todas las fotos de los tickets y reproducciones de los QRs escaneados.

---

## 5. REGLAS DE NEGOCIO Y CÁLCULOS

### 5.1 Cálculo de IVA
Para el KPI de "IVA Recuperable", el sistema debe sumar el campo `cuota_iva` de la base de datos.
* *Nota:* Si un gasto antiguo no tiene el IVA desglosado (porque el OCR falló y el usuario no lo corrigió), se asumirá 0€ de IVA para ese registro y se marcará con una alerta en el reporte.

### 5.2 Multidivisa (Alcance Futuro)
En esta versión, si existen gastos en monedas diferentes (USD, GBP), se mostrarán convertidos a EUR usando el tipo de cambio del día del gasto (si está disponible) o se excluirán con un aviso. *Para esta fase funcional, se asume todo en EUR.*

---

## 6. CASOS DE USO (User Journey)

**Actor:** Laura (Directora de Marketing).
**Objetivo:** Comprobar si se ha pasado del presupuesto de dietas este mes.

1.  Laura entra en la App y pulsa la pestaña **"Estadísticas"**.
2.  Por defecto ve **Octubre**. Ve que el "Total Gastado" es 1.200€.
3.  Mira el **Gráfico Circular**. Ve un segmento naranja muy grande que ocupa el 40%.
4.  La leyenda dice: "🟠 Comidas: 480€".
5.  Laura toca el segmento naranja.
6.  La lista de abajo se filtra. Laura hace scroll y ve que hay una comida el día 12 de 250€ (Cena con clientes VIP).
7.  Recuerda el gasto, ve que es correcto.
8.  Pulsa **"Exportar PDF"** para enviárselo a su jefe y justificar esa cena.

---

## 7. IMPACTO EN RENDIMIENTO

La generación de gráficos requiere procesar datos. Para evitar que la app vaya lenta:
* Los cálculos de agrupación (`SUM`, `GROUP BY`) se realizarán en el **Servidor (Backend)**, no en el móvil.
* La App recibirá un JSON pequeño con los datos ya "masticados" para pintar el gráfico.
* *Ejemplo de respuesta optimizada:* `{"labels": ["Comida", "Taxi"], "values": [480, 50]}`.