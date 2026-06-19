#!/usr/bin/env python3
"""Animated preview of the v2 (3D-look) jac robot: bob, head tilt, look-around,
blink, and state-based eye colors. (Real-time 3D lives in jac/app/index.html.)"""
import io, math, os, cairosvg
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); PNG = os.path.join(HERE, "png")
S = 600

def hx(c): return tuple(int(c[i:i+2],16) for i in (1,3,5))
def lp(a,b,f): return tuple(int(a[k]+(b[k]-a[k])*f) for k in range(3))
def hexs(r): return "#%02x%02x%02x"%r
KEYS=[(0.00,"#37d6ff","Salom!"),(0.24,"#37d6ff","Salom!"),
      (0.31,"#33ff6a","Tayyorman"),(0.50,"#33ff6a","Tayyorman"),
      (0.57,"#ffb02e","O'ylayapman..."),(0.72,"#ffb02e","O'ylayapman..."),
      (0.80,"#ff4d4d","Xato topildi!"),(0.94,"#ff4d4d","Xato topildi!"),
      (1.00,"#37d6ff","Salom!")]
def state(t):
    for i in range(len(KEYS)-1):
        if KEYS[i][0]<=t<=KEYS[i+1][0]:
            f=(t-KEYS[i][0])/((KEYS[i+1][0]-KEYS[i][0]) or 1)
            return hexs(lp(hx(KEYS[i][1]),hx(KEYS[i+1][1]),f)),(KEYS[i][2] if f<0.5 else KEYS[i+1][2])
    return KEYS[-1][1],KEYS[-1][2]

def frame_svg(bob,tilt,lookx,looky,blink,col,gs,label):
    eh=52*blink; ey=240+looky-eh/2
    def eye(ex):
        x=ex+lookx
        s=f'<rect x="{x-20:.1f}" y="{ey:.1f}" width="40" height="{eh:.1f}" rx="15" fill="url(#eye)" filter="url(#gl)"/>'
        if blink>0.45: s+=f'<rect x="{x-14:.1f}" y="{ey+6:.1f}" width="15" height="{eh*0.4:.1f}" rx="7" fill="#fff"/>'
        return s
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs>
<radialGradient id="bg" cx="0.5" cy="0.36" r="0.9"><stop offset="0" stop-color="#eef2f6"/><stop offset="0.7" stop-color="#d4dbe3"/><stop offset="1" stop-color="#b1bac4"/></radialGradient>
<linearGradient id="head" x1="0.15" y1="0.05" x2="0.85" y2="1"><stop offset="0" stop-color="#5b626b"/><stop offset="0.5" stop-color="#3a4047"/><stop offset="1" stop-color="#202429"/></linearGradient>
<linearGradient id="body" x1="0.2" y1="0" x2="0.8" y2="1"><stop offset="0" stop-color="#4d535b"/><stop offset="1" stop-color="#1c2025"/></linearGradient>
<radialGradient id="ao" cx="0.5" cy="0.42" r="0.62"><stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.40"/></radialGradient>
<radialGradient id="panel" cx="0.5" cy="0.35" r="0.8"><stop offset="0" stop-color="#1a1f25"/><stop offset="1" stop-color="#04060a"/></radialGradient>
<linearGradient id="eye" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{col}"/></linearGradient>
<radialGradient id="floor" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#000" stop-opacity="0.32"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<filter id="soft"><feGaussianBlur stdDeviation="10"/></filter>
<filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="{gs:.1f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="hc"><rect x="158" y="96" width="284" height="270" rx="96"/></clipPath>
</defs>
<rect width="{S}" height="{S}" fill="url(#bg)"/>
<ellipse cx="300" cy="500" rx="{170*(1-bob*0.01):.0f}" ry="{40*(1-bob*0.01):.0f}" fill="url(#floor)"/>
<g transform="translate(0 {bob:.1f})">
  <rect x="222" y="356" width="156" height="118" rx="52" fill="url(#body)"/>
  <rect x="222" y="356" width="156" height="118" rx="52" fill="url(#ao)"/>
  <rect x="240" y="360" width="120" height="40" rx="20" fill="#ffffff" opacity="0.08"/>
  <rect x="270" y="330" width="60" height="40" rx="18" fill="#2a2f35"/>
  <g transform="rotate({tilt:.2f} 300 350)">
    <rect x="166" y="104" width="284" height="270" rx="96" fill="#0e1116" opacity="0.5"/>
    <rect x="158" y="96" width="284" height="270" rx="96" fill="url(#head)"/>
    <g clip-path="url(#hc)">
      <ellipse cx="240" cy="150" rx="120" ry="70" fill="#ffffff" opacity="0.16" filter="url(#soft)"/>
      <rect x="158" y="96" width="284" height="270" rx="96" fill="url(#ao)"/>
    </g>
    <rect x="196" y="150" width="208" height="172" rx="66" fill="#0a0d12"/>
    <rect x="202" y="156" width="196" height="160" rx="60" fill="url(#panel)"/>
    {eye(272)}{eye(328)}
    <circle cx="300" cy="124" r="6" fill="{col}" filter="url(#gl)"/>
  </g>
</g>
<circle cx="200" cy="560" r="9" fill="{col}" filter="url(#gl)"/>
<text x="222" y="568" font-family="DejaVu Sans, Arial, sans-serif" font-size="26" font-weight="700" fill="#2a2e35">{label}</text>
</svg>'''

FRAMES=48; frames=[]
for i in range(FRAMES):
    tl=i/FRAMES; t=tl*2*math.pi
    col,label=state(tl)
    bob=7*math.sin(t)
    tilt=5*math.sin(t*0.5+0.4)
    lookx=10*math.sin(t*0.7+1.0)
    looky=3*math.sin(t*1.1)
    gs=4+3*(0.5+0.5*math.sin(t*1.4))
    blink=1.0
    for bc in (0.21,0.67):
        d=min(abs(tl-bc),abs(tl-bc+1),abs(tl-bc-1))
        if d<0.022: blink=0.12
    svg=frame_svg(bob,tilt,lookx,looky,blink,col,gs,label)
    frames.append(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=S,output_height=S))).convert("RGB"))

full=os.path.join(HERE,"jac-robot3d.gif")
frames[0].save(full,save_all=True,append_images=frames[1:],duration=55,loop=0,optimize=True)
lite=[f.resize((460,460)).convert("P",palette=Image.ADAPTIVE,colors=128) for f in frames]
lite[0].save(os.path.join(HERE,"jac-robot3d-lite.gif"),save_all=True,append_images=lite[1:],duration=55,loop=0,optimize=True)
frames[3].save(os.path.join(PNG,"_r3d.png"))
print("ok", os.path.getsize(full)//1024,"KB | lite",os.path.getsize(os.path.join(HERE,'jac-robot3d-lite.gif'))//1024,"KB")
