export default function FeatureSection() {
  const features = [
    {
      icon: "⏱️",
      title: "Choose your check interval",
      desc: "Ping every 1, 3, 5, or 10 minutes. Tighter intervals for critical APIs, longer ones to conserve your quota.",
    },
    {
      icon: "📈",
      title: "24-hour history, always on",
      desc: "Every check is logged. Review the last day of uptime and response times whenever you need to.",
    },
    {
      icon: "⬇️",
      title: "Export your data",
      desc: "Download your monitoring history for reporting, audits, or your own analysis. Your data isn't locked in.",
    },
    {
      icon: "🌙",
      title: "Keep free-tier apps awake",
      desc: "Regular pings prevent Render, Railway, and Heroku free plans from spinning down due to inactivity.",
    },
    {
      icon: "⚡",
      title: "Instant alerts",
      desc: "Get notified the moment a check fails, so you hear about downtime before your users do.",
    },
    {
      icon: "🔒",
      title: "Secure by default",
      desc: "Email verification, JWT auth, and rate limiting are built in from day one.",
    },
  ];

  return (
    <section className="relative z-10 max-w-6xl mx-auto px-8 pb-32">
      <h2 className="text-3xl font-black tracking-tight mb-12 text-zinc-200">
        Everything you need to
        <br />
        stay ahead of downtime.
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {features.map((f) => (
          <div
            key={f.title}
            className="border border-zinc-800 rounded-xl p-6 bg-[#0d0d0d] hover:border-zinc-600 transition-colors"
          >
            <span aria-hidden="true" className="text-2xl mb-4 block">
              {f.icon}
            </span>
            <h3 className="font-bold text-white mb-2">{f.title}</h3>
            <p className="text-sm text-zinc-500 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}