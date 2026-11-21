import * as React from "react";
import { cn } from "./utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline";
  size?: "sm" | "md" | "lg";
}

// Shared UI button used across portals.
export function Button({
  className,
  variant = "primary",
  size = "md",
  ...props
}: ButtonProps) {
  return (
    <button
      suppressHydrationWarning
      className={cn(
        "btn focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[rgba(30,49,112,0.25)] disabled:cursor-not-allowed disabled:opacity-60",
        size === "sm" && "btn-sm",
        size === "lg" && "btn-lg",
        variant === "primary" && "btn-primary",
        variant === "secondary" && "btn-gold",
        variant === "outline" && "btn-outline",
        className
      )}
      {...props}
    />
  );
}
