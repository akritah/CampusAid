# CampusAid — Next.js + FastAPI Integration Guide

## Project Structure (Target)

```
campusaid/
├── frontend/                        # Next.js 14 App
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                 # Landing page
│   │   ├── (auth)/
│   │   │   └── login/page.tsx
│   │   └── (dashboard)/
│   │       ├── layout.tsx           # Sidebar + Topbar shell
│   │       ├── dashboard/page.tsx   # Student dashboard
│   │       ├── admin/page.tsx       # Admin analytics
│   │       ├── warden/page.tsx      # Warden dashboard
│   │       ├── complaints/
│   │       │   ├── page.tsx         # Complaint list
│   │       │   └── [id]/page.tsx    # Complaint detail
│   │       └── voice/page.tsx       # Voice complaint
│   ├── components/
│   │   ├── ui/
│   │   │   ├── StatCard.tsx
│   │   │   ├── ComplaintItem.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── Button.tsx
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── Topbar.tsx
│   │   └── complaints/
│   │       ├── ComplaintForm.tsx
│   │       ├── VoiceRecorder.tsx
│   │       └── ComplaintTimeline.tsx
│   ├── lib/
│   │   ├── api.ts                   # All API call functions
│   │   └── types.ts                 # Shared TypeScript types
│   └── styles/
│       └── globals.css              # Design tokens (from prototype)
│
└── backend/                         # FastAPI app
    ├── main.py
    ├── routers/
    │   ├── complaints.py
    │   ├── auth.py
    │   ├── dashboard.py
    │   └── voice.py
    ├── models/
    │   ├── complaint.py
    │   └── user.py
    ├── schemas/
    │   ├── complaint.py
    │   └── user.py
    ├── database.py
    └── requirements.txt
```

---

## STEP 1 — Design Tokens (globals.css)

**File:** `frontend/styles/globals.css`

```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  /* Brand */
  --navy:        #0D1B3E;
  --navy-mid:    #142254;
  --navy-light:  #1E3170;
  --gold:        #C8922A;
  --gold-light:  #E5A83C;
  --gold-pale:   #F5E6C8;
  --cream:       #FAF7F2;

  /* Semantic */
  --success:     #2E7D52;
  --success-bg:  #E8F5EE;
  --warning:     #C05621;
  --warning-bg:  #FEF3E2;
  --danger:      #9B2335;
  --danger-bg:   #FDE8EC;
  --info:        #1E5799;
  --info-bg:     #E8F0FB;

  /* Neutrals */
  --slate:       #4A5568;
  --slate-light: #718096;
  --border:      #E2E8F0;

  /* Typography */
  --font-display: 'Playfair Display', serif;
  --font-body:    'DM Sans', sans-serif;
  --font-mono:    'DM Mono', monospace;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(13,27,62,0.08);
  --shadow-md: 0 4px 12px rgba(13,27,62,0.10);
  --shadow-lg: 0 10px 30px rgba(13,27,62,0.12);

  /* Radius */
  --radius-sm: 6px;
  --radius:    10px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: var(--font-body); color: var(--navy); background: #F5F7FA; }
```

---

## STEP 2 — TypeScript Types

**File:** `frontend/lib/types.ts`

```typescript
export type ComplaintStatus =
  | 'submitted'
  | 'assigned'
  | 'under_review'
  | 'resolved'
  | 'escalated';

export type UserRole = 'student' | 'worker' | 'warden' | 'admin';

export type Priority = 'low' | 'medium' | 'high' | 'critical';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department?: string;
  batch?: string;
}

export interface Complaint {
  id: string;                  // "CAid-2025-0042"
  title: string;
  description: string;
  category: string;
  department: string;
  status: ComplaintStatus;
  priority: Priority;
  filed_by: string;
  assigned_to?: string;
  filed_at: string;            // ISO datetime
  updated_at: string;
  expected_resolution?: string;
  is_voice: boolean;
  transcript?: string;
  tags: string[];
  timeline: TimelineEvent[];
}

export interface TimelineEvent {
  id: string;
  complaint_id: string;
  event: string;
  detail: string;
  timestamp: string;
}

export interface DashboardStats {
  total: number;
  pending: number;
  resolved: number;
  escalated: number;
  avg_resolution_days: number;
}
```

