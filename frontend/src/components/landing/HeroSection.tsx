import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="relative z-10 max-w-6xl mx-auto px-8 pt-24 pb-32">
      {/* Badge */}
      <div className="inline-flex items-center gap-2 border border-zinc-800 rounded-full px-4 py-1.5 mb-8">
        <span
          aria-hidden="true"
          className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"
        />
        <span className="text-xs text-zinc-400 font-mono">
          Checks every 1, 3, 5, or 10 minutes
        </span>
      </div>

      <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-none mb-6">
        Know your API
        <br />
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
          never sleeps
        </span>
        <br />
        on your watch.
      </h1>

      <p className="text-zinc-400 text-lg max-w-xl mb-4 leading-relaxed">
        TavDev Monitor is your uptime and API health tracker. Pick a check
        interval, get instant alerts when something breaks, and keep 24
        hours of history you can export anytime.
      </p>

      <p className="text-zinc-500 text-sm max-w-xl mb-10 leading-relaxed">
        Built for developers shipping APIs, teams who need to trust their
        response times, and anyone on a free hosting tier tired of cold
        starts.
      </p>

      <div className="flex flex-wrap items-center gap-4">
        <Link
          href="/register"
          className="bg-white text-black px-6 py-3 rounded-md font-semibold text-sm hover:bg-zinc-200 transition-colors"
        >
          Start monitoring free →
        </Link>
        <Link
          href="/login"
          className="text-zinc-400 text-sm hover:text-white transition-colors"
        >
          Already have an account?
        </Link>
      </div>
    </section>
  );
}