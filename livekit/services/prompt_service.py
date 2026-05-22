import logging
from pathlib import Path

logger = logging.getLogger("dental_receptionist.prompt")

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def get_system_prompt(agent_name: str, receptionist_name: str, clinic_name: str) -> str:
    """Load and render system prompt, substituting {{RECEPTIONIST_NAME}} and {{CLINIC_NAME}}."""
    prompt_file = _PROMPTS_DIR / f"{agent_name}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"No prompt file found for agent '{agent_name}' at {prompt_file}"
        )
    prompt = prompt_file.read_text(encoding="utf-8").strip()
    prompt = prompt.replace("{{RECEPTIONIST_NAME}}", receptionist_name)
    prompt = prompt.replace("{{CLINIC_NAME}}", clinic_name)
    logger.info(f"Loaded prompt for agent '{agent_name}' — name={receptionist_name}, clinic={clinic_name}")
    return prompt
