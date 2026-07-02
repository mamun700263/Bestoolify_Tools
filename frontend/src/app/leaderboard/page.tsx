export default function LeaderboardPage() {
  const data = [
    { url: "https://google.com", score: 120 },
    { url: "https://github.com", score: 180 },
    { url: "https:/API.tavdev.com", score: 95 },
  ].sort((a, b) => a.score - b.score);

  const getColor = (score: number) => {
    if (score < 150) return "text-emerald-400";
    if (score < 300) return "text-yellow-400";
    return "text-red-400";
  };

  const getBadge = (idx: number) => {
    if (idx === 0) return "🥇";
    if (idx === 1) return "🥈";
    if (idx === 2) return "🥉";
    return `#${idx + 1}`;
  };

  return (
    <main className="min-h-screen bg-[#080808] text-white px-8 py-16">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <div className="inline-flex items-center gap-2 border border-zinc-800 rounded-full px-4 py-1.5 mb-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-zinc-400 font-mono">
              Live performance ranking
            </span>
          </div>

          <h1 className="text-5xl font-black tracking-tight mb-3">
            API Leaderboard
          </h1>

          <p className="text-zinc-400 max-w-xl">
            Ranked by response latency. Lower is faster.
          </p>
        </div>

        {/* Table */}
        <div className="space-y-3">
          {data.map((item, idx) => (
            <div
              key={item.url}
              className="flex items-center justify-between p-5 rounded-xl border border-zinc-800 bg-[#111] hover:border-zinc-700 transition"
            >
              {/* Left */}
              <div className="flex items-center gap-4">
                <span className="text-lg w-10 text-center">
                  {getBadge(idx)}
                </span>

                <div>
                  <p className="text-zinc-200 font-medium">
                    {item.url}
                  </p>
                  <p className="text-xs text-zinc-500">
                    Endpoint health ranking
                  </p>
                </div>
              </div>

              {/* Right */}
              <div className="text-right">
                <p className={`text-2xl font-bold ${getColor(item.score)}`}>
                  {item.score}ms
                </p>
                <p className="text-xs text-zinc-500">
                  response time
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Footer hint */}
        <div className="mt-10 text-xs text-zinc-600">
          Updated in real-time based on active monitoring data
        </div>
      </div>
    </main>
  );
}