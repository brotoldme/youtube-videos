import sys, os, subprocess, base64

INK = "#1E1A22"; NAVY = "#23315C"; YEL = "#FFD23F"; SKIN = "#BFE3F7"; SAND = "#D2BC8A"
SHADOW = f'<ellipse cx="200" cy="358" rx="146" ry="13" fill="{INK}" opacity=".12"/>'
BODY = f'<path d="M84 290 L316 290 L322 350 Q200 362 78 350 Z" fill="{SKIN}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
DOMES = "M78 252 C78 148 134 92 200 92 C266 92 322 148 322 252 Z"
BRIMS = "M52 262 Q52 238 84 238 L316 238 Q348 238 348 262 L348 280 Q348 298 320 298 L80 298 Q52 298 52 280 Z"
BADGE = (f'<circle cx="200" cy="170" r="32" fill="{NAVY}" stroke="{INK}" stroke-width="5"/>'
         f'<circle cx="200" cy="170" r="22" fill="none" stroke="{YEL}" stroke-width="5"/>'
         f'<ellipse cx="200" cy="170" rx="9" ry="22" fill="none" stroke="{YEL}" stroke-width="4"/>'
         f'<path d="M178 170H222M182 158H218M182 182H218" stroke="{YEL}" stroke-width="4" fill="none"/>')


def helmet(dome=SAND, brim=SAND, band="#6B4A2B", knob=SAND, badge=BADGE, uid="x"):
    return (f'<path d="{DOMES}" fill="{dome}"/><clipPath id="s{uid}"><path d="{DOMES}"/></clipPath>'
            f'<rect x="60" y="214" width="280" height="34" fill="{band}" clip-path="url(#s{uid})"/>'
            f'<path d="M124 146 Q140 120 170 112" stroke="#fff" stroke-opacity=".45" stroke-width="9" fill="none" stroke-linecap="round"/>'
            f'<path d="M200 92V214M150 100 Q140 160 134 214M250 100 Q260 160 266 214" stroke="{INK}" stroke-opacity=".12" stroke-width="4" fill="none"/>'
            f'<path d="{DOMES}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            f'<rect x="60" y="214" width="280" height="34" fill="none" stroke="{INK}" stroke-width="3" clip-path="url(#s{uid})"/>'
            f'<circle cx="200" cy="90" r="11" fill="{knob}" stroke="{INK}" stroke-width="5"/>'
            + badge +
            f'<path d="{BRIMS}" fill="{brim}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')


def brows2(l, r):
    s = ''
    for d in (l, r):
        s += f'<path d="{d}" stroke="{NAVY}" stroke-width="23" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        s += f'<path d="{d}" stroke="{YEL}" stroke-width="15" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    return s

_b64 = base64.b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag_iran.svg"), "rb").read()).decode()
FLAGS = {
 "iran": f'<rect width="60" height="36" fill="#fff"/><image x="0" y="0" width="60" height="36" preserveAspectRatio="none" href="data:image/svg+xml;base64,{_b64}"/>',
}


def flag_on_helmet(key):
    return (f'<rect x="198" y="12" width="5" height="80" rx="2" fill="#5A3A1E" stroke="{INK}" stroke-width="3"/>'
            f'<g transform="translate(203 14) scale(1.25 1.25)"><clipPath id="fl"><rect width="60" height="36" rx="2"/></clipPath>'
            f'<g clip-path="url(#fl)">{FLAGS[key]}</g><rect width="60" height="36" rx="2" fill="none" stroke="{INK}" stroke-width="2.6"/></g>')


def eyes_walk():
    s = ''.join(f'<ellipse cx="{x}" cy="338" rx="15" ry="7" fill="#FF6F7D" opacity=".8"/>' for x in (112, 288))
    s += f'<ellipse cx="160" cy="318" rx="24" ry="28" fill="{SKIN}"/><ellipse cx="240" cy="318" rx="24" ry="28" fill="{SKIN}"/>'
    s += f'<path d="M144 306 L172 320 L144 334" stroke="{INK}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    s += f'<path d="M256 306 L228 320 L256 334" stroke="{INK}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    return s

def eyes_look():
    s = ''
    for x in (160, 240):
        s += (f'<ellipse cx="{x}" cy="318" rx="24" ry="28" fill="#fff" stroke="{INK}" stroke-width="4"/>'
              f'<circle cx="{x+9}" cy="318" r="10" fill="{INK}"/><circle cx="{x+13}" cy="313.5" r="3.3" fill="#fff"/>')
    return s

def eyes_happy():
    s = ''
    for x in (160, 240):
        s += f'<ellipse cx="{x}" cy="318" rx="24" ry="28" fill="{SKIN}"/>'
        s += f'<path d="M{x-18} 326 Q{x} 300 {x+18} 326" stroke="{INK}" stroke-width="7" fill="none" stroke-linecap="round"/>'
    return s

BROWS = {
 "walk":  brows2("M126 270 Q156 256 186 266", "M214 266 Q244 256 274 270"),
 "look":  brows2("M126 276 Q156 250 186 268", "M214 268 Q244 250 274 276"),
 "happy": brows2("M126 266 Q156 240 186 258", "M214 258 Q244 240 274 266"),
}
EYES = {"walk": eyes_walk, "look": eyes_look, "happy": eyes_happy}
CFG = {"iran": dict(flag="iran", scarf=False, vb="40 0 320 380")}

def pose_svg(pose, country):
    c = CFG[country]
    x0, y0, w, h = [float(v) for v in c["vb"].split()]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{c["vb"]}" width="{int(w*2)}" height="{int(h*2)}">'
            f'{SHADOW}{BODY}{EYES[pose]()}{helmet()}{BROWS[pose]}{flag_on_helmet(c["flag"])}</svg>')

if __name__ == "__main__":
    out, country = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for p in ("walk", "look", "happy"):
        f = os.path.join(out, f"pose_{p}.svg")
        open(f, "w").write(pose_svg(p, country))
        subprocess.run(["rsvg-convert", "-h", "880", f, "-o", f[:-4] + ".png"], check=True)
    print("ok", country)
