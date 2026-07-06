"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import API from "@/lib/api";
import Link from "next/link";

interface Monitor {
  id: string;
  name: string;
  url: string;
  interval_minutes: number;
  is_active: boolean;
}

interface Ping {
  id: string;
  is_up: boolean;
  status_code: number | null;
  response_time_ms: number | null;
  error_message: string | null;
  checked_at: string;
}

export default function MonitorDetailPage() {
  const params = useParams();
  const rawId = params?.id;
  const monitorId = Array.isArray(rawId) ? rawId[0] : rawId;

  const [monitor, setMonitor] = useState<Monitor | null>(null);
  const [pings, setPings] = useState<Ping[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!monitorId) return;

    const fetchData = async () => {
      try {
        const [monRes, pingRes] = await Promise.all([
          API.get(`/uptime/monitors/${monitorId}`),
          API.get(`/uptime/monitors/${monitorId}/pings`),
        ]);

        setMonitor(monRes.data);
        setPings(pingRes.data.pings);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [monitorId]);

  const uptimePercent = () => {
    if (!pings.length) return "N/A";
    const up = pings.filter((p) => p.is_up).length;
    return ((up / pings.length) * 100).toFixed(1) + "%";
  };

  const avgResponse = () => {
    const valid = pings.filter((p) => p.response_time_ms !== null);
    if (!valid.length) return "N/A";

    const avg =
      valid.reduce((sum, p) => sum + (p.response_time_ms ?? 0), 0) /
      valid.length;

    return Math.round(avg) + "ms";
  };

  if (loading) {
    return <div className="text-sm text-gray-400">Loading...</div>;
  }

  if (!monitor) {
    return <div className="text-sm text-red-400">Monitor not found.</div>;
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <Link
          href="/dashboard/monitors"
          className="text-sm text-gray-400 hover:text-gray-600"
        >
          ← Back
        </Link>

        <h1 className="text-2xl font-bold text-gray-800">
          {monitor.name}
        </h1>

        <span
          className={`text-xs px-2 py-1 rounded-full font-medium ${
            monitor.is_active
              ? "bg-green-100 text-green-700"
              : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {monitor.is_active ? "Active" : "Paused"}
        </span>
      </div>

      {/* Stats */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">URL</p>
          <div className="min-w-0">
            <p className="mt-1 truncate text-sm font-medium text-gray-800">
              {monitor.url}
            </p>
          </div>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">Interval</p>
          <p className="mt-1 text-2xl font-bold text-gray-800">
            {monitor.interval_minutes}m
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">Uptime</p>
          <p className="mt-1 text-2xl font-bold text-green-600">
            {uptimePercent()}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">Avg Response</p>
          <p className="mt-1 text-2xl font-bold text-blue-600">
            {avgResponse()}
          </p>
        </div>
      </div>

      {/* Ping history */}
      <div className="rounded-xl border bg-white shadow-sm">
        <div className="border-b p-6">
          <h2 className="font-semibold text-gray-800">Ping History</h2>
          <p className="mt-1 text-xs text-gray-400">
            {pings.length} records
          </p>
        </div>

        {!pings.length ? (
          <div className="p-6 text-center text-sm text-gray-400">
            No pings recorded yet.
          </div>
        ) : (
          <ul className="max-h-[500px] divide-y overflow-y-auto">
            {pings.map((p) => (
              <li
                key={p.id}
                className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6"
              >
                {/* Left */}
                <div className="flex items-center gap-3">
                  <span
                    className={`h-2 w-2 rounded-full ${
                      p.is_up ? "bg-green-500" : "bg-red-500"
                    }`}
                  />
                  <span className="text-sm text-gray-600">
                    {new Date(p.checked_at).toLocaleString()}
                  </span>
                </div>

                {/* Right */}
                <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                  {p.status_code !== null && (
                    <span>HTTP {p.status_code}</span>
                  )}

                  {p.response_time_ms !== null && (
                    <span>{p.response_time_ms}ms</span>
                  )}

                  {p.error_message && (
                    <span className="max-w-[200px] truncate text-red-400">
                      {p.error_message}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}