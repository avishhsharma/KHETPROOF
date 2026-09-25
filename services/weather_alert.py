import datetime
import json
import os
import requests

import tempfile

CALAMITY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'calamity_state.json')
TMP_CALAMITY_FILE = os.path.join(tempfile.gettempdir(), 'khetproof_calamity_state.json')
MP_DISTRICTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'mp_districts.json')
LEGACY_DISTRICTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'icar_biostimulants.json')

_calamity_state_mem = None


def get_all_districts():
    if os.path.exists(MP_DISTRICTS_FILE):
        try:
            with open(MP_DISTRICTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def get_district_info(district_id="raisen"):
    districts = get_all_districts()
    for d in districts:
        if d.get("id") == district_id:
            return d
    return {
        "id": "raisen",
        "name_hi": "रायसेन (Raisen)",
        "name_en": "Raisen",
        "lat": 23.3315,
        "lon": 77.7818,
        "insurance_company": "Agriculture Insurance Company of India (AIC)",
        "krishi_officer": "उप संचालक कृषि, रायसेन (07482-222450)",
        "toll_free": "14447"
    }

GEOCODE_CACHE = {
    "dewas": (22.9676, 76.0534),
    "sonkatch": (22.9772, 76.3686),
    "सोनकच्छ": (22.9772, 76.3686),
    "berakhedi": (22.9640, 76.3380),
    "बेड़ाखेड़ी": (22.9640, 76.3380),
    "बेरखेड़ी": (22.9640, 76.3380),
    "raisen": (23.3315, 77.7818),
    "gairatganj": (23.4020, 78.1050),
    "गैरतगंज": (23.4020, 78.1050),
    "vidisha": (23.5251, 77.8081),
    "sehore": (23.2030, 77.0844),
    "ujjain": (23.1765, 75.7885),
    "indore": (22.7196, 75.8577),
}

def resolve_location_coordinates(district_id="dewas", tehsil=None, village=None, lat=None, lon=None):
    """Resolves latitude and longitude for any village, tehsil, or district in Madhya Pradesh."""
    if lat and lon:
        try:
            return float(lat), float(lon)
        except Exception:
            pass

    # 1. Check local cache
    v_clean = (village or "").split('/')[0].split('(')[0].strip().lower()
    if v_clean in GEOCODE_CACHE:
        return GEOCODE_CACHE[v_clean]

    t_clean = (tehsil or "").split('(')[0].strip().lower()
    if t_clean in GEOCODE_CACHE:
        return GEOCODE_CACHE[t_clean]

    # 2. Try Open-Meteo Geocoding API for village or tehsil in MP
    for term in [v_clean, t_clean]:
        if term and len(term) >= 3 and term not in ["ग्राम केंद्र", "सदर तहसील", "n/a"]:
            try:
                g_url = f"https://geocoding-api.open-meteo.com/v1/search?name={term}&count=3&language=en&format=json"
                g_resp = requests.get(g_url, timeout=2.5)
                if g_resp.status_code == 200:
                    results = g_resp.json().get("results", [])
                    for r in results:
                        if r.get("admin1") == "Madhya Pradesh" or "Dewas" in r.get("admin2", "") or "Dewas" in r.get("name", ""):
                            coords = (float(r["latitude"]), float(r["longitude"]))
                            GEOCODE_CACHE[term] = coords
                            return coords
                    if results:
                        coords = (float(results[0]["latitude"]), float(results[0]["longitude"]))
                        GEOCODE_CACHE[term] = coords
                        return coords
            except Exception:
                pass

    # 3. Fallback to district coordinates
    dist = get_district_info(district_id)
    return dist.get("lat", 22.9676), dist.get("lon", 76.0534)


def get_weather_desc_hi(wcode, precip):
    if wcode == 0:
        return "साफ आसमान / धूप (Clear Sky)"
    elif wcode in [1, 2]:
        return "आंशिक रूप से बादल (Partly Cloudy)"
    elif wcode == 3:
        return "घने बादल छाए हैं (Overcast)"
    elif wcode in [45, 48]:
        return "सुबह का कोहरा व धुंध (Fog / Mist)"
    elif wcode in [51, 53, 55]:
        return "हल्की बूंदाबांदी (Light Drizzle)"
    elif wcode in [61, 63]:
        return "मध्यम वर्षा (Moderate Rain)"
    elif wcode == 65:
        return "मूसलाधार वर्षा (Heavy Rain)"
    elif wcode in [71, 73, 75]:
        return "ओलावृष्टि / बर्फबारी (Hailstorm)"
    elif wcode in [80, 81, 82]:
        return "तेज वर्षा बौछारें (Heavy Showers)"
    elif wcode in [95, 96, 99]:
        return "गरज-चमक के साथ आंधी-तूफान (Thunderstorm)"
    elif precip > 0:
        return f"वर्षा जारी ({precip} मिमी)"
    return "सामान्य मौसम (Fair Weather)"


def generate_agri_weather_advisory(humidity, precip, wind, rain_prob, temp):
    """Generates genuine, practical agricultural advisories based on live weather readings."""
    if precip >= 25 or rain_prob >= 65:
        return {
            "type": "danger",
            "text": "🚨 भारी वर्षा की चेतावनी: कीटनाशक, खरपतवारनाशक अथवा यूरिया का छिड़काव तुरंत रोकें। खेत से जल निकासी की व्यवस्था करें।"
        }
    elif humidity >= 85:
        return {
            "type": "warning",
            "text": f"⚠️ उच्च आर्द्रता ({humidity}%): सोयाबीन में एंथ्रेक्नोज (फली झुलसा) व इल्ली संक्रमण का खतरा। मौसम खुलते ही कवकनाशी का छिड़काव करें।"
        }
    elif wind >= 18:
        return {
            "type": "warning",
            "text": f"⚠️ तेज हवा ({wind} km/h): स्प्रेयर से रासायनिक छिड़काव न करें, हवा से रसायन उड़कर पास की फसलों को नुकसान पहुंचा सकता है।"
        }
    elif rain_prob <= 20 and wind < 12:
        return {
            "type": "success",
            "text": "✅ कृषि कार्य हेतु उत्तम समय: मौसम साफ व हवा मंद है। खरपतवारनाशक, पोषक तत्व व कीटनाशक छिड़काव के लिए अनुकूल परिस्थिति है।"
        }
    else:
        return {
            "type": "info",
            "text": f"🌦️ आंशिक बादल व {rain_prob}% वर्षा संभावना: खेत में नमी का स्तर देखकर ही हल्की सिंचाई अथवा रासायनिक खाद का प्रयोग करें।"
        }


def fetch_live_weather(district_id="dewas", tehsil=None, village=None, lat=None, lon=None):
    dist = get_district_info(district_id)
    final_lat, final_lon = resolve_location_coordinates(district_id, tehsil, village, lat, lon)

    # Build clear hierarchical location string
    loc_parts = []
    if village and village != 'ग्राम केंद्र':
        loc_parts.append(village.split('/')[0].split('(')[0].strip())
    if tehsil and tehsil != 'सदर तहसील':
        loc_parts.append(tehsil.split('(')[0].strip())
    loc_parts.append(dist.get("name_hi", district_id.capitalize()).split('(')[0].strip())
    display_location = ", ".join(loc_parts)

    now_ist = datetime.datetime.now()
    time_str = now_ist.strftime("%I:%M %p, %d %b %Y")

    # Try calling Open-Meteo Live API with exact coordinates
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={final_lat}&longitude={final_lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max"
            f"&timezone=Asia%2FKolkata"
        )
        resp = requests.get(url, timeout=4.0)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            daily = data.get("daily", {})

            temp = curr.get("temperature_2m", 24.2)
            app_temp = curr.get("apparent_temperature", temp)
            humidity = curr.get("relative_humidity_2m", 82)
            precip = curr.get("precipitation", 0.0)
            wind = curr.get("wind_speed_10m", 4.5)
            wcode = curr.get("weather_code", 1)

            # Daily forecast
            rain_prob_today = 0
            if daily.get("precipitation_probability_max"):
                rain_prob_today = daily["precipitation_probability_max"][0]
            temp_max = daily.get("temperature_2m_max", [30.0])[0]
            temp_min = daily.get("temperature_2m_min", [22.0])[0]

            # 3-Day Forecast Summary
            forecast_3day = []
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            rain_probs = daily.get("precipitation_probability_max", [])
            day_labels = ["आज (Today)", "कल (Tomorrow)", "परसों"]

            for i in range(min(3, len(dates))):
                forecast_3day.append({
                    "day": day_labels[i] if i < len(day_labels) else dates[i],
                    "date": dates[i],
                    "max_temp": f"{max_temps[i]}°C" if i < len(max_temps) else "--",
                    "min_temp": f"{min_temps[i]}°C" if i < len(min_temps) else "--",
                    "rain_prob": f"{rain_probs[i]}%" if i < len(rain_probs) else "0%"
                })

            wdesc = get_weather_desc_hi(wcode, precip)
            advisory = generate_agri_weather_advisory(humidity, precip, wind, rain_prob_today, temp)

            is_rainy = precip > 0 or wcode in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]
            calamity_risk = "HIGH" if precip > 40 or wcode in [65, 82, 95, 96, 99] else ("MODERATE" if is_rainy or rain_prob_today > 50 else "LOW")

            return {
                "source": "Open-Meteo Live Hyperlocal API",
                "location": display_location,
                "district": dist["name_hi"],
                "tehsil": tehsil or "सोनकच्छ",
                "village": village or "बेड़ाखेड़ी",
                "timestamp_ist": time_str,
                "temperature": f"{temp}°C",
                "apparent_temp": f"{app_temp}°C",
                "temp_max": f"{temp_max}°C",
                "temp_min": f"{temp_min}°C",
                "humidity": f"{humidity}%",
                "precipitation_mm": precip,
                "rain_probability": f"{rain_prob_today}%",
                "wind_speed": f"{wind} km/h",
                "weather_code": wcode,
                "description_hi": wdesc,
                "advisory_hi": advisory["text"],
                "advisory_type": advisory["type"],
                "calamity_risk": calamity_risk,
                "forecast_3day": forecast_3day,
                "lat": round(final_lat, 4),
                "lon": round(final_lon, 4)
            }
    except Exception as e:
        pass

    # Fallback with realistic time and dynamic location
    return {
        "source": "Simulated Weather (MP Agri-Station)",
        "location": display_location,
        "district": dist["name_hi"],
        "tehsil": tehsil or "सोनकच्छ",
        "village": village or "बेड़ाखेड़ी",
        "timestamp_ist": time_str,
        "temperature": "24.5°C",
        "apparent_temp": "28.0°C",
        "temp_max": "30.5°C",
        "temp_min": "22.8°C",
        "humidity": "88%",
        "precipitation_mm": 0.0,
        "rain_probability": "15%",
        "wind_speed": "6 km/h",
        "weather_code": 1,
        "description_hi": "साफ आसमान व धूप (Clear Sky)",
        "advisory_hi": "✅ अनुकूल मौसम: आसमान साफ व हवा शांत है। कृषि रसायनों के छिड़काव हेतु उपयुक्त समय है।",
        "advisory_type": "success",
        "calamity_risk": "LOW",
        "forecast_3day": [
            {"day": "आज", "max_temp": "31°C", "min_temp": "23°C", "rain_prob": "15%"},
            {"day": "कल", "max_temp": "30°C", "min_temp": "22°C", "rain_prob": "20%"},
            {"day": "परसों", "max_temp": "31°C", "min_temp": "23°C", "rain_prob": "10%"}
        ],
        "lat": round(final_lat, 4),
        "lon": round(final_lon, 4)
    }


