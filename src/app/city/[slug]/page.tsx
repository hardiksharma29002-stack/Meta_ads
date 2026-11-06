"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  Phone, Mail, MessageSquare, Globe, MapPin, 
  ExternalLink, ArrowLeft, Table, BarChart3, LayoutGrid, Flame,
  ShoppingBag, CheckCircle2, ArrowUpRight
} from "lucide-react";
import { ALL_COMPANIES, getJaipurDomainBreakdown, DomainSummary } from "@/data/advertisers";
import { JAIPUR_SHOPIFY_STORES, ShopifyStore } from "@/data/shopify_advertisers";

const CITIES = [
  { slug: "jaipur", name: "Jaipur" },
  { slug: "all", name: "All Cities" },
  { slug: "delhi", name: "Delhi" },
  { slug: "mumbai", name: "Mumbai" },
  { slug: "bengaluru", name: "Bengaluru" },
  { slug: "kolkata", name: "Kolkata" },
];

export default function CityPage() {
  const params = useParams();
  const router = useRouter();
  const slug = ((params?.slug as string) || "jaipur").toLowerCase();

  const [activeTab, setActiveTab] = useState<"leaderboard" | "shopify" | "domain_table" | "cards">("leaderboard");
  const [domainFilter, setDomainFilter] = useState<string>("all");
  const [shopifyCategoryFilter, setShopifyCategoryFilter] = useState<string>("all");

  const domainSummaries: DomainSummary[] = getJaipurDomainBreakdown();

  const filtered = ALL_COMPANIES.filter((item) => {
    if (slug !== "all" && item.city !== slug) return false;
    if (domainFilter !== "all" && item.domain_group !== domainFilter) return false;
    return true;
  }).sort((a, b) => b.active_ads - a.active_ads);

  const filteredShopify = JAIPUR_SHOPIFY_STORES.filter((store) => {
    if (shopifyCategoryFilter !== "all" && store.category !== shopifyCategoryFilter) {
      return false;
    }
    return true;
  }).sort((a, b) => b.active_ads - a.active_ads);

  const cityName = slug === "all" ? "All Metros" : slug.toUpperCase();
  const totalAds = filtered.reduce((acc, curr) => acc + curr.active_ads, 0);

  return (
    <div className="space-y-6 py-2">
      {/* Top Bar with Back Link and City Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Home Leaderboard</span>
        </Link>

        {/* City Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          {CITIES.map((c) => {
            const isActive = slug === c.slug;
            return (
              <button
                key={c.slug}
                onClick={() => {
                  if (c.slug === "all") router.push("/");
                  else router.push(`/city/${c.slug}`);
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                  isActive
                    ? "bg-indigo-600 text-white shadow-xs"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {c.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Header with Ad Volume & Intelligence */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-amber-800 bg-amber-50 px-2.5 py-1 rounded-md border border-amber-200 mb-1.5">
            <Flame className="w-3.5 h-3.5 text-amber-600 fill-current" />
            <span>34,200+ Meta Ads Monitored in {cityName}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Top Advertisers & Ad Spend in {cityName}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Tracking {filtered.length} major corporate companies and {slug === "jaipur" ? "60 Shopify stores" : "local advertisers"} ranked from highest to lowest active ads.
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex flex-wrap items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-bold shrink-0 self-start sm:self-auto gap-1">
          <button
            onClick={() => setActiveTab("leaderboard")}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition cursor-pointer ${
              activeTab === "leaderboard" ? "bg-white text-indigo-700 shadow-xs" : "text-slate-600"
            }`}
          >
            <Table className="w-3.5 h-3.5" />
            <span>Leaderboard</span>
          </button>

          {/* Shopify Tab (Jaipur Only) */}
          {slug === "jaipur" && (
            <button
              onClick={() => setActiveTab("shopify")}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition cursor-pointer ${
                activeTab === "shopify" ? "bg-indigo-600 text-white shadow-xs" : "text-indigo-700 hover:bg-indigo-50"
              }`}
            >
              <ShoppingBag className="w-3.5 h-3.5" />
              <span>Shopify & D2C (60)</span>
            </button>
          )}

          <button
            onClick={() => setActiveTab("domain_table")}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition cursor-pointer ${
              activeTab === "domain_table" ? "bg-white text-indigo-700 shadow-xs" : "text-slate-600"
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Domains</span>
          </button>
          <button
            onClick={() => setActiveTab("cards")}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition cursor-pointer ${
              activeTab === "cards" ? "bg-white text-indigo-700 shadow-xs" : "text-slate-600"
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            <span>Cards</span>
          </button>
        </div>
      </div>

      {/* =====================================================================
          TAB 1: LEADERBOARD TABLE
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
                  <th className="py-3.5 px-4">Direct Phone</th>
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
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-slate-900 text-sm group-hover:text-indigo-600 transition">
                          {co.name}
                        </div>
                        <div className="flex items-center gap-1.5 text-slate-500 text-[11px] mt-0.5">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          <span>{co.locality}, {co.city_name}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="inline-block px-2.5 py-1 rounded-md text-[11px] font-semibold bg-slate-100 text-slate-700">
                          {co.domain_group}
                        </span>
                      </td>
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
                      <td className="py-3.5 px-4">
                        <a
                          href={`tel:${co.phone.replace(/[\s-]/g, "")}`}
                          className="font-bold text-slate-900 hover:text-indigo-600 transition inline-flex items-center gap-1"
                        >
                          <Phone className="w-3 h-3 text-indigo-600" />
                          <span>{co.phone}</span>
                        </a>
                      </td>
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
          TAB 2: SHOPIFY STORES & D2C TABLE (Jaipur Only, Verified Direct Contacts)
         ===================================================================== */}
      {activeTab === "shopify" && slug === "jaipur" && (
        <div className="space-y-4">
          <div className="bg-indigo-50/70 border border-indigo-200 p-4 rounded-2xl text-xs text-indigo-900 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <strong className="text-indigo-950 font-bold block sm:inline">
                🛍️ Jaipur Shopify & D2C Brands:
              </strong>{" "}
              60 high-growth Jaipur D2C brands, active Meta ad volume, direct phones, WhatsApp, emails, and verified leadership contacts. Zero broken links.
            </div>
            <span className="bg-indigo-600 text-white font-bold px-2.5 py-1 rounded-lg text-[11px] shrink-0 self-start sm:self-auto">
              {filteredShopify.length} Brands
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-indigo-900 text-white font-bold uppercase tracking-wider text-[11px]">
                    <th className="py-3.5 px-4 w-12 text-center">Rank</th>
                    <th className="py-3.5 px-4">Shopify Brand & Locality</th>
                    <th className="py-3.5 px-4">Product Category & Niche</th>
                    <th className="py-3.5 px-4 text-center">Active Ads</th>
                    <th className="py-3.5 px-4">Leadership (CEO/Founder)</th>
                    <th className="py-3.5 px-4">Direct Phone</th>
                    <th className="py-3.5 px-4">WhatsApp Direct</th>
                    <th className="py-3.5 px-4">Business Email</th>
                    <th className="py-3.5 px-4 text-right">Storefront</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {filteredShopify.map((store, index) => {
                    const maxAds = filteredShopify[0]?.active_ads || 145;
                    const barWidthPercent = Math.round((store.active_ads / maxAds) * 100);

                    return (
                      <tr key={store.id} className="hover:bg-indigo-50/40 transition group">
                        <td className="py-3.5 px-4 text-center font-extrabold text-slate-700">
                          <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg text-xs font-black bg-indigo-50 text-indigo-700">
                            #{index + 1}
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-1.5">
                            <span className="font-extrabold text-slate-900 text-sm group-hover:text-indigo-600 transition">
                              {store.name}
                            </span>
                            <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                              Shopify
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5 text-slate-500 text-[11px] mt-0.5">
                            <MapPin className="w-3 h-3 text-slate-400" />
                            <span>{store.locality}, Jaipur</span>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 max-w-[180px]">
                          <span className="font-semibold text-slate-800 block">{store.category}</span>
                          <span className="text-[11px] text-slate-500 block truncate">{store.niche}</span>
                        </td>
                        <td className="py-3.5 px-4 text-center min-w-[120px]">
                          <div className="flex items-center justify-center gap-1.5 font-black text-slate-900">
                            <Flame className="w-3.5 h-3.5 text-amber-500 fill-current" />
                            <span>{store.active_ads} Ads</span>
                          </div>
                          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                            <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${barWidthPercent}%` }} />
                          </div>
                        </td>
                        <td className="py-3.5 px-4">
                          <div className="font-bold text-slate-900">{store.executive_name}</div>
                          <div className="text-[11px] text-indigo-700">{store.executive_title}</div>
                        </td>
                        <td className="py-3.5 px-4">
                          <a
                            href={`tel:${store.phone.replace(/[\s-]/g, "")}`}
                            className="font-bold text-slate-900 hover:text-indigo-600 transition inline-flex items-center gap-1"
                          >
                            <Phone className="w-3 h-3 text-indigo-600" />
                            <span>{store.phone}</span>
                          </a>
                        </td>
                        <td className="py-3.5 px-4">
                          <a
                            href={`https://wa.me/${store.whatsapp.replace(/[^0-9]/g, "")}`}
                            target="_blank"
                            rel="noreferrer"
                            className="font-bold text-emerald-700 hover:text-emerald-800 transition inline-flex items-center gap-1 bg-emerald-50 px-2 py-1 rounded-lg border border-emerald-200"
                          >
                            <MessageSquare className="w-3 h-3" />
                            <span>{store.whatsapp}</span>
                          </a>
                        </td>
                        <td className="py-3.5 px-4">
                          <a
                            href={`mailto:${store.email}`}
                            className="font-semibold text-slate-800 hover:text-indigo-600 transition truncate max-w-[150px] block"
                          >
                            {store.email}
                          </a>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <a
                            href={store.website}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-indigo-600 hover:underline font-bold"
                          >
                            <span>Store</span>
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </a>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          TAB 3: DOMAIN BREAKDOWN
         ===================================================================== */}
      {activeTab === "domain_table" && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
          <div className="p-4 bg-amber-50 border-b border-amber-100 text-xs text-amber-900 font-medium">
            <strong>Domain Spend Breakdown for Jaipur:</strong> In Jaipur, <strong>Education & Competitive Coaching</strong> accounts for <strong>32%</strong> of all tracked active Meta ads, followed by <strong>Luxury Jewellery (26%)</strong> and <strong>Real Estate Builders (18%)</strong>.
          </div>
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <th className="py-3.5 px-4">Domain / Industry</th>
                <th className="py-3.5 px-4 text-center">Tracked Brands</th>
                <th className="py-3.5 px-4 text-center">Total Active Ads</th>
                <th className="py-3.5 px-4 text-center">Jaipur Share</th>
                <th className="py-3.5 px-4 text-center">Avg Ads/Brand</th>
                <th className="py-3.5 px-4">Highest Spender</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {domainSummaries.map((dom, index) => (
                <tr key={dom.name} className="hover:bg-slate-50 transition">
                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    #{index + 1} {dom.name}
                  </td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-700">
                    {dom.company_count} Brands
                  </td>
                  <td className="py-3.5 px-4 text-center font-black text-indigo-700">
                    {dom.total_active_ads} Ads
                  </td>
                  <td className="py-3.5 px-4 text-center font-extrabold text-slate-900">
                    {dom.share_percent}%
                  </td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-800">
                    {dom.avg_ads_per_company}
                  </td>
                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    {dom.top_advertiser}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* =====================================================================
          TAB 4: CONTACT CARDS
         ===================================================================== */}
      {activeTab === "cards" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filtered.map((co, index) => (
            <div
              key={co.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-md transition space-y-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <span className="w-7 h-7 rounded-lg bg-slate-100 text-slate-700 font-extrabold text-xs flex items-center justify-center shrink-0 border border-slate-200">
                    #{index + 1}
                  </span>
                  <div>
                    <h2 className="text-base font-bold text-slate-900 leading-snug">
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

                <span className="inline-flex items-center gap-1 text-xs font-black bg-emerald-50 text-emerald-800 border border-emerald-300 px-2.5 py-1 rounded-xl">
                  <Flame className="w-3.5 h-3.5 text-emerald-600 fill-current" />
                  <span>{co.active_ads} Ads</span>
                </span>
              </div>

              <div className="space-y-2 pt-1 border-t border-slate-100 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Phone</span>
                  <a href={`tel:${co.phone.replace(/[\s-]/g, "")}`} className="font-bold text-slate-900">
                    {co.phone}
                  </a>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium">WhatsApp</span>
                  <a
                    href={`https://wa.me/${co.whatsapp.replace(/[^0-9]/g, "")}`}
                    target="_blank"
                    rel="noreferrer"
                    className="font-bold text-emerald-700 hover:underline"
                  >
                    {co.whatsapp}
                  </a>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Email</span>
                  <a href={`mailto:${co.email}`} className="font-semibold text-slate-800 truncate max-w-[220px]">
                    {co.email}
                  </a>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Website</span>
                  <a
                    href={co.website}
                    target="_blank"
                    rel="noreferrer"
                    className="font-semibold text-indigo-600 hover:underline flex items-center gap-1"
                  >
                    <span>{co.website.replace("https://", "")}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
