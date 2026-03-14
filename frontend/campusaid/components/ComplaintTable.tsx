"use client";

import * as React from "react";
import { Button } from "./ui/button";
import { Select } from "./ui/select";

export type Complaint = {
  id: number;
  complaint_text: string;
  predicted_category?: string | null;
  department?: string | null;
  status?: string | null;
};

interface ComplaintTableProps {
  complaints: Complaint[];
  showActions?: boolean;
  onUpdateStatus?: (id: number, status: string) => Promise<void>;
  onMarkResolved?: (id: number) => Promise<void>;
}

// Responsibility: display complaint list with optional admin actions.
export function ComplaintTable({
  complaints,
  showActions = false,
  onUpdateStatus,
  onMarkResolved
}: ComplaintTableProps) {
  if (!complaints.length) {
    return (
      <div className="rounded-[var(--radius-lg)] border border-dashed p-6 text-center text-sm" style={{ borderColor: "var(--border)", color: "var(--slate-light)" }}>
        No complaints found.
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Complaint</th>
            <th>Department</th>
            <th>Status</th>
            {showActions && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {complaints.map((complaint) => (
            <tr key={complaint.id}>
              <td>
                <p className="cell-id">
                  #{complaint.id}
                </p>
                <p>
                  {complaint.complaint_text}
                </p>
              </td>
              <td>
                {complaint.department ?? complaint.predicted_category ?? "Unassigned"}
              </td>
              <td>
                <span
                  className={`badge badge-${(complaint.status ?? "pending").toLowerCase().replace(/\s+/g, "-")}`}
                >
                  {complaint.status ?? "pending"}
                </span>
              </td>
              {showActions && (
                <td>
                  <div className="flex flex-col gap-2">
                    <Select
                      defaultValue={complaint.status ?? "auto_routed"}
                      onChange={(event) =>
                        onUpdateStatus?.(complaint.id, event.target.value)
                      }
                    >
                      <option value="auto_routed">Auto Routed</option>
                      <option value="manual_review">Manual Review</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                    </Select>
                    <Button
                      className="btn btn-outline"
                      onClick={() => onMarkResolved?.(complaint.id)}
                    >
                      Mark Resolved
                    </Button>
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
