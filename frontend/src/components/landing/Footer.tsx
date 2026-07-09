import Link from "next/link";

export default function Footer() {
  return (
    <footer className="relative z-10 max-w-6xl mx-auto px-8 pb-8 pt-8 border-t border-zinc-800">
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
        <span className="text-xs font-mono text-zinc-600 uppercase tracking-widest">
          TavDev Monitor
        </span>

        <nav aria-label="Footer navigation" className="flex gap-6 text-xs text-zinc-500">
          <Link href="/register" className="hover:text-white transition-colors">
            Sign up
          </Link>
          <Link href="/login" className="hover:text-white transition-colors">
            Log in
          </Link>
          <Link href="/test" className="hover:text-white transition-colors">
            Try the API
          </Link>
        </nav>

        <span className="text-xs text-zinc-600 text-center">
          Built for developers who care about reliability.
        </span>
      </div>
    </footer>
  );
}