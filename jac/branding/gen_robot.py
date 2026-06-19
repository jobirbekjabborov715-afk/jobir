#!/usr/bin/env python3
"""'jac' — cute 3D-style robot (dark rounded head, glowing rounded-square eyes).
Alive motion: bob, head tilt, look-around, blink + state-based eye colors."""
import io, math, os
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); PNG = os.path.join(HERE, "png")
S = 600  # working canvas
HX, HY = 300, 232          # head center
PIVOT = 338                # neck pivot y

def hx(c): return tuple(int(c[i:i+2], 16) for i in (1, 3, 5))
def lp(a, b, f): return tuple(int(a[k]+(b[k]-a[k])*f) for k in range(3))
def hexs(r): return "#%02x%02x%02x" % r
KEYS = [(0.00, "#37d6ff", "Salom!"), (0.24, "#37d6ff", "Salom!"),
        (0.31, "#33ff6a", "Tayyorman"), (0.50, "#33ff6a", "Tayyorman"),
        (0.57, "#ffb02e", "O'ylayapman..."), (0.72, "#ffb02e", "O'ylayapman..."),
        (0.80, "#ff4d4d", "Xato topildi!"), (0.94, "#ff4d4d", "Xato topildi!"),
        (1.00, "#37d6ff", "Salom!")]
def state(t):
    for i in range(len(KEYS)-1):
        if KEYS[i][0] <= t <= KEYS[i+1][0]:
            f = (t-KEYS[i][0])/((KEYS[i+1][0]-KEYS[i][0]) or 1)
            return hexs(lp(hx(KEYS[i][1]), hx(KEYS[i+1][1]), f)), (KEYS[i][2] if f < 0.5 else KEYS[i+1][2])
    return KEYS[-1][1], KEYS[-1][2]

DEFS = '''
<linearGradient id="head" x1="0.2" y1="0" x2="0.8" y2="1"><stop offset="0" stop-color="#4a5158"/><stop offset="0.55" stop-color="#363c43"/><stop offset="1" stop-color="#23272d"/></linearGradient>
<linearGradient id="neck" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4046"/><stop offset="1" stop-color="#262a30"/></linearGradient>
<radialGradient id="base" cx="0.5" cy="0.3" r="0.8"><stop offset="0" stop-color="#3c424a"/><stop offset="1" stop-color="#1c2026"/></radialGradient>
<radialGradient id="panel" cx="0.5" cy="0.4" r="0.75"><stop offset="0" stop-color="#161a1f"/><stop offset="1" stop-color="#05070a"/></radialGradient>
<radialGradient id="floor" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#000" stop-opacity="0.30"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'''

def robot(bob, tilt, lookx, looky, blink, col, gs):
    fy = 470; fscale = 1 - bob*0.012
    floor = f'<ellipse cx="300" cy="{fy}" rx="{135*fscale:.0f}" ry="{30*fscale:.0f}" fill="url(#floor)"/>'
    g = f'<g transform="translate(0 {bob:.1f})">'
    base = ('<ellipse cx="300" cy="430" rx="118" ry="42" fill="url(#base)"/>'
            '<ellipse cx="300" cy="424" rx="100" ry="30" fill="#2b3037"/>'
            f'<circle cx="300" cy="416" r="9" fill="{col}" filter="url(#gl)"/>')      # power LED
    neck = '<rect x="270" y="322" width="60" height="56" rx="20" fill="url(#neck)"/>'
    # head group tilts around neck pivot
    eye_h = 62*blink
    def eye(ex):
        y = HY+6+looky - eye_h/2
        x = ex+lookx
        s = f'<rect x="{x-23:.1f}" y="{y:.1f}" width="46" height="{eye_h:.1f}" rx="16" fill="{col}" filter="url(#gl)"/>'
        if blink > 0.45:
            s += f'<rect x="{x-23:.1f}" y="{y:.1f}" width="20" height="{eye_h*0.5:.1f}" rx="10" fill="#fff" opacity="0.85"/>'
        return s
    head = f'''<g transform="rotate({tilt:.2f} 300 {PIVOT})">
  <rect x="178" y="124" width="244" height="228" rx="70" fill="#10131a" opacity="0.55"/>
  <rect x="170" y="118" width="260" height="228" rx="70" fill="url(#head)"/>
  <ellipse cx="232" cy="168" rx="70" ry="40" fill="#ffffff" opacity="0.12"/>
  <rect x="170" y="118" width="260" height="228" rx="70" fill="none" stroke="#5a626b" stroke-width="2" opacity="0.5"/>
  <rect x="200" y="166" width="200" height="140" rx="46" fill="url(#panel)"/>
  {eye(260)}{eye(340)}
  <circle cx="300" cy="132" r="7" fill="{col}" filter="url(#gl)"/>
</g>'''
    return floor + g + base + neck + head + "</g>"

