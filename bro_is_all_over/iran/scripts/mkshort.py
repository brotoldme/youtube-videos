import json,sys,subprocess,os,math,shutil
from PIL import Image,ImageDraw,ImageFont
ANTON='/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf'
W,H=1080,1920
ENC=['-c:v','libx264','-crf','17','-preset','veryfast']
RED=(255,46,59)
def sh(c): subprocess.run(c,check=True)
def text_png(path,parts,size,y,maxw=1000,stroke=10):
    """parts: liste de lignes ; chaque ligne = liste de (texte,couleur)"""
    im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im);f=ImageFont.truetype(ANTON,size)
    lines=[]
    for ln in parts:
        full=''.join(t for t,_ in ln);w=d.textlength(full,font=f)
        s=size
        while w>maxw: s-=4;f2=ImageFont.truetype(ANTON,s);w=d.textlength(full,font=f2)
        lines.append((ln,ImageFont.truetype(ANTON,s),w))
    yy=y
    for ln,f2,w in lines:
        x=(W-w)/2
        for t,c in ln:
            d.text((x,yy),t,font=f2,fill=tuple(c),stroke_width=stroke,stroke_fill=(0,0,0,255))
            x+=d.textlength(t,font=f2)
        yy+=int(f2.size*1.12)
    im.save(path)
