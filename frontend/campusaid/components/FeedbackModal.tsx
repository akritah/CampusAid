"use client";

import * as React from "react";

import { Button } from "./ui/button";

type FeedbackModalProps = {
  open: boolean;
  complaintId: number | null;
  onClose: () => void;
};

export function FeedbackModal({ open, complaintId, onClose }: FeedbackModalProps) {
  const [rating, setRating] = React.useState(0);
  const [submitted, setSubmitted] = React.useState(false);

  React.useEffect(() => {
    if (!open) {
      setRating(0);
      setSubmitted(false);
    }
  }, [open]);

  if (!open || complaintId === null) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(13,27,62,0.35)" }}>
      <div className="card w-full max-w-md p-5">
        <h3 className="page-title !mb-1 !text-[28px]">Rate Experience</h3>
        <p className="text-sm" style={{ color: "var(--slate)" }}>Complaint #{complaintId}</p>

        <div className="mt-4 flex items-center gap-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              className="text-2xl"
              style={{ color: star <= rating ? "var(--gold)" : "var(--slate-light)" }}
              aria-label={`Rate ${star} star`}
            >
              {star <= rating ? "★" : "☆"}
            </button>
          ))}
        </div>

        {submitted && (
          <p className="mt-3 rounded-[var(--radius)] px-3 py-2 text-sm" style={{ background: "var(--success-bg)", color: "var(--success)" }}>
            Thanks for your feedback.
          </p>
        )}

        <div className="mt-5 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button
            type="button"
            onClick={() => setSubmitted(true)}
            disabled={rating === 0}
            className="btn btn-primary"
          >
            Submit Rating
          </Button>
        </div>
      </div>
    </div>
  );
}
