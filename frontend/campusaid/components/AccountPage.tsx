"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Navbar } from "./layout/Navbar";
import { Sidebar } from "./layout/Sidebar";
import { apiFetch, clearAuthSession, getAuthSession, normalizeRole } from "../lib/auth";

type AccountView = "profile" | "notifications" | "settings";
type Activity = { id: number; status: string; department: string; created_at: string };

export function AccountPage({ view }: { view: AccountView }) {
  const router = useRouter();
  const [account, setAccount] = React.useState<{ username: string; role: string; userId: number } | null>(null);
  const [activity, setActivity] = React.useState<Activity[]>([]);
  const [loading, setLoading] = React.useState(view === "notifications");
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    const session = getAuthSession();
    if (!session || !["student", "worker"].includes(normalizeRole(session.role) ?? "")) {
      router.replace("/");
      return;
    }
    setAccount(session);

    if (view === "notifications") {
      void apiFetch("/complaints")
        .then(async (response) => {
          if (!response.ok) throw new Error("Could not load complaint updates.");
          const data = (await response.json()) as { complaints?: Activity[] };
          setActivity(data.complaints ?? []);
        })
        .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Could not load updates."))
        .finally(() => setLoading(false));
    }
  }, [router, view]);

  const signOut = () => {
    clearAuthSession();
    router.replace("/");
  };

  const titles: Record<AccountView, string> = {
    profile: "Profile",
    notifications: "Notifications",
    settings: "Settings",
  };

  return (
    <>
      <Sidebar />
      <main className="main-content">
        <Navbar />
        <p className="section-label">Your account</p>
        <h1 className="page-title">{titles[view]}</h1>
        <p className="page-subtitle">Account information and complaint activity for this signed-in session.</p>

        {view === "profile" && account && (
          <section className="mt-6 max-w-2xl rounded-2xl border bg-white p-6 shadow-sm" aria-label="Profile information">
            <h2 className="text-lg font-semibold">Account information</h2>
            <dl className="mt-4 grid gap-4 sm:grid-cols-2">
              <div><dt className="text-sm text-slate-500">Username</dt><dd className="mt-1 font-medium">{account.username}</dd></div>
              <div><dt className="text-sm text-slate-500">Role</dt><dd className="mt-1 font-medium capitalize">{account.role}</dd></div>
              <div><dt className="text-sm text-slate-500">Account ID</dt><dd className="mt-1 font-medium">{account.userId}</dd></div>
            </dl>
            <Link href="/user" className="mt-6 inline-block text-sm font-semibold text-blue-800 hover:underline">Return to dashboard</Link>
          </section>
        )}

        {view === "notifications" && (
          <section className="mt-6 max-w-3xl rounded-2xl border bg-white p-6 shadow-sm" aria-label="Complaint updates">
            <h2 className="text-lg font-semibold">Complaint updates</h2>
            {loading && <p className="mt-4 text-sm text-slate-600">Loading your latest complaint activity…</p>}
            {error && <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-800">{error}</p>}
            {!loading && !error && activity.length === 0 && <p className="mt-4 text-sm text-slate-600">No complaint activity yet. Updates will appear here after you submit a complaint.</p>}
            {!loading && !error && activity.length > 0 && (
              <ul className="mt-4 divide-y">
                {activity.slice(0, 10).map((item) => (
                  <li key={item.id} className="py-3 text-sm">
                    <span className="font-medium">Complaint #{item.id}</span> · {item.department} · <span className="capitalize">{item.status.replace(/_/g, " ")}</span>
                    <time className="mt-1 block text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</time>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        {view === "settings" && account && (
          <section className="mt-6 max-w-2xl rounded-2xl border bg-white p-6 shadow-sm" aria-label="Session settings">
            <h2 className="text-lg font-semibold">Sign-in session</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">You are signed in as <strong>{account.username}</strong>. CampusAid signs you out when your access session expires; you can also end this browser session now.</p>
            <button type="button" onClick={signOut} className="mt-5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700">Sign out</button>
          </section>
        )}
      </main>
    </>
  );
}
