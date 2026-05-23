import logging
from livekit.agents import stt
from config import Settings

logger = logging.getLogger("dental_receptionist.stt")


def create_stt_service(language: str = "multi") -> stt.STT:
    """
    STT Service Factory.

    Supported providers (set STT_PROVIDER in .env):
        speechmatics - Speechmatics real-time STT (default, supports Tamil)
        deepgram      - Deepgram nova-3 (English only streaming)
        openai        - OpenAI Whisper
        google        - Google Cloud STT
        azure         - Azure Cognitive Speech
        assemblyai    - AssemblyAI
    """
    provider = Settings.STT_PROVIDER
    logger.info(f"Initializing STT service with provider: {provider}, language: {language}")

    if provider == "speechmatics":
        from livekit.plugins import speechmatics
        lang = language if language in ("en", "ta") else "en"
        logger.info(f"Using Speechmatics STT (language: {lang})")
        return speechmatics.STT(
            api_key=Settings.SPEECHMATICS_API_KEY,
            language=lang,
        )

    elif provider == "deepgram":
        from livekit.plugins import deepgram
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
        logger.warning(f"Unknown STT provider '{provider}', falling back to Speechmatics.")
        from livekit.plugins import speechmatics
        lang = language if language in ("en", "ta") else "en"
        return speechmatics.STT(
            api_key=Settings.SPEECHMATICS_API_KEY,
            language=lang,
        )
