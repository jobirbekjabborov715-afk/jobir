#!/usr/bin/env python3
"""Generate 'jac' AI companion logo concepts (SVG + PNG) and a floating animation (GIF)."""
import io, math, os
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "svg")
PNG = os.path.join(HERE, "png")
ICON = 512

# ---------- shared helpers ----------
GLOW = ('<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="7" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')

def icon(defs, body, bg):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{ICON}" height="{ICON}" viewBox="0 0 {ICON} {ICON}">
<defs>
{defs}
{GLOW}
<clipPath id="rc"><rect x="16" y="16" width="480" height="480" rx="112"/></clipPath>
</defs>
<g clip-path="url(#rc)">
<rect x="16" y="16" width="480" height="480" rx="112" fill="url(#{bg})"/>
{body}
</g>
</svg>'''

def wm(color="#dbeeff", op="0.92"):
    return (f'<text x="256" y="478" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" '
            f'font-size="56" font-weight="700" letter-spacing="5" fill="{color}" opacity="{op}">jac</text>')

# ---------- 1. Floating droid (EVE-like) ----------
def droid():
    defs = '''
<linearGradient id="bg1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c1730"/><stop offset="1" stop-color="#173a6b"/></linearGradient>
<linearGradient id="body1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#c9d6e8"/></linearGradient>
<linearGradient id="visor1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1426"/><stop offset="1" stop-color="#1f3358"/></linearGradient>
<radialGradient id="eye1" cx="0.5" cy="0.4" r="0.6"><stop offset="0" stop-color="#d7faff"/><stop offset="0.5" stop-color="#36e2ff"/><stop offset="1" stop-color="#159fdd"/></radialGradient>'''
    body = '''
<ellipse cx="256" cy="432" rx="92" ry="15" fill="#000" opacity="0.30" filter="url(#glow)"/>
<path d="M256 92 C188 92 148 168 148 248 C148 332 196 396 256 396 C316 396 364 332 364 248 C364 168 324 92 256 92 Z" fill="url(#body1)"/>
<ellipse cx="210" cy="168" rx="24" ry="40" fill="#ffffff" opacity="0.55"/>
<g transform="rotate(-8 256 232)">
  <rect x="166" y="196" width="180" height="76" rx="38" fill="url(#visor1)"/>
  <ellipse cx="224" cy="236" rx="15" ry="19" fill="url(#eye1)" filter="url(#glow)"/>
  <ellipse cx="290" cy="230" rx="15" ry="19" fill="url(#eye1)" filter="url(#glow)"/>
</g>''' + wm("#eaf4ff")
    return icon(defs, body, "bg1")

# ---------- 2. Boxy buddy ----------
def boxy():
    defs = '''
<linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#063b3a"/><stop offset="1" stop-color="#0b7268"/></linearGradient>
<linearGradient id="metal2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eef3f6"/><stop offset="1" stop-color="#b6c4cd"/></linearGradient>
<radialGradient id="eye2" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ccffff"/><stop offset="0.6" stop-color="#22e3d6"/><stop offset="1" stop-color="#0fae9f"/></radialGradient>'''
    body = '''
<line x1="256" y1="150" x2="256" y2="104" stroke="#cfdbe2" stroke-width="7" stroke-linecap="round"/>
<circle cx="256" cy="96" r="13" fill="url(#eye2)" filter="url(#glow)"/>
<rect x="128" y="214" width="22" height="74" rx="11" fill="#9fb0bb"/>
<rect x="362" y="214" width="22" height="74" rx="11" fill="#9fb0bb"/>
<rect x="146" y="150" width="220" height="200" rx="50" fill="url(#metal2)" stroke="#94a6b0" stroke-width="3"/>
<rect x="176" y="186" width="160" height="128" rx="32" fill="#0c1622"/>
<circle cx="220" cy="240" r="21" fill="url(#eye2)" filter="url(#glow)"/>
<circle cx="292" cy="240" r="21" fill="url(#eye2)" filter="url(#glow)"/>
<path d="M214 288 Q256 312 298 288" fill="none" stroke="#22e3d6" stroke-width="8" stroke-linecap="round"/>''' + wm("#d9fffb")
    return icon(defs, body, "bg2")

