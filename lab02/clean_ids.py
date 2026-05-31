#!/usr/bin/env python3

import sys
import re
import logging

logging.basicConfig(
    filename='pipeline_autid.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def is_valid_youtube_id(youtube_id):

    if len(youtube_id) != 11:
        return False
    # check vals using regx
    valid_pattern = re.compile(r'^[A-Za-z0-9_-]{11}$')
    if valid_pattern.match(youtube_id):
        return True
    return False

# Read from stdin line by line
try:
    for line in sys.stdin:
        # Strip char
        youtube_id = line.strip()
        # Skip empty
        if youtube_id == '':
            continue
        if is_valid_youtube_id(youtube_id):
            print(youtube_id)
        else:
            logging.error(f"Invalid YouTube ID: '{youtube_id}'")
# added an interupt , instead of a trace error
except KeyboardInterrupt:
    sys.exit(0)
