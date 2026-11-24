"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  getApiBaseUrl,
  normalizeRole,
  saveAuthSession,
  type UserRole
} from "../../lib/auth";

type LoginFormProps = {
  selectedRole: UserRole | null;
};

export function LoginForm({ selectedRole }: LoginFormProps) {
  const router = useRouter();
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (window.sessionStorage.getItem("campusaid_session_expired") === "1") {
      window.sessionStorage.removeItem("campusaid_session_expired");
      setError("Your session expired. Please sign in again.");
    }
  }, []);

  const handleLogin = async (loginUsername: string, loginPassword: string, targetRole?: UserRole) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: loginUsername.trim(),
          password: loginPassword,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        const normalizedRole = normalizeRole(data.role);
        console.info("Login successful for role:", normalizedRole);

        if (!normalizedRole) {
          setError("Invalid role returned by server.");
          return;
        }

        const expectedRole = targetRole || selectedRole;
        if (expectedRole && expectedRole !== normalizedRole) {
          setError(`Selected role (${expectedRole}) does not match account role (${normalizedRole}).`);
          return;
        }

        saveAuthSession({ ...data, role: normalizedRole });

        // Role-based navigation
        if (normalizedRole === "admin" || normalizedRole === "warden") {
          router.push("/admin");
        } else {
          router.push("/user");
        }
      } else if (response.status === 401) {
        setError("Invalid username or password");
      } else {
        setError(data.detail || "Login failed. Please try again.");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Network error. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!username.trim() || !password.trim()) {
      return;
    }

    await handleLogin(username, password);
  };

  return (
    <Card
      className={[
        "login-card",
        "fade-in-up",
        selectedRole ? "opacity-100 translate-y-0" : "opacity-90 translate-y-1"
      ].join(" ")}
    >
      <CardHeader className="login-card-header">
        <div>
          <p className="section-label">Authentication</p>
          <CardTitle className="auth-card-title">Secure Login</CardTitle>
        </div>
        <p className="auth-card-subtitle !mb-0">
          {selectedRole
            ? `Selected role: ${selectedRole}. Login to continue.`
            : "Select your account role, then enter your credentials."}
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="input-group">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Enter username"
              autoComplete="username"
              className={error ? "border-[var(--danger)]" : undefined}
              required
            />
          </div>

          <div className="input-group">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter password"
              autoComplete="current-password"
              className={error ? "border-[var(--danger)]" : undefined}
              required
            />
          </div>

          {error && (
            <p className="rounded-[var(--radius)] border px-3 py-2 text-sm" style={{ borderColor: "var(--danger)", background: "var(--danger-bg)", color: "var(--danger)" }}>
              {error}
            </p>
          )}

          <Button
            type="submit"
            aria-label="Login"
            data-testid="login-button"
            disabled={loading || !username.trim() || !password.trim()}
            className="btn btn-primary login-submit-btn w-full"
          >
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                Logging in...
              </span>
            ) : (
              "Login"
            )}
          </Button>

          <div className="text-center text-sm" style={{ color: "var(--slate)" }}>
            Don't have an account?{" "}
            <button
              type="button"
              onClick={() => router.push("/signup")}
              className="font-semibold hover:underline"
              style={{ color: "var(--navy)" }}
            >
              Sign up here
            </button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