# ---------- 3. Blob creature (cute "virus") ----------
def blob():
    defs = '''
<linearGradient id="bg3" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a0b2e"/><stop offset="1" stop-color="#3d1b66"/></linearGradient>
<radialGradient id="blob3" cx="0.5" cy="0.4" r="0.7"><stop offset="0" stop-color="#9bffe6"/><stop offset="0.55" stop-color="#2fe0c4"/><stop offset="1" stop-color="#13a7d6"/></radialGradient>'''
    nubs = ""
    for a in range(0, 360, 45):
        r = math.radians(a)
        x = 256 + 132*math.cos(r); y = 250 + 132*math.sin(r)
        nubs += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="url(#blob3)" filter="url(#glow)"/>'
    body = nubs + '''
<path d="M256 128 C326 128 366 176 366 236 C366 292 338 302 338 338 C338 376 302 396 256 396 C210 396 174 376 174 338 C174 302 146 292 146 236 C146 176 186 128 256 128 Z" fill="url(#blob3)" filter="url(#glow)"/>
<ellipse cx="222" cy="244" rx="20" ry="25" fill="#ffffff"/>
<ellipse cx="290" cy="244" rx="20" ry="25" fill="#ffffff"/>
<circle cx="226" cy="250" r="10" fill="#10243a"/>
<circle cx="294" cy="250" r="10" fill="#10243a"/>
<circle cx="222" cy="245" r="4" fill="#fff"/>
<circle cx="290" cy="245" r="4" fill="#fff"/>
<path d="M232 300 Q256 320 280 300" fill="none" stroke="#0c3b4a" stroke-width="7" stroke-linecap="round"/>''' + wm("#e9d9ff")
    return icon(defs, body, "bg3")

# ---------- 4. Energy orb (Jarvis) ----------
def orb():
    defs = '''
<radialGradient id="bg4" cx="0.5" cy="0.42" r="0.75"><stop offset="0" stop-color="#16284a"/><stop offset="1" stop-color="#05080f"/></radialGradient>
<radialGradient id="core4" cx="0.5" cy="0.45" r="0.55"><stop offset="0" stop-color="#ffffff"/><stop offset="0.4" stop-color="#7af0ff"/><stop offset="1" stop-color="#0e7fb8"/></radialGradient>
<filter id="glow4" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="13" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''
    dots = ""
    for a in (20, 150, 265):
        r = math.radians(a); x = 256 + 120*math.cos(r); y = 252 + 120*math.sin(r)
        dots += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="#7af0ff" filter="url(#glow4)"/>'
    body = '''
<circle cx="256" cy="252" r="150" fill="none" stroke="#39d6ff" stroke-width="2" opacity="0.22"/>
<circle cx="256" cy="252" r="120" fill="none" stroke="#5fe6ff" stroke-width="3" opacity="0.45" filter="url(#glow4)"/>
<circle cx="256" cy="252" r="90" fill="none" stroke="#9af3ff" stroke-width="4" opacity="0.8" filter="url(#glow4)"/>
''' + dots + '''
<circle cx="256" cy="252" r="60" fill="url(#core4)" filter="url(#glow4)"/>
<circle cx="256" cy="252" r="24" fill="#0a1a2a" opacity="0.55"/>
<circle cx="256" cy="252" r="12" fill="#eaffff"/>''' + wm("#bdeeff")
    return icon(defs, body, "bg4")

# ---------- 5. Minimal line bot ----------
def minimal():
    defs = '''
<linearGradient id="bg5" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f141b"/><stop offset="1" stop-color="#1b2734"/></linearGradient>'''
    s = "#dbeeff"
    body = f'''
<line x1="256" y1="160" x2="256" y2="118" stroke="{s}" stroke-width="8" stroke-linecap="round"/>
<circle cx="256" cy="110" r="11" fill="{s}"/>
<line x1="146" y1="240" x2="146" y2="290" stroke="{s}" stroke-width="8" stroke-linecap="round"/>
<line x1="366" y1="240" x2="366" y2="290" stroke="{s}" stroke-width="8" stroke-linecap="round"/>
<rect x="158" y="160" width="196" height="180" rx="46" fill="none" stroke="{s}" stroke-width="9"/>
<circle cx="222" cy="248" r="14" fill="{s}"/>
<circle cx="290" cy="248" r="14" fill="{s}"/>
<line x1="224" y1="300" x2="288" y2="300" stroke="{s}" stroke-width="9" stroke-linecap="round"/>''' + wm(s)
    return icon(defs, body, "bg5")

