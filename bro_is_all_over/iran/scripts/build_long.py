import subprocess, json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
os.makedirs('b/seg', exist_ok=True)
S = {x['n']: x for x in json.load(open('long_segs.json'))}
P = lambda n: S[n]['start'] if n > 1 else 0.0
FIN_START = P(31)
MAP_START = 30.78
# (nom, source, t0, t1, params)
def L(n, items):
    a = P(n) if n != 6 else P(6)
    b = P(n + 1) if n < 31 else FIN_START
    if n == 6: b = MAP_START
    k = len(items); out = []
    for i, it in enumerate(items):
        t0 = a + (b - a) * i / k; t1 = a + (b - a) * (i + 1) / k
        out.append((f's{n:02d}{chr(97+i)}', it, round(t0, 3), round(t1, 3)))
    return out
Z = lambda zs, ze, fx, fy: dict(zs=zs, ze=ze, fx=fx, fy=fy)
M = 'wm/'; C = 'px/'
plan = []
plan += L(1, [(M+'yakh_meybod.jpg', Z(1.0,1.10,.5,.5))])
plan += L(2, [(C+'70872.mp4', 1)])
plan += L(3, [(M+'yakh_kashmar.jpg', Z(1.0,1.12,.3,.5))])
plan += L(4, [(M+'yakh_meybod2.jpg', Z(1.08,1.0,.6,.5))])
plan += L(5, [(C+'89833.mp4', -1)])
plan += L(6, [(M+'yakh_zarisf.jpg', Z(1.0,1.12,.5,.5)), (M+'bad_pav.jpg', Z(1.0,1.1,.5,.4)), (M+'qan_gon.jpg', Z(1.0,1.1,.4,.5))])
plan += [('map', 'MAP', MAP_START, P(8))]
plan += L(8, [(M+'yakh_diagram.jpg', Z(1.0,1.08,.5,.5))])
plan += L(9, [(M+'yakh_kheshti.jpg', Z(1.0,1.12,.5,.6))])
plan += L(10, [(M+'ice_meybod3.jpg', Z(1.0,1.1,.7,.5))])
plan += L(11, [(C+'378232.mp4', 1)])
plan += L(12, [(M+'yakh_inside.jpg', Z(1.0,1.15,.3,.5)), (M+'yakh_inside.jpg', Z(1.2,1.0,.8,.6))])
plan += L(13, [(C+'378610.mp4', 1)])
plan += L(14, [(M+'faloodeh.jpg', Z(1.0,1.1,.5,.5))])
plan += L(15, [(C+'70577.mp4', 1)])
plan += L(16, [(M+'bad_yazd.jpg', Z(1.0,1.1,.5,.4))])
plan += L(17, [(M+'bad_far.jpg', Z(1.0,1.12,.6,.5))])
plan += L(18, [(M+'bad_fahadan.jpg', Z(1.0,1.1,.4,.5)), (M+'bad_haram.jpg', Z(1.0,1.12,.5,.4))])
plan += L(19, [(M+'bad_ceiling.jpg', Z(1.0,1.1,.5,.7))])
plan += L(20, [(C+'378405.mp4', 1)])
plan += L(21, [(M+'qan_gon2.jpg', Z(1.0,1.1,.5,.6))])
plan += L(22, [(M+'qan_09c.jpg', Z(1.0,1.12,.5,.5))])
plan += L(23, [(M+'qan_clock.jpg', Z(1.0,1.12,.5,.5))])
plan += L(24, [(C+'378609.mp4', 1)])
plan += L(25, [(C+'378560.mp4', 1)])
plan += L(26, [(C+'89831.mp4', 1)])
plan += L(27, [(C+'69326.mp4', 1), (C+'70610.mp4', -1)])
plan += L(28, [(C+'377372.mp4', 1), (C+'377374.mp4', 1)])
plan += L(29, [(C+'378402.mp4', 1)])
plan += L(30, [(C+'131776.mp4', 1)])
ENC = ['-c:v','libx264','-crf','17','-preset','veryfast']
def vf_clip(d, sens, src):
    w,h = [int(x) for x in subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0:s=x',src],capture_output=True,text=True).stdout.strip().split('x')]
    if h > w:   # vertical : fond flou + premier plan
        return ("split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=40:6,eq=brightness=-0.16:saturation=0.9[bg];"
                "[b]scale=-2:1020[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30,format=yuv420p"), True
    f = f"t/{d}" if sens == 1 else f"1-t/{d}"
    return ("scale=2112:1188:force_original_aspect_ratio=increase,"
            f"crop=1920:1080:x='(iw-1920)*({f})':y='(ih-1080)/2',fps=30,format=yuv420p"), False
def run(p):
    try: return run0(p)
    except Exception as e: print('ECHEC',p[0],str(e)[:60])
def run0(p):
    nm, it, a, b = p
    d = round(b - a, 3); out = f'b/seg/{nm}.mp4'
    if nm == 'map':
        subprocess.run(['ffmpeg','-loglevel','error','-y','-i','intro_map.mp4','-t',str(d),'-an']+ENC+[out],check=True); return
    src, pr = it
    if not os.path.exists(src): print('MANQUE', nm, src); return
    if src.endswith('.mp4'):
        vf, cx = vf_clip(d, pr, src)
        if cx: cmd = ['ffmpeg','-loglevel','error','-y','-ss','1','-i',src,'-t',str(d),'-filter_complex',"tpad=stop_mode=clone:stop_duration=2,"+vf,'-an']+ENC+[out]
        else: cmd = ['ffmpeg','-loglevel','error','-y','-ss','1','-i',src,'-t',str(d),'-vf',"tpad=stop_mode=clone:stop_duration=2,"+vf,'-an']+ENC+[out]
        subprocess.run(cmd, check=True); return
    w,h = Image.open(src).size
    k = min(1760/w, 960/h); fw, fh = int(w*k)//2*2, int(h*k)//2*2
    n = int(d*30)+2; zs,ze,fx,fy = pr['zs'],pr['ze'],pr['fx'],pr['fy']
    z = f"{zs}+({ze}-{zs})*on/{n}"
    fc = (f"[0:v]split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=40:6,eq=brightness=-0.16:saturation=0.9[bg];"
          f"[b]scale={fw*2}:{fh*2}:flags=lanczos,zoompan=z='{z}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d=1:s={fw}x{fh}:fps=30[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p")
    subprocess.run(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','30','-t',str(d),'-i',src,'-filter_complex',fc,'-t',str(d),'-an']+ENC+[out],check=True)
if __name__ == '__main__':
    only = sys.argv[1:]
    todo = [p for p in plan if not only or p[0] in only]
    with ThreadPoolExecutor(4) as ex: list(ex.map(run, todo))
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i','fin_iran.mp4','-an','-vf','fps=30,format=yuv420p']+ENC+['b/seg/fin.mp4'],check=True)
    open('b/seg/list.txt','w').write(''.join(f"file '{p[0]}.mp4'\n" for p in plan)+"file 'fin.mp4'\n")
    json.dump([(p[0],p[2],p[3]) for p in plan],open('b/plan_times.json','w'))
    print('ok', FIN_START)
