"use client";

import { useState } from "react";
import { BarChart3, Sliders, Info, ShieldAlert, Award, ArrowUpRight, ArrowDownRight } from "lucide-react";

interface CityScore {
  city_slug: string;
  city_name: string;
  composite_score: number;
  sample_ok: boolean;
  raw_metrics: {
    active_advertisers: number;
    advertiser_density: number;
    contact_coverage: number;
    growth_velocity: number;
    smb_share: number;
  };
  top_positive_factors: string[];
  top_negative_factors: string[];
}

const DEMO_SCORES: Record<string, CityScore[]> = {
  outreach: [
    {
      city_slug: "jaipur",
      city_name: "Jaipur",
      composite_score: 84.5,
      sample_ok: true,
      raw_metrics: { active_advertisers: 380, advertiser_density: 12.4, contact_coverage: 0.78, growth_velocity: 0.28, smb_share: 0.89 },
      top_positive_factors: ["Contact coverage (+12.4)", "SMB share (+8.2)"],
      top_negative_factors: ["Total scale (-3.1)"],
    },
    {
      city_slug: "bengaluru",
      city_name: "Bengaluru",
      composite_score: 79.2,
      sample_ok: true,
      raw_metrics: { active_advertisers: 1150, advertiser_density: 13.6, contact_coverage: 0.72, growth_velocity: 0.22, smb_share: 0.76 },
      top_positive_factors: ["Active scale (+15.0)", "Contact coverage (+6.2)"],
      top_negative_factors: ["SMB share (-4.2)"],
    },
    {
      city_slug: "mumbai",
      city_name: "Mumbai",
      composite_score: 74.0,
      sample_ok: true,
      raw_metrics: { active_advertisers: 1240, advertiser_density: 9.9, contact_coverage: 0.65, growth_velocity: 0.18, smb_share: 0.71 },
      top_positive_factors: ["Active scale (+16.5)"],
      top_negative_factors: ["Contact coverage (-6.5)", "Growth velocity (-4.0)"],
    },
    {
      city_slug: "delhi",
      city_name: "Delhi",
      composite_score: 71.8,
      sample_ok: true,
      raw_metrics: { active_advertisers: 1480, advertiser_density: 8.8, contact_coverage: 0.62, growth_velocity: 0.19, smb_share: 0.68 },
      top_positive_factors: ["Total scale (+18.0)"],
      top_negative_factors: ["Advertiser density (-8.2)", "SMB share (-5.1)"],
    },
    {
      city_slug: "kolkata",
      city_name: "Kolkata",
      composite_score: 63.4,
      sample_ok: true,
      raw_metrics: { active_advertisers: 520, advertiser_density: 11.5, contact_coverage: 0.58, growth_velocity: 0.14, smb_share: 0.84 },
      top_positive_factors: ["SMB share (+7.0)"],
      top_negative_factors: ["Contact coverage (-9.2)", "Growth velocity (-6.1)"],
    },
  ],
};

export default function CityComparisonPage() {
  const [profile, setProfile] = useState("outreach");
  const scores = DEMO_SCORES["outreach"];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-indigo-600" />
              <span>City Vitality Benchmark</span>
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Objective comparison of the 5 Indian metropolitan advertising markets using observable proxy metrics.
            </p>
          </div>

          {/* Goal Profile Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-600">Goal:</span>
            <select
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="outreach">Outreach Prospecting (Default)</option>
              <option value="maturity">Market Maturity</option>
              <option value="low_competition">Low-Competition Entry</option>
            </select>
          </div>
        </div>

        {/* Mandatory Transparency Disclosure */}
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-center gap-2">
          <Info className="w-4 h-4 shrink-0 text-amber-600" />
          <span>
            <strong>Analytical Disclosure:</strong> Scores are computed strictly from public Meta Ad Library activity and website enrichment proxies. Commercial ad spend and impressions are not published by Meta outside the EU and are not estimated.
          </span>
        </div>
      </div>

      {/* City Leaderboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {scores.map((city, idx) => (
          <div
            key={city.city_slug}
            className={`bg-white border rounded-2xl p-5 shadow-xs flex flex-col justify-between ${
              idx === 0 ? "border-indigo-500 ring-2 ring-indigo-500/10" : "border-slate-200"
            }`}
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Rank #{idx + 1}</span>
                {idx === 0 && (
                  <span className="text-[10px] font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full flex items-center gap-0.5">
                    <Award className="w-3 h-3" />
                    <span>Top Market</span>
                  </span>
                )}
              </div>
              <h3 className="text-lg font-bold text-slate-900 mt-1">{city.city_name}</h3>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-3xl font-black text-slate-900">{city.composite_score}</span>
                <span className="text-xs text-slate-400 font-semibold">/ 100</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 space-y-2 text-xs">
              <div>
                <span className="text-[10px] text-slate-400 font-bold block uppercase">Primary Drivers</span>
                <div className="space-y-1 mt-1">
                  {city.top_positive_factors.map((f, i) => (
                    <div key={i} className="text-emerald-700 font-medium flex items-center gap-1 text-[11px]">
                      <ArrowUpRight className="w-3 h-3" />
                      <span>{f}</span>
                    </div>
                  ))}
                  {city.top_negative_factors.map((f, i) => (
                    <div key={i} className="text-rose-600 font-medium flex items-center gap-1 text-[11px]">
                      <ArrowDownRight className="w-3 h-3" />
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Raw Proxy Metrics Table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
        <div className="p-5 border-b border-slate-100">
          <h2 className="text-sm font-bold text-slate-900">Cross-City Proxy Metric Matrix (Trailing 30-Day Window)</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
                <th className="py-3 px-4">City</th>
                <th className="py-3 px-4">Active Advertisers (A)</th>
                <th className="py-3 px-4">Density / 100k Pop (D)</th>
                <th className="py-3 px-4">Contact Coverage (C)</th>
                <th className="py-3 px-4">Growth Velocity (G)</th>
                <th className="py-3 px-4">SMB Share (S)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {scores.map((c) => (
                <tr key={c.city_slug} className="hover:bg-slate-50/50 transition">
                  <td className="py-3 px-4 font-bold text-slate-900">{c.city_name}</td>
                  <td className="py-3 px-4">{c.raw_metrics.active_advertisers}</td>
                  <td className="py-3 px-4">{c.raw_metrics.advertiser_density}</td>
                  <td className="py-3 px-4 text-emerald-700 font-bold">
                    {Math.round(c.raw_metrics.contact_coverage * 100)}%
                  </td>
                  <td className="py-3 px-4">{Math.round(c.raw_metrics.growth_velocity * 100)}%</td>
                  <td className="py-3 px-4">{Math.round(c.raw_metrics.smb_share * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

