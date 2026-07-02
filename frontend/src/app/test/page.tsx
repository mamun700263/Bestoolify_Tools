
"use client";

import { useState } from "react";
import API from "@/lib/api";

interface PingResult {
  is_up: boolean;
  status_code: number | null;
  reason: string | null;
  response_time_ms: number | null;
  final_url: string | null;
  redirect_count: number | null;
  http_version: string | null;
  content_type: string | null;
  content_length: number | null;
  checked_at: string | null;
  error_message: string | null;
}

export default function TestPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PingResult | null>(null);

  const handleTest = async () => {
    if (!url.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const res = await API.get("/uptime/test-ping", {
        params: {
          url,
        },
      });

      setResult(res.data);
    } catch (error) {
      setResult({
        is_up: false,
        status_code: null,
        reason: null,
        response_time_ms: null,
        final_url: null,
        redirect_count: null,
        http_version: null,
        content_type: null,
        content_length: null,
        checked_at: null,
        error_message: "Failed to test endpoint.",
      });

      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const latencyColor =
    result?.response_time_ms == null
      ? "text-zinc-300"
      : result.response_time_ms < 200
      ? "text-emerald-400"
      : result.response_time_ms < 1000
      ? "text-yellow-400"
      : "text-red-400";

  return (
    <main className="min-h-screen bg-[#080808] text-white px-8 py-16">
      <div className="max-w-5xl mx-auto">
        {/* Hero */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 border border-zinc-800 rounded-full px-4 py-1.5 mb-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-zinc-400 font-mono">
              Instant endpoint diagnostics
            </span>
          </div>

          <h1 className="text-5xl font-black tracking-tight mb-4">
            Test Any API
          </h1>

          <p className="text-zinc-400 text-lg max-w-2xl">
            Check uptime, latency, redirects, content information,
            and endpoint health in seconds.
          </p>
        </div>

        {/* Input */}
        <div className="flex flex-col md:flex-row gap-4 mb-10">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https:/API.example.com"
            className="flex-1 bg-[#111] border border-zinc-800 rounded-xl px-5 py-4 outline-none focus:border-emerald-500"
          />

          <button
            onClick={handleTest}
            disabled={loading}
            className="px-8 py-4 rounded-xl bg-white text-black font-semibold hover:bg-zinc-200 transition-colors disabled:opacity-50"
          >
            {loading ? "Testing..." : "Test Endpoint"}
          </button>
        </div>

        {/* Success */}
        {result && result.is_up && (
          <>
            <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-6 mb-8">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-emerald-400" />

                <h2 className="font-bold text-emerald-300 text-lg">
                  Endpoint Healthy
                </h2>
              </div>

              <p className="text-zinc-300 mt-2">
                Status {result.status_code} {result.reason}
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <MetricCard
                title="Response Time"
                value={`${result.response_time_ms}ms`}
                valueClass={latencyColor}
              />

              <MetricCard
                title="Status Code"
                value={String(result.status_code)}
              />

              <MetricCard
                title="Redirects"
                value={String(result.redirect_count)}
              />

              <MetricCard
                title="HTTP Version"
                value={result.http_version ?? "Unknown"}
              />

              <MetricCard
                title="Content Type"
                value={result.content_type ?? "Unknown"}
              />

              <MetricCard
                title="Content Length"
                value={
                  result.content_length
                    ? `${(result.content_length / 1024).toFixed(1)} KB`
                    : "Unknown"
                }
              />

              <MetricCard
                title="Final URL"
                value={result.final_url ?? "Unknown"}
                large
              />

              <MetricCard
                title="Checked At"
                value={
                  result.checked_at
                    ? new Date(result.checked_at).toLocaleString()
                    : "Unknown"
                }
                large
              />
            </div>
          </>
        )}

        {/* Error */}
        {result && !result.is_up && (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-6">
            <h2 className="font-bold text-red-300 text-lg mb-2">
              Endpoint Unreachable
            </h2>

            <p className="text-zinc-300">
              {result.error_message}
            </p>
          </div>
        )}
      </div>
    </main>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  valueClass?: string;
  large?: boolean;
}

function MetricCard({
  title,
  value,
  valueClass = "text-white",
  large = false,
}: MetricCardProps) {
  return (
    <div
      className={`rounded-xl border border-zinc-800 bg-[#111] p-5 ${
        large ? "md:col-span-2" : ""
      }`}
    >
      <p className="text-sm text-zinc-500 mb-2">
        {title}
      </p>

      <p
        className={`font-semibold break-all ${
          large ? "text-base" : "text-2xl"
        } ${valueClass}`}
      >
        {value}
      </p>
    </div>
  );
}
