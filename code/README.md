# Evaluator notebook

The deployable application source is in the repository root: `frontend/campusaid/` and `backend/app/`.

The [CampusAid Colab evaluator notebook](https://colab.research.google.com/github/akritah/CampusAid/blob/codex/campusaid-evaluator/code/CampusAid_Evaluator_Demo.ipynb) is a policy-Q&A prototype fallback while the Render Free backend exceeds its memory limit. It contains saved actual outputs from the 2026-11-24 run, including failures and not-testable cases. New queries call the same `backend/app/policy_qa.py` retriever and Gemini answer function after the user enters a key through a hidden prompt. No key or fabricated chatbot answer is stored in the notebook.

The notebook does not implement the full grievance submission/tracking or voice-intake workflow. See [`docs/Q23_EVALUATOR_ACCESS.md`](../docs/Q23_EVALUATOR_ACCESS.md) for the exact evaluator access status.
