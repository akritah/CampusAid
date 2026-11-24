# CampusAid deployment guide (Vercel + Render)

This guide matches the current repository. The Next.js app is in `frontend/campusaid`; the FastAPI app is in `backend`. The API uses SQLAlchemy with SQLite locally and PostgreSQL in production. Login returns a signed 12-hour bearer token. Complaint text/voice submission, complaint listing and status changes, and policy endpoints use that token. Public signup is limited to student and worker roles; staff accounts must be provisioned through `DEMO_USERS_JSON` or directly in the database.

The policy assistant extracts text from PDF, DOCX, Markdown and text files, ranks passages by normalized keyword overlap, and sends relevant passages to Gemini for a concise answer with filename citations. The interface also shows the retrieved excerpts. When no passage matches, Gemini provides general guidance without presenting it as university policy. This is lexical RAG; there is no vector database. Gemini is called only from the backend.

## 1. Before deploying

1. Commit and push the project to a GitHub repository. Keep `.env`, `.env.local`, passwords, database URLs and Render secrets out of Git. The local SQLite file is ignored by Git. `.python-version` pins Render to Python 3.11.11, which is required by the pinned Torch 2.2.2 CPU wheel. If creating the service manually, also set `PYTHON_VERSION=3.11.11` under **Environment** so the service does not use Render's newer default Python runtime.
2. Confirm `backend/models/complaint_classifier.pkl` is included in the pushed repository. It is a small trained classifier artifact required for grievance classification. The multilingual sentence-transformer weights are downloaded by Hugging Face on first backend start and cached under `/var/data/huggingface` on the Render disk.
3. The repository includes Bennett University source PDFs, a source manifest, and searchable files under `backend/policy_documents`. Section 10 attendance text is indexed from the official 2024–25 Examination Manual because the local PDF copy has no reliably extractable text. Several other source PDFs are scans that require OCR for full retrieval coverage. Confirm current-year policies before using the assistant for operational decisions.

## 2. Create the production database and preserve existing rows

The local project defaults to `backend/campusaid.db` (SQLite); the current local database is about 45 KB and contains 7 users and 19 complaints. Do not point production at that local path: Render's normal filesystem is ephemeral, and a Vercel frontend cannot access the developer's database.

For persistent production use, create a PostgreSQL database in Render in the **same region** as the API. Copy its **Internal Database URL** into the API's `DATABASE_URL` environment variable. Use a persistent database plan for an ongoing faculty deployment; Render's free Postgres expires after 30 days. Do not point the API to a temporary database if you need the complaint history to survive.

To copy the existing SQLite records to an empty PostgreSQL database, run this once from the repository root on a trusted machine. Set these variables only in the shell; do not commit or paste the database URLs into Git or this guide:

```powershell
$env:SOURCE_DATABASE_URL = "sqlite:///C:/Complaint Classifier/backend/campusaid.db"
$env:TARGET_DATABASE_URL = "<Render external PostgreSQL URL>"
.\.venv\Scripts\python.exe .\backend\migrate_sqlite_to_postgres.py
```

The script creates missing tables and copies users and complaints. It refuses to copy if any target table already contains rows, does not alter the source, and resets PostgreSQL ID sequences. It also invalidates the stock `student1`, `worker1`, `admin1`, and `warden1` passwords from older versions in the destination while preserving those account rows and IDs; provision fresh dedicated accounts after migration. Use the database's **External Database URL** for this one-time migration from your local machine; the running Render service should use the Internal URL. Verify row counts in the Render database before changing the API's `DATABASE_URL`. Back up both databases first. If the local database was never used or you do not want its data, create a clean empty database instead.

At startup, the app uses SQLAlchemy `create_all` to create missing tables and idempotent additive migrations for legacy `priority`, `root_cause`, and `owner_id` columns. It does not drop or rename tables. Historical complaints keep their rows and remain available to staff; older rows without an authenticated owner are not exposed in student complaint lists. For future structural schema changes, add and review an explicit migration before deploying; `create_all` is not a general migration system.

## 3. Deploy the FastAPI backend on Render

The repository includes `render.yaml` as a Render Blueprint. In Render:

1. Choose **New + → Blueprint** and connect the GitHub repository.
2. Review the service `campusaid-api`. Its root directory is `backend`; build command is `pip install -r requirements.txt`; start command is `uvicorn app.main:app --host 0.0.0.0 --port $PORT`; health check path is `/health`.
3. Create the PostgreSQL database separately (section 2), then set `DATABASE_URL` on the API service to its Internal Database URL.
4. The Blueprint uses the `standard` web-service plan and attaches a 1 GB persistent disk at `/var/data`; policy files and the Hugging Face cache write there. The app loads its speech model only when voice transcription is first used. Render persistent disks require a paid web-service plan. Without this disk, uploads and downloaded model cache disappear on restart/redeploy. Increase disk size if the policy library or model cache grows.
5. The Blueprint generates `SECRET_KEY`. Keep that value private and stable; rotating it invalidates active login tokens. Keep `ALLOW_STAFF_REGISTRATION=false`.
6. After creating the Vercel project, set `CORS_ORIGINS` to the exact comma-separated production frontend origin(s), for example `https://campusaid.vercel.app`. Add a custom domain here too if you use one. Do not use `*`. For a Vercel Preview URL that needs API access, add that exact preview origin temporarily or use a stable preview domain.
7. Optionally set `DEMO_USERS_JSON` for dedicated evaluator accounts (see section 7). Leave it unset if you will create a student evaluator account through `/signup` and provision a separate staff account another way.
8. Deploy and wait for `/health` to return HTTP 200. The first startup downloads the multilingual model; the Whisper speech model downloads only when a voice complaint is first transcribed. Allow extra time and inspect Render logs if the health check remains pending.

