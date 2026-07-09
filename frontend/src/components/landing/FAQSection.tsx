export default function FAQSection() {
  const faqs = [
    {
      q: "What does TavDev Monitor do?",
      a: "It pings your website or API at an interval you choose — 1, 3, 5, or 10 minutes — and keeps a record of its health for the last 24 hours. You can export that data at any time.",
    },
    {
      q: "Can it stop my free hosting tier from sleeping?",
      a: "Yes. Many free plans, including Render, Railway, and Heroku, spin your app down after a period of inactivity. A TavDev monitor with a short interval sends regular requests to your app, which keeps it awake.",
    },
    {
      q: "Can I export my monitoring data?",
      a: "Yes. You can download your monitoring history, including response times and uptime records, for your own analysis or reporting.",
    },
    {
      q: "Is TavDev Monitor free?",
      a: "Yes. The free plan includes 10 monitors with no credit card required.",
    },
    {
      q: "How fast are alerts delivered?",
      a: "Alerts go out in under a second after a check fails, so you find out before your users do.",
    },
  ];

  return (
    <section className="relative z-10 max-w-6xl mx-auto px-8 pb-32">
      <h2 className="text-3xl font-black tracking-tight mb-12 text-zinc-200">
        Frequently asked questions.
      </h2>

      <div className="space-y-4">
        {faqs.map((item) => (
          <details
            key={item.q}
            className="group border border-zinc-800 rounded-xl bg-[#0d0d0d] px-6 py-4 open:border-zinc-600"
          >
            <summary className="flex items-center justify-between cursor-pointer list-none font-semibold text-white text-sm">
              {item.q}
              <span
                aria-hidden="true"
                className="text-zinc-500 group-open:rotate-45 transition-transform text-xl leading-none"
              >
                +
              </span>
            </summary>
            <p className="mt-3 text-sm text-zinc-500 leading-relaxed">
              {item.a}
            </p>
          </details>
        ))}
      </div>
    </section>
  );
}