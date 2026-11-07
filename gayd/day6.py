MEALS = [
    dict(time="08:00", name="Nonushta", kcal=275, p=21, f=18, c=7,
         items=[("Tuxum", "2 dona"), ("Pishloq, kam tuzli", "30 g"), ("Sabzavotlar (pomidor, bodring)", "150 g")],
         note="Oqsil va yog‘ga boy nonushta — uzoq vaqt to‘qlik."),
    dict(time="11:00", name="Tamaddi", kcal=175, p=4, f=8, c=22,
         items=[("Olma", "1 dona (150 g)"), ("Bodom", "10–12 dona (15 g)")],
         note="Kletchatka va foydali yog‘lar — energiyani bir tekis ushlaydi."),
    dict(time="13:30", name="Tushlik", kcal=460, p=19, f=16, c=60,
         items=[("Palov (sabzavoti ko‘p, go‘shti me’yorida)", "250 g"), ("Achchiq-chuchuk", "150 g")],
         note="Milliy taom — to‘g‘ri porsiyada parhezga ham mos."),
    dict(time="16:30", name="Tamaddi", kcal=95, p=6, f=5, c=7,
         items=[("Tabiiy yogurt", "150 g, shakarsiz")],
         note="Palovdan keyin hazmni yengillashtiradi."),
    dict(time="19:00", name="Kechki ovqat", kcal=395, p=39, f=10, c=37,
         items=[("Baliq, pechda yoki airgrilda", "150 g"), ("Sabzavotlar", "200 g"), ("Grechka, pishgan", "120 g")],
         note="Omega-3 ga boy baliq — yurak va teri uchun foydali."),
]
PREP = [
    ("Tuxum va pishloq", "Tuxumni qaynating yoki moysiz tovada pishiring. Pishloqning kam tuzli turini tanlang (brinza, adigey)."),
    ("Palov", "Porsiyada go‘sht 70–80 g, sabzi ko‘proq, moy kamroq. Ustidagi yog‘ni olib tashlang, porsiya — 250 g."),
    ("Achchiq-chuchuk", "Pomidor, piyoz va ko‘kat, moysiz — palovning og‘irligini yengillashtiradi."),
    ("Baliq", "Pechda 180°C da 20–25 daqiqa yoki airgrilda 180°C da 12–15 daqiqa. Limon va ziravor yetarli."),
    ("Grechka", "1 o‘lchov grechkaga 2 o‘lchov suv, past olovda 15–20 daqiqa."),
]
SHOP = [
    ("Oqsil", ["Tuxum — 2 dona", "Pishloq (kam tuzli) — 30 g", "Mol go‘shti — 80 g", "Baliq — 150 g", "Tabiiy yogurt — 150 g"]),
    ("Sabzavot va meva", ["Olma — 1 dona", "Pomidor, bodring", "Sabzi — 150 g", "Piyoz, sarimsoq", "Ko‘katlar, limon"]),
    ("Don va boshqalar", ["Guruch — 60 g", "Grechka — 50 g (quruq)", "Bodom — 15 g", "O‘simlik moyi"]),
]
PLATE_LABEL = "Tushlik namunasi"
PLATE = ("sabzi, achchiq-chuchuk, salat", "tuxum, go‘sht, baliq, yogurt", "guruch, grechka")