If you create the service manually instead of using the Blueprint, choose **Python 3**, the `Standard` plan (1 CPU, 2 GB RAM), set root directory `backend`, build command `pip install -r requirements.txt`, start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, health check `/health`, and attach a paid persistent disk mounted at `/var/data`. Set the environment variables listed below.

## 4. Deploy the Next.js frontend on Vercel

1. In Vercel choose **Add New → Project**, import the GitHub repository, and configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend/campusaid` (enable including files outside the root only if Vercel prompts for it; the frontend has its own lockfile and does not need backend files)
   - **Install Command:** `npm ci`
   - **Build Command:** `npm run build`
   - **Output Directory:** leave the Next.js default
2. Add `NEXT_PUBLIC_API_URL` in Vercel Project Settings → Environment Variables for **Production**, **Preview**, and **Development** as needed. Set the production value to the Render API HTTPS base URL, e.g. `https://campusaid-api.onrender.com` (no trailing slash). This value is public by design; never put credentials or secret API keys in a `NEXT_PUBLIC_` variable.
3. Deploy. Copy the resulting production frontend origin (scheme and hostname only, without a path) into Render's `CORS_ORIGINS`, save and redeploy the API.
4. Confirm the frontend loads, register/sign in, and use the checks in section 8. No proxy rewrite to localhost is used; browser API calls go directly to the configured Render URL.

## 5. Backend environment variables

Set these on the Render API service. Render supplies `PORT`; do not hardcode or override it.

| Variable | Required | Value / source |
| --- | --- | --- |
| `APP_ENV` | Yes | `production` (set by `render.yaml`; hides interactive OpenAPI docs and requires production settings) |
| `DATABASE_URL` | Yes | Persistent Render PostgreSQL Internal Database URL. Use External URL only for the one-time local migration. |
| `SECRET_KEY` | Yes | Random secret of at least 32 characters; Blueprint generates one. Store only in Render. |
| `CORS_ORIGINS` | Yes | Exact Vercel production origin(s), comma-separated; no wildcard. |
| `POLICY_STORAGE_DIR` | Yes | `/var/data/policies` (persistent disk) |
| `HF_HOME` | Yes | `/var/data/huggingface` (persistent model cache) |
| `CLASSIFIER_MODEL_PATH` | Yes | `./models/complaint_classifier.pkl` relative to `backend` root |
| `ALLOW_STAFF_REGISTRATION` | Yes | `false`; public signup must not create admin or warden accounts |
| `DEMO_USERS_JSON` | Optional | JSON array of accounts to create on first startup. Passwords must be 12+ characters. Existing usernames are not reset on redeploy. Keep it private. |
| `GEMINI_API_KEY` | Yes for generated answers | Create in Google AI Studio; set only on the Render backend. Never add it to frontend variables or commit it. |
| `GEMINI_MODEL` | Optional | Defaults to `gemini-3.5-flash-lite`; override only with a model enabled for the key. |
| `WHISPER_MODEL` | Optional | Local speech recognition model; default `small`. Model is downloaded on first startup/use and cached on disk. |
| `USE_FASTER_WHISPER` | Optional | `true` to keep the current local voice complaint transcription path. |
| `WHISPER_DECODE_PRESET` | Optional | `fast` for lower transcription latency, with a small accuracy tradeoff. |
| `PYTHON_VERSION` | Set by Blueprint | `3.11.11` |
| `PORT` | Render-managed | Render assigns this. Uvicorn binds to it on `0.0.0.0`. |

The optional OpenAI transcription branch is not enabled by the current application. Never add an API key to frontend source or Vercel `NEXT_PUBLIC_` variables.

## 6. Frontend environment variable

| Variable | Where | Value |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Vercel Project Settings → Environment Variables | Render API's HTTPS base URL without a trailing slash |

For local development, copy `frontend/campusaid/.env.example` to `.env.local` and use your local API URL. `.env.local` is ignored by Git. The frontend fails with a configuration error if the variable is missing instead of silently calling a hardcoded host.

## 7. Persistence, policy uploads and faculty evaluator access

