# CampusAid — Technical Report

## Problem and objective

Students need a clear way to submit and track campus grievances, including in voice form. They also need to find relevant university policy language without relying on unsupported AI claims. CampusAid combines a complaint workflow with document-grounded policy Q&A.

## Architecture

- **Frontend:** Next.js 15 and React, with student, worker, and staff views.
- **API:** FastAPI with bearer-token authentication and role-restricted routes.
- **Database:** SQLAlchemy; SQLite for local development and PostgreSQL for hosted deployment.
- **Complaint classification:** multilingual sentence-transformer embeddings and a scikit-learn classifier.
- **Voice intake:** Faster-Whisper on CPU using int8 inference; the configured local profile is `small` with the `fast` decode preset.
- **Policy Q&A:** PDF/DOCX/text extraction, passage chunking, lexical overlap retrieval, Gemini Interactions API response generation, and filename citations.
- **Storage:** uploaded/searchable policies use `POLICY_STORAGE_DIR`; production requires persistent storage.

## Retrieval and answer design

The API ranks passages using normalized query/document token overlap. Relevant passages are supplied to Gemini, which is instructed to answer only from those passages, cite source filenames, and not fill factual gaps with assumptions. When no passage matches, Gemini supplies general next-step guidance without presenting it as Bennett University policy. The app currently uses lexical retrieval rather than a vector database. Scanned PDFs with no text layer require OCR; OCR is not implemented.

The attendance response is grounded in Section 10 of Bennett University's Examination Manual 2024–25. A searchable text section is included alongside the source PDF because the local PDF copy is not reliably extractable by the installed parser.

## Prompt design

Prompt snapshots in `prompts/v1` through `prompts/v3` document the progression from quote-and-refuse behavior to grounded cited answers plus useful general guidance when no source matches. `prompts/final/policy_qa.md` contains the current answer contract and retrieval safety rules.

## Demonstration and testing

A live local evaluation was run on 2026-11-24 through `backend/app/policy_qa.py`, using the checked-in indexed corpus and configured Gemini API. The complete prompts, retrieved chunks, and exact CampusAid JSON responses are in `test-data/policy_qa_run_2026-11-24.json`; the summary table and T1 sample are in `test-data/saved_outputs.md`. Results: **1 pass, 5 fail, 2 not testable**. T1 answered the 75% attendance question with the Section 10 source. The failures expose retrieval gaps, a missing clarification behavior, and incomplete combined-policy retrieval. The two non-testable cases need current or conflicting fee notices that are not present in the repository.

The runtime currently builds Gemini instructions inline in `backend/app/policy_qa.py`; it does not load `prompts/v3/policy_qa.md`. This run therefore evaluates the active implementation, not a controlled P1/v3 prompt comparison. Do not claim the v3 snapshot was used until the application loads it.

## Limitations

- Current official documents include scans with little or no extractable text; these need OCR before they can support reliable retrieval.
- The examination-manual source is from academic year 2024–25; the university should verify that the current-year threshold is unchanged before operational use.
- Keyword overlap can miss paraphrases; the current implementation includes basic inflection and synonym normalization but is not semantic vector search.
- General answers are not official decisions and must not be treated as institution-specific policy.
- Local checks are not the same as an independent production deployment or load test.
