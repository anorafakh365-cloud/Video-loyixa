MEALS = [
    dict(time="08:00", name="Nonushta", kcal=390, p=15, f=12, c=54,
         items=[("Suli bo‘tqasi (ovsyanka), sutda", "50 g suli + 200 ml sut"), ("Chia urug‘i", "1 osh qoshiq (10 g)"),
                ("Rezavor mevalar (qulupnay, malina…)", "100 g")],
         note="Sekin hazm bo‘ladigan uglevod va kletchatka — tushlikkacha to‘qlik."),
    dict(time="11:00", name="Tamaddi", kcal=150, p=4, f=8, c=16,
         items=[("Mandarin", "2 dona (150 g)"), ("Bodom", "10–12 dona (15 g)")],
         note="C vitamini va foydali yog‘lar — energiyani bir tekis ushlaydi."),
    dict(time="13:30", name="Tushlik", kcal=460, p=32, f=16, c=42,
         items=[("Tovuqli dimlama", "1 kosa (350 g)"), ("Ko‘katli salat", "150 g, 1 choy qoshiq moy")],
         note="Kunning asosiy ovqati — oqsil va sabzavotlar muvozanati."),
    dict(time="16:30", name="Tamaddi", kcal=130, p=14, f=5, c=6,
         items=[("Tabiiy grek yogurti", "150 g, shakarsiz")],
         note="Oqsilga boy tamaddi mushaklarni qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=390, p=30, f=14, c=34,
         items=[("Grechka, pishgan", "120 g"), ("Mol go‘shti, yog‘siz", "100 g"), ("Sabzavotli salat", "150 g")],
         note="Temir va oqsilga boy, yengil kechki ovqat — uyqudan 3 soat oldin."),
]
PREP = [
    ("Suli bo‘tqasi", "50 g suliga 200 ml sut quying, past olovda 5–7 daqiqa pishiring. Shakar qo‘shmang."),
    ("Chia urug‘i", "Tayyor bo‘tqaga sepib, 5 daqiqa bo‘ktiring — chia namlikni shimib, yumshoq bo‘ladi."),
    ("Tovuqli dimlama", "Terisiz tovuqdan foydalaning. Kartoshkani kamroq, karam, sabzi, qalampirni ko‘proq soling; moysiz, o‘z sharbatida dimlang."),
    ("Mol go‘shti", "Yog‘siz qismini qaynatib yoki dimlab pishiring, qovurmang. Grechka bilan birga torting."),
    ("Grek yogurti", "Tabiiy, shakarsiz turini tanlang. Shirinlik kerak bo‘lsa, bir hovuch rezavor qo‘shing."),
]
SHOP = [
    ("Oqsil", ["Tovuq (terisiz) — 120 g", "Mol go‘shti (yog‘siz) — 100 g", "Grek yogurti — 150 g", "Sut — 200 ml"]),
    ("Sabzavot va meva", ["Rezavor mevalar — 100 g", "Mandarin — 2 dona", "Karam, sabzi, kartoshka", "Pomidor, bodring", "Ko‘katlar (ukrop, kashnich)"]),
    ("Don va boshqalar", ["Suli yormasi — 50 g", "Chia urug‘i — 10 g", "Grechka — 50 g (quruq)", "Bodom — 15 g", "Zaytun moyi"]),
]
PLATE_LABEL = "Kechki ovqat namunasi"
PLATE = ("salat, ko‘katlar, rezavor mevalar", "tovuq, mol go‘shti, grek yogurti", "suli, grechka")
