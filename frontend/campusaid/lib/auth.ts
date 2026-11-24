export type UserRole = "student" | "worker" | "admin" | "warden";

type LoginResponse = {
  success: boolean;
  message: string;
  user_id: number;
  username: string;
  role: UserRole;
  access_token: string;
};

const ROLE_KEY = "campusaid_role";
const USER_ID_KEY = "campusaid_user_id";
const USERNAME_KEY = "campusaid_username";
const ACCESS_TOKEN_KEY = "campusaid_access_token";
const SESSION_EXPIRED_MESSAGE = "SESSION_EXPIRED";

export function getApiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, "");
  if (!value) {
    throw new Error("NEXT_PUBLIC_API_URL must be configured for the frontend deployment");
  }
  return value;
}

export function normalizeRole(role: string | null | undefined): UserRole | null {
  if (!role) {
    return null;
  }

  const normalized = role.toLowerCase();
  if (
    normalized === "student" ||
    normalized === "worker" ||
    normalized === "admin" ||
    normalized === "warden"
  ) {
    return normalized;
  }

  return null;
}

export function saveAuthSession(login: LoginResponse): void {
  const normalizedRole = normalizeRole(login.role);
  if (!normalizedRole) {
    throw new Error("Invalid role in login response");
  }

  window.localStorage.setItem(ROLE_KEY, normalizedRole);
  window.localStorage.setItem(USER_ID_KEY, String(login.user_id));
  window.localStorage.setItem(USERNAME_KEY, login.username);
  window.localStorage.setItem(ACCESS_TOKEN_KEY, login.access_token);
}

export function clearAuthSession(): void {
  window.localStorage.removeItem(ROLE_KEY);
  window.localStorage.removeItem(USER_ID_KEY);
  window.localStorage.removeItem(USERNAME_KEY);
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem("campusaid_basic_auth");
}

export function getAuthSession() {
  const role = normalizeRole(window.localStorage.getItem(ROLE_KEY));
  const userIdRaw = window.localStorage.getItem(USER_ID_KEY);
  const username = window.localStorage.getItem(USERNAME_KEY);
  const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);

  if (!role || !userIdRaw || !username || !accessToken) {
    clearAuthSession();
    return null;
  }

  const userId = Number(userIdRaw);

  if (!Number.isFinite(userId)) {
    clearAuthSession();
    return null;
  }

  return {
    role,
    userId,
    username,
  };
}

export async function loginWithPassword(username: string, password: string): Promise<UserRole> {
  const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error("Invalid username or password");
  }

  const login = (await response.json()) as LoginResponse;
  saveAuthSession(login);

  const normalizedRole = normalizeRole(login.role);
  if (!normalizedRole) {
    throw new Error("Invalid role in login response");
  }

  return normalizedRole;
}

export function getAuthHeaders(requireAuth = true): HeadersInit {
  const session = getAuthSession();
  if (!session && requireAuth) {
    clearAuthSession();
    throw new Error(SESSION_EXPIRED_MESSAGE);
  }

  const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);
  if (requireAuth && !accessToken) {
    clearAuthSession();
    throw new Error(SESSION_EXPIRED_MESSAGE);
  }

  if (!accessToken) {
    return {};
  }

  return {
    Authorization: `Bearer ${accessToken}`,
  };
}

export async function apiFetch(path: string, init: RequestInit = {}, requireAuth = true): Promise<Response> {
  const existingHeaders = (init.headers ?? {}) as Record<string, string>;
  const authHeaders = getAuthHeaders(requireAuth);

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      ...existingHeaders,
      ...(authHeaders as Record<string, string>),
    },
  });

  if (response.status === 401) {
    clearAuthSession();
    if (typeof window !== "undefined" && window.location.pathname !== "/") {
      window.sessionStorage.setItem("campusaid_session_expired", "1");
      window.location.replace("/");
    }
    throw new Error(SESSION_EXPIRED_MESSAGE);
  }

  return response;
}

export function isSessionExpiredError(error: unknown): boolean {
  return error instanceof Error && error.message === SESSION_EXPIRED_MESSAGE;
}
