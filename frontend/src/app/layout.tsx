import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/navbar";
import AuthProvider from "@/components/authprovider/authprovider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const SITE_URL = "https://monitor.tavdev.com";
const SITE_NAME = "TavDev Monitor";
const SITE_DESCRIPTION =
  "TavDev Monitor tracks your API and website health around the clock. Choose check intervals from 1 to 10 minutes, review 24 hours of history, export your data, and stop free-tier hosts like Render or Heroku from putting your app to sleep.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} — API & Uptime Monitoring for Developers`,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  keywords: [
    "API monitoring",
    "uptime monitor",
    "keep free tier awake",
    "prevent render sleep",
    "prevent heroku sleep",
    "API health check",
    "website downtime alerts",
    "API response time tracking",
    "free uptime robot alternative",
  ],
  authors: [{ name: "TavDev" }],
  creator: "TavDev",
  publisher: "TavDev",
  icons: {
    icon: "/favicon.png",
  },
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    url: SITE_URL,
    siteName: SITE_NAME,
    title: `${SITE_NAME} — API & Uptime Monitoring for Developers`,
    description: SITE_DESCRIPTION,
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "TavDev Monitor — API and uptime monitoring for developers",
      },
    ],
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE_NAME} — API & Uptime Monitoring for Developers`,
    description: SITE_DESCRIPTION,
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <AuthProvider>
          <Navbar />
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}