import json
from typing import Dict
from collections import Counter

FILE_PATH = "./analysis.json"

def out_count(update) -> Dict:
    if not update():
        data = read_analysis_data()
        return data["out_count"]



def in_count():
    return "in"

def read_analysis_data(path: str=FILE_PATH) -> Dict:
    with open(path, "r", encoding="utf8") as f:
        return json.loads(f.read())

def write_analysis_data(path: str=FILE_PATH, data: Dict=dict()) -> Dict:
    with open(path, "w", encoding="utf8") as f:
        f.write(json.dumps(data, ensure_ascii=False))
