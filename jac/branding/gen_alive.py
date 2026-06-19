#!/usr/bin/env python3
"""Black 'jac' virus — ALIVE: tapered tentacles flow like hair/cloth (traveling
wave + drag), body wobbles, and eyes change color by STATE (green/amber/red)."""
import io, math, os
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); PNG = os.path.join(HERE, "png")
W, H = 640, 620
FRAMES = 48
N = 16
R = 108
BODY_HI, BODY_MID, BODY_LO = "#34383f", "#16191f", "#050609"
SPIKE, TOOTH, MOUTH = "#0a0c10", "#eef1f5", "#000000"

def rnd(i): return (math.sin(i * 12.9898) * 43758.5453) % 1.0
def hx(c): return tuple(int(c[i:i+2], 16) for i in (1, 3, 5))
def lerp(a, b, f): return tuple(int(a[k] + (b[k]-a[k]) * f) for k in range(3))
def hexs(r): return "#%02x%02x%02x" % r

# state machine: color + label by loop position
KEYS = [(0.00, "#33ff6a", "Hammasi joyida"), (0.32, "#33ff6a", "Hammasi joyida"),
        (0.40, "#ffb02e", "O'ylayapman..."), (0.56, "#ffb02e", "O'ylayapman..."),
        (0.64, "#ff2a2a", "Xato topildi!"), (0.86, "#ff2a2a", "Xato topildi!"),
        (1.00, "#33ff6a", "Hammasi joyida")]
def state(t):
    for i in range(len(KEYS)-1):
        if KEYS[i][0] <= t <= KEYS[i+1][0]:
            f = (t-KEYS[i][0]) / ((KEYS[i+1][0]-KEYS[i][0]) or 1)
            return hexs(lerp(hx(KEYS[i][1]), hx(KEYS[i+1][1]), f)), (KEYS[i][2] if f < 0.5 else KEYS[i+1][2])
    return KEYS[-1][1], KEYS[-1][2]

# static faint binary backdrop
MATRIX = "".join(
    f'<text x="{x}" y="{y}" font-family="DejaVu Sans Mono, monospace" font-size="13" '
    f'fill="#1b2630" opacity="{0.05+0.12*rnd(i*31+j*7):.2f}">{"1" if rnd(i*7+j*13)>0.5 else "0"}</text>'
    for j, y in enumerate(range(22, H, 26)) for i, x in enumerate(range(14, W, 26)))

def pos(i):
    t = i / FRAMES
    return W/2 + 120*math.sin(2*math.pi*t), H/2 - 35 + 70*math.sin(4*math.pi*t + 0.6)
POS = [pos(i) for i in range(FRAMES)]
VEL = [(POS[i][0]-POS[i-1][0], POS[i][1]-POS[i-1][1]) for i in range(FRAMES)]

def tentacle(cx, cy, a, length, t, vx, vy, idx, col):
    dx, dy = math.cos(a), math.sin(a); px, py = -dy, dx
    M = 9; amp = R*0.5; dragk = 1.3; base_r = R*0.88
    pts = []
    for k in range(M):
        s = k/(M-1)
        ax = cx + (base_r + length*s)*dx
        ay = cy + (base_r + length*s)*dy
        wave = amp*s*math.sin(t*2.0 + idx*0.8 + s*math.pi*1.6)     # traveling wave
        drx = -vx*dragk*(s**1.6); dry = -vy*dragk*(s**1.6)         # tip trails most
        pts.append((ax + px*wave + drx, ay + py*wave + dry))
    def wid(s): return (R*0.18)*((1-s)**0.85) + R*0.02
    left, right = [], []
    for k in range(M):
        s = k/(M-1)
        if k == 0: tx, ty = pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]
        elif k == M-1: tx, ty = pts[k][0]-pts[k-1][0], pts[k][1]-pts[k-1][1]
        else: tx, ty = pts[k+1][0]-pts[k-1][0], pts[k+1][1]-pts[k-1][1]
        L = math.hypot(tx, ty) or 1; nx, ny = -ty/L, tx/L; w = wid(s)/2
        left.append((pts[k][0]+nx*w, pts[k][1]+ny*w))
        right.append((pts[k][0]-nx*w, pts[k][1]-ny*w))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in left)
    d += " L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in reversed(right)) + " Z"
    tip = pts[-1]
    return (f'<path d="{d}" fill="{SPIKE}"/>'
            f'<circle cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="{R*0.05:.1f}" fill="{col}" filter="url(#gl)"/>')

