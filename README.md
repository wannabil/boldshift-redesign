# Bold Shift Advisory — redesign concept

A rebuild of [boldshiftadvisory.com](https://boldshiftadvisory.com/) in the editorial executive-education style of
leading US business schools (crimson masthead flowing into the hero, oversized tight grotesk headlines, three-up photo
strip, 4-up program cards, dark program finder, image band with overlay card), built to Google's current best practice.

**Live preview:** https://boldshift-redesign.pages.dev

> Original code. Layout language inspired by Harvard Business School Executive Education (exed.hbs.edu); no logos, copy, images or code from it are used.
> Photos: Unsplash License, self-hosted as WebP. Credits in `public/assets/photos/CREDITS.md`.
> All page copy is Bold Shift Advisory's own; no testimonials, client names or results were invented.

## What's in it
- 6 pages + 404: home, `/individuals`, `/corporate-training`, `/about`, `/free-tools`, `/contact`.
  Product pages (guide checkout, resume review, checklist, companion, proposal, workshops) link to the live site.
- Zero-framework static HTML/CSS + 3 KB of JS (menu, program finder, reveal-on-scroll, mailto enquiry form).
- Self-hosted, preloaded Inter variable font; responsive `srcset` WebP photos with intrinsic sizes (no layout shift) and a preloaded LCP image.

## Google best practice checklist
- **Core Web Vitals / Lighthouse:** Performance 100, Accessibility 100, Best Practices 100, SEO 100
  (mobile + desktop; LCP 1.5 s mobile / 0.2 s desktop, CLS 0, TBT 0 ms).
- One keyword-bearing `<h1>` per page, semantic landmarks, skip link, breadcrumbs, focus styles, reduced-motion support.
- Unique `<title>` (≤60 chars) and meta description per page, canonical URLs, Open Graph + Twitter card (1200×630).
- JSON-LD `@graph`: Organization, Person (founder, `sameAs` Threads), WebSite, WebPage, BreadcrumbList,
  FAQPage (matches the visible FAQ), Product + Offer (RM20 guide), Service + Offer (RM59 resume review), ProfilePage, ContactPage.
- `sitemap.xml`, `robots.txt`, `llms.txt` (AI search / answer engines), web manifest, favicons.
- Security headers via `_headers`: strict CSP (hash for the single inline script), HSTS, nosniff, referrer and permissions policy.
- Hashed asset URLs + 1-year immutable caching.

## Preview vs production
`*.pages.dev` responses carry `X-Robots-Tag: noindex` (see `src/_headers`) so the preview never competes with the
real domain in Google. Canonicals already point at `https://boldshiftadvisory.com`. When moving to the real domain,
attach it as a custom domain in Cloudflare Pages; the noindex rule only matches `pages.dev`, so nothing else changes.

## Build, test, deploy
```bash
npm install                                   # puppeteer-core for screenshots
python3 src/build.py                          # writes ./public
npx wrangler pages dev public --port 4831     # local preview
python3 tests/check.py http://127.0.0.1:4831  # SEO/technical checks
node tests/shots.mjs http://127.0.0.1:4831 tests/shots   # 1366 + 390 screenshots, overflow/console checks
ASSET_URL=https://boldshift-redesign.pages.dev python3 src/build.py
npx wrangler pages deploy public --project-name boldshift-redesign --branch main
```

Built by [Miracle Mikhael](https://miraclemikhael.com) as a redesign concept.
