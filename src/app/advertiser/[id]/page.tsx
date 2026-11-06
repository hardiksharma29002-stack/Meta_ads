"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { 
  Building2, Globe, MapPin, Phone, Mail, MessageSquare, 
  ExternalLink, ShieldCheck, CheckCircle2, AlertCircle, ArrowLeft, Flag 
} from "lucide-react";

export default function AdvertiserProfilePage() {
  const params = useParams();
  const id = params?.id || "101";

  const [feedbackSent, setFeedbackSent] = useState(false);

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link href="/city/jaipur" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to City Directory</span>
      </Link>

      {/* Main Profile Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-slate-900">Jaipur Craft Villa</h1>
              <span className="text-xs bg-indigo-100 text-indigo-800 font-bold px-2.5 py-0.5 rounded-full">
                Local SMB
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-2">
              <span>Meta Page ID: meta_page_jpr_01</span>
              <span>•</span>
              <span>First observed: 12 Aug 2026</span>
              <span>•</span>
              <span className="text-emerald-700 font-semibold">14 Active Campaigns</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setFeedbackSent(true)}
              className="px-3 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 transition flex items-center gap-1.5"
            >
              <Flag className="w-3.5 h-3.5 text-slate-400" />
              <span>{feedbackSent ? "Feedback Logged" : "Report Issue"}</span>
            </button>
            <a
              href="https://facebook.com/ads/library"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700 transition flex items-center gap-1.5 shadow-sm"
            >
              <span>View in Meta Ad Library</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Primary Web Domain Banner */}
        <div className="flex items-center gap-2 pt-2 border-t border-slate-100 text-xs text-slate-600">
          <Globe className="w-4 h-4 text-indigo-600" />
          <span>Primary Verified Website:</span>
          <a href="https://jaipurcraftvilla.in" target="_blank" rel="noreferrer" className="text-indigo-600 font-semibold hover:underline">
            jaipurcraftvilla.in
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Provenance & Verified Contacts */}
        <div className="space-y-6 md:col-span-1">
          {/* Spatial Attribution Evidence */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-600" />
              <span>Why Jaipur? (Geo Evidence)</span>
            </h2>
            <div className="space-y-2 text-xs">
              <div className="p-3 bg-emerald-50/50 border border-emerald-100 rounded-xl space-y-1">
                <div className="flex items-center justify-between font-bold text-emerald-900">
                  <span>Postal PIN Code Match</span>
                  <span>95% Conf</span>
                </div>
                <p className="text-[11px] text-slate-600">Discovered PIN 302001 in website address context.</p>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl space-y-1">
                <div className="flex items-center justify-between font-bold text-slate-800">
                  <span>Landline STD Code</span>
                  <span>60% Conf</span>
                </div>
                <p className="text-[11px] text-slate-600">STD Area Code 0141 confirmed on contact page.</p>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl space-y-1">
                <div className="flex items-center justify-between font-bold text-slate-800">
                  <span>Rajasthan GST State Code</span>
                  <span>30% Conf</span>
                </div>
                <p className="text-[11px] text-slate-600">GSTIN prefix 08 observed in corporate footer.</p>
              </div>
            </div>
          </div>

          {/* Contact Channels */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-indigo-600" />
              <span>Verified Public Contacts</span>
            </h2>
            <div className="space-y-2.5">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Phone className="w-4 h-4 text-indigo-600" />
                  <div>
                    <p className="text-xs font-mono font-bold text-slate-900">+91-141-2365401</p>
                    <p className="text-[10px] text-slate-400">Landline Showroom • 92% Conf</p>
                  </div>
                </div>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-medium">Verified</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <MessageSquare className="w-4 h-4 text-emerald-600" />
                  <div>
                    <p className="text-xs font-mono font-bold text-slate-900">+91 98290 12345</p>
                    <p className="text-[10px] text-slate-400">WhatsApp Business • 95% Conf</p>
                  </div>
                </div>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-medium">Verified</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Mail className="w-4 h-4 text-sky-600" />
                  <div>
                    <p className="text-xs font-mono font-bold text-slate-900">care@jaipurcraftvilla.in</p>
                    <p className="text-[10px] text-slate-400">Role Email (MX Verified)</p>
                  </div>
                </div>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-medium">Verified</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Ad History & Creative Timeline */}
        <div className="md:col-span-2 space-y-4">
          <h2 className="text-sm font-bold text-slate-900 flex items-center justify-between">
            <span>Active Ad Creatives ({id})</span>
            <span className="text-xs font-normal text-slate-400">Chronological feed</span>
          </h2>

          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800">Headline: Authentic Handcrafted Blue Pottery & Rugs</span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">Active</span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Visit our showroom at M.I. Road, Jaipur or order online. Direct wholesale pricing for hotels and interior designers. Call 0141-2365401 or WhatsApp +919829012345.
              </p>
              <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-400">
                <span>CTA: SHOP_NOW</span>
                <span>Platforms: Instagram, Facebook Feed</span>
                <span className="text-indigo-600 font-semibold">Meta ID: ad_jpr_101</span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800">Headline: Handblock Printed Bed Linen & Quilts</span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">Active</span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Sanganeri block print razai and dohar sets crafted by traditional artisans. Custom orders welcome. WhatsApp us directly for wholesale catalogue.
              </p>
              <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-400">
                <span>CTA: WHATSAPP</span>
                <span>Platforms: Instagram Stories</span>
                <span className="text-indigo-600 font-semibold">Meta ID: ad_jpr_102</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

