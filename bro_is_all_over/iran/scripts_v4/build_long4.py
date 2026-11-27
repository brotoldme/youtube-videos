import subprocess, json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
OUT='v4/seg'; os.makedirs(OUT, exist_ok=True)
S = {x['n']: x for x in json.load(open('v4/long_segs3.json'))}
P = lambda n: S[n]['start'] if n > 1 else 0.0
FIN_START = S[25]['end']; MAP_START = P(5)
M='wm/'; C='px/'
def ph(n,fx=.5,fy=.5,zs=1.0,ze=1.07): return ('P',M+n+'.jpg',dict(fx=fx,fy=fy,zs=zs,ze=ze))
def cl(i,ss=1.0,fy=.35): return ('C',C+f'{i}.mp4',dict(ss=ss,fy=fy))
LINES = {
 1:[ph('yakh_meybod'),cl(69326)],
 2:[cl(70872)],
 3:[ph('yakh_kashmar',.5,.6),cl(304330)],
 4:[cl(378232),cl(282513),cl(378609,1.0,.5)],
 6:[ph('n_a',.5,.5),cl(378551,1.0,.4)],
 7:[ph('shah',.5,.5),cl(378549,1.0,.4),ph('aliqapu',.5,.5)],
 8:[cl(378556,1.0,.5),ph('gate',.5,.5)],
 9:[cl(70875),ph('persep',.5,.5),cl(146047),ph('zigg',.5,.5)],
 10:[cl(345062),ph('haft',.5,.5)],
 11:[cl(257593),cl(249475)],
 12:[ph('tahdig',.5,.5),cl(267)],
 13:[cl(21822),cl(202876)],
 14:[cl(108018),cl(378560,1.0,.5)],
 15:[cl(378403,1.0,.5),ph('yazd_old',.5,.5)],
 16:[cl(378405,1.0,.5),ph('bad_haram',.5,.4),cl(131776)],
 17:[cl(89831),cl(76367)],
 18:[ph('qan_gon2',.5,.45),cl(197780)],
 19:[ph('qan_09',.5,.5),cl(216013)],
 20:[ph('qan_gon',.5,.5),cl(243560),ph('qan_clock',.5,.55)],
 21:[cl(203923),ph('ice_meybod3')],
 22:[cl(378268,1.0,.4),ph('damavand',.5,.5),cl(125695)],
 23:[ph('lut_a',.5,.5),cl(284566),ph('lut_b',.5,.5),cl(303749)],
 24:[cl(141424),cl(51077)],
 25:[cl(80193)],
}
plan=[]
def seg(n,items):
    a=P(n); b=P(n+1) if n<25 else FIN_START
    if n==4: b=MAP_START
    k=len(items)
    for i,it in enumerate(items):
        plan.append((f's{n:02d}{chr(97+i)}',it,round(a+(b-a)*i/k,3),round(a+(b-a)*(i+1)/k,3)))
for n in sorted(LINES):
    if n==6: plan.append(('map',('MAP',),MAP_START,P(6)))
    seg(n,LINES[n])
ENC=['-c:v','libx264','-crf','17','-preset','veryfast']
def probe(src):
    w,h=[int(x) for x in subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0:s=x',src],capture_output=True,text=True).stdout.strip().split('x')[:2]]
    return w,h
def render(p):
    nm,it,a,b=p; d=round(b-a,3); out=f'{OUT}/{nm}.mp4'
    if it[0]=='MAP':
        subprocess.run(['ffmpeg','-loglevel','error','-y','-i','intro_map.mp4','-vf','tpad=stop_mode=clone:stop_duration=2,fps=30','-t',str(d),'-an']+ENC+[out],check=True); return
    kind,src,pr=it
    if not os.path.exists(src): print('MANQUE',nm,src); return
    n=int(d*30)+2
    if kind=='C':
        w,h=probe(src); ss=pr.get('ss',1.0); fy=pr.get('fy',.35)
        if h>w:
            vf=(f"scale=1920:-2:flags=lanczos,crop=1920:1080:x=0:y='(ih-1080)*({fy}+0.25*t/{d})',fps=30,format=yuv420p")
        else:
            vf=("scale=2112:1188:force_original_aspect_ratio=increase,crop=1920:1080:x='(iw-1920)*(t/%s)':y='(ih-1080)/2',fps=30,format=yuv420p"%d)
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(ss),'-i',src,'-t',str(d),'-vf',"tpad=stop_mode=clone:stop_duration=2,"+vf,'-an']+ENC+[out],check=True); return
    if kind=='D':   # schema : graphique plein cadre sur fond uni (regle 85, les graphiques gardent leur mise en page)
        im=Image.open(src).convert('RGB'); k=1040/im.height; im=im.resize((int(im.width*k),1040),Image.LANCZOS)
        bg=Image.new('RGB',(1920,1080),(244,242,238)); bg.paste(im,((1920-im.width)//2,20)); bg.save('v4/diagram.png')
        subprocess.run(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','30','-t',str(d),'-i','v4/diagram.png','-vf','format=yuv420p','-an']+ENC+[out],check=True); return
    zs,ze,fx,fy=pr['zs'],pr['ze'],pr['fx'],pr['fy']; z=f"{zs}+({ze}-{zs})*on/{n}"
    fc=(f"[0:v]scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,crop=3840:2160:x='(iw-3840)*{fx}':y='(ih-2160)*{fy}',"
        f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1920x1080:fps=30,format=yuv420p")
    subprocess.run(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','30','-t',str(d),'-i',src,'-vf',fc,'-t',str(d),'-an']+ENC+[out],check=True)
def run(p):
    try: render(p)
    except Exception as e: print('ECHEC',p[0],str(e)[:80])
if __name__=='__main__':
    # controles
    srcs=[p[1][1] for p in plan if len(p[1])>1]
    dup=[s for s in set(srcs) if srcs.count(s)>1]
    print('doublons de fichier:',dup)
    long=[(p[0],round(p[3]-p[2],2)) for p in plan if p[3]-p[2]>5.05]
    print('plans > 5 s:',long)
    kinds=[p[1][0] for p in plan]; row=0; mx=0
    for k in kinds:
        row=row+1 if k in('P','D') else 0; mx=max(mx,row)
    print('max images fixes de suite:',mx,'| nb plans',len(plan))
    only=sys.argv[1:]
    todo=[p for p in plan if not only or p[0] in only]
    with ThreadPoolExecutor(4) as ex: list(ex.map(run,todo))
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i','fin_iran.mp4','-an','-vf','fps=30,format=yuv420p']+ENC+[f'{OUT}/fin.mp4'],check=True)
    open(f'{OUT}/list.txt','w').write(''.join(f"file '{p[0]}.mp4'\n" for p in plan)+"file 'fin.mp4'\n")
    json.dump([(p[0],p[2],p[3]) for p in plan],open('v4/plan_times.json','w'))
    print('ok',FIN_START)
