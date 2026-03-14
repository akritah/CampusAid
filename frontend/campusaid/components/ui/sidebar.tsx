"use client";

import * as React from "react";
import { cn } from "./utils";

export type SidebarItem = {
  id: string;
  label: string;
  children?: SidebarItem[];
};

interface SidebarProps {
  title: string;
  items: SidebarItem[];
  activeId: string;
  onSelect: (id: string) => void;
  onLogout: () => void;
}

// Sidebar layout component shared by both portals.
export function Sidebar({
  title,
  items,
  activeId,
  onSelect,
  onLogout
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="flex items-center gap-3">
          <div className="sidebar-logo-mark">C</div>
          <div>
            <p className="sidebar-logo-text">CampusAid</p>
            <p className="sidebar-logo-sub">{title}</p>
          </div>
        </div>
      </div>

      <p className="sidebar-section-label">Navigation</p>

      <nav className="flex-1 px-2 py-2">
        {items.map((item) => (
          <div key={item.id}>
            <button
              onClick={() => onSelect(item.id)}
              className={cn(
                "sidebar-item w-full text-left",
                activeId === item.id && "active"
              )}
              aria-current={activeId === item.id ? "page" : undefined}
            >
              <span>{item.label}</span>
            </button>
            {item.children && activeId.startsWith(item.id) && (
              <div className="ml-3 mt-1 border-l border-white/20 pl-2">
                {item.children.map((child) => (
                  <button
                    key={child.id}
                    onClick={() => onSelect(child.id)}
                    className={cn(
                      "sidebar-item w-full text-left",
                      activeId === child.id && "active"
                    )}
                    aria-current={activeId === child.id ? "page" : undefined}
                  >
                    {child.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="mb-3 flex items-center gap-2">
          <div className="user-avatar">AU</div>
          <div>
            <p className="user-name">Authenticated User</p>
            <p className="user-role">{title}</p>
          </div>
        </div>
        <button
          onClick={onLogout}
          className="btn btn-outline w-full"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}
