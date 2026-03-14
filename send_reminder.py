import os
import subprocess
from datetime import date, timedelta
from muellmaenner import (
    muellmann_der_woche,
    tonnen_der_woche,
    format_message,
)


def send_whatsapp(phone: str, message: str):
    """Send a WhatsApp message via whatsapp-web.js.

    Requires Node.js and `npm install whatsapp-web.js qrcode-terminal` in the
    project directory.  On first run a QR code is shown for authentication;
    subsequent runs reuse the saved session in the auth cache directory.
    """
    script = os.path.join(os.path.dirname(__file__), "send_whatsapp.js")
    subprocess.run(["node", script, phone, message], check=True)


def main():
    today = date.today()
    next_monday = today + timedelta(days=(7 - today.weekday()))
    year, week, _ = next_monday.isocalendar()

    tonnen = tonnen_der_woche(year, week)
    muellmann = muellmann_der_woche(year, week)

    if not tonnen:
        print(f"No pickups in week {week}/{year} – no message sent.")
        return

    message = format_message(week, next_monday, tonnen, muellmann)

    print(message)

    # phone = os.environ["WHATSAPP_PHONE"]
    # apikey = os.environ["WHATSAPP_APIKEY"]

    # send_whatsapp(phone, apikey, message)


if __name__ == "__main__":
    main()
