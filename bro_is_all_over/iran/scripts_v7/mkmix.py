import json,sys,subprocess
VG=float(sys.argv[1]); out=sys.argv[2]
S={x['n']:x for x in json.load(open('v7/segs.json'))}
P30=S[30]['start']; P3=S[3]['start']; P16=S[16]['start']; P23=S[23]['start']
FIN=P30-0.28; DUR=FIN+9.6; SUB=191.5
labs=json.load(open('v7/labs.json'))
inp=['-i v7/raw.mp4','-framerate 30 -i sub/fr/%04d.png','-i v6/title6.png','-i v6/date.png','-i v6/stat44.png']
for f,_,_ in labs: inp.append('-i '+f)
n0=5+len(labs)
inp+= ['-i v7/voice24.wav','-i v7/voice24.wav','-i v4/bed4.wav','-i v4/bed4.wav','-i v5/sons/B_laiton_lourd.wav']
vf=f"[1:v]setpts=PTS+{SUB}/TB[s];[0:v][s]overlay=enable='between(t,{SUB},{SUB+4})':eof_action=pass[a0];[a0][2:v]overlay=enable='between(t,0,4.5)'[a1];[a1][3:v]overlay=enable='between(t,{P3+0.3:.2f},{P3+4.4:.2f})'[a2];[a2][4:v]overlay=enable='between(t,{P16+8.2:.2f},{P16+14.2:.2f})'[b0]"
prev='b0'
for i,(f,t0,t1) in enumerate(labs):
    nxt=f'b{i+1}'; vf+=f";[{prev}][{5+i}:v]overlay=enable='between(t,{t0},{t1})'[{nxt}]"; prev=nxt
af=(f";[{n0}:a]aresample=48000,atrim=0:{P30-0.13:.3f},asetpts=PTS-STARTPTS,volume={VG}dB,apad=whole_dur={DUR:.2f}[v1]"
    f";[{n0+1}:a]aresample=48000,atrim={P30:.3f}:254.4,asetpts=PTS-STARTPTS,volume={VG}dB,adelay={int((FIN+2.02)*1000)},apad=whole_dur={DUR:.2f}[v2]"
    f";[{n0+2}:a][{n0+3}:a]acrossfade=d=3,atrim=0:{DUR:.2f},afade=t=out:st={DUR-3:.2f}:d=3,volume=-18.5dB[bd]"
    f";[{n0+4}:a]aresample=48000,adelay={int((FIN+1.47)*1000)},apad=whole_dur={DUR:.2f}[st]"
    ";[v1][v2][bd][st]amix=inputs=4:normalize=0,alimiter=limit=0.95[au]")
cmd=f"ffmpeg -y -loglevel error {' '.join(inp)} -filter_complex \"{vf}{af}\" -map \"[{prev}]\" -map \"[au]\" -t {DUR:.2f} -c:v libx264 -preset veryfast -b:v 2.7M -maxrate 3.1M -bufsize 6M -pix_fmt yuv420p -c:a aac -b:a 192k {out}"
open('v7/mix7.sh','w').write(cmd); print(DUR)
