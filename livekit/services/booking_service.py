import json
import logging
import os
import aiohttp
from datetime import datetime
from pathlib import Path
from livekit.agents import llm
from config import Settings

logger = logging.getLogger("dental_receptionist.booking")

TIMEOUT = aiohttp.ClientTimeout(total=15)
_COUNTER_FILE = Path(os.environ.get("TOKEN_COUNTER_DIR", str(Path(__file__).parent.parent))) / ".token_counter.json"


def _next_daily_token() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    data = {}
    if _COUNTER_FILE.exists():
        try:
            data = json.loads(_COUNTER_FILE.read_text())
        except Exception:
            data = {}
    if data.get("date") != today:
        data = {"date": today, "counter": 0}
    data["counter"] += 1
    _COUNTER_FILE.write_text(json.dumps(data))
    return data["counter"]


class DentalClinicFnc:

    @llm.function_tool(
        description=(
            "Get the current date and time. Call this at the start of every conversation "
            "so you know what 'today', 'tomorrow', and 'next week' mean."
        )
    )
    async def get_current_datetime(self) -> str:
        now = datetime.now()
        return now.strftime("Today is %A, %B %d, %Y. Current time is %I:%M %p.")

    @llm.function_tool(
        description=(
            "Fetch all available appointment time slots from the clinic system. "
            "Call this once the caller gives their preferred date so you can offer real available slots."
        )
    )
    async def get_available_times(self) -> str:
        """Fetch available time slots from the clinic system."""
        get_times_url = os.environ.get(
            "N8N_GET_TIMES_URL",
            "https://n8n.basivo.in/webhook/get-appointment-times",
        )
        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                async with session.get(get_times_url) as response:
                    if response.status in [200, 201]:
                        import json
                        slots = await response.json()
                        available = [s for s in slots if s.get("Available") == "Yes"]
                        if not available:
                            return "No available slots found. Ask the caller for their preferred time."
                        lines = [f"{s['Day']} at {s['Time']}" for s in available]
                        result = "Available slots: " + ", ".join(lines)
                        logger.info(result)
                        return result
                    else:
                        text = await response.text()
                        logger.warning(f"get-appointment-times returned {response.status}: {text}")
                        return "Could not fetch available times. Ask the caller for their preferred time directly."
        except Exception as e:
            logger.error(f"get_available_times failed: {e}")
            return "Could not reach the scheduling system. Ask the caller for their preferred time directly."

    @llm.function_tool(
        description=(
            "Book the appointment once the caller has confirmed all 4 details: "
            "full name, phone number (digit-by-digit confirmed), date, and time."
        )
    )
    async def book_appointment(
        self,
        name: str,
        phone: str,
        date: str,
        time: str,
    ) -> str:
        """Book a dental clinic appointment.

        Args:
            name: The caller's full name.
            phone: The caller's confirmed phone number (digits only, no spaces).
            date: The appointment date.
            time: The appointment time.
        """
        webhook_url = Settings.N8N_WEBHOOK_URL
        if not webhook_url:
            logger.error("N8N_WEBHOOK_URL not configured.")
            return "Booking failed: webhook URL is not configured."

        payload = {
            "name": name,
            "phone": phone,
            "date": date,
            "time": time,
            "clinic": os.environ.get("CLINIC_NAME", "Demo Clinic"),
        }
        logger.info(f"Booking payload → {payload}")

        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                async with session.post(webhook_url, json=payload) as response:
                    text = await response.text()
                    if response.status in [200, 201]:
                        token = _next_daily_token()
                        logger.info(f"Booking succeeded. Token: {token}. Response: {text}")
                        return (
                            f"BOOKING_SUCCESS|token={token}|name={name}|date={date}|time={time}"
                        )
                    else:
                        logger.error(f"Booking failed — status {response.status}: {text}")
                        return f"Booking failed (status {response.status}). Please try again."
        except Exception as e:
            logger.error(f"Booking exception: {e}")
            return "Booking failed due to a network error. Please try again shortly."
