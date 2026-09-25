import datetime
import json
import os
import socket
import sys
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, Response

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from services.icar_checker import verify_agri_input, load_database
from services.weather_alert import fetch_live_weather, get_calamity_state, trigger_calamity, resolve_calamity, get_district_info
from services.dossier_generator import generate_claim_dossier, generate_dealer_legal_notice, calculate_pmfby_payout, get_pmfby_clause_info
from services.whatsapp_engine import process_farmer_message, load_chat_history, save_chat_history, handle_inbound_webhook
from services.mandi_rates import get_mandi_rates, format_mandi_whatsapp_message
from services.crop_doctor import get_all_crop_diseases, diagnose_crop_issue, format_crop_doctor_whatsapp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Handle uploads directory safely across standard and serverless environments
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception:
    import tempfile
    UPLOAD_DIR = os.path.join(tempfile.gettempdir(), 'khetproof_uploads')
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception:
        pass

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

import tempfile
TMP_DATA_DIR = tempfile.gettempdir()
FARMER_FILE = os.path.join(DATA_DIR, 'farmer_profile.json')
TMP_FARMER_FILE = os.path.join(TMP_DATA_DIR, 'khetproof_farmer_profile.json')
INPUTS_FILE = os.path.join(DATA_DIR, 'saved_inputs.json')
TMP_INPUTS_FILE = os.path.join(TMP_DATA_DIR, 'khetproof_saved_inputs.json')

_farmer_profile_mem = None
_saved_inputs_mem = None

def get_farmer_profile():
    global _farmer_profile_mem
    if _farmer_profile_mem is not None:
        return _farmer_profile_mem
    for target in (TMP_FARMER_FILE, FARMER_FILE):
        if os.path.exists(target):
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    _farmer_profile_mem = json.load(f)
                    return _farmer_profile_mem
            except Exception:
                pass
    return {}

