import Link from "next/link";
import HeroSection from "@/components/landing/HeroSection";
import StateSection from "@/components/landing/StatsSection";
import FeatureSection from "@/components/landing/FeaturesSection";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/landing/Footer";
import SystemPulseSection from "@/components/landing/dynamic_user_info";

export default function LandingPage() {
  return (
    
    <main className="min-h-screen bg-[#080808] text-white overflow-hidden">
      {/* Grid background */}
      <div
        className="fixed inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)`,
          backgroundSize: "64px 64px",
        }}
      />

      {/* Glow */}
      <div className="fixed top-[-20%] left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-emerald-500 opacity-[0.06] blur-[120px] pointer-events-none" />

      {/* Hero */}
      <HeroSection></HeroSection>

      {/* Stats */}
      <StateSection></StateSection>

      {/* Features */}
      <FeatureSection></FeatureSection>
      <SystemPulseSection />
      {/* CTA */}
      <CTASection></CTASection>

      {/* Footer */}
      <Footer></Footer>
    </main>
  );
}