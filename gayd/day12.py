MEALS = [
    dict(time="08:00", name="Nonushta", kcal=405, p=16, f=20, c=41,
         items=[("Suli bo‘tqasi", "50 g suli + 150 ml sut"), ("Chia urug‘i", "1 osh qoshiq (10 g)"), ("Yong‘oq", "5–6 dona (15 g)")],
         note="Kletchatka va omega-3 ga boy, uzoq vaqt to‘qlik."),
    dict(time="11:00", name="Tamaddi", kcal=560, p=20, f=45, c=28,
         items=[("Pista", "100 g")],
         note="Pista — oqsil va foydali yog‘lar manbai, kaloriyasi yuqori."),
    dict(time="13:30", name="Tushlik", kcal=435, p=11, f=16, c=62,
         items=[("Qovoqli manti", "3–4 dona (250 g)"), ("Yogurt", "50 g"), ("Ko‘katli salat", "150 g, 1 choy qoshiq moy")],
         note="Ko‘katli salat hamirning hazmini yengillashtiradi."),
    dict(time="16:30", name="Tamaddi", kcal=120, p=17, f=5, c=3,
         items=[("Tvorog, 5% gacha", "100 g")],
         note="Oqsilga boy tamaddi mushaklarni qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=325, p=27, f=14, c=22,
         items=[("Mol go‘shti bilan pishirilgan sabzavotlar", "350 g"), ("shundan go‘sht", "100 g")],
         note="Oqsil va sabzavotga boy kechki ovqat — uyqudan 3 soat oldin."),
]
PREP = [
    ("Suli bo‘tqasi", "50 g suliga 150 ml sut va ozroq suv, 5–7 daqiqa. Chia va yong‘oqni tayyor bo‘tqaga seping."),
    ("Qovoqli manti", "Qovoqni mayda to‘g‘rab, piyoz va ozroq dumba o‘rniga 1 choy qoshiq moy bilan. Bug‘da 35–40 daqiqa."),
    ("Ko‘katli salat", "Ukrop, kashnich, salat bargi — mantidan oldin yoki birga yeyiladi."),
    ("Go‘shtli sabzavotlar", "Yog‘siz mol go‘shti va sabzavotlarni (qalampir, baqlajon, sabzi) moysiz dimlang yoki pechda pishiring."),
    ("Pista", "Tuzlanmagan pista tanlang. Po‘chog‘i bilan 100 g taxminan 50 g mag‘iz beradi."),
]
SHOP = [
    ("Oqsil", ["Sut — 150 ml", "Tvorog (5%) — 100 g", "Mol go‘shti (yog‘siz) — 100 g", "Yogurt — 50 g"]),
    ("Sabzavot va meva", ["Qovoq — 200 g", "Piyoz, sabzi", "Bolgar qalampiri, baqlajon", "Ko‘katlar, salat bargi"]),
    ("Don va boshqalar", ["Suli yormasi — 50 g", "Chia urug‘i — 10 g", "Yong‘oq — 15 g", "Pista — 100 g", "Manti xamiri (un)"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("ko‘katli salat, qovoq, sabzavotlar", "go‘sht, tvorog, yogurt", "suli, manti xamiri")
