#!/usr/bin/env python3
"""'jac' as a small spiky VIRUS companion: icon variants + tiny-over-text animation."""
import io, math, os
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "svg"); PNG = os.path.join(HERE, "png")

PALETTES = {
    "toxic": dict(bg=("#0a1f12", "#06140c"), body=("#9bff8a", "#1f9c3a"),
                  spike="#1f7a34", knob="#c8ff9e", eye="#06210f", glow="#6dff7a"),
    "cyber": dict(bg=("#06121f", "#040a14"), body=("#9be8ff", "#0e7fb8"),
                  spike="#125f8a", knob="#c8f4ff", eye="#04161f", glow="#46d6ff"),
    "venom": dict(bg=("#1a0a22", "#0d0512"), body=("#f3a6ff", "#7a1fb0"),
                  spike="#6a1f9e", knob="#f5c8ff", eye="#1a0622", glow="#d46bff"),
}

def virus_group(cx, cy, R, gid, pal, rot=0.0, look=0.0):
    """Spiky corona-virus mascot centered at (cx,cy), body radius R."""
    n = 12
    slen = R * 0.46
    sw = max(R * 0.16, 1.2)
    kr = max(R * 0.17, 1.4)
    spikes = ""
    for i in range(n):
        a = math.radians(i * (360 / n) + rot)
        x1 = cx + R * 0.9 * math.cos(a); y1 = cy + R * 0.9 * math.sin(a)
        x2 = cx + (R + slen) * math.cos(a); y2 = cy + (R + slen) * math.sin(a)
        spikes += (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="{pal["spike"]}" stroke-width="{sw:.1f}" stroke-linecap="round"/>'
                   f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="{kr:.1f}" fill="{pal["knob"]}"/>')
    # inner texture (capsomeres)
    caps = ""
    for dx, dy in [(-.35, -.3), (.3, -.35), (.4, .25), (-.3, .35), (.05, .45), (-.5, .05)]:
        caps += (f'<circle cx="{cx+dx*R:.1f}" cy="{cy+dy*R:.1f}" r="{R*0.16:.1f}" '
                 f'fill="{pal["spike"]}" opacity="0.35"/>')
    body = (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="url(#{gid})"/>'
            f'<circle cx="{cx-R*0.32:.1f}" cy="{cy-R*0.34:.1f}" r="{R*0.34:.1f}" fill="#ffffff" opacity="0.30"/>')
    # mischievous, NOT-cute eyes: small slanted almonds + sharp highlight
    ex = R * 0.34; ey = -R * 0.05
    erx, ery = R * 0.16, R * 0.24
    lx = cx - ex + look * R * 0.12; rx = cx + ex + look * R * 0.12
    eyes = (
        f'<g transform="rotate(22 {lx:.1f} {cy+ey:.1f})"><ellipse cx="{lx:.1f}" cy="{cy+ey:.1f}" rx="{erx:.1f}" ry="{ery:.1f}" fill="{pal["eye"]}"/></g>'
        f'<g transform="rotate(-22 {rx:.1f} {cy+ey:.1f})"><ellipse cx="{rx:.1f}" cy="{cy+ey:.1f}" rx="{erx:.1f}" ry="{ery:.1f}" fill="{pal["eye"]}"/></g>'
        f'<circle cx="{lx-erx*0.3:.1f}" cy="{cy+ey-ery*0.4:.1f}" r="{R*0.06:.1f}" fill="#fff"/>'
        f'<circle cx="{rx-erx*0.3:.1f}" cy="{cy+ey-ery*0.4:.1f}" r="{R*0.06:.1f}" fill="#fff"/>'
    )
    # tiny smirk
    smirk = (f'<path d="M{cx-R*0.22:.1f} {cy+R*0.4:.1f} Q{cx:.1f} {cy+R*0.55:.1f} {cx+R*0.28:.1f} {cy+R*0.34:.1f}" '
             f'fill="none" stroke="{pal["eye"]}" stroke-width="{max(R*0.08,1.4):.1f}" stroke-linecap="round"/>')
    return spikes + body + caps + eyes + smirk

def grad_def(gid, pal):
    return (f'<radialGradient id="{gid}" cx="0.4" cy="0.35" r="0.7">'
            f'<stop offset="0" stop-color="{pal["body"][0]}"/>'
            f'<stop offset="1" stop-color="{pal["body"][1]}"/></radialGradient>')

# ---------- icon variants ----------
ICON = 512
for key, pal in PALETTES.items():
    R = 132
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{ICON}" height="{ICON}" viewBox="0 0 {ICON} {ICON}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{pal['bg'][0]}"/><stop offset="1" stop-color="{pal['bg'][1]}"/></linearGradient>
{grad_def("vb", pal)}
<filter id="gl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="rc"><rect x="16" y="16" width="480" height="480" rx="112"/></clipPath>
</defs>
<g clip-path="url(#rc)">
<rect x="16" y="16" width="480" height="480" rx="112" fill="url(#bg)"/>
<g filter="url(#gl)">{virus_group(256, 238, R, "vb", pal)}</g>
<text x="256" y="476" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="56" font-weight="700" letter-spacing="5" fill="{pal['glow']}">jac</text>
</g>
</svg>'''
    open(os.path.join(SVG, f"virus-{key}.svg"), "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(PNG, f"virus-{key}.png"),
                     output_width=512, output_height=512)
    print("icon", key)

# ---------- size demo: how tiny it is next to text ----------
pal = PALETTES["toxic"]
W2, H2 = 840, 230
sizes = [(150, 60), (340, 38), (470, 26), (560, 18)]
demo = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}">
<defs>{grad_def("vb", pal)}</defs>
<rect width="{W2}" height="{H2}" fill="#f6f8fb"/>
<text x="40" y="50" font-family="DejaVu Sans, Arial, sans-serif" font-size="26" font-weight="700" fill="#16324a">Haqiqiy o'lchamlar (kichik = shrift kabi):</text>'''
for cx, R in sizes:
    demo += virus_group(cx, 120, R, "vb", pal)
    demo += f'<text x="{cx:.0f}" y="200" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="18" fill="#5a6b7a">{int(R*2.9)}px</text>'
demo += f'''<text x="650" y="128" font-family="DejaVu Sans, Arial, sans-serif" font-size="22" fill="#33485a">matn yonida shuncha kichik</text></svg>'''
cairosvg.svg2png(bytestring=demo.encode(), write_to=os.path.join(PNG, "virus-sizes.png"), output_width=W2, output_height=H2)
print("size demo")

# ---------- animation: tiny virus crawling over/under text ----------
W, H = 860, 470
FRAMES = 44
pal = PALETTES["toxic"]
lines = [
    (70, 96,  "Salom! Men jac — sizning hamrohingiz."),
    (70, 150, "def hisobla(a, b):"),
    (96, 200, "return a + b      # bu yerda xato bormi?"),
    (70, 256, "Bugun qaysi loyiha ustida ishlaymiz?"),
    (70, 312, "console.log('jac ishga tushdi');"),
    (70, 372, "Xatolardan qo'rqmang — men yordam beraman."),
]
# route: weave over and under the text lines (x, y)
route = [(800, 70), (470, 78), (180, 70),
         (150, 138), (480, 132), (760, 140),
         (790, 196), (430, 200), (170, 192),
         (180, 250), (520, 256), (800, 248),
         (790, 320), (430, 314), (180, 322),
         (200, 372), (520, 366), (800, 372),
         (820, 70)]

def smooth(t): return t * t * (3 - 2 * t)

frames = []
segs = len(route) - 1
for i in range(FRAMES):
    g = i / FRAMES
    s = g * segs; idx = min(int(s), segs - 1); fr = smooth(s - idx)
    x = route[idx][0] + (route[idx + 1][0] - route[idx][0]) * fr
    y = route[idx][1] + (route[idx + 1][1] - route[idx][1]) * fr
    y += 2.5 * math.sin(i * 0.9)               # bob
    rot = 14 * math.sin(i * 0.5)               # spike wiggle
    dx = route[idx + 1][0] - route[idx][0]
    look = -1 if dx < 0 else 1
    gstd = 3 + 2 * (0.5 + 0.5 * math.sin(i * 0.6))
    txt = ""
    for lx, ly, t in lines:
        txt += (f'<text x="{lx}" y="{ly}" font-family="DejaVu Sans, Arial, sans-serif" '
                f'font-size="24" fill="#28465e">{t}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{grad_def("vb", pal)}
<filter id="gl" x="-120%" y="-120%" width="340%" height="340%"><feGaussianBlur stdDeviation="{gstd:.1f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="#f6f8fb"/>
<rect x="0" y="0" width="{W}" height="40" fill="#eceff4"/>
<circle cx="26" cy="20" r="6" fill="#ff6b6b"/><circle cx="48" cy="20" r="6" fill="#ffd166"/><circle cx="70" cy="20" r="6" fill="#4ade80"/>
<text x="{W-150}" y="25" font-family="DejaVu Sans, Arial, sans-serif" font-size="15" fill="#9aa7b4">jac — hamroh</text>
{txt}
<g filter="url(#gl)">{virus_group(x, y, 13, "vb", pal, rot=rot, look=look)}</g>
</svg>'''
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H)
    frames.append(Image.open(io.BytesIO(png)).convert("RGB"))

gif = os.path.join(HERE, "virus-animation.gif")
frames[0].save(gif, save_all=True, append_images=frames[1:], duration=60, loop=0, optimize=True)
print("animation:", os.path.getsize(gif)//1024, "KB")
print("DONE")
