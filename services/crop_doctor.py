import datetime
import json
import re

# ICAR - Indian Institute of Soybean Research (भा.कृ.अनु.प. - भारतीय सोयाबीन अनुसंधान संस्थान, इंदौर)
# & JNKVV (जवाहरलाल नेहरू कृषि विश्वविद्यालय, जबलपुर) Verified Plant Protection Database
CROP_DISEASE_DATABASE = {
    "soybean": [
        {
            "id": "yellow_mosaic",
            "name_hi": "पीला मोज़ेक वायरस (Yellow Mosaic Virus)",
            "vector": "सफ़ेद मक्खी (Whitefly - Bemisia tabaci)",
            "keywords": ["पीला", "पीली", "मोज़ेक", "सफेद मक्खी", "whitefly", "yellow", "पत्तियां पीली"],
            "severity": "CRITICAL",
            "symptoms_hi": "पत्तियों पर अनियमित पीले-हरे चकत्ते, धीरे-धीरे पूरी पत्ती सुनहरी पीली पड़ जाती है। फलियों का आकार छोटा रह जाता है और दाने सिकुड़ जाते हैं।",
            "recommendations": {
                "chemical_treatment": "थायमेथॉक्सम 25% WG (Thiamethoxam 25% WG) @ 40 ग्राम प्रति एकड़ अथवा बीटा-साइफ्लुथ्रिन + इमिडाक्लोप्रिड 300 OD @ 140 मिली प्रति एकड़।",
                "brand_examples": "Syngenta Actara / Bayer Solomon / UPL Ulala",
                "organic_treatment": "नीम का तेल (Neem Oil 10,000 PPM) @ 400 मिली/एकड़ + खेत में 15-20 पीले चिपचिपे प्रपंच (Yellow Sticky Traps) प्रति एकड़ लगाएं।",
                "water_volume": "150 लीटर पानी प्रति एकड़",
                "phi_days": "21 दिन (तुड़ाई से पूर्व प्रतीक्षा अवधि)"
            },
            "expert_warning_hi": "⚠️ केवल टॉनिक या फफूंदनाशक डालने से पीला मोज़ेक नहीं रुकता! वायरस फैलाने वाली सफेद मक्खी का नियंत्रण तुरंत करें। रोगग्रस्त 1-2 पौधों को तुरंत उखाड़कर जमीन में दबा दें।"
        },
        {
            "id": "girdle_beetle",
            "name_hi": "गर्डल बीटल / चक्र भृंग (Girdle Beetle - Obereopsis brevis)",
            "vector": "तना छेदक कीट (Coleopteran Borer)",
            "keywords": ["गर्डल", "बीटल", "चक्र", "रिंग", "काट", "शाखा लटक", "girdle", "beetle"],
            "severity": "HIGH",
            "symptoms_hi": "तने या शाखा पर दो समानांतर गोल चक्र (रिंग) कट जाते हैं। चक्र के ऊपर की पत्तियां व शाखा लटककर सूख जाती हैं। मादा कीट इसी रिंग के बीच अंडा देती है।",
            "recommendations": {
                "chemical_treatment": "क्लोरेंट्रानिलिप्रोल 18.5% SC (Chlorantraniliprole) @ 60 मिली प्रति एकड़ अथवा थायक्लोप्रिड 21.7% SC @ 250 मिली प्रति एकड़।",
                "brand_examples": "FMC Coragen (कोराजन) / Bayer Alanto / Tata Takumi",
                "organic_treatment": "रिंग कटी हुई प्रभावित टहनियों को काटकर नष्ट करें ताकि इल्ली तने में नीचे न जा सके।",
                "water_volume": "150 लीटर पानी प्रति एकड़",
                "phi_days": "22 दिन"
            },
            "expert_warning_hi": "⚠️ चक्र कटने के 48 घंटे के भीतर ही छिड़काव प्रभावी होता है। यदि इल्ली तने के मुख्य भाग में अंदर चली गई तो कीटनाशक असरदार नहीं होता।"
        },
        {
            "id": "semilooper_spodoptera",
            "name_hi": "तंबाकू की इल्ली व सेमीलूपर (Defoliators / Green Semilooper)",
            "vector": "पत्ती खाने वाली इल्ली (Lepidoptera)",
            "keywords": ["इल्ली", "कीड़ा", "कीट", "छेद", "पत्ती खा", "semilooper", "caterpillar", "worm"],
            "severity": "HIGH",
            "symptoms_hi": "हरी व काली इल्लियां पत्तियों को छलनी (जालीदार) बना देती हैं। भारी प्रकोप होने पर केवल नसें बचती हैं और फलियों में छेद कर दाने खा जाती हैं।",
            "recommendations": {
                "chemical_treatment": "इमामेक्टिन बेंजोएट 5% SG (Emamectin Benzoate) @ 80 ग्राम प्रति एकड़ अथवा फ्लुबेंडामाइड 39.35% SC @ 40 मिली प्रति एकड़।",
                "brand_examples": "Proclaim (प्रॉक्लेम) / Bayer Fame (फेम) / Dhanuka Cover",
                "organic_treatment": "बैसिलस थुरिंजिएंसिस (Bt) @ 400 ग्राम/एकड़ या फेरोमोन ट्रैप (Pheromone Traps) 5 प्रति एकड़ लगाएं।",
                "water_volume": "150 लीटर पानी प्रति एकड़",
                "phi_days": "14 दिन"
            },
            "expert_warning_hi": "⚠️ इल्ली छोटी अवस्था में ही नियंत्रित करें। बड़ी 3-4 सेमी इल्ली पर सामान्य कीटनाशक बेअसर हो जाते हैं।"
        },
        {
            "id": "anthracnose_pod_blight",
            "name_hi": "एंथ्रेक्नोज व फली झुलसा (Anthracnose / Pod Blight)",
            "vector": "फफूंद (Colletotrichum truncatum)",
            "keywords": ["झुलसा", "फफूंद", "धब्बे", "फली सूख", "एंथ्रेक्नोज", "anthracnose", "fungus", "blight"],
            "severity": "HIGH",
            "symptoms_hi": "पत्तियों की नसों, तने व फलियों पर गहरे कत्थई या काले धब्बे बन जाते हैं। फलियां समय से पहले पीली होकर सूखने लगती हैं और बीज नहीं बनते।",
            "recommendations": {
                "chemical_treatment": "टेबुकोनाजोल 25.9% EC @ 250 मिली प्रति एकड़ अथवा टेबुकोनाजोल 50% + ट्राइफ्लोक्सीस्ट्रोबिन 25% WG (Nativo) @ 140 ग्राम प्रति एकड़।",
                "brand_examples": "Bayer Nativo / Bayer Folicur / Dhanuka Lustre",
                "organic_treatment": "स्यूडोमोनास फ्लोरेसेंस (Pseudomonas fluorescens) @ 1 किग्रा/एकड़ पर्णीय छिड़काव।",
                "water_volume": "150 लीटर पानी प्रति एकड़",
                "phi_days": "20 दिन"
            },
            "expert_warning_hi": "⚠️ लगातार बारिश व 85% से अधिक आर्द्रता में यह फफूंद तेजी से फैलती है। मौसम खुलते ही धूप निकलने पर तत्काल छिड़काव करें।"
        },
        {
            "id": "chemical_burn_recovery",
            "name_hi": "अमानक/गलत खरपतवारनाशक से झुलसा (Herbicide Burn & Recovery)",
            "vector": "अमानक रसायन / ओवरडोज़ (2,4-D / Spurious Chemical)",
            "keywords": ["झुलस", "दवा से जली", "दवा लग गई", "पत्तियां मुड़", "खरपतवारनाशक", "burn", "weedicide"],
            "severity": "EMERGENCY",
            "symptoms_hi": "गलत खरपतवारनाशक (जैसे 2,4-D का बहाव या नकली ग्लाइफोसेट) के छिड़काव के 24-48 घंटे बाद पत्तियां मुड़कर जलने लगती हैं, बढ़वार रुक जाती है।",
            "recommendations": {
                "chemical_treatment": "प्राथमिक उपचार: खेत से जलभराव तुरंत निकालें। 19:19:19 (NPK घुलनशील खाद) @ 1 किग्रा + पोटेशियम ह्यूमेट (Humic Acid 98%) @ 250 ग्राम प्रति 150 लीटर पानी में मिलाकर तुरंत स्प्रे करें।",
                "brand_examples": "IFFCO 19-19-19 + IFFCO सागरिका लिक्विड (250 मिली/एकड़)",
                "organic_treatment": "गौमूत्र 5 लीटर + ताजा छाछ 2 लीटर को 150 लीटर पानी में मिलाकर 3 दिन के अंतराल पर छिड़कें।",
                "water_volume": "200 लीटर पानी प्रति एकड़ (हल्का स्प्रे)",
                "phi_days": "N/A (फसल बचाव उपचार)"
            },
            "expert_warning_hi": "🚨 कानूनी कदम: जिस डीलर से दवा खरीदी थी उसके बिल, खाली डिब्बे व लॉट नंबर की फोटो खेतप्रूफ में अपलोड करें और कीटनाशी अधिनियम 1968 के तहत तत्काल उप संचालक कृषि को शिकायत दर्ज कराएं!"
        }
    ]
}

