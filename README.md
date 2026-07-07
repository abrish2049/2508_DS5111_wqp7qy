# 2508_DS5111_wqp7qy

A data engineering pipeline for DS5111 that pulls YouTube transcripts, runs them through a Gemini LLM to extract useful metadata, and spits out clean JSONL records.

---

## What This Does

You give it YouTube video IDs, it fetches the transcripts, and passes them through an LLM enrichment step that pulls out cleaned text, tech terms, and book names. Everything flows through stdin/stdout so you can chain it with other UNIX tools.

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

Create a `.env` file in the repo root — it's already gitignored so you won't accidentally commit it.

| Variable | Required | Description |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes (for real runs) | Your Google Gemini API key |
| `WEBSHARE_USER` | No | Proxy username for YouTube extraction |
| `WEBSHARE_PASSWORD` | No | Proxy password for YouTube extraction |

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
