#!/usr/bin/env bash
# Yakuniy yig'ish: video + diktor ovozi + fon musiqasi (ovoz paytida musiqa pasayadi).
# Natija:
#   out/AZDIF_reklama_UHD_9x16.mp4      — ijtimoiy tarmoqlar uchun (-14 LUFS)
#   out/AZDIF_reklama_UHD_9x16_TV.mp4   — TV standarti EBU R128 (-23 LUFS)
set -euo pipefail
cd "$(dirname "$0")/.."

mix() { # $1 = LUFS, $2 = chiqish fayli
  ffmpeg -y -loglevel error -i out/_video.mp4 -i assets/voice.mp3 -i out/_music.wav -filter_complex "
    [1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,volume=1.0[v];
    [v]asplit=2[vmix][vkey];
    [2:a]volume=0.32[m];
    [m][vkey]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=400[mduck];
    [vmix][mduck]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=$1:TP=-1.5:LRA=11,aresample=48000[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 320k -ar 48000 -movflags +faststart -t 68.05 "$2"
}
mix -14 out/AZDIF_reklama_UHD_9x16.mp4
mix -23 out/AZDIF_reklama_UHD_9x16_TV.mp4
ls -la out/*.mp4
