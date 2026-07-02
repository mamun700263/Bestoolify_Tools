"use client";

import { useEffect, useState } from "react";
import API from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import Link from "next/link";

interface Monitor {
  id: string;
  name: string;
  url: string;
  interval_minutes: number;
  is_active: boolean;
}

export default function DashboardPage() {
  
  const { account } = useAuthStore();
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    
    const fetchMonitors = async () => {
      try {
        const res = await API.get(`/uptime/accounts/${account?.id}/monitors`);
        setMonitors(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (account?.id) fetchMonitors();

  }, [account]);

  const activeCount = monitors.filter((m) => m.is_active).length;
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Overview</h1>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Total Monitors</p>
          <p className="text-3xl font-bold text-gray-800 mt-1">{monitors.length}</p>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Active</p>
          <p className="text-3xl font-bold text-green-600 mt-1">{activeCount}</p>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Paused</p>
          <p className="text-3xl font-bold text-yellow-500 mt-1">
            {monitors.length - activeCount}
          </p>
        </div>
      </div>

      {/* Recent monitors */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-6 border-b flex justify-between items-center">
          <h2 className="font-semibold text-gray-800">Your Monitors</h2>
          <Link
            href="/dashboard/monitors"
            className="text-sm text-blue-600 hover:underline"
          >
            View all
          </Link>
        </div>

        {loading ? (
          <div className="p-6 text-sm text-gray-400">Loading...</div>
        ) : monitors.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-gray-400 text-sm">No monitors yet.</p>
            <Link
              href="/dashboard/monitors"
              className="text-blue-600 text-sm hover:underline mt-2 block"
            >
              Create your first monitor →
            </Link>
          </div>
        ) : (
          <ul className="divide-y">
            {monitors.slice(0, 5).map((m) => (
              <li key={m.id} className="px-6 py-4 flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-gray-800">{m.name}</p>
                  <p className="text-xs text-gray-400">{m.url}</p>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded-full font-medium ${
                    m.is_active
                      ? "bg-green-100 text-green-700"
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {m.is_active ? "Active" : "Paused"}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}