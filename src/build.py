#!/usr/bin/env python3
"""Static site generator for the Bold Shift Advisory redesign concept (exec-ed editorial style).

Usage: python3 src/build.py            (writes ./public)
Env:   SITE_URL   canonical origin  (default https://boldshiftadvisory.com)
       ASSET_URL  origin for absolute og:image URLs (default = SITE_URL)
"""
import base64
import datetime
import hashlib
import html
import json
import os
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
SITE = os.environ.get("SITE_URL", "https://boldshiftadvisory.com").rstrip("/")
ASSET = os.environ.get("ASSET_URL", SITE).rstrip("/")
LIVE = "https://boldshiftadvisory.com"  # deep product pages stay on the live site
TODAY = datetime.date.today().isoformat()
EMAIL = "ferhanjohar@boldshiftadvisory.com"
THREADS = "https://www.threads.com/@ferhanafterhours"
PHOTOS = json.loads((ROOT / "src/photos.json").read_text())

ARROW = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 12h15m-6-6 6 6-6 6" '
         'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
THREADS_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M17.7 11.1c-.1 0-.2-.1-.3-.1'
                '-.2-3.2-1.9-5-4.9-5h-.1c-1.8 0-3.2.8-4.1 2.1l1.6 1.1c.7-1 1.7-1.2 2.5-1.2 1 0 1.8.3 2.3.9.4.4.6 1 .7'
                ' 1.7-.8-.1-1.7-.2-2.6-.1-2.6.1-4.3 1.7-4.2 3.8.1 1.1.6 2 1.5 2.6.8.5 1.8.8 2.8.7 1.4-.1 2.5-.6 3.2-1.6'
                '.6-.7.9-1.7 1-2.9.7.4 1.2.9 1.4 1.6.5 1.1.5 2.9-1 4.4-1.3 1.3-2.9 1.9-5.3 1.9-2.7 0-4.7-.9-6-2.6C5'
                ' 16.8 4.4 14.7 4.4 12s.6-4.8 1.8-6.4c1.3-1.7 3.3-2.6 6-2.6s4.8.9 6.1 2.6c.7.8 1.1 1.9 1.4 3.1l1.9-.5'
                'c-.4-1.5-1-2.8-1.8-3.8C18.1 2.3 15.6 1.1 12.3 1.1h-.1C8.9 1.1 6.4 2.3 4.7 4.4 3.2 6.3 2.4 8.9 2.4 12'
                's.8 5.7 2.3 7.6c1.7 2.1 4.2 3.3 7.5 3.3h.1c2.9 0 5-.8 6.7-2.5 2.3-2.3 2.2-5.1 1.4-6.8-.5-1.2-1.5-2.2'
                '-2.7-2.7zm-5 4.6c-1.1.1-2.2-.4-2.3-1.4 0-.8.6-1.6 2.3-1.7h.6c.6 0 1.2.1 1.8.2-.2 2.4-1.3 2.8-2.4 2.9z"/></svg>')
INLINE_JS = "document.documentElement.classList.add('js')"

NAV = [("/individuals", "For Individuals"), ("/corporate-training", "Corporate Training"),
       ("/free-tools", "Free Tools"), ("/about", "About Ferhan"), ("/contact", "Contact")]

ORG_ID = f"{SITE}/#organization"
PERSON_ID = f"{SITE}/#ferhan"
WEBSITE_ID = f"{SITE}/#website"
CSS_V = JS_V = ""


def e(s):
    return html.escape(s, quote=True)


def asset_hash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:10]


def ph(name, alt, sizes="(min-width: 1100px) 25vw, (min-width: 640px) 50vw, 100vw", eager=False, cls=""):
    """Responsive, self-hosted WebP photo with intrinsic size (no CLS)."""
    w, h = PHOTOS[name]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="/assets/photos/{name}-800.webp" '
            f'srcset="/assets/photos/{name}-800.webp 800w, /assets/photos/{name}-1600.webp 1600w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{e(alt)}" {load} decoding="async">')


# ------------------------------------------------------------------ structured data
def base_graph():
    return [
        {"@type": "Organization", "@id": ORG_ID, "name": "Bold Shift Advisory",
         "legalName": "Bold Shift Advisory Sdn Bhd", "url": SITE + "/", "email": EMAIL,
         "logo": {"@type": "ImageObject", "url": ASSET + "/assets/logo-512.png", "width": 512, "height": 512},
         "description": "Interview preparation for individuals and practical workplace training for organizations, "
                        "grounded in more than 15 years of MNC banking and regional corporate operations.",
         "founder": {"@id": PERSON_ID}, "areaServed": {"@type": "Country", "name": "Malaysia"},
         "sameAs": [THREADS],
         "knowsAbout": ["Interview preparation", "Resume writing", "Workplace communication",
                        "Corporate training", "Leadership development", "Hiring"]},
        {"@type": "Person", "@id": PERSON_ID, "name": "Ferhan Johar", "jobTitle": "Founder",
         "worksFor": {"@id": ORG_ID}, "url": SITE + "/about", "sameAs": [THREADS],
         "description": "Founder of Bold Shift Advisory with more than 15 years in MNC banking and regional "
                        "corporate operations, leading teams, hiring and developing people."},
        {"@type": "WebSite", "@id": WEBSITE_ID, "name": "Bold Shift Advisory", "url": SITE + "/",
         "publisher": {"@id": ORG_ID}, "inLanguage": "en-MY"},
    ]


