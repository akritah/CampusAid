import * as React from "react";
import { cn } from "./utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline";
}

// Shared UI button used across portals.
export function Button({
  className,
  variant = "primary",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "btn focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[rgba(30,49,112,0.25)] disabled:cursor-not-allowed disabled:opacity-60",
        variant === "primary" && "btn-primary",
        variant === "secondary" && "btn-gold",
        variant === "outline" && "btn-outline",
        className
      )}
      {...props}
    />
  );
}
