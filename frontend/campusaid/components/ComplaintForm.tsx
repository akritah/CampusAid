"use client";

import * as React from "react";

import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { VoiceRecorder } from "./VoiceRecorder";
import { getApiBaseUrl } from "../lib/auth";

export type ComplaintSubmitPayload = {
  complaint_id: number;
  title: string;
  department: string;
  status: string;
  confidence_score: number;
  created_at: string;
};

type ComplaintFormProps = {
  onSubmitted: (payload: ComplaintSubmitPayload) => void;
};

export function ComplaintForm({ onSubmitted }: ComplaintFormProps) {
  const [title, setTitle] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [attachment, setAttachment] = React.useState<File | null>(null);
  const [voiceBlob, setVoiceBlob] = React.useState<Blob | null>(null);
  const [voiceName, setVoiceName] = React.useState<string | null>(null);
  const [transcriptionText, setTranscriptionText] = React.useState("");

  const [loadingText, setLoadingText] = React.useState(false);
  const [loadingVoice, setLoadingVoice] = React.useState(false);
  const [success, setSuccess] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [warning, setWarning] = React.useState<string | null>(null);

  const contentForSubmission =
    transcriptionText.trim().length > 0 ? transcriptionText.trim() : description.trim();
  const requiredFilled = title.trim().length > 0 && contentForSubmission.length > 0;

  const clearForm = () => {
    setTitle("");
    setDescription("");
    setAttachment(null);
    setVoiceBlob(null);
    setVoiceName(null);
    setTranscriptionText("");
    setWarning(null);
  };

  const handleTextSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!requiredFilled) {
      return;
    }

    setLoadingText(true);
    setSuccess(null);
    setError(null);
    setWarning(null);

    try {
      const complaintText = `Title: ${title.trim()}\n\nDescription: ${contentForSubmission}${attachment ? `\n\nAttachment: ${attachment.name}` : ""}`;

      const response = await fetch(`${getApiBaseUrl()}/submit-complaint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ complaint_text: complaintText }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail ?? "Failed to submit complaint.");
      }

      setSuccess("Complaint submitted successfully.");

      onSubmitted({
        complaint_id: data.complaint_id,
        title: title.trim(),
        department: data.department ?? data.predicted_category ?? "Unassigned",
        status: data.status ?? "manual_review",
        confidence_score: Number(data.confidence_score ?? 0),
        created_at: new Date().toISOString(),
      });

      clearForm();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to submit complaint.");
    } finally {
      setLoadingText(false);
    }
  };

  const handleVoiceSubmit = async () => {
    if (!voiceBlob) {
      setError("Please record audio before uploading voice complaint.");
      return;
    }

    setLoadingVoice(true);
    setSuccess(null);
    setError(null);
    setWarning(null);

    try {
      console.log("[Voice] audioBlob:", voiceBlob);
      const file = new File([voiceBlob], voiceName ?? "voice-complaint.webm", { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio_file", file);

      const response = await fetch(`${getApiBaseUrl()}/voice-complaint`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("[Voice] backend response:", data);
      if (!response.ok) {
        throw new Error(data?.detail ?? "Failed to submit voice complaint.");
      }

      const detectedText = typeof data?.complaint_text === "string" ? data.complaint_text : "";
      setTranscriptionText(detectedText);

      if (detectedText.trim().length === 0) {
        setWarning("Transcription is empty. Please re-record and try again.");
      } else {
        setSuccess("Voice complaint uploaded. Review or edit the detected transcription below.");
      }

      onSubmitted({
        complaint_id: data.complaint_id,
        title: title.trim() || "Voice Complaint",
        department: data.department ?? data.predicted_category ?? "Unassigned",
        status: data.status ?? "manual_review",
        confidence_score: Number(data.confidence_score ?? 0),
        created_at: new Date().toISOString(),
      });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to submit voice complaint.");
    } finally {
      setLoadingVoice(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div>
          <p className="section-label">New Entry</p>
          <CardTitle>Submit Complaint</CardTitle>
        </div>
        <p className="text-sm" style={{ color: "var(--slate)" }}>Provide complete details for faster grievance routing.</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleTextSubmit} className="space-y-4">
          <div className="input-group">
            <Label htmlFor="complaintTitle">Title</Label>
            <Input
              id="complaintTitle"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Short title for your complaint"
              required
            />
          </div>

          <div className="input-group">
            <Label htmlFor="complaintDescription">Description</Label>
            <Textarea
              id="complaintDescription"
              rows={6}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Explain the issue with clear details"
              required
            />
          </div>

          <div className="input-group">
            <Label htmlFor="complaintAttachment">Optional File Upload</Label>
            <Input
              id="complaintAttachment"
              type="file"
              onChange={(event) => {
                setAttachment(event.target.files?.[0] ?? null);
              }}
            />
            {attachment && (
              <p className="text-xs" style={{ color: "var(--slate-light)" }}>Attached: {attachment.name}</p>
            )}
          </div>

          <Button
            type="submit"
            disabled={!requiredFilled || loadingText || loadingVoice}
            className="btn btn-primary w-full"
          >
            {loadingText ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                Submitting...
              </span>
            ) : (
              "Submit Complaint"
            )}
          </Button>
        </form>

        <div className="border-t pt-4" style={{ borderColor: "var(--border)" }}>
          <VoiceRecorder
            disabled={loadingText || loadingVoice}
            onSubmitAudio={handleVoiceSubmit}
            canSubmitAudio={Boolean(voiceBlob)}
            isSubmittingAudio={loadingVoice}
            onRecorded={(blob) => {
              setVoiceBlob(blob);
              setVoiceName(`voice-${Date.now()}.webm`);
              setWarning(null);
              setError(null);
              console.log("[Voice] audioBlob captured:", blob);
              setSuccess("Voice recorded successfully. Click Submit Audio.");
            }}
          />

          <div className="input-group mt-4">
            <Label htmlFor="voiceTranscription">Transcribed Text (Editable)</Label>
            <Textarea
              id="voiceTranscription"
              rows={4}
              value={transcriptionText}
              onChange={(event) => setTranscriptionText(event.target.value)}
              placeholder="Transcription will appear here after Submit Audio."
            />
            <p className="text-xs" style={{ color: "var(--slate-light)" }}>
              Hindi and Hinglish are auto-detected by backend transcription. Text is shown exactly as returned.
            </p>
          </div>
        </div>

        {success && (
          <div className="rounded-[var(--radius)] border px-4 py-3 text-sm" style={{ borderColor: "var(--success)", background: "var(--success-bg)", color: "var(--success)" }}>
            {success}
          </div>
        )}

        {error && (
          <div className="rounded-[var(--radius)] border px-4 py-3 text-sm" style={{ borderColor: "var(--danger)", background: "var(--danger-bg)", color: "var(--danger)" }}>
            {error}
          </div>
        )}

        {warning && (
          <div className="rounded-[var(--radius)] border px-4 py-3 text-sm" style={{ borderColor: "var(--warning)", background: "var(--warning-bg)", color: "var(--warning)" }}>
            {warning}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
