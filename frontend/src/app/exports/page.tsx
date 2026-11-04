"use client";

import { Download, FileSpreadsheet, ShieldCheck, Clock } from "lucide-react";

export default function ExportsPage() {
  const demoExports = [
    {
      id: "exp_jpr_20261104",
      city: "Jaipur",
      format: "CSV",
      rows: 142,
      created_at: "Today, 14:10 IST",
      expires_in: "6 days remaining",
    },
    {
      id: "exp_mum_20261102",
      city: "Mumbai",
      format: "CSV",
      rows: 380,
      created_at: "2 Nov 2026",
      expires_in: "4 days remaining",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <Download className="w-6 h-6 text-indigo-600" />
            <span>Export Center</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Download your prospect lists in CSV format. Suppressed contacts are permanently excluded.
          </p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
              <th className="py-3 px-4">Export Batch</th>
              <th className="py-3 px-4">Market Scope</th>
              <th className="py-3 px-4">Records</th>
              <th className="py-3 px-4">Generated</th>
              <th className="py-3 px-4">Retention</th>
              <th className="py-3 px-4 text-right">Download</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium">
            {demoExports.map((exp) => (
              <tr key={exp.id} className="hover:bg-slate-50/50 transition">
                <td className="py-3.5 px-4 font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-indigo-600" />
                  <span>{exp.id}</span>
                </td>
                <td className="py-3.5 px-4">{exp.city}</td>
                <td className="py-3.5 px-4 font-bold text-slate-800">{exp.rows} Advertisers</td>
                <td className="py-3.5 px-4 text-slate-500">{exp.created_at}</td>
                <td className="py-3.5 px-4 text-amber-700 font-medium flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{exp.expires_in}</span>
                </td>
                <td className="py-3.5 px-4 text-right">
                  <a
                    href={`/api/v1/exports/${exp.id}/download`}
                    className="px-3 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-lg font-bold text-xs transition inline-flex items-center gap-1"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download CSV</span>
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="p-4 bg-slate-100 rounded-2xl text-xs text-slate-600 flex items-center gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <span>
          <strong>Export Compliance Notice:</strong> All exports embed an invisible cryptographic watermark identifying the authorized user account and timestamp under DPDP purpose limitation rules.
        </span>
      </div>
    </div>
  );
}

