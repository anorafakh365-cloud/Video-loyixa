#!/usr/bin/env bash
# TEZORA yakuniy yig'ish: video + diktor (0.4 s kechikish) + musiqa (diktor gapirganda pasayadi).
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -y -loglevel error -i assets/voice.mp3 -i out/_music.wav -filter_complex "
  [0:a]aresample=48000,adelay=400,pan=stereo|c0=c0|c1=c0,highpass=f=80,equalizer=f=200:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=100,volume=1.2[v];
  [v]asplit=2[vm][vk];
  [1:a]volume=0.55[m];
  [m][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];
  [vm][md]amix=inputs=2:normalize=0:duration=longest,apad,atrim=0:31,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000" \
  -c:a pcm_s16le out/_mix.wav
ffmpeg -y -loglevel error -i out/_video.mp4 -i out/_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -movflags +faststart -t 31 out/_master.mp4
ffmpeg -y -loglevel error -i out/_master.mp4 -c:v libx264 -preset slow -crf 18 -maxrate 24M -bufsize 48M -profile:v high -level 5.1 -pix_fmt yuv420p -c:a copy -movflags +faststart out/TEZORA_reklama_9x16.mp4
ls -la out/TEZORA_reklama_9x16.mp4
