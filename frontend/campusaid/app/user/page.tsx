"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { ComplaintForm, type ComplaintSubmitPayload } from "../../components/ComplaintForm";
import { ComplaintList, type ComplaintHistoryItem } from "../../components/ComplaintList";
import { FeedbackModal } from "../../components/FeedbackModal";
import { Button } from "../../components/ui/button";
import { clearAuthSession, getApiBaseUrl, getAuthSession, normalizeRole } from "../../lib/auth";

type ApiComplaint = {
  id: number;
  complaint_text: string;
  predicted_category?: string | null;
  department?: string | null;
  status?: string | null;
  confidence_score?: number | null;
  created_at?: string | null;
};

function deriveTitle(complaintText: string): string {
  const titleMatch = complaintText.match(/Title:\s*(.*)/i);
  if (titleMatch?.[1]) {
    return titleMatch[1].trim();
  }
  return complaintText.slice(0, 48).trim() || "Complaint";
}

export default function UserPortal() {
  const router = useRouter();
  const [complaints, setComplaints] = React.useState<ComplaintHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = React.useState(true);
  const [historyError, setHistoryError] = React.useState<string | null>(null);

  const [feedbackOpen, setFeedbackOpen] = React.useState(false);
  const [feedbackComplaintId, setFeedbackComplaintId] = React.useState<number | null>(null);

  React.useEffect(() => {
    const session = getAuthSession();
    const role = normalizeRole(session?.role);
    console.log("[UserPortal] session role:", role);

    if (!session || (role !== "student" && role !== "worker")) {
      router.replace("/");
      return;
    }

    void fetchComplaints();
  }, [router]);

  const fetchComplaints = async () => {
    setHistoryLoading(true);
    setHistoryError(null);

    try {
      console.log("[UserPortal] fetching complaints...");
      const response = await fetch(`${getApiBaseUrl()}/complaints`);
      if (!response.ok) {
        throw new Error("Unable to load complaint history.");
      }

      const data = (await response.json()) as { complaints?: ApiComplaint[] };
      console.log("[UserPortal] complaints response:", data);
      const normalized = (data.complaints ?? []).map((complaint) => ({
        id: complaint.id,
        title: deriveTitle(complaint.complaint_text),
        department: complaint.department ?? complaint.predicted_category ?? "Unassigned",
        status: complaint.status ?? "pending",
        confidence_score: Number(complaint.confidence_score ?? 0),
        created_at: complaint.created_at ?? new Date().toISOString(),
      }));

      setComplaints(normalized);
    } catch (error) {
      console.error("[UserPortal] complaint fetch error:", error);
      setHistoryError(error instanceof Error ? error.message : "Unable to load complaint history.");
      setComplaints([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleSubmitted = (payload: ComplaintSubmitPayload) => {
    setComplaints((prev) => [
      {
        id: payload.complaint_id,
        title: payload.title,
        department: payload.department,
        status: payload.status,
        confidence_score: payload.confidence_score,
        created_at: payload.created_at,
      },
      ...prev,
    ]);
  };

  const handleRate = (complaintId: number) => {
    setFeedbackComplaintId(complaintId);
    setFeedbackOpen(true);
  };

  const handleLogout = () => {
    clearAuthSession();
    router.push("/");
  };

  return (
    <main className="min-h-screen portal-bg-pattern px-6 py-8 md:px-10" style={{ background: "var(--surface)" }}>
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <p className="section-label">User Workspace</p>
            <h1 className="page-title">CampusAid User Portal</h1>
            <p className="page-subtitle">Submit grievances, track routing, and monitor progress.</p>
          </div>
          <Button
            type="button"
            onClick={handleLogout}
            className="btn btn-outline"
          >
            Logout
          </Button>
        </header>

        <section className="grid gap-6 lg:grid-cols-2 lg:items-start">
          <div className="space-y-4">
            <h2 className="card-title">Complaint Submission</h2>
            <ComplaintForm onSubmitted={handleSubmitted} />
          </div>

          <div className="space-y-4">
            <h2 className="card-title">Complaint Status</h2>

            {historyError && (
              <div className="rounded-[var(--radius)] border px-4 py-3 text-sm" style={{ borderColor: "var(--danger)", background: "var(--danger-bg)", color: "var(--danger)" }}>
                {historyError}
              </div>
            )}

            <ComplaintList complaints={complaints} loading={historyLoading} onRate={handleRate} />
          </div>
        </section>
      </div>

      <FeedbackModal
        open={feedbackOpen}
        complaintId={feedbackComplaintId}
        onClose={() => setFeedbackOpen(false)}
      />
    </main>
  );
}
