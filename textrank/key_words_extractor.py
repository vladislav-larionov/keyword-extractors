#!/usr/bin/env python
import argparse
import re
import sys
from datetime import datetime
from pymystem3 import Mystem

from keywords import extract_keywords


def initialize_argument_parser() -> argparse.ArgumentParser:
    """
    Initializes parser of cmd arguments.

    :return: configured argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--path', '-t',
        nargs='?',
        help='PATH to text'
    )
    parser.add_argument(
        '--ratio', '-r',
        nargs='?',
        const=True,
        default=0.2,
        help='Float number (0,1] that defines the length '
             'of the summary. Its a proportion of the original text. Default value: 0.2.\n'
    )
    return parser


def main():
    args = initialize_argument_parser().parse_args()
    path = args.path
    if not path:
        raise RuntimeError("Path is none")
    ratio = args.ratio
    with open(path, encoding='utf-8') as file:
        text = file.read()
    print(extract_keywords(text, ratio, 10))


if __name__ == "__main__":
    main()
