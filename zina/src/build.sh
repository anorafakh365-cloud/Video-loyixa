#!/usr/bin/env bash
# «54 zina» yakuniy yig'ish: ovoz (1 s kechikish) + musiqa (ovoz ostida pasayadi) + video.
#   bash zina/src/build.sh zina/assets/ovoz.mp3
set -euo pipefail
cd "$(dirname "$0")/.."
VOICE=${1:-assets/ovoz.mp3}; [ -f "$VOICE" ] || VOICE="../$1"
python3 src/sync.py "$VOICE"
python3 src/audio.py
python3 src/render.py
ffmpeg -y -loglevel error -i "$VOICE" -i out/_music.wav -filter_complex "
  [0:a]aresample=48000,adelay=1000|1000,pan=stereo|c0=c0|c1=c0,highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,apad[v];
  [v]asplit=2[vm][vk]; [1:a]volume=0.5[m];
  [m][vk]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=400[md];
  [md][vm]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9" -c:a pcm_s16le out/_mix.wav
ffmpeg -y -loglevel error -i out/_video.mp4 -i out/_mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 19 -maxrate 12M -bufsize 24M \
  -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart -shortest out/54_zina.mp4
ls -la out/54_zina.mp4
