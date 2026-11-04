---
description: Standards and guidelines for Next.js, TypeScript, Tailwind CSS, UI/UX state handling, and accessibility.
globs: ["frontend/**/*"]
alwaysApply: false
---

# Frontend Engineering Standards

## 1. Stack & Architecture
- **Framework:** Next.js (App Router) with TypeScript in strict mode (`strict: true`, `noImplicitAny: true`).
- **Styling & Components:** Tailwind CSS with `shadcn/ui` (accessible, customizable Radix primitives).
- **State & Data Fetching:** TanStack Query (React Query) for server-state caching, deduping, and background updates.
- **Data Tables:** TanStack Table with virtualized scrolling (`@tanstack/react-virtual`) for performant rendering of large advertiser datasets (SRCH-03).
- **Charts & Visualizations:** Recharts or ECharts for comparison radars, time series, and category breakdowns.

## 2. Security & Rendering Rules
- **No Raw HTML Injection:** Never render untrusted scraped text or ad content using `dangerouslySetInnerHTML`. Rely solely on standard JSX text escaping to neutralize XSS vectors (SEC-02).
- **Contact Masking:** Render contacts masked by default (`+91 98•••• ••21`, `in••••@domain.com`). Contact reveal triggers an explicit POST request, consumes user daily quota, and visually alerts the user to provenance and verification tier.
- **Formula Injection Prevention in CSV/Export Views:** Ensure all downloaded or table-rendered export content handles leading symbols (`=`, `+`, `-`, `@`, tab) safely (SEC-03).

## 3. UI/UX State Contract
Every data-driven page and widget must explicitly handle five discrete visual states:
1. **Loading:** Skeleton loaders reflecting the expected layout shape (never generic full-page spinners).
2. **Empty:** Informative empty state explaining *why* no records exist (e.g., active filters vs. un-crawled city), offering actionable suggestions or clear-filter actions (SRCH-02).
3. **Error:** Human-readable error banner displaying the backend `request_id` and a one-click retry trigger.
4. **Stale Data:** Visual warning badge or banner whenever a city's crawl snapshot is older than 14 days (SRCH-04).
5. **Insufficient Data:** Muted or greyed scores accompanied by an "Insufficient Sample" badge whenever an attribution group has fewer than `MIN_SAMPLE` (default 200) confirmed advertisers (ANA-01, SRCH-11).

## 4. Typography & Indic Localization
- **Font Stack:** Noto Sans for Latin scripts, paired with Google Noto fonts for Indic scripts:
  - `Noto Sans Devanagari` (Hindi, Marathi)
  - `Noto Sans Bengali` (Bengali)
  - `Noto Sans Kannada` (Kannada)
- **HTML Attributes:** Set explicit `lang` attributes on localized text spans or container elements to ensure proper font rendering and screen reader pronunciation (SRCH-07).

## 5. Mandatory Copy & Disclaimers
On all comparison pages (`/compare`) and city scorecards, the following disclosure copy must be visible adjacent to rankings:
> *"Based on Meta Ad Library activity. Commercial ad spend and impressions are not published by Meta outside the EU and are not estimated."*

## 6. Accessibility & Performance Benchmarks
- **A11y:** Adhere to WCAG 2.2 AA fundamentals: all interactive elements must be keyboard-focusable, color alone must not convey state (use icons and text labels), and all forms must feature programmatic labels.
- **Performance:** Maintain Largest Contentful Paint (LCP) < 2.5 seconds on city results pages.

