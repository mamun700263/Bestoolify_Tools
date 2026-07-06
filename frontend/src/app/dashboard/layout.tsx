"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import { isAuthenticated } from "@/lib/auth";
import { Menu, X } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { account, logout } = useAuthStore();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [checkedAuth, setCheckedAuth] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    } else {
      setCheckedAuth(true);
    }
  }, [router]);

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  const navItem = (href: string) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition ${
      pathname === href
        ? "bg-gray-100 text-gray-900"
        : "text-gray-700 hover:bg-gray-100"
    }`;

  if (!checkedAuth) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-gray-500">
        Loading...
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Mobile Top Bar */}
      <div className="fixed left-0 right-0 top-0 z-50 flex h-14 items-center justify-between border-b bg-white px-4 lg:hidden">
        <span className="font-semibold text-gray-800">Tav Tools</span>

        <button onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Sidebar (desktop) */}
      <aside className="hidden w-64 flex-col border-r bg-white lg:flex">
        <div className="border-b p-6">
          <h1 className="text-xl font-bold text-gray-800">Tav Tools</h1>
          <p className="mt-1 text-xs text-gray-400">{account?.email}</p>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          <Link href="/dashboard" className={navItem("/dashboard")}>
            📊 Overview
          </Link>

          <Link
            href="/dashboard/monitors"
            className={navItem("/dashboard/monitors")}
          >
            🔍 Monitors
          </Link>
        </nav>

        <div className="border-t p-4">
          <button
            onClick={handleLogout}
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-red-500 hover:bg-red-50"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Mobile Sidebar */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-black/40 lg:hidden">
          <div className="h-full w-64 bg-white p-4">
            <div className="border-b pb-4">
              <h1 className="text-lg font-bold text-gray-800">Tav Tools</h1>
              <p className="text-xs text-gray-400">{account?.email}</p>
            </div>

            <nav className="mt-4 space-y-1">
              <Link
                href="/dashboard"
                className={navItem("/dashboard")}
                onClick={() => setMobileOpen(false)}
              >
                📊 Overview
              </Link>

              <Link
                href="/dashboard/monitors"
                className={navItem("/dashboard/monitors")}
                onClick={() => setMobileOpen(false)}
              >
                🔍 Monitors
              </Link>
            </nav>

            <div className="mt-6 border-t pt-4">
              <button
                onClick={handleLogout}
                className="w-full rounded-lg px-3 py-2 text-left text-sm text-red-500 hover:bg-red-50"
              >
                Logout
              </button>
            </div>
          </div>

          <div
            className="flex-1"
            onClick={() => setMobileOpen(false)}
          />
        </div>
      )}

      {/* Main content */}
      <main className="flex-1 px-4 pb-8 pt-20 lg:p-8">
        {children}
      </main>
    </div>
  );
}