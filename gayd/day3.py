MEALS = [
    dict(time="08:00", name="Nonushta", kcal=370, p=27, f=21, c=19,
         items=[("Tvorog, 5% gacha", "150 g"), ("Sariyog‘", "1 choy qoshiq (5 g)"),
                ("Yong‘oq", "5–6 dona (15 g)"), ("Meva (olma yoki rezavor)", "100 g")],
         note="Tvorog — sekin hazm bo‘ladigan oqsil, uzoq vaqt to‘q tutadi."),
    dict(time="11:00", name="Tamaddi", kcal=100, p=1, f=0, c=25,
         items=[("Nok", "1 dona (180 g)")],
         note="Kletchatkaga boy meva ichak faoliyatini yaxshilaydi."),
    dict(time="13:30", name="Tushlik", kcal=415, p=19, f=15, c=51,
         items=[("Moshxo‘rda", "1 kosa (350 ml)"), ("Limonli sabzavotli salat", "150 g, 1 choy qoshiq moy")],
         note="Mosh — o‘simlik oqsili va kletchatka manbai."),
    dict(time="16:30", name="Tamaddi", kcal=120, p=8, f=4, c=11,
         items=[("Kefir, 1–2,5%", "1 piyola (250 ml)")],
         note="Kefir ichak mikroflorasini qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=370, p=32, f=10, c=37,
         items=[("Tovuqli sabzavotli dimlama", "300 g"), ("Bulgur, pishgan", "3–4 osh qoshiq (80 g)")],
         note="Oqsil va sabzavotga boy, yengil kechki ovqat — uyqudan 3 soat oldin."),
]
PREP = [
    ("Tvorog", "Yog‘liligi 5% gacha bo‘lgan tvorogni tanlang. Yong‘oqni maydalab seping, mevani yonida torting."),
    ("Moshxo‘rda", "Moshni 2–3 soat oldin ivitib qo‘ying. Yog‘siz go‘sht oling, guruchni kamroq soling, qovurmang."),
    ("Limonli salat", "Moy o‘rniga limon sharbati ishlating, ustidan 1 choy qoshiq zaytun moyi yetarli."),
    ("Tovuqli dimlama", "Terisiz tovuq, ko‘p sabzavot (karam, sabzi, qalampir); moysiz, o‘z sharbatida dimlang."),
    ("Bulgur", "1 o‘lchov bulgurga 2 o‘lchov suv, 15 daqiqa pishiring. Porsiya — 3–4 osh qoshiq."),
]
SHOP = [
    ("Oqsil", ["Tvorog (5%) — 150 g", "Tovuq (terisiz) — 120 g", "Mol go‘shti (yog‘siz) — 60 g", "Kefir — 250 ml"]),
    ("Sabzavot va meva", ["Nok — 1 dona", "Olma yoki rezavor — 100 g", "Sabzi, piyoz, pomidor", "Karam, qalampir", "Limon, ko‘katlar"]),
    ("Don va boshqalar", ["Mosh — 40 g", "Guruch — 30 g", "Bulgur — 30 g (quruq)", "Yong‘oq — 15 g", "Sariyog‘ — 5 g, zaytun moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("salat, sabzavotlar, ko‘katlar", "tvorog, tovuq, go‘sht, kefir", "mosh, guruch, bulgur")
