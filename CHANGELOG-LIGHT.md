# Cambios de Light Meimei

## 0.5.0-light-meimei.1 — 12 de octubre de 2026

Base: Voicebox v0.5.0. Estos cambios se prepararon para un equipo de 8 GB de RAM y RTX 2050 de 4 GB.

### Aplicación Linux y uso sin conexión
- Ventana de aplicación Linux con GTK/WebKit, servicio interno automático, inicio único y cierre del proceso al salir. No hace falta iniciar localhost manualmente ni abrir el navegador. Esta integración parte de la instalación manual Linux de v0.5.0; las funciones de síntesis y clonación ya existían en Voicebox.
- Lanzador con icono integrado en el menú KDE; corrección de la ruta del lanzador y actualización de la caché del menú en español.
- Nombre Voice Box Edición Light Meimei, logo Meimei y créditos de segueldev junto a los de Jamie Pine.
- Inicio con logo, aparición suave y barra animada que avanza por etapas reales hasta abrir la interfaz.
- Icono cuadrado que conserva las proporciones del logo y logo lateral ampliado.
- Corrección del bloqueo de carga al ocultar la vista WebKit: la interfaz permanece activa debajo de la bienvenida.
- Archivos instalados en una carpeta oculta del usuario; datos separados del programa.
- Distribución offline con Python, dependencias y modelos incluidos, comprobación de integridad y espacio libre, instalación sin administrador y desinstalación que conserva los datos por defecto.

### Consumo y voces
- Kokoro 82M con Alex, voz masculina en español, como preset inicial.
- Clonación Qwen3-TTS 0.6B Base y transcripción Whisper Small/Base; se ocultan opciones pesadas que no se comprobaron en el equipo.
- Exclusión mutua para tareas pesadas, bloqueo de carga para evitar modelos duplicados y descarga del modelo anterior al cambiar de motor.
- Precisión reducida compatible con CUDA, SDPA, dos hilos de cálculo y reducción de efectos visuales.
- Whisper Small ajustado para español, tipos de datos y máscara de atención correctos.
- Corrección de la actualización del identificador de voces predefinidas: cambiar el nombre de una voz ya no deja accidentalmente el preset femenino anterior.

### Español y generación
- Interfaz, fechas, estados, controles y mensajes traducidos al español.
- Normalización de números, porcentajes, fechas, horas, abreviaturas y puntuación; conservación del texto original en el historial.
- Validación de texto vacío o compuesto solamente por símbolos y comprobación de audio válido.
- Texto dividido en fragmentos más pequeños, transiciones entre fragmentos y volumen normalizado.

### Correcciones de interfaz y reproducción
- Estados visibles: en cola, cargando modelo, generando, reconectando, listo, reproduciendo, pausado, terminado y error; tiempo transcurrido.
- Botón ocupado durante toda la petición para evitar generaciones duplicadas y recuperación del texto si falla.
- Recuperación al perder los eventos de progreso, sin marcar un trabajo incompleto como terminado.
- Reproducción automática permitida por la ventana de escritorio y sincronización del estado real de reproducción; controles claros para escuchar, pausar y continuar.
- Mensajes comprensibles cuando no se puede reproducir y posibilidad de reintentar.
- Caja de escritura situada debajo del historial, reservando espacio para el reproductor; no tapa los audios generados.
- Historial con desplazamiento propio y gesto vertical del trackpad sobre la zona de voces dirigido hacia los audios.
- Tarjetas compactas con editar, exportar y eliminar alineados; corrección de botones desalineados por descripciones largas.
- Fondo opaco del compositor para evitar que el contenido se vea mezclado y alturas adaptadas al reproductor real.
- Navegación con rutas hash para evitar que recargar una pantalla abra accidentalmente una respuesta JSON de la API.
- Opciones de atajos globales, dictado y ajustes exclusivos de Tauri ocultos en esta ventana GTK cuando no funcionan allí.

### Comprobaciones realizadas en el equipo de referencia
- Generación masculina en español, clonación y transcripción local con modelos ya almacenados.
- Cambio de modelos y tareas concurrentes serializadas; validaciones de texto y normalización.
- Flujo real de generación, reproducción automática, pausa, continuación, fin y recuperación ante desconexión de progreso.
- Geometría del historial, compositor y reproductor; desplazamiento del trackpad y alineación de acciones de voces.

El resultado depende del hardware, de otros programas abiertos y de la referencia de voz. Estas comprobaciones no equivalen a una garantía de pronunciación perfecta ni de compatibilidad con todas las distribuciones Linux.
