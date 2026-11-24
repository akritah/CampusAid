# Changelog

## 2026-11-24 — Evaluator fallback and observed deployment limits

- Recorded a live eight-case policy Q&A run with retrieved chunks and exact API responses. Results: one pass, five failures, and two fee-notice cases not testable because their required sources are absent.
- Rebuilt the Colab evaluator to display the saved real run and call the application's actual policy retriever/Gemini integration for new questions; removed hand-written answer output from the notebook.
- Added the public Colab prototype link and clarified that it covers policy Q&A, not grievance submission or voice intake.
- Recorded that Render's Python 3.11.11 dependency build succeeded but the Free service exceeded 512 MiB while loading the sentence-transformer and did not become live.

## 2026-11-21 — Milestone 2 preparation

- Added the nine-block Business Model Canvas and a repository-specific technical report.
- Added versioned policy-answer prompt snapshots, final prompt, fixed QA cases, and saved outputs.
- Added a searchable attendance section transcribed from Bennett University's official Examination Manual so the attendance question returns its 75% requirement with a citation.
- Updated policy retrieval normalization for attendance/exam wording and grievance submit/file wording.
- Integrated Gemini through the backend Interactions API, with retrieved passages provided as context and source citations shown in the UI.
- Improved voice complaint responsiveness by selecting the smaller fast CPU transcription preset and moving transcription/classification off the async event loop.
- Added evaluator-access and deployment checklist documentation. Public hosting and a dedicated evaluator login remain to be configured.
- Added a saved-output Colab fallback notebook and a rendered two-page Milestone 2 PDF with a one-page BMC.

## 2026-11-20 — Policy corpus setup

- Collected official Bennett University policy PDFs and recorded their source URLs in `backend/policy_documents/source_manifest.json`.
- Added policy document extraction and passage retrieval with source filenames and quotes.
- Several source PDFs are scans and need OCR for complete searchable coverage.
