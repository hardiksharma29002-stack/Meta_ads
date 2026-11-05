"use client";

import { Download, FileSpreadsheet, ShieldCheck, Clock, FileText, ShoppingBag, Sparkles } from "lucide-react";

export default function ExportsPage() {
  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Curated Meta Ad Intelligence Dossiers</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <Download className="w-6 h-6 text-indigo-600" />
            <span>Export Center</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Download your prospect lists in Excel (.xlsx) and PDF (.pdf) formats with verified business contacts and executive leadership profiles.
          </p>
        </div>
      </div>

      {/* Featured Downloads: Jaipur Corporate Spenders & Shopify D2C Ecosystem */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Excel Dossier Card */}
        <div className="bg-white border border-emerald-200 rounded-2xl p-5 shadow-xs space-y-4 hover:shadow-md transition">
          <div className="flex items-start justify-between">
            <div className="p-3 bg-emerald-50 rounded-xl text-emerald-700">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800">
              3 Sheets Included
            </span>
          </div>
          <div>
            <h2 className="font-extrabold text-slate-900 text-base">
              Jaipur Top Meta Advertisers & Shopify Stores (.xlsx)
            </h2>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Complete workbook featuring 35 corporate powerhouse spenders, 60 Shopify D2C stores with Founder/CEO names and direct LinkedIn links, plus domain ad spend distribution.
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] text-slate-500 font-medium">Size: ~45 KB • Format: Excel</span>
            <a
              href="/exports/Jaipur_Top_Meta_Advertisers.xlsx"
              download
              className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs transition inline-flex items-center gap-1.5 shadow-2xs"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Excel</span>
            </a>
          </div>
        </div>

        {/* PDF Executive Dossier Card */}
        <div className="bg-white border border-rose-200 rounded-2xl p-5 shadow-xs space-y-4 hover:shadow-md transition">
          <div className="flex items-start justify-between">
            <div className="p-3 bg-rose-50 rounded-xl text-rose-700">
              <FileText className="w-6 h-6" />
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800">
              Executive Dossier
            </span>
          </div>
          <div>
            <h2 className="font-extrabold text-slate-900 text-base">
              Jaipur Ad Spend & CXO Intelligence Report (.pdf)
            </h2>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Print-ready executive briefing covering top corporate spenders, domain market share analysis, and full registry of 60 Jaipur Shopify brands with clickable LinkedIn links.
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] text-slate-500 font-medium">Format: Landscape A4 PDF</span>
            <a
              href="/exports/Jaipur_Top_Meta_Advertisers.pdf"
              download
              className="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold text-xs transition inline-flex items-center gap-1.5 shadow-2xs"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF</span>
            </a>
          </div>
        </div>
      </div>

      <div className="p-4 bg-slate-100 rounded-2xl text-xs text-slate-600 flex items-center gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <span>
          <strong>Export Compliance Notice:</strong> All business contacts are verified public corporate channels. Compliant with Digital Personal Data Protection (DPDP) Act 2023 & TRAI business guidelines.
        </span>
      </div>
    </div>
  );
}
