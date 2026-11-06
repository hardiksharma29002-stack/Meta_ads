import "./globals.css";
import Link from "next/link";
import { Compass, ShieldAlert } from "lucide-react";

export const metadata = {
  title: "AdAtlas India — Meta Advertisers & Business Contacts",
  description: "Browse Meta advertisers across Indian cities with direct verified business contact numbers, emails, and WhatsApp.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 antialiased font-sans">
        {/* Simple & Clean Navigation Bar */}
        <header className="border-b border-slate-200 bg-white sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2.5 font-bold text-xl text-slate-900 hover:text-indigo-600 transition">
              <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-xs">
                <Compass className="w-5 h-5" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5 leading-none">
                  <span className="tracking-tight text-lg">AdAtlas</span>
                  <span className="text-[11px] bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded font-semibold">India</span>
                </div>
                <span className="text-[11px] text-slate-600 font-normal mt-0.5">Meta Advertisers & Public Business Contacts</span>
              </div>
            </Link>

            <div className="flex items-center gap-4 text-xs font-medium text-slate-500">
              <Link href="/optout" className="flex items-center gap-1 hover:text-slate-900 transition text-slate-600">
                <ShieldAlert className="w-3.5 h-3.5 text-emerald-600" />
                <span>Business Opt-Out</span>
              </Link>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6">{children}</main>

        {/* Minimal Footer */}
        <footer className="border-t border-slate-200 bg-white py-6 mt-16 text-center text-xs text-slate-600">
          <p>© 2026 AdAtlas India — Public B2B Contact Directory for Mumbai, Delhi, Jaipur, Kolkata, and Bengaluru.</p>
        </footer>
      </body>
    </html>
  );
}
