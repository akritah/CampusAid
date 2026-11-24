"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { Sidebar } from "../../components/layout/Sidebar";
import { Navbar } from "../../components/layout/Navbar";
import { ComplaintForm, type ComplaintSubmitPayload } from "../../components/ComplaintForm";
import { ComplaintList, type ComplaintHistoryItem } from "../../components/ComplaintList";
import { StatsCards, type StatsData } from "../../components/StatsCards";
import { FeedbackModal } from "../../components/FeedbackModal";
import { apiFetch, clearAuthSession, getAuthSession, normalizeRole } from "../../lib/auth";

type ApiComplaint = {
  id: number;
  complaint_text: string;
  predicted_category?: string | null;
  department?: string | null;
  status?: string | null;
  confidence_score?: number | null;
  created_at?: string | null;
  user_id?: number | null;
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
  const [complaintFilter, setComplaintFilter] = React.useState("all");
  const [complaintSearch, setComplaintSearch] = React.useState("");
  const [historyLoading, setHistoryLoading] = React.useState(true);
  const [historyError, setHistoryError] = React.useState<string | null>(null);
  const [statsData, setStatsData] = React.useState<StatsData>({
    totalComplaints: 0,
    totalThisMonth: 0,
    pendingReview: 0,
    avgPendingDays: 0,
    resolved: 0,
    successRate: 0,
    escalated: 0,
  });
  const [session, setSession] = React.useState<{ username: string; userId: number; role: string } | null>(null);

  const [feedbackOpen, setFeedbackOpen] = React.useState(false);
  const [feedbackComplaintId, setFeedbackComplaintId] = React.useState<number | null>(null);
  const [todayLabel, setTodayLabel] = React.useState("Today");

  React.useEffect(() => {
    const auth = getAuthSession();
    const role = normalizeRole(auth?.role);
    console.log("[UserPortal] session role:", role, "user:", auth);

    if (!auth || (role !== "student" && role !== "worker")) {
      router.replace("/");
      return;
    }

    setSession({
      username: auth.username,
      userId: auth.userId,
      role: auth.role,
    });

    void fetchComplaints(auth.userId);
  }, [router]);

  React.useEffect(() => {
    const syncLocationState = () => {
      const hash = window.location.hash.slice(1);
      setComplaintFilter(["pending", "resolved", "track"].includes(hash) ? hash : "all");
      setComplaintSearch(new URLSearchParams(window.location.search).get("search") ?? "");
    };
    syncLocationState();
    window.addEventListener("hashchange", syncLocationState);
    window.addEventListener("popstate", syncLocationState);
    return () => {
      window.removeEventListener("hashchange", syncLocationState);
      window.removeEventListener("popstate", syncLocationState);
    };
  }, []);

  React.useEffect(() => {
    setTodayLabel(
      new Date().toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    );
  }, []);

  const fetchComplaints = async (userId: number) => {
    setHistoryLoading(true);
    setHistoryError(null);

    try {
      console.log("[UserPortal] fetching complaints for user:", userId);
      const response = await apiFetch(`/complaints?student_id=${encodeURIComponent(String(userId))}`);
      if (!response.ok) {
        throw new Error("Unable to load complaint history.");
      }

      const data = (await response.json()) as { complaints?: ApiComplaint[] };
      console.log("[UserPortal] complaints response:", data);

      const userComplaints = data.complaints ?? [];

      const normalized = userComplaints.map((complaint) => ({
        id: complaint.id,
        title: deriveTitle(complaint.complaint_text),
        department: complaint.department ?? complaint.predicted_category ?? "Unassigned",
        status: complaint.status ?? "pending",
        confidence_score: Number(complaint.confidence_score ?? 0),
        created_at: complaint.created_at ?? new Date().toISOString(),
      }));

      setComplaints(normalized);

      // Calculate stats
      const total = normalized.length;
      const thisMonth = normalized.filter((c) => {
        const complaintDate = new Date(c.created_at);
        const now = new Date();
        return complaintDate.getMonth() === now.getMonth() && complaintDate.getFullYear() === now.getFullYear();
      }).length;

      const pending = normalized.filter((c) =>
        ["pending", "under_review", "manual_review"].includes(c.status.toLowerCase())
      ).length;

      const pendingComplaints = normalized.filter((c) =>
        ["pending", "under_review", "manual_review"].includes(c.status.toLowerCase())
      );

      const resolved = normalized.filter((c) => c.status.toLowerCase() === "resolved").length;
      const escalated = normalized.filter((c) => c.status.toLowerCase() === "escalated").length;

      const successRate = total > 0 ? Math.round((resolved / total) * 100) : 0;
      const nowMs = Date.now();
      const avgPendingDays =
        pendingComplaints.length > 0
          ? Math.max(
              0,
              Math.round(
                pendingComplaints.reduce((sum, complaint) => {
                  const createdMs = new Date(complaint.created_at).getTime();
                  if (!Number.isFinite(createdMs)) {
                    return sum;
                  }
                  const diffDays = (nowMs - createdMs) / (1000 * 60 * 60 * 24);
                  return sum + Math.max(0, diffDays);
                }, 0) / pendingComplaints.length
              )
            )
          : 0;

      setStatsData({
        totalComplaints: total,
        totalThisMonth: thisMonth,
        pendingReview: pending,
        avgPendingDays,
        resolved,
        successRate,
        escalated,
      });
    } catch (error) {
      console.error("[UserPortal] complaint fetch error:", error);
      setHistoryError(error instanceof Error ? error.message : "Unable to load complaint history.");
      setComplaints([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleSubmitted = (payload: ComplaintSubmitPayload) => {
    const newComplaint: ComplaintHistoryItem = {
      id: payload.complaint_id,
      title: payload.title,
      department: payload.department,
      status: payload.status,
      confidence_score: payload.confidence_score,
      created_at: payload.created_at,
    };

    setComplaints((prev) => [newComplaint, ...prev]);

    // Update stats
    setStatsData((prev) => ({
      ...prev,
      totalComplaints: prev.totalComplaints + 1,
      totalThisMonth: prev.totalThisMonth + 1,
    }));
  };

  const handleRate = (complaintId: number) => {
    setFeedbackComplaintId(complaintId);
    setFeedbackOpen(true);
  };

  const handleLogout = () => {
    clearAuthSession();
    router.push("/");
  };

  const programInfo = "B.Tech CSE, Semester 6"; // Placeholder
  const visibleComplaints = complaints.filter((complaint) => {
    const isResolved = complaint.status.toLowerCase() === "resolved";
    if (complaintFilter === "resolved" && !isResolved) return false;
    if (["pending", "track"].includes(complaintFilter) && isResolved) return false;
    const query = complaintSearch.trim().toLowerCase();
    return !query || [complaint.title, complaint.department, complaint.status, String(complaint.id)]
      .some((value) => value.toLowerCase().includes(query));
  });

  return (
    <div style={{ display: "flex" }}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div style={{ flex: 1, marginLeft: "240px" }}>
        {/* Navbar */}
        <Navbar
          onSearch={setComplaintSearch}
          onVoiceClick={() => router.push("/user/voice")}
          onNewComplaintClick={() => {
            const formElement = document.getElementById("complaint-form");
            if (formElement) {
              formElement.scrollIntoView({ behavior: "smooth" });
            }
          }}
        />

        {/* Page Content */}
        <div className="main-content" style={{ marginLeft: 0, marginTop: 0 }}>
          {/* Welcome Header */}
          <div className="mb-8">
            <h1
              className="page-title"
              style={{ fontSize: "32px", marginBottom: "4px" }}
            >
              Welcome back, {session?.username || "Student"} 👋
            </h1>
            <p className="text-sm text-slate-600">
              {todayLabel}{" "}
              • {programInfo}
            </p>
          </div>

          {/* Stats Cards */}
          <StatsCards data={statsData} />

          {/* Main Grid */}
          <div className="grid gap-6 lg:grid-cols-2 lg:items-start">
            {/* Left Column: Complaint Submission */}
            <div className="space-y-4" id="complaint-form">
              <ComplaintForm onSubmitted={handleSubmitted} />
            </div>

            {/* Right Column: Complaint History */}
            <div className="space-y-4">
              <div id="all" />
              <div id="pending" />
              <div id="track" />
              <div id="resolved" />
              <h2 className="text-lg font-semibold capitalize">
                {complaintSearch ? `Search results for “${complaintSearch}”` : complaintFilter === "track" ? "Track active complaints" : `${complaintFilter} complaints`}
              </h2>
              {historyError && (
                <div
                  className="rounded-[var(--radius)] border px-4 py-3 text-sm flex items-start gap-2"
                  style={{
                    borderColor: "var(--danger)",
                    background: "var(--danger-bg)",
                    color: "var(--danger)",
                  }}
                >
                  <span>❌</span>
                  <span>{historyError}</span>
                </div>
              )}

              <ComplaintList
                complaints={visibleComplaints}
                loading={historyLoading}
                onRate={handleRate}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Feedback Modal */}
      <FeedbackModal
        open={feedbackOpen}
        complaintId={feedbackComplaintId}
        onClose={() => setFeedbackOpen(false)}
      />
    </div>
  );
}
