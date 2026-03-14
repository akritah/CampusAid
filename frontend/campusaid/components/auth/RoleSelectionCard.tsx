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
      className="group w-full text-left"
      aria-pressed={selected}
    >
      <Card
        className={cn(
          "hover-scale transition-all duration-200",
          selected
            ? "border-[var(--navy-light)] ring-2 ring-[rgba(30,49,112,0.12)]"
            : "group-hover:border-[var(--navy-light)]"
        )}
      >
        <CardHeader>
          <div className="stat-icon blue mb-3 text-xl">
            {icon}
          </div>
          <CardTitle className="text-xl" style={{ fontFamily: "var(--font-display)", color: "var(--navy)" }}>{title}</CardTitle>
          <p className="mt-1 text-sm" style={{ color: "var(--slate)" }}>{description}</p>
        </CardHeader>
        <CardContent>
          <div
            className={cn(
              "h-1 rounded-full transition-all duration-200",
              selected ? "w-16 bg-[var(--gold)]" : "w-10 bg-[var(--gold-pale)]"
            )}
          />
        </CardContent>
      </Card>
    </button>
  );
}
