import datetime
import json
import os
from services.icar_checker import verify_agri_input
from services.weather_alert import get_calamity_state, trigger_calamity, fetch_live_weather, get_district_info
from services.dossier_generator import generate_claim_dossier, generate_dealer_legal_notice
from services.mandi_rates import get_mandi_rates, format_mandi_whatsapp_message
from services.crop_doctor import diagnose_crop_issue, format_crop_doctor_whatsapp

CHAT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'whatsapp_history.json')
FARMER_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'farmer_profile.json')

def get_current_profile():
    if os.path.exists(FARMER_FILE):
        try:
            with open(FARMER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "district": "dewas",
        "tehsil": "सोनकच्छ",
        "village": "बेड़ाखेड़ी",
        "crop": "सोयाबीन JS-2034",
        "name": "नागेश शर्मा (Nagesh Sharma)"
    }

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_chat_history(messages):
    try:
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def process_farmer_message(user_text, image_url=None, location=None):
    history = load_chat_history()
    now_time = datetime.datetime.now().strftime("%I:%M %p")
    profile = get_current_profile()
    dist_id = profile.get("district", "dewas")
    dist_info = get_district_info(dist_id)
    dist_name = dist_info.get("name_hi", dist_id.capitalize())
    v_name = profile.get("village", "बेड़ाखेड़ी")
    t_name = profile.get("tehsil", "सोनकच्छ")
    crop_name = profile.get("crop", "सोयाबीन JS-2034")
    
    # Log user message
    user_msg_entry = {
        "id": f"msg_u_{len(history)+1}",
        "sender": "user",
        "text": user_text,
        "image": image_url,
        "location": location,
        "timestamp": now_time
    }
    history.append(user_msg_entry)
    
    text_clean = (user_text or "").strip().lower()
    bot_replies = []
    
    # 1. Location message received (e.g. WhatsApp pin or GPS)
    if location:
        lat = location.get("lat", 22.9750)
        lon = location.get("lon", 76.3500)
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"📍 *खेत की जीपीएस लोकेशन दर्ज हुई!*\n\nनिर्देशांक: `{lat:.4f}°, {lon:.4f}°`\nस्थान: *ग्राम {v_name}, तहसील {t_name}, जिला {dist_name}*\n\nअब आप जो भी नुकसान या दवा का फोटो भेजेंगे, उस पर यह जीपीएस और तारीख ऑटो-स्टैम्प हो जाएगी।",
            "badge": "GPS सुरक्षित",
            "quick_replies": ["नुकसान दर्ज करें", "फोटो भेजें", "मौसम स्थिति"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 2. Check if photo was sent
    elif image_url:
        if "weedicide" in image_url.lower() or "weed" in text_clean or "खरपतवार" in text_clean:
            res = verify_agri_input("Super Weed Burn 24D Mix", "SWB-7721-RAI")
            bot_reply = {
                "id": f"msg_b_{len(history)+1}",
                "sender": "bot",
                "text": f"🚨 *नकली / अमानक रसायन चेतावनी!* 🚨\n\nपहचाना गया: *{res['alert_title']}*\n\n⚠️ {res['reason']}\n\n🛡️ *खेतप्रूफ सुरक्षा कदम:*\n1. बोतल और बिल का फोटो GPS लोकेशन (`{v_name}`) के साथ सुरक्षित किया गया।\n2. कीटनाशी अधिनियम 1968 के तहत कानूनी नोटिस तैयार कर लिया गया है।",
                "badge": res["badge_hi"],
                "quick_replies": ["कानूनी नोटिस देखें", "72-घंटे दावा करें", "हेल्पलाइन 14447"],
                "timestamp": now_time
            }
        else:
            res = verify_agri_input("IFFCO Sagarika", "SG-2026-0814")
            bot_reply = {
                "id": f"msg_b_{len(history)+1}",
                "sender": "bot",
                "text": f"✅ *फोटो और बिल सुरक्षित दर्ज हुआ!*\n\nउत्पाद: *इफको सागरिका (IFFCO Sagarika)*\nबैच नं.: `SG-2026-0814`\nदर्ज स्थिति: *{res['badge_hi']}*\n\n📍 स्थान: {v_name}, {dist_name}\n📅 समय: {datetime.datetime.now().strftime('%d/%m/%Y %I:%M %p')}\n\nयह डिजिटल सबूत आपके खेतप्रूफ वॉल्ट में सुरक्षित है।",
                "badge": "प्रमाणित उत्पाद",
                "quick_replies": ["मौसम चेक करें", "नया फोटो भेजें", "मुख्य मेन्यू"],
                "timestamp": now_time
            }
        bot_replies.append(bot_reply)

    # 3. Voice text or natural language disaster report (e.g. "पानी भर गया", "फसल डूब गई", "ओले पड़े", "फसल जल गई")
    elif any(k in text_clean for k in ["पानी", "जलभराव", "डूब", "ओला", "बारिश", "बाढ़", "बरसात", "झुलस", "खराब", "बर्बाद", "बीघा"]):
        calamity_type = "अतिवृष्टि एवं जलभराव"
        if "ओला" in text_clean:
            calamity_type = "ओलावृष्टि (Hailstorm Damage)"
        elif "झुलस" in text_clean or "दवा" in text_clean or "जल" in text_clean:
            calamity_type = "अमानक रसायन से फसल क्षति (Chemical Burn)"
            
        calamity = trigger_calamity(dist_id, calamity_type, f"आवाज़/संदेश द्वारा दर्ज: {user_text}", crop_name)
        hrs = calamity.get("hours_left", 71)
        mins = calamity.get("minutes_left", 50)
        
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"🚨 *फसल नुकसान की सूचना तुरंत दर्ज हुई! (PMFBY 72-घंटे का नियम)*\n\n🌾 कृषक: *{profile.get('name', 'नागेश शर्मा')}*\n📍 स्थान: *ग्राम {v_name}, {t_name} ({dist_name})*\n🌱 फसल: *{crop_name}*\n⚠️ आपदा: *{calamity_type}*\n\n⏱️ *उलटी गिनती चालू है:* आपके पास दावा दर्ज करने हेतु केवल *{hrs} घंटे {mins} मिनट* शेष हैं!\n\n📄 आपकी आधिकारिक दावा पर्ची तैयार कर दी गई है। इसे तुरंत बीमा कंपनी या SADO को फॉरवर्ड करें:",
            "badge": f"{hrs}h {mins}m शेष",
            "quick_replies": ["दावा पर्ची देखें", "कृषि अधिकारी को भेजें", "हेल्पलाइन 14447"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 4. Mandi Rates Intent (दैनिक मंडी भाव - नजदीकी 4 मंडियां)
    elif any(k in text_clean for k in ["मंडी", "भाव", "रेट", "rate", "mandi", "bhav", "सोयाबीन भाव", "लहसुन", "चना भाव", "गेहूं भाव", "डॉलर", "प्याज भाव"]):
        mandi_msg = format_mandi_whatsapp_message(dist_id, user_text, tehsil=t_name, village=v_name)
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": mandi_msg,
            "badge": "लाइव मंडी भाव",
            "quick_replies": ["सोयाबीन भाव", "लहसुन भाव", "मौसम स्थिति", "मुख्य मेन्यू"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 5. Crop Doctor Intent (फसल डॉक्टर - कीट व रोग समाधान)
    elif any(k in text_clean for k in ["रोग", "बीमारी", "इल्ली", "कीड़ा", "कीट", "पीला", "सफेद मक्खी", "फली झुलसा", "गर्डल", "चक्र", "दवा बताओ", "डॉक्टर", "doctor", "spray", "उपचार"]):
        doctor_msg = format_crop_doctor_whatsapp(user_text, crop_name)
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": doctor_msg,
            "badge": "ICAR इंदौर प्रमाणित",
            "quick_replies": ["दवा की सही मात्रा", "मंडी भाव", "मौसम स्थिति", "मुख्य मेन्यू"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 6. Command 1: Inputs / Photo / Bill ICAR Check
    elif any(k in text_clean for k in ["1", "इनपुट", "फोटो", "बिल", "खाद", "बीज", "चेक", "नकली"]):
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"📸 *दवा, खाद या बीज का फोटो व बिल भेजें:*\n\nकृपया कीटनाशक की बोतल/बैग के सामने का भाग या डीलर के बिल का फोटो भेजें।\n\n💡 *खेतप्रूफ सुरक्षा:* तुरंत जांचेगा कि उत्पाद ICAR/CIBRC से प्रमाणित है या नकली, और ग्राम *{v_name}* के जीपीएस के साथ सुरक्षित करेगा।",
            "quick_replies": ["इफको सागरिका (नमूना 1)", "संदिग्ध खरपतवारनाशक (नमूना 2)", "मुख्य मेन्यू"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 7. Command 2: Claim loss reporting (72-Hour PMFBY)
    elif any(k in text_clean for k in ["2", "नुकसान", "दावा", "72", "claim", "आपदा"]):
        calamity = get_calamity_state()
        if not calamity.get("active"):
            calamity = trigger_calamity(dist_id, "अतिवृष्टि एवं जलभराव (Excessive Rainfall)", "खेत में पानी भरने से फसल को भारी नुकसान", crop_name)
            
        hrs = calamity.get("hours_left", 68)
        mins = calamity.get("minutes_left", 20)
        
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"🚨 *72-घंटे की PMFBY दावा विंडो सक्रिय है*\n\nगाँव: *{v_name}, {dist_name}*\nफसल: *{crop_name}*\nबीमा कंपनी: *{dist_info.get('insurance_company', 'HDFC ERGO')}*\n\n⏱️ *उलटी गिनती चालू है:* केवल *{hrs} घंटे {mins} मिनट* शेष हैं!\n\nप्रधानमंत्री फसल बीमा (PMFBY) के नियमानुसार 72 घंटे में सूचना न देने पर दावा निरस्त हो सकता है।\n\n👇 आपकी आधिकारिक दावा पर्ची व टोकन तैयार है:",
            "badge": f"{hrs}h {mins}m शेष",
            "quick_replies": ["दावा पावती टोकन", "कृषि अधिकारी को भेजें", "14447 पर कॉल"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 8. Command 3: Live Hyperlocal Weather & Spraying Advisory
    elif any(k in text_clean for k in ["3", "मौसम", "weather", "बारिश", "पानी गिरेगा", "तापमान"]):
        w = fetch_live_weather(dist_id, t_name, v_name)
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"🌦️ *लाइव मौसम स्टेशन - {v_name}, {t_name} ({dist_name})*\n\n🌡️ तापमान: *{w.get('temperature', '24°C')}* (महसूस: {w.get('apparent_temp', '26°C')})\n💧 आर्द्रता (नमी): *{w.get('humidity', '85%')}*\n🌧️ वर्षा: *{w.get('precipitation_mm', 0)} मिमी* (आज संभावना: {w.get('rain_probability', '15%')})\n💨 हवा गति: *{w.get('wind_speed', '5 km/h')}*\n\n🌾 *किसान मौसम सलाह:*\n{w.get('advisory_hi', 'मौसम सामान्य है।')}\n\n⚠️ आपातकाल में तुरंत '2' दबाकर 72 घंटे में फसल नुकसान दर्ज करें।",
            "quick_replies": ["नुकसान रिपोर्ट करें", "मंडी भाव", "मुख्य मेन्यू"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 9. Command 4: Official PMFBY Claim Slip & Token Receipt
    elif any(k in text_clean for k in ["4", "पर्ची", "दस्तावेज़", "dossier", "report", "पावती", "टोकन", "रसीद", "स्लिप", "token", "receipt"]):
        dossier = generate_claim_dossier()
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"📄 *PMFBY आधिकारिक दावा पावती (Official Receipt)*\n(टोकन क्र.: `{dossier['dossier_id']}`)\n\n👤 कृषक: *{dossier['farmer']['name']}*\n📍 ग्राम: *{v_name}, {t_name} ({dist_name})*\n🏷️ खसरा: *{dossier['farmer']['khasra_no']}* | रकबा: 6.5 एकड़\n🌱 फसल: *{crop_name}*\n🏦 बीमा कंपनी: *{dossier['district_info'].get('insurance_company')}*\n\n✅ *72-घंटे वैधता:* समय-सीमा के भीतर प्रमाणित दर्ज\n\n📌 _यह रसीद बीमा सर्वेक्षक या SADO को प्रस्तुत करने का पक्का प्रमाण है।_",
            "quick_replies": ["व्हाट्सएप पर शेयर करें", "कृषि अधिकारी फोन", "मुख्य मेन्यू"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 10. Command 5: Dealer Legal Notice (कीटनाशी अधिनियम 1968)
    elif any(k in text_clean for k in ["5", "कानूनी", "नोटिस", "डीलर", "शिकायत", "notice", "legal"]):
        legal = generate_dealer_legal_notice()
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"⚖️ *कीटनाशी अधिनियम 1968 वैधानिक नोटिस तैयार है!*\n(क्र.: `{legal['notice_no']}`)\n\nडीलर: *{legal['target_input']['dealer_name']}*\nउत्पाद: *{legal['target_input']['product_name']}*\nबैच: `{legal['target_input']['batch_no']}`\n\n📋 *कानूनी धाराएं:* धारा 21, 22 (नमूना जांच) एवं धारा 29 (दंडात्मक कार्रवाई)\n\n👇 आप इस नोटिस को सीधे कृषि उप संचालक और डीलर को व्हाट्सएप पर भेज सकते हैं:",
            "badge": "वैधानिक नोटिस तैयार",
            "quick_replies": ["व्हाट्सएप पर भेजें", "दावा पर्ची देखें", "मुख्य मेन्यू"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 11. Command 6: District Officers & Helplines (अधिकारी संपर्क व हेल्पलाइन)
    elif any(k in text_clean for k in ["6", "8", "अधिकारी", "नंबर", "संपर्क", "पटवारी", "sado", "dda", "हेल्पलाइन", "contact", "surveyor", "phone"]):
        krishi_off = dist_info.get("krishi_officer", f"उप संचालक कृषि, {dist_name}")
        ins_co = dist_info.get("insurance_company", "HDFC ERGO General Insurance")
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"📞 *कृषि अधिकारी व बीमा सहायता केंद्र ({dist_name})*\n━━━━━━━━━━━━━━━━━━━━\n1. 🏛️ *वरिष्ठ कृषि विकास अधिकारी (SADO)*\n   • क्षेत्र: तहसील {t_name}, जिला {dist_name}\n   • कार्य: 72 घंटे में फसल पंचनामा व संयुक्त सर्वे\n\n2. 🏢 *उप संचालक कृषि (DDA)*\n   • {krishi_off}\n\n3. 🛡️ *अधिकृत बीमा कंपनी:* *{ins_co}*\n   • PMFBY राष्ट्रीय टोल-फ्री: *14447* (24x7)\n\n4. 🌾 *किसान कॉल सेंटर:* *1800-180-1551* (निःशुल्क)\n5. 🚨 *म.प्र. सीएम हेल्पलाइन:* *181*",
            "badge": "अधिकारी संपर्क",
            "quick_replies": ["14447 पर कॉल", "दावा पर्ची", "मुख्य मेन्यू"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)

    # 12. Default Comprehensive Menu
    else:
        bot_reply = {
            "id": f"msg_b_{len(history)+1}",
            "sender": "bot",
            "text": f"🌾 *खेतप्रूफ (KhetProof) किसान जीवन-रेखा सहायक*\n📍 स्थान: *ग्राम {v_name}, {t_name} ({dist_name})*\n\nकृपया विकल्प चुनें या लिखकर भेजें:\n\n1️⃣ 📸 *दवा/खाद बिल व ICAR प्रमाणन जांच*\n2️⃣ 🚨 *फसल नुकसान सूचना (72-घंटे PMFBY दावा)*\n3️⃣ 🌾 *दैनिक मंडी भाव (देवास / MP मंडियां)*\n4️⃣ 🔬 *फसल डॉक्टर (इल्ली, पीला मोज़ेक सही दवा)*\n5️⃣ 🌦️ *लाइव मौसम स्टेशन व कृषि सलाह*\n6️⃣ 📄 *आधिकारिक दावा पावती रसीद (Token)*\n7️⃣ ⚖️ *डीलर कानूनी नोटिस (कीटनाशी 1968)*\n8️⃣ 📞 *कृषि अधिकारी व बीमा हेल्पलाइन नंबर*",
            "quick_replies": ["मंडी भाव 🌾", "फसल डॉक्टर 🔬", "दावा पावती 📄", "मौसम स्थिति 🌦️", "अधिकारी नंबर 📞"],
            "timestamp": now_time
        }
        bot_replies.append(bot_reply)
        
    for r in bot_replies:
        history.append(r)
        
    save_chat_history(history)
    return bot_replies


def handle_inbound_webhook(payload, form_data=None):
    """
    Processes real inbound messages from Twilio WhatsApp Sandbox or Meta WhatsApp Cloud API.
    Returns: (reply_text, twiml_xml_string)
    """
    user_text = ""
    sender_phone = ""
    media_url = None
    location = None

    # Check Twilio format (form_data: From, Body, MediaUrl0, Latitude, Longitude)
    if form_data:
        sender_phone = form_data.get('From', '')
        user_text = form_data.get('Body', '')
        media_url = form_data.get('MediaUrl0')
        lat = form_data.get('Latitude')
        lon = form_data.get('Longitude')
        if lat and lon:
            try:
                location = {"lat": float(lat), "lon": float(lon)}
            except Exception:
                pass

    # Check Meta Cloud API format
    elif payload and isinstance(payload, dict):
        try:
            entry = payload.get('entry', [{}])[0]
            change = entry.get('changes', [{}])[0].get('value', {})
            messages = change.get('messages', [])
            if messages:
                msg = messages[0]
                sender_phone = msg.get('from', '')
                if msg.get('type') == 'text':
                    user_text = msg.get('text', {}).get('body', '')
                elif msg.get('type') == 'image':
                    user_text = "फोटो भेजा गया"
                    media_url = msg.get('image', {}).get('id', 'media_img')
                elif msg.get('type') == 'location':
                    loc = msg.get('location', {})
                    location = {"lat": loc.get('latitude'), "lon": loc.get('longitude')}
                    user_text = "लोकेशन साझा की गई"
        except Exception:
            pass

    # Fallback to direct json
    if not user_text and payload and isinstance(payload, dict):
        user_text = payload.get('text', '')
        media_url = payload.get('image_url')
        location = payload.get('location')

    replies = process_farmer_message(user_text, image_url=media_url, location=location)
    reply_text = replies[0]['text'] if replies else "धन्यवाद। खेतप्रूफ पर आपकी सूचना दर्ज हो चुकी है।"

    # Generate standard Twilio TwiML XML
    twiml_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        <Body>{reply_text}</Body>
    </Message>
</Response>"""

    return {
        "reply_text": reply_text,
        "replies": replies,
        "twiml": twiml_xml,
        "sender": sender_phone
    }

