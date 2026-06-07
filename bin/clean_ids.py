#!/usr/bin/env python3
"""Module for validating and filtering YouTube IDs from stdin."""
import sys
import re
import logging

logging.basicConfig(
    filename='pipeline_autid.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def is_valid_youtube_id(youtube_id):
    """Return True if youtube_id is a valid 11-character YouTube ID."""
    if len(youtube_id) != 11:
        return False
    valid_pattern = re.compile(r'^[A-Za-z0-9_-]{11}$')
    return bool(valid_pattern.match(youtube_id))


def main():
    """Read YouTube IDs from stdin, print only valid ones."""
    try:
        for line in sys.stdin:
            youtube_id = line.strip()
            if youtube_id == '':
                continue
            if is_valid_youtube_id(youtube_id):
                print(youtube_id)
            else:
                logging.error("Invalid YouTube ID: '%s'", youtube_id)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
