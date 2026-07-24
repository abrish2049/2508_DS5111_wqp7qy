ENV = env
PYTHON = $(ENV)/bin/python3

default:
	@cat makefile

env:
	python3 -m venv $(ENV); $(ENV)/bin/pip install --upgrade pip

update: env
	$(ENV)/bin/pip install -r requirements.txt

pipeline/logs:
	mkdir -p pipeline/logs

lint:
	python -m pylint bin/ tests/ --ignore=validate_schema.py

test: pipeline/logs
	python -m pytest -vv tests

run:
	@echo "Usage: cat video_ids.txt | python bin/extract_transcripts.py | python bin/enrich_transcripts.py"

test_enrich:
	@$(PYTHON) -u bin/enrich_transcripts.py --mock < mock_transcripts.jsonl | $(PYTHON) bin/validate_schema.py
