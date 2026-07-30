# 2508_DS5111_wqp7qy

A data engineering pipeline for DS5111 that pulls YouTube transcripts, runs them through a Gemini LLM to extract useful metadata, lands everything in Snowflake, and transforms it into clean models using dbt.

---

## What This Does

You give it YouTube video IDs, it fetches the transcripts, and passes them through an LLM enrichment step that pulls out cleaned text, tech terms, and book names. Everything flows through stdin/stdout so you can chain it with other UNIX tools. From there, dbt models running natively inside Snowflake turn the raw JSON payload into a staging view, a deduped video dimension table, fact tables for books and tech terms, and a Jinja generated pivot mart.

---

## Getting Started

### 1. Clone the repo

```bash
git clone git@github.com:abrish2049/2508_DS5111_wqp7qy.git
cd 2508_DS5111_wqp7qy
```

### 2. Set up the VM

```bash
bash scripts/init.sh
bash scripts/init_git_creds.sh
```

### 3. Build the environment

```bash
make env
make update
```

---

## Environment Variables

Create a `.env` file in the repo root. It's already gitignored so you won't accidentally commit it.

| Variable | Required | Description |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes (for real runs) | Your Google Gemini API key |
| `WEBSHARE_USER` | No | Proxy username for YouTube extraction |
| `WEBSHARE_PASSWORD` | No | Proxy password for YouTube extraction |
| `SF_USER` / `SF_PASSWORD` | Yes (for Snowflake load) | Snowflake login creds |
| `SF_ACCOUNT` / `SF_WAREHOUSE` / `SF_DATABASE` / `SF_SCHEMA` / `SF_ROLE` | Yes (for Snowflake load) | Snowflake connection context |

```bash
export GEMINI_API_KEY=your_key_here
export WEBSHARE_USER=your_user
export WEBSHARE_PASSWORD=your_password
```

---

## Running and Testing

```bash
# check code quality
make lint

# run all tests
make test

# test enrichment pipeline with mock (no API key needed)
make test_enrich

# run the real pipeline
echo "dQw4w9WgXcQ" | env/bin/python3 bin/extract_transcripts.py | env/bin/python3 bin/enrich_transcripts.py
```

If everything is set up right you should see:

```
24 passed, 1 skipped, 1 xfailed
Your code has been rated at 10.00/10
```

---

## Running with Docker

Build the image locally, or pull the published one from Docker Hub (`abrish2049/ds5111-pipeline:latest`).

```bash
make docker-build
```

### Smoke test (no credentials needed)

Validates ID filtering only:

```bash
make docker-smoke
```

### Full pipeline (requires `.env`)

Runs clean, extract, enrich, and load into Snowflake:

```bash
make docker-run
```

### Push to Docker Hub

```bash
make docker-push
```

### Clean-room test

Removes local containers and image, forcing a fresh pull from Docker Hub on next run:

```bash
make docker-clean
make docker-run
```

---

## Data Transforms with dbt

Once raw JSON lands in Snowflake's `RAW_TRANSCRIPTS` table, everything downstream is handled by a dbt project that runs natively inside Snowflake, no external server needed.

### Project layout

* `dbt_project.yml`, `packages.yml`, `profiles.yml` live at the repo root, this is what tells Snowflake "this is a dbt project."
* `models/` holds the actual transforms:
  * `stg_youtube_transcripts.sql` (view) parses the raw VARIANT payload into typed columns.
  * `dim_videos.sql` (table) is a deduped one-row-per-video dimension using `QUALIFY ROW_NUMBER()` to keep only the latest load per `video_id`.
  * `fct_book_mentions.sql` and `fct_tech_terms.sql` (tables) flatten the tech term and book name arrays into fact rows.
  * `mart_tech_term_pivot.sql` uses a Jinja for loop to dynamically pivot tech term counts per video instead of hardcoding a column per term.
  * `schema.yml` holds `dbt_expectations` data quality tests: regex checks on `video_id`, uniqueness and not null checks, column shape checks, relationship checks, and length checks.
* `transform/` still has the original raw SQL from an earlier lab (pre-dbt). It's kept around for reference but the dbt models in `models/` are what actually run now.

### Running it in Snowflake

All of this runs from a Snowflake worksheet against the Git integration, no local dbt install needed:

```sql
USE ROLE DS5111_STUDENT_ROLE;
USE DATABASE DS5111_DB;
USE SCHEMA WQP7QY;

-- pull the latest code from GitHub
ALTER GIT REPOSITORY DS5111_GIT_STAGE FETCH;

-- point Snowflake at the dbt project (rerun this after every push)
CREATE OR REPLACE DBT PROJECT ds5111_pipeline
  FROM '@DS5111_GIT_STAGE/branches/main'
  EXTERNAL_ACCESS_INTEGRATIONS = (dbt_external_access);

-- build the models
EXECUTE DBT PROJECT ds5111_pipeline ARGS = 'run';

-- run the data quality tests
EXECUTE DBT PROJECT ds5111_pipeline ARGS = 'test';
```

All 7 tests should come back green. If you need to debug a failing test, add `--store-failures` to the test args and Snowflake will materialize the exact bad rows into an audit table you can query directly.
