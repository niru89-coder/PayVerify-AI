import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
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
  title: "PayVerify AI",
  description: "AI-assisted Malaysia payroll validation - Client vs Platform vs Rule Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900">
        <header className="border-b border-slate-200 bg-white">
          <nav className="mx-auto max-w-6xl flex items-center gap-6 px-6 py-4">
            <Link href="/" className="font-semibold text-lg text-slate-900">
              PayVerify <span className="text-indigo-600">AI</span>
            </Link>
            <Link href="/" className="text-sm text-slate-600 hover:text-slate-900">
              Projects
            </Link>
            <Link href="/rules" className="text-sm text-slate-600 hover:text-slate-900">
              Rule Catalog
            </Link>
          </nav>
        </header>
        <main className="flex-1 mx-auto w-full max-w-6xl px-6 py-8">{children}</main>
        <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-400">
          PayVerify AI - Malaysia MVP. Statutory validation is 100% deterministic; AI only explains results.
        </footer>
      </body>
    </html>
  );
}

