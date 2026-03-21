import json
import os
from datetime import datetime
import re

class Storage:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump({}, f)

    def _read(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            with open(self.filename, 'w') as f:
                json.dump({}, f)
            return {}

    def _write(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

    def _event_exists(self, events, text, date_str):
        """Check if an event with same text and date already exists."""
        for e in events:
            if e["text"] == text and e.get("date") == date_str:
                return True
        return False

    def add_task(self, user_id, text, date):
        data = self._read()
        data.setdefault(user_id, {"events": []})

        text = text.strip()
        date_str = date.strftime("%Y-%m-%d") if date != datetime.max else None

        if self._event_exists(data[user_id]["events"], text, date_str):
            return False  # Duplicate

        data[user_id]["events"].append({"text": text, "date": date_str})
        self._write(data)
        return True

    def list_tasks(self, user_id):
        return self._read().get(user_id, {}).get("events", [])

    def remove_task(self, user_id, index):
        data = self._read()
        events = data.get(user_id, {}).get("events", [])
        if 0 <= index < len(events):
            removed = events.pop(index)
            # Add to backlog if not duplicate
            data[user_id].setdefault("backlog", [])
            if not self._event_exists(data[user_id]["backlog"], removed["text"], removed.get("date")):
                data[user_id]["backlog"].append(removed)
            self._write(data)
            return True
        return False

    def list_backlog(self, user_id):
        return self._read().get(user_id, {}).get("backlog", [])

    def archive_event(self, user_id, event):
        """Move a specific event to backlog by matching its text and date."""
        data = self._read()
        events = data.get(user_id, {}).get("events", [])
        for i, e in enumerate(events):
            if e["text"] == event["text"] and e.get("date") == event.get("date"):
                removed = events.pop(i)
                # Add to backlog if not duplicate
                data[user_id].setdefault("backlog", [])
                if not self._event_exists(data[user_id]["backlog"], removed["text"], removed.get("date")):
                    data[user_id]["backlog"].append(removed)
                self._write(data)
                return True
        return False

    def edit_task(self, user_id, index, text, date):
        data = self._read()
        events = data.get(user_id, {}).get("events", [])
        if 0 <= index < len(events):
            events[index] = {
                "text": text,
                "date": date.strftime("%Y-%m-%d") if date != datetime.max else None
            }
            self._write(data)
            return True
        return False

    def set_reminder_time(self, user_id, reminder_time):
        data = self._read()
        if user_id not in data:
            data[user_id] = {"events": [], "reminder_time": reminder_time}
        else:
            data[user_id]["reminder_time"] = reminder_time
        self._write(data)
        return True

    def set_timezone(self, user_id, offset):
        data = self._read()
        if user_id not in data:
            data[user_id] = {"events": [], "timezone": offset}
        else:
            data[user_id]["timezone"] = offset
        self._write(data)
        return True

    def _read_birthdays(self):
        try:
            with open('birthdays.json', 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_birthdays(self, data):
        with open('birthdays.json', 'w') as f:
            json.dump(data, f, indent=2)

    def add_birthday(self, user_id, date_key, name):
        """Add a birthday. date_key is 'MM-DD', name is a string."""
        birthdays = self._read_birthdays()
        existing = birthdays.get(date_key, "")
        existing_names = [n.strip() for n in existing.split("/") if n.strip()] if existing else []
        if name.lower() in [n.lower() for n in existing_names]:
            return False
        existing_names.append(name)
        birthdays[date_key] = "/".join(existing_names)
        self._write_birthdays(birthdays)
        return True

    def remove_birthday(self, user_id, date_key, name):
        """Remove a birthday by name from a date."""
        birthdays = self._read_birthdays()
        existing = birthdays.get(date_key, "")
        if not existing:
            return False
        existing_names = [n.strip() for n in existing.split("/") if n.strip()]
        for i, n in enumerate(existing_names):
            if n.lower() == name.lower():
                existing_names.pop(i)
                if not existing_names:
                    del birthdays[date_key]
                else:
                    birthdays[date_key] = "/".join(existing_names)
                self._write_birthdays(birthdays)
                return True
        return False

    def list_birthdays(self, user_id):
        """Return birthdays dict: {'MM-DD': ['name1', 'name2'], ...}"""
        birthdays = self._read_birthdays()
        result = {}
        for date_key, names_str in birthdays.items():
            result[date_key] = [n.strip() for n in names_str.split("/") if n.strip()]
        return result
