import pytest
import os
import tempfile
from datetime import datetime
from storage import Storage
from utils import get_date, strip_year, sort_key

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


class TestSortKey:
    def test_dated_before_undated(self):
        dated = {"text": "jan 1 party", "date": "2025-01-01"}
        undated = {"text": "do laundry", "date": None}
        assert sort_key(dated) < sort_key(undated)
    
    def test_earlier_date_first(self):
        jan = {"text": "jan event", "date": "2025-01-15"}
        feb = {"text": "feb event", "date": "2025-02-15"}
        assert sort_key(jan) < sort_key(feb)
    
    def test_different_years(self):
        year_2025 = {"text": "dec event", "date": "2025-12-01"}
        year_2026 = {"text": "jan event", "date": "2026-01-15"}
        assert sort_key(year_2025) < sort_key(year_2026)


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
