# TEZORA — gilam yuvish reklamasi

Vertikal **9:16, 1080×1920**, 30 fps, 31 soniya. Instagram Reels / TikTok / YouTube Shorts / Telegram uchun (−14 LUFS).
Tayyor fayl: `out/TEZORA_reklama_9x16.mp4`

Pastki panelda (butun video davomida): **66-200-17-00 · Samarqand**.

## Sahnalar
| Vaqt | Sahna |
|---|---|
| 0:00–0:07 | Boshlovchi: "Assalomu alaykum! Gilamlaringizga haqiqiy tozalik kerakmi?" — TEZORA logotipi |
| 0:07–0:14 | Sex, cho'tkali yuvish mashinasi — "Zamonaviy uskunalar", "Professional yuvish texnologiyasi" |
| 0:14–0:17 | Tez montaj: 01 Yuvish · 02 Chayish · 03 Quritish · 04 Sifat nazorati |
| 0:17–0:19 | "Barchasi bir joyda!" ro'yxati |
| 0:19–0:22 | Boshlovchi: "Biz uchun har bir mijozning ishonchi muhim" ★★★★★ |
| 0:22–0:25 | Osilgan gilamlar — "Gilamingizni bizga topshiring…" |
| 0:25–0:31 | Yakuniy kadr: logotip, "Zamonaviy tozalik xizmati", "Hoziroq buyurtma bering!" |

## Qayta yig'ish
```bash
pip install numpy pillow
python3 tezora/src/audio.py      # musiqa + effektlar
python3 tezora/src/render.py     # video (~10 daqiqa)
bash tezora/src/build.sh         # ovoz + musiqa + yakuniy mp4
python3 tezora/src/render.py --stills 3 15 27   # nazorat kadrlari
```
Telefon, shahar, matnlar va vaqtlar `src/render.py` boshida va `CAPS` / `SHOTS` ro'yxatlarida.
