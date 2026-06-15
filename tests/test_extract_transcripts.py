import sys
import io
import json
import pytest
from youtube_transcript_api import YouTubeTranscriptApi
from bin.extract_transcripts import main


class MockTranscriptContainer:
    def to_raw_data(self):
        return [{"start": 10.5, "text": "Automated container tracking loop text entry."}]


def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", lambda self, vid: MockTranscriptContainer())
    monkeypatch.setattr(sys, "stdin", io.StringIO("fake_video_999\n"))

    main()

    lines = capsys.readouterr().out.strip().split("\n")
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed["raw_text"]


def test_extract_transcripts_handles_error_gracefully(monkeypatch, capsys):
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", lambda self, vid: (_ for _ in ()).throw(Exception("bad id")))
    monkeypatch.setattr(sys, "stdin", io.StringIO("INVALID_VIDEO_ID\n"))

    main()

    assert capsys.readouterr().out.strip() == ""
