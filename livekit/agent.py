import json
import logging
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()  # must run before any env var is read

from livekit.agents import JobContext, WorkerOptions, cli, llm, AutoSubscribe, RoomInputOptions
from livekit.agents.beta.tools import EndCallTool
from livekit.agents.voice import Agent, AgentSession
from livekit import rtc

from config import Settings
from services.stt_service import create_stt_service
from services.tts_service import create_tts_service
from services.llm_service import create_llm_service
from services.booking_service import DentalClinicFnc
from services.prompt_service import get_system_prompt

try:
    from livekit.plugins import noise_cancellation
except ImportError:
    noise_cancellation = None

# Setup logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dental_receptionist")

AGENT_NAME = os.environ.get("AGENT_NAME", "dental_receptionist")

async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room {ctx.room.name}...")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info("Successfully connected to room.")

    # 1. Validate environment configuration
    try:
        Settings.validate()
    except ValueError as val_err:
        logger.error(f"Configuration failed: {val_err}")
        # Terminate job gracefully if critical settings are missing
        ctx.shutdown()
        return

    # 2. Detect caller's preferred language from participant metadata
    lang = "en"
    for participant in ctx.room.remote_participants.values():
        try:
            meta = json.loads(participant.metadata or "{}")
            lang = meta.get("language", "en")
        except Exception:
            pass
        break
    logger.info(f"Caller language preference: {lang}")

    # 3. Instantiate VAD, STT, LLM, and TTS services
    from livekit.plugins import silero
    vad_instance = silero.VAD.load()

    stt_instance = create_stt_service(language="multi")
    llm_instance = create_llm_service()
    tts_instance = create_tts_service()

    # 4. Instantiate the Function Context (Booking tool) and find tools
    fnc_ctx = DentalClinicFnc()
    tools = llm.find_function_tools(fnc_ctx)

    system_prompt = get_system_prompt(
        AGENT_NAME,
        receptionist_name=Settings.RECEPTIONIST_NAME,
        clinic_name=Settings.CLINIC_NAME,
        lang=lang,
    )

    agent = Agent(
        instructions=system_prompt,
    )

    # 6. Configure BVC Noise Cancellation if available
    room_input_options = None
    if RoomInputOptions is not None and noise_cancellation is not None:
        try:
            room_input_options = RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC()
            )
            logger.info("Background Voice Cancellation (BVC) noise cancellation enabled.")
        except Exception as err:
            logger.warning(f"Could not configure BVC noise cancellation: {err}")

    # 7. Initialize the AgentSession
    session = AgentSession(
        stt=stt_instance,
        vad=vad_instance,
        llm=llm_instance,
        tts=tts_instance,
        tools=[*tools, EndCallTool()],
    )

    # 8. Start the agent session in the room
    if room_input_options is not None:
        await session.start(agent, room=ctx.room, room_input_options=room_input_options)
    else:
        await session.start(agent, room=ctx.room)
        
    logger.info("Agent session started successfully.")

    # 9. Shut down cleanly when the caller leaves the room
    @ctx.room.on("participant_disconnected")
    def on_participant_left(participant: rtc.RemoteParticipant) -> None:
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_STANDARD:
            logger.info(f"Caller {participant.identity} disconnected — closing session.")
            asyncio.ensure_future(session.aclose())

    # Safety net: if booking succeeded, close session after TTS finishes
    @session.on("agent_speech_committed")
    def on_speech_committed(msg) -> None:
        text = getattr(msg, "content", "") or ""
        if "BOOKING_SUCCESS" in text or "token number" in text.lower() or "token எண்" in text.lower():
            logger.info("Booking farewell detected — scheduling session close.")
            async def _close():
                await asyncio.sleep(3)
                await session.aclose()
            asyncio.ensure_future(_close())

    # 10. Greet in caller's chosen language
    name = Settings.RECEPTIONIST_NAME
    clinic = Settings.CLINIC_NAME
    greeting = (
        f"வணக்கம்! {clinic}-க்கு அழைத்தமைக்கு நன்றி. நான் {name}. "
        "உங்கள் appointment book பண்ண help பண்றேன். முதலில் உங்கள் பெயர் சொல்லுங்கள்?"
        if lang == "ta" else
        f"Hello! Thank you for calling {clinic}. This is {name} speaking. "
        "I'll help you book an appointment. Could I start with your full name, please?"
    )
    await session.say(greeting, allow_interruptions=True)


def prewarm(proc_ctx):
    # Pre-download and cache Silero VAD model to optimize agent boot time
    logger.info("Prewarming Silero VAD model...")
    from livekit.plugins import silero
    silero.VAD.load()


if __name__ == "__main__":
    if os.environ.get("HF_SPACE") == "1":
        import health
        health.start(port=7860)
        logger.info("HF Space health server started on port 7860")

    logger.info(f"LIVEKIT_URL={os.environ.get('LIVEKIT_URL', 'NOT SET')}")
    logger.info(f"LIVEKIT_API_KEY={'SET' if os.environ.get('LIVEKIT_API_KEY') else 'NOT SET'}")

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            ws_url=os.environ.get("LIVEKIT_URL"),
            api_key=os.environ.get("LIVEKIT_API_KEY"),
            api_secret=os.environ.get("LIVEKIT_API_SECRET"),
        )
    )
