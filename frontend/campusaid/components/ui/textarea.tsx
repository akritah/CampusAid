import * as React from "react";
import { cn } from "./utils";

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        suppressHydrationWarning
        className={cn(
          "input-field",
          className
        )}
        {...props}
      />
    );
  }
);

Textarea.displayName = "Textarea";
