import json, subprocess
from PIL import Image, ImageDraw, ImageFont
SENT = json.load(open('/home/claude/w/v8/voix_sent.json'))
ST = {i + 1: x['start'] for i, x in enumerate(SENT)}
F0 = ST[35] - 2.02; TOT = F0 + 9.6
F = lambda s: ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Black.otf', s)
YEL = (255, 210, 63); WHITE = (255, 255, 255); RED = (255, 46, 59)
caps = []  # (png, start, end)
def cap(name, parts, a, b, size=66):
    # parts: liste de (texte, couleur)
    f = F(size); w = sum(ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(t, font=f) for t, _ in parts)
    pad = 28; im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0 = 90, 880; d.rounded_rectangle((x0, y0, x0 + w + 2 * pad, y0 + size + 2 * pad - 6), radius=22, fill=(0, 0, 0, 170))
    x = x0 + pad
    for t, c in parts:
        d.text((x, y0 + pad - 8), t, font=f, fill=c); x += d.textlength(t, font=f)
    p = f'/home/claude/w/v8/cap_{name}.png'; im.save(p); caps.append((p, a, b))
def pill(a, b):
    f = F(60); t = "DON'T"; d0 = ImageDraw.Draw(Image.new('RGB', (1, 1))); w = d0.textlength(t, font=f)
    im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 60, 70 + w + 64, 60 + 96), radius=48, fill=(230, 33, 23, 255)); d.text((102, 60 + 14), t, font=f, fill=WHITE)
    p = '/home/claude/w/v8/pill_dont.png'; im.save(p); caps.append((p, a, b))
def title(a, b):
    f = F(150); t = "THE DON'T LIST"; d0 = ImageDraw.Draw(Image.new('RGB', (1, 1))); w = d0.textlength(t, font=f)
    im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((960 - w / 2 - 50, 400, 960 + w / 2 + 50, 400 + 230), radius=30, fill=(0, 0, 0, 150))
    d.text((960 - w / 2, 430), "THE ", font=f, fill=WHITE); wt = d.textlength("THE ", font=f)
    d.text((960 - w / 2 + wt, 430), "DON'T", font=f, fill=RED); wd = d.textlength("DON'T ", font=f)
    d.text((960 - w / 2 + wt + wd, 430), "LIST", font=f, fill=WHITE)
    p = '/home/claude/w/v8/title_dont.png'; im.save(p); caps.append((p, a, b))
cap('m1', [('$10 ', YEL), ('≈ 27,000,000 RIALS', WHITE)], ST[18] + 0.2, ST[18] + 4.7)
cap('m1b', [('OPEN-MARKET RATE, NOV. 2026', WHITE)], ST[18] + 4.9, ST[19] - 0.1, 56)
L = ST[20] - ST[19]
t1, t2 = ST[19] + 3.18, ST[19] + 5.33
cap('m2', [('METRO RIDE ', WHITE), ('≈ $0.10', YEL)], ST[19] + 0.1, t1)
cap('m3', [('CHEAP LUNCH ', WHITE), ('≈ $3.50', YEL)], t1, t2)
cap('m4', [('TAXI-APP RIDE ', WHITE), ('$1–4', YEL)], t2, ST[20] - 0.1)
cap('m5', [('DINNER FOR TWO ', WHITE), ('≈ $17', YEL)], ST[20] + 0.1, ST[21] - 0.1)
title(ST[21] - 0.05, ST[22] - 0.15)
pill(ST[22] - 0.05, ST[27] - 0.2)
cap('d1', [('NO PHOTOS: ', YEL), ('GOVERNMENT, POLICE, MILITARY', WHITE)], ST[22] + 0.2, ST[23] - 0.1, 56)
cap('d2', [('NO FOREIGN CARDS. ', YEL), ('BRING CASH.', WHITE)], ST[23] + 0.2, ST[24] - 0.1)
cap('d3', [('DRESS CODE ', YEL), ('APPLIES TO VISITORS', WHITE)], ST[24] + 0.2, ST[25] - 0.1)
cap('d5', [('FIRST "IT\'S FREE" ', YEL), ('IS TAAROF', WHITE)], ST[26] + 0.3, ST[27] - 0.1)
S0 = 0.75 * TOT - 0.8
print('SUBSCRIBE bouton a', round(S0 + 0.8, 2), 'soit', round((S0 + 0.8) / TOT * 100, 1), '%; clic', round(S0 + 0.8 + 3.55 + 1.0, 1) if False else '')
inputs = ['-f', 'concat', '-safe', '0', '-i', '/home/claude/w/seg8/list.txt']
for p, a, b in caps: inputs += ['-i', p]
inputs += ['-framerate', '30', '-i', '/home/claude/w/sub/fr/%04d.png', '-i', '/home/claude/w/v8/mix.wav']
n = len(caps); fc = ''; last = '[0:v]'
for k, (p, a, b) in enumerate(caps):
    fc += f"{last}[{k+1}:v]overlay=enable='between(t,{a:.3f},{b:.3f})'[o{k}];"; last = f'[o{k}]'
fc += f"[{n+1}:v]format=rgba,setpts=PTS+{S0:.3f}/TB[sb];{last}[sb]overlay=enable='between(t,{S0:.3f},{S0+8.8:.3f})':eof_action=pass,format=yuv420p[v]"
cmd = ['ffmpeg', '-loglevel', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[v]', '-map', f'{n+2}:a', '-t', f'{TOT:.3f}',
       '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '2.7M', '-maxrate', '3.1M', '-bufsize', '6M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '/home/claude/w/v8/long_v8.mp4']
subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)
print('ok', round(TOT, 2))