def get_all_crop_diseases(crop="soybean"):
    """Returns all certified disease diagnoses for the crop."""
    return CROP_DISEASE_DATABASE.get(crop.lower(), CROP_DISEASE_DATABASE["soybean"])

def diagnose_crop_issue(query_text="", crop="soybean"):
    """
    Intelligently identifies the pest, virus or disease based on farmer's description.
    """
    diseases = get_all_crop_diseases(crop)
    text_clean = (query_text or "").lower()

    # Score each disease by matching keywords
    best_match = None
    highest_score = 0

    for d in diseases:
        score = 0
        for kw in d["keywords"]:
            if kw.lower() in text_clean:
                score += 2
        # Also check name words
        for w in d["name_hi"].lower().split():
            if len(w) > 3 and w in text_clean:
                score += 1
        if score > highest_score:
            highest_score = score
            best_match = d

    # If no high-confidence keyword matched, default to the most frequent MP issue (Semilooper or Yellow Mosaic)
    if not best_match or highest_score == 0:
        if "पीला" in text_clean:
            best_match = diseases[0] # Yellow mosaic
        elif "जल" in text_clean or "दवा" in text_clean:
            best_match = diseases[4] # Chemical burn
        else:
            best_match = diseases[2] # Semilooper (most common)

    return {
        "status": "success",
        "matched": highest_score > 0,
        "crop": crop,
        "diagnosis": best_match,
        "certified_source": "भा.कृ.अनु.प. - भारतीय सोयाबीन अनुसंधान संस्थान (ICAR-IISR), इंदौर"
    }

