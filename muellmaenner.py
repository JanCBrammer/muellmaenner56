from datetime import date, timedelta
from icalendar import Calendar


TRASH_ICONS = {
    "bio": ("🟢", "Bio"),
    "altpapier": ("🔵", "Altpapier"),
    "gelber": ("🟡", "Gelber Sack"),
    "restabfall": ("⚫", "Restabfall"),
    "weihnachtsbaum": ("🌲", "Weihnachtsbaum"),
}
MUELLMAENNER = [
    ("Joachim", "#4a90d9"),
    ("Dirk", "#e07b3a"),
    ("Daniel", "#5bb36a"),
    ("Jan", "#b55ab5"),
    ("Jannik", "#c0a030"),
]
KALENDER = "abfuhrkalender.ics"
WOCHENTAGE = [
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
]
ROTATION_START_YEAR = 2026
ROTATION_START_WEEK = 12


def muellmann_der_woche(year: int, week: int) -> tuple[str, str]:
    """Return the (name, color) of the person responsible for the given ISO week."""
    start = date.fromisocalendar(ROTATION_START_YEAR, ROTATION_START_WEEK, 1)
    current = date.fromisocalendar(year, week, 1)
    delta_weeks = (current - start).days // 7

    return MUELLMAENNER[delta_weeks % len(MUELLMAENNER)]


def tonnen_der_woche(year: int, week: int) -> list[tuple[str, date]]:
    """Return a list of (bin type, collection date) for the given ISO week."""
    monday = date.fromisocalendar(year, week, 1)
    sunday = monday + timedelta(days=6)

    with open(KALENDER, "rb") as f:
        cal = Calendar.from_ical(f.read())

    seen = set()
    pickups = []
    for component in cal.walk():
        if component.name != "VEVENT":
            continue
        dtstart = component.get("DTSTART").dt
        event_date = dtstart.date() if hasattr(dtstart, "date") else dtstart
        if monday <= event_date <= sunday:
            summary = str(component.get("SUMMARY"))
            if summary not in seen:
                seen.add(summary)
                pickups.append((summary, event_date))

    pickups.sort(key=lambda x: x[1])  # sort by date within the week

    return pickups


def format_message(
    week: int,
    next_monday: date,
    tonnen: list[tuple[str, date]],
    muellmann: tuple[str, str],
) -> str:
    """Format the weekly WhatsApp reminder message."""
    name, _ = muellmann
    bin_lines = "\n".join(
        f"  • {tonne} ({WOCHENTAGE[tag.weekday()]})" for tonne, tag in tonnen
    )
    return (
        f"🗑️ Müll KW{week} ({next_monday.strftime('%d.%m.')} – "
        f"{(next_monday + timedelta(days=6)).strftime('%d.%m.')})\n\n"
        f"{bin_lines}\n\n"
        f"👤 Zuständig: *{name}*"
    )