def crumbs_ld(path, name):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": SITE + path}]}


def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}}
        for q, a in items]}


# ------------------------------------------------------------------ chrome
def header(path):
    links = "".join(f'<a href="{h}"{" aria-current=page" if h == path else ""}>{t}</a>' for h, t in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="wrap hdr">
<a class="brand" href="/"><span class="mk" aria-hidden="true">BS</span><span class="rule" aria-hidden="true"></span><span class="wm"><span>Bold Shift</span> <span>Advisory</span></span></a>
<div class="hdr-r">
<div class="hdr-top"><a class="hdr-title" href="/">Interview &amp; Workplace Learning</a><a class="hdr-cta" href="/contact">Get in touch</a>
<button class="menu-btn" type="button" aria-controls="nav" aria-expanded="false" aria-label="Open menu"><span></span><span></span><span></span></button></div>
<nav class="nav" id="nav" aria-label="Main">{links}<a class="nav-cta" href="/contact">Get in touch</a></nav>
</div>
</header>'''


def footer():
    return f'''<footer class="ftr"><div class="wrap">
<div class="ftr-grid">
<div><a class="wm" href="/"><span>Bold Shift</span> <span>Advisory</span></a></div>
<div><address>Bold Shift Advisory Sdn Bhd<br>Malaysia<br><a class="ul" href="mailto:{EMAIL}">{EMAIL}</a></address></div>
<ul class="links"><li><a href="{LIVE}/interviewprepared">Interview Ready Guide</a></li><li><a href="{LIVE}/resume-review">Resume Review</a></li><li><a href="{LIVE}/coaching">Interview Coaching</a></li><li><a href="/free-tools">Free Tools</a></li></ul>
<div><ul class="links"><li><a href="/corporate-training">Corporate Training</a></li><li><a href="{LIVE}/proposal">Request a Proposal</a></li><li><a href="{LIVE}/workshops">Workshops</a></li><li><a href="/about">About Ferhan</a></li></ul>
<div class="soc"><a href="{THREADS}" rel="me noopener" aria-label="Ferhan on Threads">{THREADS_ICON}</a></div></div>
</div>
<div class="ftr-base"><span class="grow">© {datetime.date.today().year} Bold Shift Advisory Sdn Bhd. Experiences and views are personal and do not represent any employer.</span>
<a href="/contact">Contact</a><a href="/about">About</a><span>Redesign concept</span></div>
</div></footer>'''


def page(path, title, desc, body, graph_extra=(), og_type="website", preload=None):
    url = SITE + ("/" if path == "/" else path)
    graph = base_graph() + [
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title, "description": desc,
         "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": ORG_ID}, "inLanguage": "en-MY",
         "primaryImageOfPage": {"@type": "ImageObject", "url": ASSET + "/assets/og.png"},
         "dateModified": TODAY}] + list(graph_extra)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    ld = ld.replace("</", "<\\/")
    pre = ""
    if preload:
        n, sizes = preload
        pre = (f'<link rel="preload" as="image" type="image/webp" imagesrcset="/assets/photos/{n}-800.webp 800w, '
               f'/assets/photos/{n}-1600.webp 1600w" imagesizes="{sizes}" fetchpriority="high">\n')
    return f'''<!doctype html>
<html lang="en-MY">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#a3123a">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Bold Shift Advisory">
<meta property="og:locale" content="en_MY">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ASSET}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Bold Shift Advisory: Build capability. Earn trust. Make your work count.">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
{pre}<link rel="stylesheet" href="/assets/site.css?v={CSS_V}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script>{INLINE_JS}</script>
<script type="application/ld+json">{ld}</script>
<script src="/assets/site.js?v={JS_V}" defer></script>
</head>
<body>
{body}
{footer()}
</body>
</html>
'''


def crumbs(name):
    return (f'<nav class="wrap crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li>'
            f'<li aria-current="page">{name}</li></ol></nav>')


def inner(path, crumb, h1, lede, photo, alt, btns="", rest=""):
    """Inner page: crimson masthead + headline, wide photo, breadcrumb bar, content."""
    return f'''<div class="mast">{header(path)}
<div class="wrap hero hero-in"><h1 class="display sm">{h1}</h1><p class="hero-lede">{lede}</p>{btns}</div></div>
<main id="main">
<div class="wrap wide-ph">{ph(photo, alt, "(min-width: 1366px) 1312px, 100vw", eager=True)}</div>
{crumbs(crumb)}
{rest}
</main>'''


def faq_html(items, heading="Common questions"):
    rows = "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in items)
    return f'''<section class="sec white" aria-labelledby="faq-h"><div class="wrap split">
<div><h2 class="h2" id="faq-h">{heading}</h2></div>
<div class="faq rv">{rows}</div></div></section>'''


def cta(h="What would you like to work on?",
        p="Tell us what your team needs, ask about an upcoming session or find the right place to start."):
    return f'''<section class="cta" aria-labelledby="cta-h"><div class="wrap cta-in">
