import os
import json
import pytest
from jsonl_converter_utils import (
    convert_jsonl_to_json,
    convert_json_to_jsonl,
    check_jsonl_is_consistent,
    find_all_jsonl_keys,
    get_list_of_json_objects_from_jsonl,
    get_number_of_json_objects_in_jsonl,
)


TEST_JSONL = "test.jsonl"
TEST_JSON = "test.json"
RECONVERTED_JSONL = "reconverted.jsonl"

@pytest.fixture
def sample_jsonl_file():
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
        {"id": 3, "value": 30},
    ]
    with open(TEST_JSONL, "w", encoding="utf-8") as f:
        for obj in data:
            f.write(json.dumps(obj) + "\n")
    yield data
    for file in [TEST_JSONL, TEST_JSON, RECONVERTED_JSONL]:
        if os.path.exists(file):
            os.remove(file)

def test_convert_jsonl_to_json(sample_jsonl_file):
    convert_jsonl_to_json(TEST_JSONL, TEST_JSON)
    assert os.path.exists(TEST_JSON)
    with open(TEST_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "data" in data
    assert len(data["data"]) == 3

def test_check_jsonl_is_consistent(sample_jsonl_file):
    assert check_jsonl_is_consistent(TEST_JSONL)

def test_find_all_jsonl_keys(sample_jsonl_file):
    keys = find_all_jsonl_keys(TEST_JSONL)
    assert "id" in keys
    assert "value" in keys

def test_convert_json_to_jsonl(sample_jsonl_file):
    convert_jsonl_to_json(TEST_JSONL, TEST_JSON)
    convert_json_to_jsonl(TEST_JSON, RECONVERTED_JSONL, data_key="data")
    assert os.path.exists(RECONVERTED_JSONL)
    objs = get_list_of_json_objects_from_jsonl(RECONVERTED_JSONL)
    assert len(objs) == 3

def test_get_number_of_json_objects_in_jsonl(sample_jsonl_file):
    num, total = get_number_of_json_objects_in_jsonl(TEST_JSONL)
    assert num == 3
    assert total == 3