#!/usr/bin/env python3
"""'jac' — BLACK menacing malware-virus: fanged, glowing eyes, neon-edged spikes."""
import io, math, os
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "svg"); PNG = os.path.join(HERE, "png")

# body is always black; the accent drives eyes / spike-tips / glow / matrix
BLACK = dict(hi="#34383f", lo="#050609", spike="#0a0c10", tooth="#eef1f5", mouth="#000000")
ACCENTS = {
    "ice":   dict(eye="#dff1ff", hot="#ffffff", glow="#8fd0ff", matrix="#244055"),
    "red":   dict(eye="#ff3b3b", hot="#fff2f0", glow="#ff2a2a", matrix="#4a1414"),
    "green": dict(eye="#48ff7a", hot="#eaffe8", glow="#33ff66", matrix="#15431f"),
}

def rnd(i):
    return (math.sin(i * 12.9898) * 43758.5453) % 1.0

def virus(cx, cy, R, gid, ac, rot=0.0):
    n = 16
    spikes = ""
    for i in range(n):
        a = math.radians(i * (360 / n) + rot)
        ln = R * (0.40 + 0.22 * rnd(i))
        if i % 2 == 0:  # sharp triangle spike, neon-lit tip
            hw = R * 0.11
            bx1 = cx + R * 0.92 * math.cos(a - hw / R); by1 = cy + R * 0.92 * math.sin(a - hw / R)
            bx2 = cx + R * 0.92 * math.cos(a + hw / R); by2 = cy + R * 0.92 * math.sin(a + hw / R)
            tx = cx + (R + ln) * math.cos(a); ty = cy + (R + ln) * math.sin(a)
            spikes += f'<path d="M{bx1:.1f} {by1:.1f} L{tx:.1f} {ty:.1f} L{bx2:.1f} {by2:.1f} Z" fill="{BLACK["spike"]}"/>'
            spikes += f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{max(R*0.05,1):.1f}" fill="{ac["glow"]}" filter="url(#gl)"/>'
        else:  # tentacle stalk + knob
            x2 = cx + (R + ln * 0.8) * math.cos(a); y2 = cy + (R + ln * 0.8) * math.sin(a)
            x1 = cx + R * 0.9 * math.cos(a); y1 = cy + R * 0.9 * math.sin(a)
            spikes += (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                       f'stroke="{BLACK["spike"]}" stroke-width="{R*0.14:.1f}" stroke-linecap="round"/>'
                       f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="{R*0.12:.1f}" fill="{BLACK["spike"]}" stroke="{ac["glow"]}" stroke-width="{R*0.025:.1f}"/>')
    body = (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="url(#{gid})" stroke="{ac["glow"]}" stroke-width="{R*0.02:.1f}" stroke-opacity="0.55"/>'
            f'<circle cx="{cx-R*0.34:.1f}" cy="{cy-R*0.36:.1f}" r="{R*0.3:.1f}" fill="#ffffff" opacity="0.10"/>')
    # cell texture
    tex = ""
    for k in range(5):
        ang = k * 1.3; rr = R * (0.2 + 0.5 * rnd(k + 7))
        tex += f'<circle cx="{cx+rr*math.cos(ang):.1f}" cy="{cy+rr*math.sin(ang):.1f}" r="{R*0.1:.1f}" fill="#000" opacity="0.22"/>'
    # angry glowing eyes (outer-high, inner-low = angry)
    def eye(mirror):
        s = -1 if mirror else 1
        ox = cx + s * R * 0.42; iy = cy - R * 0.02
        pts = [(cx + s*R*0.46, cy-R*0.20), (cx + s*R*0.30, cy-R*0.24),
               (cx + s*R*0.10, cy+R*0.02), (cx + s*R*0.30, cy-R*0.02)]
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
        cxh = cx + s * R * 0.30; cyh = cy - R * 0.10
        return (f'<path d="{d}" fill="{ac["eye"]}" filter="url(#gl)"/>'
                f'<circle cx="{cxh:.1f}" cy="{cyh:.1f}" r="{R*0.06:.1f}" fill="{ac["hot"]}"/>')
    eyes = eye(False) + eye(True)
    # fanged grin
    mw = R * 1.0; ml = cx - mw / 2; midy = cy + R * 0.40
    th = R * 0.20; nt = 6; tw = mw / nt
    mouth = f'<path d="M{ml:.1f} {midy-th*0.7:.1f} Q{cx:.1f} {cy+R*0.86:.1f} {ml+mw:.1f} {midy-th*0.7:.1f} L{ml+mw:.1f} {midy:.1f} Q{cx:.1f} {cy+R*0.66:.1f} {ml:.1f} {midy:.1f} Z" fill="{BLACK["mouth"]}"/>'
    teeth = ""
    for i in range(nt):  # top teeth pointing down
        x = ml + i * tw
        teeth += f'<path d="M{x:.1f} {midy-th*0.7:.1f} L{x+tw:.1f} {midy-th*0.7:.1f} L{x+tw/2:.1f} {midy+th*0.4:.1f} Z" fill="{BLACK["tooth"]}"/>'
    for i in range(nt):  # bottom teeth pointing up (offset)
        x = ml + i * tw + tw / 2
        teeth += f'<path d="M{x:.1f} {midy+th*0.9:.1f} L{x+tw:.1f} {midy+th*0.9:.1f} L{x+tw/2:.1f} {midy-th*0.1:.1f} Z" fill="{BLACK["tooth"]}" opacity="0.92"/>'
    return spikes + body + tex + eyes + mouth + teeth

def grad(gid):
    return (f'<radialGradient id="{gid}" cx="0.4" cy="0.34" r="0.75">'
            f'<stop offset="0" stop-color="{BLACK["hi"]}"/>'
            f'<stop offset="0.6" stop-color="#16191f"/>'
            f'<stop offset="1" stop-color="{BLACK["lo"]}"/></radialGradient>')

def matrix_bg(W, H, col, step=24):
    out = ""
    for j, y in enumerate(range(20, H, step)):
        for i, x in enumerate(range(14, W, step)):
            op = 0.05 + 0.16 * rnd(i * 31 + j * 7)
            ch = "1" if rnd(i * 7 + j * 13) > 0.5 else "0"
            out += (f'<text x="{x}" y="{y}" font-family="DejaVu Sans Mono, monospace" '
                    f'font-size="14" fill="{col}" opacity="{op:.2f}">{ch}</text>')
    return out

# ---------- icons (black body, 3 eye accents) ----------
ICON = 512
for key, ac in ACCENTS.items():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{ICON}" height="{ICON}" viewBox="0 0 {ICON} {ICON}">
<defs>
<radialGradient id="bg" cx="0.5" cy="0.45" r="0.75"><stop offset="0" stop-color="#0a0d12"/><stop offset="1" stop-color="#000000"/></radialGradient>
{grad("vb")}
<filter id="gl" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{ac['glow']}" stop-opacity="0.45"/><stop offset="1" stop-color="{ac['glow']}" stop-opacity="0"/></radialGradient>
<clipPath id="rc"><rect x="16" y="16" width="480" height="480" rx="112"/></clipPath>
</defs>
<g clip-path="url(#rc)">
<rect x="16" y="16" width="480" height="480" rx="112" fill="url(#bg)"/>
{matrix_bg(512, 512, ac["matrix"])}
<circle cx="256" cy="238" r="170" fill="url(#halo)"/>
{virus(256, 238, 132, "vb", ac)}
<text x="256" y="478" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="56" font-weight="700" letter-spacing="5" fill="{ac['glow']}" filter="url(#gl)">jac</text>
</g>
</svg>'''
    open(os.path.join(SVG, f"black-{key}.svg"), "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(PNG, f"black-{key}.png"),
                     output_width=512, output_height=512)
    print("icon black-" + key)

# ---------- animation: tiny black virus crawling over code (red eyes) ----------
W, H = 860, 470
FRAMES = 44
ac = ACCENTS["red"]
lines = [
    (70, 96,  "Salom! Men jac — sizning hamrohingiz."),
    (70, 150, "def hisobla(a, b):"),
    (96, 200, "return a + b      # bu yerda xato bormi?"),
    (70, 256, "Bugun qaysi loyiha ustida ishlaymiz?"),
    (70, 312, "console.log('jac ishga tushdi');"),
    (70, 372, "Xatolardan qo'rqmang — men yordam beraman."),
]
route = [(800, 70), (470, 78), (180, 70), (150, 138), (480, 132), (760, 140),
         (790, 196), (430, 200), (170, 192), (180, 250), (520, 256), (800, 248),
         (790, 320), (430, 314), (180, 322), (200, 372), (520, 366), (800, 372), (820, 70)]
def smooth(t): return t * t * (3 - 2 * t)
frames = []
segs = len(route) - 1
for i in range(FRAMES):
    g = i / FRAMES; s = g * segs; idx = min(int(s), segs - 1); fr = smooth(s - idx)
    x = route[idx][0] + (route[idx+1][0]-route[idx][0])*fr
    y = route[idx][1] + (route[idx+1][1]-route[idx][1])*fr + 2.5*math.sin(i*0.9)
    rot = 12 * math.sin(i*0.5)
    gs = 3 + 2*(0.5+0.5*math.sin(i*0.6))
    txt = "".join(f'<text x="{lx}" y="{ly}" font-family="DejaVu Sans Mono, monospace" font-size="22" fill="#5fe08a" opacity="0.85">{t}</text>' for lx, ly, t in lines)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{grad("vb")}
<filter id="gl" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="{gs:.1f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="#06090e"/>
<rect width="{W}" height="36" fill="#0d1218"/>
<circle cx="26" cy="18" r="6" fill="#ff5f56"/><circle cx="48" cy="18" r="6" fill="#ffbd2e"/><circle cx="70" cy="18" r="6" fill="#27c93f"/>
<text x="{W-160}" y="23" font-family="DejaVu Sans, Arial, sans-serif" font-size="14" fill="#5a6b7a">jac — hamroh</text>
{txt}
{virus(x, y, 16, "vb", ac, rot=rot)}
</svg>'''
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H)
    frames.append(Image.open(io.BytesIO(png)).convert("RGB"))
gif = os.path.join(HERE, "black-animation.gif")
frames[0].save(gif, save_all=True, append_images=frames[1:], duration=60, loop=0, optimize=True)
print("animation:", os.path.getsize(gif)//1024, "KB")
print("DONE")
