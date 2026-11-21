"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "../../../components/layout/Sidebar";
import { Navbar } from "../../../components/layout/Navbar";
import { apiFetch, getAuthSession, normalizeRole } from "../../../lib/auth";

type Source = { document: string; quote: string; relevance: number };
type Result = { answer: string; abstained: boolean; sources: Source[]; answer_type?: "general" | "policy" };

export default function PolicyQuestionsPage() {
  const router = useRouter();
  const [question, setQuestion] = React.useState("");
  const [result, setResult] = React.useState<Result | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    const session = getAuthSession();
    if (!session || !["student", "worker"].includes(normalizeRole(session.role) ?? "")) router.replace("/");
  }, [router]);

  async function ask(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await apiFetch("/policy/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Could not search policy documents");
      setResult(body as Result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not search policy documents");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Sidebar />
      <main className="main-content">
        <Navbar />
        <p className="section-label">CampusAid Knowledge Assistant</p>
        <h1 className="page-title">University policy questions</h1>
        <p className="page-subtitle">Ask in your own words. Gemini answers using relevant university policy passages when available, with source references.</p>

        <form onSubmit={ask} className="max-w-3xl rounded-2xl border bg-white p-6 shadow-sm">
          <label htmlFor="policy-question" className="mb-2 block text-sm font-semibold">What would you like to know?</label>
          <textarea id="policy-question" value={question} onChange={(e) => setQuestion(e.target.value)} minLength={5} maxLength={1000} required rows={4} className="w-full rounded-xl border p-4 text-sm outline-none focus:ring-2 focus:ring-amber-400" placeholder="For example: What is the attendance requirement for examinations?" />
          <div className="mt-4 flex items-center justify-between gap-4">
            <p className="text-xs text-slate-500">Answers use retrieved policy documents when relevant. General AI responses are labeled and aren’t verified policy.</p>
            <button type="submit" disabled={loading || question.trim().length < 5} className="shrink-0 rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
              {loading ? "Searching…" : "Ask policy"}
            </button>
          </div>
        </form>

        {error && <p role="alert" className="mt-5 max-w-3xl rounded-lg bg-red-50 p-4 text-sm text-red-800">{error}</p>}
        {result && <section aria-live="polite" className="mt-6 max-w-3xl rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">{result.answer_type === "general" ? "General answer" : "Answer from university policies"}</h2>
          {result.answer_type === "general" && <p className="mt-3 text-xs font-medium text-amber-800">General AI response · not verified university policy</p>}
          <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">{result.answer}</p>
          {result.sources.length > 0 && <div className="mt-6 border-t pt-4">
            <h3 className="text-sm font-semibold">Retrieved source passages</h3>
            {result.sources.map((source, index) => <figure key={`${source.document}-${index}`} className="mt-3 rounded-lg bg-slate-50 p-4">
              <figcaption className="text-xs font-semibold text-slate-600">{source.document}</figcaption>
              <blockquote className="mt-2 text-sm leading-6 text-slate-700">“{source.quote}”</blockquote>
            </figure>)}
          </div>}
        </section>}
        <aside className="mt-6 max-w-3xl rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
          Policy answers provide document references, not official decisions. For case-specific guidance, contact the university office named in the policy.
        </aside>
      </main>
    </>
  );
}
