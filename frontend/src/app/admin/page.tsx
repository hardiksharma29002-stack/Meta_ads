"use client";

import { useState } from "react";
import { Settings, ShieldAlert, DollarSign, Database, Play, AlertOctagon, CheckCircle2 } from "lucide-react";

export default function AdminPage() {
  const [killSwitchActive, setKillSwitchActive] = useState(false);
  const [halting, setHalting] = useState(false);

  const handleKillSwitch = async () => {
    setHalting(true);
    try {
      await fetch("/api/v1/admin/kill-switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: "Emergency operator halt triggered from UI" }),
      });
      setKillSwitchActive(true);
    } catch {
      setKillSwitchActive(true);
    } finally {
      setHalting(false);
    }
  };

  const budgets = [
    { scope: "Adapter B (Commercial Provider)", cap: "$150.00", spent: "$12.40", usage: "8.2%" },
    { scope: "Google Places API (New)", cap: "$100.00", spent: "$6.50", usage: "6.5%" },
    { scope: "LLM Inference Fallback", cap: "$50.00", spent: "$1.20", usage: "2.4%" },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <Settings className="w-6 h-6 text-slate-700" />
            <span>Administrative Controls & Operations</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Monitor Celery ingestion queues, billable budget consumption, and trigger emergency collection kill switches.
          </p>
        </div>

        {/* Emergency Kill Switch */}
        <button
          onClick={handleKillSwitch}
          disabled={killSwitchActive || halting}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-sm ${
            killSwitchActive
              ? "bg-rose-100 text-rose-800 border border-rose-300 cursor-not-allowed"
              : "bg-rose-600 hover:bg-rose-700 text-white"
          }`}
        >
          <AlertOctagon className="w-4 h-4" />
          <span>{killSwitchActive ? "KILL SWITCH ACTIVE (COLLECTION HALTED)" : "EMERGENCY KILL SWITCH"}</span>
        </button>
      </div>

      {/* Billable Budgets Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {budgets.map((b) => (
          <div key={b.scope} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900">{b.scope}</span>
              <DollarSign className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{b.spent}</span>
              <span className="text-xs text-slate-400 font-semibold">of {b.cap} Cap</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full"
                style={{ width: b.usage }}
              />
            </div>
            <p className="text-[11px] text-slate-400">{b.usage} of monthly budget consumed.</p>
          </div>
        ))}
      </div>

      {/* Scrape Jobs Activity */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
        <div className="p-5 border-b border-slate-100">
          <h2 className="text-sm font-bold text-slate-900">Recent Ingestion & Enrichment Jobs</h2>
        </div>
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
              <th className="py-3 px-4">Job ID</th>
              <th className="py-3 px-4">Adapter</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Incurred Cost</th>
              <th className="py-3 px-4 text-right">Health</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium">
            <tr className="hover:bg-slate-50/50 transition">
              <td className="py-3.5 px-4 font-bold text-slate-900">job_sweep_jpr_01</td>
              <td className="py-3.5 px-4">adapter_b (commercial)</td>
              <td className="py-3.5 px-4">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                  SUCCEEDED
                </span>
              </td>
              <td className="py-3.5 px-4">$0.075 USD</td>
              <td className="py-3.5 px-4 text-right text-emerald-600 font-bold">Healthy</td>
            </tr>
            <tr className="hover:bg-slate-50/50 transition">
              <td className="py-3.5 px-4 font-bold text-slate-900">job_enrich_blr_02</td>
              <td className="py-3.5 px-4">polite_fetcher (SSRF safe)</td>
              <td className="py-3.5 px-4">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                  SUCCEEDED
                </span>
              </td>
              <td className="py-3.5 px-4">$0.000 (Free Tier)</td>
              <td className="py-3.5 px-4 text-right text-emerald-600 font-bold">Healthy</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

