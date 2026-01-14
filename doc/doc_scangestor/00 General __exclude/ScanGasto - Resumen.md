**Resumen del Proyecto: ScanGasto**

**1. ¿Qué es ScanGasto y qué problema resuelve?**

ScanGasto es una aplicación móvil diseñada para simplificar la gestión de gastos en las empresas.

El problema principal que resuelve es el proceso tedioso y manual de reportar gastos. Empleados como los comerciales acumulan una gran cantidad de tickets y recibos en papel durante sus viajes. Tradicionalmente, deben guardar estos papeles, rellenar hojas de cálculo a mano, y adjuntar cada ticket, un proceso que consume mucho tiempo y es propenso a errores. ScanGasto automatiza esta tarea para empresas como nuestro cliente "Gestoría Future S.L.", eliminando la fricción tanto para el empleado que reporta el gasto como para sus compañeros de contabilidad, como María, que deben revisarlos y validarlos.

Para entender cómo resuelve este problema, veamos cómo lo usaría un empleado en su día a día.

**2. El día a día con ScanGasto: Un caso práctico**

Imaginemos a **Juan, un comercial** de la empresa. Acaba de repostar en una gasolinera y necesita registrar el gasto para que la empresa se lo devuelva. Con ScanGasto, el proceso es increíblemente rápido y sencillo.

- **Hacer una foto al ticket** Juan abre la app, pulsa el gran botón "+" y saca una foto a su recibo. La aplicación le muestra unas guías en la pantalla para ayudarle a encuadrar el ticket perfectamente, asegurando que toda la información sea legible.
- **La app "lee" la información** Inmediatamente después de tomar la foto, aparece un mensaje que dice _"Analizando ticket con IA..."_. En solo unos segundos, la inteligencia artificial de la aplicación analiza la imagen y extrae automáticamente los datos más importantes, como la fecha del gasto y el importe total.
- **Verificar y completar** A continuación, la app muestra un formulario con los datos que ha leído. Juan puede comprobar rápidamente si son correctos. En este caso, el sistema leyó "Repso", así que Juan lo corrige fácilmente a "Repsol". Luego, simplemente selecciona la categoría del gasto, **"Transporte/Gasolina"**, de una lista predefinida. Este paso es mucho más rápido que teclear toda la información desde cero.
- **Guardar y listo** Finalmente, Juan pulsa el botón "Guardar". Un mensaje de confirmación, "Gasto guardado con éxito", aparece en pantalla y es devuelto al panel principal, donde puede ver que el total de gastos del mes ha aumentado exactamente en 50€.

Una vez guardado, cada gasto muestra un estado claro para que Juan sepa siempre en qué punto se encuentra. Un círculo **verde (🟢) indica que ha sido 'Aprobado'** para su reembolso, uno **amarillo (🟡) significa que está 'Pendiente'** de revisión, y uno **rojo (🔴) alerta de que ha sido 'Rechazado'** y requiere su atención.

Este proceso parece mágico, pero es posible gracias a una combinación de tecnologías modernas diseñadas para trabajar juntas.

**3. La tecnología detrás de la magia**

Aunque la aplicación es muy fácil de usar para Juan, por detrás está soportada por varias tecnologías potentes, cada una con una misión específica. Esta combinación es la que permite transformar una foto en un registro contable válido.

| Componente | Tecnología Principal | ¿Para qué sirve de forma sencilla? |
| --- | --- | --- |
| **La App en el móvil** | Flutter | Es la tecnología que permite construir la aplicación que Juan instala y usa en su teléfono, asegurando que funcione bien tanto en iPhone como en Android. |
| **El "Cerebro" Central** | Python (con FastAPI) | Es el motor inteligente en el servidor que recibe las fotos, procesa la información, se comunica con la IA y guarda todo de forma segura en la base de datos. |
| **El "Ojo" que lee los tickets** | Google Cloud Vision (OCR) | Es la "inteligencia artificial" especializada que analiza la imagen del ticket y es capaz de leer y entender el texto, extrayendo datos clave como la fecha y el total. |
| **El "Archivo" digital** | PostgreSQL | Es una base de datos muy robusta y segura. Funciona como un archivador digital perfectamente organizado donde se guardan todos los gastos para que no se pierdan nunca. |

**4. Más allá del ticket: El futuro de ScanGasto**

La tecnología de ScanGasto no solo resuelve el problema actual, sino que está diseñada para evolucionar. El siguiente paso es la lectura de códigos QR, un salto hacia el "cero errores y cero esfuerzo". Con esta mejora, la aplicación podrá leer los datos de un ticket con perfecta exactitud o incluso descargar la factura digital automáticamente desde una URL, eliminando por completo la necesidad de hacer una foto.

Una vez que los datos se capturan de forma fiable, su verdadero valor reside en la información que proporcionan. El futuro módulo de analítica transformará ScanGasto en una herramienta de inteligencia de negocio. Empleados y directivos podrán visualizar gráficos de gastos por categoría o su evolución en el tiempo, respondiendo al instante a preguntas como: _"¿Cuánto he gastado en gasolina este mes?"_. Esto convierte la app de un simple gestor de tickets a un potente asistente para la toma de decisiones.

En resumen, ScanGasto no es solo una herramienta de eficiencia para hoy. Utiliza tecnologías avanzadas para transformar una tarea administrativa tediosa en un proceso de pocos segundos, pero su arquitectura la posiciona como una plataforma escalable para la gestión inteligente de gastos del mañana, ahorrando tiempo, reduciendo errores y ofreciendo valiosa información financiera a la empresa.