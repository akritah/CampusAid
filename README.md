# CampusAid

CampusAid is a student-support prototype for submitting and tracking grievances, asking questions against university documents, and submitting complaints by voice. The policy assistant retrieves text from the Bennett University documents in `backend/policy_documents`; Gemini drafts an answer from retrieved passages and cites the source file. When no passage matches, Gemini provides general guidance and does not present it as Bennett policy.

## Evaluator link

**Live app:** Not published yet. Render's Free instance built the backend on Python 3.11.11 but exceeded its 512 MiB memory limit during sentence-transformer startup. For the milestone evaluator link, open the [CampusAid policy Q&A Colab notebook](https://colab.research.google.com/github/akritah/CampusAid/blob/codex/campusaid-evaluator/code/CampusAid_Evaluator_Demo.ipynb), which includes saved actual outputs and can run new questions with a Gemini API key. See [Q23 evaluator access](docs/Q23_EVALUATOR_ACCESS.md) and [Deployment](DEPLOYMENT.md) for status and limitations.

**Colab fallback:** [Evaluator notebook](code/CampusAid_Evaluator_Demo.ipynb). It includes the captured 2026-11-24 policy QA outputs. Running new questions requires an evaluator-supplied Gemini API key, entered through a hidden prompt.

**Repository:** https://github.com/akritah/CampusAid (confirm it is public before submitting).

**Team members:** Add the project team's names and student IDs before submission.

## Try it locally

Requirements: Python 3.11, Node.js 20+, and a Gemini API key.

1. Copy `backend/.env.example` to `backend/.env`, set a strong `SECRET_KEY`, and set `GEMINI_API_KEY` from Google AI Studio.
2. In one terminal, run `cd backend`, activate the project Python environment, install `pip install -r requirements.txt`, and start `uvicorn app.main:app --reload --port 8000`.
3. In another terminal, run `cd frontend/campusaid`, install with `npm ci`, set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`, and run `npm run dev`.
4. Open `http://localhost:3000`, create or use a student account, and try policy questions, grievance submission/tracking, and voice complaint entry.

Keep all API keys in the backend environment. Never commit `.env`, `.env.local`, credentials, or a database containing real user data.

## Repository map

- `frontend/campusaid/` — Next.js student and staff interface
- `backend/app/` — FastAPI routes, authentication, complaint classifier, voice transcription, and policy RAG
- `backend/policy_documents/` — source PDFs, source manifest, and searchable text sections
- `prompts/` — versioned prompt snapshots
- `final/` — final prompt and evaluator test cases
- `test-data/` — fixed questions and saved outputs
- `docs/` — BMC, technical report, diagrams, and evaluator access checklist
- `CHANGELOG.md` — dated milestone progress

## Milestone 2 artifacts

- [Business Model Canvas](docs/BUSINESS_MODEL_CANVAS.md)
- [Milestone 2 PDF](docs/CampusAid_Milestone2.pdf)
- [Technical report](docs/TECHNICAL_REPORT.md)
- [Prompt versions](prompts/)
- [Fixed test set and outputs](test-data/)
- [Q23 evaluator access](docs/Q23_EVALUATOR_ACCESS.md)
