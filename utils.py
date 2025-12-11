from datetime import datetime
import re

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

def sort_key(event):
    text = event["text"]
    date_str = event.get("date")
    if date_str:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        date = datetime.max
    return (0, date) if date != datetime.max else (1, natural_sort(text))

