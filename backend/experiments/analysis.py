import argparse
import json
from typing import Dict

parser = argparse.ArgumentParser(description="Decide Command to Execute")

FILE_PATH = "./analysis.json"

parser.add_argument(
        "--command",
        type="str",
        description="""
        What command to execute. Options:
        [ out_count, in_count ]
        """
    )

parser.add_argument(
        "--update",
        default=False,
        description="""
        Decide whether to run update or, to check existing database
        """
    )


def main():
    return

def read_analysis_data(path: str=FILE_PATH) -> Dict:
    with open(path, "r", encoding="utf8") as f:
        return json.loads(f.read())

def write_analysis_data(path: str=FILE_PATH, data: Dict=dict()) -> Dict:
    with open(path, "w", encoding="utf8") as f:
        f.write(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()

