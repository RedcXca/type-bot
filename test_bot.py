import pytest
import os
import tempfile
from datetime import datetime
from storage import Storage
from utils import get_date, strip_year, sort_key, extract_time

USER_ID = "123"


class TestGetDate:
    def test_with_year_uses_that_year(self):
        result = get_date("jan 1 2026 happy new year")
        assert result == datetime(2026, 1, 1)
    
    def test_without_year_uses_current_year(self):
        result = get_date("jan 1 happy new year")
        assert result == datetime(datetime.now().year, 1, 1)
    
    def test_no_date_returns_max(self):
        result = get_date("do laundry")
        assert result == datetime.max
    
    def test_different_months(self):
        assert get_date("feb 14 valentines") == datetime(datetime.now().year, 2, 14)
        assert get_date("dec 25 christmas") == datetime(datetime.now().year, 12, 25)
        assert get_date("oct 31 halloween") == datetime(datetime.now().year, 10, 31)


class TestStripYear:
    def test_strips_year(self):
        assert strip_year("jan 1 2026 happy new year") == "jan 1 happy new year"
    
    def test_no_year_unchanged(self):
        assert strip_year("jan 1 happy new year") == "jan 1 happy new year"
    
    def test_no_date_unchanged(self):
        assert strip_year("do laundry") == "do laundry"


class TestExtractTime:
    def test_24_hour_format(self):
        assert extract_time("jan 7 16:00 event") == (16, 0)
        assert extract_time("jan 7 9:30 event") == (9, 30)

    def test_12_hour_format(self):
        assert extract_time("jan 7 9:30am event") == (9, 30)
        assert extract_time("jan 7 9:30pm event") == (21, 30)
        assert extract_time("jan 7 12:00pm event") == (12, 0)
        assert extract_time("jan 7 12:00am event") == (0, 0)

    def test_24_00_returns_24(self):
        assert extract_time("jan 7 24:00 event") == (24, 0)

    def test_no_time(self):
        assert extract_time("jan 7 event") is None


class TestSortKey:
    def test_dated_before_undated(self):
        dated = {"text": "jan 1 party", "date": "2025-01-01"}
        undated = {"text": "do laundry", "date": None}
        assert sort_key(dated) < sort_key(undated)

    def test_earlier_date_first(self):
        jan = {"text": "jan event", "date": "2025-01-15"}
        feb = {"text": "feb event", "date": "2025-02-15"}
        assert sort_key(jan) < sort_key(feb)

    def test_same_day_sorted_by_time(self):
        nine = {"text": "jan 7 9:00 breakfast", "date": "2025-01-07"}
        ten = {"text": "jan 7 10:00 meeting", "date": "2025-01-07"}
        six_pm = {"text": "jan 7 18:00 dinner", "date": "2025-01-07"}
        assert sort_key(nine) < sort_key(ten) < sort_key(six_pm)

    def test_24_00_sorts_after_23_59(self):
        late = {"text": "jan 7 23:30 late night", "date": "2025-01-07"}
        midnight = {"text": "jan 7 24:00 midnight", "date": "2025-01-07"}
        next_day = {"text": "jan 8 00:30 early morning", "date": "2025-01-08"}
        assert sort_key(late) < sort_key(midnight) < sort_key(next_day)


class TestStorage:
    @pytest.fixture
    def storage(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        s = Storage(path)
        yield s
        os.unlink(path)
    
    def test_add_task_with_year(self, storage):
        date = datetime(2026, 1, 1)
        storage.add_task(USER_ID, "jan 1 happy new year", date)
        
        events = storage.list_tasks(USER_ID)
        assert len(events) == 1
        assert events[0]["text"] == "jan 1 happy new year"
        assert events[0]["date"] == "2026-01-01"
    
    def test_add_task_without_year_uses_current(self, storage):
        date = datetime(datetime.now().year, 3, 15)
        storage.add_task(USER_ID, "mar 15 do something", date)
        
        events = storage.list_tasks(USER_ID)
        assert events[0]["date"] == f"{datetime.now().year}-03-15"
    
    def test_add_task_no_date(self, storage):
        storage.add_task(USER_ID, "do laundry", datetime.max)
        
        events = storage.list_tasks(USER_ID)
        assert len(events) == 1
        assert events[0]["text"] == "do laundry"
        assert events[0]["date"] is None
    
    def test_add_multiple_tasks(self, storage):
        storage.add_task(USER_ID, "task 1", datetime(2025, 1, 1))
        storage.add_task(USER_ID, "task 2", datetime(2025, 2, 1))
        
        events = storage.list_tasks(USER_ID)
        assert len(events) == 2
    
    def test_remove_task(self, storage):
        storage.add_task(USER_ID, "task 1", datetime(2025, 1, 1))
        storage.add_task(USER_ID, "task 2", datetime(2025, 2, 1))
        
        storage.remove_task(USER_ID, 0)
        
        events = storage.list_tasks(USER_ID)
        assert len(events) == 1
        assert events[0]["text"] == "task 2"
    
    def test_edit_task(self, storage):
        storage.add_task(USER_ID, "old task", datetime(2025, 1, 1))
        
        storage.edit_task(USER_ID, 0, "new task", datetime(2025, 6, 15))
        
        events = storage.list_tasks(USER_ID)
        assert events[0]["text"] == "new task"
        assert events[0]["date"] == "2025-06-15"
    
    def test_set_reminder_time(self, storage):
        storage.set_reminder_time(USER_ID, "18:00")
        
        data = storage._read()
        assert data[USER_ID]["reminder_time"] == "18:00"
    
    def test_list_tasks_empty(self, storage):
        events = storage.list_tasks(USER_ID)
        assert events == []


class TestReminderTimeCalculation:
    """Test the reminder time calculation logic used in reminder_loop"""

    def test_one_hour_before_with_time(self):
        from datetime import timedelta
        # Event at 10:30 should remind at 09:30
        event = {"text": "feb 4 10:30 meeting", "date": "2026-02-04"}
        event_date = datetime.strptime(event["date"], "%Y-%m-%d")
        time = extract_time(event["text"])
        hour, minute = time
        event_datetime = event_date.replace(hour=hour, minute=minute)
        remind_at = event_datetime - timedelta(hours=1)
        assert remind_at == datetime(2026, 2, 4, 9, 30)

    def test_one_hour_before_with_24_00(self):
        from datetime import timedelta
        # Event at 24:00 (midnight next day) should remind at 23:00 same day
        event = {"text": "feb 3 24:00 deadline", "date": "2026-02-03"}
        event_date = datetime.strptime(event["date"], "%Y-%m-%d")
        time = extract_time(event["text"])
        hour, minute = time
        if hour >= 24:
            event_date = event_date + timedelta(days=1)
            hour = 0
        event_datetime = event_date.replace(hour=hour, minute=minute)
        remind_at = event_datetime - timedelta(hours=1)
        assert remind_at == datetime(2026, 2, 3, 23, 0)

    def test_one_day_before_no_time(self):
        from datetime import timedelta
        # Event on feb 5 with no time should remind on feb 4
        event = {"text": "feb 5 birthday", "date": "2026-02-05"}
        event_date = datetime.strptime(event["date"], "%Y-%m-%d")
        now = datetime(2026, 2, 4, 3, 30)  # user's reminder time
        tomorrow = now.date() + timedelta(days=1)
        assert event_date.date() == tomorrow
