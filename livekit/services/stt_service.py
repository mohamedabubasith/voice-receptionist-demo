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

    if provider == "deepgram":
        from livekit.plugins import deepgram

        # Deepgram streaming doesn't support Tamil — use LiveKit Inference Cartesia Ink Whisper
        if language == "ta":
            logger.info("Tamil caller — using LiveKit Inference cartesia/ink-whisper (no extra API key)")
            from livekit.agents import inference
            return inference.STT(model="cartesia/ink-whisper", language="ta")

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
