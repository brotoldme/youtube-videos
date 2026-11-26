import sys,re,json,difflib
from pocketsphinx import Decoder,get_model_path
raw,ptxt,outj=sys.argv[1:4]
md=get_model_path()
d=Decoder(hmm=md+'/en-us/en-us',lm=md+'/en-us/en-us.lm.bin',dict=md+'/en-us/cmudict-en-us.dict',loglevel='FATAL')
d.start_utt();d.process_raw(open(raw,'rb').read(),False,True);d.end_utt()
hyp=[(s.word,s.start_frame/100,s.end_frame/100) for s in d.seg() if not s.word.startswith('<') and not s.word.startswith('[') and s.word!='(NULL)']
hyp=[(re.sub(r'\(\d+\)','',w),a,b) for w,a,b in hyp]
ph=[l.strip() for l in open(ptxt) if l.strip()]
ref=[];sid=[]
for i,p in enumerate(ph):
    for w in re.findall(r"[a-z']+",p.lower().replace('-',' ')): ref.append(w);sid.append(i)
sm=difflib.SequenceMatcher(None,ref,[w for w,_,_ in hyp],autojunk=False)
tm={}
for a,b,n in sm.get_matching_blocks():
    for k in range(n): tm[a+k]=hyp[b+k]
res=[]
for i in range(len(ph)):
    idx=[k for k in range(len(ref)) if sid[k]==i and k in tm]
    res.append((i+1,round(tm[idx[0]][1],2) if idx else None,round(tm[idx[-1]][2],2) if idx else None,len(idx),sum(1 for s in sid if s==i)))
for r in res: print(r)
json.dump(res,open(outj,'w'))