# ---------- 6. Pixel bot ----------
def pixel():
    defs = '''
<linearGradient id="bg6" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0f17"/><stop offset="1" stop-color="#141d2c"/></linearGradient>
<filter id="glow6" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''
    grid = [
        "....A....",
        "....A....",
        ".BBBBBBB.",
        ".B.....B.",
        ".B.C.C.B.",
        ".B.....B.",
        ".B.MMM.B.",
        ".BBBBBBB.",
        "..B...B..",
    ]
    cell = 40
    gx = (ICON - 9*cell)//2
    gy = 86
    cmap = {"A": ("#36e2ff", True), "B": ("#c4d2e0", False), "C": ("#36e2ff", True), "M": ("#1fb6c9", False)}
    sq = ""
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            col, glw = cmap[ch]
            x = gx + c*cell; y = gy + r*cell
            f = ' filter="url(#glow6)"' if glw else ""
            sq += f'<rect x="{x}" y="{y}" width="{cell-4}" height="{cell-4}" rx="6" fill="{col}"{f}/>'
    return icon(defs, sq + wm("#cfe0f2"), "bg6")

# ---------- write icons ----------
concepts = {
    "jac-1-droid":   droid(),
    "jac-2-boxy":    boxy(),
    "jac-3-blob":    blob(),
    "jac-4-orb":     orb(),
    "jac-5-minimal": minimal(),
    "jac-6-pixel":   pixel(),
}
for name, svg in concepts.items():
    open(os.path.join(SVG, name + ".svg"), "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(PNG, name + ".png"),
                     output_width=512, output_height=512)
    print("wrote", name)

# ---------- animation: droid drifting + bobbing on a "screen" ----------
W, H = 960, 560
FRAMES = 30

def droid_group(cx, cy, glow_std, s=0.8):
    return f'''
<filter id="ge" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="{glow_std:.1f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<ellipse cx="{cx:.0f}" cy="470" rx="74" ry="13" fill="#000" opacity="0.32"/>
<g transform="translate({cx:.1f} {cy:.1f}) scale({s}) translate(-256 -250)">
  <path d="M256 92 C188 92 148 168 148 248 C148 332 196 396 256 396 C316 396 364 332 364 248 C364 168 324 92 256 92 Z" fill="#eef4fb"/>
  <ellipse cx="210" cy="168" rx="24" ry="40" fill="#ffffff" opacity="0.6"/>
  <g transform="rotate(-8 256 232)">
    <rect x="166" y="196" width="180" height="76" rx="38" fill="#13243f"/>
    <ellipse cx="224" cy="236" rx="15" ry="19" fill="#46e6ff" filter="url(#ge)"/>
    <ellipse cx="290" cy="230" rx="15" ry="19" fill="#46e6ff" filter="url(#ge)"/>
  </g>
</g>'''

def bubble(cx, cy, op):
    bx = min(max(cx - 120, 24), W - 360)
    by = max(cy - 190, 20)
    return f'''<g opacity="{op:.2f}">
<rect x="{bx:.0f}" y="{by:.0f}" width="340" height="92" rx="22" fill="#ffffff"/>
<path d="M{cx-18:.0f} {by+92:.0f} l18 26 l18 -26 Z" fill="#ffffff"/>
<text x="{bx+24:.0f}" y="{by+40:.0f}" font-family="DejaVu Sans, Arial, sans-serif" font-size="22" font-weight="700" fill="#0e2336">Bu yerda kichik xato bor —</text>
<text x="{bx+24:.0f}" y="{by+70:.0f}" font-family="DejaVu Sans, Arial, sans-serif" font-size="22" font-weight="700" fill="#1aa6c4">tuzatib beraymi?</text>
</g>'''

frames = []
for i in range(FRAMES):
    t = i / FRAMES
    cx = 480 + 250*math.sin(2*math.pi*t)
    cy = 270 + 24*math.sin(4*math.pi*t)
    g = 5 + 4*(0.5 + 0.5*math.sin(6*math.pi*t))
    # speech bubble fades in during second half of the loop
    if 0.45 < t < 0.95:
        op = min((t-0.45)/0.12, 1.0, (0.95-t)/0.12)
    else:
        op = 0.0
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<linearGradient id="scr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a1020"/><stop offset="1" stop-color="#101a33"/></linearGradient>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#1b3866" stop-opacity="0.7"/><stop offset="1" stop-color="#1b3866" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="url(#scr)"/>
<rect x="70" y="60" width="820" height="440" rx="26" fill="#ffffff" opacity="0.04"/>
<rect x="70" y="60" width="820" height="46" rx="26" fill="#ffffff" opacity="0.05"/>
<circle cx="102" cy="83" r="7" fill="#ff6b6b" opacity="0.7"/><circle cx="126" cy="83" r="7" fill="#ffd166" opacity="0.7"/><circle cx="150" cy="83" r="7" fill="#4ade80" opacity="0.7"/>
<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="150" ry="150" fill="url(#halo)"/>
{droid_group(cx, cy, g)}
{bubble(cx, cy, op)}
</svg>'''
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H)
    frames.append(Image.open(io.BytesIO(png)).convert("RGB"))

gif_path = os.path.join(HERE, "jac-animation.gif")
frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
print("wrote animation:", gif_path, os.path.getsize(gif_path)//1024, "KB")
print("DONE")