def visual(src,pr,d,out,fx=.5):
    if src.endswith('.mp4'):
        w,h=[int(x) for x in subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0:s=x',src],capture_output=True,text=True).stdout.strip().split('x')]
        if h>w: vf=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,format=yuv420p"
        else:
            f=f"t/{d}" if pr.get('sens',1)==1 else f"1-t/{d}"
            vf=f"scale=-2:{H}:force_original_aspect_ratio=increase,crop={W}:{H}:x='(iw-{W})*({f})':y=0,fps=30,format=yuv420p"
        sh(['ffmpeg','-loglevel','error','-y','-ss',str(pr.get('ss',1)),'-i',src,'-t',str(d),'-vf',"tpad=stop_mode=clone:stop_duration=2,"+vf,'-an']+ENC+[out]);return
    w,h=Image.open(src).size
    k=min(1000/w,1400/h);fw,fh=int(w*k)//2*2,int(h*k)//2*2
    n=int(d*30)+2;zs,ze,fxx,fy=pr.get('zs',1.0),pr.get('ze',1.1),pr.get('fx',.5),pr.get('fy',.5)
    z=f"{zs}+({ze}-{zs})*on/{n}"
    fc=(f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:6,eq=brightness=-0.16:saturation=0.9[bg];"
        f"[b]scale={fw*3}:{fh*3}:flags=lanczos,zoompan=z='{z}':x='(iw-iw/zoom)*{fxx}':y='(ih-ih/zoom)*{fy}':d=1:s={fw}x{fh}:fps=30[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p")
    sh(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','30','-t',str(d),'-i',src,'-filter_complex',fc,'-t',str(d),'-an']+ENC+[out])
def build(spec):
    nm=spec['name'];wd=f'sh_{nm}';shutil.rmtree(wd,ignore_errors=True);os.makedirs(wd)
    V0=0.2;gap=spec.get('gap',0.28);pad=0.05
    # audio : coupes
    parts=[];t=V0;times=[]
    sil=lambda d,p:sh(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i',f'anullsrc=r=24000:cl=mono','-t',str(d),p])
    sil(V0,f'{wd}/a_sil0.wav');parts.append(f'{wd}/a_sil0.wav')
    sil(gap,f'{wd}/a_gap.wav')
    for i,(s,e,txt) in enumerate(spec['cuts']):
        a=max(0,s-pad);b=e+pad
        p=f'{wd}/a{i}.wav';sh(['ffmpeg','-loglevel','error','-y','-ss',str(a),'-to',str(b),'-i',spec['voice'],'-ar','24000','-ac','1',p])
        parts.append(p);times.append((t+pad,t+pad+(e-s),txt));t+=b-a
        if i<len(spec['cuts'])-1:parts.append(f'{wd}/a_gap.wav');t+=gap
    voice_end=t
    open(f'{wd}/l.txt','w').write(''.join(f"file '{os.path.abspath(x)}'\n" for x in parts))
    sh(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',f'{wd}/l.txt','-c','copy',f'{wd}/voice_raw.wav'])
    END=2.4;total=voice_end+0.35+END;body=voice_end+0.35
    # visuels : un par coupe (ou plus) - bornes = débuts de coupes
    vis=spec['visuals'];starts=[0.0]+[tt[0]-pad-gap/2 if False else None for tt in times[1:]]
    bounds=[0.0]+[times[i][0]-gap/2-pad for i in range(1,len(times))]+[body]
    segs=[]
    for i,v in enumerate(vis):
        a=bounds[v['cut']];b=bounds[v['cut']+1] if 'upto' not in v else bounds[v['upto']+1]
        segs.append((i,v,a,b))
    for i,v,a,b in segs:
        visual(v['src'],v.get('p',{}),round(b-a,3),f'{wd}/v{i}.mp4')
    # fin
    card=Image.new('RGB',(W,H),(14,22,46));d=ImageDraw.Draw(card)
    fl=subprocess.run(['rsvg-convert','-w','320','ir_flag.svg','-o',f'{wd}/flag.png']);fi=Image.open(f'{wd}/flag.png').convert('RGBA');card.paste(fi,((W-fi.width)//2,520),fi)
    f1=ImageFont.truetype(ANTON,92);f2=ImageFont.truetype(ANTON,60);f3=ImageFont.truetype(ANTON,54)
    def ctr(txt,f,y,c):
        w=d.textlength(txt,font=f);d.text(((W-w)/2,y),txt,font=f,fill=c)
    ctr('CANADA ADVISES',f1,900,(255,255,255));ctr('AGAINST ALL TRAVEL',f1,1010,(255,255,255));ctr('TO IRAN',f1,1120,RED)
    ctr('travel.gc.ca',f2,1290,(200,210,235));ctr('BRO IS ALL OVER',f3,1560,(255,210,63))
    card.save(f'{wd}/card.png')
    sh(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','30','-t',str(END),'-i',f'{wd}/card.png','-vf','format=yuv420p']+ENC+[f'{wd}/vend.mp4'])
    open(f'{wd}/vl.txt','w').write(''.join(f"file 'v{i}.mp4'\n" for i,_,_,_ in segs)+"file 'vend.mp4'\n")
    sh(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',f'{wd}/vl.txt','-c','copy',f'{wd}/body.mp4'])
    # textes
    inputs=['-i',f'{wd}/body.mp4'];flt='';last='[0:v]';k=1
    hk=spec['hook'];text_png(f'{wd}/hook.png',hk,spec.get('hook_size',150),spec.get('hook_y',1180))
    ov=[(f'{wd}/hook.png',0.0,2.0)]
    for i,o in enumerate(spec.get('labels',[])):
        text_png(f'{wd}/lab{i}.png',o['parts'],o.get('size',120),o.get('y',1330));
        c=o['cut'];ov.append((f'{wd}/lab{i}.png',max(2.0,times[c][0]-0.1) if c==0 else times[c][0]-0.1,bounds[c+1]-0.2 if c+1<len(times) else body-0.1))
    for p,a,b in ov:
        inputs+=['-loop','1','-i',p]
        flt+=f"{last}[{k}:v]overlay=enable='between(t,{a:.2f},{b:.2f})'[o{k}];";last=f'[o{k}]';k+=1
    flt+=f"{last}format=yuv420p[vout]"
    sh(['ffmpeg','-loglevel','error','-y']+inputs+['-filter_complex',flt,'-map','[vout]','-t',f'{total:.2f}']+ENC+[f'{wd}/video.mp4'])
    # audio mix
    g=spec['gain'];bed=spec.get('bed',-18.5)
    sh(['ffmpeg','-loglevel','error','-y','-i',f'{wd}/voice_raw.wav','-i','bed_raw.wav','-filter_complex',
        f"[0:a]volume={g}dB,apad=whole_dur={total:.2f}[v];[1:a]volume={bed}dB,atrim=0:{total:.2f},afade=t=out:st={total-1.5:.2f}:d=1.5[b];[v][b]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]",'-map','[a]','-t',f'{total:.2f}','-ar','48000',f'{wd}/audio.wav'])
    out=spec['out']
    sh(['ffmpeg','-loglevel','error','-y','-i',f'{wd}/video.mp4','-i',f'{wd}/audio.wav','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',out])
    json.dump({'times':times,'total':total,'voice_end':voice_end},open(f'{wd}/times.json','w'))
    print('ok',out,round(total,1))
if __name__=='__main__': build(json.load(open(sys.argv[1])))
