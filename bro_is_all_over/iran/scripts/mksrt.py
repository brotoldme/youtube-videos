import json,re,sys
NUM=[("Twenty-four hundred years","2,400 years"),("one hundred degrees","100 degrees"),("ninety million","90 million"),("about seven hundred","about 700"),("thirty-four meters","34 meters"),
("four hundred twenty-seven shafts","427 shafts"),("thirty-three kilometers","33 kilometers"),("twenty-five hundred years","2,500 years"),("six hundred dams","600 dams"),
("thirty-three thousand","33,000"),("fifty thousand","50,000"),("twenty twenty-five","2025"),("ten percent","10%"),("twenty-five centuries","25 centuries"),("four hundred B.C.","400 B.C."),
("sixteen hundred","1600"),("Five things","5 things"),("Twenty-four hundred","2,400")]
def dg(t):
    for a,b in NUM: t=t.replace(a,b)
    return t
def ts(x):
    h=int(x//3600);m=int(x%3600//60);s=x%60;return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s-int(s))*1000)):03d}"
def chunks(text,maxc=76):
    # coupe aux ponctuations, regroupe
    parts=re.findall(r'[^.?!,:;]+[.?!,:;]*\s*',text);out=[];cur=''
    for p in parts:
        p=p.strip()
        if cur and len(cur)+1+len(p)>maxc: out.append(cur);cur=p
        else: cur=(cur+' '+p).strip()
        if cur.endswith(('.','?','!')) and len(cur)>30: out.append(cur);cur=''
    if cur: out.append(cur)
    # rattache les très courts
    res=[]
    for c in out:
        if res and len(c)<14: res[-1]+=' '+c
        else: res.append(c)
    return res
def wrap(c):
    if len(c)<=42: return c
    words=c.split();best=None
    for i in range(1,len(words)):
        a=' '.join(words[:i]);b=' '.join(words[i:])
        sc=max(len(a),len(b))
        if best is None or sc<best[0]: best=(sc,a,b)
    return best[1]+'\n'+best[2] if best else c
def build(items,out):
    cues=[]
    for (s,e,text) in items:
        text=dg(text);cs=chunks(text);tot=sum(len(c) for c in cs);t=s
        for c in cs:
            d=(e-s)*len(c)/tot;cues.append([t,t+d,wrap(c)]);t+=d
    # contraintes : pas de chevauchement
    for i in range(len(cues)-1):
        if cues[i][1]>cues[i+1][0]-0.02: cues[i][1]=cues[i+1][0]-0.02
    with open(out,'w') as f:
        for i,(a,b,t) in enumerate(cues,1): f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
    print(out,len(cues),'cues; max dur',round(max(b-a for a,b,_ in cues),1),'max line',max(len(l) for _,_,t in cues for l in t.split('\n')),'min dur',round(min(b-a for a,b,_ in cues),1))
disp=[l.strip() for l in open('long_disp.txt') if l.strip()]
S={x['n']:x for x in json.load(open('long_segs.json'))}
build([(S[n]['start'],S[n]['end'],disp[n-1]) for n in range(1,32)],'iran_long.srt')
tl=json.load(open('sh_short_long/times.json'))['times'];order=[1,2,9,11,12,14,4]
build([(tl[i][0],tl[i][1],disp[n-1]) for i,n in enumerate(order)],'iran_short_long.srt')
for nm,sc in [('dont','script_dont.txt'),('must','script_mustdo.txt')]:
    lines=[l.strip() for l in open(sc) if l.strip()][:6] if nm=='dont' else [l.strip() for l in open(sc) if l.strip()][:6]
    tl=json.load(open(f'sh_short_{nm}/times.json'))['times']
    build([(tl[i][0],tl[i][1],lines[i]) for i in range(6)],f'iran_short_{nm}.srt')
