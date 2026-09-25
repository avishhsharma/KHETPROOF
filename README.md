# 🌾 खेतप्रूफ (KhetProof) - Farmer Claim & Agri-Input Proof Copilot

> **"72 घंटे की समय-सीमा में बीमा दावा और असली-नकली खाद-दवा का पक्का डिजिटल सबूत"**

**KhetProof** is a Hindi-first mobile copilot and WhatsApp assistant designed to eliminate the two biggest financial risks faced by Indian farmers (with specialized context for Madhya Pradesh, which accounts for ~14% of India's insured sum under PMFBY):

1. **The 72-Hour PMFBY Insurance Claim Trap**: Under PMFBY Operational Guidelines (Section 21.4), localized losses (waterlogging, hailstorms, cloudbursts) MUST be reported within 72 hours. Missing this window or lacking timestamped, geotagged proof is the #1 reason crop insurance claims are rejected.
2. **Counterfeit Agri-Inputs (Weedicides & Biostimulants)**: Recent cases in Raisen and Vidisha saw entire soybean crops scorched by spurious weedicides. Out of ~30,000 biostimulants on the Indian market, only ~600 are verified under ICAR / FCO Schedule VI. Farmers lack the bill, batch number, and geo-proof needed to demand compensation under the Insecticides Act.

---

## 🚀 Key Features

### 1. ⏱️ 72-Hour Calamity Countdown & Weather Sentinel
- Ticking countdown timer (`68h : 24m remaining`) triggered by weather anomalies (heavy rain >40mm, hailstorm) or manual farmer reporting.
- Status classification: **Golden Period (0-24h)**, **Urgent (24-48h)**, **Critical (48-72h)**, and **Expired**.
- Automatically captures village, khasra number, crop, and live weather conditions.

### 2. 📦 Agri-Input Security Vault (ICAR & CIBRC Verifier)
- Saves photo of chemical bottle/seed bag, dealer tax invoice, and batch number with GPS coordinates.
- **Instant Verifier**: Type any chemical or biostimulant to instantly cross-check:
  - ✅ **ICAR / CIBRC Verified**: e.g. IFFCO Sagarika, Pursuit (BASF), Targa Super.
  - 🚨 **Flagged Counterfeit Alert**: e.g. Spurious 2,4-D mixes seized in Raisen/Vidisha.
  - ⚠️ **Unverified Biostimulant Warning**: Flags products not listed in the ~600 verified Schedule-VI registry.

### 3. 📄 One-Tap Claim & Legal Complaint Dossier
- Generates official PMFBY Loss Intimation Form (प्रपत्र) addressed to the Senior Agriculture Development Officer (SADO), Insurance Company (AIC), and Toll-Free 14447.
- Embeds verified photos, GPS coordinates, weather readings, and dealer info.
- **1-Click WhatsApp Share**: Ready-to-send formatted text for SADO/RAEO and insurance surveyors.
- **Clean Print / PDF Layout**: Optimized for A4 printing.

### 4. 💬 WhatsApp Bot Simulator
- An embedded, fully interactive Hindi WhatsApp chat screen.
- Allows testing conversational flows with farmers (sending photos, quick replies, voice notes) without needing an expensive WhatsApp Business API number right away.

### 5. 🔊 Voice Guidance (बोलकर सुनें)
- Web Speech Synthesis in Hindi (`hi-IN`) to read alerts and instructions for farmers who struggle to read dense text in outdoor sunlight.

---

## 🧪 Testing with Your Dad & 10 Neighbours (Feedback Guide)

1. **Step 1**: Run `run.bat` or run `python app.py` and open `http://localhost:5000` on a mobile phone (connect to same Wi-Fi using your PC's IP, e.g. `http://192.168.1.X:5000`).
2. **Step 2 (The Purchase Flow)**: Hand them a fertilizer/weedicide bag. Ask them to tap **"दवा/बिल फोटो जोड़ें"**, take a photo, and observe the ICAR verification badge.
3. **Step 3 (The Calamity Flow)**: Tap **"फसल नुकसान रिपोर्ट (72h)"**, show them the 72-hour countdown clock, and ask: *"क्या यह टाइमर आपको याद दिलाएगा कि 3 दिन के अंदर दावा करना है?"*
4. **Step 4 (The WhatsApp Flow)**: Switch to the **"व्हाट्सएप बॉट"** tab. Have them type "1" or tap "नुकसान दर्ज करें".
5. **Step 5 (The Dossier)**: Tap **"WhatsApp पर शेयर"** to see the pre-formatted claim notice sent to their WhatsApp.

---

## 🛠️ How to Run

### Requirements
- Python 3.10+ (tested on Python 3.14)
- Flask & Requests (`pip install flask requests`)

### Start Server
```powershell
python app.py
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.

Or double-click `run.bat` on Windows.
