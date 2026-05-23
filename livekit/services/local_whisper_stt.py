import asyncio
import logging
import numpy as np
from livekit.agents import stt

logger = logging.getLogger("dental_receptionist.stt.local_whisper")

_model_cache: dict = {}


def _get_model(model_size: str):
    if model_size not in _model_cache:
        from faster_whisper import WhisperModel
        logger.info(f"Loading faster-whisper model: {model_size}")
        _model_cache[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
        logger.info(f"faster-whisper {model_size} loaded")
    return _model_cache[model_size]


class LocalWhisperSTT(stt.STT):
    def __init__(
        self,
        model_size: str = "small",
        language: str | None = None,
        beam_size: int = 1,
        best_of: int = 1,
        temperature: float = 0.0,
        no_speech_threshold: float = 0.6,
        vad_filter: bool = True,
    ):
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False)
        )
        self._model_size = model_size
        self._language = language
        self._beam_size = beam_size
        self._best_of = best_of
        self._temperature = temperature
        self._no_speech_threshold = no_speech_threshold
        self._vad_filter = vad_filter
        # Eagerly load model on init (avoid first-call delay)
        _get_model(model_size)

    async def _recognize_impl(
        self,
        buffer,
        *,
        language: str | None = None,
        conn_options=None,
    ) -> stt.SpeechEvent:
        model = _get_model(self._model_size)
        lang = language or self._language

        raw = bytes(buffer.data)
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

        loop = asyncio.get_event_loop()

        beam_size = self._beam_size
        best_of = self._best_of
        temperature = self._temperature
        no_speech_threshold = self._no_speech_threshold
        vad_filter = self._vad_filter

        def _transcribe():
            segs, info = model.transcribe(
                audio,
                language=lang,
                beam_size=beam_size,
                best_of=best_of,
                temperature=temperature,
                no_speech_threshold=no_speech_threshold,
                vad_filter=vad_filter,
            )
            return list(segs), info

        segments, info = await loop.run_in_executor(None, _transcribe)
        text = " ".join(s.text for s in segments).strip()
        logger.info(f"LocalWhisper [{info.language}]: {text!r}")

        return stt.SpeechEvent(
            type=stt.SpeechEventType.FINAL_TRANSCRIPT,
            alternatives=[stt.SpeechData(language=info.language, text=text)],
        )
