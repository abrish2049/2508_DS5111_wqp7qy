#!/usr/bin/env python3
"""Fetches raw YouTube transcripts and emits JSONL to stdout."""

import sys
import os
import json
import logging
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

load_dotenv()

logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """Reads video IDs from stdin and writes transcript JSONL to stdout."""
    proxy_user = os.getenv("WEBSHARE_USER")
    proxy_pass = os.getenv("WEBSHARE_PASSWORD")

    if proxy_user and proxy_pass:
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_user,
                proxy_password=proxy_pass,
            )
        )
    else:
        ytt_api = YouTubeTranscriptApi()

    for line in sys.stdin:
        video_id = line.strip()
        if not video_id:
            continue

        try:
            fetched_transcript = ytt_api.fetch(video_id)
            transcript_list = fetched_transcript.to_raw_data()
            raw_text = " ".join([f"[{item['start']}] {item['text']}" for item in transcript_list])
            payload = {"video_id": video_id, "raw_text": raw_text}
            sys.stdout.write(json.dumps(payload) + "\n")
            sys.stdout.flush()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Failed to fetch transcript for %s: %s", video_id, str(e))
            continue


if __name__ == '__main__':
    main()
