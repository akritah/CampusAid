"use client";

import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { cn } from "../ui/utils";
import type { UserRole } from "../../lib/auth";

type RoleSelectionCardProps = {
  role: UserRole;
  title: string;
  description: string;
  icon: string;
  selected: boolean;
  onSelect: (role: UserRole) => void;
};

export function RoleSelectionCard({
  role,
  title,
  description,
  icon,
  selected,
  onSelect,
}: RoleSelectionCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(role)}
      className="role-card-button group w-full text-left"
      aria-pressed={selected}
    >
      <Card
        className={cn(
          "role-card hover-scale transition-all duration-200",
          selected
            ? "role-card--selected border-[var(--navy-light)] ring-2 ring-[rgba(30,49,112,0.16)]"
            : "group-hover:border-[var(--navy-light)]"
        )}
      >
        <CardHeader className="role-card-header">
          <div className="role-card-icon">
            {icon}
          </div>
          <CardTitle className="role-card-title">{title}</CardTitle>
          <p className="role-card-description">{description}</p>
        </CardHeader>
        <CardContent className="role-card-footer">
          <div
            className={cn(
              "role-card-indicator transition-all duration-200",
              selected ? "w-16 bg-[var(--gold)]" : "w-10 bg-[var(--gold-pale)]"
            )}
          />
        </CardContent>
      </Card>
    </button>
  );
}
