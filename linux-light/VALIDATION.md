# Comprobaciones de la primera edición

Fecha: 12 de octubre de 2026. Equipo: EndeavourOS/KDE X11, Ryzen 5 7535HS, 7.08 GiB de RAM utilizables, RTX 2050 de 4 GiB y controlador NVIDIA operativo.

- **13 pruebas automatizadas correctas:** 10 de normalización española y 3 de exclusión mutua, reentrada y cancelación de tareas pesadas.
- **Interfaz:** compilación TypeScript/Vite correcta. Historial visible encima del compositor, botones de ambas voces alineados y desplazamiento vertical sobre voces que mueve el historial de 0 a 180 píxeles. Reproducción y recuperación de progreso comprobadas en la adaptación local.
- **Sin internet real:** generación de Alex, texto con fechas/números, clonación de una referencia sintética y transcripción Whisper Small realizadas con red externa aislada. Los datos iniciales estaban vacíos y los modelos eran los del paquete.
- **Runtime propio de ventana:** Python, bindings GTK y WebKit incluidos cargaron la interfaz en español y el perfil Alex. La barra de inicio termina cuando aparece el compositor, después de la carga inicial de React.
- **Instalador real:** integridad de cuatro partes correcta, extracción e instalación en una ruta con espacios y caracteres españoles, creación de lanzador válido y comprobación del intérprete instalado con CUDA disponible. Los datos y el menú habituales no se modificaron durante esta instalación de prueba.

La clonación de prueba usa una referencia sintética; no se publican grabaciones ni clones personales. No se ha probado esta distribución en otro equipo ni en otras distribuciones Linux. Estas comprobaciones no son una garantía de pronunciación perfecta para cualquier texto.
