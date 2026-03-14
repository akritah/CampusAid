import * as React from "react";
import { cn } from "./utils";

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={cn(
          "input-field select-field",
          className
        )}
        {...props}
      />
    );
  }
);

Select.displayName = "Select";
