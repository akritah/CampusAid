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

export function ComplaintList({ complaints, loading, onRate }: ComplaintListProps) {
  return (
    <Card>
      <CardHeader>
        <div>
          <p className="section-label">Your Records</p>
          <CardTitle>Complaint History</CardTitle>
        </div>
        <p className="text-sm" style={{ color: "var(--slate)" }}>Track complaint routing and status updates.</p>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading && (
          <div className="rounded-[var(--radius)] px-4 py-3 text-sm" style={{ background: "var(--cream)", color: "var(--slate)" }}>Loading complaints...</div>
        )}

        {!loading && complaints.length === 0 && (
          <div className="rounded-[var(--radius)] border border-dashed px-4 py-6 text-center text-sm" style={{ borderColor: "var(--border)", color: "var(--slate-light)" }}>
            No complaints submitted yet.
          </div>
        )}

        {!loading && complaints.map((complaint) => (
          <article
            key={complaint.id}
            className="complaint-item"
          >
            <div className="complaint-icon">🧾</div>
            <div className="flex-1">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="complaint-id">#{complaint.id}</p>
                  <h4 className="complaint-title">{complaint.title}</h4>
                </div>
                <span className={`badge badge-${complaint.status.toLowerCase().replace(/\s+/g, "-")}`}>
                  {complaint.status}
                </span>
              </div>

              <div className="complaint-meta mt-2">
                <span>Department: {complaint.department}</span>
                <span>Confidence: {(complaint.confidence_score * 100).toFixed(1)}%</span>
                <span>{new Date(complaint.created_at).toLocaleString()}</span>
              </div>

              {complaint.status.toLowerCase() === "resolved" && (
                <div className="mt-4">
                  <Button
                    type="button"
                    onClick={() => onRate(complaint.id)}
                    className="btn btn-gold"
                  >
                    Rate Experience
                  </Button>
                </div>
              )}
            </div>
          </article>
        ))}
      </CardContent>
    </Card>
  );
}
