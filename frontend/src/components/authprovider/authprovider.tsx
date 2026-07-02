"use client";

import { useEffect, useState } from "react";
import { initAuth } from "@/lib/authBootstrap";

interface AuthProviderProps {
  children: React.ReactNode;
}

export default function AuthProvider({
  children,
}: AuthProviderProps) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      try {
        await initAuth();
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, []);

  // Prevent the app from rendering until auth has been initialized
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-gray-500">Loading...</p>
      </div>
    );
  }

  return <>{children}</>;
}