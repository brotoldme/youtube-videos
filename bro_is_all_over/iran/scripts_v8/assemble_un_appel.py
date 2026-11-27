import sys, json, wave, numpy as np, subprocess, os
d, outwav = sys.argv[1:3]
rap=json.load(open(os.path.join(d,'decoupe.json')))
SR=44100; PAUSE=0.22; TARGET=0.105
parts=[]; sent=[]; t=0.0
for r in rap:
    f=os.path.join(d,f"p{r['n']:02d}.wav"); g=f+'.44k.wav'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f,'-ar',str(SR),'-ac','1',g],check=True)
    w=wave.open(g); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float64)/32768
    x=x*(TARGET/np.sqrt((x**2).mean())); x=np.clip(x,-0.99,0.99)
    sent.append({'start':round(t,3),'dur':round(len(x)/SR,3),'text':r['phrase']})
    parts.append(x); t+=len(x)/SR
    parts.append(np.zeros(int(PAUSE*SR))); t+=PAUSE
y=np.concatenate(parts[:-1])
o=wave.open(outwav,'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes((y*32767).astype(np.int16).tobytes()); o.close()
json.dump(sent,open(os.path.splitext(outwav)[0]+'_sent.json','w'),indent=1,ensure_ascii=False)
print('total',round(len(y)/SR,2),'s');[print(s) for s in sent]
