MEALS = [
    dict(time="08:00", name="Nonushta", kcal=250, p=26, f=8, c=19,
         items=[("Tvorog, 5% gacha", "150 g"), ("Rezavor mevalar", "150 g")],
         note="Oqsil va antioksidantlarga boy yengil nonushta."),
    dict(time="11:00", name="Tamaddi", kcal=60, p=1, f=0, c=14,
         items=[("Mandarin", "2 dona (150 g)")],
         note="C vitamini immunitetni qo‘llab-quvvatlaydi."),
    dict(time="13:30", name="Tushlik", kcal=330, p=26, f=14, c=24,
         items=[("Mol go‘shtli sabzavotli qaynatma sho‘rva", "1 kosa (400 ml)"), ("shundan go‘sht", "100 g")],
         note="Qaynatma sho‘rva — qovurmasiz, oshqozonga yengil."),
    dict(time="16:30", name="Tamaddi", kcal=120, p=8, f=4, c=11,
         items=[("Kefir, 1–2,5%", "1 piyola (250 ml)")],
         note="Kefir ichak mikroflorasini qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=405, p=37, f=11, c=40,
         items=[("Tovuqli grechka (tovuq)", "120 g"), ("Grechka, pishgan", "150 g"), ("Pomidor-bodring salati", "200 g, 1 choy qoshiq moy")],
         note="Oqsil va murakkab uglevod — to‘yimli, lekin yengil."),
]
PREP = [
    ("Tvorog", "Yog‘liligi 5% gacha bo‘lgan tvorogni tanlang. Rezavor mevalar muzlatilgan bo‘lsa ham bo‘ladi."),
    ("Qaynatma sho‘rva", "Yog‘siz mol go‘shtini qaynatib, ko‘pigini oling. Sabzi, qalampir, piyoz, ozroq kartoshka; qovurmang."),
    ("Tovuqli grechka", "Terisiz tovuqni bo‘laklab dimlang, grechka bilan aralashtiring. 1 o‘lchov grechkaga 2 o‘lchov suv."),
    ("Pomidor-bodring salati", "Pomidor, bodring, piyoz, ko‘kat; 1 choy qoshiq zaytun moyi yoki limon."),
    ("Mandarin", "Butun mevani yeng, sharbat emas — kletchatka saqlanadi."),
]
SHOP = [
    ("Oqsil", ["Tvorog (5%) — 150 g", "Mol go‘shti (yog‘siz) — 100 g", "Tovuq (terisiz) — 120 g", "Kefir — 250 ml"]),
    ("Sabzavot va meva", ["Rezavor mevalar — 150 g", "Mandarin — 2 dona", "Pomidor, bodring", "Sabzi, qalampir, piyoz, kartoshka", "Ko‘katlar, limon"]),
    ("Don va boshqalar", ["Grechka — 60 g (quruq)", "Zaytun moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("pomidor, bodring, sabzavotlar", "tvorog, go‘sht, tovuq, kefir", "grechka")
