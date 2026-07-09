import HeroSection from "@/components/landing/HeroSection";
import StatsSection from "@/components/landing/StatsSection";
import UseCasesSection from "@/components/landing/UseCasesSection";
import FeatureSection from "@/components/landing/FeaturesSection";
import FAQSection from "@/components/landing/FAQSection";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/landing/Footer";
import SystemPulseSection from "@/components/landing/dynamic_user_info";

const softwareJsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "TavDev Monitor",
  applicationCategory: "DeveloperApplication",
  operatingSystem: "Web",
  description:
    "API and uptime monitoring with configurable check intervals, 24-hour history, and exportable data.",
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "USD",
    description: "Free plan with 10 monitors",
  },
  url: "https://monitor.tavdev.com",
};

const faqJsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "What does TavDev Monitor do?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "TavDev Monitor pings your website or API at an interval you choose — 1, 3, 5, or 10 minutes — and keeps a record of its health for the last 24 hours. You can export that data at any time.",
      },
    },
    {
      "@type": "Question",
      name: "Can TavDev Monitor stop my free hosting tier from sleeping?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. Many free hosting plans, including Render, Railway, and Heroku, spin your app down after a period of inactivity. Setting up a TavDev monitor with a short check interval sends regular requests to your app, which keeps it awake.",
      },
    },
    {
      "@type": "Question",
      name: "Can I export my monitoring data?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. TavDev Monitor lets you download your monitoring history, including response times and uptime records, for your own analysis or reporting.",
      },
    },
    {
      "@type": "Question",
      name: "Is TavDev Monitor free?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. The free plan includes 10 monitors with no credit card required.",
      },
    },
    {
      "@type": "Question",
      name: "How fast are alerts delivered?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Alerts are delivered in under a second after a check fails.",
      },
    },
  ],
};

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#080808] text-white overflow-hidden">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(softwareJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />

      <div
        aria-hidden="true"
        className="fixed inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)`,
          backgroundSize: "64px 64px",
        }}
      />

      <div
        aria-hidden="true"
        className="fixed top-[-20%] left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-emerald-500 opacity-[0.06] blur-[120px] pointer-events-none"
      />

      <HeroSection />
      <StatsSection />
      <UseCasesSection />
      <FeatureSection />
      <SystemPulseSection />
      <FAQSection />
      <CTASection />
      <Footer />
    </main>
  );
}