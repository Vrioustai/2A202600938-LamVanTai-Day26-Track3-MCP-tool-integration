import os
import pytest
import sys
import json

# Add implementation to sys path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import SQLiteAdapter, ValidationError
from init_db import create_database

@pytest.fixture
def db_adapter():
    # Setup test DB
    test_db_path = "test_app.db"
    create_database(test_db_path)
    adapter = SQLiteAdapter(test_db_path)
    yield adapter
    # Teardown
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_list_tables(db_adapter):
    tables = db_adapter.list_tables()
    assert set(tables) == {"students", "courses", "enrollments"}

def test_search_valid(db_adapter):
    results = db_adapter.search("students", filters={"cohort": "A1"})
    assert len(results) == 2
    assert results[0]["name"] == "Alice Smith"

def test_search_invalid_table(db_adapter):
    with pytest.raises(ValidationError):
        db_adapter.search("unknown_table")

def test_search_invalid_column(db_adapter):
    with pytest.raises(ValidationError):
        db_adapter.search("students", filters={"invalid_col": "A1"})

def test_insert_valid(db_adapter):
    res = db_adapter.insert("students", {"name": "David", "cohort": "C3"})
    assert res["inserted"] is True
    assert res["id"] is not None
    
    results = db_adapter.search("students", filters={"cohort": "C3"})
    assert len(results) == 1
    assert results[0]["name"] == "David"

def test_aggregate_valid(db_adapter):
    res = db_adapter.aggregate("courses", metric="SUM", column="credits")
    assert len(res) == 1
    assert res[0]["value"] == 11 # 3 + 4 + 4

def test_aggregate_invalid_metric(db_adapter):
    with pytest.raises(ValidationError):
        db_adapter.aggregate("courses", metric="INVALID", column="credits")

def test_get_table_schema(db_adapter):
    schema = db_adapter.get_table_schema("students")
    assert len(schema) == 3
    col_names = [col["name"] for col in schema]
    assert "id" in col_names
    assert "name" in col_names
    assert "cohort" in col_names
