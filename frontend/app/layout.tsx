import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GotchAI - Financial X-Ray Vision",
  description: "Don't sign blind. GotchAI exposes hidden fees, predatory clauses, and privacy traps in any contract instantly. Powered by AI.",
  keywords: ["contract review", "legal ai", "hidden fees", "consumer rights", "lease audit", "fine print"],
  openGraph: {
    title: "GotchAI - Financial X-Ray Vision",
    description: "Instant AI auditing for contracts. Find the traps before you sign.",
    url: "https://gotchai.vercel.app",
    siteName: "GotchAI",
    images: [
      {
        url: "/opengraph-image.png",
        width: 1200,
        height: 630,
      },
    ],
    locale: "en_US",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        suppressHydrationWarning={true}
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-950 text-slate-100`}
      >
        {children}
      </body>
    </html>
  );
}