def body_blob(cx, cy, t):
    Nb = 30; pts = []
    for k in range(Nb):
        ang = k*2*math.pi/Nb
        rad = R*(1 + 0.05*math.sin(t*1.7 + k*1.3) + 0.03*math.sin(t*2.6 + k*0.6))
        pts.append((cx+rad*math.cos(ang), cy+rad*math.sin(ang)))
    d = "M" + f"{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for k in range(1, Nb+1):
        p = pts[k % Nb]; pv = pts[k-1]
        mx, my = (p[0]+pv[0])/2, (p[1]+pv[1])/2
        d += f" Q{pv[0]:.1f} {pv[1]:.1f} {mx:.1f} {my:.1f}"
    return d + " Z"

def eyes(cx, cy, col, blink):
    def one(m):
        s = -1 if m else 1
        pts = [(cx+s*R*0.46, cy-R*0.20), (cx+s*R*0.30, cy-R*0.24),
               (cx+s*R*0.10, cy+R*0.02), (cx+s*R*0.30, cy-R*0.02)]
        if blink < 1:
            ec = cy-R*0.10; pts = [(x, ec+(y-ec)*blink) for x, y in pts]
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
        hot = (f'<circle cx="{cx+s*R*0.30:.1f}" cy="{cy-R*0.10:.1f}" r="{R*0.055*blink:.1f}" fill="#fff"/>') if blink > 0.4 else ""
        return f'<path d="{d}" fill="{col}" filter="url(#gl)"/>' + hot
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
    tl = i/FRAMES; t = tl*2*math.pi
    cx, cy = POS[i]; vx, vy = VEL[i]
    col, label = state(tl)
    gs = 4 + 3*(0.5+0.5*math.sin(t*1.3))
    bp = tl; blink = 0.12 if 0.47 < bp < 0.50 else 1.0
    wob = math.radians(4*math.sin(t))
    strands = "".join(tentacle(cx, cy, k*(2*math.pi/N)+wob, R*(0.7+0.4*rnd(k)), t, vx, vy, k, col) for k in range(N))
    body = (f'<path d="{body_blob(cx, cy, t)}" fill="url(#vb)" stroke="{col}" stroke-width="{R*0.018:.1f}" stroke-opacity="0.55"/>'
            f'<ellipse cx="{cx-R*0.34:.1f}" cy="{cy-R*0.36:.1f}" rx="{R*0.3:.1f}" ry="{R*0.26:.1f}" fill="#fff" opacity="0.10"/>')
    tex = "".join(f'<circle cx="{cx+(R*(0.2+0.5*rnd(k+7)))*math.cos(k*1.3+t*0.2):.1f}" cy="{cy+(R*(0.2+0.5*rnd(k+7)))*math.sin(k*1.3+t*0.2):.1f}" r="{R*0.1:.1f}" fill="#000" opacity="0.22"/>' for k in range(5))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<radialGradient id="vb" cx="0.4" cy="0.34" r="0.75"><stop offset="0" stop-color="{BODY_HI}"/><stop offset="0.6" stop-color="{BODY_MID}"/><stop offset="1" stop-color="{BODY_LO}"/></radialGradient>
<radialGradient id="bgg" cx="0.5" cy="0.42" r="0.8"><stop offset="0" stop-color="#0a0d12"/><stop offset="1" stop-color="#000"/></radialGradient>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{col}" stop-opacity="0.30"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>
<filter id="gl" x="-160%" y="-160%" width="420%" height="420%"><feGaussianBlur stdDeviation="{gs:.1f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bgg)"/>
{MATRIX}
<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="230" ry="230" fill="url(#halo)"/>
{strands}{body}{tex}
{eyes(cx, cy, col, blink)}{mouth(cx, cy)}
<circle cx="{W/2-95:.0f}" cy="{H-34}" r="9" fill="{col}" filter="url(#gl)"/>
<text x="{W/2-75:.0f}" y="{H-28}" font-family="DejaVu Sans, Arial, sans-serif" font-size="24" font-weight="700" fill="{col}">{label}</text>
</svg>'''
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H)
    frames.append(Image.open(io.BytesIO(png)).convert("RGB"))

full = os.path.join(HERE, "jac-alive.gif")
frames[0].save(full, save_all=True, append_images=frames[1:], duration=55, loop=0, optimize=True)
# lite version for delivery
lite = [f.resize((480, 465)).convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
litep = os.path.join(HERE, "jac-alive-lite.gif")
lite[0].save(litep, save_all=True, append_images=lite[1:], duration=55, loop=0, optimize=True)
frames[8].save(os.path.join(PNG, "_alive_s.png"))
print("full", os.path.getsize(full)//1024, "KB | lite", os.path.getsize(litep)//1024, "KB")
