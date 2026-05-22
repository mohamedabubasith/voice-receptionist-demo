import logging
from livekit.agents import tts
from config import Settings

logger = logging.getLogger("dental_receptionist.tts")

def create_tts_service() -> tts.TTS:
    """
    TTS Service Factory. Initializes Text-to-Speech engines dynamically
    based on application settings. Lazy-imports modules to avoid boot-time
    dependency issues when unused.

    Supported providers (set TTS_PROVIDER in .env):
        deepgram   - Deepgram Aura (default)
        openai     - OpenAI TTS (tts-1 / tts-1-hd)
        elevenlabs - ElevenLabs
        cartesia   - Cartesia Sonic
        google     - Google Cloud TTS
        azure      - Azure Cognitive TTS
        playht     - Play.ht
    """
    provider = Settings.TTS_PROVIDER
    logger.info(f"Initializing TTS service with provider: {provider}")

    if provider == "deepgram":
        from livekit.plugins import deepgram

        model = Settings.TTS_MODEL or "aura-2-asteria-en"
        logger.info(f"Using Deepgram TTS (model: {model})")
        return deepgram.TTS(
            api_key=Settings.DEEPGRAM_API_KEY,
            model=model,
        )

    elif provider == "openai":
        from livekit.plugins import openai

        model = Settings.TTS_MODEL or "tts-1"
        voice = Settings.TTS_VOICE or "nova"
        logger.info(f"Using OpenAI TTS (model: {model}, voice: {voice})")
        return openai.TTS(
            api_key=Settings.OPENAI_API_KEY,
            model=model,
            voice=voice,
        )

    elif provider == "elevenlabs":
        from livekit.plugins import elevenlabs

        # eleven_turbo_v2_5 supports Tamil + English in the same session
        model = Settings.ELEVEN_MODEL_ID or "eleven_turbo_v2_5"
        voice_id = Settings.ELEVEN_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
        logger.info(f"Using ElevenLabs TTS (model: {model}, voice_id: {voice_id})")
        return elevenlabs.TTS(
            api_key=Settings.ELEVEN_API_KEY,
            model=model,
            voice_id=voice_id,
        )

    elif provider == "cartesia":
        from livekit.plugins import cartesia

        model = Settings.CARTESIA_MODEL or "sonic-english"
        voice = Settings.CARTESIA_VOICE or "c694ee36-39cc-4395-8e93-c97800c732b2"
        logger.info(f"Using Cartesia TTS (model: {model}, voice: {voice})")
        return cartesia.TTS(
            api_key=Settings.CARTESIA_API_KEY,
            model=model,
            voice=voice,
        )

    elif provider == "google":
        from livekit.plugins import google
        logger.info("Using Google Cloud TTS")
        return google.TTS()

    elif provider == "azure":
        from livekit.plugins import azure
        logger.info("Using Azure Cognitive TTS")
        return azure.TTS()

    elif provider == "playht":
        from livekit.plugins import playht
        logger.info("Using Play.ht TTS")
        return playht.TTS()

    else:
        logger.warning(f"Unknown TTS provider '{provider}', falling back to Deepgram TTS.")
        from livekit.plugins import deepgram
        return deepgram.TTS(
            api_key=Settings.DEEPGRAM_API_KEY,
            model=Settings.TTS_MODEL or "aura-2-asteria-en",
        )
