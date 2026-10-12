# Componentes y licencias de la distribución offline

La licencia MIT de Voicebox se conserva en LICENSE. Los modelos públicos redistribuidos conservan sus respectivos avisos de licencia, junto al paquete:

- Qwen/Qwen3-TTS-12Hz-0.6B-Base: Apache-2.0.
- hexgrad/Kokoro-82M: Apache-2.0.
- openai/whisper-base y openai/whisper-small: licencia MIT de Whisper.

Python, PyTorch, NVIDIA CUDA runtime/cuDNN, Transformers, GTK, WebKitGTK, GStreamer, eSpeak NG y otras dependencias tienen licencias propias; se incluyen sus avisos disponibles en `licenses/` y los directorios `.dist-info` del entorno Python. Los componentes LGPL/GPL mantienen sus enlaces dinámicos y no se modifican, salvo la adaptación del cargador Python de eSpeak documentada en el constructor. El controlador NVIDIA del sistema no se redistribuye.

El constructor registra los paquetes nativos y sus versiones en `licenses/native-packages.txt`. Para obtener el código de esos componentes se deben consultar las fuentes y paquetes de Arch correspondientes a esas versiones; una publicación final debe revisar los avisos y obligaciones de redistribución de todos los componentes incluidos. El instalador y la generación no consultan esos enlaces.
