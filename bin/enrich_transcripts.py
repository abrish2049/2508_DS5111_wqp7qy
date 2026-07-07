#!/usr/bin/env python3
"""Transcript enrichment pipeline using pluggable LLM strategy pattern."""
import sys
import os
import json
import logging
import argparse
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# =====================================================================
# 1. THE CONTRACT (Interface)
# =====================================================================
class LLMStrategy(ABC):
    """Abstract base class defining the enrichment strategy contract."""

    @abstractmethod
    def enrich(self, record: dict) -> dict:
        """Must accept a raw transcript record and return an enriched record."""


# =====================================================================
# 2. MOCK STRATEGY (for testing without live API)
# =====================================================================
class MockLLMStrategy(LLMStrategy):
    """Returns a deterministic fake response for testing."""

    def __init__(self, fixed_response: dict):
        self.fixed_response = fixed_response

    def enrich(self, record: dict) -> dict:
        """Injects the incoming video_id into the static fixed response."""
        return {**self.fixed_response, "video_id": record["video_id"]}


# =====================================================================
# 3. ENRICHMENT ENGINE (Invariant pipeline orchestrator)
# =====================================================================
class EnrichmentEngine:
    """Streams JSONL from stdin through the injected LLM strategy."""

    def __init__(self, strategy: LLMStrategy):
        self.strategy = strategy

    def run_stream(self):
        """Reads stdin line by line, enriches each record, writes to stdout."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                logging.error("Skipping malformed line: %s", e)
                continue

            try:
                result = self.strategy.enrich(record)
                sys.stdout.write(json.dumps(result) + "\n")
                sys.stdout.flush()
            except Exception as e:  # pylint: disable=broad-exception-caught
                logging.error("Enrichment failed for record: %s", e)
                continue

class GeminiStrategy(LLMStrategy):
    """Concrete LLM strategy that calls the Gemini API to enrich transcripts."""

    def __init__(self, client):
        self.client = client
        self.generate_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=types.Schema(
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
        )

    def enrich(self, record: dict) -> dict:
        """Builds prompt from record, calls Gemini, returns enriched dict."""
        video_id = record.get("video_id", "unknown")
        raw_text = record.get("raw_text", "")
        prompt = (
            f"You are a data engineering assistant. Return a JSON object with:\n"
            f"- video_id: the original video ID (string)\n"
            f"- cleaned_text: transcript with timestamps removed (string)\n"
            f"- tech_terms: technical terms mentioned (array of strings)\n"
            f"- book_names: book titles mentioned (array of strings)\n\n"
            f"video_id: {video_id}\nraw_text: {raw_text}"
        )
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=self.generate_config
        )
        return json.loads(response.text)

# =====================================================================
# 4. COMPOSITION ROOT
# =====================================================================
def main(argv=None):
    """Parses CLI args, selects strategy, and runs the enrichment engine."""
    parser = argparse.ArgumentParser(description="Multi-Source Transcript Enrichment Node.")
    parser.add_argument("--mock", action="store_true", help="Run with mock strategy, no API key needed.")
    args = parser.parse_args(argv)

    logging.info("Pipeline Step 2B (LLM Enrichment) started.")

    if args.mock:
        fixed = {
            "video_id": "",
            "cleaned_text": "mock cleaned text",
            "tech_terms": ["mock term"],
            "book_names": []
        }
        selected_strategy = MockLLMStrategy(fixed_response=fixed)
    else:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.critical("GEMINI_API_KEY is not set. Aborting pipeline.")
            sys.exit(1)
        client = genai.Client(api_key=api_key)
        selected_strategy = GeminiStrategy(client)

    engine = EnrichmentEngine(selected_strategy)
    engine.run_stream()

    logging.info("Pipeline Step 2B (LLM Enrichment) finished.")


if __name__ == "__main__":
    main()