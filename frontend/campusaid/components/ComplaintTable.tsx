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
  priority?: string | null;
  root_cause?: string | null;
  confidence_score?: number | null;
  created_at?: string | null;
};

interface ComplaintTableProps {
  complaints: Complaint[];
  showActions?: boolean;
  onUpdateStatus?: (id: number, status: string) => Promise<void>;
  onMarkResolved?: (id: number) => Promise<void>;
  onUpdatePriority?: (id: number, priority: string) => Promise<void>;
  onUpdateRootCause?: (id: number, rootCause: string) => Promise<void>;
}

// Responsibility: display complaint list with optional admin actions.
export function ComplaintTable({
  complaints,
  showActions = false,
  onUpdateStatus,
  onMarkResolved,
  onUpdatePriority,
  onUpdateRootCause,
}: ComplaintTableProps) {
  if (!complaints.length) {
    return (
      <div className="rounded-[var(--radius-lg)] border border-dashed p-6 text-center text-sm" style={{ borderColor: "var(--border)", color: "var(--slate-light)" }}>
        No complaints found.
      </div>
    );
  }

  const getPriorityColor = (priority?: string | null) => {
    const priorityMap: Record<string, { bg: string; text: string }> = {
      "low": { bg: "#E8F5EE", text: "#2E7D52" },
      "medium": { bg: "#FEF3E2", text: "#C05621" },
      "high": { bg: "#E8F0FB", text: "#1E5799" },
      "critical": { bg: "#FDE8EC", text: "#9B2335" },
    };
    return priorityMap[priority?.toLowerCase() || "medium"] || priorityMap["medium"];
  };

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Complaint</th>
            <th>Department</th>
            <th>Status</th>
            {showActions && <th>Priority</th>}
            {showActions && <th>Root Cause</th>}
            {showActions && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {complaints.map((complaint) => {
            const priorityColor = getPriorityColor(complaint.priority);
            return (
              <tr key={complaint.id}>
                <td>
                  <p className="cell-id">
                    #{complaint.id}
                  </p>
                  <p className="text-sm font-medium">
                    {complaint.complaint_text.substring(0, 80)}...
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    {complaint.created_at ? new Date(complaint.created_at).toLocaleDateString() : ""}
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
                    <span
                      className="badge text-xs font-semibold px-2 py-1 capitalize"
                      style={{
                        background: priorityColor.bg,
                        color: priorityColor.text,
                      }}
                    >
                      {complaint.priority || "Not Set"}
                    </span>
                  </td>
                )}
                {showActions && (
                  <td>
                    <span className="text-xs font-medium text-slate-600 capitalize">
                      {complaint.root_cause?.replace(/_/g, " ") || "Under Review"}
                    </span>
                  </td>
                )}
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
                      
                      <Select
                        defaultValue={complaint.priority || "medium"}
                        onChange={(event) =>
                          onUpdatePriority?.(complaint.id, event.target.value)
                        }
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                      </Select>

                      <Select
                        defaultValue={complaint.root_cause || "unknown"}
                        onChange={(event) =>
                          onUpdateRootCause?.(complaint.id, event.target.value)
                        }
                      >
                        <option value="unknown">Unknown</option>
                        <option value="infrastructure_failure">Infrastructure Failure</option>
                        <option value="policy_gap">Policy Gap</option>
                        <option value="human_error_staff">Human Error - Staff</option>
                        <option value="human_error_student">Human Error - Student</option>
                        <option value="resource_shortage">Resource Shortage</option>
                        <option value="communication_breakdown">Communication Breakdown</option>
                        <option value="pending_investigation">Pending Investigation</option>
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
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