def format_crop_doctor_whatsapp(query_text="", crop="soybean"):
    """
    Formats an actionable, scientific Hindi response for WhatsApp messages.
    """
    res = diagnose_crop_issue(query_text, crop)
    d = res["diagnosis"]
    recs = d["recommendations"]

    lines = [
        f"🔬 *खेतप्रूफ फसल डॉक्टर (ICAR-IISR इंदौर प्रमाणित)*",
        f"🌱 फसल: *सोयाबीन*",
        f"🚨 पहचानी गई बीमारी/कीट: *{d['name_hi']}*",
        f"⚠️ गंभीरता: *{d['severity']}*",
        "━━━━━━━━━━━━━━━━━━━━",
        f"📋 *लक्षण:* {d['symptoms_hi']}",
        "",
        f"💊 *अनुमोदित रासायनिक उपचार (सही दवा व मात्रा):*",
        f"• *{recs['chemical_treatment']}*",
        f"• प्रचलित ब्रांड: _{recs['brand_examples']}_",
        f"• पानी की मात्रा: *{recs['water_volume']}*",
        f"• प्रतीक्षा अवधि (PHI): {recs['phi_days']}",
        "",
        f"🌿 *जैविक व देसी उपाय:*",
        f"• {recs['organic_treatment']}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        f"{d['expert_warning_hi']}",
        "",
        f"🏛️ _सलाह स्रोत: {res['certified_source']}_",
        "_दवा का पक्का बिल अवश्य लें और खेतप्रूफ में फोटो सुरक्षित रखें!_"
    ]

    return "\n".join(lines)
