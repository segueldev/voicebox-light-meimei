# Voice Box Edición Light Meimei

**Voicebox, creado por [Jamie Pine](https://github.com/jamiepine) y sus colaboradores.**

**Light Meimei es la adaptación de [segueldev](https://github.com/segueldev) como aplicación Linux optimizada para equipos modestos**, basada en [Voicebox v0.5.0](https://github.com/jamiepine/voicebox/tree/v0.5.0).

Aplicación de escritorio en español para generar y clonar voces de forma local. El lanzador abre una ventana propia y gestiona automáticamente el servicio interno; no hay que abrir el navegador, escribir localhost ni mantener una terminal. No es una versión oficial del proyecto original.

## Proyecto original y adaptación

El proyecto original es [jamiepine/voicebox](https://github.com/jamiepine/voicebox), creado por Jamie Pine junto con sus colaboradores. Se conserva su licencia MIT, su aviso de copyright y el historial de la versión utilizada.

segueldev adaptó esa base a sus necesidades: convertirla en una aplicación Linux fácil de abrir, configurar modelos ligeros para un equipo de 8 GB de RAM y RTX 2050 de 4 GB, ponerla en español, mejorar los estados de generación y reproducción y corregir los problemas de interfaz encontrados durante el uso. El nombre y logo Meimei identifican esta edición comunitaria.

Esta adaptación no es una publicación oficial de Jamie Pine. Las mejoras se documentan para poder compartirlas y proponer contribuciones concretas al repositorio original.

## Instalación sin conexión

La distribución completa incluye Python, dependencias, interfaz, modelos y un instalador para el usuario. Descarga **el instalador, el manifiesto y todas las partes** de la misma versión en una carpeta. Ejecuta `bash instalar-meimei.run`. El instalador verifica las partes y muestra su progreso; no solicita privilegios de administrador ni descarga paquetes. Después encontrarás **Voice Box Edición Light Meimei** en el menú de aplicaciones.

El paquete es grande porque incluye los modelos y las bibliotecas de IA. GitHub limita cada archivo de una release a menos de 2 GiB; por eso se distribuye por partes. **El repositorio de código por sí solo no es el instalador offline.**

Sistema objetivo inicial: Linux x86_64, Arch/EndeavourOS con sesión gráfica y glibc compatible con el equipo de construcción. No se promete compatibilidad con todas las distribuciones. La GPU requiere el controlador NVIDIA instalado en el sistema; el controlador no se incluye. Se mantienen los requisitos normales de una sesión Linux (glibc, D-Bus, audio, fuentes, bubblewrap para la protección de WebKit).

La generación, clonación y transcripción usan archivos locales. Los enlaces a GitHub y cualquier actualización futura necesitan internet si decides abrirlos. No se incluye telemetría adicional. El servicio escucha solamente en la dirección local del equipo.

## Modelos incluidos

- Kokoro 82M: voz masculina en español **Alex**, ligera y seleccionada inicialmente.
- Qwen3-TTS 0.6B Base: clonación con una grabación de referencia propia.
- Whisper Base y Small: transcripción local; Small priorizado por su precisión en español.

La edición limita la interfaz a estos modelos. No incluye modelos de 1.7B, Whisper Medium/Large ni motores adicionales que no se verificaron en el equipo objetivo. No incluye grabaciones, historial, referencias de voz ni bases de datos del desarrollador.

## Equipo de referencia

| Componente | Configuración comprobada |
| --- | --- |
| Sistema | EndeavourOS x86_64, KDE Plasma, KWin X11 |
| Equipo | ASUS TUF Gaming A15 FA506NF |
| CPU | AMD Ryzen 5 7535HS, 6 núcleos / 12 hilos |
| RAM disponible para el sistema | 7.08 GiB (equipo de 8 GB) |
| GPU | NVIDIA RTX 2050, 4 GiB de VRAM; AMD Radeon 680M |
| Intercambio | 19.54 GiB |
| Disco | SSD de 474.94 GiB, btrfs |
| Pantalla | 1920 × 1080, escala 125 % |

Se ejecuta una tarea pesada a la vez y se libera el modelo anterior al cambiar de motor. Kokoro es la opción cotidiana de menor consumo. La clonación tarda más y puede usar intercambio si otras aplicaciones ocupan la RAM. La CPU sirve como alternativa, con tiempos mayores. El instalador comprueba el disco; el controlador GPU sigue siendo responsabilidad del sistema operativo.

Las mejoras de pronunciación normalizan números, fechas, horas y abreviaturas en español. Ningún modelo garantiza pronunciación perfecta: revisa el audio final, especialmente nombres propios, textos ambiguos y referencias con ruido. Una referencia clara y un texto bien puntuado mejoran los resultados.

## Cambios, créditos y desarrollo

Consulta [los cambios de Light Meimei](CHANGELOG-LIGHT.md), [los créditos](CREDITS.md), [la construcción offline](linux-light/BUILD.md) y [las propuestas para upstream](UPSTREAM-CONTRIBUTIONS.md). Conservamos la [licencia MIT original](LICENSE) y los [avisos de terceros](linux-light/THIRD-PARTY.md). El README original está en [docs/upstream](docs/upstream/README-v0.5.0.md).