def save_farmer_profile(data):
    global _farmer_profile_mem
    _farmer_profile_mem = data
    try:
        with open(FARMER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            return
    except Exception:
        pass
    try:
        with open(TMP_FARMER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_saved_inputs():
    global _saved_inputs_mem
    if _saved_inputs_mem is not None:
        return _saved_inputs_mem
    for target in (TMP_INPUTS_FILE, INPUTS_FILE):
        if os.path.exists(target):
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    _saved_inputs_mem = json.load(f)
                    return _saved_inputs_mem
            except Exception:
                pass
    return []

def save_saved_inputs(inputs):
    global _saved_inputs_mem
    _saved_inputs_mem = inputs
    try:
        with open(INPUTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(inputs, f, ensure_ascii=False, indent=2)
            return
    except Exception:
        pass
    try:
        with open(TMP_INPUTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(inputs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass



@app.route('/')
def index():
    return render_template('index.html')


def get_public_tunnel_url():
    """Check if running on Vercel or if Cloudflare or public tunnel is running and read active URL."""
    vercel_url = os.environ.get('VERCEL_URL')
    if vercel_url:
        return f"https://{vercel_url}" if not vercel_url.startswith('http') else vercel_url
    tunnel_file = os.path.join(DATA_DIR, 'public_tunnel.txt')
    if os.path.exists(tunnel_file):
        try:
            with open(tunnel_file, 'r', encoding='utf-8') as f:
                url = f.read().strip()
                if url.startswith('http'):
                    return url
        except Exception:
            pass
    return None

def get_lan_ip():
    """Discover the local Wi-Fi / LAN IP so farmers can access from their phones."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

@app.route('/api/network-info', methods=['GET'])
def network_info_endpoint():
    ip = get_lan_ip()
    pub_url = get_public_tunnel_url()
    host = request.host
    if not pub_url and any(domain in host for domain in ('vercel.app', 'onrender.com', 'khetproof')):
        pub_url = request.host_url.rstrip('/')
    effective_url = pub_url if pub_url else f"http://{ip}:5000"
    is_cloud = bool(os.environ.get('VERCEL') or (pub_url and 'vercel.app' in pub_url))
    return jsonify({
        "lan_ip": ip,
        "port": 5000,
        "public_url": pub_url,
        "mobile_url": effective_url,
        "is_public": bool(pub_url),
        "is_lan": ip != '127.0.0.1',
        "is_cloud": is_cloud,
        "title": "24/7 क्लाउड लाइव (कहीं से भी खोलें)" if is_cloud else ("लाइव वेबसाइट (कहीं से भी खोलें)" if pub_url else "मोबाइल से खेतप्रूफ खोलें")
    })

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')



MP_DIST_FILE = os.path.join(DATA_DIR, 'mp_districts.json')

def get_all_mp_districts():
    if os.path.exists(MP_DIST_FILE):
        try:
            with open(MP_DIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    db = load_database()
    return db.get("districts", [])

@app.route('/api/districts', methods=['GET'])
@app.route('/api/locations', methods=['GET'])
def list_locations():
    return jsonify(get_all_mp_districts())


@app.route('/api/profile', methods=['GET', 'POST'])
def profile_handler():
    if request.method == 'POST':
        data = request.json or {}
        curr = get_farmer_profile()
        curr.update(data)
        save_farmer_profile(curr)
        return jsonify({"success": True, "profile": curr})
    return jsonify(get_farmer_profile())


@app.route('/api/inputs', methods=['GET', 'POST'])
def inputs_handler():
    if request.method == 'POST':
        data = request.json or {}
        inputs = get_saved_inputs()
        
        # Verify product against ICAR database
        prod_name = data.get("product_name", "")
        batch_no = data.get("batch_no", "")
        cat = data.get("category", "")
        
        verification = verify_agri_input(prod_name, batch_no, cat)
        
        new_entry = {
            "id": f"inp_{uuid.uuid4().hex[:6]}",
            "product_name": prod_name,
            "category": cat or "Agri-Input",
            "batch_no": batch_no or "N/A",
            "mfg_date": data.get("mfg_date", "N/A"),
            "exp_date": data.get("exp_date", "N/A"),
            "mrp": data.get("mrp", "₹0"),
            "purchase_date": data.get("purchase_date", datetime.date.today().isoformat()),
            "dealer_name": data.get("dealer_name", "स्थानीय कृषि केंद्र"),
            "dealer_invoice_no": data.get("dealer_invoice_no", "CASH-MEMO"),
            "gps_lat": data.get("gps_lat", 23.3315),
            "gps_lon": data.get("gps_lon", 77.7818),
            "gps_location_text": data.get("gps_location_text", "रायसेन, म.प्र."),
            "bag_photo": data.get("bag_photo") or "/static/images/sample_sagarika.svg",
            "bill_photo": data.get("bill_photo") or "/static/images/sample_bill.svg",
            "icar_status": verification["status"],
            "icar_reg_no": verification["icar_reg_no"],
            "safety_score": verification["safety_score"],
            "badge_hi": verification["badge_hi"],
            "warning": verification["reason"] if not verification["is_verified"] else None,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        inputs.insert(0, new_entry)
        save_saved_inputs(inputs)
        return jsonify({"success": True, "entry": new_entry, "verification": verification})
        
    return jsonify(get_saved_inputs())


@app.route('/api/inputs/verify', methods=['POST'])
def verify_input_endpoint():
    data = request.json or {}
    res = verify_agri_input(data.get("product_name", ""), data.get("batch_no", ""), data.get("category", ""))
    return jsonify(res)


@app.route('/api/weather', methods=['GET'])
def weather_endpoint():
    profile = get_farmer_profile()
    district_id = request.args.get('district') or profile.get('district', 'dewas')
    tehsil = request.args.get('tehsil') or profile.get('tehsil', 'सोनकच्छ')
    village = request.args.get('village') or profile.get('village', 'बेड़ाखेड़ी')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    weather = fetch_live_weather(district_id, tehsil=tehsil, village=village, lat=lat, lon=lon)
    return jsonify(weather)


@app.route('/api/mandi-rates', methods=['GET'])
def mandi_rates_endpoint():
    profile = get_farmer_profile()
    district_id = request.args.get('district') or profile.get('district', 'dewas')
    tehsil = request.args.get('tehsil') or profile.get('tehsil', 'सोनकच्छ')
    village = request.args.get('village') or profile.get('village', 'बेड़ाखेड़ी')
    crop = request.args.get('crop') or 'soybean'
    rates = get_mandi_rates(district_id, tehsil=tehsil, village=village, crop=crop)
    return jsonify(rates)


@app.route('/api/crop-doctor', methods=['GET'])
def crop_doctor_endpoint():
    crop = request.args.get('crop', 'soybean')
    diseases = get_all_crop_diseases(crop)
    return jsonify({
        "status": "success",
        "crop": crop,
        "diseases": diseases,
        "source": "भा.कृ.अनु.प. - भारतीय सोयाबीन अनुसंधान संस्थान (ICAR-IISR), इंदौर"
    })


@app.route('/api/crop-doctor/diagnose', methods=['POST'])
def crop_doctor_diagnose_endpoint():
    data = request.json or {}
    query = data.get('query') or data.get('symptom', '')
    crop = data.get('crop', 'soybean')
    result = diagnose_crop_issue(query, crop=crop)
    return jsonify(result)


@app.route('/api/officers', methods=['GET'])
def officers_endpoint():
    profile = get_farmer_profile()
    district_id = request.args.get('district') or profile.get('district', 'dewas')
    tehsil = request.args.get('tehsil') or profile.get('tehsil', 'सोनकच्छ')
    dist_info = get_district_info(district_id)
    insurance_name = dist_info.get("insurance_company", "HDFC ERGO General Insurance")
    
    return jsonify({
        "status": "success",
        "district": dist_info.get("name_hi", district_id.capitalize()),
        "tehsil": tehsil,
        "insurance_company": insurance_name,
        "insurer": insurance_name,
        "krishi_officer": dist_info.get("krishi_officer", f"उप संचालक कृषि, {dist_info.get('name_hi')}"),
        "helplines": [
            {
                "title": "PMFBY 24x7 राष्ट्रीय हेल्पलाइन",
                "number": "14447",
                "desc": "दावा सूचना व पॉलिसी समस्या समाधान (निःशुल्क)",
                "type": "emergency"
            },
            {
                "title": "किसान कॉल सेंटर (Kisan Call Centre)",
                "number": "1800-180-1551",
                "desc": "कृषि विशेषज्ञ व वैज्ञानिक सलाह (सुबह 6 से रात 10)",
                "type": "advisory"
            },
            {
                "title": "मध्य प्रदेश सीएम हेल्पलाइन",
                "number": "181",
                "desc": "बीमा भुगतान व डीलर शिकायत निवारण",
                "type": "complaint"
            },
            {
                "title": "वरिष्ठ कृषि विकास अधिकारी (SADO)",
                "number": "07272-252130",
                "desc": f"तहसील {tehsil} कार्यालय (फसल नुकसान पंचनामा)",
                "type": "local"
            }
        ]
    })




@app.route('/api/calamity/status', methods=['GET'])
def calamity_status_endpoint():
    state = get_calamity_state()
    return jsonify(state)


@app.route('/api/calamity/trigger', methods=['POST'])
def calamity_trigger_endpoint():
    data = request.json or {}
    profile = get_farmer_profile()
    district_id = data.get('district') or profile.get('district', 'raisen')
    calamity_type = data.get('calamity_type', 'अतिवृष्टि एवं जलभराव (Excessive Rainfall)')
    notes = data.get('notes', '')
    crop = profile.get('crop', 'Soybean (सोयाबीन JS-2034)')
    
    state = trigger_calamity(district_id, calamity_type, notes, crop)
    return jsonify({"success": True, "state": state})


@app.route('/api/calamity/resolve', methods=['POST'])
def calamity_resolve_endpoint():
    data = request.json or {}
    ref = data.get('claim_reference', f"PMFBY-CLAIM-{uuid.uuid4().hex[:8].upper()}")
    state = resolve_calamity(ref)
    return jsonify({"success": True, "state": state})


@app.route('/api/dossier', methods=['GET'])
def dossier_endpoint():
    dossier = generate_claim_dossier()
    return jsonify(dossier)


@app.route('/api/claim/calculate-payout', methods=['GET', 'POST'])
def claim_calculate_payout_endpoint():
    data = request.json if request.is_json else request.args.to_dict()
    profile = get_farmer_profile()
    acres = data.get('acres') or profile.get('total_land_acres', 6.5)
    crop = data.get('crop') or profile.get('crop', 'सोयाबीन')
    loss_percent = data.get('loss_percent') or 65
    district = data.get('district') or profile.get('district', 'dewas')
    calamity_type = data.get('calamity_type', 'अतिवृष्टि एवं जलभराव')
    
    payout = calculate_pmfby_payout(acres, crop, loss_percent, district)
    clause = get_pmfby_clause_info(calamity_type)
    return jsonify({
        "success": True,
        "payout": payout,
        "clause": clause
    })


@app.route('/api/whatsapp/message', methods=['POST'])
def whatsapp_message_endpoint():
    data = request.json or {}
    user_text = data.get('text', '')
    image_url = data.get('image_url')
    location = data.get('location')
    
    replies = process_farmer_message(user_text, image_url, location)
    return jsonify({"success": True, "replies": replies})


@app.route('/api/whatsapp/history', methods=['GET'])
def whatsapp_history_endpoint():
    history = load_chat_history()
    if not history:
        # Preload initial greeting
        process_farmer_message("नमस्ते")
        history = load_chat_history()
    return jsonify(history)


@app.route('/api/scan-label', methods=['POST'])
def scan_label_endpoint():
    data = request.json or {}
    sample_type = data.get('sample_type', 'sagarika')
    if sample_type == 'weedicide':
        prod_name = "Super Weed Burn 24D Mix"
        batch_no = "SWB-7721-RAI"
        category = "Weedicide / शाकनाशी"
        mfg = "06/2026"
        exp = "05/2028"
        active = "अघोषित रसायनों का मिश्रण (Unregistered 2,4-D)"
        img = "/static/images/sample_weedicide.svg"
    elif sample_type == 'pursuit':
        prod_name = "Pursuit (पर्स्यूट खरपतवारनाशक)"
        batch_no = "PR-9844-BASF"
        category = "Weedicide / शाकनाशी"
        mfg = "05/2026"
        exp = "04/2028"
        active = "Imazethapyr 10% SL"
        img = "/static/images/sample_sagarika.svg"
    else:
        prod_name = "IFFCO Sagarika (इफको सागरिका)"
        batch_no = "SG-2026-0814"
        category = "Bio-stimulant (सीवीड अर्क)"
        mfg = "04/2026"
        exp = "03/2028"
        active = "Seaweed Extract 28% w/w"
        img = "/static/images/sample_sagarika.svg"

    verification = verify_agri_input(prod_name, batch_no, category)
    return jsonify({
        "success": True,
        "ocr_result": {
            "product_name": prod_name,
            "batch_no": batch_no,
            "category": category,
            "mfg_date": mfg,
            "exp_date": exp,
            "active_ingredient": active,
            "image": img
        },
        "verification": verification
    })


@app.route('/api/whatsapp/push-imd-alert', methods=['POST'])
def whatsapp_push_imd():
    profile = get_farmer_profile()
    dist_name = profile.get('district', 'raisen').capitalize()
    v_name = profile.get('village', 'बरखेड़ी')
    
    calamity = trigger_calamity(profile.get('district', 'raisen'), 'अतिवृष्टि एवं जलभराव (IMD मौसम चेतावनी)', 'मौसम विभाग द्वारा भारी वर्षा का रेड अलर्ट जारी।')
    
    history = load_chat_history()
    now_time = datetime.datetime.now().strftime("%I:%M %p")
    alert_msg = {
        "id": f"msg_imd_{len(history)+1}",
        "sender": "bot",
        "text": f"🚨 *IMD मौसम विभाग आपातकालीन अलर्ट!* 🚨\n\nस्थान: *{v_name}, {dist_name}*\n⚠️ *चेतावनी:* आपके क्षेत्र में अगले 24 घंटे में मूसलाधार वर्षा / जलभराव की उच्च आशंका है।\n\n⏱️ *72-घंटे की PMFBY दावा विंडो शुरू हो चुकी है!*\nयदि फसल में पानी भरता है, तो 72 घंटे के भीतर नुकसान की सूचना दर्ज करें।\n\n👇 अभी दावा प्रपत्र तैयार करने हेतु '2' दबाएं या नीचे दिए गए बटन पर टैप करें:",
        "badge": "IMD रेड अलर्ट",
        "quick_replies": ["2. नुकसान दर्ज करें", "दावा पर्ची देखें", "मौसम स्थिति"],
        "timestamp": now_time
    }
    history.append(alert_msg)
    save_chat_history(history)
    return jsonify({"success": True, "alert": alert_msg, "calamity": calamity})


@app.route('/api/whatsapp/reset', methods=['POST'])
def whatsapp_reset_endpoint():
    save_chat_history([])
    process_farmer_message("नमस्ते")
    return jsonify({"success": True, "history": load_chat_history()})


@app.route('/api/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Real WhatsApp Webhook compatible with Twilio and Meta WhatsApp Cloud API."""
    # Meta webhook verification handshake
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token:
            return challenge or "OK", 200
        return jsonify({"status": "KhetProof WhatsApp Webhook Active", "ready": True}), 200

    form_data = request.form.to_dict() if request.form else None
    payload = request.json if request.is_json else None
    
    result = handle_inbound_webhook(payload, form_data)
    
    if form_data and 'From' in form_data:
        return Response(result['twiml'], mimetype='application/xml')
    return jsonify({"status": "success", "response": result})


@app.route('/api/whatsapp/config', methods=['GET'])
def whatsapp_config_endpoint():
    """Returns connection details, direct links, and webhook setup for real phones."""
    ip = get_lan_ip()
    dossier = generate_claim_dossier()
    legal = generate_dealer_legal_notice()
    return jsonify({
        "direct_wa_share_claim": dossier['whatsapp_share_url'],
        "direct_wa_share_legal": legal['whatsapp_share_url'],
        "webhook_endpoint": f"http://{ip}:5000/api/whatsapp/webhook",
        "twilio_instructions": "Twilio Console -> WhatsApp Sandbox Settings -> When a message comes in: POST to this webhook URL",
        "meta_verify_token": "khetproof_mp_farmer_token_2026",
        "ready": True
    })


@app.route('/api/voice-extract', methods=['POST'])
def voice_extract_endpoint():
    """Extracts claim/calamity details from spoken Hindi voice recognition text."""
    data = request.json or {}
    text = data.get('speech_text', '').strip()
    profile = get_farmer_profile()
    dist_id = profile.get('district', 'dewas')
    
    text_lower = text.lower()
    calamity_type = "अतिवृष्टि एवं जलभराव (Heavy Rain / Waterlogging)"
    if "ओला" in text_lower or "ओले" in text_lower:
        calamity_type = "ओलावृष्टि (Hailstorm)"
    elif "दवा" in text_lower or "खरपतवार" in text_lower or "झुलस" in text_lower:
        calamity_type = "अमानक रसायन से फसल क्षति (Chemical Burn)"
    elif "सूखा" in text_lower or "बारिश नहीं" in text_lower:
        calamity_type = "दीर्घकालिक सूखा (Severe Drought)"
    elif "कीट" in text_lower or "इल्ली" in text_lower:
        calamity_type = "कीट व्याधि प्रकोप (Pest Infestation)"
        
    crop = profile.get('crop', 'सोयाबीन JS-2034')
    if "सोयाबीन" in text:
        crop = "सोयाबीन (Soybean)"
    elif "गेहूं" in text:
        crop = "गेहूं (Wheat)"
    elif "चना" in text:
        crop = "चना (Gram)"
    elif "मक्का" in text:
        crop = "मक्का (Maize)"
        
    est_loss = 65
    if any(w in text_lower for w in ["पूरी", "100", "सब कुछ", "बर्बाद"]):
        est_loss = 90
    elif any(w in text_lower for w in ["आधा", "50", "काफी"]):
        est_loss = 50
    elif any(w in text_lower for w in ["थोड़ा", "हल्का", "20", "25"]):
        est_loss = 25
        
    auto_trigger = data.get('auto_trigger', True)
    calamity_state = None
    if auto_trigger:
        calamity_state = trigger_calamity(dist_id, calamity_type, f"वॉयस रिपोर्ट: {text}", crop)
        
    return jsonify({
        "success": True,
        "extracted": {
            "transcript": text,
            "calamity_type": calamity_type,
            "crop": crop,
            "estimated_loss_percent": est_loss,
            "timeframe": "पिछले 24 घंटे (वैध 72-घंटे अवधि)"
        },
        "calamity_state": calamity_state
    })


@app.route('/api/legal-notice/dealer', methods=['GET', 'POST'])
def dealer_notice_endpoint():
    """Generates official legal notice under Insecticides Act 1968."""
    input_id = request.args.get('input_id')
    if request.method == 'POST' and request.json:
        input_id = request.json.get('input_id')
    notice = generate_dealer_legal_notice(input_id)
    return jsonify(notice)


@app.route('/api/sync-offline', methods=['POST'])
def sync_offline_endpoint():
    """Receives offline-captured proofs when farmer returns to network coverage."""
    data = request.json or {}
    offline_inputs = data.get('inputs', [])
    offline_calamity = data.get('calamity')
    
    synced_inputs_count = 0
    if offline_inputs:
        existing_inputs = get_saved_inputs()
        for item in offline_inputs:
            if not any(e.get('id') == item.get('id') for e in existing_inputs):
                existing_inputs.insert(0, item)
                synced_inputs_count += 1
        save_saved_inputs(existing_inputs)
        
    if offline_calamity:
        profile = get_farmer_profile()
        dist_id = offline_calamity.get('district') or profile.get('district', 'dewas')
        c_type = offline_calamity.get('calamity_type', 'अतिवृष्टि एवं जलभराव')
        notes = offline_calamity.get('notes', 'फील्ड ऑफलाइन मोड से सिंक किया गया')
        crop = offline_calamity.get('crop') or profile.get('crop', 'सोयाबीन')
        trigger_calamity(dist_id, c_type, notes, crop)
        
    return jsonify({
        "success": True,
        "synced_inputs": synced_inputs_count,
        "calamity_active": bool(offline_calamity),
        "message": f"{synced_inputs_count} साक्ष्य सफलतापूर्वक सर्वर पर सिंक हुए।"
    })


if __name__ == '__main__':
    print("[KhetProof] Copilot Server Starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

