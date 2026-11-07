MEALS = [
    dict(time="08:00", name="Nonushta", kcal=335, p=27, f=17, c=19,
         items=[("Tvorog, 5% gacha", "150 g"), ("Meva", "100 g"), ("Yong‘oq", "5–6 dona (15 g)")],
         note="Tvorog — sekin hazm bo‘ladigan oqsil, uzoq vaqt to‘q tutadi."),
    dict(time="11:00", name="Tamaddi", kcal=85, p=1, f=0, c=20,
         items=[("Kivi", "2 dona (140 g)")],
         note="Kivi — C vitamini va kletchatkaga boy."),
    dict(time="13:30", name="Tushlik", kcal=400, p=25, f=13, c=46,
         items=[("Tovuqli uy kesma sho‘rva", "1 kosa (400 ml)"), ("Ko‘katli salat", "150 g, 1 choy qoshiq moy")],
         note="Ugra bezglyuten yoki 2-nav bug‘doy unidan bo‘lsa — yanada foydali."),
    dict(time="16:30", name="Tamaddi", kcal=120, p=8, f=4, c=11,
         items=[("Kefir, 1–2,5%", "1 piyola (250 ml)")],
         note="Kefir ichak mikroflorasini qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=360, p=28, f=14, c=30,
         items=[("Mol go‘shtli sabzavotli dimlama", "350 g"), ("shundan go‘sht", "100 g")],
         note="Oqsil va sabzavotga boy kechki ovqat — uyqudan 3 soat oldin."),
]
PREP = [
    ("Uy kesma (ugra)", "Bezglyuten ugra eng yaxshisi; bo‘lmasa 2-nav bug‘doy unidan tayyorlangan makaron. Porsiyaga 40 g quruq."),
    ("Tovuqli sho‘rva", "Terisiz tovuqni qaynatib, ko‘pigini oling. Sabzi, bolgar qalampiri qo‘shing; ugrani oxirida 5–7 daqiqa qaynating."),
    ("Mol go‘shtli dimlama", "Yog‘siz go‘sht, sabzavot ko‘p (karam, sabzi, qalampir, baqlajon); moysiz, o‘z sharbatida 1–1,5 soat dimlang."),
    ("Tvorog", "Yog‘liligi 5% gacha bo‘lgan tvorogni tanlang. Yong‘oqni maydalab seping."),
    ("Kivi", "Po‘stini archib yeng. Ochlik payti uchun qulay, yengil tamaddi."),
]
SHOP = [
    ("Oqsil", ["Tvorog (5%) — 150 g", "Tovuq (terisiz) — 80 g", "Mol go‘shti (yog‘siz) — 100 g", "Kefir — 250 ml"]),
    ("Sabzavot va meva", ["Kivi — 2 dona", "Meva — 100 g", "Sabzi, bolgar qalampiri", "Karam, piyoz, baqlajon", "Ko‘katlar, limon"]),
    ("Don va boshqalar", ["Ugra (bezglyuten yoki 2-nav) — 40 g", "Yong‘oq — 15 g", "Zaytun moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("sabzi, qalampir, ko‘katlar, salat", "tvorog, tovuq, go‘sht, kefir", "ugra (bezglyuten yoki 2-nav)")
