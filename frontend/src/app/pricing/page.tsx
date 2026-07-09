"use client";

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gray-50 px-6 py-16">
      <div className="mx-auto max-w-4xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900">
            Pricing
          </h1>

          <p className="mt-4 text-gray-600">
            Simple uptime monitoring for your websites and services.
          </p>
        </div>

        <div className="mx-auto mt-10 max-w-md rounded-2xl border bg-white p-8 shadow-sm">
          <h2 className="text-center text-xl font-semibold text-gray-800">
            Early Access
          </h2>

          <div className="mt-6 text-center">
            <span className="text-5xl font-bold text-gray-900">
              Free
            </span>

            <p className="mt-2 text-sm text-gray-500">
              Beta access
            </p>
          </div>

          <div className="mt-8 space-y-4 text-sm text-gray-700">
            <div className="flex items-center gap-3">
              <span className="text-green-500">✓</span>
              <span>Up to 10 uptime monitors</span>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-green-500">✓</span>
              <span>Automatic uptime checks</span>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-green-500">✓</span>
              <span>Response time tracking</span>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-green-500">✓</span>
              <span>Monitoring history export</span>
            </div>
          </div>

          <div className="mt-8 rounded-lg bg-gray-100 p-4 text-center">
            <p className="text-sm text-gray-600">
              Premium plans are currently under development.
            </p>

            <p className="mt-2 text-sm text-gray-600">
              Need more than 10 uptime monitors?
            </p>

            <a
              href="mailto:mamun700263@gmail.com"
              className="mt-3 inline-block font-medium text-blue-600 hover:text-blue-700"
            >
              Contact us
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}