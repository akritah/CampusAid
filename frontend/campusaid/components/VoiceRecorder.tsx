"use client";

import * as React from "react";

import { Button } from "./ui/button";

type VoiceRecorderProps = {
  disabled?: boolean;
  onRecorded: (audioBlob: Blob) => void;
  onSubmitAudio: () => void;
  canSubmitAudio: boolean;
  isSubmittingAudio: boolean;
};

export function VoiceRecorder({
  disabled = false,
  onRecorded,
  onSubmitAudio,
  canSubmitAudio,
  isSubmittingAudio,
}: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const chunksRef = React.useRef<BlobPart[]>([]);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);

      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        onRecorded(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch {
      setError("Microphone permission denied. Please allow microphone access in your browser settings.");
    }
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (!recorder || recorder.state === "inactive") {
      return;
    }
    recorder.stop();
    setIsRecording(false);
  };

  return (
    <div
      className={`card-dark space-y-3 p-4 ${
        isRecording
          ? "ring-2 ring-[rgba(229,168,60,0.35)]"
          : ""
      }`}
    >
      <p className="text-sm font-semibold">Submit Voice Complaint</p>

      <div className="flex flex-wrap items-center gap-2">
        <Button
          type="button"
          onClick={startRecording}
          disabled={disabled || isRecording}
          className="btn btn-gold disabled:bg-[var(--slate-light)] disabled:text-[var(--cream)]"
        >
          Start Recording
        </Button>
        <Button
          type="button"
          onClick={stopRecording}
          disabled={disabled || !isRecording}
          className={`btn btn-danger disabled:bg-[var(--slate-light)] disabled:text-[var(--cream)] ${
            isRecording
              ? "opacity-100"
              : "opacity-90"
          }`}
        >
          Stop Recording
        </Button>

        <Button
          type="button"
          onClick={onSubmitAudio}
          disabled={disabled || !canSubmitAudio || isSubmittingAudio || isRecording}
          className="btn btn-primary disabled:bg-[var(--slate-light)] disabled:text-[var(--cream)]"
        >
          {isSubmittingAudio ? (
            <span className="inline-flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
              Submitting Audio...
            </span>
          ) : (
            "Submit Audio"
          )}
        </Button>
      </div>

      {isRecording && (
        <p className="text-xs font-medium" style={{ color: "var(--gold-light)" }}>Recording in progress...</p>
      )}

      {error && <p className="text-xs" style={{ color: "#fff" }}>{error}</p>}
    </div>
  );
}
