"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Sidebar, type SidebarItem } from "../../components/ui/sidebar";
import { ComplaintTable, type Complaint } from "../../components/ComplaintTable";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { apiFetch, clearAuthSession, getAuthSession, isSessionExpiredError, normalizeRole } from "../../lib/auth";
import {
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const ALL_DEPARTMENTS = ["Hostel", "IT", "Academic", "Maintenance"] as const;

type Department = (typeof ALL_DEPARTMENTS)[number];

type Statistics = {
  total_complaints: number;
  resolved: number;
  pending: number;
  departments: Array<{
    name: string;
    total: number;
    resolved: number;
    pending: number;
    avg_resolution_time_days: number;
  }>;
  trend?: Array<{
    date: string;
    total: number;
  }>;
};

const NAVY = "var(--navy)";
const RED = "var(--danger)";
const PIE_COLORS = [NAVY, RED];

export default function AdminPortal() {
  const router = useRouter();
  const [role, setRole] = React.useState<"admin" | "warden" | null>(null);
  const [activeId, setActiveId] = React.useState("dashboard");
  const [complaints, setComplaints] = React.useState<Complaint[]>([]);
  const [statistics, setStatistics] = React.useState<Statistics | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [statsLoading, setStatsLoading] = React.useState(false);
  const [complaintsError, setComplaintsError] = React.useState<string | null>(null);
  const [updateError, setUpdateError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const storedRole = normalizeRole(getAuthSession()?.role);
    console.log("[AdminPortal] session role:", storedRole);
    if (storedRole !== "admin" && storedRole !== "warden") {
      router.replace("/");
      return;
    }
    setRole(storedRole);
  }, [router]);

  React.useEffect(() => {
    if (!role) {
      return;
    }

    void loadStatistics();

    if (activeId === "dashboard") {
      void loadAllComplaints();
    }

    if (activeId.startsWith("departments-")) {
      const department = activeId.replace("departments-", "") as Department;
      void loadDepartmentComplaints(department);
    }
  }, [role]);

  React.useEffect(() => {
    if (!role) {
      return;
    }

    if (activeId === "dashboard") {
      void loadAllComplaints();
    } else if (activeId.startsWith("departments-")) {
      const department = activeId.replace("departments-", "") as Department;
      void loadDepartmentComplaints(department);
    }
  }, [activeId, role]);

  const loadStatistics = async () => {
    setStatsLoading(true);
    try {
      console.log("[AdminPortal] fetching statistics...");
      const response = await apiFetch("/stats", {}, true);
      if (!response.ok) {
        throw new Error("Failed to fetch statistics");
      }

      const data = (await response.json()) as Statistics;
      console.log("[AdminPortal] statistics response:", data);
      setStatistics(data);
    } catch (error) {
      console.error("[AdminPortal] statistics fetch error:", error);
      if (isSessionExpiredError(error)) {
        clearAuthSession();
        router.replace("/");
        return;
      }
      setStatistics(null);
    } finally {
      setStatsLoading(false);
    }
  };

  const loadDepartmentComplaints = async (department: Department) => {
    setLoading(true);
    setComplaintsError(null);
    try {
      const params = new URLSearchParams();
      params.set("department", department);
      params.set("predicted_category", department);

      console.log("[AdminPortal] fetching complaints with params:", params.toString());
      const response = await apiFetch(`/complaints?${params.toString()}`, {}, true);
      if (!response.ok) {
        throw new Error("Failed to fetch complaints");
      }

      const data = (await response.json()) as { complaints?: Complaint[] } | Complaint[];
      console.log("[AdminPortal] complaints response:", data);

      const complaintsList = Array.isArray(data) ? data : (data.complaints ?? []);
      setComplaints(complaintsList);
    } catch (error) {
      console.error("[AdminPortal] complaints fetch error:", error);
      if (isSessionExpiredError(error)) {
        clearAuthSession();
        router.replace("/");
        return;
      }
      setComplaintsError(error instanceof Error ? error.message : "Failed to load complaints");
      setComplaints([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAllComplaints = async () => {
    setLoading(true);
    setComplaintsError(null);
    try {
      const params = new URLSearchParams();
      params.set("limit", "100");

      console.log("[AdminPortal] fetching all complaints");
      const response = await apiFetch(`/complaints?${params.toString()}`, {}, true);
      if (!response.ok) {
        throw new Error("Failed to fetch complaints");
      }

      const data = (await response.json()) as { complaints?: Complaint[] } | Complaint[];
      console.log("[AdminPortal] all complaints response:", data);

      const complaintsList = Array.isArray(data) ? data : (data.complaints ?? []);
      setComplaints(complaintsList);
    } catch (error) {
      console.error("[AdminPortal] all complaints fetch error:", error);
      if (isSessionExpiredError(error)) {
        clearAuthSession();
        router.replace("/");
        return;
      }
      setComplaintsError(error instanceof Error ? error.message : "Failed to load complaints");
      setComplaints([]);
    } finally {
      setLoading(false);
    }
  };

  const updateComplaintStatus = async (id: number, status: string) => {
    setUpdateError(null);
    try {
      console.log("[AdminPortal] updating complaint status:", { id, status });
      const response = await apiFetch(`/complaints/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
      }, true);

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const message = (payload as { detail?: string }).detail ?? "Failed to update complaint status";
        throw new Error(message);
      }

      const payload = (await response.json()) as {
        complaint?: Complaint;
      };
      console.log("[AdminPortal] status update response:", payload);

      setComplaints((prev) =>
        prev.map((complaint) =>
          complaint.id === id
            ? {
                ...complaint,
                status: payload.complaint?.status ?? status,
                department: payload.complaint?.department ?? complaint.department,
                predicted_category: payload.complaint?.predicted_category ?? complaint.predicted_category,
              }
            : complaint
        )
      );
    } catch (error) {
      console.error("[AdminPortal] status update error:", error);
      if (isSessionExpiredError(error)) {
        clearAuthSession();
        router.replace("/");
        return;
      }
      setUpdateError(error instanceof Error ? error.message : "Failed to update complaint status");
      throw error;
    }
  };

  const markResolved = async (id: number) => {
    await updateComplaintStatus(id, "resolved");
  };

  const handleLogout = () => {
    clearAuthSession();
    router.push("/");
  };

  const departmentItems: SidebarItem[] = (role === "warden"
    ? [{ id: "departments-Hostel", label: "Hostel" }]
    : ALL_DEPARTMENTS.map((dept) => ({
        id: `departments-${dept}`,
        label: dept
      }))) as SidebarItem[];

  const items: SidebarItem[] = [
    { id: "dashboard", label: "Dashboard" },
    { id: "departments", label: "Departments", children: departmentItems }
  ];

  const selectedDepartment = activeId.startsWith("departments-")
    ? activeId.replace("departments-", "")
    : null;

  const departmentChartData = (statistics?.departments ?? []).map((department) => ({
    name: department.name,
    total: department.total,
  }));

  const statusChartData = [
    { name: "Resolved", value: statistics?.resolved ?? 0 },
    { name: "Pending", value: statistics?.pending ?? 0 },
  ];

  const trendChartData = statistics?.trend ?? [];

  return (
    <div className="min-h-screen" style={{ background: "var(--surface)" }}>
      <Sidebar
        title="Admin Portal"
        items={items}
        activeId={activeId}
        onSelect={setActiveId}
        onLogout={handleLogout}
      />
      <main className="main-content">
        {activeId === "dashboard" && (
          <div className="space-y-8">
            <Card>
              <CardHeader>
                <div>
                  <p className="section-label">Admin Analytics</p>
                  <CardTitle className="page-title">Dashboard Overview</CardTitle>
                </div>
                <p className="text-sm leading-6" style={{ color: "var(--slate)" }}>
                  {role === "warden" 
                    ? "Hostel complaints statistics and overview"
                    : "System-wide complaint statistics and analytics"}
                </p>
              </CardHeader>
              <CardContent>
                {statsLoading ? (
                  <p className="text-sm" style={{ color: "var(--slate)" }}>Loading statistics...</p>
                ) : statistics ? (
                  <div className="space-y-8">
                    <div className="grid gap-4 md:grid-cols-3">
                      <div className="stat-card blue">
                        <p className="stat-label">Total Complaints</p>
                        <p className="stat-value">
                          {statistics.total_complaints}
                        </p>
                      </div>
                      <div className="stat-card green">
                        <p className="stat-label">Resolved</p>
                        <p className="stat-value">
                          {statistics.resolved}
                        </p>
                      </div>
                      <div className="stat-card red">
                        <p className="stat-label">Pending</p>
                        <p className="stat-value">
                          {statistics.pending}
                        </p>
                      </div>
                    </div>

                    <div className="grid gap-4 xl:grid-cols-2">
                      <Card>
                        <CardHeader>
                          <CardTitle>Complaints per Department</CardTitle>
                        </CardHeader>
                        <CardContent className="h-72">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={departmentChartData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                              <XAxis dataKey="name" tick={{ fill: "var(--slate)", fontSize: 12 }} />
                              <YAxis allowDecimals={false} tick={{ fill: "var(--slate)", fontSize: 12 }} />
                              <Tooltip />
                              <Bar dataKey="total" fill={NAVY} radius={[8, 8, 0, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle>Resolved vs Pending</CardTitle>
                        </CardHeader>
                        <CardContent className="h-72">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={statusChartData}
                                dataKey="value"
                                nameKey="name"
                                outerRadius={92}
                                innerRadius={50}
                                label
                              >
                                {statusChartData.map((entry, index) => (
                                  <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                                ))}
                              </Pie>
                              <Tooltip />
                              <Legend />
                            </PieChart>
                          </ResponsiveContainer>
                        </CardContent>
                      </Card>
                    </div>

                    {trendChartData.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle>Complaint Trend Over Time</CardTitle>
                        </CardHeader>
                        <CardContent className="h-72">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trendChartData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                              <XAxis dataKey="date" tick={{ fill: "var(--slate)", fontSize: 12 }} />
                              <YAxis allowDecimals={false} tick={{ fill: "var(--slate)", fontSize: 12 }} />
                              <Tooltip />
                              <Line
                                type="monotone"
                                dataKey="total"
                                stroke={RED}
                                strokeWidth={3}
                                dot={{ r: 4, fill: RED }}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </CardContent>
                      </Card>
                    )}

                    <div className="space-y-4">
                      <div>
                        <h2 className="card-title">Complaint Table</h2>
                        <p className="text-sm" style={{ color: "var(--slate)" }}>Latest complaints across departments.</p>
                      </div>

                      {complaintsError && (
                        <p className="rounded-[var(--radius)] border px-3 py-2 text-sm" style={{ borderColor: "var(--danger)", background: "var(--danger-bg)", color: "var(--danger)" }}>
                          {complaintsError}
                        </p>
                      )}
                      {updateError && (
                        <p className="rounded-[var(--radius)] border px-3 py-2 text-sm" style={{ borderColor: "var(--danger)", background: "var(--danger-bg)", color: "var(--danger)" }}>
                          {updateError}
                        </p>
                      )}
                      {loading ? (
                        <p className="text-sm" style={{ color: "var(--slate)" }}>Loading complaints...</p>
                      ) : (
                        <ComplaintTable
                          complaints={complaints}
                          showActions
                          onUpdateStatus={updateComplaintStatus}
                          onMarkResolved={markResolved}
                        />
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm" style={{ color: "var(--slate)" }}>Unable to load statistics</p>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {selectedDepartment && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div>
                  <p className="section-label">Department View</p>
                  <CardTitle>{selectedDepartment} Complaints</CardTitle>
                </div>
                <p className="text-sm" style={{ color: "var(--slate)" }}>
                  Admins see all departments, while wardens only see Hostel.
                </p>
              </CardHeader>
              <CardContent>
                {complaintsError && (
                  <p className="mb-3 rounded-[var(--radius)] border px-3 py-2 text-sm" style={{ borderColor: "var(--danger)", background: "var(--danger-bg)", color: "var(--danger)" }}>
                    {complaintsError}
                  </p>
                )}
                {updateError && (
                  <p className="mb-3 rounded-[var(--radius)] border px-3 py-2 text-sm" style={{ borderColor: "var(--danger)", background: "var(--danger-bg)", color: "var(--danger)" }}>
                    {updateError}
                  </p>
                )}
                {loading ? (
                  <p className="text-sm" style={{ color: "var(--slate)" }}>Loading...</p>
                ) : (
                  <ComplaintTable
                    complaints={complaints}
                    showActions
                    onUpdateStatus={updateComplaintStatus}
                    onMarkResolved={markResolved}
                  />
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