<div><h2 class="h2" id="cta-h">{h}</h2><p>{p}</p></div>
<p class="btns"><a class="btn btn-white" href="/contact">Get in touch {ARROW}</a></p>
</div></section>'''


def pcard(photo, alt, title, url, desc, price, sub):
    return f'''<article class="pcard rv"><div class="ph">{ph(photo, alt)}</div>
<h3 class="h3"><a href="{url}">{title}</a></h3><p>{desc}</p>
<p class="price">{price} <span>· {sub}</span></p></article>'''


# ------------------------------------------------------------------ pages
HOME_FAQ = [
    ("Who is Bold Shift Advisory for?",
     "Graduates, young professionals and aspiring managers preparing for interviews, and organizations that want "
     "practical workplace training for their people. It is founded and run by Ferhan Johar."),
    ("What does Ferhan's experience cover?",
     "More than 15 years across MNC banking and regional corporate operations, including leading teams, hiring and "
     "developing people. The teaching draws on that hiring-side perspective."),
    ("How much is the Interview Ready Guide?",
     "RM20. It is a 61-page PDF, emailed to you after payment."),
    ("Is the corporate training HRDC claimable?",
     "Not confirmed yet. Ferhan's HRDC accreditation process is in progress, and program availability and any "
     "claimable status will be confirmed before booking."),
    ("Are the free tools really free?",
     "Yes. The interview preparation checklist and the Interview Companion are free with no account needed, and "
     "your preparation stays in your browser on your device."),
]

GOALS = [("Understand what interviewers look for", f"{LIVE}/interviewprepared"),
         ("Strengthen my resume", f"{LIVE}/resume-review"),
         ("Practice with personal feedback", f"{LIVE}/coaching#interest"),
         ("Start preparing for free", "/free-tools"),
         ("Develop my team", "/corporate-training")]
ROLES = ["A graduate", "A young professional", "An aspiring manager", "An HR or L&amp;D lead", "A business owner"]


def home():
    strip_sizes = "(min-width: 760px) 50vw, 100vw"
    finder_roles = "".join(f"<option>{r}</option>" for r in ROLES)
    finder_goals = "".join(f'<option data-url="{u}">{g}</option>' for g, u in GOALS)
    body = f'''<div class="mast">{header("/")}
<div class="wrap hero">
<h1 class="display">Build capability. Earn trust. Make your work count.</h1>
<p class="hero-lede">Practical preparation for individuals and learning for organizations, grounded in more than 15 years of MNC banking and regional corporate operations.</p>
<div class="strip">
<figure>{ph("interview", "An interviewer reviews a candidate's answers across a desk", "(min-width: 760px) 25vw, 1px")}</figure>
<figure class="wide">{ph("kl-sunset", "Kuala Lumpur skyline at sunset", strip_sizes, eager=True)}</figure>
<figure>{ph("training", "A facilitator leads a workplace training session", "(min-width: 760px) 25vw, 1px")}</figure>
</div></div></div>
<main id="main">
<div class="wrap crumbs" aria-label="At a glance"><ul class="creds"><li>By Ferhan Johar</li><li>15+ years in MNC banking &amp; regional operations</li><li>The hiring-side perspective</li><li>Malaysia</li></ul></div>

<section class="sec sec-tight" aria-labelledby="prog-h"><div class="wrap">
<h2 class="h2" id="prog-h">Find the support that fits where you are today</h2>
<div class="pgrid">
{pcard("hero-portrait", "A confident young professional smiling in a modern office", "Interview Ready Guide", f"{LIVE}/interviewprepared",
       "A hiring manager’s view of what makes an answer convincing, and how to structure yours with purpose.", "RM20", "61-page PDF")}
{pcard("resume", "A hiring manager reads a printed resume", "Resume Review &amp; Editing", f"{LIVE}/resume-review",
       "Uncover the scope, responsibility and results behind your tasks, edited into specific, credible statements.", "RM59", "One target role")}
{pcard("coaching", "Two colleagues in a one-to-one conversation", "Personal Interview Coaching", f"{LIVE}/coaching#interest",
       "Find out how your answers land and what to improve, then practice applying the feedback.", "By enquiry", "Personal")}
{pcard("boardroom", "A team in a boardroom listening to a presenter", "Corporate Training", "/corporate-training",
       "Training that connects workplace expectations with the communication, judgment and ownership to meet them.", "In-house", "In development")}
</div>
<div class="finder rv">
<h2 class="h2-lite">Find your starting point. <span>Tell us where you are.</span></h2>
<form id="finder" action="/individuals" method="get">
<label><span class="sr">I am</span><select name="role">{finder_roles}</select></label>
<label><span class="sr">I want to</span><select name="goal">{finder_goals}</select></label>
<button class="btn btn-red" type="submit">Find support {ARROW}</button>
</form>
<p class="alt">Prefer to talk it through? <a class="ul" href="/contact">Send Ferhan a note</a>.</p>
</div>
</div></section>

