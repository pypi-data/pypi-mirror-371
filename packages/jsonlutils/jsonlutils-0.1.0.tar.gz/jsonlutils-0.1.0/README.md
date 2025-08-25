# jsonlutils

A lightweight Python library for working with **JSONL (JSON Lines)** and **JSON** files.  
Provides easy conversion, validation, and utility functions.

## ✨ Features

- Convert JSONL → JSON (with metadata)
- Convert JSON → JSONL
- Validate JSONL consistency
- Extract keys from JSONL
- Get statistics (average values, counts, etc.)
- Stream JSONL objects with a generator

## 📦 Installation

```bash```
pip install jsonlutils

import jsonlutils as ju

# Convert JSONL → JSON
ju.convert_jsonl_to_json("data.jsonl", "data.json")

# Convert JSON → JSONL
ju.convert_json_to_jsonl("data.json", "data.jsonl", data_key="data")

# Validate consistency
is_consistent = ju.check_jsonl_is_consistent("data.jsonl")
print("Consistent:", is_consistent)

# Get keys
keys = ju.find_all_jsonl_keys("data.jsonl")
print("Keys found:", keys)