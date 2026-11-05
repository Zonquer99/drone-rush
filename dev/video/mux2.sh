#!/bin/bash
# $1 = v5|v2  $2 = salida
T=/tmp/claude-0/s/trailer;D=$(python3 -c "import os;print(len(os.listdir('$T/fr_$1'))/30)")
python3 $T/scripts/sfx2.py $1 $D
ffmpeg -y -loglevel error -framerate 30 -i $T/fr_$1/f%05d.jpg -i $T/sfx_$1.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest "$2"
