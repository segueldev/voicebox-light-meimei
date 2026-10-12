"""Serialize heavy model work and reclaim unused TTS on the 4 GB setup."""
import asyncio
import functools
import gc
import os
from contextvars import ContextVar

_model_work_lock = asyncio.Lock()
_owner = ContextVar("voicebox_model_work_owner", default=None)

def serialized_model_work(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        task = asyncio.current_task()
        if os.environ.get("VOICEBOX_LOW_MEMORY") != "1" or _owner.get() is task:
            return await func(*args, **kwargs)
        async with _model_work_lock:
            token = _owner.set(task)
            try:
                return await func(*args, **kwargs)
            finally:
                _owner.reset(token)
    return wrapped

def release_other_tts_engines(engine):
    if os.environ.get("VOICEBOX_LOW_MEMORY") != "1":
        return
    from ..backends import _tts_backends, _stt_backend
    released = False
    for other_engine, backend in list(_tts_backends.items()):
        if other_engine != engine and backend.is_loaded():
            backend.unload_model()
            released = True
    if engine != "whisper" and _stt_backend is not None and _stt_backend.is_loaded():
        _stt_backend.unload_model()
        released = True
    if released:
        gc.collect()
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
