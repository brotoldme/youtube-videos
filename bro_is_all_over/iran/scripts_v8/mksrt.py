import json,re,textwrap
d=json.load(open('voix_sent.json'))
R=[("nineteen thirty-five","1935"),("nineteen fifty-nine","1959"),("twenty-first","21"),("five fifty B C","550 BC"),("four eighty B C","480 BC"),
("forty-four percent","44%"),("twenty-three","23"),("third century A D","3rd century AD"),("seventeen hundred","1,700"),("seventeen centuries","17 centuries"),
("six fifty-one","651"),("thirty years","30 years"),("fifty thousand","50,000"),("Nearly ninety million","Nearly 90 million"),("Ten dollars","$10"),("ten dollars","$10"),
("twenty-seven million","27 million"),("ten cents","10 cents"),("three fifty","$3.50"),("one to four dollars","$1 to $4"),("seventeen dollars","$17"),
("three thousand","3,000"),("two thousand nine","2009"),("thirteenth","13th"),("thirteen days","13 days"),("Three centuries","Three centuries")]
def conv(t):
    for a,b in R: t=t.replace(a,b)
    return t.replace("March 21","March 21").replace("about $17","about $17")
def ts(x):
    h=int(x//3600);m=int(x%3600//60);s=x%60
    return f"{h:02}:{m:02}:{int(s):02},{int(round((s-int(s))*1000)):03}"
END=217.574
cues=[]
for i,s in enumerate(d):
    t=conv(s['text']); a=s['start']; b=a+s['dur']
    parts=re.split(r'(?<=[.?!:]) ',t)
    # merge into chunks <=80 chars
    ch=[];cur=''
    for p in parts:
        if cur and len(cur)+1+len(p)>80: ch.append(cur);cur=p
        else: cur=(cur+' '+p).strip()
    if cur: ch.append(cur)
    # split chunks too long by comma
    out=[]
    def sp(c):
        if len(textwrap.wrap(c,42))<=2: return [c]
        w=c.split(' ');h=len(w)//2
        return sp(' '.join(w[:h]))+sp(' '.join(w[h:]))
    for c in ch: out+=sp(c)
    while any(s['dur']*len(c)/sum(len(x) for x in out)>5.9 for c in out):
        k=max(range(len(out)),key=lambda j:len(out[j]));w=out[k].split(' ');h=len(w)//2
        out[k:k+1]=[' '.join(w[:h]),' '.join(w[h:])]
    tot=sum(len(c) for c in out);pos=a
    for c in out:
        du=s['dur']*len(c)/tot
        cues.append([pos,pos+du-0.02,c]);pos+=du
# enforce 1-6 s: merge tiny (<1s) into previous if possible
res=[]
for c in cues:
    if res and c[1]-c[0]<1.0 and len(res[-1][2])+len(c[2])<=80 and c[0]-res[-1][1]<0.4:
        res[-1][1]=c[1];res[-1][2]+=' '+c[2]
    else: res.append(c)
with open('long_v8.srt','w') as f:
    for n,(a,b,t) in enumerate(res,1):
        b=min(b,END-0.05)
        L=textwrap.wrap(t,42)
        assert len(L)<=2,(t,L)
        f.write(f"{n}\n{ts(a)} --> {ts(b)}\n"+"\n".join(L)+"\n\n")
print(len(res), max(c[1]-c[0] for c in res), min(c[1]-c[0] for c in res))
