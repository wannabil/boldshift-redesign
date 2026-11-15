#!/usr/bin/env python3
"""Static site generator for the Bold Shift Advisory redesign concept.

Usage: python3 src/build.py            (writes ./public)
Env:   SITE_URL   canonical origin  (default https://boldshiftadvisory.com)
       ASSET_URL  origin for absolute og:image URLs (default = SITE_URL)
"""
import base64
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import datetime

import art

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
SITE = os.environ.get("SITE_URL", "https://boldshiftadvisory.com").rstrip("/")
ASSET = os.environ.get("ASSET_URL", SITE).rstrip("/")
LIVE = "https://boldshiftadvisory.com"  # deep product pages stay on the live site
TODAY = datetime.date.today().isoformat()
EMAIL = "ferhanjohar@boldshiftadvisory.com"
THREADS = "https://www.threads.com/@ferhanafterhours"

ARROW = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 12h15m-6-6 6 6-6 6" '
         'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
CHEV = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m9 5 7 7-7 7" fill="none" '
        'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
INLINE_JS = "document.documentElement.classList.add('js')"

NAV = [("/individuals", "For individuals"), ("/corporate-training", "Corporate training"),
       ("/free-tools", "Free tools"), ("/about", "About"), ("/contact", "Contact")]

ORG_ID = f"{SITE}/#organization"
PERSON_ID = f"{SITE}/#ferhan"
WEBSITE_ID = f"{SITE}/#website"


ART_DIR = OUT / "assets" / "art"
EAGER = {"h1", "h2"}


def img(svg, name):
    """Write artwork to a cacheable file; return a lazy <img> (decorative, empty alt)."""
    ART_DIR.mkdir(parents=True, exist_ok=True)
    svg = svg.replace('<svg class="art" ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    (ART_DIR / f"{name}.svg").write_text(svg, encoding="utf-8")
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    w, h = m.group(1), m.group(2)
    load = 'fetchpriority="high"' if name in EAGER else 'loading="lazy"'
    v = hashlib.sha256(svg.encode()).hexdigest()[:8]
    return (f'<img class="art" src="/assets/art/{name}.svg?v={v}" alt="" width="{w}" height="{h}" '
            f'{load} decoding="async">')


def e(s):
    return html.escape(s, quote=True)


def asset_hash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:10]


