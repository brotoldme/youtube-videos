import sys, re, json, subprocess, os
wav, ptxt, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
ph = [l.strip() for l in open(ptxt, encoding='utf-8') if l.strip()]
N = len(ph)
dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',wav]))
log = subprocess.run(['ffmpeg','-hide_banner','-i',wav,'-af','silencedetect=noise=-40dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',log)]
en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
sil=list(zip(st,en))
t0 = sil[0][1] if sil and sil[0][0]<0.05 else 0.0
t1 = sil[-1][0] if sil and sil[-1][1]>dur-0.05 else dur
import wave, numpy as np
_w=wave.open(wav); _sr=_w.getframerate(); _x=np.frombuffer(_w.readframes(_w.getnframes()),np.int16)/32768
def rms(a,b): s=_x[int(a*_sr):int(b*_sr)]; return float(np.sqrt((s**2).mean())) if len(s) else 0
ref=rms(t0,t1)
for a,b in sil:
    if t0 < a < t0+0.45 and rms(t0,a) < 0.3*ref: t0=b
for a,b in reversed(sil):
    if t1-0.45 < b < t1 and rms(b,t1) < 0.3*ref: t1=a
cand=[(a,b) for a,b in sil if a>t0+0.3 and b<t1-0.3]
w=[len(p)+6*len(re.findall(r'[,;:]',p)) for p in ph]
tot=sum(w); speech=t1-t0
exp=[t0+speech*sum(w[:i+1])/tot for i in range(N-1)]
INF=1e9
M=len(cand)
if M < N-1: sys.exit(f'ERREUR: {M} silences pour {N-1} frontieres')
def cost(k,j):
    a,b=cand[j]; mid=(a+b)/2
    return ((mid-exp[k])/1.0)**2 - 2.0*(b-a)
dp=[[INF]*M for _ in range(N-1)]; bk=[[-1]*M for _ in range(N-1)]
for j in range(M): dp[0][j]=cost(0,j)
for k in range(1,N-1):
    best=INF;bi=-1
    for j in range(M):
        if j>0 and dp[k-1][j-1]<best: best=dp[k-1][j-1];bi=j-1
        if bi>=0: dp[k][j]=best+cost(k,j); bk[k][j]=bi
j=min(range(M),key=lambda j:dp[N-2][j]); ch=[j]
for k in range(N-2,0,-1): j=bk[k][j]; ch.append(j)
ch=ch[::-1]
bounds=[t0]+[x for j in ch for x in cand[j]]+[t1]
segs=[(bounds[2*i],bounds[2*i+1]) for i in range(N)]
rapport=[]
for i,(a,b) in enumerate(segs):
    expd=speech*w[i]/tot
    f=os.path.join(out,f'p{i+1:02d}.wav')
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',wav,'-ss',f'{max(0,a-0.03):.3f}','-to',f'{b+0.05:.3f}',f],check=True)
    r=(b-a)/expd
    rapport.append({'n':i+1,'debut':round(a,3),'fin':round(b,3),'duree':round(b-a,3),'attendu':round(expd,2),'ratio':round(r,2),'alerte':not(0.6<r<1.5),'phrase':ph[i]})
json.dump(rapport,open(os.path.join(out,'decoupe.json'),'w'),indent=1,ensure_ascii=False)
for r in rapport: print(f"{r['n']:2d} {r['debut']:6.2f}-{r['fin']:6.2f} {r['duree']:5.2f}s att {r['attendu']:5.2f} x{r['ratio']} {'!!' if r['alerte'] else ''} {r['phrase'][:50]}")
print('silences non retenus (pauses internes):',[(round(a,2),round(b-a,2)) for k,(a,b) in enumerate(cand) if k not in ch])
