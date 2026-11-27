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
def visual(src,pr,d,out,fx=.5,HV=1920):
    pad=f",pad={W}:{H}:0:{H-HV}:black" if HV<H else ""
    if src.endswith('.mp4'):
        w,h=[int(x) for x in subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0:s=x',src],capture_output=True,text=True).stdout.strip().split('x')[:2]]
        if h>w: vf=f"scale={W}:{HV}:force_original_aspect_ratio=increase,crop={W}:{HV},fps=30,format=yuv420p"+pad
        else:
            f=(str(pr['x0']) if 'x0' in pr else (f"t/{d}" if pr.get('sens',1)==1 else f"1-t/{d}"))
            vf=f"scale=-2:{HV}:force_original_aspect_ratio=increase,crop={W}:{HV}:x='(iw-{W})*({f})':y=0,fps=30,format=yuv420p"+pad
        sh(['ffmpeg','-loglevel','error','-y','-ss',str(pr.get('ss',1)),'-i',src,'-t',str(d),'-vf',"tpad=stop_mode=clone:stop_duration=2,"+vf,'-an']+ENC+[out]);return
    n=int(d*30)+2;zs,ze,fxx=pr.get('zs',1.0),pr.get('ze',1.1),pr.get('fx',.5)
    z=f"{zs}+({ze}-{zs})*on/{n}"
    fc=(f"[0:v]scale=-2:{HV*2}:flags=lanczos,crop=2160:{HV*2}:x='(iw-2160)*{fxx}':y=0,"
        f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{HV}:fps=30,format=yuv420p"+pad)
    sh(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','30','-t',str(d),'-i',src,'-vf',fc,'-t',str(d),'-an']+ENC+[out])

LORA='/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
YEL=(255,210,63);TEAL=(12,60,70)
def gabarit_png(path,G,c):
    N=len(G['names']);dont=G['kind']=='dont'
    im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,216),fill=TEAL+(255,));d.rectangle((0,216,W,220),fill=YEL+(255,))
    ft=ImageFont.truetype(ANTON,56);t1="THE DON'T LIST" if dont else "THE MUST DO LIST"
    d.text((44,26),t1,font=ft,fill=YEL);d.text((44+d.textlength(t1+' ',font=ft),26),f"{c}/{N}",font=ft,fill=(255,255,255))
    fn=ImageFont.truetype(ANTON,32);xs=[110+190*i for i in range(N)]
    for i,x in enumerate(xs):
        nm=G['names'][i];d.text((x-d.textlength(nm,font=fn)/2,118),nm,font=fn,fill=YEL)
    y=190
    for i in range(N):
        x=xs[i]
        if i<c-1: d.line((x,y,xs[i+1],y),fill=YEL,width=5)
        elif i==c-1 and i<N-1:
            for xx in range(x+20,xs[i+1]-6,19): d.ellipse((xx-3,y-3,xx+3,y+3),fill=(120,170,175))
        elif i>c-1 and i<N-1:
            for xx in range(x+14,xs[i+1]-6,19): d.ellipse((xx-3,y-3,xx+3,y+3),fill=(120,170,175))
    for i,x in enumerate(xs):
        r=15 if i==c-1 else 10
        if i==c-1: d.ellipse((x-r-6,y-r-6,x+r+6,y+r+6),fill=YEL+(70,))
        d.ellipse((x-r,y-r,x+r,y+r),fill=YEL)
    fl=Image.open('flag_tmp.png').convert('RGBA').rotate(3,expand=True,resample=Image.BICUBIC);im.paste(fl,(905,4),fl)
    # card
    title,cap=G['cards'][c-1]
    ov=Image.new('RGBA',(W,H),(0,0,0,0));od=ImageDraw.Draw(ov)
    od.rounded_rectangle((40,1306,900,1494),radius=14,fill=(6,40,48,175),outline=YEL+(255,),width=5)
    im=Image.alpha_composite(im,ov);d=ImageDraw.Draw(im)
    s=76
    while True:
        f=ImageFont.truetype(ANTON,s)
        if d.textlength(title,font=f)<=780: break
        s-=3
    d.text((76,1328+(76-s)//2),title,font=f,fill=YEL)
    fc=ImageFont.truetype(LORA,36);fc.set_variation_by_axes([700])
    cs=36
    while d.textlength(cap,font=fc)>790: cs-=1;fc=ImageFont.truetype(LORA,cs);fc.set_variation_by_axes([700])
    d.text((76,1426),cap,font=fc,fill=(255,255,255))
    # tag
    tg=Image.new('RGBA',(300,120),(0,0,0,0));td=ImageDraw.Draw(tg);ff=ImageFont.truetype(ANTON,50)
    label="DON'T" if dont else "\u2713 MUST DO"
    if dont:
        wv=int(td.textlength(label,font=ff))+44;td.rounded_rectangle((4,4,4+wv,84),radius=10,fill=(215,19,42,255),outline=(255,255,255,255),width=4);td.text((26,12),label,font=ff,fill=(255,255,255))
    else:
        lab="MUST DO";wv=int(td.textlength(lab,font=ff))+44+44;td.rounded_rectangle((4,4,4+wv,84),radius=10,fill=YEL+(255,),outline=(30,26,34,255),width=4)
        td.line((26,48,38,62),fill=(30,26,34,255),width=7);td.line((38,62,58,30),fill=(30,26,34,255),width=7);td.text((70,12),lab,font=ff,fill=(30,26,34))
    tg=tg.rotate(4,expand=True,resample=Image.BICUBIC);im.paste(tg,(900-tg.width+20,1238),tg)
    im.save(path)
def build(spec):
    subprocess.run(['rsvg-convert','-w','128','ir_flag.svg','-o','flag_tmp0.png']);fi0=Image.open('flag_tmp0.png').convert('RGBA');bd=Image.new('RGBA',(fi0.width+8,fi0.height+8),(255,255,255,255));bd.paste(fi0,(4,4),fi0);bd.save('flag_tmp.png')
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
    END=0.0;total=voice_end+0.35;body=voice_end+0.35
    # visuels : un par coupe (ou plus) - bornes = débuts de coupes
    vis=spec['visuals'];starts=[0.0]+[tt[0]-pad-gap/2 if False else None for tt in times[1:]]
    bounds=[0.0]+[times[i][0]-gap/2-pad for i in range(1,len(times))]+[body]
    segs=[]
    for i,v in enumerate(vis):
        a=bounds[v['cut']];b=bounds[v['cut']+1] if 'upto' not in v else bounds[v['upto']+1]
        if 'part' in v:
            pi,pk=v['part'];L=b-a;a,b=a+L*pi/pk,a+L*(pi+1)/pk
        segs.append((i,v,a,b))
    for i,v,a,b in segs:
        visual(v['src'],v.get('p',{}),round(b-a,3),f'{wd}/v{i}.mp4',HV=(1920 if (v['cut']==0 or not spec.get('gabarit')) else 1700))
    # fin : plus de carte d'avertissement (retiree sur demande 26 nov 22:26)
    open(f'{wd}/vl.txt','w').write(''.join(f"file 'v{i}.mp4'\n" for i,_,_,_ in segs))
    sh(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',f'{wd}/vl.txt','-c','copy',f'{wd}/body.mp4'])
    # textes
    inputs=['-i',f'{wd}/body.mp4'];flt='';last='[0:v]';k=1
    hk=spec['hook'];text_png(f'{wd}/hook.png',hk,spec.get('hook_size',150),spec.get('hook_y',1180))
    ov=[(f'{wd}/hook.png',0.0,2.0)]
    G=spec.get('gabarit')
    if G:
        for c in range(1,len(times)):
            gabarit_png(f'{wd}/gab{c}.png',G,c)
            a0=bounds[c] if c>1 else max(2.0,bounds[c]);b0=bounds[c+1] if c+1<len(bounds) else body
            ov.append((f'{wd}/gab{c}.png',a0,b0))
    else:
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
