"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export function useAuth() {
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    setIsAuthenticated(!!localStorage.getItem("access_token"));
  }, [pathname]);

  return isAuthenticated;
}