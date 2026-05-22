import os
import logging
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger("dental_receptionist.config")


class Settings:
    """Centralized, structured configuration access and validation."""

    # Core LiveKit keys
    LIVEKIT_URL = os.environ.get("LIVEKIT_URL", "").strip()
    LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY", "").strip()
    LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET", "").strip()

    # Agent identity
    RECEPTIONIST_NAME = os.environ.get("RECEPTIONIST_NAME", "Priya").strip()
    CLINIC_NAME = os.environ.get("CLINIC_NAME", "Demo Clinic").strip()

    # Booking webhook endpoint
    N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "").strip()

    # LLM Settings
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai").lower().strip()

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
    OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "").strip() or None
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    ANTHROPIC_MODEL = os.environ.get(
        "ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"
    ).strip()

    OLLAMA_API_BASE = os.environ.get(
        "OLLAMA_API_BASE", "http://localhost:11434"
    ).strip()
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3").strip()

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip()

    # STT Settings
    STT_PROVIDER = os.environ.get("STT_PROVIDER", "deepgram").lower().strip()

    DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY", "").strip()
    DEEPGRAM_MODEL = os.environ.get("DEEPGRAM_MODEL", "nova-2").strip()

    OPENAI_STT_MODEL = os.environ.get("OPENAI_STT_MODEL", "whisper-1").strip()

    AZURE_STT_KEY = os.environ.get("AZURE_STT_KEY", "").strip()
    AZURE_STT_REGION = os.environ.get("AZURE_STT_REGION", "").strip()

    ASSEMBLYAI_API_KEY = os.environ.get("ASSEMBLYAI_API_KEY", "").strip()

    # TTS Settings
    TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "deepgram").lower().strip()

    TTS_MODEL = os.environ.get("TTS_MODEL", "").strip()
    TTS_VOICE = os.environ.get("TTS_VOICE", "nova").strip()

    # ElevenLabs
    ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY", "").strip()
    ELEVEN_MODEL_ID = os.environ.get("ELEVEN_MODEL_ID", "eleven_flash_v2_5").strip()
    ELEVEN_VOICE_ID = os.environ.get("ELEVEN_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()

    # Cartesia
    CARTESIA_API_KEY = os.environ.get("CARTESIA_API_KEY", "").strip()
    CARTESIA_MODEL = os.environ.get("CARTESIA_MODEL", "sonic-english").strip()
    CARTESIA_VOICE = os.environ.get(
        "CARTESIA_VOICE", "c694ee36-39cc-4395-8e93-c97800c732b2"
    ).strip()

    @classmethod
    def validate(cls):
        """Validates critical connection keys depending on the chosen providers."""
        errors = []

        # Check LiveKit credentials (only check when running in production/normal mode;
        # in dev mode these are loaded by CLI, but it is best to warn if they are completely empty)
        if not cls.LIVEKIT_URL:
            logger.warning("LIVEKIT_URL is not set in environment.")

        # LLM validation
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")
        elif cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            errors.append(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER is 'anthropic'"
            )
        elif cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is required when LLM_PROVIDER is 'groq'")
        elif cls.LLM_PROVIDER == "google" and not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required when LLM_PROVIDER is 'google'")

        # STT validation
        if cls.STT_PROVIDER == "deepgram" and not cls.DEEPGRAM_API_KEY:
            errors.append(
                "DEEPGRAM_API_KEY is required when STT_PROVIDER is 'deepgram'"
            )
        elif cls.STT_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when STT_PROVIDER is 'openai'")
        elif cls.STT_PROVIDER == "azure" and (
            not cls.AZURE_STT_KEY or not cls.AZURE_STT_REGION
        ):
            errors.append(
                "AZURE_STT_KEY and AZURE_STT_REGION are required when STT_PROVIDER is 'azure'"
            )
        elif cls.STT_PROVIDER == "assemblyai" and not cls.ASSEMBLYAI_API_KEY:
            errors.append(
                "ASSEMBLYAI_API_KEY is required when STT_PROVIDER is 'assemblyai'"
            )

        # TTS validation
        if cls.TTS_PROVIDER == "deepgram":
            if not cls.DEEPGRAM_API_KEY:
                errors.append(
                    "DEEPGRAM_API_KEY is required when TTS_PROVIDER is 'deepgram'"
                )
        elif cls.TTS_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                errors.append(
                    "OPENAI_API_KEY is required when TTS_PROVIDER is 'openai'"
                )
        elif cls.TTS_PROVIDER == "elevenlabs":
            if not cls.ELEVEN_API_KEY:
                errors.append(
                    "ELEVEN_API_KEY is required when TTS_PROVIDER is 'elevenlabs'"
                )
        elif cls.TTS_PROVIDER == "cartesia":
            if not cls.CARTESIA_API_KEY:
                errors.append(
                    "CARTESIA_API_KEY is required when TTS_PROVIDER is 'cartesia'"
                )

        if errors:
            raise ValueError(
                "Environment Configuration Error:\n"
                + "\n".join(f" - {err}" for err in errors)
            )

        logger.info(
            f"Configuration validated successfully. LLM: {cls.LLM_PROVIDER}, "
            f"STT: {cls.STT_PROVIDER}, TTS: {cls.TTS_PROVIDER}"
        )
