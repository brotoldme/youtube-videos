import subprocess, json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
OUT='v7/seg'
S={x['n']:x for x in json.load(open('v7/segs.json'))}
P=lambda n: S[n]['start'] if n>1 else 0.0
FIN_START=P(30)-0.28; MAP_START=P(5)
def ph(n,fx=.5,fy=.5,zs=1.0,ze=1.07,w=1,d='wm/'): return ('P',d+n+'.jpg',dict(fx=fx,fy=fy,zs=zs,ze=ze,w=w))
def p6(n,*a,**k): return ph(n,*a,d='wm6/',**k)
def p7(n,*a,**k): return ph(n,*a,d='wm7/',**k)
def L(item,*lab):
    item[2]['lab']=list(lab); return item
def cl(i,ss=0.5,fy=.35,w=1): return ('C',f'px/{i}.mp4',dict(ss=ss,fy=fy,w=w))
W='W'
Y='Y'
LINES={
 1:[p6('map1850',.75,.6)],
 2:[cl(51077,1.0,.5),cl(377372,1.0,.4)],
 3:[cl(378565,1.0,.4),cl(203923,1.0)],
 4:[cl(78894,2.0),cl(69326,2.0)],
 6:[L(cl(1052,1.0),('SALAAM',W),('= HELLO',Y)),cl(377374,1.0,.4)],
 7:[L(cl(70875,1.0),('1 TOMAN',W),('= 10 RIALS',Y)),cl(378549,1.0,.4)],
 8:[cl(377348,1.0,.4,w=1),L(cl(21822,1.0,w=1.3),('NEARLY 90%',W),("OF THE WORLD'S SAFFRON",Y))],
 9:[L(p7('tehran',.5,.5,w=.9),('TEHRAN',W)),L(cl(378601,1.0,.35,w=1.1),('TOCHAL GONDOLA',W),('UP TO 3,740 M',Y)),cl(378268,1.0,.4,w=.9)],
 10:[L(ph('damavand',.5,.4,w=1.05),('MOUNT DAMAVAND',W),("ASIA'S HIGHEST VOLCANO",Y)),cl(304330,1.0)],
 11:[L(ph('lut_a',.5,.5),('LUT DESERT',W),('SAND OVER 70 \u00b0C',Y)),cl(378226,1.0,.5),ph('lut_b',.5,.5)],
 12:[cl(150941,1.0),L(ph('yakh_kashmar',.5,.5),('YAKHCHAL',W),('DESERT ICE HOUSE',Y)),cl(108018,1.0),ph('yakh_zarisf',.5,.5)],
 13:[cl(378402,1.0,.5),L(ph('n_a',.5,.5),('ISFAHAN',W),('"HALF THE WORLD"',Y))],
 14:[cl(173638,1.0),L(ph('naqsh',.5,.5),('NAQSH-E JAHAN',W),('512 \u00d7 163 M',Y))],
 15:[L(cl(131776,6.0),('SHIRAZ',W)),L(ph('nasir',.5,.5),('NASIR AL-MULK',W),('THE PINK MOSQUE',Y)),cl(146047,1.0)],
 16:[L(ph('persep',.5,.5,w=1.05),('PERSEPOLIS',W),('FOUNDED 518 B.C.',Y)),cl(378609,1.0,.5,w=.95),ph('gate',.5,.4,w=1.1)],
 17:[cl(70577,1.0),L(ph('bad_yazd',.5,.5),('YAZD',W),('CITY OF MUD BRICK',Y))],
 18:[cl(9591,1.0),L(p7('kebab',.5,.5),('CHELOW KABAB',W),('IRAN\'S NATIONAL DISH',Y))],
 19:[cl(11626,1.0,w=1.0),L(ph('tahdig',.5,.5,w=1.0),('TAHDIG',W),("'BOTTOM OF THE POT'",Y))],
 20:[cl(243560,1.0),L(ph('faloodeh',.5,.5),('FALOODEH',W),('FROZEN NOODLE DESSERT',Y))],
 21:[cl(49970,1.0),L(p6('carpet',.5,.35),('PERSIAN CARPETS',W),('UNESCO LISTED 2010',Y)),cl(232357,1.0)],
 22:[L(p7('hafez',.5,.5,w=1.2),('TOMB OF HAFEZ',W),('SHIRAZ',Y)),cl(185092,1.0),p6('shah_well',.5,.35)],
 23:[L(cl(22761,1.0),('NOWRUZ',W),("'NEW DAY' \u00b7 3,000+ YEARS",Y)),cl(119252,1.0),p6('haft2',.5,.6)],
 24:[cl(9373,1.0),L(p6('chahar',.5,.35),('BONFIRE JUMPING',W)),cl(257593,1.0)],
 25:[L(ph('haft',.5,.5),('HAFT-SEEN',W),('7 THINGS STARTING WITH S',Y)),cl(147196,1.0),cl(143682,1.0),cl(11606,1.0),cl(142984,1.0)],
 26:[cl(56959,1.0),L(p6('sizdah',.5,.5),('13 DAYS',W),('THEN A PICNIC',Y))],
 27:[cl(378570,1.0,.4),cl(154001,1.0)],
 28:[p6('map1724',.5,.5),cl(378556,1.0,.4),p6('necro',.5,.5)],
 29:[cl(378560,1.0,.4),p6('shah_dara',.5,.3),cl(378551,1.0,.4)],
}
plan=[]
def seg(n,items):
    a=P(n); b=P(n+1) if n<29 else FIN_START
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
    json.dump([(p[0],p[2],p[3]) for p in plan],open('v7/plan_times.json','w')); print('ok',FIN_START)
