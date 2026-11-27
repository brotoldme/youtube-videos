import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
START, DUR = 0.8, 7.9
RED = (230, 33, 23); GRAY = (62, 60, 56); WHITE = (255, 255, 255)
SS = 4; BH = 84; TOP, RIGHT = 44, 92
S = 0.46
BRO_Y0 = 22
ROPE_SVG_Y = 256
G_ROPE = 150
_F = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
_cache = {}

WALK, PULL, HOLD, BACK, NP = 0.7, 0.6, 0.3, 0.45, 3
T_END = WALK + NP * (PULL + HOLD) + (NP - 1) * BACK
CLICK = T_END + 1.0

def _ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def _pill(text, fill, check=False):
    f = ImageFont.truetype(_F, 38 * SS); tw = f.getlength(text)
    icon = 46 * SS if check else 0
    w, h = int(tw + icon + 64 * SS), BH * SS
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=fill + (255,))
    x = 32 * SS
    if check:
        c = h // 2
        d.line([(x + 4 * SS, c), (x + 14 * SS, c + 11 * SS), (x + 34 * SS, c - 12 * SS)], fill=WHITE, width=7 * SS, joint="curve")
        x += icon
    asc, desc = f.getmetrics()
    d.text((x, (h - asc - desc) // 2 + 2 * SS), text, font=f, fill=WHITE)
    return im.resize((w // SS, h // SS), Image.LANCZOS)

def _bell():
    s = BH * SS; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=GRAY + (255,)); cx = s // 2
    d.pieslice((cx - 20 * SS, 20 * SS, cx + 20 * SS, 60 * SS), 180, 360, fill=WHITE)
    d.polygon([(cx - 20 * SS, 40 * SS), (cx + 20 * SS, 40 * SS), (cx + 26 * SS, 56 * SS), (cx - 26 * SS, 56 * SS)], fill=WHITE)
    d.ellipse((cx - 6 * SS, 54 * SS, cx + 6 * SS, 66 * SS), fill=WHITE)
    d.ellipse((cx - 4 * SS, 15 * SS, cx + 4 * SS, 23 * SS), fill=WHITE)
    return im.resize((BH, BH), Image.LANCZOS)

def _cursor():
    s = 3; pts = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
    im = Image.new("RGBA", (34 * s, 46 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(x * s + 3 * s, y * s + 3 * s) for x, y in pts], fill=WHITE, outline=(0, 0, 0), width=2 * s)
    return im.resize((34, 46), Image.LANCZOS)

def _drop():
    k = 4; w, h = 20, 28; out = (34, 48)
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for i in range(40):
        a = math.pi * 2 * i / 40
        x = math.sin(a) * 8; y = -math.cos(a) * 8
        if y < 0: x *= (1 + y / 8) * 0.9 + 0.1
        pts.append(((10 + x) * k, (18 + (y if y > 0 else y * 1.9)) * k))
    d.polygon(pts, fill=(95, 180, 240, 255), outline=(30, 26, 34, 255), width=2 * k)
    d.ellipse((7 * k, 16 * k, 10 * k, 19 * k), fill=(255, 255, 255, 230))
    return im.resize(out, Image.LANCZOS)

def _layers():
    if not _cache:
        _cache.update(off=_pill("SUBSCRIBE", RED), on=_pill("SUBSCRIBED", GRAY, check=True), bell=_bell(), cur=_cursor(), drop=_drop())
    return _cache

def load_poses(folder):
    out = {}
    for k in ("walk", "look", "happy"):
        im = Image.open(f"{folder}/pose_{k}.png").convert("RGBA")
        h = round(im.height / 2 * S)
        out[k] = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    return out

def _paste(fr, im, x, y, a):
    if a <= 0: return
    m = im.getchannel("A")
    if a < 1: m = m.point(lambda v: int(v * a))
    fr.paste(im, (int(round(x)), int(round(y))), m)

def _rope(fr, p0, p1, sag, a):
    if a <= 0: return
    k = 3
    xs = [p0[0], p1[0]]; ys = [p0[1], p1[1], (p0[1] + p1[1]) / 2 + sag]
    bx0, by0 = int(min(xs)) - 10, int(min(ys)) - 10
    bw, bh = int(max(xs)) - bx0 + 12, int(max(ys)) - by0 + 12
    if bw <= 2 or bh <= 2: return
    lay = Image.new("RGBA", (bw * k, bh * k), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + sag * 2
    pts = []
    for i in range(25):
        u = i / 24
        x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * mx + u ** 2 * p1[0]
        y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * my + u ** 2 * p1[1]
        pts.append(((x - bx0) * k, (y - by0) * k))
    d.line(pts, fill=(30, 26, 34, 255), width=9 * k, joint="curve")
    d.line(pts, fill=(176, 120, 64, 255), width=5 * k, joint="curve")
    lay = lay.resize((bw, bh), Image.LANCZOS)
    _paste(fr, lay, bx0, by0, a)

def _io(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def draw_subscribe_bro(fr, t, poses):
    t -= START
    if t < 0 or t > DUR: return
    L = _layers(); gap = 12
    maxw = max(L["on"].width, L["off"].width)
    x0 = W - RIGHT - (maxw + gap + BH)
    pill_left = x0 + (maxw - L["off"].width)
    bw = poses["walk"].width; bro_h = poses["walk"].height
    fade = 1 - _ease((t - (DUR - 0.5)) / 0.5)
    G = G_ROPE
    R = 46
    B0 = W + 40
    Bk = [B0 + k * (pill_left - B0) / NP for k in range(NP + 1)]
    def state(tt):
        if tt < WALK:
            u = _ease(tt / WALK); target = Bk[0] - G + R
            return W + 60 + bw + (target - W - 60 - bw) * u, Bk[0], "walk", u
        tt -= WALK
        for k in range(NP):
            last = k == NP - 1
            cyc = PULL + HOLD + (0 if last else BACK)
            if tt < cyc or last:
                if tt < PULL:
                    u = tt / PULL
                    br_ = (Bk[k] - G + R) + ((Bk[k + 1] - G) - (Bk[k] - G + R)) * _io(u)
                    bl = Bk[k] + (Bk[k + 1] - Bk[k]) * _io((u - 0.25) / 0.75)
                    return br_, bl, "pull", u
                if tt < PULL + HOLD or last:
                    return Bk[k + 1] - G, Bk[k + 1], "hold", min(1, (tt - PULL) / HOLD)
                u = (tt - PULL - HOLD) / BACK
                return Bk[k + 1] - G + R * _io(u), Bk[k + 1], "back", u
            tt -= cyc
    bro_r, btn_l, ph, u = state(t)
    bro_x = bro_r - bw + 14
    btn_dx = btn_l - pill_left
    hop = abs(math.sin(t * math.pi * 5)) * 10 if ph == "walk" else 0
    if ph == "back": hop = math.sin(u * math.pi) * 8
    tilt = {"walk": -4 + 2 * math.sin(t * math.pi * 10), "pull": -9 * math.sin(min(1, u) * math.pi),
            "hold": -3 * (1 - u), "back": 3 * math.sin(u * math.pi)}[ph]
    if t >= T_END: tilt = 0
    if ph == "hold" and t < T_END + 0.4:
        btn_dx -= math.sin(min(1, u) * math.pi) * 8
    click = CLICK
    on = t >= click
    pose = "walk" if t < T_END + 0.2 else ("happy" if click + 0.1 <= t < click + 1.8 else "look")
    jump = math.sin(math.pi * (t - click - 0.1) / 0.45) * 12 if click + 0.1 <= t < click + 0.55 else 0
    bro_y = BRO_Y0 - hop - jump
    rope_a = (1 - _ease((t - T_END - 0.3) / 0.4)) * fade
    sag = {"walk": 18, "pull": 18 * (1 - min(1, u * 3)) + 3, "hold": 3 + 10 * u, "back": 13 + 10 * u}[ph]
    _rope(fr, (bro_x + bw - 14, bro_y + ROPE_SVG_Y * S), (pill_left + btn_dx + 12, TOP + BH / 2), sag, rope_a)
    s0 = 0.0
    while s0 <= min(t, T_END):
        r_, _, phs, _ = state(s0)
        if phs in ("pull", "hold"):
            age = t - s0
            if 0 <= age < 0.75:
                seed = int(s0 * 100)
                side = 1 if seed % 3 else -1
                ex = (r_ - bw + 14) + (bw * 0.88 if side > 0 else bw * 0.12)
                ey = BRO_Y0 + bro_h * (0.40 + 0.05 * (seed % 4))
                vx = side * (110 + 40 * (seed % 5)); vy = -(150 + 25 * (seed % 4))
                dx = ex + vx * age; dy = ey + vy * age + 0.5 * 900 * age * age
                _paste(fr, L["drop"], dx - 17, dy - 24, (1 - age / 0.75) * fade)
        s0 += 0.09
    btn = L["on"] if on else L["off"]
    sc = 1.0
    if click - 0.08 <= t < click + 0.12:
        sc = 0.93 if t < click + 0.04 else 1.0 + 0.04 * (1 - (t - click - 0.04) / 0.08)
    b = btn if sc == 1.0 else btn.resize((int(btn.width * sc), int(btn.height * sc)), Image.LANCZOS)
    bx = x0 + btn_dx + (maxw - btn.width) + (btn.width - b.width) / 2
    by = TOP + (btn.height - b.height) / 2
    _paste(fr, b, bx, by, fade)
    ang = 22 * math.sin((t - click - 0.3) * 2 * math.pi * 3.5) * (1 - (t - click - 0.3)) if click + 0.3 <= t < click + 1.3 else 0
    bell = L["bell"].rotate(ang, resample=Image.BICUBIC) if ang else L["bell"]
    _paste(fr, bell, x0 + maxw + gap + btn_dx, TOP, fade)
    im = poses[pose]
    if tilt: im = im.rotate(tilt, resample=Image.BICUBIC, expand=False)
    _paste(fr, im, bro_x, bro_y, fade)
    cur = L["cur"]; tx, ty = x0 + maxw - L["off"].width * 0.38, TOP + BH * 0.55
    if T_END + 0.3 <= t < click + 0.9:
        q = _ease((t - T_END - 0.3) / (click - T_END - 0.4))
        cx, cy = tx + (1 - q) * 220, ty + (1 - q) * 260
        ca = min(1, (t - T_END - 0.3) / 0.2) * (1 - _ease((t - click - 0.5) / 0.4))
        if t >= click:
            e = _ease((t - click - 0.3) / 0.6); cx, cy = tx + e * 60, ty + e * 80
        _paste(fr, cur, cx, cy, ca * fade)
