import subprocess, json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
OUT='v6/seg'
S={x['n']:x for x in json.load(open('v6/segs.json'))}
P=lambda n: S[n]['start'] if n>1 else 0.0
FIN_START=201.9; MAP_START=P(5)
def ph(n,fx=.5,fy=.5,zs=1.0,ze=1.07,w=1,d='wm/'): return ('P',d+n+'.jpg',dict(fx=fx,fy=fy,zs=zs,ze=ze,w=w))
def p6(n,*a,**k): return ph(n,*a,d='wm6/',**k)
def cl(i,ss=0.5,fy=.35,w=1): return ('C',f'px/{i}.mp4',dict(ss=ss,fy=fy,w=w))
LINES={
 1:[p6('map1850',.75,.6)],
 2:[cl(377372,1.0,.4),cl(51077,1.0,.5)],
 3:[cl(202876,1.0),cl(378570,1.0,.4)],
 4:[ph('gate',.5,.4),cl(185092),p6('haft2',.5,.6)] if False else [ph('gate',.5,.4),cl(185092),ph('haft',.5,.5)],
 6:[p6('cyrus',.5,.5),cl(378609,1.0,.5)],
 7:[cl(69326,2.0),p6('map1724',.5,.5)],
 8:[cl(80193,2.0),cl(78894,2.0)],
 9:[ph('persep',.5,.4),cl(70872,2.0),ph('apadana',.5,.3)],
 10:[cl(378549,1.0,.4),cl(378404,1.0,.5)],
 11:[cl(378405,1.0,.5),p6('necro',.5,.5),cl(378556,1.0,.4)],
 12:[cl(146047,1.0)],
 13:[cl(282513,1.0),cl(378232,1.0,.4)],
 14:[p6('shah_dara',.5,.3),cl(41146,1.0)],
 15:[p6('shah_well',.5,.35),cl(107240,1.0),p6('ferd2',.5,.4)],
 16:[cl(378551,1.0,.4),p6('ferd4',.5,.5)],
 17:[cl(303749,1.0),cl(154001,1.0)],
 18:[cl(21822,1.0),cl(203923,1.0)],
 19:[cl(378403,1.0,.5),ph('persep2',.5,.5)],
 20:[cl(9373,1.0),p6('chahar',.5,.35),cl(257593,1.0)],
 21:[p6('haft2',.5,.6),cl(119252,1.0),cl(143682,1.0),cl(142984,1.0)],
 22:[cl(22761,2.0),cl(92651,1.0),cl(11606,1.0)],
 23:[cl(56959,1.0),p6('sizdah',.5,.5)],
 24:[cl(378565,1.0,.4),cl(345062,1.0)],
 25:[cl(70610,2.0),cl(42846,1.0),p6('carpet',.5,.35)],
 26:[cl(378560,1.0,.4),ph('naqsh',.5,.5)],
 27:[cl(125695,1.0),ph('damavand',.5,.4)],
 28:[cl(89831,1.0),ph('lut_a',.5,.5)],
}
W={ (21,):[.28,.24,.24,.24] }
plan=[]
def seg(n,items):
    a=P(n); b=P(n+1) if n<28 else FIN_START
    if n==4: b=MAP_START
    ws=[it[2].get('w',1) for it in items]; tot=sum(ws); acc=0
    for i,it in enumerate(items):
        plan.append((f's{n:02d}{chr(97+i)}',it,round(a+(b-a)*acc/tot,3),round(a+(b-a)*(acc+ws[i])/tot,3))); acc+=ws[i]
for n in sorted(LINES):
    if n==6: plan.append(('map',('MAP',),MAP_START,P(6)))
    seg(n,LINES[n])
ENC=['-c:v','libx264','-crf','17','-preset','veryfast']
def probe(src):
    return [int(x) for x in subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0:s=x',src],capture_output=True,text=True).stdout.strip().split('x')[:2]]
def render(p):
    nm,it,a,b=p; d=round(b-a,3); out=f'{OUT}/{nm}.mp4'
    if it[0]=='MAP':
        subprocess.run(['ffmpeg','-loglevel','error','-y','-i','intro_map.mp4','-vf','tpad=stop_mode=clone:stop_duration=6,fps=30','-t',str(d),'-an']+ENC+[out],check=True); return
    kind,src,pr=it
    if not os.path.exists(src): print('MANQUE',nm,src); return
    n=int(d*30)+2
    if kind=='C':
        w,h=probe(src); ss=pr.get('ss',.5); fy=pr.get('fy',.35)
        if h>w: vf=f"scale=1920:-2:flags=lanczos,crop=1920:1080:x=0:y='(ih-1080)*({fy}+0.25*t/{d})',fps=30,format=yuv420p"
        else: vf="scale=2112:1188:force_original_aspect_ratio=increase,crop=1920:1080:x='(iw-1920)*(t/%s)':y='(ih-1080)/2',fps=30,format=yuv420p"%d
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(ss),'-i',src,'-t',str(d),'-vf',"tpad=stop_mode=clone:stop_duration=2,"+vf,'-an']+ENC+[out],check=True); return
    zs,ze,fx,fy=pr['zs'],pr['ze'],pr['fx'],pr['fy']; z=f"{zs}+({ze}-{zs})*on/{n}"
    fc=(f"[0:v]scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,crop=3840:2160:x='(iw-3840)*{fx}':y='(ih-2160)*{fy}',"
        f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1920x1080:fps=30,format=yuv420p")
    subprocess.run(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','30','-t',str(d),'-i',src,'-vf',fc,'-t',str(d),'-an']+ENC+[out],check=True)
def run(p):
    try: render(p)
    except Exception as e: print('ECHEC',p[0],str(e)[:80])
if __name__=='__main__':
    srcs=[p[1][1] for p in plan if len(p[1])>1]
    print('doublons de fichier:',[s for s in set(srcs) if srcs.count(s)>1])
    print('clips >5.05 s:',[(p[0],round(p[3]-p[2],2)) for p in plan if p[1][0]=='C' and p[3]-p[2]>5.05])
    row=mx=0
    for p in plan:
        row=row+1 if p[1][0]=='P' else 0; mx=max(mx,row)
    print('max photos de suite:',mx,'| plans',len(plan))
    if '--check' in sys.argv: sys.exit()
    only=[a for a in sys.argv[1:] if not a.startswith('--')]
    with ThreadPoolExecutor(4) as ex: list(ex.map(run,[p for p in plan if not only or p[0] in only]))
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i','fin_iran.mp4','-an','-vf','fps=30,format=yuv420p']+ENC+[f'{OUT}/fin.mp4'],check=True)
    open(f'{OUT}/list.txt','w').write(''.join(f"file '{p[0]}.mp4'\n" for p in plan)+"file 'fin.mp4'\n")
    json.dump([(p[0],p[2],p[3]) for p in plan],open('v6/plan_times.json','w')); print('ok',FIN_START)
