import os
import logging
from livekit.agents import llm
from config import Settings

logger = logging.getLogger("dental_receptionist.llm")

def create_llm_service() -> llm.LLM:
    """
    LLM Service Factory. Initializes Large Language Model engines dynamically
    based on application settings. Lazy-imports modules to avoid boot-time
    dependency issues when unused.
    """
    provider = Settings.LLM_PROVIDER
    logger.info(f"Initializing LLM service with provider: {provider}")

    if provider == "openai":
        from livekit.plugins import openai
        
        api_key = Settings.OPENAI_API_KEY
        base_url = Settings.OPENAI_API_BASE
        model = Settings.OPENAI_MODEL or "gpt-4o-mini"
        
        logger.info(f"Using OpenAI LLM (model: {model})")
        return openai.LLM(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        
    elif provider == "anthropic":
        from livekit.plugins import anthropic
        
        api_key = Settings.ANTHROPIC_API_KEY
        model = Settings.ANTHROPIC_MODEL or "claude-3-5-sonnet-latest"
        
        logger.info(f"Using Anthropic LLM (model: {model})")
        return anthropic.LLM(
            api_key=api_key,
            model=model
        )
        
    elif provider == "ollama":
        from livekit.plugins import openai
        
        api_base = Settings.OLLAMA_API_BASE or "http://localhost:11434/v1"
        # Standardize Ollama endpoint suffix for LiveKit OpenAI compatibility
        if not api_base.endswith("/v1"):
            api_base = api_base.rstrip("/") + "/v1"
            
        model = Settings.OLLAMA_MODEL or "llama3"
        
        logger.info(f"Using Ollama LLM (base: {api_base}, model: {model})")
        return openai.LLM.with_ollama(
            model=model,
            base_url=api_base
        )
        
    elif provider == "groq":
        from livekit.plugins import groq
        
        api_key = Settings.GROQ_API_KEY
        model = Settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        
        logger.info(f"Using Groq LLM (model: {model})")
        return groq.LLM(
            api_key=api_key,
            model=model
        )
        
    elif provider == "google":
        from livekit.plugins import google
        
        api_key = Settings.GEMINI_API_KEY
        model = Settings.GEMINI_MODEL or "gemini-1.5-flash"
        
        logger.info(f"Using Google Gemini LLM (model: {model})")
        return google.LLM(
            api_key=api_key,
            model=model
        )
        
    else:
        logger.warning(f"Unknown LLM provider '{provider}', falling back to OpenAI LLM.")
        from livekit.plugins import openai
        return openai.LLM(
            api_key=Settings.OPENAI_API_KEY,
            base_url=Settings.OPENAI_API_BASE,
            model=Settings.OPENAI_MODEL or "gpt-4o-mini"
        )
