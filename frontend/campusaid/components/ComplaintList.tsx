"use client";

import * as React from "react";

import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

export type ComplaintHistoryItem = {
  id: number;
  title: string;
  department: string;
  status: string;
  confidence_score: number;
  created_at: string;
};

type ComplaintListProps = {
  complaints: ComplaintHistoryItem[];
  loading: boolean;
  onRate: (complaintId: number) => void;
};

// Map status to display names and colors
function getStatusBadge(status: string) {
  const statusMap: Record<string, { label: string; color: string; icon: string }> = {
    "auto_routed": { label: "Under Review", color: "info", icon: "📋" },
    "manual_review": { label: "Under Review", color: "info", icon: "📋" },
    "resolved": { label: "Resolved", color: "success", icon: "✅" },
    "pending": { label: "Pending", color: "warning", icon: "⏳" },
    "escalated": { label: "Escalated", color: "danger", icon: "📈" },
  };
  
  const mapped = statusMap[status.toLowerCase().replace(/\s+/g, "_")];
  return mapped || { label: status, color: "info", icon: "📋" };
}

function getCategoryIcon(department: string): string {
  const icons: Record<string, string> = {
    "academic": "📚",
    "administration": "🏢",
    "harassment": "🚨",
    "hostel": "🏠",
    "it": "💻",
    "infrastructure": "🔧",
    "default": "📌",
  };
  
  const key = department?.toLowerCase().split(/ |\/|-/)[0] || "default";
  return icons[key] || icons["default"];
}

export function ComplaintList({ complaints, loading, onRate }: ComplaintListProps) {
  // Sort complaints newest first
  const sortedComplaints = [...complaints].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <Card>
      <CardHeader>
        <div className="space-y-1">
          <p className="section-label">Your Submissions</p>
          <CardTitle className="text-2xl">Your Complaints</CardTitle>
        </div>
        <p className="text-sm text-slate-600">Track complaint routing and monitor progress.</p>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading && (
          <div
            className="rounded-[var(--radius)] px-4 py-4 text-sm flex items-center gap-2"
            style={{ background: "var(--cream)", color: "var(--slate)" }}
          >
            <span className="text-lg">⏳</span> Loading your complaints...
          </div>
        )}

        {!loading && sortedComplaints.length === 0 && (
          <div
            className="rounded-[var(--radius)] border border-dashed px-4 py-8 text-center"
            style={{ borderColor: "var(--border)", color: "var(--slate-light)" }}
          >
            <div className="text-3xl mb-2">📭</div>
            <p className="text-sm font-medium">No complaints submitted yet.</p>
            <p className="text-xs mt-1">Submit your first complaint to get started.</p>
          </div>
        )}

        {!loading && sortedComplaints.map((complaint) => {
          const statusInfo = getStatusBadge(complaint.status);
          const categoryIcon = getCategoryIcon(complaint.department);
          const complaintId = `CAId-${new Date(complaint.created_at).getFullYear()}-${String(complaint.id).padStart(4, "0")}`;

          return (
            <article
              key={complaint.id}
              className="complaint-item"
              style={{
                background: "#fff",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-lg)",
                padding: "16px",
                display: "flex",
                alignItems: "flex-start",
                gap: "12px",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "var(--navy-light)";
                (e.currentTarget as HTMLElement).style.boxShadow = "var(--shadow-md)";
                (e.currentTarget as HTMLElement).style.transform = "translateY(-1px)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "var(--border)";
                (e.currentTarget as HTMLElement).style.boxShadow = "none";
                (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
              }}
            >
              {/* Category Icon */}
              <div
                className="flex items-center justify-center flex-shrink-0"
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "var(--radius)",
                  background: "var(--info-bg)",
                  fontSize: "20px",
                }}
              >
                {categoryIcon}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-500 font-mono">{complaintId}</p>
                    <h4
                      className="text-sm font-bold text-navy truncate"
                      title={complaint.title}
                    >
                      {complaint.title}
                    </h4>
                  </div>
                  <span
                    className={`badge badge-${statusInfo.color} flex-shrink-0 whitespace-nowrap`}
                  >
                    {statusInfo.icon} {statusInfo.label}
                  </span>
                </div>

                {/* Metadata */}
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 mb-3">
                  <span className="flex items-center gap-1">
                    📍 {complaint.department}
                  </span>
                  <span className="flex items-center gap-1">
                    🎯 {(complaint.confidence_score * 100).toFixed(0)}% Confidence
                  </span>
                  <span className="flex items-center gap-1">
                    📅 {new Date(complaint.created_at).toLocaleDateString()}
                  </span>
                </div>

                {/* Action Button */}
                {complaint.status.toLowerCase() === "resolved" && (
                  <Button
                    type="button"
                    onClick={() => onRate(complaint.id)}
                    className="btn btn-gold text-xs"
                    style={{ padding: "6px 12px" }}
                  >
                    ⭐ Rate Experience
                  </Button>
                )}
              </div>
            </article>
          );
        })}
      </CardContent>
    </Card>
  );
}