<section class="sec white" aria-labelledby="why-h"><div class="wrap">
<span class="label">Why learn with Ferhan</span>
<h2 class="h2" id="why-h">Experience that shapes how I teach</h2>
<div class="fgrid">
{ph("kl-towers", "The Petronas Twin Towers rising over Kuala Lumpur", "(min-width: 900px) 250px, 100vw")}
<div class="feats">
<div class="feat rv"><h3 class="h3">The hiring-side perspective</h3><p>I’ve sat in both chairs: the candidate trying to be understood, and the manager trying to understand what someone can bring.</p></div>
<div class="feat rv"><h3 class="h3">Grounded in real operations</h3><p>More than 15 years leading teams, developing people and managing pressure across MNC banking and regional corporate operations.</p></div>
<div class="feat rv"><h3 class="h3">Practical, not textbook</h3><p>Capability is how people communicate, think, decide, handle pressure, explain their work and build trust with the people around them.</p></div>
<div class="feat rv"><h3 class="h3">Direct and human</h3><p>I struggled with grades, English and confidence earlier in life. I know what it feels like to be underestimated, and what it takes to become someone others rely on.</p></div>
</div></div>
<p class="btns mt"><a class="btn btn-line" href="/about">About Ferhan {ARROW}</a></p>
</div></section>

<section class="sec" aria-labelledby="ideas-h"><div class="wrap">
<span class="label">In Ferhan’s words</span>
<h2 class="sr" id="ideas-h">In Ferhan’s words</h2>
<div class="stories">
<figure class="story rv">{ph("presenting", "A professional presents a chart to colleagues", "(min-width: 800px) 50vw, 100vw")}
<blockquote>“In real workplaces, capability is not only technical knowledge.”</blockquote>
<figcaption>Ferhan Johar, Founder · <a class="ul" href="/corporate-training">Corporate training</a></figcaption></figure>
<figure class="story rv">{ph("team-skyline", "A team works together in a high-rise office", "(min-width: 800px) 50vw, 100vw")}
<blockquote>“Understand what matters to the person assessing you, make your contribution clear, and practice explaining it in your own words.”</blockquote>
<figcaption>Ferhan Johar, Founder · <a class="ul" href="/individuals">For individuals</a></figcaption></figure>
</div></div></section>

<section class="black band" aria-labelledby="free-h"><div class="wrap"><div class="frame">
{ph("kl-night", "Kuala Lumpur city lights at night", "(min-width: 1366px) 1312px, 100vw", cls="bimg")}
<div class="card"><span class="label">Free tools · No account needed</span>
<h2 class="h3" id="free-h">Start preparing with what you have</h2>
<p>An interview preparation checklist and an Interview Companion to build your Evidence Bank. Your preparation stays in your browser, on your device.</p>
<a class="more" href="/free-tools">Explore the free tools {ARROW}</a></div>
</div></div></section>

{faq_html(HOME_FAQ)}
{cta()}
</main>'''
    return page("/", "Bold Shift Advisory | Interview Prep & Corporate Training",
                "Interview preparation for individuals and practical training for organizations, from Ferhan Johar, "
                "15+ years on the hiring side in MNC banking.",
                body, [faq_ld(HOME_FAQ)], preload=("kl-sunset", strip_sizes))


IND_FAQ = [
    ("How is the Interview Ready Guide delivered?", "It is a 61-page PDF, emailed to you after payment. The price is RM20."),
    ("What do I get with the resume review?",
     "For RM59, Ferhan reviews your resume for one target role and personally edits it into specific, credible "
     "statements. You receive edited Word and PDF files by email, and the guide is included."),
    ("How much does personal interview coaching cost?",
     "Coaching is by enquiry. Scope, availability and fees are shared personally after you explain what you are preparing for."),
    ("Do I need an account for the free tools?",
     "No. The checklist and the Interview Companion are free with no account. Your preparation stays in your browser on your device."),
]
WIDE = "(min-width: 1366px) 1312px, 100vw"


def individuals():
    offers = [
        ("hero-portrait", "A confident young professional in a modern office", "Understand the interview", "Interview Ready Guide",
         "Understand what hiring managers look for. Get my perspective as a hiring manager on what makes an answer convincing, then learn to structure your answers and approach your interview with purpose.",
         ["Understand how your answers are assessed.", "Connect your experience to what the role needs."],
         "RM20", "61-page PDF · Emailed after payment", f"{LIVE}/interviewprepared", "Explore the guide"),
        ("resume", "A hiring manager reads a printed resume", "Strengthen your resume", "Resume Review &amp; Editing",
         "Show the contribution behind your everyday work. I uncover the scope, responsibility and results behind your tasks, then personally edit your resume into specific, credible statements.",
         ["Make your contribution tangible and measurable where the facts support it.", "Receive edited Word and PDF files. Guide included."],
         "RM59", "One target role · Everything by email", f"{LIVE}/resume-review", "See the resume service"),
        ("coaching", "Two colleagues in a one-to-one conversation", "Practice with feedback", "Personal Interview Coaching",
         "Find out how your answers land, and what to improve. Tell me what you are preparing for and we can discuss the support that fits your situation.",
         ["Get direct feedback on how you answer.", "Practice applying that feedback with me."],
         "By enquiry", "Scope, availability and fees shared personally", f"{LIVE}/coaching#interest", "Enquire about coaching"),
    ]
    cards = "".join(f'''<article class="offer rv"><div class="ph">{ph(p, a, "(min-width: 1000px) 33vw, 100vw")}</div><div class="in">
