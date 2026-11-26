set -e
cd /home/claude/japon/jp2
ffmpeg -loglevel error -y -f concat -safe 0 -i seg2/list.txt -c copy seg2/raw.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 seg2/raw.mp4
