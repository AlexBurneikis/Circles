"""
Constructs the course graph using the conditions objects and jumps it as a json file.

From `/backend`, run this as:
    `python3 -m data.processors.cache_graph`

Do NOT run this from it's current location.

TODO: This should be moved as a command that can be run by `run_processors.py`
"""

import json
from data.utility.data_helpers import read_data, write_data

OUTPUT_PATH = "./data"

def cache_graph():
    graph = construct_full_graph()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(json.dump(graph))
    return graph

def construct_full_graph():
    pass

if __name__ == "__main__":
    cache_graph()

