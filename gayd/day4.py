MEALS = [
    dict(time="08:00", name="Nonushta", kcal=300, p=16, f=15, c=25,
         items=[("Sabzavotli omlet: tuxum", "2 dona"), ("Bolgar qalampiri, pomidor", "50 g + 80 g"),
                ("Ko‘katlar, sariyog‘", "1 hovuch, 5 g"), ("Donli non", "1 bo‘lak (40 g)")],
         note="Tuxum oqsili va sabzavotlar — kunni yengil va to‘yimli boshlash."),
    dict(time="11:00", name="Tamaddi", kcal=190, p=4, f=10, c=21,
         items=[("Kivi", "2 dona (140 g)"), ("Yong‘oq", "5–6 dona (15 g)")],
         note="Kivi — C vitaminiga boy, yong‘oq — foydali yog‘lar manbai."),
    dict(time="13:30", name="Tushlik", kcal=290, p=20, f=10, c=30,
         items=[("Qovoqli mol go‘shtli sho‘rva", "1 kosa (400 ml)"), ("shundan go‘sht", "80 g")],
         note="Qovoq — beta-karotin va kletchatka, oshqozonga yengil."),
    dict(time="16:30", name="Tamaddi", kcal=130, p=14, f=5, c=6,
         items=[("Tabiiy grek yogurti", "150 g, shakarsiz")],
         note="Oqsilga boy tamaddi mushaklarni qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=335, p=38, f=11, c=21,
         items=[("Tovuq ko‘kragi, pechda", "150 g"), ("Bulgur, pishgan", "3–4 osh qoshiq (80 g)"),
                ("Ko‘katli salat", "150 g, 1 choy qoshiq moy")],
         note="Oqsilga boy, yengil kechki ovqat — uyqudan 3 soat oldin."),
]
PREP = [
    ("Sabzavotli omlet", "Bolgar qalampiri va pomidorni 5 g sariyog‘da 2–3 daqiqa yumshating. Ko‘katli tuxumni quyib, qopqoq ostida past olovda 4–5 daqiqa pishiring."),
    ("Qovoqli sho‘rva", "Yog‘siz mol go‘shtini qaynatib, ko‘pigini oling. Qovoq, sabzi, piyoz qo‘shing; qovurmang, kartoshkani kamroq soling."),
    ("Pechda tovuq", "Tovuq ko‘kragini sarimsoq, limon va ziravor bilan 30 daqiqa marinadlang. 200°C da folgada 20–25 daqiqa pishiring."),
    ("Bulgur", "1 o‘lchov bulgurga 2 o‘lchov suv, 15 daqiqa pishiring. Porsiya — 3–4 osh qoshiq."),
    ("Grek yogurti", "Tabiiy, shakarsiz turini tanlang. Shirinlik kerak bo‘lsa, bir oz kivi bo‘lagi qo‘shing."),
]
SHOP = [
    ("Oqsil", ["Tuxum — 2 dona", "Mol go‘shti (yog‘siz) — 80 g", "Tovuq ko‘kragi — 150 g", "Grek yogurti — 150 g"]),
    ("Sabzavot va meva", ["Kivi — 2 dona", "Qovoq — 150 g", "Bolgar qalampiri, pomidor", "Sabzi, piyoz, kartoshka", "Ko‘katlar, limon, sarimsoq"]),
    ("Don va boshqalar", ["Donli non — 1 bo‘lak", "Bulgur — 30 g (quruq)", "Yong‘oq — 15 g", "Sariyog‘ — 5 g", "Zaytun moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("qovoq, ko‘katlar, salat", "tuxum, tovuq, go‘sht, yogurt", "donli non, bulgur")
