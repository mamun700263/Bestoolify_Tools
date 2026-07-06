"use client";

import { useEffect, useState } from "react";
import API from "@/lib/api";

export default function SystemPulseSection() {
  const [users, setUsers] = useState<number | null>(null);
  const [monitors, setMonitors] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [userRes, monitorRes] = await Promise.all([
          API.get("/accounts/all_account_count"),
          API.get("/uptime/motinor_count/"),
        ]);

        setUsers(userRes.data);
        setMonitors(monitorRes.data);
      } catch (err) {
        console.error("SystemPulse fetch failed:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <section className="relative mx-auto max-w-6xl px-6 py-24">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-bold sm:text-4xl">
          Live System Pulse
        </h2>
        <p className="mt-2 text-sm text-gray-400">
          Real-time system scale across infrastructure
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
          <p className="text-xs text-gray-400">Active Users</p>

          {loading ? (
            <div className="mt-2 h-8 w-20 animate-pulse rounded bg-white/10" />
          ) : (
            <p className="mt-2 text-3xl font-bold text-emerald-400">
              {users?.toLocaleString() ?? "—"}
            </p>
          )}
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
          <p className="text-xs text-gray-400">Monitors Running</p>

          {loading ? (
            <div className="mt-2 h-8 w-20 animate-pulse rounded bg-white/10" />
          ) : (
            <p className="mt-2 text-3xl font-bold text-blue-400">
              {monitors?.toLocaleString() ?? "—"}
            </p>
          )}
        </div>
      </div>

      <div className="mt-12 h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
    </section>
  );
}