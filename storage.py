import json
import os
from datetime import datetime

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

    def add_task(self, user_id, event_obj):
        data = self._read()
        data.setdefault(user_id, {"events": []})
        data[user_id]["events"].append(event_obj)
        self._write(data)

    def list_tasks(self, user_id):
        return self._read().get(user_id, {}).get("events", [])

    def remove_task(self, user_id, index):
        data = self._read()
        events = data.get(user_id, {}).get("events", [])
        if 0 <= index < len(events):
            events.pop(index)
            self._write(data)
            return True
        return False

    def edit_task(self, user_id, index, event_obj):
        data = self._read()
        events = data.get(user_id, {}).get("events", [])
        if 0 <= index < len(events):
            events[index] = event_obj
            self._write(data)
            return True
        return False
