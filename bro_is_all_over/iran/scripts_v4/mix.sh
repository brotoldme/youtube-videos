ffmpeg -y -loglevel error -i v4/raw.mp4 -framerate 30 -i sub/fr/%04d.png -i v4/title_long4.png -i v4/long_raw.wav -i v4/bed4.wav \
-filter_complex "[1:v]setpts=PTS+178.6/TB[s];[0:v][s]overlay=enable='between(t,178.6,182.6)':eof_action=pass[a];[a][2:v]overlay=enable='between(t,0,3.5)'[v];[3:a]volume=-3dB,apad=whole_dur=238.2[vo];[4:a]volume=-18.5dB[b];[vo][b]amix=inputs=2:normalize=0,alimiter=limit=0.95[au]" \
-map "[v]" -map "[au]" -t 238.2 -c:v libx264 -preset veryfast -b:v 3.2M -maxrate 3.8M -bufsize 7M -pix_fmt yuv420p -c:a aac -b:a 192k iran_long_v4.mp4
