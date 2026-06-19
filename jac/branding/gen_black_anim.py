#!/usr/bin/env python3
"""Black 'jac' virus with ORGANIC motion — tentacles sway like hair/cloth and
trail behind when it moves. Cinematic floating loop."""
import io, math, os
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "png")

AC = dict(eye="#ff3b3b", hot="#fff2f0", glow="#ff2a2a", matrix="#4a1414")
BODY_HI, BODY_MID, BODY_LO = "#34383f", "#16191f", "#050609"
SPIKE, TOOTH, MOUTH = "#0a0c10", "#eef1f5", "#000000"

W, H = 720, 600
FRAMES = 48
N = 20                      # number of flowing tentacles
R = 110

def rnd(i):
    return (math.sin(i * 12.9898) * 43758.5453) % 1.0

def matrix_bg():
    out = ""
    for j, y in enumerate(range(22, H, 26)):
        for i, x in enumerate(range(14, W, 26)):
            op = 0.04 + 0.13 * rnd(i * 31 + j * 7)
            ch = "1" if rnd(i * 7 + j * 13) > 0.5 else "0"
            out += (f'<text x="{x}" y="{y}" font-family="DejaVu Sans Mono, monospace" '
                    f'font-size="14" fill="{AC["matrix"]}" opacity="{op:.2f}">{ch}</text>')
    return out
MATRIX = matrix_bg()

# ---- precompute a smooth periodic float path + per-frame velocity ----
def pos(i):
    t = i / FRAMES
    cx = W / 2 + 130 * math.sin(2 * math.pi * t)
    cy = H / 2 - 30 + 80 * math.sin(4 * math.pi * t + 0.6)
    return cx, cy
POS = [pos(i) for i in range(FRAMES)]
VEL = [(POS[i][0] - POS[i - 1][0], POS[i][1] - POS[i - 1][1]) for i in range(FRAMES)]

def strand(cx, cy, a, length, t, vx, vy, idx):
    """One flowing tentacle: base on body, tip sways (idle) + trails (drag)."""
    dx, dy = math.cos(a), math.sin(a)          # radial dir
    px, py = -dy, dx                            # perpendicular
    bx, by = cx + R * 0.9 * dx, cy + R * 0.9 * dy
    rtx, rty = cx + (R + length) * dx, cy + (R + length) * dy   # rest tip
    sway = 0.22 * math.sin(t * 2.2 + idx * 0.9)                 # idle hair sway
    dragk = 1.5                                                  # trail behind motion
    offx = px * length * sway - vx * dragk
    offy = py * length * sway - vy * dragk
    tipx, tipy = rtx + offx, rty + offy
    # control point: bends the strand smoothly (curve concentrated near the tip)
    cxp = bx + (rtx - bx) * 0.55 + offx * 0.45
    cyp = by + (rty - by) * 0.55 + offy * 0.45
    w = max(R * 0.11 * (0.6 + 0.4 * rnd(idx + 3)), 2)
    knob = R * 0.095
    return (f'<path d="M{bx:.1f} {by:.1f} Q{cxp:.1f} {cyp:.1f} {tipx:.1f} {tipy:.1f}" '
            f'fill="none" stroke="{SPIKE}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
            f'<circle cx="{tipx:.1f}" cy="{tipy:.1f}" r="{knob:.1f}" fill="{SPIKE}" '
            f'stroke="{AC["glow"]}" stroke-width="{R*0.02:.1f}"/>'
            f'<circle cx="{tipx:.1f}" cy="{tipy:.1f}" r="{R*0.03:.1f}" fill="{AC["glow"]}" filter="url(#gl)"/>')

def eyes(cx, cy, blink):
    def one(mirror):
        s = -1 if mirror else 1
        pts = [(cx + s*R*0.46, cy-R*0.20), (cx + s*R*0.30, cy-R*0.24),
               (cx + s*R*0.10, cy+R*0.02), (cx + s*R*0.30, cy-R*0.02)]
        if blink < 1:  # squash vertically toward eye center for a blink
            ecy = cy - R*0.10
            pts = [(x, ecy + (y-ecy)*blink) for x, y in pts]
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
        hot = f'<circle cx="{cx+s*R*0.30:.1f}" cy="{cy-R*0.10:.1f}" r="{R*0.06*blink:.1f}" fill="{AC["hot"]}"/>' if blink > 0.4 else ""
        return f'<path d="{d}" fill="{AC["eye"]}" filter="url(#gl)"/>' + hot
    return one(False) + one(True)

