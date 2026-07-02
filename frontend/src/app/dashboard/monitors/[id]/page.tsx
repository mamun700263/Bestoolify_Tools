"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
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
  const { id } = useParams();
  const router = useRouter();
  const [monitor, setMonitor] = useState<Monitor | null>(null);
  const [pings, setPings] = useState<Ping[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const [monRes, pingRes] = await Promise.all([
          API.get(`/uptime/monitors/${id}`),
          API.get(`/uptime/monitors/${id}/pings`),
        ]);
        setMonitor(monRes.data);
        setPings(pingRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [id]);

  const uptimePercent = () => {
    if (pings.length === 0) return "N/A";
    const up = pings.filter((p) => p.is_up).length;
    return ((up / pings.length) * 100).toFixed(1) + "%";
  };

  const avgResponse = () => {
    const valid = pings.filter((p) => p.response_time_ms !== null);
    if (valid.length === 0) return "N/A";
    const avg = valid.reduce((sum, p) => sum + p.response_time_ms!, 0) / valid.length;
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
      <div className="flex items-center gap-3 mb-6">
        <Link href="/dashboard/monitors" className="text-gray-400 hover:text-gray-600 text-sm">
          ← Back
        </Link>
        <h1 className="text-2xl font-bold text-gray-800">{monitor.name}</h1>
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
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-gray-500">URL</p>
          <p className="text-sm font-medium text-gray-800 mt-1 truncate">{monitor.url}</p>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Interval</p>
          <p className="text-2xl font-bold text-gray-800 mt-1">
            {monitor.interval_minutes}m
          </p>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Uptime</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{uptimePercent()}</p>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Avg Response</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{avgResponse()}</p>
        </div>
      </div>

      {/* Ping history */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="font-semibold text-gray-800">Ping History</h2>
          <p className="text-xs text-gray-400 mt-1">{pings.length} records</p>
        </div>

        {pings.length === 0 ? (
          <div className="p-6 text-center text-gray-400 text-sm">
            No pings recorded yet.
          </div>
        ) : (
          <ul className="divide-y max-h-[500px] overflow-y-auto">
            {pings.map((p) => (
              <li key={p.id} className="px-6 py-3 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      p.is_up ? "bg-green-500" : "bg-red-500"
                    }`}
                  />
                  <span className="text-sm text-gray-600">
                    {new Date(p.checked_at).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  {p.status_code && <span>HTTP {p.status_code}</span>}
                  {p.response_time_ms && <span>{p.response_time_ms}ms</span>}
                  {p.error_message && (
                    <span className="text-red-400 truncate max-w-[200px]">
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