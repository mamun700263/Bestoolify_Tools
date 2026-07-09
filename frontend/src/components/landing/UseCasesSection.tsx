export default function UseCasesSection() {
  const useCases = [
    {
      title: "Building an API",
      desc: "Track how your endpoints behave over time. Catch latency creep and outages before your users file a ticket.",
    },
    {
      title: "Running production traffic",
      desc: "Get a clear, exportable record of response times and incidents — useful for post-mortems, SLAs, and status pages.",
    },
    {
      title: "On a free hosting tier",
      desc: "Render, Railway, and Heroku free plans spin down when idle. Set a short check interval and TavDev keeps your app warm automatically.",
    },
  ];

  return (
    <section className="relative z-10 max-w-6xl mx-auto px-8 pb-32">
      <h2 className="text-3xl font-black tracking-tight mb-2 text-zinc-200">
        Built for how you actually work.
      </h2>
      <p className="text-zinc-500 mb-12 max-w-2xl">
        Whether you're shipping an API, keeping production honest, or just
        trying to stop your free-tier app from falling asleep — TavDev fits.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {useCases.map((u) => (
          <div
            key={u.title}
            className="border border-zinc-800 rounded-xl p-6 bg-[#0d0d0d]"
          >
            <h3 className="font-bold text-white mb-2">{u.title}</h3>
            <p className="text-sm text-zinc-500 leading-relaxed">{u.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}