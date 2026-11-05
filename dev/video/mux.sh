#!/bin/bash
# $1 = salida
T=/tmp/claude-0/s/trailer;D=$(python3 -c "import os;print(len(os.listdir('$T/frames_final'))/30)")
ffmpeg -y -loglevel error -framerate 30 -i $T/frames_final/f%05d.jpg -ss 88.77 -t $D -i /tmp/claude-0/s/vid/suno/fest.wav -i $T/sfx.wav \
 -filter_complex "[1:a]afade=t=in:d=1.5,afade=t=out:st=$(python3 -c "print($D-1.6)"):d=1.6,volume=0.75[m];[2:a]volume=1.0[s];[m][s]amix=inputs=2:normalize=0[a]" \
 -map 0:v -map "[a]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest "$1"