def base_graph():
    return [
        {"@type": "Organization", "@id": ORG_ID, "name": "Bold Shift Advisory",
         "legalName": "Bold Shift Advisory Sdn Bhd", "url": SITE + "/", "email": EMAIL,
         "logo": {"@type": "ImageObject", "url": ASSET + "/assets/logo-512.png", "width": 512, "height": 512},
         "description": "Interview preparation for individuals and practical workplace training for organizations, "
                        "grounded in more than 15 years of MNC banking and regional corporate operations.",
         "founder": {"@id": PERSON_ID}, "areaServed": {"@type": "Country", "name": "Malaysia"},
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


def faq_html(items, heading="Common questions"):
    rows = "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in items)
    return f'''<section class="sec" aria-labelledby="faq-h"><div class="wrap split">
<div><span class="eyebrow">FAQ</span><h2 class="h2" id="faq-h">{heading}</h2></div>
<div class="faq rv">{rows}</div></div></section>'''


def header(path):
    links = "".join(f'<a href="{h}"{" aria-current=page" if h == path else ""}>{t}</a>' for h, t in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="hdr"><div class="wrap">
<a class="brand" href="/"><span>Bold Shift</span> <span>Advisory</span></a>
<nav class="nav" id="nav" aria-label="Main">{links}<a class="nav-cta" href="/contact">Get in touch →</a></nav>
<a class="hdr-cta" href="/contact">Get in touch</a>
<button class="menu-btn" type="button" aria-controls="nav" aria-expanded="false" aria-label="Open menu"><span></span><span></span><span></span></button>
</div></header>'''


def footer():
    return f'''<footer class="ftr"><div class="wrap">
<div class="ftr-grid">
<div><a class="brand" href="/"><span>Bold Shift</span> <span>Advisory</span></a>
<p>Practical preparation for individuals and learning for organizations, by Ferhan Johar.</p>
<p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<div><h2>Individuals</h2><ul>
<li><a href="{LIVE}/interviewprepared">Interview Ready Guide</a></li>
<li><a href="{LIVE}/resume-review">Resume review</a></li>
<li><a href="{LIVE}/coaching">Interview coaching</a></li>
<li><a href="/free-tools">Free tools</a></li></ul></div>
<div><h2>Organizations</h2><ul>
<li><a href="/corporate-training">Corporate training</a></li>
<li><a href="{LIVE}/proposal">Request a proposal</a></li>
<li><a href="{LIVE}/workshops">Workshops</a></li></ul></div>
<div><h2>Company</h2><ul>
<li><a href="/about">About Ferhan</a></li>
<li><a href="/contact">Contact</a></li>
<li><a href="{THREADS}" rel="me noopener">Threads @ferhanafterhours</a></li></ul></div>
</div>
<div class="ftr-base"><span>© {datetime.date.today().year} Bold Shift Advisory Sdn Bhd. Experiences and views are personal and do not represent any employer.</span>
<span>Redesign concept preview</span></div>
</div></footer>'''


def page(path, title, desc, body, graph_extra=(), og_type="website"):
    url = SITE + ("/" if path == "/" else path)
    graph = base_graph() + [
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title, "description": desc,
         "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": ORG_ID}, "inLanguage": "en-MY",
         "dateModified": TODAY}] + list(graph_extra)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    ld = ld.replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="en-MY">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#051c2c">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Bold Shift Advisory">
<meta property="og:locale" content="en_MY">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ASSET}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Bold Shift Advisory — Build capability. Earn trust. Make your work count.">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/assets/fonts/caslon-bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={CSS_V}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script>{INLINE_JS}</script>
<script type="application/ld+json">{ld}</script>
<script src="/assets/site.js?v={JS_V}" defer></script>
</head>
<body>
{header(path)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''


def cta_band(h="What would you like <em>to work on?</em>",
             p="Tell us what your team needs, ask about an upcoming session or find the right place to start."):
    return f'''<section class="sec grad cta-band" aria-labelledby="cta-h"><div class="wrap">
<div><h2 class="h2" id="cta-h">{h}</h2><p>{p}</p></div>
<div class="btns"><a class="btn btn-white" href="/contact">Get in touch {ARROW}</a></div>
</div></section>'''


def page_hero(crumb, eyebrow, h1, lede, extra=""):
    nav = ""
    if crumb:
        nav = (f'<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li>'
               f'<li aria-current="page">{crumb}</li></ol></nav>')
    return f'''<section class="dark page-hero"><div class="wrap">
{nav}<span class="eyebrow">{eyebrow}</span>
<h1 class="display stagger">{h1}</h1>
<p class="lede">{lede}</p>{extra}
</div></section>'''


# ---------------------------------------------------------------- pages
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


def home():
    body = f'''<section class="dark hero"><div class="wrap hero-grid">
<div class="hero-copy">
<span class="hero-kicker">Bold Shift Advisory · By Ferhan Johar</span>
<h1 class="display stagger"><span>Build capability.</span> <span><em>Earn trust.</em></span> <span>Make your work count.</span></h1>
<div class="hero-row"><p>Practical preparation for individuals and learning for organizations, grounded in more than 15 years of MNC banking and regional corporate operations.</p>
<a class="circle-arrow" href="#paths" aria-label="See where to start">{ARROW}</a></div>
<div class="btns"><a class="btn btn-blue" href="/individuals">For individuals {ARROW}</a><a class="btn btn-line" href="/corporate-training">For organizations {ARROW}</a></div>
</div>
<div class="hero-cards">
<a class="tile" href="/individuals">{img(art.fan("h1", 7), "h1")}<span class="tag">For individuals</span><span class="t">Prepare for your next step {CHEV}</span></a>
<a class="tile" href="/corporate-training">{img(art.rings("h2", 11, bg="#0b2a42"), "h2")}<span class="tag">Corporate training</span><span class="t">Develop the people you depend on {CHEV}</span></a>
</div>
</div></section>
<section class="dark proof" aria-label="Experience at a glance"><div class="wrap">
<div class="p"><div class="num">15+ years</div><div class="lbl">in MNC banking &amp; regional corporate operations</div></div>
<div class="p"><div class="num">Hiring side</div><div class="lbl">Senior leadership &amp; hiring perspective</div></div>
<div class="p"><div class="num">Malaysia</div><div class="lbl">Grounded in Malaysian workplace realities</div></div>
</div></section>

<section class="sec" id="paths" aria-labelledby="paths-h"><div class="wrap">
<div class="sec-head"><span class="eyebrow">A practical place to start</span><h2 class="h2" id="paths-h">What brings you here?</h2></div>
<div class="paths">
<article class="card rv"><div class="media">{img(art.steps("p1", 3), "p1")}</div><div class="body">
<span class="eyebrow">For individuals</span><h3 class="h3">Prepare for your next step.</h3>
<p>Interview preparation, free tools and upcoming ways to learn with Ferhan. Find the support that fits where you are today.</p>
<a class="arrow-link cover" href="/individuals">Explore guides &amp; support {ARROW}</a></div></article>
<article class="card rv"><div class="media">{img(art.waves("p2", 5), "p2")}</div><div class="body">
<span class="eyebrow">Corporate training</span><h3 class="h3">Develop the people you depend on.</h3>
<p>Explore training that connects workplace expectations with the communication, judgment and ownership needed to meet them.</p>
<a class="arrow-link cover" href="/corporate-training">Explore training {ARROW}</a></div></article>
</div></div></section>

<section class="sec paper" aria-labelledby="founder-h"><div class="wrap founder">
<div class="portrait rv">{img(art.fan("f1", 21, 600, 750), "f1")}<span class="mono" aria-hidden="true">FJ</span><span class="cap">Ferhan Johar · Founder, Bold Shift Advisory</span></div>
<div class="rv"><span class="eyebrow">Meet the founder</span>
<h2 class="h2" id="founder-h">Experience that shapes <em>how I teach.</em></h2>
<p class="quote">“I’ve sat in both chairs: the candidate trying to be understood, and the manager trying to understand what someone can bring.”</p>
<p class="lede">I’m Ferhan Johar. I’ve led teams, developed people and managed pressure across MNC banking and regional corporate operations. Bold Shift Advisory brings that experience into practical learning for the workplace.</p>
<a class="arrow-link" href="/about">About me {ARROW}</a></div>
</div></section>

<section class="sec dark grad-v" aria-labelledby="offers-h"><div class="wrap">
<div class="sec-head"><span class="eyebrow">Three ways I can help</span><h2 class="h2-sans" id="offers-h">What would help you move forward?</h2></div>
<div class="tabset rv">
<div class="panel" id="t1" role="tabpanel" aria-labelledby="b1"><div class="feature">
<div class="fcopy"><span class="eyebrow">01 · Understand the interview</span><h3 class="h3">Interview Ready Guide</h3>
<p>Get a hiring manager’s perspective on what makes an answer convincing, then learn to structure your answers and approach your interview with purpose.</p>
<ul><li>Understand how your answers are assessed.</li><li>Connect your experience to what the role needs.</li></ul>
<div class="price"><b>RM20</b><span>61-page PDF · Emailed after payment</span></div>
<a class="arrow-link" href="{LIVE}/interviewprepared">Explore the guide {ARROW}</a></div>
<div class="fart">{img(art.rings("o1", 4, bg="#0b2a42"), "o1")}</div></div></div>
<div class="panel" id="t2" role="tabpanel" aria-labelledby="b2" hidden><div class="feature">
<div class="fcopy"><span class="eyebrow">02 · Strengthen your resume</span><h3 class="h3">Resume Review &amp; Editing</h3>
<p>I uncover the scope, responsibility and results behind your tasks, then personally edit your resume into specific, credible statements that give your experience more weight.</p>
<ul><li>Make your contribution tangible and measurable where the facts support it.</li><li>Receive edited Word and PDF files. Guide included.</li></ul>
<div class="price"><b>RM59</b><span>One target role · Everything by email</span></div>
<a class="arrow-link" href="{LIVE}/resume-review">See the resume service {ARROW}</a></div>
<div class="fart">{img(art.steps("o2", 8), "o2")}</div></div></div>
<div class="panel" id="t3" role="tabpanel" aria-labelledby="b3" hidden><div class="feature">
<div class="fcopy"><span class="eyebrow">03 · Practice with feedback</span><h3 class="h3">Personal Interview Coaching</h3>
<p>Looking for individual help with an interview? Tell me what you are preparing for, and we can discuss the support that fits your situation.</p>
<ul><li>Get direct feedback on how you answer.</li><li>Practice applying that feedback with me.</li></ul>
<div class="price"><b>By enquiry</b><span>Scope, availability and fees shared personally</span></div>
<a class="arrow-link" href="{LIVE}/coaching#interest">Enquire about interview support {ARROW}</a></div>
<div class="fart">{img(art.waves("o3", 9), "o3")}</div></div></div>
<div class="tabs" role="tablist" aria-label="Ways I can help">
<button role="tab" id="b1" aria-controls="t1" aria-selected="true">Interview Ready Guide<small>RM20 · PDF</small></button>
<button role="tab" id="b2" aria-controls="t2" aria-selected="false" tabindex="-1">Resume Review &amp; Editing<small>RM59 · by email</small></button>
<button role="tab" id="b3" aria-controls="t3" aria-selected="false" tabindex="-1">Personal Interview Coaching<small>By enquiry</small></button>
</div></div>
</div></section>

<section class="sec" aria-labelledby="convo-h"><div class="wrap convo">
<div class="rv"><span class="eyebrow">Ferhanafterhours @ Threads</span>
<h2 class="h2" id="convo-h">Where the conversation starts.</h2>
<p class="lede">Practical lessons for young professionals on interviews, communication, confidence and workplace growth. The guide and free tools turn those conversations into something you can work through.</p>
<div class="btns mt"><a class="btn btn-blue" href="/free-tools">Explore the free tools {ARROW}</a><a class="btn btn-line" href="{THREADS}" rel="me noopener">Follow on Threads</a></div></div>
<div class="convo-card rv"><div class="handle"><i aria-hidden="true">FJ</i><span>@ferhanafterhours</span></div>
<p>Free, no account needed: an interview preparation checklist and an Interview Companion to build your Evidence Bank.</p>
<div class="topics"><span>Interviews</span><span>Communication</span><span>Confidence</span><span>Workplace growth</span></div></div>
</div></section>
{faq_html(HOME_FAQ)}
{cta_band()}'''
    return page("/", "Bold Shift Advisory | Interview Prep & Corporate Training",
                "Interview preparation for individuals and practical training for organizations, from Ferhan Johar, "
                "15+ years on the hiring side in MNC banking.",
                body, [faq_ld(HOME_FAQ)])


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


def individuals():
    offers = [
        ("01", "Understand the interview", "Interview Ready Guide",
         "Understand what hiring managers look for during an interview. Get my perspective as a hiring manager on what makes an answer convincing, then learn to structure your answers and approach your interview with purpose.",
         ["Understand how your answers are assessed.", "Connect your experience to what the role needs."],
         "RM20", "61-page PDF · Emailed after payment", f"{LIVE}/interviewprepared", "Explore the guide"),
        ("02", "Strengthen your resume", "Resume Review &amp; Editing",
         "Show the contribution behind your everyday work. I uncover the scope, responsibility and results behind your tasks, then personally edit your resume into specific, credible statements.",
         ["Make your contribution tangible and measurable where the facts support it.", "Receive edited Word and PDF files. Guide included."],
         "RM59", "One target role · Everything by email", f"{LIVE}/resume-review", "See the resume service"),
        ("03", "Practice with feedback", "Personal Interview Coaching",
         "Find out how your answers land, and what to improve. Tell me what you are preparing for and we can discuss the support that fits your situation.",
         ["Get direct feedback on how you answer.", "Practice applying that feedback with me."],
         "By enquiry", "Scope, availability and fees shared personally", f"{LIVE}/coaching#interest", "Enquire about interview support"),
    ]
    cards = "".join(f'''<article class="offer rv"><span class="n">{n}</span><span class="eyebrow">{k}</span><h3 class="h3">{t}</h3>
<p>{d}</p><ul class="ticks">{"".join(f"<li>{b}</li>" for b in bl)}</ul>
<div class="price"><b>{pr}</b><span>{ps}</span></div><a class="arrow-link" href="{u}">{c} {ARROW}</a></article>'''
                    for n, k, t, d, bl, pr, ps, u, c in offers)
    body = page_hero("For individuals", "For graduates, professionals &amp; aspiring managers",
                     "<span>Understand the hiring side.</span> <span><em>Make your experience count.</em></span>",
                     "Learn what a hiring manager listens for, turn everyday work into a stronger resume, and get personal feedback on how you interview.",
                     f'<p class="btns mt"><a class="btn btn-blue" href="#offers">Find the help you need {ARROW}</a></p>') + f'''
<section class="sec" id="offers" aria-labelledby="off-h"><div class="wrap">
<div class="sec-head"><span class="eyebrow">Three ways I can help</span><h2 class="h2" id="off-h">What would help you move forward?</h2><p class="lede">Choose the support that fits your next step.</p></div>
<div class="offers">{cards}</div></div></section>
<section class="sec paper" aria-labelledby="chairs-h"><div class="wrap founder">
<div class="portrait rv">{img(art.waves("c1", 13, 600, 750), "c1")}<span class="mono" aria-hidden="true">FJ</span><span class="cap">Ferhan Johar · @ferhanafterhours</span></div>
<div class="rv"><span class="eyebrow">The experience behind the offers</span><h2 class="h2" id="chairs-h">I’ve sat in <em>both chairs.</em></h2>
<p class="quote">The candidate trying to be understood. The manager trying to understand what someone can bring.</p>
<div class="prose"><p>I’ve spent more than 15 years in banking and corporate operations, hiring, leading teams and developing people. I also know what it feels like to struggle with English and confidence early in a career.</p>
<p>That experience shapes how I help: understand what matters to the person assessing you, make your contribution clear and practice explaining it in your own words.</p></div>
<a class="arrow-link" href="/about">More about Ferhan {ARROW}</a></div></div></section>
<section class="sec" aria-labelledby="free-h"><div class="wrap">
<div class="sec-head"><span class="eyebrow">A free starting point</span><h2 class="h2" id="free-h">Start with what you have.</h2><p class="lede">Use the checklist for practical preparation and the Companion to organize your examples. Both are free, with no account needed.</p></div>
<div class="duo"><div class="box rv"><h3 class="h3">Interview preparation checklist</h3><p>Research, documents, travel, technology and mindset, adapted for physical, online or hybrid interviews.</p><a class="arrow-link" href="{LIVE}/checklist">Use the free checklist {ARROW}</a></div>
<div class="box rv"><h3 class="h3">Interview Companion</h3><p>Build your Evidence Bank, connect stories to the role and record what you learn after each interview.</p><a class="arrow-link" href="{LIVE}/companion/">Build your Evidence Bank {ARROW}</a></div></div>
</div></section>
{faq_html(IND_FAQ)}
{cta_band("Not sure which <em>fits you?</em>", "Tell Ferhan what you are preparing for and he will point you to the right place to start.")}'''
    extra = [crumbs_ld("/individuals", "For individuals"), faq_ld(IND_FAQ),
             {"@type": "Product", "name": "Interview Ready Guide (The Other Side of the Table)",
              "description": "A 61-page PDF guide on what hiring managers look for in an interview and how to structure convincing answers.",
              "brand": {"@id": ORG_ID}, "url": f"{LIVE}/interviewprepared",
              "offers": {"@type": "Offer", "price": "20.00", "priceCurrency": "MYR", "availability": "https://schema.org/InStock",
                         "url": f"{LIVE}/interviewprepared", "seller": {"@id": ORG_ID}}},
             {"@type": "Service", "name": "Resume Review & Editing", "serviceType": "Resume editing",
              "provider": {"@id": ORG_ID}, "areaServed": "MY", "url": f"{LIVE}/resume-review",
              "offers": {"@type": "Offer", "price": "59.00", "priceCurrency": "MYR", "url": f"{LIVE}/resume-review"}},
             {"@type": "Service", "name": "Personal Interview Coaching", "serviceType": "Interview coaching",
              "provider": {"@id": ORG_ID}, "areaServed": "MY", "url": f"{LIVE}/coaching"}]
    return page("/individuals", "Interview Prep & Resume Review | Bold Shift Advisory",
                "Interview Ready Guide (RM20), resume review and editing (RM59) and interview coaching from a hiring "
                "manager with 15+ years in banking.", body, extra)


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
    body = page_hero("Corporate training", "Corporate training",
                     "<span>Build the capabilities</span> <span><em>your workplace needs.</em></span>",
                     "Training grounded in operational experience, shaped around how people communicate, think, decide and deliver at work.",
                     f'<p class="btns mt"><a class="btn btn-blue" href="{LIVE}/proposal">Discuss your training needs {ARROW}</a></p>') + f'''
<section class="dark proof" aria-label="Trainer background"><div class="wrap">
<div class="p"><div class="num">15+ years</div><div class="lbl">MNC banking &amp; regional corporate operations</div></div>
<div class="p"><div class="num">Leadership</div><div class="lbl">Senior leadership &amp; team development</div></div>
<div class="p"><div class="num">Hiring</div><div class="lbl">Knows what workplaces expect from people</div></div>
</div></section>
<section class="sec" aria-labelledby="change-h"><div class="wrap split">
<div><span class="eyebrow">Start with the workplace</span><h2 class="h2" id="change-h">What needs to change <em>after the training?</em></h2></div>
<div class="prose rv"><p>That is where the conversation starts. Who are the participants? What situations do they find difficult? What would better performance look like?</p>
<p>Program scope and delivery can then be discussed against the needs of your organization.</p>
<h3 class="h3 mt">A practical discussion covers</h3>
<ul class="ticks"><li>Your participants and their responsibilities.</li><li>The behaviors or capabilities you want to develop.</li><li>The workplace situations the learning must address.</li><li>Your intended timing and delivery requirements.</li></ul></div>
</div></section>
<section class="sec paper" aria-labelledby="prog-h"><div class="wrap">
<div class="sec-head"><span class="eyebrow">Program development</span><h2 class="h2" id="prog-h">In-house training &amp; public courses.</h2></div>
<div class="duo">
<article class="card rv"><div class="media">{img(art.rings("k1", 17), "k1")}</div><div class="body"><h3 class="h3">Programs in development</h3><p>The program offering is being developed. Contact us to discuss your requirements or register interest in future course announcements.</p><a class="arrow-link cover" href="{LIVE}/proposal">Start a conversation {ARROW}</a></div></article>
<article class="card rv"><div class="media">{img(art.fan("k2", 19), "k2")}</div><div class="body"><h3 class="h3">Accreditation status</h3><p>Ferhan’s HRDC accreditation process is in progress. Program availability and any applicable claimable status will be confirmed before booking.</p><a class="arrow-link cover" href="/contact">Ask a question {ARROW}</a></div></article>
</div></div></section>
{faq_html(CORP_FAQ)}
{cta_band("Let’s talk about <em>your team.</em>", "Share who your participants are and what you want to develop. Scope and delivery follow from there.")}'''
    extra = [crumbs_ld("/corporate-training", "Corporate training"), faq_ld(CORP_FAQ),
             {"@type": "Service", "name": "Corporate training", "serviceType": "Corporate workplace training",
              "provider": {"@id": ORG_ID}, "areaServed": "MY", "audience": {"@type": "BusinessAudience"},
              "url": SITE + "/corporate-training"}]
    return page("/corporate-training", "Corporate Training in Malaysia | Bold Shift Advisory",
                "Workplace training on communication, judgment and ownership, grounded in 15+ years of MNC banking and "
                "regional corporate operations.", body, extra)


def about():
    body = page_hero("About", "Ferhan Johar · Ferhanafterhours @ Threads",
                     "<span>I’ve sat in</span> <span><em>both chairs.</em></span>",
                     "The candidate trying to be understood. The manager trying to understand what someone can bring.") + f'''
<section class="sec" aria-labelledby="me-h"><div class="wrap founder">
<div class="portrait rv">{img(art.rings("a1", 23, 600, 750), "a1")}<span class="mono" aria-hidden="true">FJ</span><span class="cap">Ferhan Johar · Founder</span></div>
<div class="prose rv"><span class="eyebrow">About me</span><h2 class="h2" id="me-h">Practical, direct <em>and human.</em></h2>
<p>I’m Ferhan Johar, founder of Bold Shift Advisory.</p>
<p>For more than 15 years, I’ve worked across MNC banking and regional corporate operations, leading teams, developing people, managing pressure, and seeing what separates people who are merely busy from people who are trusted to deliver.</p>
<p>That experience shaped the way I teach. In real workplaces, capability is not only technical knowledge. It is how people communicate, think, decide, handle pressure, explain their work, use tools, and build trust with the people around them.</p>
<p>Bold Shift Advisory was built to help organizations develop those practical capabilities through training that is grounded in real operational experience, not textbook theory.</p>
<p>My own path was not perfect. I struggled with grades, English and confidence earlier in life. That is why my work is direct, practical and human. I know what it feels like to be underestimated, and I also know what it takes to become someone others can rely on.</p></div>
</div></section>
<section class="sec dark" aria-labelledby="ways-h"><div class="wrap">
<div class="sec-head"><span class="eyebrow">One perspective</span><h2 class="h2" id="ways-h">Different ways to learn.</h2></div>
<div class="duo">
<div class="box rv"><h3 class="h3">Ferhanafterhours @ Threads</h3><p>Practical lessons and conversations for graduates, juniors and young professionals on interviews, communication, confidence and workplace growth.</p><a class="arrow-link" href="{THREADS}" rel="me noopener">Follow on Threads {ARROW}</a></div>
<div class="box rv"><h3 class="h3">Bold Shift Advisory</h3><p>The home for the guide, free tools, upcoming workshops, coaching and organizational training.</p><a class="arrow-link" href="/free-tools">Start with the free tools {ARROW}</a></div>
</div>
<p class="fine mt">Experiences and views are personal and do not represent any employer.</p>
</div></section>
{cta_band()}'''
    extra = [crumbs_ld("/about", "About"),
             {"@type": "ProfilePage", "@id": SITE + "/about#profile", "url": SITE + "/about", "mainEntity": {"@id": PERSON_ID}}]
    return page("/about", "About Ferhan Johar, Founder | Bold Shift Advisory",
                "Ferhan Johar spent 15+ years in MNC banking and regional corporate operations, hiring, leading teams and "
                "developing people. This is his story.", body, extra, og_type="profile")


def free_tools():
    body = page_hero("Free tools", "Free tools · No account needed",
                     "<span>Start preparing.</span> <span><em>Start here, free.</em></span>",
                     "Practical tools to organize the details, find your evidence and arrive ready for the conversation.") + f'''
<section class="sec" aria-labelledby="tools-h"><div class="wrap">
<h2 class="sr" id="tools-h">The tools</h2>
<div class="duo">
<article class="card rv"><div class="media">{img(art.steps("ft1", 31), "ft1")}</div><div class="body"><span class="eyebrow">01 · Get the practical details right</span><h3 class="h3">Interview preparation checklist</h3>
<p>Research, documents, travel, technology and mindset. Adapt your checklist for a physical, online or hybrid interview.</p>
<div class="chips"><span>Read the job description</span><span>Confirm the location or meeting link</span><span>Prepare questions for the interviewer</span></div>
<a class="arrow-link cover" href="{LIVE}/checklist">Use the free checklist {ARROW}</a></div></article>
<article class="card rv"><div class="media">{img(art.fan("ft2", 33), "ft2")}</div><div class="body"><span class="eyebrow">02 · Prepare what you want to say</span><h3 class="h3">Interactive Companion</h3>
<p>Build your Evidence Bank, connect stories to the role and record what you learn after each interview.</p>
<div class="chips"><span>Communication</span><span>Accountability</span><span>Learning</span></div>
<a class="arrow-link cover" href="{LIVE}/companion/">Build your Evidence Bank {ARROW}</a></div></article>
</div>
<p class="note rv mt">Your preparation stays in your browser on your device. Use the Companion’s backup feature before switching devices or clearing browser data.</p>
</div></section>
<section class="sec paper" aria-labelledby="guide-h"><div class="wrap split">
<div><span class="eyebrow">Go further</span><h2 class="h2" id="guide-h">The tools give you somewhere <em>to prepare.</em></h2></div>
<div class="prose rv"><p>The guide explains how to find relevant evidence and turn it into a clear conversation.</p>
<a class="btn btn-blue" href="{LIVE}/interviewprepared">Explore The Other Side of the Table · RM20 {ARROW}</a></div>
</div></section>'''
    extra = [crumbs_ld("/free-tools", "Free tools"),
             {"@type": "ItemList", "name": "Free interview preparation tools", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Interview preparation checklist", "url": f"{LIVE}/checklist"},
                 {"@type": "ListItem", "position": 2, "name": "Interview Companion", "url": f"{LIVE}/companion/"}]}]
    return page("/free-tools", "Free Interview Preparation Tools | Bold Shift Advisory",
                "A free interview preparation checklist and an Interview Companion to build your Evidence Bank. No "
                "account needed; your preparation stays on your device.", body, extra)


def contact():
    routes = [(f"{LIVE}/proposal", "Corporate training inquiry?"), (f"{LIVE}/workshops", "Looking for the workshops?"),
              (f"{LIVE}/coaching", "Interested in 1-to-1 coaching?"), (f"{LIVE}/interviewprepared", "Looking for the interview guide?")]
    r = "".join(f'<a href="{u}">{t}{ARROW}</a>' for u, t in routes)
    opts = ["General inquiry", "Corporate training inquiry", "Public course interest", "Workshop inquiry",
            "Coaching inquiry", "Existing purchase support"]
    body = page_hero("Contact", "Contact", "<span>Let’s understand</span> <span><em>what you need.</em></span>",
                     "For individual support, corporate training or general inquiries, start here.") + f'''
<section class="sec" aria-labelledby="c-h"><div class="wrap split">
<div class="rv"><h2 class="h2" id="c-h">A useful first conversation.</h2>
<p class="lede">Tell us who you are, what you are working towards and where you would like support.</p>
<p><a class="email-big" href="mailto:{EMAIL}">{EMAIL}</a></p>
<p>Bold Shift Advisory Sdn Bhd<br>Ferhan Johar · <a href="{THREADS}" rel="me noopener">Ferhanafterhours @ Threads</a></p>
<div class="routes mt">{r}</div></div>
<form class="form rv" id="enquiry" action="mailto:{EMAIL}" method="post" enctype="text/plain">
<label>Your name<input name="name" autocomplete="name" required></label>
<label>Email address<input name="email" type="email" autocomplete="email" required></label>
<label>What is this about?<select name="topic">{"".join(f"<option>{o}</option>" for o in opts)}</select></label>
<label>Organization, if relevant<input name="org" autocomplete="organization"></label>
<label>How can we help?<textarea name="message" required></textarea></label>
<button class="btn btn-blue" type="submit">Send inquiry {ARROW}</button>
<small>Opens your email app with your message ready to send. These details are only used to respond to your inquiry.</small>
</form>
</div></section>'''
    extra = [crumbs_ld("/contact", "Contact"),
             {"@type": "ContactPage", "@id": SITE + "/contact#contact", "url": SITE + "/contact", "about": {"@id": ORG_ID}}]
    return page("/contact", "Contact Bold Shift Advisory | Ferhan Johar",
                "Contact Bold Shift Advisory for interview support, corporate training, workshops or coaching. Email "
                "ferhanjohar@boldshiftadvisory.com.", body, extra)


def notfound():
    body = page_hero("", "404", "<span>This page</span> <span><em>moved on.</em></span>",
                     "The page you were looking for isn’t here. Try one of these instead.",
                     f'<p class="btns mt"><a class="btn btn-blue" href="/">Home {ARROW}</a><a class="btn btn-line" href="/individuals">For individuals</a><a class="btn btn-line" href="/corporate-training">Corporate training</a></p>')
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
        (OUT / name).write_text(fn(), encoding="utf-8")
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
    # CSP hash for the one-line inline script
    h = base64.b64encode(hashlib.sha256(INLINE_JS.encode()).digest()).decode()
    hdr = (ROOT / "src/_headers").read_text().replace("__INLINE_HASH__", h)
    (OUT / "_headers").write_text(hdr)
    print("built", len(PAGES), "pages ->", OUT, "| SITE", SITE, "| ASSET", ASSET)


CSS_V = JS_V = ""
if __name__ == "__main__":
    main()
