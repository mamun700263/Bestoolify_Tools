import Link from "next/link";

export default function CTASection() {
  return (
    <section className="relative z-10 max-w-6xl mx-auto px-8 pb-32">
      <div className="border border-zinc-800 rounded-2xl p-12 text-center bg-[#0d0d0d] relative overflow-hidden">
        <div
          aria-hidden="true"
          className="absolute inset-0 bg-gradient-to-b from-emerald-500/5 to-transparent"
        />

        <h2 className="text-4xl font-black tracking-tight mb-4 relative z-10">
          Start monitoring in 60 seconds.
        </h2>

        <p className="text-zinc-400 mb-8 relative z-10">
          10 free monitors, 1-minute check intervals, no credit card
          required.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 relative z-10">
          <Link
            href="/register"
            className="bg-white text-black px-8 py-3 rounded-md font-semibold text-sm hover:bg-zinc-200 transition-colors"
          >
            Create free account →
          </Link>

          <Link
            href="/test"
            className="border border-zinc-700 text-white px-6 py-3 rounded-md font-semibold text-sm hover:border-zinc-500 transition-colors"
          >
            Try API instantly →
          </Link>
        </div>
      </div>
    </section>
  );
}