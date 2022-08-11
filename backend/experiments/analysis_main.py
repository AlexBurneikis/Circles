import argparse
from sys import exit as graceful_exit
from typing import Dict

from functions import out_count, in_count

parser = argparse.ArgumentParser(description="Decide Command to Execute")

parser.add_argument(
    "--command",
    type=str,
    # help="""
    # What command to execute. Options:
    # [ out_count, in_count ]
    # """
)

parser.add_argument(
    "--update",
    default=False,
    # help="""
    # Decide whether to run update or, to check existing database
    # """
)

try:
    args = parser.parse_args()
except argparse.ArgumentError:
    print("Argument Error:")
    parser.print_help()
    graceful_exit(0)


def main():
    if args.command == "out_count":
        print(
                out_count(args.update)
            )
    if args.command == "in_count":
        print(
                in_count(args.update)
            )

    return



if __name__ == "__main__":
    main()

