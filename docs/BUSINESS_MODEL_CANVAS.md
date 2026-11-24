# CampusAid — Business Model Canvas

| Block | CampusAid proposal |
|---|---|
| **Customer segments** | Universities and colleges operating student-support services; students submitting complaints; faculty, wardens, and student-affairs staff handling cases. |
| **Value propositions** | One place to file and track grievances; multilingual voice complaint intake; automatic complaint classification; policy answers grounded in university documents with citations. |
| **Channels** | University-branded web portal; links from student ERP/LMS; QR codes and orientation materials; student-affairs communications. |
| **Customer relationships** | Self-service student portal; status notifications and case tracking; assisted escalation to the responsible university office; onboarding and support for institutional administrators. |
| **Revenue streams** | Proposed institutional annual subscription or per-campus license; paid setup, integration, and support. This is a business hypothesis; the prototype has no current revenue. |
| **Key resources** | Next.js and FastAPI application; complaint classifier and multilingual embedding model; policy document corpus and retrieval pipeline; secure database and persistent document storage; university domain expertise. |
| **Key activities** | Maintain secure complaint workflows; update and validate policy documents; evaluate answer grounding and classification; operate hosting, backups, access controls, and user support. |
| **Key partners** | Participating universities and student-affairs offices; cloud hosting/database providers; Gemini API provider; accessibility and student-support stakeholders. |
| **Cost structure** | Hosting and persistent storage; database and backups; Gemini API usage; speech-transcription compute; implementation and support; security, monitoring, and policy-document review. |

## Assumptions to validate

- Universities will approve an institution-specific deployment and nominate policy owners.
- Students prefer a transparent, trackable digital grievance workflow.
- Staff can resolve cases faster when submissions are categorized and routed consistently.
- Universities will accept AI-generated general guidance only when clearly separated from official policy answers.
