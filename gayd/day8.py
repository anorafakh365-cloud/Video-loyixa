MEALS = [
    dict(time="08:00", name="Nonushta", kcal=300, p=16, f=15, c=25,
         items=[("Sabzavotli omlet: tuxum", "2 dona"), ("Pomidor, qalampir, ko‘katlar", "130 g"), ("Sariyog‘", "5 g"), ("Donli non", "1 bo‘lak (40 g)")],
         note="Tuxum oqsili va sabzavotlar — kunni yengil va to‘yimli boshlash."),
    dict(time="11:00", name="Tamaddi", kcal=190, p=4, f=10, c=21,
         items=[("Anor donalari", "½ dona (100 g)"), ("Yong‘oq", "5–6 dona (15 g)")],
         note="Anor — antioksidantlarga boy, yong‘oq — foydali yog‘lar."),
    dict(time="13:30", name="Tushlik", kcal=440, p=26, f=22, c=35,
         items=[("Mol go‘shtli tefteli", "4–5 dona (150 g)"), ("Bulgur, pishgan", "100 g"), ("Salat", "150 g, 1 choy qoshiq moy")],
         note="Oqsil, murakkab uglevod va sabzavot — to‘liq tushlik."),
    dict(time="16:30", name="Tamaddi", kcal=120, p=8, f=4, c=11,
         items=[("Kefir, 1–2,5%", "1 piyola (250 ml)")],
         note="Kefir ichak mikroflorasini qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=240, p=5, f=10, c=32,
         items=[("Qovoq va sabzavotli sho‘rva", "1 kosa (400 ml)"), ("Sabzi salat", "150 g")],
         note="Eng yengil kechki ovqat — beta-karotin va kletchatkaga boy."),
]
PREP = [
    ("Sabzavotli omlet", "Pomidor va qalampirni 5 g sariyog‘da 2–3 daqiqa yumshating. Ko‘katli tuxumni quyib, qopqoq ostida 4–5 daqiqa pishiring."),
    ("Tefteli", "Yog‘siz mol qiymasi, piyoz, ko‘kat va 1 tuxum oqi. Qovurmasdan, pomidorli sousda 25 daqiqa dimlang."),
    ("Bulgur", "1 o‘lchov bulgurga 2 o‘lchov suv, 15 daqiqa pishiring."),
    ("Qovoqli sho‘rva", "Qovoq, sabzi, piyoz, kartoshka kam. Blenderda pyure-sho‘rva qilsa ham bo‘ladi."),
    ("Sabzi salat", "Sabzini qirg‘ichdan o‘tkazing, limon sharbati va 1 choy qoshiq moy qo‘shing. Sarimsoq — ixtiyoriy."),
]
SHOP = [
    ("Oqsil", ["Tuxum — 2 dona (+1 oqi)", "Mol go‘shti qiymasi (yog‘siz) — 120 g", "Kefir — 250 ml"]),
    ("Sabzavot va meva", ["Anor — ½ dona", "Qovoq — 200 g", "Sabzi — 2 dona", "Pomidor, bolgar qalampiri", "Piyoz, ko‘katlar, limon"]),
    ("Don va boshqalar", ["Donli non — 1 bo‘lak", "Bulgur — 35 g (quruq)", "Yong‘oq — 15 g", "Sariyog‘ — 5 g, zaytun moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("salat, pomidor sousi, qovoq", "tefteli, tuxum, kefir", "bulgur, donli non")