def get_calamity_state():
    global _calamity_state_mem
    if _calamity_state_mem is not None:
        state = dict(_calamity_state_mem)
    else:
        state = {"active": False}
        for target in (TMP_CALAMITY_FILE, CALAMITY_FILE):
            if os.path.exists(target):
                try:
                    with open(target, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        _calamity_state_mem = dict(state)
                        break
                except Exception:
                    pass

    if state.get("active"):
        # Calculate time left
        try:
            started = datetime.datetime.fromisoformat(state["started_at"])
            now = datetime.datetime.now(datetime.timezone.utc).astimezone()
            
            # Normalize started to aware datetime if needed
            if started.tzinfo is None:
                started = started.replace(tzinfo=now.tzinfo)

            deadline = started + datetime.timedelta(hours=72)
            time_left = deadline - now
            total_seconds_left = max(0, int(time_left.total_seconds()))
            
            hours = total_seconds_left // 3600
            minutes = (total_seconds_left % 3600) // 60
            seconds = total_seconds_left % 60

            state["deadline_72h"] = deadline.isoformat()
            state["seconds_left"] = total_seconds_left
            state["hours_left"] = hours
            state["minutes_left"] = minutes
            state["seconds_rem"] = seconds
            state["is_expired"] = (total_seconds_left == 0)
            
            if total_seconds_left == 0:
                state["urgency_status"] = "EXPIRED"
                state["urgency_badge_hi"] = "❌ 72 घंटे की समय-सीमा समाप्त"
                state["urgency_color"] = "red"
            elif hours < 24:
                state["urgency_status"] = "CRITICAL"
                state["urgency_badge_hi"] = f"🚨 आपातकाल: केवल {hours} घंटे {minutes} मिनट बचे!"
                state["urgency_color"] = "red"
            elif hours < 48:
                state["urgency_status"] = "WARNING"
                state["urgency_badge_hi"] = f"⚠️ ध्यान दें: {hours} घंटे शेष"
                state["urgency_color"] = "amber"
            else:
                state["urgency_status"] = "ACTIVE"
                state["urgency_badge_hi"] = f"⏱️ 72-घंटे विंडो चालू: {hours} घंटे बाकी"
                state["urgency_color"] = "emerald"

        except Exception as ex:
            state["seconds_left"] = 72 * 3600
            state["hours_left"] = 72
            state["minutes_left"] = 0
            state["urgency_badge_hi"] = "⏱️ 72-घंटे विंडो चालू"
            state["urgency_color"] = "emerald"

    return state

def trigger_calamity(district_id, calamity_type, notes="", crop="Soybean (सोयाबीन JS-2034)"):
    global _calamity_state_mem
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    deadline = now + datetime.timedelta(hours=72)
    
    state = {
        "active": True,
        "calamity_id": f"CLM-{now.strftime('%Y%m%d-%H%M')}",
        "district": district_id,
        "calamity_type": calamity_type,
        "triggered_by": "किसान द्वारा सीधा दर्ज / मौसम अलार्म",
        "started_at": now.isoformat(),
        "deadline_72h": deadline.isoformat(),
        "affected_crop": crop,
        "estimated_loss_percent": 60,
        "field_photo": "/static/images/sample_waterlogged_field.svg",
        "loss_status": "INTIMATION_PENDING",
        "notes": notes or "फसल में प्राकृतिक आपदा/अमानक रसायन से व्यापक नुकसान।"
    }
    
    _calamity_state_mem = dict(state)
    try:
        with open(CALAMITY_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        try:
            with open(TMP_CALAMITY_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        
    return get_calamity_state()

def resolve_calamity(claim_ref="CLAIM-COMPLETED"):
    global _calamity_state_mem
    state = get_calamity_state()
    state["active"] = False
    state["loss_status"] = "INTIMATION_SUBMITTED"
    state["claim_reference_no"] = claim_ref
    state["resolved_at"] = datetime.datetime.now().isoformat()
    
    _calamity_state_mem = dict(state)
    try:
        with open(CALAMITY_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        try:
            with open(TMP_CALAMITY_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        
    return state

