import { create } from "zustand";
import { persist } from "zustand/middleware";

interface Account {
  id: string;
  email: string;
  role: string;
  is_verified: boolean;
  status: string;
}

interface AuthState {
  account: Account | null;
  isAuthenticated: boolean;
  login: (account: Account, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  setAccount: (account: Account) => void;
}

export const getToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
};

export const setToken = (token: string): void => {
  localStorage.setItem("access_token", token);
};

export const removeToken = (): void => {
  localStorage.removeItem("access_token");
};
function setAccount(accountId: string) {
  localStorage.setItem("account_id", accountId);
}
export const isAuthenticated = (): boolean => {
  return !!getToken();
};
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      account: null,
      isAuthenticated: false,

      login: (account, accessToken, refreshToken) => {
        setToken(accessToken);
        localStorage.setItem("refresh_token", refreshToken);
        set({ account, isAuthenticated: true });
      },

      logout: () => {
        removeToken();
        localStorage.removeItem("refresh_token");
        set({ account: null, isAuthenticated: false });
      },

      setAccount: (account) => set({ account }),
    }),
    {
      name: "auth-storage",
    }
  )
);