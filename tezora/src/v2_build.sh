#!/usr/bin/env bash
# TEZORA v2 yig'ish: mijoz videosining asl ovozi + musiqa (ovoz ostida pasayadi) -> 4K 60 fps yakuniy fayl.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -y -loglevel error -i assets/manba.mov -i out/_v2_music.wav -filter_complex "
  [0:a]aresample=48000,highpass=f=70,equalizer=f=3500:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,loudnorm=I=-16:TP=-2:LRA=8[v];
  [v]asplit=2[vm][vk];
  [1:a]volume=0.32[m];
  [m][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[md];
  [vm][md]amix=inputs=2:normalize=0:duration=longest,apad,atrim=0:30.4,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000" \
  -c:a pcm_s16le out/_v2_mix.wav
ffmpeg -y -loglevel error -i out/_v2_video.mp4 -i out/_v2_mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 16 \
  -maxrate 45M -bufsize 90M -profile:v high -level 5.2 -pix_fmt yuv420p -r 60 -c:a aac -b:a 320k -ar 48000 \
  -movflags +faststart -t 30.4 out/TEZORA_v2_4K_60fps.mp4
ls -la out/TEZORA_v2_4K_60fps.mp4
