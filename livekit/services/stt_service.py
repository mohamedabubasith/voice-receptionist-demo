import logging
from livekit.agents import stt
from config import Settings

logger = logging.getLogger("dental_receptionist.stt")

def create_stt_service(language: str = "multi") -> stt.STT:
    """
    STT Service Factory. Initializes Speech-to-Text engines dynamically
    based on application settings. Lazy-imports modules to avoid boot-time
    dependency issues when unused.

    Supported providers (set STT_PROVIDER in .env):
        deepgram  - Deepgram nova-2 / nova-3 (default)
        openai    - OpenAI Whisper
        google    - Google Cloud STT
        azure     - Azure Cognitive Speech
        assemblyai - AssemblyAI
    """
    provider = Settings.STT_PROVIDER
    logger.info(f"Initializing STT service with provider: {provider}")

    if provider == "local":
        from livekit.agents.stt import StreamAdapter
        from livekit.plugins import silero
        from services.local_whisper_stt import LocalWhisperSTT
        model_size = Settings.LOCAL_WHISPER_MODEL or "small"
        lang = language if language in ("en", "ta") else None
        logger.info(f"Using local faster-whisper ({model_size}, language: {lang or 'auto'})")
        return StreamAdapter(
            stt=LocalWhisperSTT(
                model_size=model_size,
                language=lang,
                beam_size=1,
                best_of=1,
                temperature=0.0,
                no_speech_threshold=0.6,
                vad_filter=True,
            ),
            vad=silero.VAD.load(),
        )

    elif provider == "deepgram":
        from livekit.plugins import deepgram

        # Deepgram streaming doesn't support Tamil — use local faster-whisper
        if language == "ta":
            from livekit.agents.stt import StreamAdapter
            from livekit.plugins import silero
            from services.local_whisper_stt import LocalWhisperSTT
            model_size = Settings.LOCAL_WHISPER_MODEL or "small"
            logger.info(f"Tamil caller — using local faster-whisper ({model_size})")
            return StreamAdapter(
                stt=LocalWhisperSTT(
                    model_size=model_size,
                    language="ta",
                    beam_size=1,
                    best_of=1,
                    temperature=0.0,
                    no_speech_threshold=0.6,
                    vad_filter=True,
                ),
                vad=silero.VAD.load(),
            )

        model = Settings.DEEPGRAM_MODEL or "nova-3"
        logger.info(f"Using Deepgram STT (model: {model}, language: multi)")
        return deepgram.STT(
            api_key=Settings.DEEPGRAM_API_KEY,
            model=model,
            language="multi",
        )

    elif provider == "openai":
        from livekit.plugins import openai

        model = Settings.OPENAI_STT_MODEL or "whisper-1"
        logger.info(f"Using OpenAI Whisper STT (model: {model})")
        return openai.STT(
            api_key=Settings.OPENAI_API_KEY,
            model=model,
        )

    elif provider == "google":
        from livekit.plugins import google
        logger.info("Using Google Cloud STT")
        return google.STT()

    elif provider == "azure":
        from livekit.plugins import azure
        logger.info(f"Using Azure Cognitive STT (region: {Settings.AZURE_STT_REGION})")
        return azure.STT(
            api_key=Settings.AZURE_STT_KEY,
            region=Settings.AZURE_STT_REGION,
        )

    elif provider == "assemblyai":
        from livekit.plugins import assemblyai
        logger.info("Using AssemblyAI STT")
        return assemblyai.STT(
            api_key=Settings.ASSEMBLYAI_API_KEY,
        )

    else:
        logger.warning(f"Unknown STT provider '{provider}', falling back to Deepgram STT.")
        from livekit.plugins import deepgram
        return deepgram.STT(
            api_key=Settings.DEEPGRAM_API_KEY,
            model=Settings.DEEPGRAM_MODEL or "nova-3",
            language="multi",
        )
