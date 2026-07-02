import API from "@/lib/api";
import { getToken } from "@/lib/auth";
import { useAuthStore } from "@/store/auth";

export async function initAuth(): Promise<void> {
  const token = getToken();

  // No access token → guest user
  if (!token) {
    return;
  }

  try {
    const res = await API.get("/accounts/me");

    useAuthStore.getState().setAccount(res.data);
  } catch (err) {
    // Invalid/expired token (and refresh failed)
    useAuthStore.getState().logout();
  }
}