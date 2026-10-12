# Construcción de la edición offline

Estos scripts empaquetan una instalación local ya verificada. No descargan nada y no incluyen datos personales. Las rutas se suministran como argumentos; no se incorpora el nombre del usuario ni secretos en el código.

1. Instala las dependencias de desarrollo y prepara los modelos públicos en un entorno de construcción con internet. Usa Python 3.12 para el backend. El constructor inicial usa Python 3.14 del sistema Arch y sus bindings GI/cairo para la ventana.
2. Compila la interfaz con `VITE_LOCAL_DESKTOP=1 VITE_LOW_MEMORY=1 VITE_APP_VERSION=0.5.0-light-meimei.1 bun run --cwd web build`. Copia `web/dist` a `frontend`. Bun y node_modules solamente se utilizan durante la construcción.
3. Ejecuta `python linux-light/build-runtime.py --installation /ruta/a/instalacion-verificada --output /ruta/payload`. La instalación de origen sigue el diseño de la primera adaptación local: `app/work/voicebox-0.5.0/.venv`, `app/work/tools/python/cpython-3.12.15-linux-x86_64-gnu`, `models/hub` y SoX en `app/work/tools/sox`.
4. Prueba `payload/linux-light/launch` con datos nuevos y otro puerto: `VOICEBOX_DATA_HOME=/ruta/datos-de-prueba VOICEBOX_PORT=17495 payload/linux-light/launch`. Comprueba que se abre Alex y que genera sin red; revisa también clonación y transcripción.
5. Ejecuta `python linux-light/build-release.py --payload /ruta/payload --output /ruta/release`. Crea partes de 1800 MiB, manifiesto, instalador y checksums. Cada archivo queda bajo el límite de GitHub.
6. Verifica `bash /ruta/release/instalar-meimei.run --check`; instala en un XDG_DATA_HOME temporal para comprobar relocación. Para publicar, conserva todas las partes y el manifiesto juntos.

La extracción utiliza tar/gzip y la verificación sha256sum, herramientas básicas del sistema. Zenity muestra el diálogo y progreso si está disponible; se ofrece modo de terminal como alternativa. El runtime incluye bindings, GTK/WebKit y dependencias nativas; glibc, sesión D-Bus, audio, fuentes, bubblewrap y controlador NVIDIA pertenecen al sistema operativo.

El constructor detecta glibc y declara esa versión como mínimo. Este paquete inicial debe etiquetarse para Arch/EndeavourOS x86_64, no como compatible universal. Construir sobre una distribución más antigua y realizar pruebas independientes ampliaría la compatibilidad.

Para un lanzamiento público, revisa las licencias de modelos, runtimes CUDA y bibliotecas nativas. Conserva los archivos `.dist-info`, avisos de licencias y versiones de `licenses/`. Proporciona el código fuente correspondiente de los componentes GPL/LGPL distribuidos o una forma de entrega que cumpla sus licencias. No publiques credenciales, .env, bases de datos, grabaciones ni cachés de autenticación.