---

## STEP 3 — API Client

**File:** `frontend/lib/api.ts`

```typescript
import type { Complaint, DashboardStats, User } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// ── Auth ──────────────────────────────────────────────────
export async function login(email: string, password: string, role: string) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, role }),
  });
  if (!res.ok) throw new Error('Login failed');
  return res.json() as Promise<{ access_token: string; user: User }>;
}

// ── Complaints ────────────────────────────────────────────
export async function getComplaints(token: string): Promise<Complaint[]> {
  const res = await fetch(`${BASE_URL}/complaints`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Failed to fetch complaints');
  return res.json();
}

export async function getComplaint(id: string, token: string): Promise<Complaint> {
  const res = await fetch(`${BASE_URL}/complaints/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Complaint not found');
  return res.json();
}

export async function submitComplaint(
  data: Partial<Complaint>,
  token: string
): Promise<Complaint> {
  const res = await fetch(`${BASE_URL}/complaints`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Submission failed');
  return res.json();
}

export async function resolveComplaint(
  id: string,
  note: string,
  token: string
): Promise<Complaint> {
  const res = await fetch(`${BASE_URL}/complaints/${id}/resolve`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ resolution_note: note }),
  });
  if (!res.ok) throw new Error('Resolution failed');
  return res.json();
}

// ── Dashboard ─────────────────────────────────────────────
export async function getDashboardStats(token: string): Promise<DashboardStats> {
  const res = await fetch(`${BASE_URL}/dashboard/stats`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Stats fetch failed');
  return res.json();
}

// ── Voice ─────────────────────────────────────────────────
export async function transcribeAudio(audioBlob: Blob, token: string) {
  const form = new FormData();
  form.append('file', audioBlob, 'recording.webm');
  const res = await fetch(`${BASE_URL}/voice/transcribe`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  if (!res.ok) throw new Error('Transcription failed');
  return res.json() as Promise<{
    transcript: string;
    category: string;
    department: string;
    priority: string;
    tags: string[];
  }>;
}
```

---

## STEP 4 — Key React Components

### StatCard

**File:** `frontend/components/ui/StatCard.tsx`

```tsx
interface StatCardProps {
  icon: string;
  value: string | number;
  label: string;
  trend?: string;
  variant?: 'blue' | 'gold' | 'green' | 'red';
}

export function StatCard({ icon, value, label, trend, variant = 'blue' }: StatCardProps) {
  const borderColors = {
    blue: 'var(--navy-light)', gold: 'var(--gold)',
    green: 'var(--success)',   red: 'var(--danger)',
  };
  const bgColors = {
    blue: 'rgba(30,49,112,0.08)', gold: 'var(--gold-pale)',
    green: 'var(--success-bg)',   red: 'var(--danger-bg)',
  };
  return (
    <div style={{
      background: 'white',
      border: '1px solid var(--border)',
      borderLeft: `4px solid ${borderColors[variant]}`,
      borderRadius: 'var(--radius-lg)',
      padding: '20px 24px',
      boxShadow: 'var(--shadow-sm)',
    }}>
      <div style={{
        width: 40, height: 40,
        borderRadius: 'var(--radius)',
        background: bgColors[variant],
        display: 'flex', alignItems: 'center',
        justifyContent: 'center',
        fontSize: 18, marginBottom: 12,
      }}>
        {icon}
      </div>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: 32, fontWeight: 700, color: 'var(--navy)' }}>
        {value}
      </div>
      <div style={{ fontSize: 12, color: 'var(--slate-light)', fontWeight: 500 }}>{label}</div>
      {trend && (
        <div style={{ fontSize: 11, fontWeight: 600, marginTop: 8, color: 'var(--success)' }}>
          {trend}
        </div>
      )}
    </div>
  );
}
```

### Badge

**File:** `frontend/components/ui/Badge.tsx`

```tsx
import type { ComplaintStatus } from '@/lib/types';

