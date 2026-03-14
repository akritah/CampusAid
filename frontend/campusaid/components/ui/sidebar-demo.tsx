"use client";

import * as React from "react";
import { Sidebar, type SidebarItem } from "./sidebar";

// Demo wrapper inspired by https://ui.aceternity.com/components/sidebar
// Used to showcase the shared Sidebar component styling.
export function SidebarDemo() {
  const [activeId, setActiveId] = React.useState("overview");

  const items: SidebarItem[] = [
    { id: "overview", label: "Overview" },
    {
      id: "departments",
      label: "Departments",
      children: [
        { id: "departments-hostel", label: "Hostel" },
        { id: "departments-it", label: "IT" }
      ]
    }
  ];

  return (
    <div className="h-96 rounded-[var(--radius-lg)] border border-dashed" style={{ borderColor: "var(--border)" }}>
      <Sidebar
        title="Demo"
        items={items}
        activeId={activeId}
        onSelect={setActiveId}
        onLogout={() => setActiveId("overview")}
      />
    </div>
  );
}
