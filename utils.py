from datetime import datetime, timedelta
import re


def parse_backlog_filter(filter_str):
    """Parse filter like '2026' or 'feb 2026'. Returns (year, month) tuple."""
    filter_str = filter_str.strip().lower()
    months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
              'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}

    parts = filter_str.split()
    year = None
    month = None

    for part in parts:
        if part in months:
            month = months[part]
        elif part.isdigit() and len(part) == 4:
            year = int(part)

    return (year, month)


def matches_date_filter(date_str, year, month):
    """Check if date string matches year/month filter."""
    if not date_str:
        return False
    parts = date_str.split('-')
    if year and parts[0] != str(year):
        return False
    if month and int(parts[1]) != month:
        return False
    return True


def format_tz(tz):
    """Format timezone offset for display (e.g., UTC-5, UTC5.5)"""
    tz_str = str(int(tz)) if tz == int(tz) else str(tz)
    return f"UTC{tz_str}"


def local_to_utc(local_dt, tz_offset):
    """Convert local datetime to UTC given timezone offset"""
    return local_dt - timedelta(hours=tz_offset)


def get_reminder_time_utc(reminder_time_str, tz_offset, reference_date):
    """Convert HH:MM reminder time string to UTC datetime"""
    hour, minute = map(int, reminder_time_str.split(':'))
    local_dt = datetime.combine(reference_date, datetime.min.time()).replace(hour=hour, minute=minute)
    return local_to_utc(local_dt, tz_offset)


def get_event_utc_datetime(event, tz_offset):
    """Get event's datetime in UTC. Returns None if event has no date/time."""
    date_str = event.get("date")
    if not date_str:
        return None
    event_date = datetime.strptime(date_str, "%Y-%m-%d")
    time = extract_time(event["text"])
    if not time:
        return None
    hour, minute = time
    if hour >= 24:
        event_date = event_date + timedelta(days=1)
        hour = 0
    local_dt = event_date.replace(hour=hour, minute=minute)
    return local_to_utc(local_dt, tz_offset)

# remove year from event text if present
def strip_year(text: str) -> str:
    text = re.sub(r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+[0-3]?\d)\s+\d{4}', r'\1', text, flags=re.I)
    return text

# returns date found in string, defaults to current year
# only supports formats like oct 20 or oct 20 2025
def get_date(event: str):
    # consumes month, then spaces, then day, then optional year
    DATE_RE = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+[0-3]?\d(?:\s+\d{4})?\b', re.I)
    m = DATE_RE.search(event)
    if not m:
        return datetime.max
    s = m.group(0)
    try:
        return datetime.strptime(s, "%b %d %Y")
    except ValueError:
        return datetime.strptime(s, "%b %d").replace(year=datetime.now().year)

def natural_sort(text):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    return [convert(c) for c in re.split('([0-9]+)', text)]

def extract_time(text):
    """Extract time from text like 'jan 7 16:00 event' or 'jan 7 9:20am event'"""
    # Match time patterns: 16:00, 9:20, 9:20am, 9:20 am, etc.
    time_re = re.compile(r'\b(\d{1,2}):(\d{2})\s*(am|pm)?\b', re.I)
    m = time_re.search(text)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    ampm = m.group(3)
    if ampm:
        ampm = ampm.lower()
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
    return (hour, minute)

def sort_key(event):
    text = event["text"]
    date_str = event.get("date")
    if date_str:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        time = extract_time(text)
        if time:
            hour, minute = time
            if hour >= 24:
                date = date + timedelta(days=1)
                hour = 0
            date = date.replace(hour=hour, minute=minute)
    else:
        date = datetime.max
    return (0, date) if date != datetime.max else (1, natural_sort(text))