def mouth(cx, cy):
    mw = R*1.0; ml = cx-mw/2; midy = cy+R*0.40; th = R*0.20; nt = 6; tw = mw/nt
    m = (f'<path d="M{ml:.1f} {midy-th*0.7:.1f} Q{cx:.1f} {cy+R*0.86:.1f} {ml+mw:.1f} {midy-th*0.7:.1f} '
         f'L{ml+mw:.1f} {midy:.1f} Q{cx:.1f} {cy+R*0.66:.1f} {ml:.1f} {midy:.1f} Z" fill="{MOUTH}"/>')
    for i in range(nt):
        x = ml+i*tw
        m += f'<path d="M{x:.1f} {midy-th*0.7:.1f} L{x+tw:.1f} {midy-th*0.7:.1f} L{x+tw/2:.1f} {midy+th*0.4:.1f} Z" fill="{TOOTH}"/>'
    for i in range(nt):
        x = ml+i*tw+tw/2
        m += f'<path d="M{x:.1f} {midy+th*0.9:.1f} L{x+tw:.1f} {midy+th*0.9:.1f} L{x+tw/2:.1f} {midy-th*0.1:.1f} Z" fill="{TOOTH}" opacity="0.92"/>'
    return m

frames = []
for i in range(FRAMES):
    t = i / FRAMES * 2 * math.pi
    cx, cy = POS[i]; vx, vy = VEL[i]
    breathe = 0.04 * math.sin(t * 1.5)
    rx, ry = R * (1 + breathe), R * (1 - breathe)
    gs = 4 + 3 * (0.5 + 0.5 * math.sin(t * 1.3))       # glow pulse
    # blink: closed briefly once per loop
    bp = (i % FRAMES) / FRAMES
    blink = 0.12 if 0.46 < bp < 0.50 else 1.0
    wob = math.radians(4 * math.sin(t))                # tiny rotation wobble
    strands = "".join(
        strand(cx, cy, i2 * (2*math.pi/N) + wob, R * (0.42 + 0.28 * rnd(i2)), t, vx, vy, i2)
        for i2 in range(N))
    body = (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#vb)" '
            f'stroke="{AC["glow"]}" stroke-width="{R*0.02:.1f}" stroke-opacity="0.5"/>'
            f'<ellipse cx="{cx-R*0.34:.1f}" cy="{cy-R*0.36:.1f}" rx="{R*0.3:.1f}" ry="{R*0.26:.1f}" fill="#fff" opacity="0.10"/>')
    tex = ""
    for k in range(5):
        ang = k*1.3 + t*0.2; rr = R*(0.2+0.5*rnd(k+7))
        tex += f'<circle cx="{cx+rr*math.cos(ang):.1f}" cy="{cy+rr*math.sin(ang):.1f}" r="{R*0.1:.1f}" fill="#000" opacity="0.22"/>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<radialGradient id="vb" cx="0.4" cy="0.34" r="0.75"><stop offset="0" stop-color="{BODY_HI}"/><stop offset="0.6" stop-color="{BODY_MID}"/><stop offset="1" stop-color="{BODY_LO}"/></radialGradient>
<radialGradient id="bgg" cx="0.5" cy="0.45" r="0.75"><stop offset="0" stop-color="#0a0d12"/><stop offset="1" stop-color="#000"/></radialGradient>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{AC['glow']}" stop-opacity="0.30"/><stop offset="1" stop-color="{AC['glow']}" stop-opacity="0"/></radialGradient>
<filter id="gl" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="{gs:.1f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bgg)"/>
{MATRIX}
<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="220" ry="220" fill="url(#halo)"/>
{strands}
{body}{tex}
{eyes(cx, cy, blink)}
{mouth(cx, cy)}
</svg>'''
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H)
    frames.append(Image.open(io.BytesIO(png)).convert("RGB"))

gif = os.path.join(HERE, "black-organic.gif")
frames[0].save(gif, save_all=True, append_images=frames[1:], duration=55, loop=0, optimize=True)
print("organic animation:", os.path.getsize(gif)//1024, "KB", FRAMES, "frames")
