import { create } from "zustand";

interface UserInfo {
  id: string;
  email: string;
  full_name?: string;
  workspace_id?: string;
  role?: string;
}

interface AuthState {
  token: string | null;
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  sessionExpiredMessage: string | null;

  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, fullName?: string) => Promise<boolean>;
  logout: (message?: string) => void;
  checkAuth: () => Promise<boolean>;
  clearError: () => void;
  clearSessionExpiredMessage: () => void;
}

const API_BASE = "/api";

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem("token") || null,
  user: null,
  isAuthenticated: !!localStorage.getItem("token"),
  isLoading: false,
  error: null,
  sessionExpiredMessage: null,

  clearError: () => set({ error: null }),
  clearSessionExpiredMessage: () => set({ sessionExpiredMessage: null }),

  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true, error: null, sessionExpiredMessage: null });
      const params = new URLSearchParams();
      params.append("username", email);
      params.append("password", password);

      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: params.toString(),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: "Login failed" }));
        throw new Error(data.detail || "Invalid email or password");
      }

      const data = await res.json();
      const token = data.access_token;
      localStorage.setItem("token", token);

      set({
        token,
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        sessionExpiredMessage: null,
      });
      return true;
    } catch (err: any) {
      set({
        isLoading: false,
        error: err.message || "Failed to log in",
        isAuthenticated: false,
        token: null,
      });
      localStorage.removeItem("token");
      return false;
    }
  },

  register: async (email: string, password: string, fullName?: string) => {
    try {
      set({ isLoading: true, error: null, sessionExpiredMessage: null });
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName || email.split("@")[0],
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: "Registration failed" }));
        throw new Error(data.detail || "Registration failed");
      }

      const data = await res.json();
      const token = data.access_token;
      localStorage.setItem("token", token);

      set({
        token,
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        sessionExpiredMessage: null,
      });
      return true;
    } catch (err: any) {
      set({
        isLoading: false,
        error: err.message || "Failed to register",
        isAuthenticated: false,
        token: null,
      });
      localStorage.removeItem("token");
      return false;
    }
  },

  logout: (message?: string) => {
    localStorage.removeItem("token");
    set({
      token: null,
      user: null,
      isAuthenticated: false,
      sessionExpiredMessage: message || null,
      isLoading: false,
    });
  },

  checkAuth: async () => {
    const token = get().token || localStorage.getItem("token");
    if (!token) {
      set({ isAuthenticated: false, user: null, token: null });
      return false;
    }

    try {
      set({ isLoading: true });
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.status === 401) {
        get().logout("Session expired, please log in again");
        return false;
      }

      if (!res.ok) {
        get().logout();
        return false;
      }

      const user = await res.json();
      set({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      });
      return true;
    } catch {
      // In case of network errors or server downtime, don't crash
      set({ isLoading: false });
      return false;
    }
  },
}));
