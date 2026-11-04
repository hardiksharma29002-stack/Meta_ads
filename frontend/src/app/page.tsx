"use client";

import { useState } from "react";
import { 
  Phone, Mail, MessageSquare, Globe, MapPin, 
  ExternalLink, Search, Sparkles, TrendingUp, 
  BarChart3, Table, LayoutGrid, CheckCircle2, Flame, Building2, Download
} from "lucide-react";
import { ALL_COMPANIES, getJaipurDomainBreakdown, Company, DomainSummary } from "@/data/advertisers";

const CITIES = [
  { slug: "jaipur", name: "Jaipur", count: 35, highlight: true },
  { slug: "all", name: "All Metros", count: 41 },
  { slug: "delhi", name: "Delhi NCT", count: 5 },
  { slug: "mumbai", name: "Mumbai", count: 5 },
  { slug: "bengaluru", name: "Bengaluru", count: 5 },
  { slug: "kolkata", name: "Kolkata", count: 5 },
];

export default function HighAdDirectoryPage() {
  const [selectedCity, setSelectedCity] = useState("jaipur");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"leaderboard" | "domain_table" | "cards">("leaderboard");
  const [domainFilter, setDomainFilter] = useState<string>("all");

  const domainSummaries: DomainSummary[] = getJaipurDomainBreakdown();

  // Filtered and sorted strictly from highest ads to lowest ads
  const filtered = ALL_COMPANIES.filter((item) => {
    // City filter
    if (selectedCity !== "all" && item.city !== selectedCity) {
      return false;
    }
    // Domain filter
    if (domainFilter !== "all" && item.domain_group !== domainFilter) {
      return false;
    }
    // Search text filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      const matchName = item.name.toLowerCase().includes(q);
      const matchCat = item.category.toLowerCase().includes(q);
      const matchDomain = item.domain_group.toLowerCase().includes(q);
      const matchLoc = item.locality.toLowerCase().includes(q);
      if (!matchName && !matchCat && !matchDomain && !matchLoc) return false;
    }
    return true;
  }).sort((a, b) => b.active_ads - a.active_ads); // Highest ads first

  const totalFilteredAds = filtered.reduce((acc, curr) => acc + curr.active_ads, 0);

  return (
    <div className="space-y-6 py-2">
      {/* Top Banner: Jaipur 34K Ad Intelligence */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-sm relative overflow-hidden">
        <div className="relative z-10 space-y-3 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-amber-400 text-slate-950">
            <Flame className="w-3.5 h-3.5 fill-current" />
            <span>Jaipur Meta Ad Intelligence — 34,200+ Active Ads Discovered</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Top Advertisers Ranked by Active Ads & Spend Intensity
          </h1>
          <p className="text-indigo-200 text-sm leading-relaxed">
            Directly see which companies are spending the most on Facebook & Instagram in Jaipur. Ranked from highest ad volume to lowest with direct phone, WhatsApp, email, and websites.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
            <div className="bg-white/10 backdrop-blur-xs p-3 rounded-xl border border-white/10">
              <span className="text-indigo-200 block">Total Jaipur Ads</span>
              <strong className="text-lg font-black text-white">34,200+</strong>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-3 rounded-xl border border-white/10">
              <span className="text-indigo-200 block">Top Spender Ad Count</span>
              <strong className="text-lg font-black text-amber-300">240 Ads</strong>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-3 rounded-xl border border-white/10">
              <span className="text-indigo-200 block">Top Spending Domain</span>
              <strong className="text-lg font-black text-white">Education (32%)</strong>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-3 rounded-xl border border-white/10">
              <span className="text-indigo-200 block">2nd Top Domain</span>
              <strong className="text-lg font-black text-white">Jewellery (26%)</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Export Download Bar (Excel & PDF for Jaipur) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs text-xs">
        <div className="flex items-center gap-2">
          <span className="font-extrabold text-slate-900">📥 Export Jaipur Data:</span>
          <span className="text-slate-500 hidden sm:inline">Download full list with verified phone, WhatsApp & emails for prospecting</span>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="/exports/Jaipur_Top_Meta_Advertisers.xlsx"
            download
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 text-white font-bold hover:bg-emerald-700 transition shadow-2xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Excel (.xlsx)</span>
          </a>
          <a
            href="/exports/Jaipur_Top_Meta_Advertisers.pdf"
            download
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-600 text-white font-bold hover:bg-rose-700 transition shadow-2xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download PDF (.pdf)</span>
          </a>
        </div>
      </div>

      {/* City Switcher & Navigation Controls */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        {/* City Filter Pills */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 mr-1">City:</span>
            {CITIES.map((c) => {
              const isActive = selectedCity === c.slug;
              return (
                <button
                  key={c.slug}
                  onClick={() => {
                    setSelectedCity(c.slug);
                    setDomainFilter("all");
                  }}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-xs"
                      : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                  }`}
                >
                  <span>{c.name}</span>
                  <span
                    className={`text-[11px] px-1.5 py-0.2 rounded-full ${
                      isActive ? "bg-indigo-700 text-indigo-100" : "bg-white text-slate-500 border border-slate-200"
                    }`}
                  >
                    {c.count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* View Mode Switcher (Table vs Domain Table vs Cards) */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-bold">
            <button
              onClick={() => setActiveTab("leaderboard")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition cursor-pointer ${
                activeTab === "leaderboard"
                  ? "bg-white text-indigo-700 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Table className="w-3.5 h-3.5" />
              <span>Company Leaderboard</span>
            </button>
            <button
              onClick={() => setActiveTab("domain_table")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition cursor-pointer ${
                activeTab === "domain_table"
                  ? "bg-white text-indigo-700 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Domain Spend Breakdown</span>
            </button>
            <button
              onClick={() => setActiveTab("cards")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition cursor-pointer ${
                activeTab === "cards"
                  ? "bg-white text-indigo-700 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              <span>Contact Cards</span>
            </button>
          </div>
        </div>

        {/* Filter by Domain & Search Bar */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2 border-t border-slate-100">
          {/* Quick Domain Filter Dropdown */}
          <div className="sm:w-64">
            <select
              value={domainFilter}
              onChange={(e) => setDomainFilter(e.target.value)}
              aria-label="Filter by Domain"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="all">All Domains / Industries</option>
              <option value="Education & Coaching">Education & Coaching (Highest Ads)</option>
              <option value="Jewellery & Gems">Jewellery & Luxury Gems</option>
              <option value="Real Estate & Builders">Real Estate & Builders</option>
              <option value="Healthcare & Hospitals">Healthcare & Hospitals</option>
              <option value="Fashion & Sarees">Fashion & Traditional Sarees</option>
              <option value="Hospitality & Sweets">Hospitality & Sweets</option>
              <option value="Tech & E-Commerce">Tech & E-Commerce (HQ)</option>
            </select>
          </div>

          {/* Search Box */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search company name, locality (Tonk Road, MI Road, Gopalpura...), or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Export Download Bar (Excel & PDF for Jaipur) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs text-xs">
        <div className="flex items-center gap-2">
          <span className="font-extrabold text-slate-900">📥 Export Jaipur Data:</span>
          <span className="text-slate-500 hidden sm:inline">Download full list with verified phone, WhatsApp & emails for prospecting</span>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="/exports/Jaipur_Top_Meta_Advertisers.xlsx"
            download
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 text-white font-bold hover:bg-emerald-700 transition shadow-2xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Excel (.xlsx)</span>
          </a>
          <a
            href="/exports/Jaipur_Top_Meta_Advertisers.pdf"
            download
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-600 text-white font-bold hover:bg-rose-700 transition shadow-2xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download PDF (.pdf)</span>
          </a>
        </div>
      </div>

      {/* Active Count & Metric Bar */}
      <div className="flex items-center justify-between text-xs text-slate-500 px-1">
        <span>
          Showing <strong className="text-slate-900">{filtered.length} companies</strong> accounting for{" "}
          <strong className="text-indigo-700 font-bold">{totalFilteredAds} Active Meta Ads</strong> in{" "}
          <span className="capitalize font-bold text-slate-800">{selectedCity}</span>
        </span>
        <span className="text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
          Ranked Highest to Lowest Active Ads
        </span>
      </div>

      {/* =====================================================================
          TAB 1: COMPANY AD SPEND LEADERBOARD TABLE (Requested by User)
         ===================================================================== */}
      {activeTab === "leaderboard" && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                  <th className="py-3.5 px-4 w-12 text-center">Rank</th>
                  <th className="py-3.5 px-4">Company Name & Locality</th>
                  <th className="py-3.5 px-4">Domain / Industry</th>
                  <th className="py-3.5 px-4 text-center">Active Ads (High-to-Low)</th>
                  <th className="py-3.5 px-4 text-center">Spend Intensity</th>
                  <th className="py-3.5 px-4">Direct Phone / Call</th>
                  <th className="py-3.5 px-4">WhatsApp Direct</th>
                  <th className="py-3.5 px-4 text-right">Website</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filtered.map((co, index) => {
                  const maxAds = filtered[0]?.active_ads || 240;
                  const barWidthPercent = Math.round((co.active_ads / maxAds) * 100);

                  return (
                    <tr key={co.id} className="hover:bg-indigo-50/40 transition group">
                      {/* Rank */}
                      <td className="py-3.5 px-4 text-center font-extrabold text-slate-700">
                        <span className={`inline-flex items-center justify-center w-7 h-7 rounded-lg text-xs font-black ${
                          index === 0
                            ? "bg-amber-100 text-amber-900 border border-amber-300"
                            : index === 1
                            ? "bg-slate-200 text-slate-800"
                            : index === 2
                            ? "bg-amber-50 text-amber-800 border border-amber-200"
                            : "bg-slate-100 text-slate-600"
                        }`}>
                          #{index + 1}
                        </span>
                      </td>

                      {/* Company Name & Locality */}
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-slate-900 text-sm group-hover:text-indigo-600 transition">
                          {co.name}
                        </div>
                        <div className="flex items-center gap-1.5 text-slate-500 text-[11px] mt-0.5">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          <span>{co.locality}, {co.city_name}</span>
                        </div>
                      </td>

                      {/* Domain / Industry */}
                      <td className="py-3.5 px-4">
                        <span className="inline-block px-2.5 py-1 rounded-md text-[11px] font-semibold bg-slate-100 text-slate-700">
                          {co.domain_group}
                        </span>
                      </td>

                      {/* Active Ads (Bar Visualizer) */}
                      <td className="py-3.5 px-4 text-center min-w-[140px]">
                        <div className="flex items-center justify-center gap-1.5 font-black text-slate-900">
                          <Flame className="w-3.5 h-3.5 text-amber-500 fill-current" />
                          <span>{co.active_ads} Ads</span>
                        </div>
                        <div className="w-full bg-slate-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                          <div
                            className="bg-indigo-600 h-full rounded-full"
                            style={{ width: `${barWidthPercent}%` }}
                          />
                        </div>
                      </td>

                      {/* Spend Intensity Tier */}
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-md text-[11px] font-bold border ${
                            co.spend_tier === "Very High"
                              ? "bg-rose-50 text-rose-700 border-rose-200"
                              : co.spend_tier === "High"
                              ? "bg-amber-50 text-amber-700 border-amber-200"
                              : "bg-emerald-50 text-emerald-700 border-emerald-200"
                          }`}
                        >
                          {co.spend_tier}
                        </span>
                      </td>

                      {/* Phone */}
                      <td className="py-3.5 px-4">
                        <a
                          href={`tel:${co.phone.replace(/[\s-]/g, "")}`}
                          className="font-bold text-slate-900 hover:text-indigo-600 transition inline-flex items-center gap-1"
                        >
                          <Phone className="w-3 h-3 text-indigo-600" />
                          <span>{co.phone}</span>
                        </a>
                      </td>

                      {/* WhatsApp */}
                      <td className="py-3.5 px-4">
                        <a
                          href={`https://wa.me/${co.whatsapp.replace(/[^0-9]/g, "")}`}
                          target="_blank"
                          rel="noreferrer"
                          className="font-bold text-emerald-700 hover:text-emerald-800 transition inline-flex items-center gap-1 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200"
                        >
                          <MessageSquare className="w-3 h-3" />
                          <span>{co.whatsapp}</span>
                        </a>
                      </td>

                      {/* Website */}
                      <td className="py-3.5 px-4 text-right">
                        <a
                          href={co.website}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-indigo-600 hover:underline font-bold"
                        >
                          <span>Visit</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* =====================================================================
          TAB 2: DOMAIN & INDUSTRY BREAKDOWN TABLE (Requested by User)
         ===================================================================== */}
      {activeTab === "domain_table" && (
        <div className="space-y-4">
          <div className="bg-amber-50 border border-amber-200 p-4 rounded-2xl text-xs text-amber-900">
            <strong>Ad Spend Intelligence Summary:</strong> In Jaipur, the top 2 dominating domains spending the most on Facebook & Instagram ads are <strong>Education & Competitive Coaching (32% ad share)</strong> and <strong>Luxury Kundan & Polki Jewellery (26% ad share)</strong>, followed by <strong>Real Estate Developers</strong>.
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Domain / Industry</th>
                    <th className="py-3.5 px-4 text-center">Tracked Companies</th>
                    <th className="py-3.5 px-4 text-center">Total Active Ads</th>
                    <th className="py-3.5 px-4 text-center">Jaipur Ad Share</th>
                    <th className="py-3.5 px-4 text-center">Average Ads / Brand</th>
                    <th className="py-3.5 px-4 text-center">Spend Intensity</th>
                    <th className="py-3.5 px-4">Highest Spender in Domain</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {domainSummaries.map((dom, index) => (
                    <tr key={dom.name} className="hover:bg-slate-50/80 transition">
                      <td className="py-3.5 px-4 font-bold text-slate-900 text-sm">
                        <div className="flex items-center gap-2">
                          <span className="w-6 h-6 rounded-md bg-indigo-50 text-indigo-700 font-bold text-xs flex items-center justify-center">
                            #{index + 1}
                          </span>
                          <span>{dom.name}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-slate-700">
                        {dom.company_count} Brands
                      </td>
                      <td className="py-3.5 px-4 text-center font-black text-indigo-700 text-sm">
                        🔥 {dom.total_active_ads} Ads
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="font-extrabold text-slate-900">{dom.share_percent}%</span>
                        <div className="w-20 mx-auto bg-slate-100 h-1.5 rounded-full mt-1">
                          <div
                            className="bg-indigo-600 h-full rounded-full"
                            style={{ width: `${dom.share_percent * 2.5}%` }}
                          />
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-slate-800">
                        {dom.avg_ads_per_company} Ads/Brand
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`inline-block px-2.5 py-0.5 rounded-md text-[11px] font-bold border ${
                            dom.spend_intensity === "Very High"
                              ? "bg-rose-50 text-rose-700 border-rose-200"
                              : dom.spend_intensity === "High"
                              ? "bg-amber-50 text-amber-700 border-amber-200"
                              : "bg-emerald-50 text-emerald-700 border-emerald-200"
                          }`}
                        >
                          {dom.spend_intensity}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">
                        ⭐ {dom.top_advertiser}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          TAB 3: CONTACT CARDS VIEW (Clean & Direct)
         ===================================================================== */}
      {activeTab === "cards" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filtered.map((co, index) => (
            <div
              key={co.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-md transition space-y-4 relative"
            >
              {/* Top: Rank, Name & Badges */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <span className="w-7 h-7 rounded-lg bg-slate-100 text-slate-700 font-extrabold text-xs flex items-center justify-center shrink-0 border border-slate-200">
                    #{index + 1}
                  </span>
                  <div>
                    <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                      {co.name}
                    </h2>
                    <div className="flex flex-wrap items-center gap-1.5 mt-1">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md">
                        <MapPin className="w-3 h-3" />
                        <span>{co.locality}, {co.city_name}</span>
                      </span>
                      <span className="text-[11px] text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md font-medium">
                        {co.domain_group}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Prominent Active Ads Count Badge */}
                <div className="flex flex-col items-end shrink-0 gap-1">
                  <span className="inline-flex items-center gap-1 text-xs font-black bg-emerald-50 text-emerald-800 border border-emerald-300 px-2.5 py-1 rounded-xl shadow-2xs">
                    <Flame className="w-3.5 h-3.5 text-emerald-600 fill-current" />
                    <span>{co.active_ads} Ads</span>
                  </span>
                  <span className="text-[10px] text-slate-500 font-semibold">
                    {co.spend_tier} Spend
                  </span>
                </div>
              </div>

              {/* Ad Headline Preview */}
              <p className="text-xs text-slate-600 italic bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                "{co.ad_headline}"
              </p>

              {/* DIRECT CONTACT DETAILS */}
              <div className="space-y-2 pt-1 border-t border-slate-100 text-xs">
                {/* Phone */}
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-indigo-600" />
                    <span>Phone</span>
                  </span>
                  <a
                    href={`tel:${co.phone.replace(/[\s-]/g, "")}`}
                    className="font-bold text-slate-900 hover:text-indigo-600 transition"
                  >
                    {co.phone}
                  </a>
                </div>

                {/* WhatsApp */}
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium flex items-center gap-1.5">
                    <MessageSquare className="w-3.5 h-3.5 text-emerald-600" />
                    <span>WhatsApp</span>
                  </span>
                  <a
                    href={`https://wa.me/${co.whatsapp.replace(/[^0-9]/g, "")}`}
                    target="_blank"
                    rel="noreferrer"
                    className="font-bold text-emerald-700 hover:underline flex items-center gap-1"
                  >
                    <span>{co.whatsapp}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>

                {/* Email */}
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-sky-600" />
                    <span>Email</span>
                  </span>
                  <a
                    href={`mailto:${co.email}`}
                    className="font-semibold text-slate-800 hover:text-indigo-600 transition truncate max-w-[220px]"
                  >
                    {co.email}
                  </a>
                </div>

                {/* Website */}
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium flex items-center gap-1.5">
                    <Globe className="w-3.5 h-3.5 text-slate-600" />
                    <span>Website</span>
                  </span>
                  <a
                    href={co.website}
                    target="_blank"
                    rel="noreferrer"
                    className="font-semibold text-indigo-600 hover:underline flex items-center gap-1 truncate max-w-[220px]"
                  >
                    <span>{co.website.replace("https://", "")}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>

                {/* Address */}
                <div className="pt-1.5 border-t border-slate-100 flex items-start gap-1.5 text-slate-500 text-[11px] leading-relaxed">
                  <MapPin className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                  <span>{co.address}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
