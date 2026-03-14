"use client";

import * as React from "react";
import { AuthContainer } from "../components/auth/AuthContainer";
import { LoginForm } from "../components/auth/LoginForm";
import { RoleSelectionCard } from "../components/auth/RoleSelectionCard";
import { clearAuthSession, type UserRole } from "../lib/auth";

export default function LandingPage() {
  const [mounted, setMounted] = React.useState(false);
  const [selectedRole, setSelectedRole] = React.useState<UserRole | null>(null);

  const roleCards: Array<{
    role: UserRole;
    title: string;
    description: string;
    icon: string;
  }> = [
    {
      role: "student",
      title: "Student",
      description: "Submit grievances and track resolutions transparently.",
      icon: "🎓",
    },
    {
      role: "worker",
      title: "Worker",
      description: "Report operational and infrastructure issues efficiently.",
      icon: "🛠️",
    },
    {
      role: "admin",
      title: "Admin",
      description: "Oversee governance workflows across all departments.",
      icon: "🧭",
    },
    {
      role: "warden",
      title: "Warden",
      description: "Manage hostel-related concerns with accountability.",
      icon: "🏛️",
    },
  ];

  React.useEffect(() => {
    setMounted(true);
    clearAuthSession();
  }, []);

  if (!mounted) {
    return <div className="min-h-screen" style={{ background: "var(--surface)" }} />;
  }

  const handleSelect = (role: UserRole) => {
    setSelectedRole(role);
  };

  return (
    <AuthContainer>
      <div className="grid gap-8 lg:grid-cols-[1.45fr_1fr] lg:items-start">
        <section>
          <p className="section-label">Access Control</p>
          <h2 className="page-title">Select Your Role</h2>
          <p className="page-subtitle">
            Choose your role to continue. Access is validated only by backend-authenticated role.
          </p>

          <div className="grid gap-4 md:grid-cols-2">
            {roleCards.map((card) => (
              <RoleSelectionCard
                key={card.role}
                role={card.role}
                title={card.title}
                description={card.description}
                icon={card.icon}
                selected={selectedRole === card.role}
                onSelect={handleSelect}
              />
            ))}
          </div>
        </section>

        <section className="lg:sticky lg:top-8">
          <LoginForm
            selectedRole={selectedRole}
          />
        </section>
      </div>
    </AuthContainer>
  );
}
