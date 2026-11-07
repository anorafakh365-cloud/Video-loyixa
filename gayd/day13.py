MEALS = [
    dict(time="08:00", name="Nonushta", kcal=265, p=20, f=18, c=6,
         items=[("Tuxum", "2 dona"), ("Pishloq, kam tuzli", "30 g"), ("Pomidor", "150 g")],
         note="Oqsilga boy nonushta — uzoq vaqt to‘qlik."),
    dict(time="11:00", name="Tamaddi", kcal=185, p=3, f=10, c=21,
         items=[("Olma", "1 dona (150 g)"), ("Yong‘oq", "5–6 dona (15 g)")],
         note="Kletchatka va foydali yog‘lar — energiyani bir tekis ushlaydi."),
    dict(time="13:30", name="Tushlik", kcal=400, p=27, f=19, c=30,
         items=[("Mol go‘shtli sho‘rva", "1 kosa (400 ml)"), ("Ko‘katli salat", "150 g, 1 choy qoshiq moy")],
         note="Issiq sho‘rva va ko‘katlar — hazm uchun qulay tushlik."),
    dict(time="16:30", name="Tamaddi", kcal=120, p=8, f=4, c=11,
         items=[("Kefir, 1–2,5%", "1 piyola (250 ml)")],
         note="Kefir ichak mikroflorasini qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=330, p=39, f=8, c=25,
         items=[("Tovuq, duxovkada", "150 g"), ("Bulgur, pishgan", "3–4 osh qoshiq (80 g)"), ("Sabzavotlar", "200 g")],
         note="Oqsilga boy, yengil kechki ovqat — uyqudan 3 soat oldin."),
]
PREP = [
    ("Tuxum va pishloq", "Tuxumni qaynating yoki moysiz tovada pishiring. Pishloqning kam tuzli turini tanlang."),
    ("Mol go‘shtli sho‘rva", "Yog‘siz go‘shtni qaynatib, ko‘pigini oling. Sabzi, qalampir, piyoz, ozroq kartoshka; qovurmang."),
    ("Duxovkada tovuq", "Tovuq ko‘kragini sarimsoq, limon, ziravor bilan marinadlang. 200°C da folgada 20–25 daqiqa."),
    ("Bulgur", "1 o‘lchov bulgurga 2 o‘lchov suv, 15 daqiqa pishiring."),
    ("Sabzavotlar", "Tovuq bilan birga pechda yoki bug‘da pishiring: qalampir, kabachok, sabzi."),
]
SHOP = [
    ("Oqsil", ["Tuxum — 2 dona", "Pishloq (kam tuzli) — 30 g", "Mol go‘shti (yog‘siz) — 100 g", "Tovuq ko‘kragi — 150 g", "Kefir — 250 ml"]),
    ("Sabzavot va meva", ["Pomidor — 150 g", "Olma — 1 dona", "Sabzi, qalampir, kabachok", "Piyoz, kartoshka", "Ko‘katlar, limon, sarimsoq"]),
    ("Don va boshqalar", ["Bulgur — 30 g (quruq)", "Yong‘oq — 15 g", "Zaytun moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("pomidor, ko‘katlar, sabzavotlar", "tuxum, go‘sht, tovuq, kefir", "bulgur")