- **Complaint data and accounts:** Render PostgreSQL, not local SQLite or the service filesystem.
- **Policy source documents:** Render persistent disk under `/var/data/policies`. Upload an official file as a user with admin or warden role. The upload endpoint is `POST https://<api-host>/policy/documents`, multipart field name `file`; accepted extensions are `.pdf`, `.docx`, `.md`, `.txt`, max 15 MB. Example:

  ```powershell
  curl.exe -X POST "https://<api-host>/policy/documents" `
    -H "Authorization: Bearer <staff-access-token>" `
    -F "file=@C:\path\to\official-policy.pdf"
  ```

- **RAG index:** no vector database or serialized index exists in this version. Retrieval chunks are rebuilt from persisted files on each question, so there is no index file to back up. Keep source policies under the persistent disk and retain a separate copy of official source documents.
- **Evaluator login:** easiest option is to use `/signup` to create a dedicated student account and share its username/password with faculty out-of-band. Do not use personal accounts or a shared default password. For a pre-seeded student and policy uploader, enter a Render-only `DEMO_USERS_JSON` such as:

  ```json
  [{"username":"faculty_demo","password":"<unique-12+-character-secret>","role":"student"},{"username":"policy_admin","password":"<different-unique-12+-character-secret>","role":"admin"}]
  ```

  Set real unique passwords in the Render dashboard, then deploy. The passwords are hashed before storage. Seeding is idempotent and only creates missing usernames; changing this variable will not change existing account passwords. Use the student account to try login, policy answers, citations, unsupported-question refusal and grievance submission/tracking. Use the admin account to obtain a bearer token via `/auth/login` and upload approved policy documents. `APP_ENV=production` disables `/docs`; login and upload can be done with the frontend and an API client such as curl/Postman.

All signed-in browser requests use a 12-hour bearer token. The UI stores the token in browser local storage; deploy only over HTTPS and avoid third-party scripts that could execute on the app origin.

## 8. Deploy, redeploy and verify

1. Push changes to GitHub. Vercel and Render deploy from the connected branch; wait for both deployment records to report live.
2. If changing a secret or environment value, save it in the provider dashboard and trigger a redeploy. Vercel must rebuild when `NEXT_PUBLIC_API_URL` changes because it is embedded at build time.
3. Check `https://<api-host>/health` returns `{"status":"healthy", ...}`. `GET /` also reports the database and complaint-classifier state. Production interactive API docs are intentionally disabled.
4. Open the Vercel production URL. Register or use the dedicated student evaluator login. Confirm a policy question with an answerable topic returns quoted text and a filename, and an unsupported topic returns an abstention with no citations.
5. Submit a test grievance and confirm it appears in that account's history; use an admin account to update status and confirm it is reflected.
6. Upload one policy file, redeploy the backend, and ask the same question again. A successful answer after redeployment verifies the disk mount and policy path. Check complaints remain after deployment through PostgreSQL.

The deployment is not considered successful until the actual Vercel and Render services pass these checks. This repository has not been deployed by these instructions.

## 9. Local checks and troubleshooting

```powershell
cd frontend/campusaid
npm ci
npm run build

cd ../../backend
..\.venv\Scripts\python.exe -m compileall app migrate_sqlite_to_postgres.py
..\.venv\Scripts\python.exe test_production_smoke.py
```

The legacy `test_database.py` inserts and updates complaint rows. To run it without touching the existing local DB, point it at an in-memory DB in PowerShell:

```powershell
$env:DATABASE_URL = "sqlite:///:memory:"
..\.venv\Scripts\python.exe test_database.py
Remove-Item Env:DATABASE_URL
```

Common issues:

- **CORS error:** Render `CORS_ORIGINS` must exactly match the Vercel origin, including `https://` and any custom domain. Do not include a route path or trailing slash.
- **Frontend network/config error:** verify Vercel `NEXT_PUBLIC_API_URL`, then redeploy/rebuild Vercel.
- **Render health check fails:** inspect API logs for PostgreSQL URL/network issues, model download failures, or a missing `complaint_classifier.pkl`; check `/health` directly.
- **Classifier unavailable:** ensure `backend/models/complaint_classifier.pkl` was committed and `CLASSIFIER_MODEL_PATH` matches it. Do not train from a deployment with missing data; the model is included as a small artifact.
- **Policy uploads disappear:** verify the disk is attached at `/var/data`, the service uses a disk-capable plan, and `POLICY_STORAGE_DIR=/var/data/policies`.
- **Policy answers are general rather than cited:** check that `GEMINI_API_KEY` is set on the backend, the relevant document exists in `POLICY_STORAGE_DIR`, and its text is extractable. Scanned-image PDFs without a text layer need OCR before upload; this code does not perform OCR.
- **Gemini answers time out or fail:** confirm the backend key is valid and enabled for the Gemini API, check backend logs for status/model errors, and use a currently available model through `GEMINI_MODEL`.
- **Login expired:** tokens expire after 12 hours; log in again. Changing `SECRET_KEY` invalidates every existing token.
- **Old complaint rows aren't in a student's personal list:** legacy complaints with no `student_id` or without a matching account cannot be safely assigned automatically; they remain available to authorized administrators. New complaints are linked to the submitting account.
- **First request is slow:** free Render web services spin down when idle; production persistent disk and always-on compute are on paid plans. First deployment also downloads the language models.
