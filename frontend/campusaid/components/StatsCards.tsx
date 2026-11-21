"use client";

import * as React from "react";
import { Card, CardContent } from "./ui/card";

export type StatsData = {
  totalComplaints: number;
  totalThisMonth: number;
  pendingReview: number;
  avgPendingDays: number;
  resolved: number;
  successRate: number;
  escalated: number;
};

type StatsCardsProps = {
  data: StatsData;
};

export function StatsCards({ data }: StatsCardsProps) {
  const stats = [
    {
      label: "Total Complaints Filed",
      value: data.totalComplaints,
      subLabel: `${data.totalThisMonth} this month`,
      icon: "📋",
      color: "blue",
    },
    {
      label: "Pending Review",
      value: data.pendingReview,
      subLabel: `Avg ${data.avgPendingDays} days`,
      icon: "⏳",
      color: "amber",
    },
    {
      label: "Resolved",
      value: data.resolved,
      subLabel: `${data.successRate}% success rate`,
      icon: "✅",
      color: "green",
    },
    {
      label: "Escalated",
      value: data.escalated,
      subLabel: "All in good standing",
      icon: "📈",
      color: "red",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {stats.map((stat, index) => (
        <Card key={index} className="stat-card">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="text-sm font-semibold text-slate-600 mb-2">
                  {stat.label}
                </div>
                <div className="text-3xl font-bold text-navy mb-1">
                  {stat.value}
                </div>
                <div className="text-xs text-slate-500">
                  {stat.subLabel}
                </div>
              </div>
              <div className="text-2xl">{stat.icon}</div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
