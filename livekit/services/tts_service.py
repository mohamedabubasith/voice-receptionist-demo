import logging
from livekit.agents import tts
from config import Settings

logger = logging.getLogger("dental_receptionist.tts")

def create_tts_service(language: str = "en") -> tts.TTS:
    provider = Settings.TTS_PROVIDER
    logger.info(f"Initializing TTS service with provider: {provider}, language: {language}")

    if provider == "inference":
        from livekit.agents import inference

        model = Settings.INFERENCE_TTS_MODEL or "cartesia/sonic-3"
        voice = Settings.INFERENCE_TTS_VOICE or "f786b574-daa5-4673-aa0c-cbe3e8534c02"
        logger.info(f"Using LiveKit Inference TTS (model: {model}, voice: {voice}, language: {language})")
        return inference.TTS(model=model, voice=voice, language=language)

    elif provider == "deepgram":
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
        voice = Settings.GOOGLE_TTS_VOICE or "en-US-Neural2-F"
        language = Settings.GOOGLE_TTS_LANGUAGE or "en-US"
        logger.info(f"Using Google Cloud TTS (voice: {voice}, language: {language})")
        kwargs: dict = {"voice_name": voice, "language": language}
        if Settings.GOOGLE_CREDENTIALS_JSON:
            import json as _json
            kwargs["credentials_info"] = _json.loads(Settings.GOOGLE_CREDENTIALS_JSON)
        return google.TTS(**kwargs)

    elif provider == "azure":
        from livekit.plugins import azure
        voice = Settings.AZURE_TTS_VOICE or "en-US-JennyNeural"
        language = Settings.AZURE_TTS_LANGUAGE or "en-US"
        logger.info(f"Using Azure Cognitive TTS (voice: {voice}, language: {language})")
        azure_kwargs: dict = {"voice": voice, "language": language}
        if Settings.AZURE_TTS_KEY:
            azure_kwargs["speech_key"] = Settings.AZURE_TTS_KEY
        if Settings.AZURE_TTS_REGION:
            azure_kwargs["speech_region"] = Settings.AZURE_TTS_REGION
        return azure.TTS(**azure_kwargs)

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