const config: Record<ComplaintStatus, { label: string; bg: string; color: string }> = {
  submitted:    { label: 'Submitted',    bg: 'var(--info-bg)',    color: 'var(--info)'    },
  assigned:     { label: 'Assigned',     bg: 'var(--gold-pale)',  color: 'var(--gold)'    },
  under_review: { label: 'Under Review', bg: 'var(--warning-bg)', color: 'var(--warning)' },
  resolved:     { label: 'Resolved',     bg: 'var(--success-bg)', color: 'var(--success)' },
  escalated:    { label: 'Escalated',    bg: 'var(--danger-bg)',  color: 'var(--danger)'  },
};

export function StatusBadge({ status }: { status: ComplaintStatus }) {
  const { label, bg, color } = config[status];
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '3px 10px', borderRadius: 20,
      fontSize: 11, fontWeight: 600, background: bg, color,
    }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: color }} />
      {label}
    </span>
  );
}
```

### VoiceRecorder

**File:** `frontend/components/complaints/VoiceRecorder.tsx`

```tsx
'use client';
import { useState, useRef } from 'react';
import { transcribeAudio } from '@/lib/api';

interface TranscribeResult {
  transcript: string;
  category: string;
  department: string;
  priority: string;
  tags: string[];
}

interface Props {
  token: string;
  onTranscribed: (result: TranscribeResult) => void;
}

