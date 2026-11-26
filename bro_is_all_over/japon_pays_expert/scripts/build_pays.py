import subprocess, json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
os.makedirs('seg2', exist_ok=True)
S = json.load(open('voix_pays_sent.json'))
P = {x['n']: x['start'] for x in S}.__getitem__
FIN_START = P(31)
FIN_LEN = 9.6
# (nom, source, ss, t début, t fin, params)  params stills : zs, ze, fx, fy ; clips : sens
plan = [
 ('s01', '../clips/53789.mp4', 1, 0, P(2), {'sens': 1}),
 ('s02', 'wm2/dejima_bay.jpg', 0, P(2), P(3), dict(zs=1.0, ze=1.10, fx=.2, fy=.5)),
 ('s03', 'wm2/kurofune_photo.jpg', 0, P(3), P(4), dict(zs=1.0, ze=1.10, fx=.5, fy=.5)),
 ('map', '../intro_map.mp4', 0, P(4), P(4) + 7.6, {}),
 ('s05', '../clips/275983.mp4', 1, P(4) + 7.6, P(6), {'sens': 1}),
 ('s06', '../clips/23525.mp4', 1, P(6), P(7), {'sens': -1}),
 ('s07', 'wm2/stillfried.jpg', 0, P(7), P(8), dict(zs=1.0, ze=1.08, fx=.5, fy=.3)),
 ('s08', 'wm2/dejima_keiga.jpg', 0, P(8), P(9), dict(zs=1.0, ze=1.12, fx=.3, fy=.6)),
 ('s09a', 'wm2/plattegrond.jpg', 0, P(9), P(9) + 5.0, dict(zs=1.0, ze=1.25, fx=.3, fy=.4)),
 ('s09b', 'wm2/plattegrond.jpg', 0, P(9) + 5.0, P(10), dict(zs=1.3, ze=1.0, fx=.7, fy=.6)),
 ('s10', 'wm2/dejima_scroll.jpg', 0, P(10), P(11), dict(zs=1.0, ze=1.18, fx=.8, fy=.4)),
 ('s11', 'wm2/kaitai.jpg', 0, P(11), P(12), dict(zs=1.0, ze=1.08, fx=.5, fy=.5)),
 ('s12', 'wm2/kurofune_print.jpg', 0, P(12), P(13), dict(zs=1.0, ze=1.15, fx=.8, fy=.7)),
 ('s13', 'wm2/kurofune3.jpg', 0, P(13), P(14), dict(zs=1.0, ze=1.10, fx=.5, fy=.5)),
 ('s14', 'wm2/perry_print.jpg', 0, P(14), P(15), dict(zs=1.0, ze=1.08, fx=.5, fy=.2)),
 ('s15a', 'wm2/perry_kanagawa.jpg', 0, P(15), P(15) + 4.2, dict(zs=1.0, ze=1.2, fx=.2, fy=.5)),
 ('s15b', 'wm2/perry_kanagawa.jpg', 0, P(15) + 4.2, P(16), dict(zs=1.25, ze=1.0, fx=.8, fy=.5)),
 ('s16', '../clips/33821.mp4', 1, P(16), P(17), {'sens': 1}),
 ('s17', '../clips/248449.mp4', 1, P(17), P(18), {'sens': -1}),
 ('s18', 'wm2/satsuma_boshin.jpg', 0, P(18), P(19), dict(zs=1.0, ze=1.1, fx=.5, fy=.5)),
 ('s19', 'wm2/meiji.jpg', 0, P(19), P(20), dict(zs=1.0, ze=1.08, fx=.5, fy=.25)),
 ('s20', 'wm2/train_yoko.jpg', 0, P(20), P(21), dict(zs=1.0, ze=1.15, fx=.2, fy=.6)),
 ('s21', 'wm2/saigo_off.jpg', 0, P(21), P(22), dict(zs=1.0, ze=1.12, fx=.4, fy=.5)),
 ('s22', 'wm2/samurai_beato.jpg', 0, P(22), P(23), dict(zs=1.0, ze=1.12, fx=.5, fy=.4)),
 ('s23a', 'wm2/shiroyama.jpg', 0, P(23), P(23) + 4.6, dict(zs=1.0, ze=1.12, fx=.3, fy=.5)),
 ('s23b', 'wm2/tabaruzaka.jpg', 0, P(23) + 4.6, P(24), dict(zs=1.0, ze=1.12, fx=.7, fy=.5)),
 ('s24', 'wm2/genkan.jpg', 0, P(24), P(25), dict(zs=1.0, ze=1.12, fx=.5, fy=.8)),
 ('s25', 'wm2/slippers_house.jpg', 0, P(25), P(26), dict(zs=1.0, ze=1.12, fx=.3, fy=.5)),
 ('s26', 'wm2/slippers_white.jpg', 0, P(26), P(27), dict(zs=1.0, ze=1.1, fx=.5, fy=.5)),
 ('s27a', 'wm2/toilet_squat.jpg', 0, P(27), P(27) + 5.2, dict(zs=1.0, ze=1.12, fx=.5, fy=.8)),
 ('s27b', 'wm2/toilet_closeup.jpg', 0, P(27) + 5.2, P(28), dict(zs=1.0, ze=1.1, fx=.5, fy=.5)),
 ('s28', '../clips/268537.mp4', 1, P(28), P(29), {'sens': 1}),
 ('s29', '../clips/84908.mp4', 1, P(29), P(30), {'sens': -1}),
 ('s30', '../clips/321038.mp4', 1, P(30), P(31), {'sens': 1}),
]
ENC = ['-c:v', 'libx264', '-crf', '17', '-preset', 'veryfast']