<span class="kick">{k}</span><h3 class="h3">{t}</h3><p>{d}</p><ul class="ticks">{"".join(f"<li>{b}</li>" for b in bl)}</ul>
<div class="price"><b>{pr}</b><span>{ps}</span></div><a class="more" href="{u}">{c} {ARROW}</a></div></article>'''
                    for p, a, k, t, d, bl, pr, ps, u, c in offers)
    rest = f'''<section class="sec sec-tight" id="offers" aria-labelledby="off-h"><div class="wrap">
<h2 class="h2" id="off-h">What would help you move forward?</h2>
<p class="lede">Choose the support that fits your next step.</p>
<div class="offers mt">{cards}</div></div></section>
<section class="sec white" aria-labelledby="chairs-h"><div class="wrap split">
<div class="mono-card rv" aria-hidden="true"><b>FJ</b><span>Ferhan Johar<small>Founder · @ferhanafterhours</small></span></div>
<div class="rv"><span class="label">The experience behind the offers</span><h2 class="h2" id="chairs-h">I’ve sat in both chairs.</h2>
<p class="pull">The candidate trying to be understood. The manager trying to understand what someone can bring.</p>
<div class="prose"><p>I’ve spent more than 15 years in banking and corporate operations, hiring, leading teams and developing people. I also know what it feels like to struggle with English and confidence early in a career.</p>
<p>That experience shapes how I help: understand what matters to the person assessing you, make your contribution clear and practice explaining it in your own words.</p></div>
<a class="more" href="/about">More about Ferhan {ARROW}</a></div></div></section>
<section class="sec" aria-labelledby="free-h"><div class="wrap">
<span class="label">A free starting point</span><h2 class="h2" id="free-h">Start with what you have.</h2>
<p class="lede">Use the checklist for practical preparation and the Companion to organize your examples. Both are free, with no account needed.</p>
<div class="duo mt">
<article class="box rv"><div class="ph">{ph("laptop-duo", "Two professionals working through a laptop together", "(min-width: 800px) 50vw, 100vw")}</div><div class="in"><h3 class="h3">Interview preparation checklist</h3><p>Research, documents, travel, technology and mindset, adapted for physical, online or hybrid interviews.</p><a class="more" href="{LIVE}/checklist">Use the free checklist {ARROW}</a></div></article>
<article class="box rv"><div class="ph">{ph("collab", "Colleagues collaborating on a laptop in an office", "(min-width: 800px) 50vw, 100vw")}</div><div class="in"><h3 class="h3">Interview Companion</h3><p>Build your Evidence Bank, connect stories to the role and record what you learn after each interview.</p><a class="more" href="{LIVE}/companion/">Build your Evidence Bank {ARROW}</a></div></article>
</div></div></section>
{faq_html(IND_FAQ)}
{cta("Not sure which fits you?", "Tell Ferhan what you are preparing for and he will point you to the right place to start.")}'''
    body = inner("/individuals", "For Individuals", "Understand the hiring side. Make your experience count.",
                 "Learn what a hiring manager listens for, turn everyday work into a stronger resume, and get personal feedback on how you interview.",
                 "interview", "An interviewer listens to a candidate across a desk",
                 f'<p class="btns"><a class="btn btn-white" href="#offers">Find the help you need {ARROW}</a></p>', rest)
    extra = [crumbs_ld("/individuals", "For individuals"), faq_ld(IND_FAQ),
             {"@type": "Product", "name": "Interview Ready Guide (The Other Side of the Table)",
              "description": "A 61-page PDF guide on what hiring managers look for in an interview and how to structure convincing answers.",
              "brand": {"@id": ORG_ID}, "url": f"{LIVE}/interviewprepared", "image": ASSET + "/assets/og.png",
              "offers": {"@type": "Offer", "price": "20.00", "priceCurrency": "MYR", "availability": "https://schema.org/InStock",
                         "url": f"{LIVE}/interviewprepared", "seller": {"@id": ORG_ID}}},
             {"@type": "Service", "name": "Resume Review & Editing", "serviceType": "Resume editing",
              "provider": {"@id": ORG_ID}, "areaServed": "MY", "url": f"{LIVE}/resume-review",
              "offers": {"@type": "Offer", "price": "59.00", "priceCurrency": "MYR", "url": f"{LIVE}/resume-review"}},
             {"@type": "Service", "name": "Personal Interview Coaching", "serviceType": "Interview coaching",
              "provider": {"@id": ORG_ID}, "areaServed": "MY", "url": f"{LIVE}/coaching"}]
    return page("/individuals", "Interview Prep & Resume Review | Bold Shift Advisory",
                "Interview Ready Guide (RM20), resume review and editing (RM59) and interview coaching from a hiring "
                "manager with 15+ years in banking.", body, extra, preload=("interview", WIDE))


CORP_FAQ = [
    ("What kind of training does Bold Shift Advisory offer organizations?",
     "Training shaped around how people communicate, think, decide and deliver at work, grounded in Ferhan's "
     "operational experience in MNC banking and regional corporate operations."),
    ("Are there in-house programs and public courses?",
     "The program offering is being developed. You can contact Bold Shift Advisory to discuss your requirements or "
     "register interest in future course announcements."),
    ("Is the training HRDC claimable?",
     "Not confirmed yet. Ferhan's HRDC accreditation process is in progress; program availability and any applicable "
     "claimable status will be confirmed before booking."),
    ("How does a training discussion start?",
     "With your workplace: who the participants are, which situations they find difficult, what better performance "
     "would look like, and your timing and delivery requirements."),
]


def corporate():
    rest = f'''<section class="sec sec-tight" aria-labelledby="change-h"><div class="wrap split">
