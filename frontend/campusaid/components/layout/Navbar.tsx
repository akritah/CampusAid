"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "../ui/button";
import { Input } from "../ui/input";

type NavbarProps = {
  onVoiceClick?: () => void;
  onNewComplaintClick?: () => void;
  onSearch?: (query: string) => void;
};

export function Navbar({ onVoiceClick, onNewComplaintClick, onSearch }: NavbarProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = React.useState("");

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const query = searchQuery.trim();
    if (onSearch) onSearch(query);
    else router.push(`/user?search=${encodeURIComponent(query)}#all`);
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        {/* Search Bar */}
        <form className="navbar-search" onSubmit={handleSearch} role="search">
          <Input
            type="search"
            placeholder="Search complaints, departments..."
            aria-label="Search complaints and departments"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="navbar-search-input"
          />
        </form>

        {/* Right Section */}
        <div className="navbar-actions">
          {/* Notifications Bell */}
          <Link href="/user/notifications" className="navbar-icon-btn" title="Notifications" aria-label="Notifications">
            <span className="text-lg">🔔</span>
          </Link>

          {/* Voice Complaint Button */}
          <Button
            onClick={onVoiceClick ?? (() => router.push("/user/voice"))}
            className="btn btn-gold"
          >
            🎤 Voice Complaint
          </Button>

          {/* New Complaint Button */}
          <Button
            onClick={onNewComplaintClick ?? (() => router.push("/user#complaint-form"))}
            className="btn btn-primary"
          >
            + New Complaint
          </Button>
        </div>
      </div>
    </nav>
  );
}
