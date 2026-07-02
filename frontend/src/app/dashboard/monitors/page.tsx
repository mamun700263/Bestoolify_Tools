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

const defaultForm = { name: "", url: "", interval_minutes: 5 };

export default function MonitorsPage() {
  const { account } = useAuthStore();
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(defaultForm);
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");

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

  useEffect(() => {
    if (account?.id) fetchMonitors();
  }, [account]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setCreating(true);
    try {
      await API.post("/uptime/monitors", {
        ...form,
        account_id: account?.id,
      });
      setForm(defaultForm);
      setShowForm(false);
      await fetchMonitors();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create monitor");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this monitor?")) return;
    try {
      await API.delete(`/uptime/monitors/${id}`);
      setMonitors((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggle = async (monitor: Monitor) => {
    try {
      await API.patch(`/uptime/monitors/${monitor.id}`, {
        is_active: !monitor.is_active,
      });
      await fetchMonitors();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Monitors</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "+ New Monitor"}
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <h2 className="font-semibold text-gray-800 mb-4">New Monitor</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="My API"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <input
                  type="url"
                  required
                  value={form.url}
                  onChange={(e) => setForm({ ...form, url: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Check interval
              </label>
              <select
                value={form.interval_minutes}
                onChange={(e) =>
                  setForm({ ...form, interval_minutes: parseInt(e.target.value) })
                }
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>Every 1 minute</option>
                <option value={3}>Every 3 minutes</option>
                <option value={5}>Every 5 minutes</option>
                <option value={10}>Every 10 minutes</option>
              </select>
            </div>

            {error && <p className="text-red-500 text-sm">{error}</p>}

            <button
              type="submit"
              disabled={creating}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {creating ? "Creating..." : "Create Monitor"}
            </button>
          </form>
        </div>
      )}

      {/* Monitors list */}
      <div className="bg-white rounded-xl shadow-sm border">
        {loading ? (
          <div className="p-6 text-sm text-gray-400">Loading...</div>
        ) : monitors.length === 0 ? (
          <div className="p-6 text-center text-gray-400 text-sm">
            No monitors yet. Create your first one above.
          </div>
        ) : (
          <ul className="divide-y">
            {monitors.map((m) => (
              <li key={m.id} className="px-6 py-4 flex justify-between items-center">
                <div>
                  <Link
                    href={`/dashboard/monitors/${m.id}`}
                    className="text-sm font-medium text-gray-800 hover:text-blue-600"
                  >
                    {m.name}
                  </Link>
                  <p className="text-xs text-gray-400">{m.url}</p>
                  <p className="text-xs text-gray-400">Every {m.interval_minutes} min</p>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`text-xs px-2 py-1 rounded-full font-medium ${
                      m.is_active
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {m.is_active ? "Active" : "Paused"}
                  </span>
                  <button
                    onClick={() => handleToggle(m)}
                    className="text-xs text-gray-500 hover:text-blue-600"
                  >
                    {m.is_active ? "Pause" : "Resume"}
                  </button>
                  <button
                    onClick={() => handleDelete(m.id)}
                    className="text-xs text-red-400 hover:text-red-600"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}