def clip_vf(d, sens):
    f = f"t/{d}" if sens == 1 else f"1-t/{d}"
    return ("scale=2112:1188:force_original_aspect_ratio=increase,"
            f"crop=1920:1080:x='(iw-1920)*({f})':y='(ih-1080)/2',fps=30,format=yuv420p")


def run(p):
    nm, src, ss, a, b, pr = p
    d = round(b - a, 3)
    out = f'seg2/{nm}.mp4'
    if not os.path.exists(src):
        print('MANQUE', nm, src); return
    if nm == 'map':
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-t', str(d), '-an'] + ENC + [out], check=True)
        return
    if src.endswith('.mp4'):
        cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(ss), '-i', src, '-t', str(d), '-vf',
               "tpad=stop_mode=clone:stop_duration=2," + clip_vf(d, pr['sens']), '-an'] + ENC + [out]
        subprocess.run(cmd, check=True)
        return
    w, h = Image.open(src).size
    k = min(1760 / w, 960 / h)
    fw, fh = int(w * k) // 2 * 2, int(h * k) // 2 * 2
    n = int(d * 30) + 2
    zs, ze, fx, fy = pr['zs'], pr['ze'], pr['fx'], pr['fy']
    z = f"{zs}+({ze}-{zs})*on/{n}"
    fc = (f"[0:v]split[a][b];"
          f"[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=40:6,eq=brightness=-0.16:saturation=0.9[bg];"
          f"[b]scale={fw*2}:{fh*2}:flags=lanczos,zoompan=z='{z}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d=1:s={fw}x{fh}:fps=30[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p")
    cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-loop', '1', '-framerate', '30', '-t', str(d), '-i', src,
           '-filter_complex', fc, '-t', str(d), '-an'] + ENC + [out]
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    only = sys.argv[1:]
    todo = [p for p in plan if not only or p[0] in only]
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(run, todo))
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', '../fin/fin_japan.mp4', '-an', '-vf', 'fps=30,format=yuv420p'] + ENC + ['seg2/fin.mp4'], check=True)
    open('seg2/list.txt', 'w').write(''.join(f"file '{p[0]}.mp4'\n" for p in plan) + "file 'fin.mp4'\n")
    print('ok', FIN_START, FIN_START + FIN_LEN)
