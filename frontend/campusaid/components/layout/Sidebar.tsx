"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getAuthSession, clearAuthSession } from "../../lib/auth";

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [session, setSession] = React.useState<{ username: string; role: string } | null>(null);

  React.useEffect(() => {
    const auth = getAuthSession();
    if (auth) {
      setSession({ username: auth.username, role: auth.role });
    }
  }, []);

  const handleLogout = () => {
    clearAuthSession();
    router.push("/");
  };

  const isActive = (href: string) => {
    return pathname === href;
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-brand">
        <div className="flex items-center gap-2 mb-2">
          <div className="sidebar-logo-mark">C</div>
          <div>
            <div className="sidebar-logo-text">CampusAid</div>
            <div className="sidebar-logo-sub">Student Portal</div>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 space-y-1">
        <div className="sidebar-section-label">Navigation</div>
        <Link
          href="/user"
          className={`sidebar-item ${isActive("/user") ? "active" : ""}`}
        >
          <span>📊</span> Dashboard
        </Link>
        <Link
          href="/user/voice"
          className={`sidebar-item ${isActive("/user/voice") ? "active" : ""}`}
        >
          <span>🎤</span> Voice Complaint
        </Link>
        <Link href="/user/policies" className={`sidebar-item ${isActive("/user/policies") ? "active" : ""}`}>
          <span>📚</span> Ask University Policy
        </Link>

        {/* My Complaints Section */}
        <div className="sidebar-section-label mt-6">My Complaints</div>
        <Link href="/user#all" className="sidebar-item">
          <span>📋</span> All Complaints
        </Link>
        <Link href="/user#pending" className="sidebar-item">
          <span>⏳</span> Pending
        </Link>
        <Link href="/user#track" className="sidebar-item">
          <span>📍</span> Track Status
        </Link>
        <Link href="/user#resolved" className="sidebar-item">
          <span>✅</span> Resolved
        </Link>

        {/* Account Section */}
        <div className="sidebar-section-label mt-6">Account</div>
        <Link href="/user/profile" className="sidebar-item">
          <span>👤</span> Profile
        </Link>
        <Link href="/user/notifications" className="sidebar-item">
          <span>🔔</span> Notifications
        </Link>
        <Link href="/user/settings" className="sidebar-item">
          <span>⚙️</span> Settings
        </Link>
      </nav>

      {/* User Footer */}
      <div className="sidebar-footer">
        <div className="flex items-center gap-2 mb-3">
          <div
            className="user-avatar"
            title={session?.username}
          >
            {session?.username?.charAt(0).toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-white truncate">
              {session?.username || "User"}
            </div>
            <div className="text-xs text-gray-400 capitalize truncate">
              {session?.role || "Student"}
            </div>
          </div>
        </div>
        <button
          onClick={handleLogout}
          suppressHydrationWarning
          className="w-full text-left text-xs font-semibold text-red-400 hover:text-red-300 transition-colors"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}
