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
.PHONY: load
load:
	@echo "Snowflake thing...."
	cat data/enriched_transcripts.jsonl | $(PYTHON) bin/load_snowflake.py

IMAGE = abrish2049/ds5111-pipeline:latest

.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE) .

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)

.PHONY: docker-run
docker-run:
	cat data/youtube_ids.txt | docker run -i --env-file .env $(IMAGE)

.PHONY: docker-smoke
docker-smoke:
	cat data/youtube_ids.txt | docker run -i $(IMAGE) sh -c "python bin/clean_ids.py"

.PHONY: docker-clean
docker-clean:
	docker rm -f $$(docker ps -aq) 2>/dev/null || true
	docker rmi $(IMAGE) 2>/dev/null || true
