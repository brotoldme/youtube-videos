import json, subprocess, os, sys
from concurrent.futures import ThreadPoolExecutor
V6 = '/home/claude/youtube-videos/bro_is_all_over/iran/long_v6.mp4'
WM = '/home/claude/w/wmc/'
OUT = '/home/claude/w/seg8/'
S6 = {x['n']: x['start'] for x in json.load(open('/home/claude/youtube-videos/bro_is_all_over/iran/scripts_v6/segs.json'))}
SENT = json.load(open('/home/claude/w/v8/voix_sent.json'))
ST = {i + 1: x['start'] for i, x in enumerate(SENT)}
FIN6 = (201.9, 9.6)
F0 = ST[35] - 2.02
WIN = {i: (ST[i], ST[i + 1]) for i in range(1, 34)}
WIN[34] = (ST[34], F0)
MAP = {i: i for i in range(1, 18)}
MAP.update({27: 18, 28: 19, 29: 20, 30: 21, 31: 22, 32: 23, 33: 24, 34: 25})
S6[26] = 179.97
ENC = ['-c:v', 'libx264', '-crf', '17', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30']
PH = {  # phrase -> liste de (fichier, fx, fy, zs, ze)
    18: [('10000_Rials_banknote_of_the_Islamic_Repu.jpg', .5, .5, 1.0, 1.10), ('Iran_5000_Rials_overprint_banknote_rev_j.jpg', .5, .5, 1.10, 1.0)],
    19: [('Tehran_Metro_Train_Arrived_At_Tajrish_St.jpg', .5, .5, 1.0, 1.08), ('Fast_Foods__Vozara_Ave__Tehran___panoram.jpg', .5, .4, 1.06, 1.0), ('Tehran_Hybrid_Taxi_01_jpg.jpg', .5, .5, 1.0, 1.08)],
    20: [('Sayda_Vegan_karaj_Food_jpg.jpg', .5, .5, 1.0, 1.08), ('Iran___Téhéran___intérieur_salon_de_thé_.jpg', .5, .5, 1.08, 1.0)],
    21: [('Grand_Bazaar__Tehran_12_jpg.jpg', .5, .5, 1.0, 1.06)],
    22: [('Old_Building_of_Iranian_Parliament_jpg.jpg', .5, .5, 1.0, 1.08)],
    23: [('Grand_Bazaar__Tehran_07_jpg.jpg', .5, .5, 1.0, 1.08)],
    24: [('Iranian_women_walking_and_talking_jpg.jpg', .5, .35, 1.0, 1.10)],
    25: [('CARD', 0, 0, 0, 0)],
    26: [('Paykan_Taxi_Tajrish_Tehran_jpg.jpg', .5, .5, 1.0, 1.08), ('Taxi_in_Tehran_jpg.jpg', .5, .5, 1.08, 1.0)],
}


WT = {18: [4.8, 3.1], 19: [3.18, 2.15, 3.28], 20: [3.2, 2.9]}


def run(cmd):
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)


def seg_v6(i):
    m = MAP[i]; a, b = WIN[i]; d8 = b - a
    a6 = S6[m]; d6 = S6[m + 1] - S6[m]
    f = max(0.85, min(1.2, d8 / d6))
    vf = f"setpts=PTS*{f:.4f},tpad=stop_mode=clone:stop_duration=3,fps=30"
    if i == 32:  # cache le bouton SUBSCRIBE cuit dans la v6 (bas à droite)
        vf = "crop=1400:788:0:0,scale=1920:1080:flags=lanczos," + vf
    out = f'{OUT}s{i:02d}.mp4'
    run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', f'{a6:.3f}', '-i', V6, '-t', f'{d6 + 0.2:.3f}', '-an', '-vf', vf, '-t', f'{d8:.3f}'] + ENC + [out])
    return out


def kb(src, d, fx, fy, zs, ze, out):
    n = int(d * 30) + 2
    z = f"{zs}+({ze}-{zs})*on/{n}"
    fc = (f"[0:v]scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,crop=3840:2160:x='(iw-3840)*{fx}':y='(ih-2160)*{fy}',"
          f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1920x1080:fps=30,format=yuv420p")
    run(['ffmpeg', '-loglevel', 'error', '-y', '-loop', '1', '-framerate', '30', '-t', f'{d:.3f}', '-i', src, '-vf', fc, '-t', f'{d:.3f}', '-an'] + ENC + [out])


def seg_new(i):
    a, b = WIN[i]; d8 = b - a; items = PH[i]; out = f'{OUT}s{i:02d}.mp4'
    if items[0][0] == 'CARD':
        run(['ffmpeg', '-loglevel', 'error', '-y', '-loop', '1', '-framerate', '30', '-t', f'{d8:.3f}', '-i', '/home/claude/w/v8/card_alcohol.png', '-vf', 'format=yuv420p', '-an'] + ENC + [out])
        return out
    n = len(items); parts = []
    w = WT.get(i, [1] * n); tw = sum(w)
    for k, (fn, fx, fy, zs, ze) in enumerate(items):
        p = f'{OUT}s{i:02d}_{k}.mp4'; kb(WM + fn, d8 * w[k] / tw, fx, fy, zs, ze, p); parts.append(p)
    if n == 1:
        os.replace(parts[0], out); return out
    open(f'{OUT}s{i:02d}.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
    run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}s{i:02d}.txt', '-c', 'copy', out])
    return out


def seg(i):
    try:
        return seg_v6(i) if i in MAP else seg_new(i)
    except Exception as e:
        print('ECHEC', i, e); raise


if __name__ == '__main__':
    only = [int(a) for a in sys.argv[1:]]
    ids = [i for i in range(1, 35) if not only or i in only]
    with ThreadPoolExecutor(4) as ex: list(ex.map(seg, ids))
    run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', f'{FIN6[0]}', '-i', V6, '-t', f'{FIN6[1]}', '-an', '-vf', 'fps=30'] + ENC + [OUT + 'fin.mp4'])
    open(OUT + 'list.txt', 'w').write(''.join(f"file 's{i:02d}.mp4'\n" for i in range(1, 35)) + "file 'fin.mp4'\n")
    print('F0', round(F0, 3), 'total', round(F0 + FIN6[1], 3))
