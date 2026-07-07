ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip

default:
	@cat makefile

env:
	python3 -m venv $(ENV); $(PIP) install --upgrade pip

update: env
	$(PIP) install -r requirements.txt

pipeline/logs:
	mkdir -p pipeline/logs

lint:
	$(PYTHON) -m pylint bin/ tests/ --ignore=validate_schema.py

test: pipeline/logs
	$(PYTHON) -m pytest -vv tests

run:
	@echo "Usage: cat video_ids.txt | $(PYTHON) bin/extract_transcripts.py | $(PYTHON) bin/enrich_transcripts.py"

test_enrich:
	@cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py --mock | $(PYTHON) bin/validate_schema.py
