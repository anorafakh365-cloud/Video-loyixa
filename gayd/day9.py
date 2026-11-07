MEALS = [
    dict(time="08:00", name="Nonushta", kcal=300, p=12, f=6, c=50,
         items=[("Sutli grechka bo‘tqasi", "40 g grechka + 200 ml sut"), ("Meva", "100 g")],
         note="Grechka — temir va magniyga boy, sekin hazm bo‘ladi."),
    dict(time="11:00", name="Tamaddi", kcal=175, p=4, f=8, c=22,
         items=[("Olma", "1 dona (150 g)"), ("Bodom", "10–12 dona (15 g)")],
         note="Kletchatka va foydali yog‘lar — energiyani bir tekis ushlaydi."),
    dict(time="13:30", name="Tushlik", kcal=390, p=27, f=14, c=38,
         items=[("Yasmiqli sho‘rva", "1 kosa (350 ml)"), ("Mol go‘shtli salat", "150 g (go‘sht 60 g)")],
         note="O‘simlik va hayvon oqsili birga — to‘yimli tushlik."),
    dict(time="16:30", name="Tamaddi", kcal=95, p=6, f=5, c=7,
         items=[("Tabiiy yogurt", "150 g, shakarsiz")],
         note="Yengil, oqsilli tamaddi."),
    dict(time="19:00", name="Kechki ovqat", kcal=320, p=32, f=9, c=28,
         items=[("Tovuqli sabzavotli dimlama", "350 g")],
         note="Oqsil va sabzavotga boy, yengil kechki ovqat — uyqudan 3 soat oldin."),
]
PREP = [
    ("Sutli grechka", "40 g grechkani suvda yarim pishiring, 200 ml sut qo‘shib yana 5–7 daqiqa qaynating. Shakar o‘rniga meva."),
    ("Yasmiqli sho‘rva", "Yasmiqni yuvib (yashil yasmiqni 1 soat iviting), sabzi, piyoz, pomidor bilan 30–35 daqiqa qaynating."),
    ("Mol go‘shtli salat", "Qaynatilgan yog‘siz go‘sht, bodring, pomidor, ko‘kat. Mayonez o‘rniga limon va 1 choy qoshiq moy yoki yogurt."),
    ("Tovuqli dimlama", "Terisiz tovuq, sabzavot ko‘p (karam, sabzi, qalampir); moysiz, o‘z sharbatida dimlang."),
    ("Yogurt", "Tabiiy, shakarsiz turini tanlang."),
]
SHOP = [
    ("Oqsil", ["Sut — 200 ml", "Mol go‘shti (yog‘siz) — 60 g", "Tovuq (terisiz) — 120 g", "Tabiiy yogurt — 150 g"]),
    ("Sabzavot va meva", ["Olma — 1 dona", "Meva — 100 g", "Sabzi, piyoz, pomidor", "Bodring, karam, qalampir", "Ko‘katlar, limon"]),
    ("Don va boshqalar", ["Grechka — 40 g", "Yasmiq — 50 g", "Bodom — 15 g", "Zaytun moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("salat, sabzavotlar, ko‘katlar", "go‘sht, tovuq, yogurt, yasmiq", "grechka, yasmiq")
