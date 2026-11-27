from pocketsphinx import Decoder, Config
import json
cfg=Config(); cfg.set_string('-loglevel','FATAL')
d=Decoder(cfg)
d.start_utt(); d.process_raw(open('raw16.pcm','rb').read(),False,True); d.end_utt()
out=[(s.word,round(s.start_frame/100,2),round(s.end_frame/100,2)) for s in d.seg() if not s.word.startswith('<') and s.word not in('[SPEECH]','[NOISE]')]
json.dump(out,open('stt.json','w'))
print(len(out)); print(' '.join(f"{w}@{a}" for w,a,b in out if 56<a<160))
