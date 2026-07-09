import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/", "/dashboard/", "/settings/"],
    },
    sitemap: "https://monitor.tavdev.com/sitemap.xml",
  };
}