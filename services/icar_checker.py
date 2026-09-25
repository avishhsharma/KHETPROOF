import json
import os
import re

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'icar_biostimulants.json')

def load_database():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading ICAR database: {e}")
        return {"verified_products": [], "flagged_counterfeits": [], "districts": []}

def verify_agri_input(product_name: str, batch_no: str = "", category: str = ""):
    """
    Verifies an agricultural chemical, seed or bio-stimulant against ICAR whitelist
    and known counterfeit advisories (especially MP/Raisen/Vidisha cases).
    """
    db = load_database()
    product_lower = (product_name or "").lower().strip()
    batch_lower = (batch_no or "").lower().strip()
    
    # 1. Check known flagged counterfeits & hazards first
    for item in db.get("flagged_counterfeits", []):
        keyword = item.get("keyword", "").lower()
        brand = item.get("brand_name", "").lower()
        if (keyword and (keyword in product_lower or keyword in batch_lower)) or \
           (brand and (brand in product_lower)):
            return {
                "status": item.get("icar_status", "SUSPICIOUS_UNAPPROVED"),
                "is_verified": False,
                "is_hazardous": True,
                "safety_score": 15,
                "badge_hi": "🚨 संदिग्ध / अमानक उत्पाद",
                "badge_en": "Suspicious / Spurious Alert",
                "alert_title": item.get("alert_title_hi"),
                "reason": item.get("reason_hi"),
                "active_ingredient": item.get("active_ingredient"),
                "icar_reg_no": "अमानक / गैर-पंजीकृत (Non-Compliant)",
                "action_recommended_hi": "तत्काल उपयोग रोकें! डीलर का पक्का बिल, डिब्बे की फोटो व बैच नंबर 'खेतप्रूफ' में सुरक्षित रखें और उप संचालक कृषि को सूचित करें।"
            }
            
    # 2. Check verified whitelist (ICAR Schedule VI & CIBRC registered)
    for item in db.get("verified_products", []):
        brand = item.get("brand_name", "").lower()
        active = item.get("active_ingredient", "").lower()
        if any(w in product_lower for w in brand.split() if len(w) > 3) or \
           (active and any(w in product_lower for w in active.split() if len(w) > 4)):
            return {
                "status": "VERIFIED",
                "is_verified": True,
                "is_hazardous": False,
                "safety_score": item.get("safety_score", 95),
                "badge_hi": "✅ ICAR / CIBRC प्रमाणित",
                "badge_en": "ICAR / CIBRC Verified",
                "alert_title": "सुरक्षित एवं सरकार द्वारा अनुमोदित उत्पाद",
                "reason": item.get("notes_hi"),
                "active_ingredient": item.get("active_ingredient"),
                "icar_reg_no": item.get("icar_reg_no"),
                "action_recommended_hi": "उत्पाद वैध है। फिर भी बिल व बैच नंबर हमेशा सुरक्षित रखें ताकि विपत्ति के समय बीमा या क्षतिपूर्ति का पक्का सबूत रहे।"
            }

    # 3. Check for bio-stimulant keyword alert (out of ~30,000 biostimulants, only ~600 are verified)
    is_biostimulant = any(k in product_lower or k in (category or "").lower() for k in ["bio", "humic", "tonic", "booster", "stimulant", "growth", "बायो", "टॉनिक", "ह्यूमिक"])
    if is_biostimulant:
        return {
            "status": "UNVERIFIED_BIOSTIMULANT",
            "is_verified": False,
            "is_hazardous": False,
            "safety_score": 45,
            "badge_hi": "⚠️ गैर-प्रमाणित बायो-स्टिमुलेंट (सावधानी)",
            "badge_en": "Unverified Bio-stimulant",
            "alert_title": "30,000 में से केवल ~600 उत्पाद ICAR प्रमाणित हैं",
            "reason": "यह बायो-स्टिमुलेंट ICAR/FCO अनुसूची-VI की प्रथम प्रमाणित सूची में तुरंत नहीं पाया गया। कई गैर-प्रमाणित टॉनिक बेअसर या हानिकारक हो सकते हैं।",
            "active_ingredient": "अघोषित / जांच आवश्यक",
            "icar_reg_no": "जांच लंबित / FCO शेड्यूल VI अपुष्ट",
            "action_recommended_hi": "डीलर से ICAR / FCO Schedule-VI पंजीकरण प्रमाण पत्र मांगें एवं पक्के बिल पर बैच नंबर अनिवार्य रूप से लिखवाएं।"
        }

    # 4. Default generic response
    return {
        "status": "STANDARD_RECORDED",
        "is_verified": True,
        "is_hazardous": False,
        "safety_score": 75,
        "badge_hi": "ℹ️ विवरण दर्ज (सबूत सुरक्षित)",
        "badge_en": "Record Saved in Vault",
        "alert_title": "इनपुट का डिजिटल रिकॉर्ड तैयार है",
        "reason": "फोटो, बैच संख्या व स्थान का डिजिटल वाटरमार्क बना दिया गया है।",
        "active_ingredient": "दर्ज किया गया",
        "icar_reg_no": "समीक्षाधीन",
        "action_recommended_hi": "यह सबूत किसी भी फसल विवाद या बीमा दावे में मान्य साक्ष्य का काम करेगा।"
    }
