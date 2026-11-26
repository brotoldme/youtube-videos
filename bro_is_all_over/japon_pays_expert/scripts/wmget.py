import hashlib,subprocess,sys,time,urllib.parse,os
items=[l.rstrip('\n').split('|') for l in open('wm_list.txt') if l.strip()]
for out,fn in items:
    o='wm2/'+out
    if os.path.exists(o) and os.path.getsize(o)>5000: continue
    n=fn.replace(' ','_'); h=hashlib.md5(n.encode()).hexdigest(); q=urllib.parse.quote(n)
    for w in (1280,960):
        url=f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{w}px-{q}"
        r=subprocess.run(['curl','-s','-A','BroIsAllOver/1.0','-o',o,'-w','%{http_code}',url],capture_output=True,text=True).stdout
        if r=='200' and os.path.getsize(o)>5000: break
        # petit original : pas de miniature plus grande que l'original -> original
        url2=f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}"
        r=subprocess.run(['curl','-s','-A','BroIsAllOver/1.0','-o',o,'-w','%{http_code}',url2],capture_output=True,text=True).stdout
        if r=='200' and os.path.getsize(o)>5000 and os.path.getsize(o)<3_000_000: break
        time.sleep(20)
    print(out,r,os.path.getsize(o) if os.path.exists(o) else 0); time.sleep(15)
