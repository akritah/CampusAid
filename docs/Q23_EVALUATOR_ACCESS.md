# Q23 — Evaluator access handoff

## Q11 prototype link

**Open the CampusAid policy Q&A evaluator in Colab:**
https://colab.research.google.com/github/akritah/CampusAid/blob/codex/campusaid-evaluator/code/CampusAid_Evaluator_Demo.ipynb

The repository and branch are public. A standard Google sign-in may be required to open Colab; no additional access request or project invitation is needed. The notebook displays saved, actual retrieval and Gemini outputs without requiring an API key. To run a new question, execute its setup cell and enter a Gemini API key into the hidden prompt; that key is not saved. The notebook tests policy Q&A only. It does not implement grievance submission/tracking or voice intake.

## Deployment and login status

- **Full public web app:** Not available yet. Render completed the Python 3.11.11 dependency build but the Free instance exceeded its 512 MiB memory limit while loading the sentence-transformer model, before opening a port. The app has not been verified live.
- **Next no-card hosting attempt:** Railway's new-account Trial provides up to 1 GB RAM for a limited period without a card, but this is not deployed or verified. Its later Free plan returns to 512 MB, so the Colab link above remains the available evaluator link until a hosted app passes its checks.
- **Evaluator app login:** Not applicable to the Colab notebook; it does not use CampusAid authentication.
- **Student username/password:** Not provided. Do not use a fabricated or default credential.
- **Source repository:** https://github.com/akritah/CampusAid/tree/codex/campusaid-evaluator
- **Saved evaluation outputs:** [`test-data/policy_qa_run_2026-11-24.json`](../test-data/policy_qa_run_2026-11-24.json)

The actual evaluation recorded one pass, five failures, and two cases that could not be tested because the required fee notices are absent from the indexed corpus. The notebook exposes these results as recorded and does not present them as a successful full-app deployment.

Do not commit API keys, passwords, or tokens. If the full web app is later deployed, provision a dedicated student account and add its credentials to the assignment response privately, not to this public repository.
