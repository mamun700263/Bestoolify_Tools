"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";

export default function Navbar() {
  const pathname = usePathname();

  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsAuthenticated(!!token);
  }, [pathname]);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const navLink = (href: string) =>
    `transition-colors ${
      pathname === href
        ? "text-white"
        : "text-zinc-500 hover:text-white"
    }`;

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-900 bg-[#080808]/80 backdrop-blur-xl">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          <img
            src="/favicon.png"
            alt="TavDev"
            className="h-10 w-10 object-contain"
          />
          <span className="font-bold tracking-tight text-white">
            TavDev Monitor
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden items-center gap-8 lg:flex">
          <Link href="/test" className={navLink("/test")}>
            Test API
          </Link>

          <Link
            href="/leaderboard"
            className={navLink("/leaderboard")}
          >
            Leaderboard
          </Link>

          {isAuthenticated && (
            <Link
              href="/dashboard"
              className={navLink("/dashboard")}
            >
              Dashboard
            </Link>
          )}
        </div>

        {/* Desktop CTA */}
        <div className="hidden min-w-[140px] items-center justify-end gap-3 lg:flex">
          {isAuthenticated === null ? (
            <div className="h-9 w-20" />
          ) : isAuthenticated ? null : (
            <>
              <Link
                href="/login"
                className="text-sm text-zinc-500 hover:text-white"
              >
                Login
              </Link>

              <Link
                href="/register"
                className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black hover:bg-zinc-200"
              >
                Get Started
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="text-white lg:hidden"
        >
          {mobileOpen ? <X size={26} /> : <Menu size={26} />}
        </button>
      </nav>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="border-t border-zinc-900 bg-[#080808] lg:hidden">
          <div className="flex flex-col space-y-4 px-6 py-6">
            <Link href="/test" className={navLink("/test")}>
              Test API
            </Link>

            <Link
              href="/leaderboard"
              className={navLink("/leaderboard")}
            >
              Leaderboard
            </Link>

            {isAuthenticated && (
              <Link
                href="/dashboard"
                className={navLink("/dashboard")}
              >
                Dashboard
              </Link>
            )}

            {isAuthenticated === false && (
              <>
                <Link href="/login" className={navLink("/login")}>
                  Login
                </Link>

                <Link
                  href="/register"
                  className="rounded-lg bg-white px-4 py-2 text-center font-semibold text-black"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}