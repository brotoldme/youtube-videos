import sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ANTON='/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf'
RED=(255,46,59); WHITE=(255,255,255)
def flag(w):
    subprocess.run(['rsvg-convert','-w',str(w*2),'../carte/flag_japan.svg','-o','flag_big.png'],check=True)
    f=Image.open('flag_big.png').convert('RGBA'); return f.resize((w,round(f.height*w/f.width)),Image.LANCZOS)
def grad(im,W,H):
    g=Image.new('L',(1,H))
    for y in range(H): g.putpixel((0,y),int(max(0,(y-H*0.5)/(H*0.5))**1.2*150))
    im.paste(Image.new('RGB',(W,H),(0,0,0)),(0,0),g.resize((W,H)))
def put_flag(im,w,m):
    f=flag(w); bd=Image.new('RGBA',(f.width+8,f.height+8),(10,10,14,255)); bd.paste(f,(4,4),f)
    im.paste(bd,(im.width-bd.width-m,m),bd)
def shadow(im,items,off):
    W,H=im.size; sh=Image.new('L',(W,H),0); sd=ImageDraw.Draw(sh)
    for f,x,y,t,sw in items: sd.text((x+6,y+7),t,font=f,fill=200,stroke_width=sw,stroke_fill=200)
    sh=sh.filter(ImageFilter.GaussianBlur(8)); im.paste(Image.new('RGB',(W,H),(0,0,0)),(0,0),sh)
def long(img,l1,key,out):
    W,H=1280,720; im=Image.open(img).convert('RGB')
    r=max(W/im.width,H/im.height); im=im.resize((round(im.width*r)+1,round(im.height*r)+1),Image.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2; im=im.crop((x,y,x+W,y+H)); im=im.filter(ImageFilter.UnsharpMask(2,80,2))
    grad(im,W,H); d=ImageDraw.Draw(im)
    size=108
    while True:
        f=ImageFont.truetype(ANTON,size)
        if d.textlength(l1+' '+key,font=f)<=W*0.90-0: break
        size-=2
    yy=H-70-size; x0=51
    shadow(im,[(f,x0,yy,l1+' '+key,6)],0)
    d=ImageDraw.Draw(im)
    d.text((x0,yy),l1+' ',font=f,fill=WHITE,stroke_width=6,stroke_fill=(0,0,0))
    d.text((x0+d.textlength(l1+' ',font=f),yy),key,font=f,fill=RED,stroke_width=6,stroke_fill=(0,0,0))
    put_flag(im,260,36); im.save(out,quality=92); print(out,size)
def short(img,l1,l2,out,pos=0.5):
    W,H=1080,1920; im=Image.open(img).convert('RGB')
    r=max(W/im.width,H/im.height); im=im.resize((round(im.width*r)+1,round(im.height*r)+1),Image.LANCZOS)
    x=int((im.width-W)*pos); y=(im.height-H)//2; im=im.crop((x,y,x+W,y+H)); im=im.filter(ImageFilter.UnsharpMask(2,80,2))
    grad(im,W,H); d=ImageDraw.Draw(im)
    f2=ImageFont.truetype(ANTON,120); f1=ImageFont.truetype(ANTON,70); x0=70
    rows=[];cur=''
    if d.textlength(l2,font=f2)<=W-2*x0: rows=[l2]
    else:
        for w in l2.split():
            t=(cur+' '+w).strip()
            if d.textlength(t,font=f2)<=W*0.77: cur=t
            else: rows.append(cur);cur=w
        rows.append(cur)
    y=H-420-f2.size*len(rows); lines=[(f1,y-f1.size*1.05,l1)]
    for w in rows: lines.append((f2,y,w)); y+=f2.size
    shadow(im,[(f,x0,yy,t,6) for f,yy,t in lines],0)
    d=ImageDraw.Draw(im)
    for i,(f,yy,t) in enumerate(lines): d.text((x0,yy),t,font=f,fill=WHITE if i==0 else RED,stroke_width=7,stroke_fill=(0,0,0))
    put_flag(im,200,50); im.save(out,quality=92); print(out)
if __name__=='__main__':
    long('long_raw.jpg','LOCKED FOR','220 YEARS','miniature_pays_long.jpg')
    short('short_raw.jpg',"JAPAN'S SAMURAI",'ABOLISHED THEMSELVES','miniature_pays_short.jpg',0.5)