# ---------- static icon ----------
for bgkey, bg in [("dark", '<radialGradient id="bg" cx="0.5" cy="0.42" r="0.8"><stop offset="0" stop-color="#141922"/><stop offset="1" stop-color="#05070b"/></radialGradient>'),
                  ("studio", '<radialGradient id="bg" cx="0.5" cy="0.4" r="0.8"><stop offset="0" stop-color="#eef2f6"/><stop offset="1" stop-color="#c4ccd5"/></radialGradient>')]:
    col = "#37d6ff"
    name_fill = col if bgkey == "dark" else "#2a2e35"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs>{bg}{DEFS}
<filter id="gl" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="rc"><rect x="20" y="20" width="560" height="560" rx="130"/></clipPath></defs>
<g clip-path="url(#rc)"><rect x="20" y="20" width="560" height="560" rx="130" fill="url(#bg)"/>
{robot(0, -4, 0, 0, 1.0, col, 6)}
<text x="300" y="556" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="60" font-weight="700" letter-spacing="6" fill="{name_fill}">jac</text>
</g></svg>'''
    open(os.path.join(HERE, "svg", f"robot-{bgkey}.svg"), "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(PNG, f"robot-{bgkey}.png"), output_width=512, output_height=512)
    print("icon", bgkey)

# ---------- alive animation ----------
FRAMES = 48
frames = []
for i in range(FRAMES):
    tl = i/FRAMES; t = tl*2*math.pi
    col, label = state(tl)
    bob = 7*math.sin(t)
    tilt = 6*math.sin(t*0.5 + 0.4)
    lookx = 9*math.sin(t*0.7 + 1.0)
    looky = 3*math.sin(t*1.1)
    gs = 4 + 3*(0.5+0.5*math.sin(t*1.4))
    # two blinks per loop
    blink = 1.0
    for bc in (0.20, 0.66):
        if abs(((tl-bc) % 1.0)) < 0.02 or abs(((tl-bc) % 1.0) - 1.0) < 0.02:
            blink = 0.12
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs>
<radialGradient id="bg" cx="0.5" cy="0.36" r="0.85"><stop offset="0" stop-color="#eef2f6"/><stop offset="0.7" stop-color="#d2d9e1"/><stop offset="1" stop-color="#b3bcc6"/></radialGradient>
{DEFS}
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{col}" stop-opacity="0.22"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>
<filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="{gs:.1f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{S}" height="{S}" fill="url(#bg)"/>
<ellipse cx="300" cy="232" rx="250" ry="250" fill="url(#halo)"/>
{robot(bob, tilt, lookx, looky, blink, col, gs)}
<circle cx="205" cy="556" r="9" fill="{col}" filter="url(#gl)"/>
<text x="226" y="563" font-family="DejaVu Sans, Arial, sans-serif" font-size="26" font-weight="700" fill="#2a2e35">{label}</text>
</svg>'''
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=S, output_height=S)
    frames.append(Image.open(io.BytesIO(png)).convert("RGB"))

full = os.path.join(HERE, "jac-robot.gif")
frames[0].save(full, save_all=True, append_images=frames[1:], duration=55, loop=0, optimize=True)
lite = [f.resize((460, 460)).convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
lite[0].save(os.path.join(HERE, "jac-robot-lite.gif"), save_all=True, append_images=lite[1:], duration=55, loop=0, optimize=True)
frames[2].save(os.path.join(PNG, "_robot_s.png"))
print("robot anim:", os.path.getsize(full)//1024, "KB | lite", os.path.getsize(os.path.join(HERE,'jac-robot-lite.gif'))//1024, "KB")