<div><span class="label">Start with the workplace</span><h2 class="h2" id="change-h">What needs to change after the training?</h2></div>
<div class="prose rv"><p>That is where the conversation starts. Who are the participants? What situations do they find difficult? What would better performance look like?</p>
<p>Program scope and delivery can then be discussed against the needs of your organization.</p>
<h3 class="h3 mt">A practical discussion covers</h3>
<ul class="ticks"><li>Your participants and their responsibilities.</li><li>The behaviors or capabilities you want to develop.</li><li>The workplace situations the learning must address.</li><li>Your intended timing and delivery requirements.</li></ul></div>
</div></section>
<section class="sec white" aria-labelledby="why-h"><div class="wrap">
<span class="label">The trainer</span><h2 class="h2" id="why-h">Grounded in operational experience</h2>
<div class="feats mt">
<div class="feat rv"><h3 class="h3">15+ years</h3><p>MNC banking and regional corporate operations.</p></div>
<div class="feat rv"><h3 class="h3">Senior leadership</h3><p>Leading teams, developing people and managing pressure.</p></div>
<div class="feat rv"><h3 class="h3">The hiring side</h3><p>Knows what workplaces expect from people, because he has hired for it.</p></div>
<div class="feat rv"><h3 class="h3">Real situations</h3><p>Communication, judgment and ownership, taught against the work your people actually do.</p></div>
</div></div></section>
<section class="sec" aria-labelledby="prog-h"><div class="wrap">
<span class="label">Program development</span><h2 class="h2" id="prog-h">In-house training &amp; public courses</h2>
<div class="duo mt">
<article class="box rv"><div class="ph">{ph("boardroom", "A team in a boardroom listening to a presenter", "(min-width: 800px) 50vw, 100vw")}</div><div class="in"><h3 class="h3">Programs in development</h3><p>The program offering is being developed. Contact us to discuss your requirements or register interest in future course announcements.</p><a class="more" href="{LIVE}/proposal">Start a conversation {ARROW}</a></div></article>
<article class="box rv"><div class="ph">{ph("presenting", "A professional presents a chart to colleagues", "(min-width: 800px) 50vw, 100vw")}</div><div class="in"><h3 class="h3">Accreditation status</h3><p>Ferhan’s HRDC accreditation process is in progress. Program availability and any applicable claimable status will be confirmed before booking.</p><a class="more" href="/contact">Ask a question {ARROW}</a></div></article>
</div></div></section>
{faq_html(CORP_FAQ)}
{cta("Let’s talk about your team.", "Share who your participants are and what you want to develop. Scope and delivery follow from there.")}'''
    body = inner("/corporate-training", "Corporate Training", "Build the capabilities your workplace needs.",
                 "Training grounded in operational experience, shaped around how people communicate, think, decide and deliver at work.",
                 "training", "A facilitator leads a workplace training session",
                 f'<p class="btns"><a class="btn btn-white" href="{LIVE}/proposal">Discuss your training needs {ARROW}</a></p>', rest)
    extra = [crumbs_ld("/corporate-training", "Corporate training"), faq_ld(CORP_FAQ),
             {"@type": "Service", "name": "Corporate training", "serviceType": "Corporate workplace training",
              "provider": {"@id": ORG_ID}, "areaServed": "MY", "audience": {"@type": "BusinessAudience"},
              "url": SITE + "/corporate-training"}]
    return page("/corporate-training", "Corporate Training in Malaysia | Bold Shift Advisory",
                "Workplace training on communication, judgment and ownership, grounded in 15+ years of MNC banking and "
                "regional corporate operations.", body, extra, preload=("training", WIDE))


def about():
    rest = f'''<section class="sec sec-tight" aria-labelledby="me-h"><div class="wrap split">
