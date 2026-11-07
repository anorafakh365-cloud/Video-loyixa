MEALS = [
    dict(time="08:00", name="Nonushta", kcal=335, p=28, f=16, c=20,
         items=[("Tvorog, 5% gacha", "150 g"), ("Meva", "100 g"), ("Bodom", "10–12 dona (15 g)")],
         note="Tvorog — sekin hazm bo‘ladigan oqsil, uzoq vaqt to‘q tutadi."),
    dict(time="11:00", name="Tamaddi", kcal=85, p=1, f=0, c=20,
         items=[("Kivi", "2 dona (140 g)")],
         note="Kivi — C vitamini va kletchatkaga boy."),
    dict(time="13:30", name="Tushlik", kcal=450, p=23, f=14, c=58,
         items=[("Tovuqli palov", "250 g"), ("Achchiq-chuchuk", "150 g")],
         note="Tovuqli palov — mol go‘shtliga qaraganda yengilroq."),
    dict(time="16:30", name="Tamaddi", kcal=95, p=6, f=5, c=7,
         items=[("Tabiiy yogurt", "150 g, shakarsiz")],
         note="Palovdan keyin hazmni yengillashtiradi."),
    dict(time="19:00", name="Kechki ovqat", kcal=290, p=14, f=9, c=38,
         items=[("Yasmiq sho‘rvasi", "1 kosa (350 ml)"), ("Sabzavotli salat", "150 g, 1 choy qoshiq moy")],
         note="Yasmiq — o‘simlik oqsili va temir manbai, yengil kechki ovqat."),
]
PREP = [
    ("Tvorog", "Yog‘liligi 5% gacha bo‘lgan tvorogni tanlang. Bodomni maydalab seping."),
    ("Tovuqli palov", "Terisiz tovuq, sabzi ko‘proq, moy kamroq. Porsiya — 250 g, ustidagi yog‘ni oling."),
    ("Achchiq-chuchuk", "Pomidor, piyoz va ko‘kat, moysiz — palovning og‘irligini yengillashtiradi."),
    ("Yasmiq sho‘rvasi", "Qizil yasmiqni yuvib, sabzi va piyoz bilan 25–30 daqiqa qaynating. Zira va limon ta’m beradi."),
    ("Sabzavotli salat", "Bodring, pomidor, ko‘kat; 1 choy qoshiq zaytun moyi yoki limon."),
]
SHOP = [
    ("Oqsil", ["Tvorog (5%) — 150 g", "Tovuq (terisiz) — 100 g", "Tabiiy yogurt — 150 g"]),
    ("Sabzavot va meva", ["Meva — 100 g", "Kivi — 2 dona", "Sabzi — 150 g", "Pomidor, bodring, piyoz", "Ko‘katlar, limon"]),
    ("Don va boshqalar", ["Guruch — 60 g", "Qizil yasmiq — 50 g", "Bodom — 15 g", "O‘simlik moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("sabzi, achchiq-chuchuk, salat", "tvorog, tovuq, yogurt, yasmiq", "guruch, yasmiq")
