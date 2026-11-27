from PIL import Image,ImageDraw,ImageFont
F='/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf'
GRAY=(62,69,72,255); W=(255,255,255,255); Y=(255,215,0,255); R=(255,46,59,255)
def card(lines,out,size=112):
    # lines: list of (text,color) bottom-left box, same look as title card
    f=ImageFont.truetype(F,size)
    wmax=max(f.getlength(t) for t,_ in lines)
    h=len(lines)*118+60
    x0,y1=60,1010; y0=y1-h; x1=int(x0+50+wmax+50)
    im=Image.new('RGBA',(1920,1080),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((x0,y0,x1,y1),radius=28,fill=GRAY)
    for i,(t,c) in enumerate(lines):
        d.text((x0+50,y0+30+i*118+ (0)),t,font=f,fill=c,anchor='la')
    im.save(out); return x1
if __name__=='__main__':
    card([('THE WORLD CALLED IT PERSIA.',W),('THEN IT ASKED FOR IRAN',Y)],'t_test.png')
