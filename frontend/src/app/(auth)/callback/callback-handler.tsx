"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import API from "@/lib/api";
import { useAuthStore } from "@/store/auth";

export default function CallbackContent() {
  const router = useRouter();
  const params = useSearchParams();
  const login = useAuthStore((s) => s.login);

  useEffect(() => {
    const access = params.get("access_token");
    const refresh = params.get("refresh_token");

    if (!access || !refresh) {
      router.push("/login");
      return;
    }

    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);

    API
      .get("/accounts/me")
      .then((res) => {
        login(res.data, access, refresh);
        router.push("/dashboard");
      })
      .catch(() => {
        localStorage.clear();
        router.push("/login");
      });
  }, [params, router, login]);

  return <p>Signing you in...</p>;
}