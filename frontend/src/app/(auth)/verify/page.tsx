"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import API from "@/lib/api";

function VerifyContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const token = searchParams.get("token");

  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");

  const [message, setMessage] = useState("");

  useEffect(() => {
    if (token) {
      verifyToken(token);
    }
  }, [token]);

  const verifyToken = async (t: string) => {
    setStatus("loading");

    try {
      const res = await API.get(`/accounts/verify/${t}`);

      setMessage(res.data.message);
      setStatus("success");

      setTimeout(() => router.push("/login"), 3000);
    } catch (err: any) {
      setMessage(
        err.response?.data?.detail || "Verification failed"
      );

      setStatus("error");
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md text-center">
          <div className="text-5xl mb-4">📧</div>

          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            Check your email
          </h1>

          <p className="text-gray-500 text-sm">
            We sent a verification link to your email address.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md text-center">

        {status === "loading" && (
          <>
            <div className="text-5xl mb-4">⏳</div>
            <h1 className="text-2xl font-bold text-gray-800">
              Verifying...
            </h1>
          </>
        )}

        {status === "success" && (
          <>
            <div className="text-5xl mb-4">✅</div>

            <h1 className="text-2xl font-bold text-gray-800 mb-2">
              Email verified!
            </h1>

            <p className="text-gray-500 text-sm">
              {message}
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <div className="text-5xl mb-4">❌</div>

            <h1 className="text-2xl font-bold text-gray-800 mb-2">
              Verification failed
            </h1>

            <p className="text-red-500 text-sm">
              {message}
            </p>
          </>
        )}
      </div>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VerifyContent />
    </Suspense>
  );
}