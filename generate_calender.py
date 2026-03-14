from datetime import date, timedelta
from collections import defaultdict
from icalendar import Calendar

from muellmaenner import (
    KALENDER,
    TRASH_ICONS,
    muellmann_der_woche,
)


def trash_icon(summary: str) -> tuple[str, str]:
    key = summary.lower().split()[0]
    return TRASH_ICONS.get(key, ("♻️", summary))


def load_events() -> dict[date, list[str]]:
    """Return {date: [summary, ...]} for all events in the calendar."""
    events: dict[date, list[str]] = defaultdict(list)
    with open(KALENDER, "rb") as f:
        cal = Calendar.from_ical(f.read())
    for component in cal.walk():
        if component.name != "VEVENT":
            continue
        dtstart = component.get("DTSTART").dt
        event_date = dtstart.date() if hasattr(dtstart, "date") else dtstart
        summary = str(component.get("SUMMARY"))
        events[event_date].append(summary)
    return events


def months_range(events: dict[date, list]) -> list[tuple[int, int]]:
    """Return list of (year, month) tuples covering all events."""
    dates = sorted(events)
    start, end = dates[0], dates[-1]
    result = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        result.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return result


def render_month(year: int, month: int, events: dict[date, list[str]]) -> str:
    MONTH_NAMES = [
        "Januar",
        "Februar",
        "März",
        "April",
        "Mai",
        "Juni",
        "Juli",
        "August",
        "September",
        "Oktober",
        "November",
        "Dezember",
    ]
    today = date.today()

    first = date(year, month, 1)
    # Monday of the week containing the 1st
    start = first - timedelta(days=first.weekday())

    # Last day of month
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)

    rows = []
    cursor = start
    while cursor <= last or cursor.month != month:
        if cursor > last and cursor.weekday() == 0:
            break
        iso = cursor.isocalendar()
        muellmann, color = muellmann_der_woche(iso[0], iso[1])

        cells = []
        # Week number cell
        cells.append(
            f'<td class="kw" style="border-left:4px solid {color};color:{color}">'
            f'<span class="kw-num">KW{iso[1]}</span>'
            f'<span class="kw-person" style="color:{color}">{muellmann}</span>'
            f"</td>"
        )

        for _ in range(7):
            day_events = events.get(cursor, [])
            extra = "other-month" if cursor.month != month else ""
            extra += " today" if cursor == today else ""

            event_html = ""
            for summary in day_events:
                icon, label = trash_icon(summary)
                event_html += f'<span class="event" title="{label}">{icon} </span>'

            cells.append(
                f'<td class="{extra.strip()}">'
                f'<span class="day-num">{cursor.day}</span>'
                f"{event_html}"
                f"</td>"
            )
            cursor += timedelta(days=1)

        rows.append(f"<tr>{''.join(cells)}</tr>")

    month_label = f"{MONTH_NAMES[month - 1]} {year}"
    return f"""
  <section class="month">
    <h2>{month_label}</h2>
    <table>
      <thead><tr>
        <th>KW</th>
        <th>Mo</th><th>Di</th><th>Mi</th><th>Do</th><th>Fr</th><th>Sa</th><th>So</th>
      </tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
  </section>"""


def build_legend() -> str:
    icon_items = ""
    for icon, label in TRASH_ICONS.values():
        icon_items += f'<span class="legend-item">{icon} {label}</span>'

    return f"""
  <div class="legend">
    <div class="legend-group">{icon_items}</div>
  </div>"""


def generate() -> None:
    events = load_events()
    months = months_range(events)

    month_html = "\n".join(render_month(y, m, events) for y, m in months)
    legend_html = build_legend()

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Müllkalender 2026</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, sans-serif;
      background: #f0f0f0;
      color: #222;
      padding: 2rem 1.5rem;
    }}
    h1 {{ font-size: 1.5rem; margin-bottom: 0.4rem; }}
    .subtitle {{ color: #666; font-size: 0.9rem; margin-bottom: 2rem; }}
    .month {{ margin-bottom: 2.5rem; }}
    .month h2 {{
      font-size: 1.1rem;
      margin-bottom: 0.6rem;
      color: #444;
    }}
    table {{
      border-collapse: collapse;
      background: #fff;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
      width: 100%;
      max-width: 800px;
    }}
    thead th {{
      padding: 0.5rem 0.3rem;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: .04em;
      color: #888;
      border-bottom: 1px solid #eee;
    }}
    td {{
      padding: 0.3rem 0.4rem;
      border: 1px solid #f0f0f0;
      vertical-align: top;
      min-width: 2.4rem;
      min-height: 3.5rem;
    }}
    td.other-month .day-num {{ color: #ccc; }}
    .day-num {{
      font-size: 0.8rem;
      font-weight: 600;
      display: block;
      margin-bottom: 0.2rem;
    }}
    td.kw {{
      background: #fafafa;
      border-right: 2px solid #e5e5e5;
      min-width: 5rem;
      vertical-align: middle;
      text-align: center;
      padding: 0.4rem 0.5rem;
    }}
    .kw-num {{
      display: block;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: .03em;
    }}
    .kw-person {{
      display: block;
      font-size: 0.75rem;
      font-weight: 600;
      margin-top: 0.15rem;
    }}
    .event {{
      display: block;
      font-size: 0.7rem;
      line-height: 1.3;
      white-space: nowrap;
    }}
    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      max-width: 800px;
      margin-bottom: 2.5rem;
    }}
    .legend-group {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      align-items: center;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 0.35rem;
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 20px;
      padding: 0.25rem 0.7rem;
      font-size: 0.82rem;
    }}
    .legend-dot {{
      width: 9px; height: 9px;
      border-radius: 50%;
      flex-shrink: 0;
    }}
  </style>
</head>
<body>
  <h1>🗑️ Müllmänner 2026</h1>
  {legend_html}
  {month_html}
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    generate()
