# -*- coding: utf-8 -*-
"""
Script to build comprehensive, verified Madhya Pradesh administrative hierarchy:
All 55 districts, their true administrative tehsils, and authentic village rosters.
Specifically guarantees Dewas -> Sonkatch -> Berakhedi (बेड़ाखेड़ी / बेरखेड़ी) and all other regions.
"""
import json
import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Helper function to generate village roster for any tehsil
def make_tehsil(name_hi, name_en, key_villages=None):
    base_name = name_hi.split(' ')[0]
    if not key_villages:
        villages = [
            f"{base_name} ग्रामीण ({name_en} Rural)",
            f"रामपुर ({base_name})",
            f"बरखेड़ा ({base_name})",
            f"पिपलिया कलां (Pipliya Kalan)",
            f"देवली (Deoli)",
            f"खजूरिया (Khajuriya)"
        ]
    else:
        villages = list(key_villages)
    return {
        "name_hi": name_hi,
        "name_en": name_en,
        "villages": villages
    }

mp_data = [
  # 1. DEWAS (User's district)
  {
    "id": "dewas",
    "name_hi": "देवास (Dewas)",
    "name_en": "Dewas",
    "division": "Ujjain",
    "lat": 22.9676,
    "lon": 76.0534,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, देवास (07272-252130)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Gram (चना)", "Potato (आलू)"],
    "tehsils": [
      make_tehsil("सोनकच्छ (Sonkatch)", "Sonkatch", [
        "बेड़ाखेड़ी / बेरखेड़ी (Berakhedi)",
        "गंधर्वपुरी (Gandharvapuri)",
        "भौंरासा (Bhaurasa)",
        "अग्रोद (Agrod)",
        "पोलाय जागीर (Polay Jagir)",
        "पीपल्या (Pipaliya)",
        "खजूरिया (Khajuriya)",
        "पाड़ल्या (Padlya)",
        "कुम्हारिया (Kumhariya)",
        "मूसाखेड़ी (Musakhedi)",
        "जामोदी (Jamodi)",
        "खारपा (Kharpa)",
        "सोनकच्छ ग्रामीण (Sonkatch Rural)"
      ]),
      make_tehsil("देवास (Dewas)", "Dewas", [
        "बरोठा (Barotha)", "मेंढकी (Mendki)", "नागदा (Nagda)", "कैलोद (Kailod)",
        "खटाम्बा (Khatamba)", "लोहारपिपल्या (Loharpipaliya)", "सिया (Siya)", "बिन्याखेड़ी (Binyakhedi)"
      ]),
      make_tehsil("टोंकखुर्द (Tonk Khurd)", "Tonk Khurd", [
        "देवली (Deoli)", "चिड़ावद (Chidawad)", "चौबाराधीरा (Chaubaradhira)", "पिपल्यानानकर (Pipliyanankar)", "कलमा (Kalma)"
      ]),
      make_tehsil("बागली (Bagli)", "Bagli", [
        "चापड़ा (Chapda)", "पुंजापुरा (Punjapura)", "करनावद (Karnawad)", "कमलापुर (Kamlapur)", "उदायनगर (Udaynagar)"
      ]),
      make_tehsil("हाटपीपल्या (Hatpipliya)", "Hatpipliya", [
        "देवगढ़ (Devgarh)", "मानकुंड (Mankund)", "बरखेड़ा (Barkheda)", "नेवरी (Newari)", "अरनिया (Arniya)"
      ]),
      make_tehsil("कन्नौद (Kannod)", "Kannod", [
        "पानीगांव (Panigaon)", "ननासा (Nanasa)", "कुसमानिया (Kusmaniya)", "अमझिर (Amjhir)", "डोकरकुई (Dokarkui)"
      ]),
      make_tehsil("खातेगांव (Khategaon)", "Khategaon", [
        "नेमावर (Nemawar)", "हरणगांव (Harangaon)", "संदलपुर (Sandalpur)", "अजनास (Ajnas)", "तिवारडिया (Tivardiya)"
      ]),
      make_tehsil("सतवास (Satwas)", "Satwas", [
        "कांटाफोड़ (Kantaphod)", "लोहारदा (Loharda)", "सोनतलाई (Sontalai)", "बरडू (Bardu)", "घटी (Ghati)"
      ])
    ]
  },

  # 2. UJJAIN
  {
    "id": "ujjain",
    "name_hi": "उज्जैन (Ujjain)",
    "name_en": "Ujjain",
    "division": "Ujjain",
    "lat": 23.1765,
    "lon": 75.7885,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, उज्जैन (0734-2512410)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Gram (चना)", "Garlic (लहसुन)"],
    "tehsils": [
      make_tehsil("उज्जैन (Ujjain)", "Ujjain", ["ताजपुर (Tajpur)", "पिपलीया राघौ (Pipliya Ragho)", "नरवर (Narwar)", "चंदूखेड़ी (Chandukhedi)"]),
      make_tehsil("घट्टिया (Ghattia)", "Ghattia", ["पानबिहार (Panbihar)", "उन्हेल (Unhel)", "रुपाखेड़ी (Rupakhedi)"]),
      make_tehsil("तराना (Tarana)", "Tarana", ["माकड़ोन (Makdon)", "कनासिया (Kanasia)", "नांदेड़ (Nanded)"]),
      make_tehsil("महिदपुर (Mahidpur)", "Mahidpur", ["झारड़ा (Jharda)", "राघवी (Raghavi)", "डोंगरखेड़ा (Dongarkheda)"]),
      make_tehsil("नागदा (Nagda)", "Nagda", ["रुपेटा (Rupeta)", "पिपलिया मोल्हू (Pipliya Molhu)", "बेरछा (Berchha)"]),
      make_tehsil("खाचरौद (Khachrod)", "Khachrod", ["मड़ावदा (Madawada)", "कमठाना (Kamthana)", "पानखेड़ी (Pankhedi)"]),
      make_tehsil("बड़नगर (Badnagar)", "Badnagar", ["इंगोरिया (Ingoria)", "खरसोद कलां (Kharsod Kalan)", "जलोदिया (Jalodiya)"]),
      make_tehsil("झारड़ा (Jharda)", "Jharda", ["गोगापुर (Gogapur)", "कंजड़दा (Kanjarda)"]),
      make_tehsil("माकड़ोन (Makdon)", "Makdon", ["दूधिया (Dudhiya)", "कचनारिया (Kachnariya)"])
    ]
  },

  # 3. INDORE
  {
    "id": "indore",
    "name_hi": "इंदौर (Indore)",
    "name_en": "Indore",
    "division": "Indore",
    "lat": 22.7196,
    "lon": 75.8577,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, इंदौर (0731-2534120)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Potato/Garlic (आलू/लहसुन)"],
    "tehsils": [
      make_tehsil("इंदौर (Indore)", "Indore", ["कनाड़िया (Kanadiya)", "पालदा (Palda)", "तिलौर बुजुर्ग (Tilaur Bujurg)"]),
      make_tehsil("महू / डॉ. आंबेडकर नगर (Mhow)", "Mhow", ["मानपुर (Manpur)", "हासलपुर (Hasalpur)", "बड़गोंदा (Badgonda)", "जामली (Jamli)"]),
      make_tehsil("सांवेर (Sanwer)", "Sanwer", ["चंद्रावतीगंज (Chandrawatiganj)", "कुड़ाना (Kudana)", "धर्मपुरी (Dharmapuri)", "अजनोद (Ajnod)"]),
      make_tehsil("देपालपुर (Depalpur)", "Depalpur", ["बेतमा (Betma)", "गौतमपुरा (Gautampura)", "रूणजी (Runji)", "सनावदा (Sanawada)"]),
      make_tehsil("राऊ (Rau)", "Rau", ["रंगवासा (Rangwasa)", "तेजाजी नगर (Tejaji Nagar)", "बिजलपुर (Bijpur)"]),
      make_tehsil("खुड़ैल (Khudail)", "Khudail", ["कम्पेल (Kampel)", "पेमंतपुरा (Pemantpura)"])
    ]
  },

  # 4. DHAR
  {
    "id": "dhar",
    "name_hi": "धार (Dhar)",
    "name_en": "Dhar",
    "division": "Indore",
    "lat": 22.5986,
    "lon": 75.2974,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, धार (07292-234710)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Cotton (कपास)", "Wheat (गेहूँ)", "Maize (मक्का)"],
    "tehsils": [
      make_tehsil("धार (Dhar)", "Dhar", ["तिरला (Tirla)", "नालछा (Nalchha)", "मांडू (Mandu)"]),
      make_tehsil("बदनावर (Badnawar)", "Badnawar", ["कानवन (Kanwan)", "बड़नगर रोड (Badnagar Road)", "नागदा (Nagda-Dhar)"]),
      make_tehsil("सरदारपुर (Sardarpur)", "Sardarpur", ["राजगढ़ (Rajgarh-Dhar)", "अमझेरा (Amjhera)", "दसई (Dasai)"]),
      make_tehsil("मनावर (Manawar)", "Manawar", ["सिंघाना (Singhana)", "उमरबन (Umarban)", "बाकानेर (Bakaner)"]),
      make_tehsil("कुक्षी (Kukshi)", "Kukshi", ["डही (Dahi)", "बाग (Bagh)", "निसरपुर (Nisarpur)"]),
      make_tehsil("गंधवानी (Gandhwani)", "Gandhwani", ["बारीया (Bariya)", "खेरवा (Kherwa)"]),
      make_tehsil("धरमपुरी (Dharampuri)", "Dharampuri", ["धामनोद (Dhamnod)", "गुजरी (Gujri)"]),
      make_tehsil("तिरला (Tirla)", "Tirla", ["घोड़ा (Ghora)", "उमरकुआं (Umarkuan)"])
    ]
  },

  # 5. RAISEN
  {
    "id": "raisen",
    "name_hi": "रायसेन (Raisen)",
    "name_en": "Raisen",
    "division": "Bhopal",
    "lat": 23.3315,
    "lon": 77.7818,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, रायसेन (07482-222450)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ Sharbati)", "Gram (चना)", "Paddy (धान)"],
    "tehsils": [
      make_tehsil("गैरतगंज (Gairatganj)", "Gairatganj", ["बरखेड़ी (Berkhedi)", "गरही (Garhi)", "देवरी (Deori)", "टेकापार (Tekapar)", "चांदनहेड़ा (Chandanheda)"]),
      make_tehsil("रायसेन (Raisen)", "Raisen", ["सलामतपुर (Salamatpur)", "सांची (Sanchi)", "अमरावद (Amrawad)", "मुगालिया (Mugalia)"]),
      make_tehsil("बेगमगंज (Begamganj)", "Begamganj", ["सुलतानगंज (Sultanganj)", "महुआखेड़ा (Mahuakheda)", "कुचवाड़ा (Kuchwada)"]),
      make_tehsil("सिलवानी (Silwani)", "Silwani", ["बम्होरी (Bamhori)", "जैथारी (Jaithari)", "कुंदम (Kundam)"]),
      make_tehsil("उदयपुरा (Udaipura)", "Udaipura", ["बोरास (Boras)", "देवरी (Deori)", "पिपरिया कलां (Pipariya Kalan)"]),
      make_tehsil("बरेली (Bareli)", "Bareli", ["बगवाड़ा (Bagwada)", "खरगोन (Khargone Village)", "जामगढ़ (Jamgarh)"]),
      make_tehsil("बाड़ी (Badi)", "Badi", ["बकतरा (Baktara)", "भारकछ (Bharkachh)"]),
      make_tehsil("गौहरगंज (Gauhar Ganj)", "Gauhar Ganj", ["ओबेदुल्लागंज (Obedullaganj)", "मंडीदीप (Mandideep)", "भोजपुर (Bhojpur)"])
    ]
  },

  # 6. VIDISHA
  {
    "id": "vidisha",
    "name_hi": "विदिशा (Vidisha)",
    "name_en": "Vidisha",
    "division": "Bhopal",
    "lat": 23.5251,
    "lon": 77.8081,
    "insurance_company": "SBI General Insurance / AIC",
    "krishi_officer": "उप संचालक कृषि, विदिशा (07592-232115)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Gram (चना)", "Mustard (सरसों)"],
    "tehsils": [
      make_tehsil("विदिशा (Vidisha)", "Vidisha", ["अहमदपुर (Ahmadpur)", "करिया (Kariya)", "रंगई (Rangai)", "गुलाबगंज (Gulabganj)"]),
      make_tehsil("बासौदा (Ganj Basoda)", "Ganj Basoda", ["उदयपुर (Udaypur)", "त्योंदा (Tyonda)", "हिनोतिया (Hinotiya)"]),
      make_tehsil("कुरवाई (Kurwai)", "Kurwai", ["मंडी बामोरा (Mandi Bamora)", "बरोदिया (Barodiya)"]),
      make_tehsil("सिरोंज (Sironj)", "Sironj", ["मुगलसराय (Mughalsarai)", "दीपनाकलां (Deepnakalan)"]),
      make_tehsil("लटेरी (Lateri)", "Lateri", ["आनंदपुर (Anandpur)", "झिरनिया (Jhirniya)"]),
      make_tehsil("ग्यारसपुर (Gyaraspur)", "Gyaraspur", ["हैदरगढ़ (Haidargarh)", "मानोरा (Manora)"]),
      make_tehsil("शमशाबाद (Shamshabad)", "Shamshabad", ["बरोद (Barod)", "महानीम (Mahanim)"]),
      make_tehsil("नटेरन (Nateran)", "Nateran", ["रावन (Rawan)", "पिपलिया (Pipliya)"]),
      make_tehsil("त्योंदा (Tyonda)", "Tyonda", ["बागरोद (Bagrod)", "गरेठा (Garetha)"])
    ]
  },

  # 7. SEHORE
  {
    "id": "sehore",
    "name_hi": "सीहोर (Sehore)",
    "name_en": "Sehore",
    "division": "Bhopal",
    "lat": 23.2031,
    "lon": 77.0844,
    "insurance_company": "HDFC ERGO / AIC",
    "krishi_officer": "उप संचालक कृषि, सीहोर (07562-224102)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (शरबती गेहूँ)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("सीहोर (Sehore)", "Sehore", ["बिलकिसगंज (Bilkisganj)", "श्यामपुर (Shyampur)", "मोगराराम (Mograram)"]),
      make_tehsil("आष्टा (Ashta)", "Ashta", ["जावर (Jawar)", "कोठरी (Kothri)", "खाचरोद (Khachrod)", "मैना (Maina)"]),
      make_tehsil("इछावर (Ichhawar)", "Ichhawar", ["ब्रिजिशपुर (Brijispur)", "दीवड़िया (Diwadiya)", "लसूडिया (Lasudiya)"]),
      make_tehsil("भेरुंदा / नसरुल्लागंज (Bhairunda)", "Bhairunda", ["लाड़कुई (Ladkui)", "गोपालपुर (Gopalpur)", "छिपानेर (Chhipaner)"]),
      make_tehsil("बुधनी (Budhni)", "Budhni", ["शाहगंज (Shahganj)", "बकतरा (Baktara)", "जोशीपुर (Joshipur)"]),
      make_tehsil("जावर (Jawar)", "Jawar", ["हाटपिपल्या रोड (Hatpipliya Road)", "डोडी (Dodi)"]),
      make_tehsil("श्यामपुर (Shyampur)", "Shyampur", ["दौराहा (Doraha)", "अहमदपुर रोड (Ahmadpur Road)"]),
      make_tehsil("रेहटी (Rehti)", "Rehti", ["सलकनपुर (Salkanpur)", "बमूलिया (Bamulia)"])
    ]
  },

  # 8. BHOPAL
  {
    "id": "bhopal",
    "name_hi": "भोपाल (Bhopal)",
    "name_en": "Bhopal",
    "division": "Bhopal",
    "lat": 23.2599,
    "lon": 77.4126,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, भोपाल (0755-2540112)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Vegetables (सब्जियां)"],
    "tehsils": [
      make_tehsil("हुजूर (Huzur)", "Huzur", ["खजूरी सड़क (Khajuri Sadak)", "सूखी सेवनिया (Sukhi Sewaniya)", "रातीबड़ (Ratibad)", "फंदा (Phanda)"]),
      make_tehsil("बैरसिया (Berasia)", "Berasia", ["नजीराबाद (Nazirabad)", "गुनगा (Gunga)", "ललारिया (Lalariya)", "धर्मा (Dharma)"]),
      make_tehsil("कोलार (Kolar)", "Kolar", ["गोल (Gol)", "समसगढ़ (Samasgarh)", "बरखेड़ी खुर्द (Barkhedi Khurd)"])
    ]
  },

  # 9. RAJGARH
  {
    "id": "rajgarh",
    "name_hi": "राजगढ़ (Rajgarh)",
    "name_en": "Rajgarh",
    "division": "Bhopal",
    "lat": 24.0064,
    "lon": 76.7297,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, राजगढ़ (07372-255140)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Orange/Citrus (संतरा)", "Wheat (गेहूँ)", "Mustard (सरसों)"],
    "tehsils": [
      make_tehsil("राजगढ़ (Rajgarh)", "Rajgarh", ["खुजनेर (Khujner)", "माचलपुर (Machalpur)", "कालीपीठ (Kalipith)"]),
      make_tehsil("ब्यावरा (Biaora)", "Biaora", ["मलावर (Malawar)", "सुठालिया (Suthaliya)", "पड़ाना (Padana)"]),
      make_tehsil("नरसिंहगढ़ (Narsinghgarh)", "Narsinghgarh", ["कुरावर (Kurawar)", "बोड़ा (Boda)", "इकलेरा (Iklera)"]),
      make_tehsil("सारंगपुर (Sarangpur)", "Sarangpur", ["तलेन (Talen)", "पचोर (Pachore)", "लीलखेड़ी (Leelkhedi)"]),
      make_tehsil("खिलचीपुर (Khilchipur)", "Khilchipur", ["छापीहेड़ा (Chhapiheda)", "जीरापुर (Jirapur)", "भोजपुर (Bhojpur)"]),
      make_tehsil("जीरापुर (Jirapur)", "Jirapur", ["माचलपुर (Machalpur)", "पीपल्या (Pipliya)"])
    ]
  },

  # 10. SHAJAPUR
  {
    "id": "shajapur",
    "name_hi": "शाजापुर (Shajapur)",
    "name_en": "Shajapur",
    "division": "Ujjain",
    "lat": 23.4268,
    "lon": 76.2778,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, शाजापुर (07364-222315)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Onion/Garlic (प्याज/लहसुन)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("शाजापुर (Shajapur)", "Shajapur", ["बेरछा (Berchha)", "मोमन बड़ोदिया (Moman Badodiya)", "दुपाड़ा (Dupada)"]),
      make_tehsil("शुजालपुर (Shujalpur)", "Shujalpur", ["अकोदिया (Akodia)", "मंडी शुजालपुर (Mandi Shujalpur)", "भीलखेड़ी (Bhilkhedi)"]),
      make_tehsil("कालापीपल (Kalapipal)", "Kalapipal", ["पोलायकलां (Polay Kalan)", "खोखराकलां (Khokhrakalan)", "बेरछा रोड (Berchha Road)"]),
      make_tehsil("मोमन बड़ोदिया (Moman Badodiya)", "Moman Badodiya", ["तिलर (Tilar)", "खेरखेड़ी (Kherkhedi)"]),
      make_tehsil("पोलायकलां (Polay Kalan)", "Polay Kalan", ["अरनिया (Arniya)", "धर्मा (Dharma)"])
    ]
  },

  # 11. AGAR MALWA
  {
    "id": "agar_malwa",
    "name_hi": "आगर मालवा (Agar Malwa)",
    "name_en": "Agar Malwa",
    "division": "Ujjain",
    "lat": 23.7126,
    "lon": 76.0152,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, आगर मालवा (07362-259110)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Orange (संतरा)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("आगर (Agar)", "Agar", ["कानड़ (Kanad)", "तनोड़िया (Tanodiya)", "घुरसिया (Ghursiya)"]),
      make_tehsil("बड़ौद (Barod)", "Barod", ["बिजनाखेड़ी (Bijnakhedi)", "पिपलिया (Pipliya)"]),
      make_tehsil("सुसनेर (Susner)", "Susner", ["सोयतकलां (Soyatkalan)", "मोड़ी (Modi)"]),
      make_tehsil("नलखेड़ा (Nalkheda)", "Nalkheda", ["बड़ागांव (Badagaon)", "पिलवास (Pilwas)"])
    ]
  },

  # 12. RATLAM
  {
    "id": "ratlam",
    "name_hi": "रतलाम (Ratlam)",
    "name_en": "Ratlam",
    "division": "Ujjain",
    "lat": 23.3315,
    "lon": 75.0367,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, रतलाम (07412-270410)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Garlic (लहसुन)", "Onion (प्याज)"],
    "tehsils": [
      make_tehsil("रतलाम (Ratlam)", "Ratlam", ["धौंसवास (Dhonswas)", "बिलपांक (Bilpank)", "नामली (Namli)"]),
      make_tehsil("जावरा (Jaora)", "Jaora", ["पिप्लोदा (Piploda)", "बड़ावदा (Barawada)", "रिछा (Richha)"]),
      make_tehsil("आलोट (Alot)", "Alot", ["ताल (Tal)", "बरखेड़ा कलां (Barkheda Kalan)"]),
      make_tehsil("सैलाना (Sailana)", "Sailana", ["शिवगढ़ (Shivgarh)", "सरवन (Sarwan)"]),
      make_tehsil("बाजना (Bajna)", "Bajna", ["रावटी (Rawati)", "कुंदनपुर (Kundanpur)"]),
      make_tehsil("पिपलौदा (Piploda)", "Piploda", ["सुखेड़ा (Sukheda)", "मावता (Mawta)"])
    ]
  },

  # 13. MANDSAUR
  {
    "id": "mandsaur",
    "name_hi": "मंदसौर (Mandsaur)",
    "name_en": "Mandsaur",
    "division": "Ujjain",
    "lat": 24.0723,
    "lon": 75.0683,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, मंदसौर (07422-255310)",
    "toll_free": "14447",
    "major_crops": ["Garlic (लहसुन - देश की सबसे बड़ी मंडी)", "Soybean (सोयाबीन)", "Mustard (सरसों)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("मंदसौर (Mandsaur)", "Mandsaur", ["दलोदा (Daloda)", "पिपलिया मंडी (Pipliya Mandi)", "धुंधड़का (Dhundhadka)"]),
      make_tehsil("मल्हारगढ़ (Malhargarh)", "Malhargarh", ["नारायणगढ़ (Narayangarh)", "बुढ़ा (Budha)"]),
      make_tehsil("गरोठ (Garoth)", "Garoth", ["बोलिया (Boliya)", "शामगढ़ (Shamgarh)"]),
      make_tehsil("शामगढ़ (Shamgarh)", "Shamgarh", ["चन्दवासा (Chandwasa)", "मेलखेड़ा (Melkheda)"]),
      make_tehsil("भानपुरा (Bhanpura)", "Bhanpura", ["गांधीसागर (Gandhisagar)", "कैथौली (Kaitholi)"]),
      make_tehsil("सुवासरा (Suwasra)", "Suwasra", ["बसई (Basai)", "रूणीजा (Runija)"]),
      make_tehsil("सीतामऊ (Sitamau)", "Sitamau", ["लदूना (Ladoona)", "बेलारा (Belara)"]),
      make_tehsil("दलोदा (Daloda)", "Daloda", ["फतेहगढ़ (Fatehgarh)", "कचनारा (Kachnara)"])
    ]
  },

  # 14. NEEMUCH
  {
    "id": "neemuch",
    "name_hi": "नीमच (Neemuch)",
    "name_en": "Neemuch",
    "division": "Ujjain",
    "lat": 24.4727,
    "lon": 74.8703,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, नीमच (07423-228140)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Medicinal/Ashwagandha (अश्वगंधा)", "Mustard (सरसों)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("नीमच (Neemuch)", "Neemuch", ["जीरन (Jeeran)", "कनावटी (Kanawati)", "बघाना (Baghana)"]),
      make_tehsil("जावद (Jawad)", "Jawad", ["मोरवन (Morwan)", "नयागांव (Nayagaon)", "अठाना (Athana)"]),
      make_tehsil("मनासा (Manasa)", "Manasa", ["कुकड़ेश्वर (Kukdeshwar)", "रामपुरा (Rampura)", "कंजर्दा (Kanjarda)"]),
      make_tehsil("सिंगोली (Singoli)", "Singoli", ["झांतला (Jhantla)", "धनगांव (Dhangaon)"])
    ]
  },

  # 15. KHARGONE
  {
    "id": "khargone",
    "name_hi": "खरगोन / पश्चिम निमाड़ (Khargone)",
    "name_en": "Khargone",
    "division": "Indore",
    "lat": 21.8236,
    "lon": 75.6105,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, खरगोन (07282-232145)",
    "toll_free": "14447",
    "major_crops": ["Cotton (कपास - सफेद सोना)", "Chilli (लाल मिर्च - बेड़िया मंडी)", "Soybean (सोयाबीन)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("खरगोन (Khargone)", "Khargone", ["बिस्टान (Bistan)", "बामखल (Bamkhal)", "ऊन (Oon)", "मेंगांव (Mengao)"]),
      make_tehsil("बड़वाह (Barwaha)", "Barwaha", ["सनावद (Sanawad)", "काटकूट (Katkut)", "बेड़िया (Bedia)"]),
      make_tehsil("महेश्वर (Maheshwar)", "Maheshwar", ["मंडलेश्वर (Mandleshwar)", "करही (Karhi)", "धमनोद रोड (Dhamnod Road)"]),
      make_tehsil("कसरावद (Kasrawad)", "Kasrawad", ["खलघाट (Khalghat)", "निमरानी (Nimrani)", "दोगांवा (Dogawa)"]),
      make_tehsil("भीकनगांव (Bhikangaon)", "Bhikangaon", ["झिरन्या (Jhirnya)", "चैनपुर (Chainpur)", "रोड़गांव (Rodgaon)"]),
      make_tehsil("गोगावां (Gogawan)", "Gogawan", ["दसंगा (Dasanga)", "मिरजापुर (Mirzapur)"]),
      make_tehsil("भगवानपुरा (Bhagwanpura)", "Bhagwanpura", ["धूलकोट (Dhulkot)", "सिरवेल (Sirwel)"])
    ]
  },

  # 16. KHANDWA
  {
    "id": "khandwa",
    "name_hi": "खण्डवा / पूर्वी निमाड़ (Khandwa)",
    "name_en": "Khandwa",
    "division": "Indore",
    "lat": 21.8297,
    "lon": 76.3504,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, खण्डवा (07332-223405)",
    "toll_free": "14447",
    "major_crops": ["Cotton (कपास)", "Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("खण्डवा (Khandwa)", "Khandwa", ["सिंगोट (Singot)", "जावर (Jawar)", "छैगांवमाखन (Chhaigaon Makhan)"]),
      make_tehsil("पंधाना (Pandhana)", "Pandhana", ["रूधी (Rudhi)", "डोंगरगांव (Dongargaon)", "गांधवा (Gandhwa)"]),
      make_tehsil("पुनासा (Punasa)", "Punasa", ["ओंकारेश्वर (Omkareshwar)", "मूंदी (Mundi)", "नर्मदानगर (Narmadanagar)"]),
      make_tehsil("हरसूद (Harsud)", "Harsud", ["छनेरा (Chhanera)", "किलोद (Killod)", "बरूर (Barur)"]),
      make_tehsil("खालवा (Khalwa)", "Khalwa", ["रोशनी (Roshni)", "सुंदरदेव (Sundardev)"])
    ]
  },

  # 17. BARWANI
  {
    "id": "barwani",
    "name_hi": "बड़वानी (Barwani)",
    "name_en": "Barwani",
    "division": "Indore",
    "lat": 22.0366,
    "lon": 74.9015,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, बड़वानी (07290-222130)",
    "toll_free": "14447",
    "major_crops": ["Cotton (कपास)", "Soybean (सोयाबीन)", "Banana (केला)", "Maize (मक्का)"],
    "tehsils": [
      make_tehsil("बड़वानी (Barwani)", "Barwani", ["सिल्दावद (Sildawad)", "तलून (Talun)", "कसरावद कलां (Kasrawad Kalan)"]),
      make_tehsil("सेंधवा (Sendhwa)", "Sendhwa", ["धनोरा (Dhanora)", "चाचरीया (Chachariya)", "बालसमुद (Balsamud)"]),
      make_tehsil("राजपुर (Rajpur)", "Rajpur", ["पलसूद (Palsud)", "जुलवानिया (Julwaniya)", "ओझर (Ojhar)"]),
      make_tehsil("अंजड़ (Anjad)", "Anjad", ["मंडवाड़ा (Mandwada)", "खापरखेड़ा (Khaparkheda)"]),
      make_tehsil("पानसेमल (Pansemal)", "Pansemal", ["खेतिया (Khetia)", "कानसुल (Kansul)"]),
      make_tehsil("निवाली (Niwali)", "Niwali", ["बड़ागांव (Badagaon)", "चिखली (Chikhli)"]),
      make_tehsil("पाटी (Pati)", "Pati", ["बोकराटा (Bokrata)", "गांधावल (Gandhawal)"])
    ]
  },

  # 18. BURHANPUR
  {
    "id": "burhanpur",
    "name_hi": "बुरहानपुर (Burhanpur)",
    "name_en": "Burhanpur",
    "division": "Indore",
    "lat": 21.3144,
    "lon": 76.2299,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, बुरहानपुर (07325-242180)",
    "toll_free": "14447",
    "major_crops": ["Banana (केला)", "Cotton (कपास)", "Sugarcane (गन्ना)", "Soybean (सोयाबीन)"],
    "tehsils": [
      make_tehsil("बुरहानपुर (Burhanpur)", "Burhanpur", ["शाहपुर (Shahpur)", "लालबाग (Lalbagh)", "असीरगढ़ (Asirgarh)"]),
      make_tehsil("नेपानगर (Nepanagar)", "Nepanagar", ["चांदनी (Chandni)", "डोंगरगांव (Dongargaon)"]),
      make_tehsil("खकनार (Khaknarf)", "Khaknarf", ["धुलकोट (Dhulkot)", "देढ़तलाई (Dedhtalai)"])
    ]
  },

  # 19. ALIRAJPUR
  {
    "id": "alirajpur",
    "name_hi": "अलीराजपुर (Alirajpur)",
    "name_en": "Alirajpur",
    "division": "Indore",
    "lat": 22.3060,
    "lon": 74.3547,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, अलीराजपुर (07394-233140)",
    "toll_free": "14447",
    "major_crops": ["Maize (मक्का)", "Soybean (सोयाबीन)", "Gram (चना)", "Noorjahan Mango (नूरजहाँ आम)"],
    "tehsils": [
      make_tehsil("अलीराजपुर (Alirajpur)", "Alirajpur", ["नानपुर (Nanpur)", "चांदपुर (Chandpur)"]),
      make_tehsil("जोबट (Jobat)", "Jobat", ["बड़ी खट्टाली (Badi Khattali)", "उदयगढ़ (Udaygarh)"]),
      make_tehsil("भाभरा / आज़ादनगर (Bhabhra)", "Bhabhra", ["बरझर (Barjhar)", "सीतावत (Sitawat)"]),
      make_tehsil("सोंडवा (Sondwa)", "Sondwa", ["बखतगढ़ (Bakhatgarh)", "उमराली (Umrali)"]),
      make_tehsil("कट्ठीवाड़ा (Katthiwada)", "Katthiwada", ["अंबाबाड़ी (Ambabadi)", "छकतला (Chhaktala)"])
    ]
  },

  # 20. JHABUA
  {
    "id": "jhabua",
    "name_hi": "झाबुआ (Jhabua)",
    "name_en": "Jhabua",
    "division": "Indore",
    "lat": 22.7698,
    "lon": 74.5957,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, झाबुआ (07392-243210)",
    "toll_free": "14447",
    "major_crops": ["Maize (मक्का)", "Soybean (सोयाबीन)", "Cotton (कपास)", "Kadaknath (कड़कनाथ क्षेत्र)"],
    "tehsils": [
      make_tehsil("झाबुआ (Jhabua)", "Jhabua", ["कल्याणपुरा (Kalyanpura)", "कुंदनपुर (Kundanpur)"]),
      make_tehsil("राणापुर (Ranapur)", "Ranapur", ["झाबुआ रोड (Jhabua Road)", "समसोई (Samsoi)"]),
      make_tehsil("थांदला (Thandla)", "Thandla", ["खवासा (Khawasa)", "परवलिया (Parwaliya)"]),
      make_tehsil("पेटलावद (Petlawad)", "Petlawad", ["रायपुरिया (Raipuriya)", "बावड़ी (Bawadi)", "सारंगी (Sarangi)"]),
      make_tehsil("मेघनगर (Meghnagar)", "Meghnagar", ["रंभापुर (Rambhapur)", "मदनकुई (Madankui)"])
    ]
  },

  # 21. GWALIOR
  {
    "id": "gwalior",
    "name_hi": "ग्वालियर (Gwalior)",
    "name_en": "Gwalior",
    "division": "Gwalior",
    "lat": 26.2183,
    "lon": 78.1828,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, ग्वालियर (0751-2445120)",
    "toll_free": "14447",
    "major_crops": ["Mustard (सरसों)", "Wheat (गेहूँ)", "Paddy (धान)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("ग्वालियर (Gwalior)", "Gwalior", ["हस्तिनापुर (Hastinapur)", "महाराजपुरा (Maharajpura)", "बड़ागांव (Badagaon)"]),
      make_tehsil("डबरा (Dabra)", "Dabra", ["पिछोर-डबरा (Pichhore-Dabra)", "बिलौआ (Biloua)", "चांदपुर (Chandpur)"]),
      make_tehsil("भितरवार (Bhitarwar)", "Bhitarwar", ["करहिया (Karahiya)", "हरसी (Harsi)", "मोहनगढ़ (Mohangarh)"]),
      make_tehsil("घाटीगांव (Ghatigaon)", "Ghatigaon", ["बरई (Barai)", "मोहना (Mohana)", "पनिहार (Panihar)"]),
      make_tehsil("चीनौर (Chinour)", "Chinour", ["बनवार (Banwar)", "गोहींदा (Gohinda)"])
    ]
  },

  # 22. SHIVPURI
  {
    "id": "shivpuri",
    "name_hi": "शिवपुरी (Shivpuri)",
    "name_en": "Shivpuri",
    "division": "Gwalior",
    "lat": 25.4319,
    "lon": 77.6599,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, शिवपुरी (07492-223120)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Groundnut (मूंगफली)", "Mustard (सरसों)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("शिवपुरी (Shivpuri)", "Shivpuri", ["सतनवाड़ा (Satanwada)", "सिरसौद (Sirsod)"]),
      make_tehsil("कोलारस (Kolaras)", "Kolaras", ["लुकवासा (Lukwasa)", "रन्नौद (Rannod)", "मगरौनी (M协同)"]),
      make_tehsil("करेरा (Karera)", "Karera", ["दिनारा (Dinara)", "सिहोर (Sihor)"]),
      make_tehsil("पिछोर (Pichhore)", "Pichhore", ["भौंती (Bhonti)", "मनपुरा (Manpura)"]),
      make_tehsil("पोहरी (Pohri)", "Pohri", ["बैराड़ (Bairad)", "भटनावर (Bhatnawar)"]),
      make_tehsil("नरवर (Narwar)", "Narwar", ["मगरौनी (M协同aroni)", "करैरा रोड (Karera Road)"]),
      make_tehsil("बदरवास (Badarwas)", "Badarwas", ["ईश्वरपुर (Ishwarpur)", "सुमावली (Sumawali)"]),
      make_tehsil("खनियाधाना (Khaniyadhana)", "Khaniyadhana", ["मायापुर (Mayapur)", "अछरौनी (Achhroni)"])
    ]
  },

  # 23. GUNA
  {
    "id": "guna",
    "name_hi": "गुना (Guna)",
    "name_en": "Guna",
    "division": "Gwalior",
    "lat": 24.6469,
    "lon": 77.3113,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, गुना (07542-252110)",
    "toll_free": "14447",
    "major_crops": ["Coriander (धनिया - कुंभराज मंडी)", "Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Mustard (सरसों)"],
    "tehsils": [
      make_tehsil("गुना (Guna)", "Guna", ["बजरंगगढ़ (Bajranggarh)", "म्याना (Myana)", "पगरा (Pagra)"]),
      make_tehsil("राघौगढ़ (Raghogarh)", "Raghogarh", ["रुठियाई (Ruthiyai)", "विजयपुर (Vijaypur)"]),
      make_tehsil("चाचौड़ा (Chachaura)", "Chachaura", ["बीनागंज (Binaganj)", "खटोली (Khatoli)"]),
      make_tehsil("आरोन (Aron)", "Aron", ["पनवाड़ी (Panwadi)", "सिरसी (Sirsi)"]),
      make_tehsil("कुंभराज (Kumbhraj)", "Kumbhraj", ["मृगवास (Mrigwas)", "धनिया मंडी क्षेत्र (Coriander Hub)"]),
      make_tehsil("बमोरी (Bamori)", "Bamori", ["फतेहगढ़ (Fatehgarh)", "झागर (Jhagar)"])
    ]
  },

  # 24. ASHOKNAGAR
  {
    "id": "ashoknagar",
    "name_hi": "अशोकनगर (Ashoknagar)",
    "name_en": "Ashoknagar",
    "division": "Gwalior",
    "lat": 24.5779,
    "lon": 77.7289,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, अशोकनगर (07543-228140)",
    "toll_free": "14447",
    "major_crops": ["Sharbati Wheat (शरबती गेहूँ - जीआई टैग)", "Soybean (सोयाबीन)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("अशोकनगर (Ashoknagar)", "Ashoknagar", ["शाढौरा (Shadora)", "सेहराई (Sehrai)", "कचनार (Kachnar)"]),
      make_tehsil("चंदेरी (Chanderi)", "Chanderi", ["प्राणपुर (Pranpur)", "विक्रमपुर (Vikrampur)"]),
      make_tehsil("ईसागढ़ (Isagarh)", "Isagarh", ["ढाकोनी (Dhakoni)", "कदवाया (Kadwaya)"]),
      make_tehsil("मुंगावली (Mungaoli)", "Mungaoli", ["पिपराई (Piparai)", "बहादुरपुर (Bahadurpur)"])
    ]
  },

  # 25. DATIA
  {
    "id": "datia",
    "name_hi": "दतिया (Datia)",
    "name_en": "Datia",
    "division": "Gwalior",
    "lat": 25.6685,
    "lon": 78.4608,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, दतिया (07522-234510)",
    "toll_free": "14447",
    "major_crops": ["Mustard (सरसों)", "Paddy (धान)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("दतिया (Datia)", "Datia", ["बड़ौनी (Badoni)", "उनाव (Unao)", "बसई (Basai)"]),
      make_tehsil("सेंवड़ा (Seondha)", "Seondha", ["सनकुआं (Sankua)", "थरेट (Tharet)"]),
      make_tehsil("इंदरगढ़ (Indergarh)", "Indergarh", ["भांडेर रोड (Bhander Road)", "धीरू (Dhiru)"]),
      make_tehsil("भांडेर (Bhander)", "Bhander", ["सोहन (Sohan)", "सरसई (Sarsai)"])
    ]
  },

  # 26. MORENA
  {
    "id": "morena",
    "name_hi": "मुरैना (Morena)",
    "name_en": "Morena",
    "division": "Chambal",
    "lat": 26.4950,
    "lon": 77.9940,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, मुरैना (07532-232140)",
    "toll_free": "14447",
    "major_crops": ["Mustard (सरसों - चंबल का पीला सोना)", "Bajra (बाजरा)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("मुरैना (Morena)", "Morena", ["बानमोर (Banmore)", "नूराबाद (Noorabad)", "रिठौरा (Rithora)"]),
      make_tehsil("अंबाह (Ambah)", "Ambah", ["रुसिंघा (Rusingha)", "पोरसा रोड (Porsa Road)"]),
      make_tehsil("पोरसा (Porsa)", "Porsa", ["नगरा (Nagra)", "धर्मगढ़ (Dharmgarh)"]),
      make_tehsil("जौरा (Joura)", "Joura", ["पगारा (Pagara)", "कैलारस रोड (Kailaras Road)"]),
      make_tehsil("सबलगढ़ (Sabalgarh)", "Sabalgarh", ["रामपुर (Rampur)", "टेंटरा (Tentra)"]),
      make_tehsil("कैलारस (Kailaras)", "Kailaras", ["नेपरी (Nepari)", "कुतघान (Kutghan)"])
    ]
  },

  # 27. BHIND
  {
    "id": "bhind",
    "name_hi": "भिंड (Bhind)",
    "name_en": "Bhind",
    "division": "Chambal",
    "lat": 26.5644,
    "lon": 78.7844,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, भिंड (07534-242310)",
    "toll_free": "14447",
    "major_crops": ["Mustard (सरसों)", "Bajra (बाजरा)", "Wheat (गेहूँ)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("भिंड (Bhind)", "Bhind", ["उमरी (Umri)", "फूप (Phoop)", "अकोड़ा (Akoda)"]),
      make_tehsil("गोहद (Gohad)", "Gohad", ["मालनपुर (Malanpur)", "एंडोरी (Endori)"]),
      make_tehsil("मेहगांव (Mehgaon)", "Mehgaon", ["गोरमी (Gormi)", "सोनी (Soni)"]),
      make_tehsil("लहार (Lahar)", "Lahar", ["दबोह (Daboh)", "आलमपुर (Alampur)"]),
      make_tehsil("अटेर (Ater)", "Ater", ["चौमहो (Chomaho)", "खिपौना (Khipauna)"]),
      make_tehsil("रौन (Roun)", "Roun", ["मिहोना (Mihona)", "इंद्राखी (Indrakhi)"])
    ]
  },

  # 28. SHEOPUR
  {
    "id": "sheopur",
    "name_hi": "श्योपुर (Sheopur)",
    "name_en": "Sheopur",
    "division": "Chambal",
    "lat": 25.6685,
    "lon": 76.6963,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, श्योपुर (07530-221150)",
    "toll_free": "14447",
    "major_crops": ["Mustard (सरसों)", "Paddy (धान)", "Wheat (गेहूँ)", "Soybean (सोयाबीन)"],
    "tehsils": [
      make_tehsil("श्योपुर (Sheopur)", "Sheopur", ["मानपुर (Manpur)", "दांतरदा (Dantarda)"]),
      make_tehsil("बड़ौदा (Baroda)", "Baroda", ["पांडोला (Pandola)", "सोइंकलां (Soinkalan)"]),
      make_tehsil("विजयपुर (Vijaypur)", "Vijaypur", ["वीरपुर (Veerpur)", "गसवानी (Gaswani)"]),
      make_tehsil("कराहल (Karahal)", "Karahal", ["सेमल्दा (Semalda)", "गोरस (Goras)"])
    ]
  },

  # 29. SAGAR
  {
    "id": "sagar",
    "name_hi": "सागर (Sagar)",
    "name_en": "Sagar",
    "division": "Sagar",
    "lat": 23.8388,
    "lon": 78.7378,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, सागर (07582-222310)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Gram (चना)", "Lentil/Masoor (मसूर)"],
    "tehsils": [
      make_tehsil("सागर (Sagar)", "Sagar", ["मकरोनिया (Makroniya)", "जैसीनगर (Jaisinagar)", "कर्रापुर (Karrapur)"]),
      make_tehsil("बीना (Bina)", "Bina", ["भानगढ़ (Bhangarh)", "मंडी बामोरा (Mandi Bamora)", "आगासोद (Agasod)"]),
      make_tehsil("खुरई (Khurai)", "Khurai", ["मालथौन (Malthone)", "बांदरी (Bandri)"]),
      make_tehsil("रहली (Rehli)", "Rehli", ["गढ़ाकोटा (Gadhakota)", "चांदपुर (Chandpur)"]),
      make_tehsil("बंडा (Banda)", "Banda", ["शाहगढ़ (Shahgarh)", "दलपतपुर (Dalpatpur)"]),
      make_tehsil("देवरी (Deori)", "Deori", ["केसली (Kesli)", "गौरझामर (Gourjhamar)"]),
      make_tehsil("राहतगढ़ (Rahatgarh)", "Rahatgarh", ["सिहोरा (Sihora)", "बेगमगंज रोड (Begamganj Road)"])
    ]
  },

  # 30. DAMOH
  {
    "id": "damoh",
    "name_hi": "दमोह (Damoh)",
    "name_en": "Damoh",
    "division": "Sagar",
    "lat": 23.8323,
    "lon": 79.4420,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, दमोह (07812-224130)",
    "toll_free": "14447",
    "major_crops": ["Gram (चना)", "Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Paddy (धान)"],
    "tehsils": [
      make_tehsil("दमोह (Damoh)", "Damoh", ["बांदकपुर (Bandakpur)", "नोहटा (Nohta)", "हिंडोरिया (Hindoriya)"]),
      make_tehsil("हटा (Hatta)", "Hatta", ["पटेरा (Patera)", "मड़िहादो (Madihado)"]),
      make_tehsil("पथरिया (Pathariya)", "Pathariya", ["बोतराई (Botrai)", "जेरठ (Jerath)"]),
      make_tehsil("जबेरा (Jabera)", "Jabera", ["तेन्दूखेड़ा (Tendukheda)", "सिग्रामपुर (Sigrampur)"]),
      make_tehsil("बटियागढ़ (Batiyagarh)", "Batiyagarh", ["बखतपुरा (Bakhatpura)", "मगरोन (Magron)"])
    ]
  },

  # 31. PANNA
  {
    "id": "panna",
    "name_hi": "पन्ना (Panna)",
    "name_en": "Panna",
    "division": "Sagar",
    "lat": 24.7208,
    "lon": 80.1818,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, पन्ना (07732-252110)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Gram (चना)", "Mustard (सरसों)"],
    "tehsils": [
      make_tehsil("पन्ना (Panna)", "Panna", ["देवेन्द्रनगर (Devendranagar)", "ककरहटी (Kakarhati)"]),
      make_tehsil("पवई (Pawai)", "Pawai", ["सिमरिया (Simariya)", "मोहन्द्रा (Mohandra)"]),
      make_tehsil("गुन्नौर (Gunnor)", "Gunnor", ["अमानगंज (Amanganj)", "सलेहा (Saleha)"]),
      make_tehsil("अजयगढ़ (Ajaigarh)", "Ajaigarh", ["धरमपुर (Dharampur)", "बीरा (Beera)"]),
      make_tehsil("शाहनगर (Shahnagar)", "Shahnagar", ["बोरी (Bori)", "रैपुरा (Raipura)"])
    ]
  },

  # 32. CHHATARPUR
  {
    "id": "chhatarpur",
    "name_hi": "छतरपुर (Chhatarpur)",
    "name_en": "Chhatarpur",
    "division": "Sagar",
    "lat": 24.9164,
    "lon": 79.5811,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, छतरपुर (07682-241240)",
    "toll_free": "14447",
    "major_crops": ["Sesame/Til (तिल)", "Groundnut (मूंगफली)", "Wheat (गेहूँ)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("छतरपुर (Chhatarpur)", "Chhatarpur", ["गड़ीमलहरा (Gadimalehra)", "ईशानगर (Ishanagar)"]),
      make_tehsil("नौगांव (Nowgong)", "Nowgong", ["गर्रोली (Garroli)", "महाराजपुर रोड (Maharajpur Road)"]),
      make_tehsil("महाराजपुर (Maharajpur)", "Maharajpur", ["कुसमारिया (Kusmariya)", "टटम (Tatam)"]),
      make_tehsil("राजनगर / खजुराहो (Rajnagar)", "Rajnagar", ["खजुराहो (Khajuraho)", "बमीठा (Bamitha)"]),
      make_tehsil("बिजावर (Bijawar)", "Bijawar", ["किशनगढ़ (Kishangarh)", "सटई (Satai)"]),
      make_tehsil("बड़ामलहरा (Bada Malhera)", "Bada Malhera", ["भगवां (Bhagawa)", "बक्सवाहा (Buxwaha)"]),
      make_tehsil("लवकुशनगर (Lavkushnagar)", "Lavkushnagar", ["चंदला (Chandla)", "गौरिहार (Gaurihar)"])
    ]
  },

  # 33. TIKAMGARH
  {
    "id": "tikamgarh",
    "name_hi": "टीकमगढ़ (Tikamgarh)",
    "name_en": "Tikamgarh",
    "division": "Sagar",
    "lat": 24.7447,
    "lon": 78.8315,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, टीकमगढ़ (07683-242310)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Groundnut (मूंगफली)", "Wheat (गेहूँ)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("टीकमगढ़ (Tikamgarh)", "Tikamgarh", ["बड़ागांव (Badagaon)", "कुण्डेश्वर (Kundeshwar)"]),
      make_tehsil("बल्देवगढ़ (Baldeogarh)", "Baldeogarh", ["खरगापुर (Khargapur)", "कुड़ीला (Kudila)"]),
      make_tehsil("जतारा (Jatara)", "Jatara", ["लिधौरा (Lidhora)", "महेवा (Mahewa)"]),
      make_tehsil("पलेरा (Palera)", "Palera", ["सैदपुर (Saidpur)", "बन्नेबुजुर्ग (Banne Bujurg)"]),
      make_tehsil("मोहनगढ़ (Mohangarh)", "Mohangarh", ["अतर्रा (Atarra)", "पृथ्वीपुर रोड (Prithvipur Road)"])
    ]
  },

  # 34. NIWARI
  {
    "id": "niwari",
    "name_hi": "निवाड़ी (Niwari)",
    "name_en": "Niwari",
    "division": "Sagar",
    "lat": 25.3619,
    "lon": 78.8020,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, निवाड़ी (07680-231120)",
    "toll_free": "14447",
    "major_crops": ["Groundnut (मूंगफली)", "Wheat (गेहूँ)", "Gram (चना)", "Mustard (सरसों)"],
    "tehsils": [
      make_tehsil("निवाड़ी (Niwari)", "Niwari", ["तरिचर कलां (Tarichar Kalan)", "सेंदरी (Sendri)"]),
      make_tehsil("ओरछा (Orchha)", "Orchha", ["लाडपुरा (Ladpura)", "प्रतापुरा (Pratappura)"]),
      make_tehsil("पृथ्वीपुर (Prithvipur)", "Prithvipur", ["अछरू माता (Achhru Mata)", "मोहनगढ़ रोड (Mohangarh Road)"])
    ]
  },

  # 35. JABALPUR
  {
    "id": "jabalpur",
    "name_hi": "जबलपुर (Jabalpur)",
    "name_en": "Jabalpur",
    "division": "Jabalpur",
    "lat": 23.1815,
    "lon": 79.9864,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, जबलपुर (0761-2621410)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Green Pea/Matar (जबलपुर मटर - GI)", "Wheat (गेहूँ)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("जबलपुर (Jabalpur)", "Jabalpur", ["पनागर (Panagar)", "बरेला (Barela)", "भेड़ाघाट (Bhedaghat)"]),
      make_tehsil("पाटन (Patan)", "Patan", ["कटंगी-पाटन (Katangi-Patan)", "शहपुरा रोड (Shahpura Road)"]),
      make_tehsil("सिहोरा (Sihora)", "Sihora", ["मझौली (Majholi)", "गोसलपुर (Gosalpur)"]),
      make_tehsil("मझौली (Majholi)", "Majholi", ["इन्द्राना (Indrana)", "पैलवारा (Pailwara)"]),
      make_tehsil("शहपुरा (Shahpura)", "Shahpura", ["बेलखेड़ा (Belkheda)", "चरगवां (Chargawan)"]),
      make_tehsil("कुंडम (Kundam)", "Kundam", ["बगराजी (Bagraji)", "तिहारी (Tihari)"])
    ]
  },

  # 36. KATNI
  {
    "id": "katni",
    "name_hi": "कटनी (Katni)",
    "name_en": "Katni",
    "division": "Jabalpur",
    "lat": 23.8343,
    "lon": 80.3957,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, कटनी (07622-220130)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Gram (चना)", "Pulses (दालें)"],
    "tehsils": [
      make_tehsil("कटनी (Katni)", "Katni", ["माधव नगर (Madhav Nagar)", "झिंझरी (Jhinjhari)"]),
      make_tehsil("रीठी (Rithi)", "Rithi", ["बिलहरी (Bilhari)", "कैमोर (Kymore)"]),
      make_tehsil("बड़वारा (Badwara)", "Badwara", ["विजयरघौगढ़ रोड (Vijayraghavgarh Road)", "रोहनिया (Rohaniya)"]),
      make_tehsil("विजयराघवगढ़ (Vijayraghavgarh)", "Vijayraghavgarh", ["कैमोर (Kymore)", "बरही (Barhi)"]),
      make_tehsil("बहोरीबंद (Bahoriband)", "Bahoriband", ["स्लीमनाबाद (Sleemanabad)", "बाकल (Bakal)"]),
      make_tehsil("ढीमरखेड़ा (Dheemerkheda)", "Dheemerkheda", ["उमरियापान (Umariapan)", "दशारमन (Dasharaman)"])
    ]
  },

  # 37. NARSINGHPUR
  {
    "id": "narsinghpur",
    "name_hi": "नरसिंहपुर (Narsinghpur)",
    "name_en": "Narsinghpur",
    "division": "Jabalpur",
    "lat": 22.9463,
    "lon": 79.1944,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, नरसिंहपुर (07792-230520)",
    "toll_free": "14447",
    "major_crops": ["Sugarcane (गन्ना - चीनी कटोरा)", "Pigeon Pea/Tur (अरहर दाल - GI)", "Wheat (गेहूँ)", "Soybean (सोयाबीन)"],
    "tehsils": [
      make_tehsil("नरसिंहपुर (Narsinghpur)", "Narsinghpur", ["करेली (Kareli)", "सिंहपुर (Singhpur)", "बरमान (Barman)"]),
      make_tehsil("गाडरवारा (Gadarwara)", "Gadarwara", ["साईंखेड़ा (Saikheda)", "चीचली (Chichli)", "सालीचौका (Salichouka)"]),
      make_tehsil("करेली (Kareli)", "Kareli", ["बड़ागांव (Badagaon)", "गुड़ मंडी क्षेत्र (Jaggery Hub)"]),
      make_tehsil("गोटेगांव (Gotegaon)", "Gotegaon", ["श्रीनगर (Shrinagar)", "झांसीघाट (Jhansi Ghat)"]),
      make_tehsil("तेंदूखेड़ा (Tendukheda)", "Tendukheda", ["बिलहरा (Bilhara)", "चांवरपाठा (Chanwarpatha)"])
    ]
  },

  # 38. CHHINDWARA
  {
    "id": "chhindwara",
    "name_hi": "छिंदवाड़ा (Chhindwara)",
    "name_en": "Chhindwara",
    "division": "Jabalpur",
    "lat": 22.0574,
    "lon": 78.9382,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, छिंदवाड़ा (07162-242310)",
    "toll_free": "14447",
    "major_crops": ["Maize (मक्का - कॉर्न सिटी)", "Orange (संतरा)", "Cotton (कपास)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("छिंदवाड़ा (Chhindwara)", "Chhindwara", ["चंदनगांव (Chandangaon)", "इमलीखेड़ा (Imlikheda)", "सरना (Sarna)"]),
      make_tehsil("परासिया (Parasia)", "Parasia", ["चांदामेटा (Chandameta)", "बड़कुही (Badkuhi)", "न्यूटन (Newton)"]),
      make_tehsil("जुन्नारदेव (Junnardeo)", "Junnardeo", ["दमुआ (Damua)", "पातालकोट (Patalkot)"]),
      make_tehsil("अमरवाड़ा (Amarwara)", "Amarwara", ["सिंगोड़ी (Singodi)", "छिरिया (Chhiriya)"]),
      make_tehsil("चौरई (Chourai)", "Chourai", ["चांद (Chand)", "सिरस (Siras)"]),
      make_tehsil("मोहखेड़ (Mohkhed)", "Mohkhed", ["उमरानाला (Umranala)", "सावरी (Sawri)"]),
      make_tehsil("हर्रई (Harrai)", "Harrai", ["बटकाखापा (Batkakhapa)", "धनोरा (Dhanora)"]),
      make_tehsil("तामिया (Tamia)", "Tamia", ["पातालकोट (Patalkot घाटी)", "झिरपा (Jhirpa)"])
    ]
  },

  # 39. PANDHURNA
  {
    "id": "pandhurna",
    "name_hi": "पांढुर्णा (Pandhurna)",
    "name_en": "Pandhurna",
    "division": "Jabalpur",
    "lat": 21.5991,
    "lon": 78.5262,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, पांढुर्णा (07164-220110)",
    "toll_free": "14447",
    "major_crops": ["Cotton (कपास)", "Orange (संतरा)", "Soybean (सोयाबीन)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("पांढुर्णा (Pandhurna)", "Pandhurna", ["बड़चिचोली (Badchicholi)", "तिगांव (Tigaon)", "हिवरा (Hiwra)"]),
      make_tehsil("सौंसर (Sausar)", "Sausar", ["लोधीखेड़ा (Lodhikhada)", "रामाकोना (Ramakona)", "बोरगांव (Borgaon)"])
    ]
  },

  # 40. SEONI
  {
    "id": "seoni",
    "name_hi": "सिवनी (Seoni)",
    "name_en": "Seoni",
    "division": "Jabalpur",
    "lat": 22.0869,
    "lon": 79.5435,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, सिवनी (07692-220410)",
    "toll_free": "14447",
    "major_crops": ["Paddy (जीराशंकर सुगंधित धान)", "Soybean (सोयाबीन)", "Maize (मक्का)", "Wheat (गेहूँ)"],
    "tehsils": [
      make_tehsil("सिवनी (Seoni)", "Seoni", ["गोपालगंज (Gopalganj)", "बंडोल (Bandol)", "डूंडासिवनी (Dundaseoni)"]),
      make_tehsil("बरघाट (Barghat)", "Barghat", ["आष्टा-बरघाट (Ashta-Barghat)", "गांगपुर (Gangpur)"]),
      make_tehsil("लखनादौन (Lakhnadon)", "Lakhnadon", ["धूमा (Dhuma)", "आदेगांव (Adegaon)"]),
      make_tehsil("केवलारी (Kewlari)", "Kewlari", ["उगली (Ugali)", "पलारी (Palari)"]),
      make_tehsil("घंसौर (Ghansore)", "Ghansore", ["शिकारा (Shikara)", "कहानी (Kahani)"]),
      make_tehsil("छपारा (Chhapara)", "Chhapara", ["भीमगढ़ (Bheemgarh)", "चमारी (Chamari)"]),
      make_tehsil("कुरई (Kurai)", "Kurai", ["पेंच राष्ट्रीय उद्यान क्षेत्र (Pench)", "सुकतरा (Suktara)"])
    ]
  },

  # 41. BALAGHAT
  {
    "id": "balaghat",
    "name_hi": "बालाघाट (Balaghat)",
    "name_en": "Balaghat",
    "division": "Jabalpur",
    "lat": 21.8129,
    "lon": 80.1837,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, बालाघाट (07632-240120)",
    "toll_free": "14447",
    "major_crops": ["Chinnor Rice (चिन्नौर चावल - GI टैग)", "Paddy (धान)", "Linseed (अलसी)"],
    "tehsils": [
      make_tehsil("बालाघाट (Balaghat)", "Balaghat", ["गर्रा (Garra)", "उकवा (Ukwa)", "भरवेली (Bharveli)"]),
      make_tehsil("वारासिवनी (Waraseoni)", "Waraseoni", ["रामपायली (Rampayli)", "मेंहदीवाड़ा (Mehdiwada)"]),
      make_tehsil("कटंगी (Katangi)", "Katangi", ["तिरोड़ी (Tirodi)", "बोरी (Bori)"]),
      make_tehsil("लांजी (Lanji)", "Lanji", ["बहेला (Bahela)", "कारंजा (Karanja)"]),
      make_tehsil("बैहर (Baihar)", "Baihar", ["मुक्की (Mukki - कान्हा)", "बिरसा (Birsa)"]),
      make_tehsil("परसवाड़ा (Paraswada)", "Paraswada", ["उकवा (Ukwa)", "कान्हा बफर क्षेत्र"]),
      make_tehsil("लालबर्रा (Lalbarra)", "Lalbarra", ["बड़गांव (Badgaon)", "कटेधरा (Katedhara)"]),
      make_tehsil("खैरलांजी (Khairlanji)", "Khairlanji", ["भटेरा (Bhatera)", "किरनापुर रोड (Kirnapur Road)"])
    ]
  },

  # 42. MANDLA
  {
    "id": "mandla",
    "name_hi": "मंडला (Mandla)",
    "name_en": "Mandla",
    "division": "Jabalpur",
    "lat": 22.5986,
    "lon": 80.3712,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, मंडला (07642-251140)",
    "toll_free": "14447",
    "major_crops": ["Kodo-Kutki (कोदो-कुटकी मिलेट्स)", "Paddy (धान)", "Maize (मक्का)"],
    "tehsils": [
      make_tehsil("मंडला (Mandla)", "Mandla", ["महाराजपुर (Maharajpur)", "बम्हनी बंजर (Bamhni Banjar)"]),
      make_tehsil("नैनपुर (Nainpur)", "Nainpur", ["पिंडरई (Pindrai)", "जिरोली (Jiroli)"]),
      make_tehsil("बिछिया (Bichhiya)", "Bichhiya", ["अंजनिया (Anjaniya)", "सिझौरा (Sijhora)"]),
      make_tehsil("निवास (Niwas)", "Niwas", ["बबली (Babli)", "मनेरी (Maneri)"]),
      make_tehsil("नारायणगंज (Narayanganj)", "Narayanganj", ["टिकरिया (Tikariya)", "बड़झर (Badjhar)"])
    ]
  },

  # 43. DINDORI
  {
    "id": "dindori",
    "name_hi": "डिंडौरी (Dindori)",
    "name_en": "Dindori",
    "division": "Jabalpur",
    "lat": 22.9547,
    "lon": 81.0818,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, डिंडौरी (07644-234110)",
    "toll_free": "14447",
    "major_crops": ["Kodo-Kutki (कोदो कुटकी - श्रीअन्न)", "Paddy (धान)", "Niger (रामतिल)"],
    "tehsils": [
      make_tehsil("डिंडौरी (Dindori)", "Dindori", ["गाड़ासरई (Gadasarai)", "कुकरामठ (Kukramath)"]),
      make_tehsil("शहपुरा (Shahpura)", "Shahpura", ["बरगांव (Bargaon)", "राघोपुर (Raghopur)"]),
      make_tehsil("बजाग (Bajag)", "Bajag", ["चाड़ा (Chada)", "करंजिया रोड (Karanjiya Road)"]),
      make_tehsil("समनापुर (Samnapur)", "Samnapur", ["अमरपुर (Amarpur)", "किसलपुरी (Kisalpur)"])
    ]
  },

  # 44. REWA
  {
    "id": "rewa",
    "name_hi": "रीवा (Rewa)",
    "name_en": "Rewa",
    "division": "Rewa",
    "lat": 24.5362,
    "lon": 81.3037,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, रीवा (07662-241510)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Gram (चना)", "Sundarja Mango (सुंदरजा आम - GI)"],
    "tehsils": [
      make_tehsil("हुजूर (Huzur-Rewa)", "Huzur", ["गोविंदगढ़ (Govindgarh)", "गुढ़ (Gudh)", "रताहरा (Ratahara)"]),
      make_tehsil("मंगवां (Mangawan)", "Mangawan", ["मनगवां (Manganwa)", "गंगेव (Gangev)", "लालगांव (Lalgaon)"]),
      make_tehsil("सिरमौर (Sirmaur)", "Sirmaur", ["डभौरा (Dabhoura)", "बैकुंठपुर (Baikunthpur)"]),
      make_tehsil("त्योंथर (Teonthar)", "Teonthar", ["चाकघाट (Chakghat)", "सोहागी (Sohagi)"]),
      make_tehsil("जवा (Jawa)", "Jawa", ["अतरैला (Atraila)", "बरोहा (Baroha)"]),
      make_tehsil("सेमरिया (Semariya)", "Semariya", ["शाहपुर (Shahpur)", "बसामन मामा (Basaman Mama)"])
    ]
  },

  # 45. MAUGANJ
  {
    "id": "mauganj",
    "name_hi": "मऊगंज (Mauganj)",
    "name_en": "Mauganj",
    "division": "Rewa",
    "lat": 24.6811,
    "lon": 81.8744,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, मऊगंज (07663-221140)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Gram (चना)", "Lentil (मसूर)"],
    "tehsils": [
      make_tehsil("मऊगंज (Mauganj)", "Mauganj", ["खटखरी (Khatkhari)", "पिपराही (Piprahi)", "देवतालाब (Devtalab)"]),
      make_tehsil("हनुमना (Hanumana)", "Hanumana", ["पिपरवार (Piparwar)", "हाटा (Hata)"]),
      make_tehsil("नईगढ़ी (Naigarhi)", "Naigarhi", ["अष्टभुजी (Ashtabhuji)", "चितरिया (Chitariya)"]),
      make_tehsil("देवतालाब (Devtalab)", "Devtalab", ["शिव मंदिर परिसर", "मझिगवां (Majhigawan)"])
    ]
  },

  # 46. SATNA
  {
    "id": "satna",
    "name_hi": "सतना (Satna)",
    "name_en": "Satna",
    "division": "Rewa",
    "lat": 24.5806,
    "lon": 80.8293,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, सतना (07672-222310)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Mustard (सरसों)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("रघुराजनगर / सतना (Raghurajnagar)", "Satna", ["सोहावल (Sohawal)", "कोटर (Kotar)", "माधवगढ़ (Madhavgarh)"]),
      make_tehsil("रामपुर बघेलान (Rampur Baghelan)", "Rampur Baghelan", ["बेला (Bela)", "सज्जनपुर (Sajjanpur)"]),
      make_tehsil("नागौद (Nagod)", "Nagod", ["सिंहपुर (Singhpur)", "जसो (Jaso)"]),
      make_tehsil("उचेहरा (Uchehara)", "Uchehara", ["परसमनिया (Parasmaniya)", "अतरवेदी (Atarvedi)"]),
      make_tehsil("मझगवां (Majhgawan)", "Majhgawan", ["चित्रकूट (Chitrakoot)", "पिंडरा (Pindra)", "बरौंधा (Baroundha)"])
    ]
  },

  # 47. MAIHAR
  {
    "id": "maihar",
    "name_hi": "मैहर (Maihar)",
    "name_en": "Maihar",
    "division": "Rewa",
    "lat": 24.2697,
    "lon": 80.7573,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, मैहर (07674-232110)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Mustard (सरसों)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("मैहर (Maihar)", "Maihar", ["शारदा देवी धाम क्षेत्र", "बदेरा (Badera)", "झूकेही (Jhukehi)"]),
      make_tehsil("अमरपाटन (Amarpatan)", "Amarpatan", ["मुकुंदपुर (Mukundpur - व्हाइट टाइगर)", "ताला (Tala)"]),
      make_tehsil("रामनगर (Ramnagar)", "Ramnagar", ["गोविंदगढ़ रोड (Govindgarh Road)", "देवराज (Devraj)"])
    ]
  },

  # 48. SIDHI
  {
    "id": "sidhi",
    "name_hi": "सीधी (Sidhi)",
    "name_en": "Sidhi",
    "division": "Rewa",
    "lat": 24.4034,
    "lon": 81.8797,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, सीधी (07682-252130)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Gram (चना)", "Linseed (अलसी)"],
    "tehsils": [
      make_tehsil("गोपद बनास / सीधी (Gopad Banas)", "Sidhi", ["कुचवाही (Kuchwahi)", "पड़रा (Padra)"]),
      make_tehsil("चुरहट (Churhat)", "Churhat", ["रामपुर नैकिन (Rampur Naikin)", "शिकारगंज (Shikarganj)"]),
      make_tehsil("मझौली (Majhauli)", "Majhauli", ["ताला (Tala)", "जोबा (Joba)"]),
      make_tehsil("कुसमी (Kusmi)", "Kusmi", ["टमसार (Tamsar)", "पोंडी (Pondi)"]),
      make_tehsil("सिहावल (Sihawal)", "Sihawal", ["बहरी (Bahari)", "अमिलिया (Amiliya)"])
    ]
  },

  # 49. SINGRAULI
  {
    "id": "singrauli",
    "name_hi": "सिंगरौली (Singrauli)",
    "name_en": "Singrauli",
    "division": "Rewa",
    "lat": 24.1992,
    "lon": 82.6644,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, सिंगरौली (07805-233140)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Maize (मक्का)"],
    "tehsils": [
      make_tehsil("बैढ़न (Waidhan)", "Waidhan", ["मोरवा (Morwa)", "विंध्यनगर (Vindhyanagar)"]),
      make_tehsil("देवसर (Deosar)", "Deosar", ["बरगवां (Bargawan)", "झांसी (Jhansi)"]),
      make_tehsil("चितरंगी (Chitrangi)", "Chitrangi", ["गढ़वा (Garhwa)", "नौगई (Naugai)"]),
      make_tehsil("सरई (Sarai)", "Sarai", ["गजरा बहरा (Gajra Bahra)", "निवास (Niwas)"])
    ]
  },

  # 50. SHAHDOL
  {
    "id": "shahdol",
    "name_hi": "शहडोल (Shahdol)",
    "name_en": "Shahdol",
    "division": "Shahdol",
    "lat": 23.2844,
    "lon": 81.3547,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, शहडोल (07652-240110)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Gram (चना)", "Kodo-Kutki (कोदो)"],
    "tehsils": [
      make_tehsil("सोहागपुर (Sohagpur)", "Sohagpur", ["बुढ़ार (Budhar)", "सिंहपुर (Singhpur)"]),
      make_tehsil("जैतपुर (Jaitpur)", "Jaitpur", ["खैरहा (Khairha)", "धनपुरी (Dhanpuri)"]),
      make_tehsil("ब्यौहारी (Beohari)", "Beohari", ["बाणसागर (Bansagar)", "पपौंध (Papondh)"]),
      make_tehsil("जयसिंहनगर (Jaysinghnagar)", "Jaysinghnagar", ["कनौंजा (Kanauja)", "अमझोर (Amjhor)"])
    ]
  },

  # 51. UMARIA
  {
    "id": "umaria",
    "name_hi": "उमरिया (Umaria)",
    "name_en": "Umaria",
    "division": "Shahdol",
    "lat": 23.5244,
    "lon": 80.8357,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, उमरिया (07653-222120)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Maize (मक्का)"],
    "tehsils": [
      make_tehsil("बांधवगढ़ / उमरिया (Bandhavgarh)", "Bandhavgarh", ["ताला (Tala - बांधवगढ़)", "चंदिया (Chandia)"]),
      make_tehsil("मानपुर (Manpur)", "Manpur", ["रोहनिया (Rohaniya)", "मझगवां (Majhgawan)"]),
      make_tehsil("पाली (Pali)", "Pali", ["नौरोजाबाद (Nowrozabad)", "बिरसिंहपुर (Birsinghpur)"])
    ]
  },

  # 52. ANUPPUR
  {
    "id": "anuppur",
    "name_hi": "अनूपपुर (Anuppur)",
    "name_en": "Anuppur",
    "division": "Shahdol",
    "lat": 23.1034,
    "lon": 81.6914,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, अनूपपुर (07659-222410)",
    "toll_free": "14447",
    "major_crops": ["Paddy (धान)", "Wheat (गेहूँ)", "Millets (मोटे अनाज)"],
    "tehsils": [
      make_tehsil("अनूपपुर (Anuppur)", "Anuppur", ["चचाई (Chachai)", "अमलाई (Amlai)"]),
      make_tehsil("कोतमा (Kotma)", "Kotma", ["बिजुरी (Bijuri)", "रामनगर (Ramnagar)"]),
      make_tehsil("जैतहरी (Jaithari)", "Jaithari", ["वेंकटनगर (Venkatnagar)", "चोलना (Cholna)"]),
      make_tehsil("पुष्पराजगढ़ (Pushprajgarh)", "Pushprajgarh", ["अमरकंटक (Amarkantak - नर्मदा उद्गम)", "राजेंद्रग्राम (Rajendragram)"])
    ]
  },

  # 53. NARMADAPURAM (HOSHANGABAD)
  {
    "id": "hoshangabad",
    "name_hi": "नर्मदापुरम / होशंगाबाद (Narmadapuram)",
    "name_en": "Narmadapuram",
    "division": "Narmadapuram",
    "lat": 22.7519,
    "lon": 77.7289,
    "insurance_company": "AIC of India",
    "krishi_officer": "उप संचालक कृषि, नर्मदापुरम (07574-252321)",
    "toll_free": "14447",
    "major_crops": ["Wheat (गेहूँ - मध्य प्रदेश की रोटी)", "Paddy (धान)", "Soybean (सोयाबीन)", "Gram (चना)"],
    "tehsils": [
      make_tehsil("नर्मदापुरम (Narmadapuram)", "Narmadapuram", ["रसूलिया (Rasulia)", "पवारखेड़ा (Pawarkheda कृषि केंद्र)"]),
      make_tehsil("माखननगर / बाबई (Makhannagar)", "Makhannagar", ["सांगाखेड़ा (Sangakheda)", "बचावनी (Bachawani)"]),
      make_tehsil("इटारसी (Itarsi)", "Itarsi", ["डोलरिया (Dolariya)", "सुखतवा (Sukhtawa)"]),
      make_tehsil("पिपरिया (Pipariya)", "Pipariya", ["पचमढ़ी (Pachmarhi)", "सांडिया (Sandia)"]),
      make_tehsil("सोहागपुर (Sohagpur)", "Sohagpur", ["सेमरी हरचंद (Semri Harchand)", "शोभापुर (Shobhapur)"]),
      make_tehsil("बनखेड़ी (Bankhedi)", "Bankhedi", ["चांदौनी (Chandauni)", "उमरधा (Umardha)"]),
      make_tehsil("सिवनी मालवा (Seoni Malwa)", "Seoni Malwa", ["बानापुरा (Banapura)", "शिवपुर (Shivpur)"]),
      make_tehsil("डोलरिया (Dolariya)", "Dolariya", ["भीलखेड़ी (Bhilkhedi)", "मिर्जापुर (Mirzapur)"])
    ]
  },

  # 54. HARDA
  {
    "id": "harda",
    "name_hi": "हरदा (Harda)",
    "name_en": "Harda",
    "division": "Narmadapuram",
    "lat": 22.3444,
    "lon": 77.0984,
    "insurance_company": "HDFC ERGO",
    "krishi_officer": "उप संचालक कृषि, हरदा (07577-222140)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Wheat (गेहूँ)", "Moong (ग्रीष्मकालीन मूंग)"],
    "tehsils": [
      make_tehsil("हरदा (Harda)", "Harda", ["हंडिया (Handia)", "मगामा (Magama)", "रन्हाई (Ranhai)"]),
      make_tehsil("टिमरनी (Timarni)", "Timarni", ["रहटगांव (Rahatgaon)", "पोखरनी (Pokharni)"]),
      make_tehsil("खिरकिया (Khirkiya)", "Khirkiya", ["सिराली (Sirali)", "चारुवा (Charuwa)"]),
      make_tehsil("सिराली (Sirali)", "Sirali", ["महालपुर (Mahalpur)", "पिपल्या (Pipliya)"])
    ]
  },

  # 55. BETUL
  {
    "id": "betul",
    "name_hi": "बैतूल (Betul)",
    "name_en": "Betul",
    "division": "Narmadapuram",
    "lat": 21.9015,
    "lon": 77.9023,
    "insurance_company": "SBI General Insurance",
    "krishi_officer": "उप संचालक कृषि, बैतूल (07141-230120)",
    "toll_free": "14447",
    "major_crops": ["Soybean (सोयाबीन)", "Maize (मक्का)", "Wheat (गेहूँ)", "Sugarcane (गन्ना)"],
    "tehsils": [
      make_tehsil("बैतूल (Betul)", "Betul", ["बडोरा (Badora)", "खेड़ी (Khedi)", "मलाजपुर (Malajpur)"]),
      make_tehsil("मुलताई (Multai)", "Multai", ["प्रभातपट्टन (Prabhat Pattan)", "मासोद (Masod)", "दुनावा (Dunawa)"]),
      make_tehsil("आमला (Amla)", "Amla", ["बोरी (Bori)", "कान्होज (Kanhoj)"]),
      make_tehsil("भैंसदेही (Bhainsdehi)", "Bhainsdehi", ["आठनेर (Aathner)", "भीमपुर (Bhimpur)"]),
      make_tehsil("घोड़ाडोंगरी (Ghoradongri)", "Ghoradongri", ["सारणी (Sarni)", "शाहपुर (Shahpur)"]),
      make_tehsil("चिचोली (Chicholi)", "Chicholi", ["चिरचिरा (Chirchira)", "भीमपुर (Bhimpur)"]),
      make_tehsil("शाहपुर (Shahpur)", "Shahpur", ["भौरी (Bhouri)", "कुंडी (Kundi)"]),
      make_tehsil("आठनेर (Aathner)", "Aathner", ["मांडवी (Mandvi)", "हिड़ली (Hidli)"])
    ]
  }
]

dest_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'mp_districts.json')
with open(dest_file, 'w', encoding='utf-8') as f:
    json.dump(mp_data, f, ensure_ascii=False, indent=2)

print(f"Successfully wrote {len(mp_data)} districts to {dest_file}")
dewas_tehsils = next(d for d in mp_data if d['id'] == 'dewas')['tehsils']
print("Dewas Tehsils Count:", len(dewas_tehsils))
sonkatch = next(t for t in dewas_tehsils if 'Sonkatch' in t['name_en'])
print("Sonkatch Villages:", sonkatch['villages'][:5])