<div class="mono-card rv" aria-hidden="true"><b>FJ</b><span>Ferhan Johar<small>Founder, Bold Shift Advisory</small></span></div>
<div class="prose rv"><span class="label">About me</span><h2 class="h2" id="me-h">Practical, direct and human.</h2>
<p>I’m Ferhan Johar, founder of Bold Shift Advisory.</p>
<p>For more than 15 years, I’ve worked across MNC banking and regional corporate operations, leading teams, developing people, managing pressure, and seeing what separates people who are merely busy from people who are trusted to deliver.</p>
<p>That experience shaped the way I teach. In real workplaces, capability is not only technical knowledge. It is how people communicate, think, decide, handle pressure, explain their work, use tools, and build trust with the people around them.</p>
<p>Bold Shift Advisory was built to help organizations develop those practical capabilities through training that is grounded in real operational experience, not textbook theory.</p>
<p>My own path was not perfect. I struggled with grades, English and confidence earlier in life. That is why my work is direct, practical and human. I know what it feels like to be underestimated, and I also know what it takes to become someone others can rely on.</p></div>
</div></section>
<section class="sec white" aria-labelledby="ways-h"><div class="wrap">
<span class="label">One perspective</span><h2 class="h2" id="ways-h">Different ways to learn</h2>
<div class="duo mt">
<article class="box rv"><div class="ph">{ph("coaching", "Two colleagues in a one-to-one conversation", "(min-width: 800px) 50vw, 100vw")}</div><div class="in"><h3 class="h3">Ferhanafterhours @ Threads</h3><p>Practical lessons and conversations for graduates, juniors and young professionals on interviews, communication, confidence and workplace growth.</p><a class="more" href="{THREADS}" rel="me noopener">Follow on Threads {ARROW}</a></div></article>
<article class="box rv"><div class="ph">{ph("team-skyline", "A team works together in a high-rise office", "(min-width: 800px) 50vw, 100vw")}</div><div class="in"><h3 class="h3">Bold Shift Advisory</h3><p>The home for the guide, free tools, upcoming workshops, coaching and organizational training.</p><a class="more" href="/free-tools">Start with the free tools {ARROW}</a></div></article>
</div>
<p class="muted mt">Experiences and views are personal and do not represent any employer.</p>
</div></section>
{cta()}'''
    body = inner("/about", "About Ferhan", "I’ve sat in both chairs.",
                 "The candidate trying to be understood. The manager trying to understand what someone can bring.",
                 "kl-sunset", "Kuala Lumpur skyline at sunset", "", rest)
    extra = [crumbs_ld("/about", "About"),
             {"@type": "ProfilePage", "@id": SITE + "/about#profile", "url": SITE + "/about", "mainEntity": {"@id": PERSON_ID}}]
    return page("/about", "About Ferhan Johar, Founder | Bold Shift Advisory",
                "Ferhan Johar spent 15+ years in MNC banking and regional corporate operations, hiring, leading teams and "
                "developing people. This is his story.", body, extra, og_type="profile", preload=("kl-sunset", WIDE))


def free_tools():
    rest = f'''<section class="sec sec-tight" aria-labelledby="tools-h"><div class="wrap">
<h2 class="h2" id="tools-h">Two tools, both free</h2>
<div class="duo mt">
<article class="box rv"><div class="ph">{ph("resume", "A hiring manager reads a printed resume", "(min-width: 800px) 50vw, 100vw")}</div><div class="in"><span class="kick">01 · Get the practical details right</span><h3 class="h3">Interview preparation checklist</h3>
<p>Research, documents, travel, technology and mindset. Adapt your checklist for a physical, online or hybrid interview.</p>
<div class="chips"><span>Read the job description</span><span>Confirm the location or meeting link</span><span>Prepare questions for the interviewer</span></div>
<a class="more" href="{LIVE}/checklist">Use the free checklist {ARROW}</a></div></article>
<article class="box rv"><div class="ph">{ph("collab", "Colleagues collaborating on a laptop in an office", "(min-width: 800px) 50vw, 100vw")}</div><div class="in"><span class="kick">02 · Prepare what you want to say</span><h3 class="h3">Interactive Companion</h3>
<p>Build your Evidence Bank, connect stories to the role and record what you learn after each interview.</p>
<div class="chips"><span>Communication</span><span>Accountability</span><span>Learning</span></div>
<a class="more" href="{LIVE}/companion/">Build your Evidence Bank {ARROW}</a></div></article>
</div>
<p class="note rv">Your preparation stays in your browser on your device. Use the Companion’s backup feature before switching devices or clearing browser data.</p>
</div></section>
<section class="sec white" aria-labelledby="guide-h"><div class="wrap split">
<div><span class="label">Go further</span><h2 class="h2" id="guide-h">The tools give you somewhere to prepare.</h2></div>
<div class="prose rv"><p>The guide explains how to find relevant evidence and turn it into a clear conversation.</p>
<a class="btn btn-red" href="{LIVE}/interviewprepared">Explore The Other Side of the Table · RM20 {ARROW}</a></div>
</div></section>'''
    body = inner("/free-tools", "Free Tools", "Start preparing. Start here, free.",
                 "Practical tools to organize the details, find your evidence and arrive ready for the conversation.",
                 "laptop-duo", "Two professionals working through a laptop together", "", rest)
    extra = [crumbs_ld("/free-tools", "Free tools"),
             {"@type": "ItemList", "name": "Free interview preparation tools", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Interview preparation checklist", "url": f"{LIVE}/checklist"},
                 {"@type": "ListItem", "position": 2, "name": "Interview Companion", "url": f"{LIVE}/companion/"}]}]
    return page("/free-tools", "Free Interview Preparation Tools | Bold Shift Advisory",
                "A free interview preparation checklist and an Interview Companion to build your Evidence Bank. No "
                "account needed; your preparation stays on your device.", body, extra, preload=("laptop-duo", WIDE))


def contact():
    routes = [(f"{LIVE}/proposal", "Corporate training inquiry?"), (f"{LIVE}/workshops", "Looking for the workshops?"),
              (f"{LIVE}/coaching", "Interested in 1-to-1 coaching?"), (f"{LIVE}/interviewprepared", "Looking for the interview guide?")]
    r = "".join(f'<a href="{u}">{t}{ARROW}</a>' for u, t in routes)
    opts = ["General inquiry", "Corporate training inquiry", "Public course interest", "Workshop inquiry",
            "Coaching inquiry", "Existing purchase support"]
    rest = f'''<section class="sec sec-tight" aria-labelledby="c-h"><div class="wrap split">
