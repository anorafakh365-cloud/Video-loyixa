#!/usr/bin/env bash
# v2 yakuniy yig'ish: video + diktor + saundtrek (diktor gapirganda musiqa pasayadi).
set -euo pipefail
cd "$(dirname "$0")/../.."
V=out/_v2_video.mp4

mixaudio() { # $1 LUFS  $2 chiqish.wav
  ffmpeg -y -loglevel error -i assets/voice.mp3 -i out/_v2_music.wav -filter_complex "
    [0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=70,equalizer=f=3000:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=3:attack=5:release=120[v];
    [v]asplit=2[vm][vk];
    [1:a]volume=0.42[m];
    [m][vk]sidechaincompress=threshold=0.025:ratio=5:attack=30:release=350[md];
    [vm][md]amix=inputs=2:normalize=0:duration=longest,apad,atrim=0:70,loudnorm=I=$1:TP=-1.5:LRA=11,aresample=48000" \
    -c:a pcm_s16le "$2"
}
mixaudio -14 out/_v2_mix_social.wav
mixaudio -23 out/_v2_mix_tv.wav

enc() { # $1 audio  $2 out  $3.. video opts
  local a=$1 o=$2; shift 2
  ffmpeg -y -loglevel error -i $V -i "$a" -map 0:v -map 1:a "$@" -c:a aac -b:a 256k -ar 48000 -movflags +faststart -t 70 "$o"
}
enc out/_v2_mix_social.wav out/AZDIF_v2_UHD_9x16.mp4 -c:v libx264 -preset slow -crf 17 -maxrate 40M -bufsize 80M -profile:v high -level 5.1 -pix_fmt yuv420p
enc out/_v2_mix_tv.wav out/AZDIF_v2_UHD_9x16_TV.mp4 -c:v copy
enc out/_v2_mix_social.wav out/AZDIF_v2_4K_yengil.mp4 -c:v libx264 -preset medium -b:v 10M -maxrate 14M -bufsize 28M -profile:v high -level 5.1 -pix_fmt yuv420p
enc out/_v2_mix_social.wav out/AZDIF_v2_telefon.mp4 -vf scale=1080:1920:flags=lanczos -c:v libx264 -preset slow -profile:v main -level 4.0 -b:v 1800k -maxrate 2600k -bufsize 5200k -pix_fmt yuv420p
ls -la out/AZDIF_v2_*
