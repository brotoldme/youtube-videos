import sys,json,subprocess,os
sys.path.insert(0,'v7'); sys.argv=['x']
exec(open('v7/build_long7.py').read().split("if __name__=='__main__':")[0])
from cardlib import card,W as CW,Y as CY
COL={'W':CW,'Y':CY}
os.makedirs('v7/lab',exist_ok=True)
labs=[]
for nm,it,a,b in plan:
    lab=it[2].get('lab') if len(it)>2 and isinstance(it[2],dict) else None
    if not lab: continue
    t0=a+0.35; t1=b-0.2
    if t1-t0>5.2: t1=t0+5.2
    f=f'v7/lab/{nm}.png'; card([(t,COL[c]) for t,c in lab],f); labs.append((f,round(t0,2),round(t1,2)))
json.dump(labs,open('v7/labs.json','w'))
print(len(labs),'labels'); 
print('FIN_START',FIN_START,'P30',P(30),'dur',FIN_START+9.6)
