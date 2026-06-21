#!/usr/bin/env python3
import sys
import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# TODO 1: validate key and init client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.critical("GEMINI_API_KEY is not set. Aborting pipeline.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# TODO 2: schema contract
response_schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "video_id": types.Schema(type=types.Type.STRING),
        "cleaned_text": types.Schema(type=types.Type.STRING),
        "tech_terms": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING)
        ),
        "book_names": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING)
        ),
    },
    required=["video_id", "cleaned_text", "tech_terms", "book_names"]
)

generate_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=response_schema
)


def main():
    logging.info("Pipeline Step 2B (LLM Enrichment) started.")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # TODO 3: safe per-row deserialization
        try:
            record = json.loads(line)
        except json.JSONDecodeError as e:
            logging.error("Skipping malformed line: %s", e)
            continue

        video_id = record.get("video_id", "unknown")
        raw_text = record.get("raw_text", "")
        logging.info("Enriching transcript for video: %s", video_id)

        prompt = (
            f"You are a data engineering assistant. Given the following raw lecture transcript, "
            f"return a JSON object with:\n"
            f"- video_id: the original video ID (string)\n"
            f"- cleaned_text: transcript with timestamps removed and cleaned up (string)\n"
            f"- tech_terms: technical terms, tools, or technologies mentioned (array of strings)\n"
            f"- book_names: book titles mentioned (array of strings)\n\n"
            f"video_id: {video_id}\nraw_text: {raw_text}"
        )

        try:
            # TODO 4: model invocation and immediate flush
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=generate_config
            )
            sys.stdout.write(json.dumps(json.loads(response.text)) + "\n")
            sys.stdout.flush()

        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Gemini API call failed for video %s: %s", video_id, e)
            continue

    logging.info("Pipeline Step 2B (LLM Enrichment) finished.")


if __name__ == '__main__':
    main()
