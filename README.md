# AZDIF 45% S.C. — reklama roligi

Vertikal **9:16 Ultra HD (2160×3840)**, 25 fps, 68 soniya. Diktor ovozi: `assets/voice.mp3`.

## Tayyor fayllar (`out/`)
| Fayl | Maqsad |
|---|---|
| `AZDIF_reklama_UHD_9x16.mp4` | Instagram Reels / TikTok / YouTube Shorts / Telegram (−14 LUFS) |
| `AZDIF_reklama_UHD_9x16_TV.mp4` | TV efir standarti EBU R128 (−23 LUFS) |

## Sahnalar
| Vaqt | Sahna |
|---|---|
| 0:00–0:03 | Quyosh chiqishidagi uzumzor — "Sog'lom bog' — mo'l hosil garovi" |
| 0:03–0:12 | Muammo: uzum bargida zamburug' dog'lari va un shudring o'sadi |
| 0:12–0:21 | Mahsulot: AZDIF 45% S.C. flakoni nur ichida paydo bo'ladi |
| 0:21–0:31 | Tarkib: Azoksistrobin 250 g/l + Difenokonazol 200 g/l |
| 0:31–0:45 | Ekinlar: uzum, pomidor, shaftoli, loviya |
| 0:45–0:57 | Himoya: purkash, dog'lar yo'qoladi, barg sog'ayadi |
| 0:57–1:08 | Yakuniy kadr: flakon, nom, 500 ml, ogohlantirish |

## Qayta yig'ish
```bash
pip install numpy pillow
python3 src/audio.py          # fon musiqasi + effektlar
K=2 python3 src/render.py     # video (K=1 — tezkor 1080x1920 sinov)
bash src/build.sh             # ovoz + musiqa + yakuniy mp4
python3 src/render.py --stills 8 27 40   # nazorat kadrlari
```
Matn, vaqt va ranglar `src/render.py` dagi `sc_*` funksiyalarida.
