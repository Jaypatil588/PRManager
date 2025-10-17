# PR Manager (NVIDIA Hackathon)

Automated pull-request reviewer that blends retrieval-augmented generation (RAG), GitHub automation, and Slack notifications. The project ingests recent PR metadata, builds contextual understanding from a captured code dump, and lets an NVIDIA NeMo model deliver review feedback, vulnerability summaries, and chat notifications.

## Features
- Fetches the latest webhook payload (owner, repo, PR, diff) and enriches it with repository context.
- Runs a LangChain RAG pipeline backed by FAISS and sentence-transformer embeddings to produce structured PR reviews.
- Performs a second pass focused on vulnerability hunting and posts both analyses to a webhook endpoint.
- Publishes review summaries back to GitHub issues API and mirrors them to Slack via incoming webhooks.
- Ships an optional Flask + GitHub OAuth dashboard (`client/`) you can host alongside the automation script.
- Includes diagnostic scripts to validate environment configuration and exercise GitHub service helpers.

## Repository Layout
- `app.py` – entry point that orchestrates webhook ingestion, AI analysis, GitHub commenting, and Slack alerts.
- `pr_analyzer.py` – constructs the FAISS index, LangChain retrievers, and NVIDIA NeMo chat clients.
- `slack_client.py`, `github_client.py`, `github_service.py` – integrations for Slack and GitHub REST APIs.
- `client/` – minimal Flask backend and React UI for GitHub OAuth login and dashboard.
- `faiss_index/` – persisted vector store built from `Jaypatil588_nvidia-hackathon_dump.txt`.
- `test_setup.py`, `test_github_service.py` – scripts to verify dependencies, environment, and GitHub reachability.
- `requiremets.txt` – dependency pin list (note the intentional typo matches existing usage).

## Prerequisites
- Python 3.10+ and `pip`
- An NVIDIA API key with access to NeMo endpoints
- A GitHub personal access token (classic or fine-grained) with `repo` scope
- Slack incoming webhook URL (optional but recommended)

## Setup
```bash
git clone <repo-url>
cd nvidia-hackathon-local
python -m venv .venv
source .venv/bin/activate
pip install -r requiremets.txt
```

### Environment Variables
Create a `.env` file in the project root (never commit real secrets). Required keys depend on which modules you run:

| Key | Purpose |
| --- | --- |
| `GITHUB_TOKEN` / `GH_TOKEN` | GitHub authentication for posting comments and fetching metadata |
| `REPO_OWNER`, `REPO_NAME` | Default repository fallback when GitHub data is missing |
| `NVIDIA_API_KEY` | Auth token for the NVIDIA NeMo chat endpoint |
| `SLACK_WEBHOOK_URL` | Incoming webhook for Slack notifications |
| `TEST_COMMENT` | Set to `1` to force a dry-run GitHub comment (skips AI analysis) |
| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `SECRET_KEY` | Required only for the optional Flask OAuth dashboard |

The analyzer automatically (re)uses `faiss_index/`. Delete that directory if you need to rebuild the vector store from `Jaypatil588_nvidia-hackathon_dump.txt`.

## Running the Automation Pipeline
```bash
python app.py
```
The script:
1. Downloads the most recent webhook payload from `flask-hello-world-eight-lac.vercel.app`.
2. Extracts the latest pull request and diff.
3. Generates a PR review and vulnerability report via `PRAnalyzer`.
4. Posts the review back to GitHub (unless required variables are missing or `TEST_COMMENT=1`).
5. Sends both reports to the configured Slack channel and external webhook endpoints.

Check the console for emoji-prefixed status logs describing each stage.

## Optional Web Dashboard
The `client/app.py` Flask app provides GitHub OAuth login and a lightweight React dashboard.

```bash
export FLASK_APP=client/app.py
flask run
```

Set your GitHub OAuth application's callback URL to `http://localhost:5000/auth/github/callback` (or match your deployment). The app shares the same `.env` file for secrets.

## Diagnostics & Utilities
- `python test_setup.py` – confirms required files exist and environment variables are populated.
- `python test_github_service.py` – exercises the GitHub API helpers using live requests. Expect real API traffic and rate limiting; ensure your token has the proper scopes.

## Notes
- Replace hard-coded tokens in source files with environment variables before deploying beyond a demo.
- The NVIDIA endpoints bill per token—monitor usage when iterating.
- Slack notifications will fail fast if `SLACK_WEBHOOK_URL` is missing; the pipeline continues after log output.
- Tests and services reach out to the public internet; run them from an environment with outbound access.

