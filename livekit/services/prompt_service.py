import logging
from pathlib import Path

logger = logging.getLogger("dental_receptionist.prompt")

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def get_system_prompt(agent_name: str, receptionist_name: str, clinic_name: str, lang: str = "en") -> str:
    """Load prompt for agent+language. Tries <agent>_<lang>.txt first, falls back to <agent>.txt."""
    lang_file = _PROMPTS_DIR / f"{agent_name}_{lang}.txt"
    base_file = _PROMPTS_DIR / f"{agent_name}.txt"

    if lang_file.exists():
        prompt_file = lang_file
        logger.info(f"Using lang-specific prompt: {lang_file.name}")
    elif base_file.exists():
        prompt_file = base_file
        logger.info(f"No lang prompt for '{lang}', using base: {base_file.name}")
    else:
        raise FileNotFoundError(
            f"No prompt file found for agent '{agent_name}' (lang={lang}) in {_PROMPTS_DIR}"
        )

    prompt = prompt_file.read_text(encoding="utf-8").strip()
    prompt = prompt.replace("{{RECEPTIONIST_NAME}}", receptionist_name)
    prompt = prompt.replace("{{CLINIC_NAME}}", clinic_name)
    return prompt
