"""Original generative SVG artwork (deterministic) used instead of stock photography."""
import math
import random


def _grad(gid, a, b, vertical=False):
    x2, y2 = ("0", "1") if vertical else ("1", "0")
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')


def fan(uid, seed=1, w=800, h=600, bg="#071f33"):
    """Lines that fan out from a low focal point (growth / opportunity)."""
    r = random.Random(seed)
    fx, fy = w * (0.35 + r.random() * 0.3), h * 1.02
    paths, dots = [], []
    n = 30
    for i in range(n):
        t = i / (n - 1)
        ex = -w * 0.2 + t * w * 1.4
        ey = h * (0.05 + 0.35 * abs(t - 0.5) * 2) + r.uniform(-30, 30)
        c1x, c1y = fx + (ex - fx) * 0.15, fy - h * (0.45 + r.random() * 0.2)
        c2x, c2y = ex + r.uniform(-90, 90), ey + h * 0.35
        op = 0.25 + 0.6 * (1 - abs(t - 0.5) * 2)
        paths.append(f'<path d="M{fx:.0f} {fy:.0f}C{c1x:.0f} {c1y:.0f} {c2x:.0f} {c2y:.0f} {ex:.0f} {ey:.0f}" '
                     f'stroke="url(#{uid}g)" stroke-opacity="{op:.2f}" stroke-width="1.3" fill="none"/>')
    for _ in range(46):
        x, y = r.uniform(0, w), r.uniform(0, h * 0.75)
        rad = r.choice([1.5, 2, 3, 4, 6])
        dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad}" fill="{r.choice(["#2251ff", "#00a9f4", "#7fd3ff"])}" fill-opacity="{r.uniform(.35, .9):.2f}"/>')
    return (f'<svg class="art" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
            f'<defs>{_grad(uid + "g", "#00a9f4", "#2251ff")}<radialGradient id="{uid}r" cx=".5" cy="1" r=".8">'
            f'<stop offset="0" stop-color="#1b4bd8" stop-opacity=".55"/><stop offset="1" stop-color="{bg}" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="{bg}"/><rect width="{w}" height="{h}" fill="url(#{uid}r)"/>'
            f'<g class="flow">{"".join(paths)}</g>{"".join(dots)}</svg>')


def waves(uid, seed=2, w=800, h=600, bg="#0a2a6b"):
    """Layered horizontal waves (momentum / a shift)."""
    r = random.Random(seed)
    out = []
    n = 22
    for i in range(n):
        y0 = h * 0.15 + i * (h * 0.75 / n)
        amp = 18 + r.random() * 40
        ph = r.random() * math.tau
        k = 1.2 + r.random() * 1.2
        pts = []
        for s in range(0, 41):
            x = -40 + s * (w + 80) / 40
            y = y0 + math.sin(ph + k * s / 40 * math.tau) * amp * (0.4 + s / 40)
            pts.append(f"{x:.0f} {y:.0f}")
        out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="url(#{uid}g)" '
                   f'stroke-width="1.2" stroke-opacity="{0.25 + 0.6 * i / n:.2f}"/>')
    return (f'<svg class="art" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
            f'<defs>{_grad(uid + "g", "#7fd3ff", "#2251ff")}{_grad(uid + "b", bg, "#051c2c", True)}</defs>'
            f'<rect width="{w}" height="{h}" fill="url(#{uid}b)"/><g class="flow">{"".join(out)}</g></svg>')


def rings(uid, seed=3, w=800, h=600, bg="#051c2c"):
    """Concentric arcs + a dot grid (structure / a framework)."""
    r = random.Random(seed)
    cx, cy = w * (0.62 + r.random() * 0.2), h * (0.45 + r.random() * 0.2)
    arcs = []
    for i in range(1, 16):
        rad = i * 34
        a0 = r.uniform(0, 360)
        sweep = r.uniform(120, 300)
        x1 = cx + rad * math.cos(math.radians(a0)); y1 = cy + rad * math.sin(math.radians(a0))
        x2 = cx + rad * math.cos(math.radians(a0 + sweep)); y2 = cy + rad * math.sin(math.radians(a0 + sweep))
        large = 1 if sweep > 180 else 0
        arcs.append(f'<path d="M{x1:.0f} {y1:.0f}A{rad} {rad} 0 {large} 1 {x2:.0f} {y2:.0f}" fill="none" '
                    f'stroke="url(#{uid}g)" stroke-width="{1 + (i % 3) * 0.6:.1f}" stroke-opacity="{0.3 + 0.5 * (1 - i / 16):.2f}"/>')
    grid = []
    for gx in range(0, w + 1, 40):
        for gy in range(0, h + 1, 40):
            d = math.hypot(gx - cx, gy - cy)
            if d > 140:
                grid.append(f'<circle cx="{gx}" cy="{gy}" r="1.2" fill="#9fb3c4" fill-opacity="{max(0.08, 0.35 - d / 2400):.2f}"/>')
    return (f'<svg class="art" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
            f'<defs>{_grad(uid + "g", "#00a9f4", "#2251ff")}</defs><rect width="{w}" height="{h}" fill="{bg}"/>'
            f'{"".join(grid)}<g class="flow">{"".join(arcs)}</g><circle cx="{cx:.0f}" cy="{cy:.0f}" r="7" fill="#00a9f4"/></svg>')


def steps(uid, seed=4, w=800, h=600, bg="#0b2a42"):
    """Rising bars/steps (progress, a next step)."""
    r = random.Random(seed)
    bars = []
    n = 14
    bw = w / n
    for i in range(n):
        bh = h * (0.12 + 0.7 * (i / n) ** 1.4) + r.uniform(-20, 20)
        bars.append(f'<rect x="{i * bw + 6:.0f}" y="{h - bh:.0f}" width="{bw - 12:.0f}" height="{bh:.0f}" '
                    f'fill="url(#{uid}g)" fill-opacity="{0.25 + 0.6 * i / n:.2f}"/>')
    line = " ".join(f"{i * bw + bw / 2:.0f} {h - h * (0.16 + 0.7 * (i / n) ** 1.4) - 30:.0f}" for i in range(n))
    return (f'<svg class="art" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
            f'<defs>{_grad(uid + "g", "#2251ff", "#00a9f4", True)}</defs><rect width="{w}" height="{h}" fill="{bg}"/>'
            f'<g class="flow">{"".join(bars)}</g><polyline points="{line}" fill="none" stroke="#7fd3ff" stroke-width="2.5"/></svg>')
