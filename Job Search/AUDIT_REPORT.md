# Project Audit: Job Search Pipeline

## Overview
I reviewed the current Python-based job search pipeline, its configuration, dependencies, and automated tests to assess readiness for production use. The audit focuses on functional gaps, reliability, and deployment preparedness.

## Key Findings
- **Configuration path mismatch:** `scraper.load_config` expects `config/config.yaml`, but the repository only ships `config.yaml` at the project root, so configuration loading fails before scraping starts.【F:src/scraper.py†L8-L117】【F:config.yaml†L3-L28】
- **Missing required settings:** The main pipeline references `config["openai_api_key"]` but no such key exists in the provided configuration, causing a runtime error before LLM calls can run.【F:src/main.py†L13-L47】【F:config.yaml†L3-L28】
- **Dependency gaps:** Core runtime dependencies (e.g., `sentence-transformers`, `faiss`, `rank-bm25`, `langchain`, `numpy`) are used in the code but absent from `requirements.txt`, and the file currently only lists four packages, leaving the environment incomplete for both the app and tests.【F:requirements.txt†L1-L4】【F:src/processor.py†L1-L74】【F:src/analyzer.py†L1-L69】【F:src/main.py†L1-L47】
- **Test suite will not execute as written:** Tests import modules via the non-existent `Job_Search` package, expect FAISS and transformer models to be installed, and will fail immediately due to missing dependencies and package path setup.【F:tests/test_processor.py†L1-L120】【F:tests/test_analyzer.py†L1-L84】【F:requirements.txt†L1-L4】
- **Hybrid search lacks guardrails:** `hybrid_search` executes BM25 and vector searches even for empty/invalid queries and assumes every job has a `description`, which can yield meaningless results or exceptions when data is incomplete.【F:src/analyzer.py†L40-L69】
- **Output and notification robustness:** Scraping writes to `output/scraped_jobs.json` and PDF generation writes to `config['cloud']['pdf_destination']`, but neither function ensures the target directory exists, leading to file I/O errors at runtime.【F:src/scraper.py†L92-L117】【F:src/notifier.py†L33-L65】
- **Security and resilience concerns:** SMTP credentials are expected directly in config, connections are not wrapped in retries, and there is no rate limiting or request backoff around scraping; failures are only printed, not surfaced for monitoring or alerting.【F:src/scraper.py†L34-L117】【F:src/notifier.py†L6-L65】【F:config.yaml†L20-L28】

## Recommendations
- Align configuration paths and keys: either move `config.yaml` into a `config/` directory or update the loader to match the current location; add the missing `openai_api_key` entry and validate required keys at startup.
- Expand and correct `requirements.txt` to include all runtime and test dependencies (FAISS CPU build, SentenceTransformers, rank-bm25, langchain, numpy, etc.), then pin versions and add installation instructions.
- Normalize imports/package layout so tests can run (e.g., convert `src` into a package with `__init__.py` and adjust imports or test paths accordingly).
- Harden `hybrid_search` and preprocessing: short-circuit on empty queries, tolerate missing descriptions, and normalize text consistently with `processor.normalize_text` before scoring.
- Ensure filesystem safety: create `output/` (and any configured PDF destinations) before writing files, and handle I/O errors with logged exceptions.
- Improve operational hygiene: add retry/backoff for scraping and SMTP sends, surface errors through logging/metrics, and avoid storing SMTP passwords in plain text by supporting environment variables.
- Add runnable integration tests or mocks that avoid heavyweight model downloads, and document how to run the suite end-to-end.

## Completeness Checklist
- Configuration validation and secrets handling: **Incomplete**
- Dependency specification and installation guidance: **Incomplete**
- Automated tests runnable in CI without manual setup: **Incomplete**
- Error handling, retries, and logging for external calls (HTTP, SMTP, filesystem): **Incomplete**
- Documentation for setup, API keys, and operational playbooks: **Partial**

## Readiness Assessment
Overall readiness for production or deployment is **low**. The project cannot run successfully without addressing configuration path/key issues, filling dependency gaps, and stabilizing tests and error handling.
