"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "../../../components/layout/Sidebar";
import { Navbar } from "../../../components/layout/Navbar";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Textarea } from "../../../components/ui/textarea";
import { Select } from "../../../components/ui/select";
import { getAuthSession, normalizeRole, getApiBaseUrl } from "../../../lib/auth";

type Step = 1 | 2 | 3 | 4;

function buildTitleFromText(text: string): string {
  const cleaned = text.replace(/\s+/g, " ").trim();
  if (!cleaned) {
    return "Voice Complaint";
  }

  const words = cleaned.split(" ").slice(0, 8);
  return words.join(" ");
}

export default function VoiceComplaintPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = React.useState<Step>(1);
  const [language, setLanguage] = React.useState("English");
  const [isRecording, setIsRecording] = React.useState(false);
  const [recordingTime, setRecordingTime] = React.useState(0);
  const [audioBlob, setAudioBlob] = React.useState<Blob | null>(null);
  const [transcription, setTranscription] = React.useState("");
  const [title, setTitle] = React.useState("");
  const [department, setDepartment] = React.useState("");
  const [detectedCategory, setDetectedCategory] = React.useState("");
  const [priority, setPriority] = React.useState("medium");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState<string | null>(null);

  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const chunksRef = React.useRef<BlobPart[]>([]);
  const timerRef = React.useRef<NodeJS.Timeout | null>(null);

  React.useEffect(() => {
    const auth = getAuthSession();
    const role = normalizeRole(auth?.role);
    if (!auth || (role !== "student" && role !== "worker")) {
      router.replace("/");
      return;
    }
  }, [router]);

  React.useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          if (prev >= 300) {
            // Max 5 minutes
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording]);

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
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setAudioBlob(blob);
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setRecordingTime(0);
    } catch (err) {
      setError("Microphone permission denied. Please allow microphone access.");
    }
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
      setIsRecording(false);
    }
  };

  const submitVoiceComplaint = async () => {
    if (!audioBlob) {
      setError("Please record audio first.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const file = new File([audioBlob], `voice-${Date.now()}.webm`, {
        type: "audio/webm",
      });
      const formData = new FormData();
      formData.append("audio_file", file);
      formData.append("language", language);

      const response = await fetch(`${getApiBaseUrl()}/voice-complaint`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data?.detail || "Failed to submit voice complaint");
      }

      const data = await response.json();
      const detectedText = data.complaint_text || "";
      setTranscription(detectedText);
      setDetectedCategory(data.predicted_category || "");
      setDepartment(data.suggested_department || data.predicted_category || "");
      if (!title.trim() && detectedText.trim()) {
        setTitle(buildTitleFromText(detectedText));
      }
      setSuccess("Transcription ready. Review and edit it before final submission.");
      setCurrentStep(3);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit voice complaint");
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitFinalComplaint = async () => {
    if (!transcription.trim()) {
      setError("Transcription cannot be empty.");
      return;
    }

    const finalTitle = title.trim() || buildTitleFromText(transcription);

    setIsSubmitting(true);
    setError(null);

    try {
      if (!title.trim()) {
        setTitle(finalTitle);
      }

      const complaintText = `Title: ${finalTitle}\n\nDescription: ${transcription.trim()}`;

      const response = await fetch(`${getApiBaseUrl()}/submit-complaint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ complaint_text: complaintText }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data?.detail || "Failed to submit complaint");
      }

      setSuccess("Voice complaint submitted successfully!");
      setCurrentStep(4);

      setTimeout(() => {
        router.push("/user");
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit complaint");
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const steps = [
    { number: 1, label: "Language" },
    { number: 2, label: "Record" },
    { number: 3, label: "Review" },
    { number: 4, label: "Submit" },
  ];

  return (
    <div style={{ display: "flex" }}>
      <Sidebar />
      <div style={{ flex: 1, marginLeft: "240px" }}>
        <Navbar onVoiceClick={() => {}} onNewComplaintClick={() => router.push("/user")} />
        <div className="main-content" style={{ marginLeft: 0, marginTop: 0 }}>
          {/* Header */}
          <div className="mb-8">
            <h1 className="page-title" style={{ fontSize: "32px", marginBottom: "12px" }}>
              🎤 Voice Complaint Submission
            </h1>
            <p className="text-sm text-slate-600">
              Speak your complaint and we'll transcribe and analyze it for you.
            </p>
          </div>

          {/* Stepper */}
          <div className="mb-8 flex items-center justify-between">
            {steps.map((step, index) => (
              <React.Fragment key={step.number}>
                <div className="flex flex-col items-center">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-white mb-2 transition-all"
                    style={{
                      background: currentStep >= step.number ? "var(--navy)" : "var(--border)",
                      color: currentStep >= step.number ? "white" : "var(--slate)",
                    }}
                  >
                    {step.number}
                  </div>
                  <span className="text-xs font-semibold text-slate-600">{step.label}</span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className="flex-1 h-1 mx-2 mb-8 transition-all"
                    style={{
                      background: currentStep > step.number ? "var(--navy)" : "var(--border)",
                    }}
                  />
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Error message */}
          {error && (
            <div
              className="rounded-[var(--radius)] border px-4 py-3 text-sm mb-6 flex items-start gap-3"
              style={{
                borderColor: "var(--danger)",
                background: "var(--danger-bg)",
                color: "var(--danger)",
              }}
            >
              <span className="text-lg">❌</span>
              <span>{error}</span>
            </div>
          )}

          {/* Success message */}
          {success && (
            <div
              className="rounded-[var(--radius)] border px-4 py-3 text-sm mb-6 flex items-start gap-3"
              style={{
                borderColor: "var(--success)",
                background: "var(--success-bg)",
                color: "var(--success)",
              }}
            >
              <span className="text-lg">✅</span>
              <span>{success}</span>
            </div>
          )}

          {/* Step 1: Language Selection */}
          {currentStep === 1 && (
            <Card>
              <CardHeader>
                <CardTitle>Select Language</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {["English", "Hindi", "Hinglish", "Tamil"].map((lang) => (
                    <button
                      key={lang}
                      onClick={() => setLanguage(lang)}
                      className="p-4 border-2 rounded-lg font-semibold transition-all text-center"
                      style={{
                        borderColor: language === lang ? "var(--navy)" : "var(--border)",
                        background: language === lang ? "var(--cream)" : "white",
                        color: language === lang ? "var(--navy)" : "var(--slate)",
                      }}
                    >
                      {lang}
                    </button>
                  ))}
                </div>
                <p className="text-sm text-slate-600 mt-4">
                  Selected: <strong>{language}</strong>
                </p>
                <Button
                  onClick={() => setCurrentStep(2)}
                  className="btn btn-primary w-full"
                >
                  Continue to Recording
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Step 2: Recording */}
          {currentStep === 2 && (
            <Card>
              <CardHeader>
                <CardTitle>Record Your Complaint</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Recording Area */}
                <div
                  className="rounded-lg p-8 text-center"
                  style={{
                    background: "linear-gradient(135deg, var(--navy), var(--navy-mid))",
                    color: "white",
                  }}
                >
                  <div className="mb-4 text-5xl animate-pulse">🎤</div>
                  <h3 className="text-2xl font-bold mb-2">Speak Now</h3>
                  <p className="text-gray-300 mb-4">Language: {language}</p>
                  <div className="text-3xl font-mono font-bold mb-6">
                    {formatTime(recordingTime)} / 5:00
                  </div>

                  <div className="flex justify-center gap-4 mb-4">
                    <Button
                      onClick={startRecording}
                      disabled={isRecording}
                      className="btn btn-gold"
                    >
                      ▶ Start Recording
                    </Button>
                    <Button
                      onClick={stopRecording}
                      disabled={!isRecording}
                      className="btn btn-danger"
                    >
                      ⏹ Stop Recording
                    </Button>
                  </div>

                  {audioBlob && (
                    <div className="mt-4 p-3 bg-white/10 rounded">
                      <p className="text-sm">✓ Audio recorded ({(audioBlob.size / 1024).toFixed(1)} KB)</p>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <Button
                    onClick={() => setCurrentStep(1)}
                    className="btn btn-outline flex-1"
                  >
                    Back
                  </Button>
                  <Button
                    onClick={submitVoiceComplaint}
                    disabled={!audioBlob || isSubmitting}
                    className="btn btn-primary flex-1"
                  >
                    {isSubmitting ? "Uploading..." : "Upload & Transcribe"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 3: Review */}
          {currentStep === 3 && (
            <Card>
              <CardHeader>
                <CardTitle>Review & Edit</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Left: AI Analysis */}
                  <div
                    className="rounded-lg p-6"
                    style={{
                      background: "linear-gradient(135deg, var(--navy), var(--navy-mid))",
                      color: "white",
                    }}
                  >
                    <h3 className="font-bold mb-4 flex items-center gap-2">
                      🤖 AI Analysis
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-semibold text-gray-300">
                          Auto-Categorized
                        </label>
                        <div
                          className="mt-1 px-3 py-2 rounded bg-white/20 text-white font-semibold"
                        >
                          {detectedCategory || "Processing..."}
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="category" className="text-gray-300 font-semibold">
                          Detected Category
                        </Label>
                        <Select
                          id="category"
                          value={detectedCategory}
                          onChange={(e) => setDetectedCategory(e.target.value)}
                          style={{
                            background: "rgba(255,255,255,0.1)",
                            color: "white",
                            borderColor: "rgba(255,255,255,0.2)",
                          }}
                        >
                          <option value="">Select category...</option>
                          <option value="Academic">Academic</option>
                          <option value="Hostel">Hostel</option>
                          <option value="IT">IT & Infrastructure</option>
                          <option value="Admin">Administration</option>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="dept" className="text-gray-300 font-semibold">
                          Suggested Department
                        </Label>
                        <Select
                          id="dept"
                          value={department}
                          onChange={(e) => setDepartment(e.target.value)}
                          style={{
                            background: "rgba(255,255,255,0.1)",
                            color: "white",
                            borderColor: "rgba(255,255,255,0.2)",
                          }}
                        >
                          <option value="">Select department...</option>
                          <option value="Academic Affairs">Academic Affairs</option>
                          <option value="Hostel / Residence">Hostel / Residence</option>
                          <option value="IT & Infrastructure">IT & Infrastructure</option>
                          <option value="Administration">Administration</option>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="priority" className="text-gray-300 font-semibold">
                          Priority (Auto-suggested)
                        </Label>
                        <Select
                          id="priority"
                          value={priority}
                          onChange={(e) => setPriority(e.target.value)}
                          style={{
                            background: "rgba(255,255,255,0.1)",
                            color: "white",
                            borderColor: "rgba(255,255,255,0.2)",
                          }}
                        >
                          <option value="low">Low - Minor inconvenience</option>
                          <option value="medium">Medium - Affects workflow</option>
                          <option value="high">High - Multiple students</option>
                          <option value="critical">Critical - Safety concern</option>
                        </Select>
                      </div>
                    </div>
                  </div>

                  {/* Right: Transcription */}
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="title" className="font-semibold">
                        Complaint Title *
                      </Label>
                      <Input
                        id="title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Short title for your complaint..."
                        className="mt-2"
                      />
                    </div>

                    <div>
                      <Label htmlFor="transcription" className="font-semibold">
                        Transcribed Text (Editable)
                      </Label>
                      <Textarea
                        id="transcription"
                        value={transcription}
                        onChange={(e) => setTranscription(e.target.value)}
                        rows={8}
                        placeholder="Your transcribed complaint will appear here..."
                        className="mt-2"
                      />
                      <p className="text-xs text-slate-500 mt-2">
                        You can edit the transcription above before submitting.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={() => setCurrentStep(2)}
                    className="btn btn-outline flex-1"
                  >
                    Back to Recording
                  </Button>
                  <Button
                    onClick={submitFinalComplaint}
                    disabled={!transcription.trim() || isSubmitting}
                    className="btn btn-primary flex-1"
                  >
                    {isSubmitting ? "Submitting..." : "Submit Complaint"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 4: Success */}
          {currentStep === 4 && (
            <Card>
              <CardHeader>
                <CardTitle>✅ Submitted Successfully!</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-center py-12">
                <div className="text-6xl mb-4">🎉</div>
                <h2 className="text-2xl font-bold text-navy">Thank You!</h2>
                <p className="text-slate-600 mb-6">
                  Your voice complaint has been submitted successfully. You'll be redirected to your dashboard shortly.
                </p>
                <Button
                  onClick={() => router.push("/user")}
                  className="btn btn-primary"
                >
                  Go to Dashboard
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