<div class="rv"><h2 class="h2" id="c-h">A useful first conversation.</h2>
<p class="lede">Tell us who you are, what you are working towards and where you would like support.</p>
<p><a class="email-big" href="mailto:{EMAIL}">{EMAIL}</a></p>
<p>Bold Shift Advisory Sdn Bhd<br>Ferhan Johar · <a class="ul" href="{THREADS}" rel="me noopener">Ferhanafterhours @ Threads</a></p>
<div class="routes">{r}</div></div>
<form class="form rv" id="enquiry" action="mailto:{EMAIL}" method="post" enctype="text/plain">
<label>Your name<input name="name" autocomplete="name" required></label>
<label>Email address<input name="email" type="email" autocomplete="email" required></label>
<label>What is this about?<select name="topic">{"".join(f"<option>{o}</option>" for o in opts)}</select></label>
<label>Organization, if relevant<input name="org" autocomplete="organization"></label>
<label>How can we help?<textarea name="message" required></textarea></label>
<button class="btn btn-red" type="submit">Send inquiry {ARROW}</button>
<small>Opens your email app with your message ready to send. These details are only used to respond to your inquiry.</small>
</form>
</div></section>'''
    body = inner("/contact", "Contact", "Let’s understand what you need.",
                 "For individual support, corporate training or general inquiries, start here.",
                 "kl-towers", "The Petronas Twin Towers rising over Kuala Lumpur", "", rest)
    extra = [crumbs_ld("/contact", "Contact"),
             {"@type": "ContactPage", "@id": SITE + "/contact#contact", "url": SITE + "/contact", "about": {"@id": ORG_ID}}]
    return page("/contact", "Contact Bold Shift Advisory | Ferhan Johar",
                "Contact Bold Shift Advisory for interview support, corporate training, workshops or coaching. Email "
                "ferhanjohar@boldshiftadvisory.com.", body, extra, preload=("kl-towers", WIDE))


def notfound():
    body = f'''<div class="mast">{header("")}
<div class="wrap hero hero-in"><h1 class="display sm">This page moved on.</h1>
<p class="hero-lede">The page you were looking for isn’t here. Try one of these instead.</p>
<p class="btns"><a class="btn btn-white" href="/">Home {ARROW}</a><a class="btn btn-ghost" href="/individuals">For individuals</a><a class="btn btn-ghost" href="/corporate-training">Corporate training</a></p></div></div>
<main id="main"><div class="sec"></div></main>'''
    return page("/404", "Page not found | Bold Shift Advisory", "This page could not be found.", body).replace(
        '<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">')


PAGES = {"index.html": home, "individuals.html": individuals, "corporate-training.html": corporate,
         "about.html": about, "free-tools.html": free_tools, "contact.html": contact, "404.html": notfound}


def main():
    global CSS_V, JS_V
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    shutil.rmtree(OUT / "assets" / "art", ignore_errors=True)
    shutil.copy(ROOT / "src/site.css", OUT / "assets/site.css")
    shutil.copy(ROOT / "src/site.js", OUT / "assets/site.js")
    CSS_V, JS_V = asset_hash(OUT / "assets/site.css"), asset_hash(OUT / "assets/site.js")
    for name, fn in PAGES.items():
        s = fn()
        assert 'style="' not in s, name
        (OUT / name).write_text(s, encoding="utf-8")
    urls = ["/", "/individuals", "/corporate-training", "/about", "/free-tools", "/contact"]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    (OUT / "llms.txt").write_text(f"""# Bold Shift Advisory

> Interview preparation for individuals and practical workplace training for organizations in Malaysia, founded by Ferhan Johar (15+ years in MNC banking and regional corporate operations: leading teams, hiring, developing people). Company: Bold Shift Advisory Sdn Bhd. Contact: {EMAIL}.

## For individuals
- [Interview Ready Guide]({LIVE}/interviewprepared): 61-page PDF, RM20, emailed after payment.
- [Resume Review & Editing]({LIVE}/resume-review): RM59, one target role, edited Word + PDF by email, guide included.
- [Personal Interview Coaching]({LIVE}/coaching): by enquiry.
- [Free tools]({SITE}/free-tools): interview checklist + Interview Companion, free, no account, data stays in the browser.

## For organizations
- [Corporate training]({SITE}/corporate-training): communication, judgment and ownership at work. Programs in development. HRDC accreditation in progress (not yet claimable).

## About
- [About Ferhan Johar]({SITE}/about) · Threads: {THREADS}
""")
    h = base64.b64encode(hashlib.sha256(INLINE_JS.encode()).digest()).decode()
    hdr = (ROOT / "src/_headers").read_text().replace("__INLINE_HASH__", h)
    (OUT / "_headers").write_text(hdr)
    print("built", len(PAGES), "pages ->", OUT, "| SITE", SITE, "| ASSET", ASSET)


if __name__ == "__main__":
    main()
