"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { AuthContainer } from "../../components/auth/AuthContainer";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Select } from "../../components/ui/select";
import { getApiBaseUrl, type UserRole } from "../../lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [role, setRole] = React.useState<UserRole>("student");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState(false);

  const isDisabled = 
    loading || 
    !username.trim() || 
    !password.trim() || 
    !confirmPassword.trim() ||
    password !== confirmPassword;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username.trim(),
          password: password,
          role: role,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setSuccess(true);
        setTimeout(() => {
          router.push("/");
        }, 2000);
      } else if (response.status === 400) {
        setError(data.detail || "Username already exists");
      } else {
        setError(data.detail || "Registration failed. Please try again.");
      }
    } catch (err) {
      console.error("Registration error:", err);
      setError("Network error. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContainer>
      <div className="mx-auto max-w-md">
        <Card>
          <CardHeader>
            <div>
              <p className="section-label">Registration</p>
              <CardTitle className="auth-form-title">Create Account</CardTitle>
            </div>
            <p className="auth-form-subtitle !mb-0">
              Register to access the CampusAid portal
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="input-group">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="Choose a username"
                  autoComplete="username"
                  required
                />
              </div>

              <div className="input-group">
                <Label htmlFor="role">Role</Label>
                <Select
                  id="role"
                  value={role}
                  onChange={(event) => setRole(event.target.value as UserRole)}
                  required
                >
                  <option value="student">Student</option>
                  <option value="worker">Worker</option>
                  <option value="admin">Admin</option>
                  <option value="warden">Warden</option>
                </Select>
              </div>

              <div className="input-group">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="At least 6 characters"
                  autoComplete="new-password"
                  required
                />
              </div>

              <div className="input-group">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="Re-enter password"
                  autoComplete="new-password"
                  required
                />
              </div>

              {error && (
                <p className="rounded-[var(--radius)] border px-3 py-2 text-sm" style={{ borderColor: "var(--danger)", background: "var(--danger-bg)", color: "var(--danger)" }}>
                  {error}
                </p>
              )}

              {success && (
                <p className="rounded-[var(--radius)] border px-3 py-2 text-sm" style={{ borderColor: "var(--success)", background: "var(--success-bg)", color: "var(--success)" }}>
                  Registration successful! Redirecting to login...
                </p>
              )}

              <Button
                type="submit"
                disabled={isDisabled}
                className="btn btn-primary w-full"
              >
                {loading ? (
                  <span className="inline-flex items-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                    Creating Account...
                  </span>
                ) : (
                  "Create Account"
                )}
              </Button>

              <div className="text-center text-sm" style={{ color: "var(--slate)" }}>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => router.push("/")}
                  className="font-semibold hover:underline"
                  style={{ color: "var(--navy)" }}
                >
                  Login here
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </AuthContainer>
  );
}