export function VoiceRecorder({ token, onTranscribed }: Props) {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [loading, setLoading] = useState(false);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];

    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      setLoading(true);
      try {
        const result = await transcribeAudio(blob, token);
        onTranscribed(result);
      } finally {
        setLoading(false);
      }
    };

    recorder.start();
    mediaRef.current = recorder;
    setRecording(true);
    timerRef.current = setInterval(() => setSeconds((s) => s + 1), 1000);
  }

  function stopRecording() {
    mediaRef.current?.stop();
    if (timerRef.current) clearInterval(timerRef.current);
    setRecording(false);
    setSeconds(0);
  }

  const formatTime = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  return (
    <div style={{
      background: 'linear-gradient(135deg, var(--navy), var(--navy-mid))',
      borderRadius: 'var(--radius-xl)', padding: 40, textAlign: 'center', color: 'white',
    }}>
      <p style={{ fontSize: 11, letterSpacing: 2, textTransform: 'uppercase', color: 'var(--gold-light)', marginBottom: 8 }}>
        {recording ? '● Recording' : 'Ready'}
      </p>
      <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 24, fontWeight: 700, marginBottom: 24 }}>
        {recording ? 'Speak Now' : 'Start Recording'}
      </h3>

      <button
        onClick={recording ? stopRecording : startRecording}
        disabled={loading}
        style={{
          width: 100, height: 100, borderRadius: '50%',
          background: recording
            ? 'linear-gradient(135deg, var(--danger), #c0392b)'
            : 'linear-gradient(135deg, var(--gold-light), var(--gold))',
          border: 'none', cursor: 'pointer',
          fontSize: 36, boxShadow: '0 8px 30px rgba(200,146,42,0.5)',
          transition: 'all 0.2s',
        }}
      >
        {loading ? '⏳' : recording ? '⏹' : '🎙️'}
      </button>

      {recording && (
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 28, marginTop: 16, color: 'white' }}>
          {formatTime(seconds)}
        </div>
      )}

      {loading && (
        <p style={{ marginTop: 16, color: 'rgba(255,255,255,0.6)', fontSize: 13 }}>
          Transcribing with AI…
        </p>
      )}
    </div>
  );
}
```

---

## STEP 5 — Dashboard Page (wired to API)

**File:** `frontend/app/(dashboard)/dashboard/page.tsx`

```tsx
'use client';
import { useEffect, useState } from 'react';
import { getComplaints, getDashboardStats } from '@/lib/api';
import { StatCard } from '@/components/ui/StatCard';
import { StatusBadge } from '@/components/ui/Badge';
import type { Complaint, DashboardStats } from '@/lib/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('campusaid_token') ?? '';
    Promise.all([getDashboardStats(token), getComplaints(token)])
      .then(([s, c]) => { setStats(s); setComplaints(c); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ padding: 40, color: 'var(--slate)' }}>Loading…</div>;

  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 26, fontWeight: 700, marginBottom: 24 }}>
        Dashboard
      </h1>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <StatCard icon="📋" value={stats?.total ?? 0}     label="Total Complaints"  variant="blue" />
        <StatCard icon="⏳" value={stats?.pending ?? 0}   label="Pending Review"    variant="gold" />
        <StatCard icon="✅" value={stats?.resolved ?? 0}  label="Resolved"          variant="green" />
        <StatCard icon="🚨" value={stats?.escalated ?? 0} label="Escalated"         variant="red" />
      </div>

      {/* Recent Complaints */}
      <div style={{ background: 'white', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', fontWeight: 600, fontSize: 14, color: 'var(--navy)' }}>
          Recent Complaints
        </div>
        {complaints.slice(0, 5).map((c) => (
          <div key={c.id} style={{
            padding: '14px 20px', borderBottom: '1px solid var(--border)',
            display: 'flex', alignItems: 'center', gap: 14,
            cursor: 'pointer', transition: 'background 0.15s',
          }}
            onMouseEnter={e => (e.currentTarget.style.background = '#f9fafb')}
            onMouseLeave={e => (e.currentTarget.style.background = 'white')}
            onClick={() => window.location.href = `/complaints/${c.id}`}
          >
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--slate-light)', minWidth: 130 }}>
              {c.id}
            </div>
            <div style={{ flex: 1, fontSize: 14, fontWeight: 600, color: 'var(--navy)' }}>
              {c.title}
            </div>
            <div style={{ fontSize: 12, color: 'var(--slate-light)' }}>{c.department}</div>
            <StatusBadge status={c.status} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## STEP 6 — FastAPI Backend

### main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import complaints, auth, dashboard, voice

app = FastAPI(title="CampusAid API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/auth",       tags=["Auth"])
app.include_router(complaints.router,  prefix="/complaints", tags=["Complaints"])
app.include_router(dashboard.router,   prefix="/dashboard",  tags=["Dashboard"])
app.include_router(voice.router,       prefix="/voice",      tags=["Voice"])
```

### schemas/complaint.py

```python
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

class ComplaintStatus(str, Enum):
    submitted    = "submitted"
    assigned     = "assigned"
    under_review = "under_review"
    resolved     = "resolved"
    escalated    = "escalated"

class Priority(str, Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"

class ComplaintCreate(BaseModel):
    title: str
    description: str
    category: str
    department: str
    priority: Priority = Priority.medium
    is_voice: bool = False
    transcript: Optional[str] = None
    tags: List[str] = []

class ComplaintOut(ComplaintCreate):
    id: str
    status: ComplaintStatus
    filed_by: str
    assigned_to: Optional[str]
    filed_at: datetime
    updated_at: datetime
    expected_resolution: Optional[datetime]

    class Config:
        from_attributes = True
```

### routers/complaints.py

```python
from fastapi import APIRouter, Depends, HTTPException
from schemas.complaint import ComplaintCreate, ComplaintOut, ComplaintStatus
from typing import List
from auth import get_current_user   # your JWT dependency

router = APIRouter()

@router.get("/", response_model=List[ComplaintOut])
async def list_complaints(current_user=Depends(get_current_user), db=Depends(get_db)):
    # Filter by user role automatically
    if current_user.role == "student":
        return db.query(Complaint).filter(Complaint.filed_by == current_user.id).all()
    elif current_user.role in ("admin", "warden"):
        return db.query(Complaint).all()
    raise HTTPException(403, "Forbidden")

@router.post("/", response_model=ComplaintOut, status_code=201)
async def create_complaint(
    data: ComplaintCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    complaint = Complaint(
        **data.dict(),
        id=generate_complaint_id(),   # e.g. "CAid-2025-0048"
        filed_by=current_user.id,
        status=ComplaintStatus.submitted,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint

@router.patch("/{id}/resolve", response_model=ComplaintOut)
async def resolve_complaint(
    id: str,
    body: dict,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(404, "Not found")
    complaint.status = ComplaintStatus.resolved
    complaint.resolution_note = body.get("resolution_note")
    db.commit()
    return complaint
```

### routers/voice.py

```python
from fastapi import APIRouter, UploadFile, File, Depends
import openai   # or use Whisper locally

router = APIRouter()

@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    audio_bytes = await file.read()

    # Option A — OpenAI Whisper API
    transcript = openai.Audio.transcribe("whisper-1", audio_bytes)["text"]

    # Option B — local faster-whisper
    # from faster_whisper import WhisperModel
    # model = WhisperModel("base")
    # segments, _ = model.transcribe(audio_bytes)
    # transcript = " ".join(s.text for s in segments)

    # AI categorisation (simple keyword approach or call GPT)
    category, department, priority, tags = categorise(transcript)

    return {
        "transcript": transcript,
        "category":   category,
        "department": department,
        "priority":   priority,
        "tags":       tags,
    }

def categorise(text: str):
    text_lower = text.lower()
    if any(w in text_lower for w in ["wifi", "internet", "network", "it"]):
        return "IT & Infrastructure", "IT Department", "high", ["WiFi", "Internet"]
    if any(w in text_lower for w in ["hostel", "room", "block", "warden"]):
        return "Hostel", "Warden", "medium", ["Hostel", "Residential"]
    if any(w in text_lower for w in ["food", "mess", "cafeteria"]):
        return "Cafeteria", "Administration", "medium", ["Food", "Cafeteria"]
    return "General", "Administration", "low", []
```

### routers/dashboard.py

```python
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/stats")
async def get_stats(current_user=Depends(get_current_user), db=Depends(get_db)):
    base = db.query(Complaint)
    if current_user.role == "student":
        base = base.filter(Complaint.filed_by == current_user.id)

    total     = base.count()
    resolved  = base.filter(Complaint.status == "resolved").count()
    pending   = base.filter(Complaint.status.in_(["submitted", "under_review"])).count()
    escalated = base.filter(Complaint.status == "escalated").count()

    return {
        "total":                total,
        "resolved":             resolved,
        "pending":              pending,
        "escalated":            escalated,
        "avg_resolution_days":  2.4,   # compute from actual timestamps
    }
```

---

## STEP 7 — Environment Setup

### frontend/.env.local
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### backend/.env
```
DATABASE_URL=sqlite:///./campusaid.db
SECRET_KEY=your-jwt-secret-key-here
OPENAI_API_KEY=sk-...          # only if using Whisper API
```

### backend/requirements.txt
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
pydantic==2.7.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
openai==1.30.0
faster-whisper==1.0.1          # optional: local transcription
```

---

## STEP 8 — Running the Full Stack

```bash
# Terminal 1 — FastAPI backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 — Next.js frontend
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

API docs auto-generated at: **http://localhost:8000/docs**

---

## Quick Checklist

- [ ] Copy design tokens into `globals.css`
- [ ] Add `.env.local` to frontend with API URL
- [ ] Add `.env` to backend with DB + secret key
- [ ] Run `uvicorn` and `npm run dev` simultaneously
- [ ] Test `/auth/login` via Swagger at `localhost:8000/docs`
- [ ] Test complaint creation end-to-end
- [ ] Wire `VoiceRecorder` component to `/voice/transcribe`
- [ ] Add JWT token storage (`localStorage.setItem('campusaid_token', ...)`)
