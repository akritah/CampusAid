"use client";

import * as React from "react";

type AuthContainerProps = {
  children: React.ReactNode;
};

export function AuthContainer({ children }: AuthContainerProps) {
  return (
    <main className="auth-screen">
      <section className="auth-left">
        <div className="mb-8 flex items-center gap-3">
          <div className="sidebar-logo-mark">C</div>
          <div>
            <p className="sidebar-logo-text">CampusAid</p>
            <p className="sidebar-logo-sub">Bennett University</p>
          </div>
        </div>

        <h1 className="auth-left-title">Campus Grievance Portal</h1>
        <p className="auth-left-subtitle">
          A transparent, accountable, and secure channel for raising, tracking, and resolving campus concerns.
        </p>

        <div className="mt-8">
          <div className="auth-feature-card">
            <span>🧭</span>
            <div>
              <p className="auth-feature-title">Smart Routing</p>
              <p className="auth-feature-desc">Classify and direct complaints to the right department.</p>
            </div>
          </div>
          <div className="auth-feature-card">
            <span>🔐</span>
            <div>
              <p className="auth-feature-title">Secure Access</p>
              <p className="auth-feature-desc">Role-based login with protected workflows for every user.</p>
            </div>
          </div>
          <div className="auth-feature-card">
            <span>📈</span>
            <div>
              <p className="auth-feature-title">Transparent Tracking</p>
              <p className="auth-feature-desc">Monitor status and resolution history in real time.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="auth-right">
        <div className="auth-form-wrap">
          <h2 className="auth-form-title">Welcome Back</h2>
          <p className="auth-form-subtitle">Select your role and sign in to continue.</p>

          {children}

          <footer className="mt-6 text-center text-xs" style={{ color: "var(--slate-light)" }}>
            © Bennett University | CampusAid 2024
          </footer>
        </div>
      </section>
    </main>
  );
}
