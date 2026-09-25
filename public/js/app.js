// KhetProof (खेतप्रूफ) - Farmer Claim & Proof Copilot Client Logic

let currentLang = 'hi';
let activeTab = 'tab-dashboard';
let timerInterval = null;
let calamitySecondsLeft = 68 * 3600 + 24 * 60 + 10;
let selectedBagPhoto = '/static/images/sample_sagarika.svg';

let allMpDistricts = [];
let currentProfile = {};
let currentDossier = null;
let activeScannedData = null;

const translations = {
  hi: {
    tagline: 'किसान दावा व इनपुट सुरक्षा साथी',
    voiceGuide: 'बोलकर सुनें',
    tabDashboard: 'डैशबोर्ड',
    tabVault: 'इनपुट वॉल्ट',
    tabLoss: '72h दावा',
    tabWhatsapp: 'WhatsApp',
    tabDossier: 'दावा पर्ची',
    vaultHeading: 'इनपुट सुरक्षा वॉल्ट (Agri-Input Vault)',
    quickClaimBtn: 'दावा पर्ची',
    remaining: 'बाकी'
  },
  en: {
    tagline: 'Farmer Claim & Input Proof Copilot',
    voiceGuide: 'Voice Assist',
    tabDashboard: 'Dashboard',
    tabVault: 'Input Vault',
    tabLoss: '72h Claim',
    tabWhatsapp: 'WhatsApp',
    tabDossier: 'Claim Slip',
    vaultHeading: 'Agri-Input Proof Vault',
    quickClaimBtn: 'Claim Slip',
    remaining: 'left'
  }
};

let activeDossierDoc = 'pmfby';
let speechRecognizer = null;
let isRecordingVoice = false;

document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  loadAllLocations();
  await loadProfile();
  await loadWeather();
  loadMandiRates();
  loadCropDoctor();
  loadOfficersDirectory();
  loadInputs();
  loadCalamityState();
  loadWhatsAppHistory();
  loadDossierData();
  loadDealerLegalNotice();
  startCountdownTicker();
  initPwaAndOffline();
  updateClaimCalculation();
});


// ==================== TAB SWITCHING ====================
function switchTab(tabId) {
  const tabs = ['tab-dashboard', 'tab-vault', 'tab-loss-reporter', 'tab-mandi-doctor', 'tab-whatsapp', 'tab-dossier'];
  tabs.forEach(id => {
    const el = document.getElementById(id);
    const navEl = document.getElementById('nav-' + id);
    const mobNavEl = document.getElementById('mob-nav-' + id);
    if (el) {
      if (id === tabId) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    }
    if (navEl) {
      if (id === tabId) {
        navEl.classList.add('active-tab');
      } else {
        navEl.classList.remove('active-tab');
      }
    }
    if (mobNavEl) {
      if (id === tabId) {
        mobNavEl.classList.add('text-emerald-700', 'font-black');
        mobNavEl.classList.remove('text-slate-500');
      } else {
        mobNavEl.classList.remove('text-emerald-700', 'font-black');
        mobNavEl.classList.add('text-slate-500');
      }
    }
  });

  activeTab = tabId;
  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (tabId === 'tab-whatsapp') {
    scrollWhatsAppToBottom();
  } else if (tabId === 'tab-dossier') {
    loadDossierData();
  } else if (tabId === 'tab-mandi-doctor') {
    loadMandiRates();
    loadCropDoctor();
  }
}

// ==================== LANGUAGE TOGGLE ====================
function toggleLanguage() {
  currentLang = currentLang === 'hi' ? 'en' : 'hi';
  document.getElementById('lang-label').innerText = currentLang === 'hi' ? 'ENG' : 'हिंदी';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[currentLang][key]) {
      el.innerText = translations[currentLang][key];
    }
  });

  showToast(currentLang === 'hi' ? 'भाषा: हिंदी चुनी गई' : 'Language: English selected');
}

// ==================== VOICE GUIDANCE (WEB SPEECH API) ====================
function speakText(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*_#`]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = currentLang === 'hi' ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  } else {
    showToast('स्पीच सिंथेसिस उपलब्ध नहीं है');
  }
}

function speakCurrentSummary() {
  const hrs = Math.floor(calamitySecondsLeft / 3600);
  const mins = Math.floor((calamitySecondsLeft % 3600) / 60);
  const dist = currentProfile.district_name_hi || 'रायसेन';
  const text = `खेतप्रूफ अलर्ट। ${dist} में मौसम अलर्ट दर्ज है। फसल नुकसान की सूचना देने के लिए 72 घंटे में से केवल ${hrs} घंटे और ${mins} मिनट बचे हैं। अपनी दावा पर्ची तत्काल निकालें।`;
  speakText(text);
}

function speakWhatsAppLastBot() {
  const botMsgs = document.querySelectorAll('.wa-bubble-bot');
  if (botMsgs.length > 0) {
    const lastMsg = botMsgs[botMsgs.length - 1].innerText;
    speakText(lastMsg);
  }
}

// ==================== 72-HOUR COUNTDOWN TICKER ====================
function startCountdownTicker() {
  if (timerInterval) clearInterval(timerInterval);

  timerInterval = setInterval(() => {
    if (calamitySecondsLeft > 0) {
      calamitySecondsLeft--;
      renderCountdownDisplays();
    } else {
      calamitySecondsLeft = 0;
      renderCountdownDisplays();
    }
  }, 1000);
}

function renderCountdownDisplays() {
  const hrs = Math.floor(calamitySecondsLeft / 3600);
  const mins = Math.floor((calamitySecondsLeft % 3600) / 60);
  const secs = calamitySecondsLeft % 60;

  const formatted = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  
  const elTop = document.getElementById('countdown-timer');
  const elDash = document.getElementById('dash-countdown');
  const elBig = document.getElementById('calamity-big-timer');

  if (elTop) elTop.innerText = formatted;
  if (elDash) elDash.innerText = `${hrs}h ${mins}m`;
  if (elBig) elBig.innerText = formatted;
}

// ==================== ALL 55 MP DISTRICTS & VILLAGE ENGINE ====================
async function loadAllLocations() {
  try {
    const res = await fetch('/api/locations');
    allMpDistricts = await res.json();
    populateDistrictsDropdown(allMpDistricts);
  } catch (err) {
    console.error('Failed to load locations', err);
  }
}

function populateDistrictsDropdown(districtsList) {
  const sel = document.getElementById('modal-select-district');
  if (!sel) return;

  const currentDistId = currentProfile.district || 'raisen';
  sel.innerHTML = '';

  districtsList.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d.id;
    opt.innerText = `${d.name_hi} [${d.division} संभाग]`;
    if (d.id === currentDistId) {
      opt.selected = true;
    }
    sel.appendChild(opt);
  });

  onDistrictChange(sel.value);
}

function filterDistrictsDropdown(query) {
  const q = (query || '').toLowerCase().trim();
  const filtered = allMpDistricts.filter(d => 
    d.name_hi.toLowerCase().includes(q) || 
    d.name_en.toLowerCase().includes(q) || 
    (d.division && d.division.toLowerCase().includes(q))
  );

  const sel = document.getElementById('modal-select-district');
  if (!sel) return;

  sel.innerHTML = '';
  filtered.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d.id;
    opt.innerText = `${d.name_hi} [${d.division} संभाग]`;
    sel.appendChild(opt);
  });

  if (filtered.length > 0) {
    onDistrictChange(filtered[0].id);
  }
}

function onDistrictChange(districtId) {
  const dist = allMpDistricts.find(d => d.id === districtId);
  if (!dist) return;

  // Update Tehsils
  const tehsilSel = document.getElementById('modal-select-tehsil');
  let selectedIdx = 0;
  if (tehsilSel) {
    tehsilSel.innerHTML = '';
    (dist.tehsils || []).forEach((t, idx) => {
      const opt = document.createElement('option');
      opt.value = idx;
      opt.innerText = t.name_hi || t.name_en;
      if (currentProfile.tehsil && (t.name_hi.includes(currentProfile.tehsil) || t.name_en.toLowerCase() === currentProfile.tehsil.toLowerCase())) {
        opt.selected = true;
        selectedIdx = idx;
      }
      tehsilSel.appendChild(opt);
    });
    onTehsilChange(selectedIdx);
  }

  // Update Intelligence Card
  const insEl = document.getElementById('modal-info-insurance');
  const krishiEl = document.getElementById('modal-info-krishi');
  const cropsEl = document.getElementById('modal-info-crops');

  if (insEl) insEl.innerText = dist.insurance_company || 'AIC of India';
  if (krishiEl) krishiEl.innerText = dist.krishi_officer || 'उप संचालक कृषि';
  if (cropsEl) cropsEl.innerText = (dist.major_crops || []).join(', ');
}

function onTehsilChange(tehsilIndex) {
  const distSel = document.getElementById('modal-select-district');
  const dist = allMpDistricts.find(d => d.id === distSel.value);
  if (!dist || !dist.tehsils) return;

  const tehsil = dist.tehsils[tehsilIndex];
  const villageSel = document.getElementById('modal-select-village');
  const customVillageInput = document.getElementById('modal-custom-village');
  if (!villageSel || !tehsil) return;

  villageSel.innerHTML = '<option value="">-- गाँव सूची में से चुनें (Select from list) --</option>';
  (tehsil.villages || []).forEach(v => {
    const opt = document.createElement('option');
    opt.value = v;
    opt.innerText = v;
    if (currentProfile.village && v.includes(currentProfile.village)) {
      opt.selected = true;
    }
    villageSel.appendChild(opt);
  });

  // If current profile has village set for this area, preserve it; do NOT auto-overwrite with villages[0]
  if (currentProfile.village && !customVillageInput.value) {
    customVillageInput.value = currentProfile.village;
  }
}

function onVillageChange(villageVal) {
  if (villageVal) {
    // Extract clean name before brackets if any, or keep full
    const cleanName = villageVal.split('(')[0].trim();
    document.getElementById('modal-custom-village').value = cleanName;
  }
}

function openLocationModal() {
  const modal = document.getElementById('modal-location-picker');
  modal.classList.remove('hidden');

  const currentDistId = currentProfile.district || 'raisen';
  const sel = document.getElementById('modal-select-district');
  if (sel && sel.value !== currentDistId) {
    sel.value = currentDistId;
    onDistrictChange(currentDistId);
  }
  if (currentProfile.village) {
    document.getElementById('modal-custom-village').value = currentProfile.village;
  }
}

function closeLocationModal() {
  document.getElementById('modal-location-picker').classList.add('hidden');
}

async function saveLocationSelection() {
  const distId = document.getElementById('modal-select-district').value;
  const tehsilIdx = document.getElementById('modal-select-tehsil').value;
  const dist = allMpDistricts.find(d => d.id === distId);

  let tehsilName = 'सदर तहसील';
  if (dist && dist.tehsils && dist.tehsils[tehsilIdx]) {
    tehsilName = dist.tehsils[tehsilIdx].name_hi || dist.tehsils[tehsilIdx].name_en;
  }

  const customVillage = document.getElementById('modal-custom-village').value.trim();
  const dropdownVillage = document.getElementById('modal-select-village').value;
  let chosenVillage = customVillage;
  if (!chosenVillage && dropdownVillage) {
    chosenVillage = dropdownVillage.split('(')[0].trim();
  }
  if (!chosenVillage) {
    chosenVillage = 'ग्राम केंद्र';
  }

  const payload = {
    district: distId,
    tehsil: tehsilName,
    village: chosenVillage,
    state: "Madhya Pradesh"
  };

  try {
    const res = await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      currentProfile = data.profile;
      closeLocationModal();
      
      const cleanDist = dist.name_hi.split(' ')[0];
      const cleanTehsil = tehsilName.split(' ')[0];
      const cleanVillage = chosenVillage.split(' ')[0].split('/')[0].trim();
      
      showToast(`✓ स्थान सहेजा गया: ${cleanDist} • ${cleanTehsil} • ${cleanVillage}`);
      
      // Update header label with all 3: District • Tehsil • Village
      const navLoc = document.getElementById('nav-location-label');
      if (navLoc) {
        navLoc.innerText = `${cleanDist} • ${cleanTehsil} • ${cleanVillage}`;
      }

      // Refresh data with newly chosen village / tehsil / district
      await loadProfile();
      await loadWeather(true);
      await loadMandiRates(true);
      loadDossierData();
    }
  } catch (err) {
    showToast('स्थान सहेजने में त्रुटि आई');
  }
}

// ==================== PROFILE & WEATHER ====================
async function loadProfile() {
  try {
    const res = await fetch('/api/profile');
    const p = await res.json();
    currentProfile = p || {};

    if (p) {
      if (document.getElementById('prof-name')) document.getElementById('prof-name').innerText = p.name || 'नागेश शर्मा (Nagesh Sharma)';
      if (document.getElementById('prof-crop')) document.getElementById('prof-crop').innerText = p.crop || 'सोयाबीन JS-2034';
      if (document.getElementById('prof-khasra')) document.getElementById('prof-khasra').innerText = p.khasra_no || '142/2';
      if (document.getElementById('prof-policy')) document.getElementById('prof-policy').innerText = p.pmfby_application_no || 'MP-PMFBY-2026-8942110';
      
      const vClean = p.village ? p.village.split('/')[0].split('(')[0].trim() : 'बेड़ाखेड़ी';
      const tClean = p.tehsil ? p.tehsil.split('(')[0].trim() : 'सोनकच्छ';
      const dClean = p.district_name_hi ? p.district_name_hi.split('(')[0].trim() : (p.district ? p.district.toUpperCase() : 'देवास');

      const locText = `${vClean}, ${tClean} (जिला: ${dClean}, म.प्र.)`;
      if (document.getElementById('prof-location')) document.getElementById('prof-location').innerText = locText;

      const navLoc = document.getElementById('nav-location-label');
      if (navLoc) {
        navLoc.innerText = `${dClean} • ${tClean} • ${vClean}`;
      }

      // Update Top Banner location
      const bannerLoc = document.getElementById('banner-loc-name');
      if (bannerLoc) {
        bannerLoc.innerText = `${vClean} (${dClean})`;
      }

      // Update Calamity Header Subtitle
      if (document.getElementById('calamity-village-b')) {
        document.getElementById('calamity-village-b').innerText = `${vClean} (${tClean}, ${dClean})`;
      }
      if (document.getElementById('calamity-crop-b')) {
        document.getElementById('calamity-crop-b').innerText = p.crop || 'सोयाबीन JS-2034';
      }

      // Update loss GPS field default if present
      const gpsInput = document.getElementById('loss-gps');
      if (gpsInput && !gpsInput.value.includes(vClean)) {
        gpsInput.value = `22°57'50.4"N 76°20'16.8"E (${vClean}, ${dClean})`;
      }
    }
    return currentProfile;
  } catch (err) {
    console.error('Failed to load profile', err);
    return null;
  }
}

async function loadWeather(forceRefresh = false) {
  const refreshBtn = document.getElementById('weather-refresh-btn');
  if (refreshBtn) {
    refreshBtn.classList.add('animate-spin');
  }

  try {
    // If profile not loaded yet, fetch it first
    if (!currentProfile || !currentProfile.district) {
      await loadProfile();
    }

    const distId = currentProfile.district || 'dewas';
    const tehsil = currentProfile.tehsil || 'सोनकच्छ';
    const village = currentProfile.village || 'बेड़ाखेड़ी';

    const params = new URLSearchParams({
      district: distId,
      tehsil: tehsil,
      village: village
    });
    if (forceRefresh) params.set('refresh', '1');

    const res = await fetch(`/api/weather?${params.toString()}`);
    const w = await res.json();
    if (w) {
      // 1. Location & Source
      const elLoc = document.getElementById('weather-location-name');
      if (elLoc) elLoc.innerText = w.location || `${village}, ${tehsil} (${distId})`;

      const elSource = document.getElementById('weather-source');
      if (elSource) elSource.innerText = w.source || 'Open-Meteo सैटेलाइट सिंक';

      // 2. Timestamp & Coordinates
      const elTime = document.getElementById('weather-timestamp');
      if (elTime) elTime.innerHTML = `<i data-lucide="clock" class="w-3 h-3 inline mr-1"></i> समय: ${w.timestamp_ist || 'लाइव'}`;

      const elCoords = document.getElementById('weather-coords');
      if (elCoords && w.lat && w.lon) {
        elCoords.innerText = `${w.lat}°N, ${w.lon}°E`;
      }

      // 3. Temperatures & Description
      const elTemp = document.getElementById('weather-temp');
      if (elTemp) elTemp.innerText = w.temperature || '--°C';

      const elApparent = document.getElementById('weather-apparent');
      if (elApparent) elApparent.innerText = `(महसूस: ${w.apparent_temp || w.temperature})`;

      const elRange = document.getElementById('weather-temp-range');
      if (elRange) elRange.innerText = `${w.temp_max || '--'} / ${w.temp_min || '--'}`;

      const elDesc = document.getElementById('weather-desc');
      if (elDesc) elDesc.innerText = w.description_hi || 'सामान्य मौसम';

      // 4. Meteorological Metrics
      const elHum = document.getElementById('weather-humidity');
      if (elHum) elHum.innerText = w.humidity || '--%';

      const elRainStat = document.getElementById('weather-rain-stat');
      if (elRainStat) elRainStat.innerText = `${w.precipitation_mm}mm (${w.rain_probability || '0%'})`;

      const elWind = document.getElementById('weather-wind');
      if (elWind) elWind.innerText = w.wind_speed || '-- km/h';

      // 5. Calamity Risk Badge
      const elRisk = document.getElementById('weather-risk-badge');
      if (elRisk) {
        if (w.calamity_risk === 'HIGH') {
          elRisk.className = 'text-[11px] font-bold px-2.5 py-1 rounded-full bg-red-100 text-red-800 border border-red-300 animate-pulse';
          elRisk.innerText = '🚨 अतिवृष्टि जोखिम';
        } else if (w.calamity_risk === 'MODERATE') {
          elRisk.className = 'text-[11px] font-bold px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 border border-amber-300';
          elRisk.innerText = '⚠️ मध्यम वर्षा जोखिम';
        } else {
          elRisk.className = 'text-[11px] font-bold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200';
          elRisk.innerText = '✅ सामान्य मौसम';
        }
      }

      // 6. Actionable Agricultural Advisory
      const elAdvBox = document.getElementById('weather-advisory-box');
      const elAdvText = document.getElementById('weather-advisory-text');
      if (elAdvText && w.advisory_hi) {
        elAdvText.innerText = w.advisory_hi;
      }
      if (elAdvBox && w.advisory_type) {
        if (w.advisory_type === 'danger') {
          elAdvBox.className = 'mt-3 p-2.5 rounded-xl bg-red-50 border border-red-200 text-xs transition-colors';
        } else if (w.advisory_type === 'warning') {
          elAdvBox.className = 'mt-3 p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-xs transition-colors';
        } else if (w.advisory_type === 'success') {
          elAdvBox.className = 'mt-3 p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs transition-colors';
        } else {
          elAdvBox.className = 'mt-3 p-2.5 rounded-xl bg-sky-50 border border-sky-200 text-xs transition-colors';
        }
      }

      // 7. 3-Day Forecast Strip
      const elStrip = document.getElementById('weather-3day-strip');
      if (elStrip && w.forecast_3day && w.forecast_3day.length > 0) {
        elStrip.innerHTML = w.forecast_3day.map(d => `
          <div class="bg-slate-50 hover:bg-slate-100 transition p-1.5 rounded-xl border border-slate-200/70 text-center">
            <span class="text-[10px] font-bold text-slate-600 block truncate">${d.day.split(' ')[0]}</span>
            <div class="text-[11px] font-black text-slate-800 mt-0.5">${d.max_temp}</div>
            <div class="text-[9px] text-slate-400">${d.min_temp}</div>
            <div class="text-[10px] font-bold mt-1 text-sky-600 flex items-center justify-center gap-0.5">
              <span>🌧️</span>${d.rain_prob}
            </div>
          </div>
        `).join('');
      }

      // 8. Top Banner Subtitle Sync
      const bannerLoc = document.getElementById('banner-loc-name');
      if (bannerLoc) {
        const vClean = (w.village || village).split('/')[0].trim();
        const dClean = (w.district || distId).split('(')[0].trim();
        bannerLoc.innerText = `${vClean} (${dClean})`;
      }

      // Re-render Lucide icons
      if (window.lucide) {
        lucide.createIcons();
      }

      if (forceRefresh) {
        showToast(`✓ ${w.location || village} का लाइव मौसम अपडेट हुआ (${w.temperature})`);
      }
    }
  } catch (err) {
    console.error('Failed to load weather', err);
    if (forceRefresh) {
      showToast('मौसम आंकड़े प्राप्त करने में विफल');
    }
  } finally {
    if (refreshBtn) {
      setTimeout(() => refreshBtn.classList.remove('animate-spin'), 400);
    }
  }
}

async function loadCalamityState() {
  try {
    const res = await fetch('/api/calamity/status');
    const c = await res.json();
    if (c && c.active) {
      if (c.seconds_left !== undefined) {
        calamitySecondsLeft = c.seconds_left;
      }
      document.getElementById('calamity-title-full').innerText = c.calamity_type || 'अतिवृष्टि एवं जलभराव';
      renderCountdownDisplays();
    }
  } catch (err) {
    console.error('Failed to load calamity state', err);
  }
}

// ==================== DISPUTE-PROOF CANVAS GEO-WATERMARKER ====================
function burnGeoWatermark(imageSrc, callback) {
  const canvas = document.getElementById('watermark-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const img = new Image();
  img.crossOrigin = 'anonymous';

  img.onload = function() {
    canvas.width = img.width || 800;
    canvas.height = img.height || 600;

    // 1. Draw original photo
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    // 2. Overlay bottom legal banner bar
    const barHeight = Math.max(90, Math.floor(canvas.height * 0.18));
    ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
    ctx.fillRect(0, canvas.height - barHeight, canvas.width, barHeight);

    // 3. Top accent line
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(0, canvas.height - barHeight, canvas.width, 4);

    // 4. Red REC / VERIFIED Badge
    ctx.fillStyle = '#dc2626';
    ctx.beginPath();
    ctx.roundRect(16, canvas.height - barHeight + 14, 110, 24, 6);
    ctx.fill();

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px sans-serif';
    ctx.fillText('● PMFBY साक्ष्य', 24, canvas.height - barHeight + 30);

    // 5. Legal metadata texts
    const now = new Date();
    const dateStr = now.toLocaleDateString('en-GB') + ' ' + now.toLocaleTimeString('en-GB') + ' IST';
    const distText = (currentProfile.district || 'Raisen').toUpperCase();
    const villageText = currentProfile.village || 'बरखेड़ी';
    const khasraText = currentProfile.khasra_no || '142/2';
    const farmerName = currentProfile.name || 'नागेश शर्मा';
    const gpsCoords = document.getElementById('loss-gps') ? document.getElementById('loss-gps').value : '23.3315°N, 77.7818°E';

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 14px sans-serif';
    ctx.fillText(`खेतप्रूफ डिजिटल भू-साक्ष्य | कृषक: ${farmerName} | खसरा: ${khasraText}`, 140, canvas.height - barHeight + 31);

    ctx.fillStyle = '#38bdf8';
    ctx.font = 'bold 12px monospace';
    ctx.fillText(`GPS: ${gpsCoords} | गाँव: ${villageText}, जिला: ${distText} (म.प्र.)`, 16, canvas.height - barHeight + 58);

    ctx.fillStyle = '#cbd5e1';
    ctx.font = '11px monospace';
    ctx.fillText(`तारीख व समय: ${dateStr} | SHA-256 डिजिटल वाटरमार्क सत्यापित`, 16, canvas.height - barHeight + 77);

    const watermarkedDataUrl = canvas.toDataURL('image/jpeg', 0.92);
    if (callback) callback(watermarkedDataUrl);
  };

  img.src = imageSrc;
}

function burnGeoWatermarkOnCurrentPhoto() {
  const currentImg = document.getElementById('loss-photo-preview');
  if (!currentImg) return;

  burnGeoWatermark(currentImg.src, (newUrl) => {
    currentImg.src = newUrl;
    showToast('✓ अमान्य-रोधी GPS वाटरमार्क फोटो पर सफलतापूर्वक स्टैम्प हुआ!');
  });
}

function previewLossPhoto(e) {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(evt) {
      burnGeoWatermark(evt.target.result, (watermarkedUrl) => {
        document.getElementById('loss-photo-preview').src = watermarkedUrl;
        showToast('✓ नया फोटो GPS व समय वाटरमार्क के साथ लोड हुआ');
      });
    };
    reader.readAsDataURL(file);
  }
}

function refreshGPS() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => {
        const lat = pos.coords.latitude.toFixed(4);
        const lon = pos.coords.longitude.toFixed(4);
        const v = currentProfile.village || 'बरखेड़ी';
        const d = (currentProfile.district || 'रायसेन').toUpperCase();
        document.getElementById('loss-gps').value = `${lat}°N, ${lon}°E (${v}, ${d})`;
        showToast('सटीक GPS निर्देशांक प्राप्त हुए');
        burnGeoWatermarkOnCurrentPhoto();
      },
      err => {
        showToast('डिफ़ॉल्ट जिला भू-निर्देशांक सेट हैं');
      }
    );
  }
}

// ==================== SMART LABEL / OCR SCANNER MODAL ====================
function openSmartScanModal() {
  document.getElementById('modal-smart-scan').classList.remove('hidden');
  runScannerSample('sagarika');
}

function closeSmartScanModal() {
  document.getElementById('modal-smart-scan').classList.add('hidden');
}

async function runScannerSample(type) {
  try {
    const res = await fetch('/api/scan-label', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sample_type: type })
    });
    const data = await res.json();
    if (data.success) {
      activeScannedData = data;
      const ocr = data.ocr_result;
      const v = data.verification;

      document.getElementById('scan-viewfinder-img').src = ocr.image;
      document.getElementById('scan-out-prod').innerText = ocr.product_name;
      document.getElementById('scan-out-batch').innerText = ocr.batch_no;
      document.getElementById('scan-out-mfg').innerText = ocr.mfg_date;
      document.getElementById('scan-out-exp').innerText = ocr.exp_date;
      document.getElementById('scan-out-active').innerText = ocr.active_ingredient;

      const badgeEl = document.getElementById('scan-out-badge');
      if (v.is_hazardous) {
        badgeEl.className = 'font-bold px-2.5 py-1 rounded-full bg-red-100 text-red-800 text-[10px]';
        badgeEl.innerText = '🚨 अमानक / संदिग्ध रसायन';
      } else if (v.is_verified) {
        badgeEl.className = 'font-bold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[10px]';
        badgeEl.innerText = '✅ ICAR / CIBRC प्रमाणित';
      } else {
        badgeEl.className = 'font-bold px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-[10px]';
        badgeEl.innerText = '⚠️ गैर-प्रमाणित बायो-स्टिमुलेंट';
      }

      document.getElementById('scan-out-notes').innerText = v.reason || v.alert_title;
    }
  } catch (err) {
    showToast('स्कैनर प्रक्रिया में त्रुटि');
  }
}

async function addScannedProductToVault() {
  if (!activeScannedData) return;
  const ocr = activeScannedData.ocr_result;
  const payload = {
    product_name: ocr.product_name,
    batch_no: ocr.batch_no,
    category: ocr.category,
    mfg_date: ocr.mfg_date,
    exp_date: ocr.exp_date,
    dealer_name: "श्री बालाजी कृषि केंद्र",
    dealer_invoice_no: `INV-SCAN-${Math.floor(1000 + Math.random()*9000)}`,
    bag_photo: ocr.image,
    bill_photo: "/static/images/sample_bill.svg",
    purchase_date: new Date().toISOString().split('T')[0]
  };

  try {
    const res = await fetch('/api/inputs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast('✓ स्कैन किया गया उत्पाद वॉल्ट में सुरक्षित हुआ!');
      closeSmartScanModal();
      loadInputs();
    }
  } catch (e) {
    showToast('सहेजने में त्रुटि आई');
  }
}

// ==================== AGRI-INPUT VAULT ====================
async function loadInputs() {
  try {
    const res = await fetch('/api/inputs');
    const inputs = await res.json();
    renderInputs(inputs);
  } catch (err) {
    console.error('Failed to load inputs', err);
  }
}

function renderInputs(inputs) {
  const container = document.getElementById('inputs-list-container');
  const countBadge = document.getElementById('vault-count-badge');
  const totalCount = document.getElementById('vault-total-count');

  if (countBadge) countBadge.innerText = inputs.length;
  if (totalCount) totalCount.innerText = inputs.length;

  if (!container) return;
  container.innerHTML = '';

  inputs.forEach(item => {
    const isWarning = item.icar_status !== 'VERIFIED';
    const card = document.createElement('div');
    card.className = `bg-white border ${isWarning ? 'border-red-300 ring-1 ring-red-200' : 'border-slate-200'} rounded-2xl p-4 shadow-sm hover:shadow transition flex flex-col justify-between`;

    const nameLower = (item.product_name || '').toLowerCase();
    let defaultBag = '/static/images/sample_sagarika.svg';
    if (nameLower.includes('weed') || nameLower.includes('24d') || nameLower.includes('शाकनाशी')) {
      defaultBag = '/static/images/sample_weedicide.svg';
    } else if (nameLower.includes('dap') || nameLower.includes('डीएपी') || nameLower.includes('उर्वरक') || nameLower.includes('fertilizer')) {
      defaultBag = '/static/images/sample_dap.svg';
    } else if (nameLower.includes('belt') || nameLower.includes('कीटनाशक') || nameLower.includes('insecticide')) {
      defaultBag = '/static/images/sample_belt.svg';
    }

    const bagPhoto = (item.bag_photo && typeof item.bag_photo === 'string' && item.bag_photo.trim().length > 3) ? item.bag_photo : defaultBag;
    const billPhoto = (item.bill_photo && typeof item.bill_photo === 'string' && item.bill_photo.trim().length > 3) ? item.bill_photo : '/static/images/sample_bill.svg';
    const safeProdName = (item.product_name || 'कृषि इनपुट').replace(/'/g, "\\'");
    const safeInvNo = (item.dealer_invoice_no || 'रसीद').replace(/'/g, "\\'");

    card.innerHTML = `
      <div>
        <div class="flex items-start justify-between gap-2">
          <div>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${isWarning ? 'bg-red-100 text-red-800' : 'bg-emerald-100 text-emerald-800'}">
              ${item.badge_hi || (isWarning ? '🚨 अमानक/संदिग्ध' : '✅ ICAR प्रमाणित')}
            </span>
            <h4 class="font-bold text-slate-900 text-sm mt-1.5">${item.product_name}</h4>
            <p class="text-[11px] text-slate-500">${item.category}</p>
          </div>
          <div class="text-right">
            <span class="font-mono text-[10px] font-bold text-slate-600 block bg-slate-100 px-2 py-0.5 rounded">
              ${item.batch_no}
            </span>
            <span class="text-[9px] text-slate-400 mt-0.5 block">${item.purchase_date}</span>
          </div>
        </div>

        ${item.warning ? `
          <div class="mt-2.5 bg-red-50 border border-red-200 rounded-xl p-2 text-[11px] text-red-800 leading-snug">
            ${item.warning}
          </div>
        ` : ''}

        <div class="grid grid-cols-2 gap-2 mt-3 text-[11px] text-slate-600">
          <div>
            <span class="text-slate-400 block text-[10px]">डीलर:</span>
            <span class="font-medium text-slate-800 truncate block">${item.dealer_name}</span>
          </div>
          <div>
            <span class="text-slate-400 block text-[10px]">बिल / रसीद नं:</span>
            <span class="font-mono font-medium text-slate-800">${item.dealer_invoice_no}</span>
          </div>
        </div>

        <div class="mt-3 flex gap-2">
          <div class="w-1/2 border border-slate-200 rounded-xl p-1.5 text-center bg-slate-50 hover:bg-slate-100 transition cursor-pointer shadow-xs" onclick="previewVaultPhoto('${bagPhoto}', '${safeProdName}')" title="बड़ा देखने के लिए क्लिक करें">
            <div class="h-20 w-full rounded-lg overflow-hidden bg-white border border-slate-200 flex items-center justify-center p-1">
              <img src="${bagPhoto}" alt="बोतल/थैली" onerror="this.onerror=null; this.src='/static/images/sample_sagarika.svg';" class="h-full w-full object-contain">
            </div>
            <span class="text-[10px] font-bold text-slate-700 block mt-1">📸 बोतल/थैली 🔍</span>
          </div>
          <div class="w-1/2 border border-slate-200 rounded-xl p-1.5 text-center bg-slate-50 hover:bg-slate-100 transition cursor-pointer shadow-xs" onclick="previewVaultPhoto('${billPhoto}', 'पक्का बिल: ${safeInvNo}')" title="बड़ा देखने के लिए क्लिक करें">
            <div class="h-20 w-full rounded-lg overflow-hidden bg-white border border-slate-200 flex items-center justify-center p-1">
              <img src="${billPhoto}" alt="पक्का बिल" onerror="this.onerror=null; this.src='/static/images/sample_bill.svg';" class="h-full w-full object-contain">
            </div>
            <span class="text-[10px] font-bold text-slate-700 block mt-1">🧾 पक्का बिल 🔍</span>
          </div>
        </div>
      </div>

      <div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
        <span class="flex items-center">
          <i data-lucide="map-pin" class="w-3 h-3 mr-1 text-slate-400"></i>
          ${item.gps_location_text || (currentProfile.district ? currentProfile.district.toUpperCase() : 'रायसेन, म.प्र.')}
        </span>
        <span class="font-semibold text-emerald-700">✓ साक्ष्य सुरक्षित</span>
      </div>
    `;

    container.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

function previewVaultPhoto(imgUrl, title) {
  const modal = document.getElementById('modal-image-preview');
  if (!modal) return;
  const imgEl = document.getElementById('image-preview-img');
  const titleEl = document.getElementById('image-preview-title');
  if (imgEl) imgEl.src = imgUrl;
  if (titleEl) titleEl.innerText = title || 'साक्ष्य फोटो';
  modal.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
}

function closeImagePreviewModal() {
  const modal = document.getElementById('modal-image-preview');
  if (modal) modal.classList.add('hidden');
}

function openNewInputModal() {
  document.getElementById('modal-new-input').classList.remove('hidden');
}

function closeNewInputModal() {
  document.getElementById('modal-new-input').classList.add('hidden');
}

function setModalSamplePhoto(type) {
  if (type === 'sagarika') {
    selectedBagPhoto = '/static/images/sample_sagarika.svg';
    document.getElementById('inp-name').value = 'IFFCO Sagarika (इफको सागरिका)';
    document.getElementById('inp-batch').value = 'SG-2026-0814';
    checkProductLive('IFFCO Sagarika');
    showToast('इफको सागरिका नमूना चुना गया');
  } else {
    selectedBagPhoto = '/static/images/sample_weedicide.svg';
    document.getElementById('inp-name').value = 'Super Weed Burn 24D Mix';
    document.getElementById('inp-batch').value = 'SWB-7721-RAI';
    checkProductLive('Super Weed Burn 24D Mix');
    showToast('संदिग्ध खरपतवारनाशक नमूना चुना गया');
  }
}

async function saveNewAgriInput(e) {
  e.preventDefault();
  const payload = {
    product_name: document.getElementById('inp-name').value,
    batch_no: document.getElementById('inp-batch').value,
    category: document.getElementById('inp-category').value,
    dealer_name: document.getElementById('inp-dealer').value,
    dealer_invoice_no: document.getElementById('inp-bill-no').value || 'INV-2026-NEW',
    bag_photo: selectedBagPhoto,
    bill_photo: '/static/images/sample_bill.svg',
    purchase_date: new Date().toISOString().split('T')[0]
  };

  // Check if offline in field
  if (!navigator.onLine) {
    const offlineItem = {
      ...payload,
      id: 'inp_off_' + Date.now().toString(36),
      icar_status: 'PENDING_SYNC',
      badge_hi: '📦 ऑफ़लाइन सुरक्षित',
      gps_location_text: (currentProfile.village || 'बेड़ाखेड़ी') + ', ' + (currentProfile.district || 'देवास'),
      warning: 'ऑफ़लाइन दर्ज: इंटरनेट सिग्नल मिलते ही ICAR सत्यापन होगा।'
    };
    saveOfflineInput(offlineItem);
    showToast('📦 इंटरनेट नहीं है - इनपुट साक्ष्य फोन में सुरक्षित हो गया!');
    closeNewInputModal();
    return;
  }

  try {
    const res = await fetch('/api/inputs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast('✓ इनपुट वॉल्ट में सफलतापूर्वक सुरक्षित हुआ!');
      closeNewInputModal();
      loadInputs();
    }
  } catch (err) {
    showToast('इनपुट सुरक्षित करने में त्रुटि आई।');
  }
}


async function performQuickCheck() {
  const query = document.getElementById('quick-check-input').value.trim();
  const resBox = document.getElementById('quick-check-result');
  if (!query) return;

  try {
    const res = await fetch('/api/inputs/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_name: query, batch_no: query })
    });
    const data = await res.json();
    resBox.classList.remove('hidden');

    if (data.is_hazardous) {
      resBox.className = 'mt-3 p-3.5 rounded-xl border border-red-300 bg-red-50 text-red-900 text-xs';
      resBox.innerHTML = `
        <div class="flex items-center space-x-2 font-bold text-red-800">
          <i data-lucide="alert-triangle" class="w-4 h-4 text-red-600"></i>
          <span>${data.alert_title}</span>
        </div>
        <p class="mt-1 leading-relaxed">${data.reason}</p>
        <p class="mt-1 font-bold text-red-700">अनुशंसा: ${data.action_recommended_hi}</p>
      `;
    } else if (data.is_verified) {
      resBox.className = 'mt-3 p-3.5 rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-900 text-xs';
      resBox.innerHTML = `
        <div class="flex items-center space-x-2 font-bold text-emerald-800">
          <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600"></i>
          <span>${data.alert_title}</span>
        </div>
        <p class="mt-1 leading-relaxed">${data.reason}</p>
        <p class="mt-1 font-mono text-[11px] text-emerald-700">पंजीकरण संख्या: ${data.icar_reg_no}</p>
      `;
    } else {
      resBox.className = 'mt-3 p-3.5 rounded-xl border border-amber-300 bg-amber-50 text-amber-900 text-xs';
      resBox.innerHTML = `
        <div class="flex items-center space-x-2 font-bold text-amber-800">
          <i data-lucide="info" class="w-4 h-4 text-amber-600"></i>
          <span>${data.badge_hi}</span>
        </div>
        <p class="mt-1 leading-relaxed">${data.reason}</p>
        <p class="mt-1 text-amber-800">कार्रवाई: ${data.action_recommended_hi}</p>
      `;
    }

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    showToast('सत्यापन जांच में त्रुटि आई।');
  }
}

let checkTimeout = null;
async function checkProductLive(val) {
  if (checkTimeout) clearTimeout(checkTimeout);
  const badgeEl = document.getElementById('modal-icar-badge');
  if (!val || val.length < 3) {
    badgeEl.classList.add('hidden');
    return;
  }

  checkTimeout = setTimeout(async () => {
    try {
      const res = await fetch('/api/inputs/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: val })
      });
      const data = await res.json();
      badgeEl.classList.remove('hidden');

      if (data.is_hazardous) {
        badgeEl.className = 'p-2.5 rounded-xl border border-red-300 bg-red-50 text-red-800 text-xs';
        badgeEl.innerHTML = `<b>🚨 अलर्ट:</b> ${data.alert_title}<br><span class="text-[11px]">${data.reason}</span>`;
      } else if (data.is_verified) {
        badgeEl.className = 'p-2.5 rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-800 text-xs';
        badgeEl.innerHTML = `<b>✓ ICAR प्रमाणित:</b> ${data.alert_title}<br><span class="text-[11px]">${data.reason}</span>`;
      } else {
        badgeEl.className = 'p-2.5 rounded-xl border border-amber-300 bg-amber-50 text-amber-800 text-xs';
        badgeEl.innerHTML = `<b>⚠️ बायो-स्टिमुलेंट समीक्षा:</b> ${data.reason}`;
      }
    } catch (e) {
      console.error(e);
    }
  }, 350);
}

// ==================== CALAMITY & LOSS REPORTING ====================
async function submitLossReport(e) {
  e.preventDefault();
  const cType = document.getElementById('loss-calamity-type').value;
  const notes = document.getElementById('loss-notes').value;

  try {
    const res = await fetch('/api/calamity/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        calamity_type: cType,
        notes: notes,
        district: currentProfile.district || 'raisen'
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast('🚨 72-घंटे का दावा समय-सीमा में सफलतापूर्वक दर्ज!');
      loadCalamityState();
      switchTab('tab-dossier');
    }
  } catch (err) {
    showToast('दावा दर्ज करने में त्रुटि');
  }
}

function triggerTestCalamity(type) {
  if (type === 'hailstorm') {
    document.getElementById('loss-calamity-type').value = 'ओलावृष्टि (Hailstorm Damage)';
    document.getElementById('loss-notes').value = 'अचानक 20 मिनट तेज ओलावृष्टि से सोयाबीन की पत्तियां व फलियां टूट कर गिर गईं।';
    showToast('ओलावृष्टि टेस्ट लोड किया गया');
  } else if (type === 'fake_weedicide') {
    document.getElementById('loss-calamity-type').value = 'अमानक/नकली खरपतवारनाशक से झुलसा (Spurious Chemical Burn)';
    document.getElementById('loss-notes').value = 'अमानक खरपतवारनाशक (बैच SWB-7721-RAI) के छिड़काव के 48 घंटे बाद पूरी फसल पीली पड़कर झुलस गई।';
    showToast('नकली दवा झुलसा टेस्ट लोड किया गया');
  }
  burnGeoWatermarkOnCurrentPhoto();
}

// ==================== WHATSAPP SIMULATOR ====================
async function loadWhatsAppHistory() {
  try {
    const res = await fetch('/api/whatsapp/history');
    const history = await res.json();
    renderWhatsAppChat(history);
  } catch (err) {
    console.error('Failed to load whatsapp history', err);
  }
}

function renderWhatsAppChat(messages) {
  const container = document.getElementById('wa-chat-container');
  const quickBox = document.getElementById('wa-quick-replies');
  if (!container) return;

  container.innerHTML = '';
  let latestQuickReplies = ["1. इनपुट फोटो भेजें", "2. नुकसान दर्ज करें", "3. मौसम चेक करें", "4. दावा पर्ची"];

  messages.forEach(msg => {
    const isUser = msg.sender === 'user';
    const bubble = document.createElement('div');
    bubble.className = isUser ? 'wa-bubble-user' : 'wa-bubble-bot';

    let content = '';
    if (msg.image) {
      content += `<img src="${msg.image}" class="rounded-lg mb-2 max-h-36 w-full object-cover border border-slate-200">`;
    }
    
    let formattedText = (msg.text || '').replace(/\*(.*?)\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
    content += `<div>${formattedText}</div>`;
    content += `<div class="wa-time">${msg.timestamp || 'अब'} ${isUser ? '✓✓' : ''}</div>`;

    bubble.innerHTML = content;
    container.appendChild(bubble);

    if (!isUser && msg.quick_replies) {
      latestQuickReplies = msg.quick_replies;
    }
  });

  if (quickBox) {
    quickBox.innerHTML = '';
    latestQuickReplies.forEach(qr => {
      const btn = document.createElement('button');
      btn.className = 'bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 text-[11px] font-semibold px-3 py-1.5 rounded-full whitespace-nowrap shadow-sm transition';
      btn.innerText = qr;
      btn.onclick = () => sendQuickReply(qr);
      quickBox.appendChild(btn);
    });
  }

  scrollWhatsAppToBottom();
}

function scrollWhatsAppToBottom() {
  const container = document.getElementById('wa-chat-container');
  if (container) {
    setTimeout(() => {
      container.scrollTop = container.scrollHeight;
    }, 50);
  }
}

async function sendWhatsAppMessage(e) {
  e.preventDefault();
  const input = document.getElementById('wa-message-input');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  await postToWhatsAppApi({ text: text });
}

async function sendQuickReply(text) {
  await postToWhatsAppApi({ text: text });
}

async function triggerWaSamplePhoto(type) {
  const imgUrl = type === 'sagarika' ? '/static/images/sample_sagarika.svg' : '/static/images/sample_weedicide.svg';
  const label = type === 'sagarika' ? 'इफको सागरिका (दवा का फोटो)' : 'Super Weed Burn (संदिग्ध दवा फोटो)';
  await postToWhatsAppApi({ text: label, image_url: imgUrl });
}

async function triggerImdAlertPush() {
  try {
    const res = await fetch('/api/whatsapp/push-imd-alert', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      loadWhatsAppHistory();
      loadCalamityState();
      speakText('मौसम विभाग आपातकालीन अलर्ट जारी। 72 घंटे की दावा विंडो शुरू हो चुकी है।');
      showToast('⚡ IMD आपात अलर्ट व्हाट्सएप पर प्राप्त हुआ!');
    }
  } catch (err) {
    showToast('अलर्ट ट्रिगर में त्रुटि');
  }
}

async function postToWhatsAppApi(payload) {
  try {
    const res = await fetch('/api/whatsapp/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      loadWhatsAppHistory();
    }
  } catch (err) {
    showToast('व्हाट्सएप संदेश भेजने में त्रुटि');
  }
}

async function resetWhatsAppChat() {
  try {
    const res = await fetch('/api/whatsapp/reset', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      renderWhatsAppChat(data.history);
      showToast('व्हाट्सएप चैट रीसेट किया गया');
    }
  } catch (err) {
    showToast('रीसेट त्रुटि');
  }
}

// ==================== DOSSIER GENERATION & EXPORT ====================
async function loadDossierData() {
  try {
    const res = await fetch('/api/dossier');
    const d = await res.json();
    currentDossier = d;

    if (d) {
      if (document.getElementById('dos-id')) document.getElementById('dos-id').innerText = d.dossier_id;
      if (document.getElementById('dos-date')) document.getElementById('dos-date').innerText = d.generated_at;
      if (document.getElementById('dos-farmer-name')) document.getElementById('dos-farmer-name').innerText = `${d.farmer.name} (आत्मज: ${d.farmer.father_name || 'श्री शिवनारायण शर्मा'})`;
      if (document.getElementById('dos-farmer-mobile')) document.getElementById('dos-farmer-mobile').innerText = d.farmer.mobile;
      if (document.getElementById('dos-farmer-village')) document.getElementById('dos-farmer-village').innerText = `${d.farmer.village}, तहसील ${d.farmer.tehsil}`;
      if (document.getElementById('dos-farmer-district')) document.getElementById('dos-farmer-district').innerText = `${(d.farmer.district || 'Dewas').toUpperCase()}, मध्य प्रदेश`;
      if (document.getElementById('dos-farmer-khasra')) document.getElementById('dos-farmer-khasra').innerText = `${d.farmer.khasra_no} (रकबा ${d.farmer.total_land_acres} एकड़)`;
      if (document.getElementById('dos-farmer-crop')) document.getElementById('dos-farmer-crop').innerText = d.farmer.crop;
      if (document.getElementById('dos-farmer-policy')) document.getElementById('dos-farmer-policy').innerText = d.farmer.pmfby_application_no;
      if (document.getElementById('dos-farmer-bank')) document.getElementById('dos-farmer-bank').innerText = `${d.farmer.bank_name} (खाता अंतिम: ${d.farmer.bank_account_last4})`;
      if (document.getElementById('dos-calamity-type')) document.getElementById('dos-calamity-type').innerText = d.calamity.calamity_type;
      if (document.getElementById('dos-calamity-time')) document.getElementById('dos-calamity-time').innerText = d.calamity.started_at ? d.calamity.started_at.slice(0, 16).replace('T', ' ') : 'उपलब्ध नहीं';
      if (document.getElementById('dos-loss-pct')) document.getElementById('dos-loss-pct').innerText = `${d.calamity.estimated_loss_percent}% (गंभीर क्षति)`;

      // Populate Financial Breakdown Table
      if (d.payout_info) {
        if (document.getElementById('dos-sum-insured-rate')) document.getElementById('dos-sum-insured-rate').innerText = `${d.payout_info.sum_insured_per_ha_formatted} / हेक्टेयर`;
        if (document.getElementById('dos-affected-ha')) document.getElementById('dos-affected-ha').innerText = `${d.payout_info.hectares} हेक्टेयर (${d.farmer.total_land_acres} एकड़)`;
        if (document.getElementById('dos-total-sum-insured')) document.getElementById('dos-total-sum-insured').innerText = d.payout_info.total_sum_insured_formatted;
        if (document.getElementById('dos-payout-formula')) document.getElementById('dos-payout-formula').innerText = `${d.payout_info.loss_percent}% क्षति आंकलन आधारित`;
        if (document.getElementById('dos-payout-amount')) document.getElementById('dos-payout-amount').innerText = `${d.payout_info.estimated_payout_formatted}/- (${d.payout_info.formula})`;
      }

      // Populate Weather Station Satellite Corroboration Seal
      if (d.satellite_evidence) {
        if (document.getElementById('dos-weather-precip')) document.getElementById('dos-weather-precip').innerText = `${d.satellite_evidence.recorded_rainfall_mm} mm অতিवृष्टि (${d.satellite_evidence.station_name})`;
        if (document.getElementById('dos-satellite-seal-text')) document.getElementById('dos-satellite-seal-text').innerText = `${d.satellite_evidence.station_name} द्वारा ${d.satellite_evidence.recorded_rainfall_mm} mm वर्षा दर्ज • ${d.satellite_evidence.rainfall_category}`;
      }

      // Populate SMS Preview
      if (d.sms_intimation) {
        if (document.getElementById('sms-body-preview')) document.getElementById('sms-body-preview').innerText = d.sms_intimation.text;
        const smsLink = document.getElementById('btn-sms-app-launcher');
        if (smsLink) smsLink.href = d.sms_intimation.sms_url;
      }

      // Populate Telephonic Call Assistant Script
      if (d.telephonic_operator_script && d.telephonic_operator_script.script_points) {
        const pts = d.telephonic_operator_script.script_points;
        if (pts[0] && document.getElementById('script-point-1')) document.getElementById('script-point-1').innerHTML = pts[0];
        if (pts[1] && document.getElementById('script-point-2')) document.getElementById('script-point-2').innerHTML = pts[1];
        if (pts[2] && document.getElementById('script-point-3')) document.getElementById('script-point-3').innerHTML = pts[2];
        if (pts[3] && document.getElementById('script-point-4')) document.getElementById('script-point-4').innerHTML = pts[3];
      }
      if (document.getElementById('script-token-display')) document.getElementById('script-token-display').innerText = d.claim_token || d.dossier_id;

      // Populate official PMFBY Claim Token Receipt
      const token = d.claim_token || d.dossier_id;
      if (document.getElementById('receipt-token-no')) document.getElementById('receipt-token-no').innerText = token;
      if (document.getElementById('receipt-big-token')) document.getElementById('receipt-big-token').innerText = token;
      if (document.getElementById('receipt-date')) document.getElementById('receipt-date').innerText = d.generated_at;
      if (document.getElementById('receipt-farmer-name')) document.getElementById('receipt-farmer-name').innerText = d.farmer.name;
      if (document.getElementById('receipt-farmer-mobile')) document.getElementById('receipt-farmer-mobile').innerText = d.farmer.mobile;
      if (document.getElementById('receipt-farmer-village')) document.getElementById('receipt-farmer-village').innerText = d.farmer.village;
      if (document.getElementById('receipt-farmer-tehsil')) document.getElementById('receipt-farmer-tehsil').innerText = d.farmer.tehsil;
      if (document.getElementById('receipt-farmer-district')) document.getElementById('receipt-farmer-district').innerText = `${d.farmer.district ? d.farmer.district.toUpperCase() : 'DEWAS'} (म.प्र.)`;
      if (document.getElementById('receipt-farmer-land')) document.getElementById('receipt-farmer-land').innerText = `${d.farmer.khasra_no} (${d.farmer.total_land_acres} एकड़)`;
      if (document.getElementById('receipt-policy-no')) document.getElementById('receipt-policy-no').innerText = d.farmer.pmfby_application_no;
      if (document.getElementById('receipt-calamity-type')) document.getElementById('receipt-calamity-type').innerText = d.calamity.calamity_type;
      if (document.getElementById('receipt-loss-percent')) document.getElementById('receipt-loss-percent').innerText = `${d.calamity.estimated_loss_percent}% (गंभीर)`;
      if (document.getElementById('receipt-insurer')) document.getElementById('receipt-insurer').innerText = d.district_info ? d.district_info.insurance_company : 'HDFC ERGO';
      if (document.getElementById('receipt-gps')) document.getElementById('receipt-gps').innerText = `${d.calamity.gps_lat || '22.9640'}°N, ${d.calamity.gps_lon || '76.3380'}°E`;
    }
  } catch (err) {
    console.error('Failed to load dossier', err);
  }
}

function shareOnWhatsApp() {
  if (currentDossier && currentDossier.whatsapp_share_url) {
    window.open(currentDossier.whatsapp_share_url, '_blank');
  } else {
    showToast('दावा पर्ची तैयार नहीं है');
  }
}

function shareClaimOnWhatsApp() {
  shareOnWhatsApp();
}

function copyDossierText() {
  if (currentDossier && currentDossier.whatsapp_text) {
    navigator.clipboard.writeText(currentDossier.whatsapp_text).then(() => {
      showToast('दावा सूचना कॉपी हो गई! आप इसे सीधे व्हाट्सएप पर पेस्ट कर सकते हैं।');
    });
  }
}

// ==================== INTERACTIVE PMFBY CLAIM CALCULATOR ====================
async function updateClaimCalculation() {
  const acresEl = document.getElementById('calc-input-acres');
  const lossEl = document.getElementById('calc-slider-loss');
  if (!acresEl || !lossEl) return;

  const acres = parseFloat(acresEl.value) || 6.5;
  const loss = parseFloat(lossEl.value) || 65;
  const ha = (acres / 2.47105).toFixed(2);

  const haEl = document.getElementById('calc-converted-ha');
  if (haEl) haEl.innerText = `(= ${ha} हेक्टेयर)`;

  const lossBadge = document.getElementById('calc-loss-badge');
  if (lossBadge) {
    let severity = 'मध्यम';
    if (loss >= 75) severity = 'पूर्ण विनाश';
    else if (loss >= 50) severity = 'गंभीर नुकसान';
    else if (loss >= 33) severity = 'मध्यम नुकसान';
    else severity = 'न्यूनतम क्षति';
    lossBadge.innerText = `${loss}% (${severity})`;
  }

  // Also sync the form inputs in tab-loss-reporter
  const formAcres = document.getElementById('loss-acres');
  if (formAcres) formAcres.value = `${acres} एकड़`;
  const formLoss = document.getElementById('loss-percentage');
  if (formLoss) formLoss.value = loss.toString();

  const cropName = currentProfile.crop || 'सोयाबीन';
  const rate = 48000;
  const totalSI = Math.round(parseFloat(ha) * rate);
  const payout = Math.round(totalSI * (loss / 100));

  const payoutEl = document.getElementById('calc-claim-payout');
  if (payoutEl) payoutEl.innerText = `₹${payout.toLocaleString('en-IN')}`;

  const subEl = document.getElementById('calc-formula-subtitle');
  if (subEl) subEl.innerText = `${ha} हेक्टेयर × ₹${rate.toLocaleString('en-IN')} × ${loss}%`;

  try {
    const res = await fetch(`/api/claim/calculate-payout?acres=${acres}&loss_percent=${loss}&crop=${encodeURIComponent(cropName)}`);
    const data = await res.json();
    if (data.success && data.payout) {
      if (payoutEl) payoutEl.innerText = data.payout.estimated_payout_formatted;
      if (subEl) subEl.innerText = data.payout.formula;
    }
  } catch (e) {
    console.log('Calculation sync error', e);
  }
}

function onCalamityTypeChange(val) {
  const citeEl = document.getElementById('calc-clause-cite');
  if (!citeEl) return;
  if (val.includes('ओला')) {
    citeEl.innerText = 'लागू नियम: कंडिका 21.4 (स्थानीयकृत आपदा - ओलावृष्टि / 72h अनिवार्य)';
  } else if (val.includes('दवा') || val.includes('रसायन')) {
    citeEl.innerText = 'लागू नियम: कीटनाशी अधिनियम 1968 (धारा 21, 22 व 29) + फसल झुलसा विवाद';
  } else if (val.includes('बादल')) {
    citeEl.innerText = 'लागू नियम: कंडिका 21.4 (स्थानीयकृत आपदा - बादल फटना / तेज आंधी)';
  } else {
    citeEl.innerText = 'लागू नियम: कंडिका 21.4 (स्थानीयकृत आपदा - जलभराव व अतिवृष्टि)';
  }
}

// ==================== 14447 CALL SCRIPT & SMS MODALS ====================
function openCallScriptModal() {
  const modal = document.getElementById('modal-call-script-14447');
  if (modal) modal.classList.remove('hidden');
}

function closeCallScriptModal() {
  const modal = document.getElementById('modal-call-script-14447');
  if (modal) modal.classList.add('hidden');
}

function saveDocketNumber() {
  const input = document.getElementById('docket-input');
  if (!input || !input.value.trim()) {
    showToast('कृपया पहले 14447 से प्राप्त डॉकेट नंबर दर्ज करें');
    return;
  }
  const val = input.value.trim().toUpperCase();
  localStorage.setItem('khetproof_pmfby_docket', val);
  showToast(`✅ डॉकेट नंबर ${val} PMFBY क्लेम रिकॉर्ड में सुरक्षित हुआ!`);
  closeCallScriptModal();
}

function openSmsIntimationModal() {
  const modal = document.getElementById('modal-sms-intimation');
  if (modal) modal.classList.remove('hidden');
}

function closeSmsIntimationModal() {
  const modal = document.getElementById('modal-sms-intimation');
  if (modal) modal.classList.add('hidden');
}

function copySmsText() {
  const el = document.getElementById('sms-body-preview');
  if (el) {
    navigator.clipboard.writeText(el.innerText).then(() => {
      showToast('✓ SMS टेक्स्ट कॉपी हो गया! मैसेज ऐप में पेस्ट करके भेजें।');
    });
  }
}

// ==================== 3-ANGLE EVIDENCE PHOTO CAPTURE ====================
function previewEvidencePhoto(event, slot) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const rawDataUrl = e.target.result;
    const imgEl = document.getElementById(`img-evidence-${slot}`);
    if (imgEl) {
      imgEl.src = rawDataUrl;
    }

    // Apply digital GPS watermark
    const canvas = document.getElementById('watermark-canvas');
    if (canvas) {
      const img = new Image();
      img.onload = function() {
        canvas.width = img.width || 800;
        canvas.height = img.height || 600;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Watermark bar
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, canvas.height - 50, canvas.width, 50);

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 16px sans-serif';
        const nowStr = new Date().toLocaleString('en-IN');
        const lat = currentProfile.gps_lat || '22.9640';
        const lon = currentProfile.gps_lon || '76.3380';
        ctx.fillText(`🌾 KHETPROOF EVIDENCE [${slot.toUpperCase()}] • Lat: ${lat}°N, Lon: ${lon}°E • ${nowStr}`, 15, canvas.height - 20);

        const watermarkedUrl = canvas.toDataURL('image/jpeg', 0.85);
        if (imgEl) imgEl.src = watermarkedUrl;
      };
      img.src = rawDataUrl;
    }

    showToast(`✓ कोण ${slot}: साक्ष्य फोटो GPS व टाइमस्टैम्प वाटरमार्क सहित सुरक्षित हुई!`);
  };
  reader.readAsDataURL(file);
}

function simulateWeatherStorm() {
  calamitySecondsLeft = 72 * 3600;
  showToast('⚡ अतिवृष्टि व आंधी-तूफान सिमुलेशन सक्रिय! 72-घंटे की PMFBY उलटी गिनती शुरू।');
  renderCountdownDisplays();

  // Dynamically reflect in the Weather Station card
  const elRisk = document.getElementById('weather-risk-badge');
  if (elRisk) {
    elRisk.className = 'text-[11px] font-bold px-2.5 py-1 rounded-full bg-red-100 text-red-800 border border-red-300 animate-pulse';
    elRisk.innerText = '🚨 अतिवृष्टि (84mm)';
  }
  const elDesc = document.getElementById('weather-desc');
  if (elDesc) elDesc.innerText = 'तूफानी वर्षा व तेज हवाएं दर्ज';
  const elRain = document.getElementById('weather-rain-stat');
  if (elRain) elRain.innerText = '84.0mm (95%)';
  const elWind = document.getElementById('weather-wind');
  if (elWind) elWind.innerText = '38 km/h';
  
  const elAdvBox = document.getElementById('weather-advisory-box');
  const elAdvText = document.getElementById('weather-advisory-text');
  if (elAdvBox && elAdvText) {
    elAdvBox.className = 'mt-3 p-2.5 rounded-xl bg-red-50 border border-red-200 text-xs transition-colors';
    elAdvText.innerText = '🚨 अतिवृष्टि व जलभराव अलर्ट: 72 घंटे में फसल बीमा सूचना दर्ज करना अनिवार्य है। खेत के जल निकासी का फोटो लें व दावा पर्ची तैयार करें!';
  }
}

// ==================== PWA & OFFLINE FIELD RESILIENCE ====================
function initPwaAndOffline() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('[KhetProof] SW Registered'))
      .catch(err => console.warn('[KhetProof] SW registration failed', err));
  }

  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  updateOnlineStatus();
}

function updateOnlineStatus() {
  const badge = document.getElementById('offline-badge');
  if (!badge) return;
  if (!navigator.onLine) {
    badge.classList.remove('hidden');
    badge.classList.add('flex');
  } else {
    const queue = getOfflineQueue();
    if (queue.inputs.length === 0 && !queue.calamity) {
      badge.classList.add('hidden');
      badge.classList.remove('flex');
    } else {
      badge.classList.remove('hidden');
      badge.classList.add('flex');
    }
  }
}

function getOfflineQueue() {
  try {
    return JSON.parse(localStorage.getItem('khetproof_offline_queue') || '{"inputs":[],"calamity":null}');
  } catch (e) {
    return { inputs: [], calamity: null };
  }
}

function saveOfflineInput(item) {
  const q = getOfflineQueue();
  q.inputs.push(item);
  localStorage.setItem('khetproof_offline_queue', JSON.stringify(q));
  updateOnlineStatus();
  loadInputs();
}

function saveOfflineLoss(calamityData) {
  const q = getOfflineQueue();
  q.calamity = calamityData;
  localStorage.setItem('khetproof_offline_queue', JSON.stringify(q));
  updateOnlineStatus();
}

async function syncOfflineData() {
  if (!navigator.onLine) {
    showToast('⚠️ अभी इंटरनेट नहीं है। कृपया सिग्नल आने पर पुनः प्रयास करें।');
    return;
  }
  const q = getOfflineQueue();
  if (q.inputs.length === 0 && !q.calamity) {
    showToast('✓ सभी साक्ष्य पहले से सिंक हैं। कोई पेंडिंग डेटा नहीं।');
    return;
  }

  showToast('🔄 ऑफ़लाइन साक्ष्य सर्वर पर सिंक हो रहे हैं...');
  try {
    const res = await fetch('/api/sync-offline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(q)
    });
    const data = await res.json();
    if (data.success) {
      localStorage.removeItem('khetproof_offline_queue');
      updateOnlineStatus();
      loadInputs();
      loadCalamityState();
      loadDossierData();
      showToast(`✅ ${data.message}`);
    }
  } catch (err) {
    showToast('सिंक करने में त्रुटि आई। कृपया नेटवर्क जांचें।');
  }
}

// ==================== 72-HOUR LOSS REPORT SUBMISSION ====================
async function submitLossReport(e) {
  if (e) e.preventDefault();
  const cType = document.getElementById('loss-calamity-type').value;
  const lossPct = document.getElementById('loss-percentage').value;
  const notes = document.getElementById('loss-notes').value;
  const acres = document.getElementById('loss-acres').value;

  const payload = {
    district: currentProfile.district || 'dewas',
    calamity_type: cType,
    estimated_loss_percent: parseInt(lossPct, 10),
    notes: `${notes} | रकबा: ${acres}`,
    crop: currentProfile.crop || 'सोयाबीन JS-2034'
  };

  if (!navigator.onLine) {
    saveOfflineLoss(payload);
    calamitySecondsLeft = 72 * 3600;
    renderCountdownDisplays();
    showToast('📦 72-घंटे दावा ऑफ़लाइन सुरक्षित हुआ! सिग्नल मिलने पर सिंक होगा।');
    switchTab('tab-dossier');
    return;
  }

  try {
    const res = await fetch('/api/calamity/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      calamitySecondsLeft = 72 * 3600;
      renderCountdownDisplays();
      showToast('🚨 72-घंटे का PMFBY दावा सफलतापूर्वक लॉक हुआ!');
      loadDossierData();
      switchTab('tab-dossier');
    }
  } catch (err) {
    showToast('दावा दर्ज करने में त्रुटि');
  }
}

function triggerTestCalamity(type) {
  if (type === 'hailstorm') {
    document.getElementById('loss-calamity-type').value = 'ओलावृष्टि (Hailstorm Damage)';
    document.getElementById('loss-percentage').value = '65';
    document.getElementById('loss-notes').value = 'दोपहर 3 बजे भीषण ओलावृष्टि से फलियां झड़ीं।';
  } else if (type === 'fake_weedicide') {
    document.getElementById('loss-calamity-type').value = 'अमानक/नकली खरपतवारनाशक से झुलसा (Spurious Chemical Burn)';
    document.getElementById('loss-percentage').value = '90';
    document.getElementById('loss-notes').value = 'छिड़काव के 48 घंटे बाद पूरी फसल पीली पड़कर झुलस गई। डीलर: किसान सेवा केंद्र';
  }
  submitLossReport();
}

// ==================== HINDI VOICE INPUT & NLP PARSING ====================
function toggleVoiceReporting() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast('आपके ब्राउज़र में सीधा माइक समर्थित नहीं है। कृपया नीचे दिए गए डेमो बटन दबाएं।');
    return;
  }

  if (isRecordingVoice) {
    if (speechRecognizer) speechRecognizer.stop();
    return;
  }

  try {
    speechRecognizer = new SpeechRecognition();
    speechRecognizer.lang = 'hi-IN';
    speechRecognizer.interimResults = true;
    speechRecognizer.continuous = false;

    const statusEl = document.getElementById('voice-recording-status');
    const dispEl = document.getElementById('voice-transcript-display');

    speechRecognizer.onstart = () => {
      isRecordingVoice = true;
      if (statusEl) statusEl.classList.remove('hidden');
      if (dispEl) dispEl.innerHTML = '<i>🎤 आपकी आवाज़ सुनी जा रही है... बोलिए</i>';
    };

    speechRecognizer.onresult = (event) => {
      const transcript = Array.from(event.results).map(r => r[0].transcript).join('');
      if (dispEl) dispEl.innerText = transcript;
    };

    speechRecognizer.onerror = (event) => {
      console.warn('Speech recognition error', event);
      isRecordingVoice = false;
      if (statusEl) statusEl.classList.add('hidden');
      showToast('माइक आवाज़ नहीं पकड़ सका। कृपया पुनः प्रयास करें।');
    };

    speechRecognizer.onend = () => {
      isRecordingVoice = false;
      if (statusEl) statusEl.classList.add('hidden');
      const text = dispEl ? dispEl.innerText : '';
      if (text && text.length > 3) {
        processSpokenHindi(text);
      }
    };

    speechRecognizer.start();
  } catch (err) {
    showToast('माइक शुरू नहीं हो सका');
  }
}

async function simulateVoiceInput(sampleText) {
  const dispEl = document.getElementById('voice-transcript-display');
  if (dispEl) {
    dispEl.innerText = sampleText;
  }
  showToast('🎙️ वॉयस इनपुट प्रोसेस हो रहा है...');
  processSpokenHindi(sampleText);
}

async function processSpokenHindi(text) {
  try {
    const res = await fetch('/api/voice-extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speech_text: text, auto_trigger: false })
    });
    const data = await res.json();
    if (data.success) {
      const ext = data.extracted;
      if (document.getElementById('loss-calamity-type')) {
        document.getElementById('loss-calamity-type').value = ext.calamity_type;
      }
      if (document.getElementById('loss-percentage')) {
        document.getElementById('loss-percentage').value = ext.estimated_loss_percent.toString();
      }
      if (document.getElementById('loss-notes')) {
        document.getElementById('loss-notes').value = `[वॉयस रिकॉर्ड]: ${ext.transcript}`;
      }
      showToast(`✓ आवाज़ से पहचाना गया: ${ext.calamity_type} (${ext.estimated_loss_percent}% नुकसान)`);
    }
  } catch (e) {
    console.error('Voice extract error', e);
  }
}


// ==================== REAL PHONE WHATSAPP ACTIONS ====================
let currentDealerNotice = null;

async function openRealPhoneWhatsAppClaim() {
  try {
    const res = await fetch('/api/dossier');
    const d = await res.json();
    if (d && d.whatsapp_share_url) {
      window.open(d.whatsapp_share_url, '_blank');
    }
  } catch (err) {
    showToast('दावा पर्ची तैयार नहीं हो सकी');
  }
}

async function openRealPhoneWhatsAppNotice() {
  try {
    const res = await fetch('/api/legal-notice/dealer');
    const n = await res.json();
    if (n && n.whatsapp_share_url) {
      window.open(n.whatsapp_share_url, '_blank');
    }
  } catch (err) {
    showToast('कानूनी नोटिस लोड नहीं हो सका');
  }
}

function switchDossierDoc(docType) {
  activeDossierDoc = docType;
  const pmfbyBtn = document.getElementById('btn-doc-pmfby');
  const legalBtn = document.getElementById('btn-doc-legal');
  const receiptBtn = document.getElementById('btn-doc-receipt');
  const pmfbyDoc = document.getElementById('printable-dossier');
  const legalDoc = document.getElementById('printable-legal-notice');
  const receiptDoc = document.getElementById('printable-claim-receipt');

  const baseBtnClass = 'bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs px-3.5 py-2 rounded-xl border border-slate-300 transition flex items-center gap-1.5';
  if (pmfbyBtn) pmfbyBtn.className = baseBtnClass;
  if (legalBtn) legalBtn.className = baseBtnClass;
  if (receiptBtn) receiptBtn.className = baseBtnClass;

  if (pmfbyDoc) pmfbyDoc.classList.add('hidden');
  if (legalDoc) legalDoc.classList.add('hidden');
  if (receiptDoc) receiptDoc.classList.add('hidden');

  if (docType === 'pmfby') {
    if (pmfbyDoc) pmfbyDoc.classList.remove('hidden');
    if (pmfbyBtn) pmfbyBtn.className = 'bg-blue-600 text-white font-bold text-xs px-3.5 py-2 rounded-xl shadow-sm transition flex items-center gap-1.5';
    loadDossierData();
  } else if (docType === 'legal') {
    if (legalDoc) legalDoc.classList.remove('hidden');
    if (legalBtn) legalBtn.className = 'bg-amber-600 text-white font-bold text-xs px-3.5 py-2 rounded-xl shadow-sm transition flex items-center gap-1.5';
    loadDealerLegalNotice();
  } else if (docType === 'receipt') {
    if (receiptDoc) receiptDoc.classList.remove('hidden');
    if (receiptBtn) receiptBtn.className = 'bg-emerald-600 text-white font-bold text-xs px-3.5 py-2 rounded-xl shadow-sm transition flex items-center gap-1.5';
    loadDossierData();
  }
}

async function loadDealerLegalNotice(inputId) {
  try {
    const url = inputId ? `/api/legal-notice/dealer?input_id=${inputId}` : '/api/legal-notice/dealer';
    const res = await fetch(url);
    const n = await res.json();
    currentDealerNotice = n;

    if (n) {
      if (document.getElementById('legal-notice-id')) document.getElementById('legal-notice-id').innerText = n.notice_no;
      if (document.getElementById('legal-notice-date')) document.getElementById('legal-notice-date').innerText = n.date;
      if (document.getElementById('legal-farmer-name')) document.getElementById('legal-farmer-name').innerText = n.farmer.name;
      if (document.getElementById('legal-farmer-mobile')) document.getElementById('legal-farmer-mobile').innerText = n.farmer.mobile;
      if (document.getElementById('legal-farmer-loc')) document.getElementById('legal-farmer-loc').innerText = `${n.village}, ${n.tehsil} (${n.district})`;
      if (document.getElementById('legal-farmer-land')) document.getElementById('legal-farmer-land').innerText = `खसरा ${n.farmer.khasra_no} (${n.farmer.total_land_acres} एकड़)`;
      if (document.getElementById('legal-dealer-name')) document.getElementById('legal-dealer-name').innerText = n.target_input.dealer_name;
      if (document.getElementById('legal-prod-name')) document.getElementById('legal-prod-name').innerText = n.target_input.product_name;
      if (document.getElementById('legal-batch-no')) document.getElementById('legal-batch-no').innerText = n.target_input.batch_no;
      if (document.getElementById('legal-bill-no')) document.getElementById('legal-bill-no').innerText = `${n.target_input.dealer_invoice_no} (${n.target_input.purchase_date})`;
      if (document.getElementById('legal-sign-name')) document.getElementById('legal-sign-name').innerText = n.farmer.name;
      if (document.getElementById('legal-sign-loc')) document.getElementById('legal-sign-loc').innerText = `ग्राम ${n.village}, तहसील ${n.tehsil}`;
    }
  } catch (err) {
    console.error('Failed to load dealer legal notice', err);
  }
}

function shareActiveDocOnWhatsApp() {
  if (activeDossierDoc === 'legal') {
    if (currentDealerNotice && currentDealerNotice.whatsapp_share_url) {
      window.open(currentDealerNotice.whatsapp_share_url, '_blank');
    } else {
      showToast('कानूनी नोटिस तैयार नहीं है');
    }
  } else if (activeDossierDoc === 'receipt') {
    if (currentDossier) {
      const token = currentDossier.claim_token || currentDossier.dossier_id;
      const farmer = currentDossier.farmer;
      const text = `*🌾 PMFBY 72-घंटे दावा पावती टोकन रसीद*\n-----------------------------------\n📄 टोकन क्र.: *${token}*\n👤 कृषक: ${farmer.name}\n📍 ग्राम/तहसील: ${farmer.village}, ${farmer.tehsil} (${currentDossier.district_info ? currentDossier.district_info.name_hi : 'देवास'})\n🌱 फसल: ${farmer.crop} | खसरा: ${farmer.khasra_no}\n⚠️ नुकसान: ${currentDossier.calamity.estimated_loss_percent}% (${currentDossier.calamity.calamity_type})\n🛡️ बीमा कंपनी: ${currentDossier.district_info ? currentDossier.district_info.insurance_company : 'HDFC ERGO'}\n✅ समय-सीमा: 72 घंटे के भीतर प्रमाणित दर्ज\n-----------------------------------\n_यह रसीद बीमा सर्वेक्षक / SADO निरीक्षण हेतु मान्य विधिक साक्ष्य है।_`;
      window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
    } else {
      showToast('पावती तैयार नहीं है');
    }
  } else {
    shareOnWhatsApp();
  }
}

// ==================== LIVE MANDI BHAV & CROP DOCTOR ====================
let currentMandiData = null;
let currentCropDiseases = [];
let selectedComparisonCrop = 'soybean';

async function loadMandiRates(forceRefresh = false) {
  const refreshBtn = document.getElementById('mandi-refresh-btn');
  if (refreshBtn) refreshBtn.classList.add('animate-spin');

  try {
    const dist = currentProfile.district || 'dewas';
    const tehsil = currentProfile.tehsil || 'सोनकच्छ';
    const village = currentProfile.village || 'बेड़ाखेड़ी';
    const res = await fetch(`/api/mandi-rates?district=${dist}&tehsil=${encodeURIComponent(tehsil)}&village=${encodeURIComponent(village)}&crop=${encodeURIComponent(selectedComparisonCrop)}`);
    const data = await res.json();
    currentMandiData = data;

    if (data && data.commodities) {
      const mandiCount = data.nearby_mandis ? data.nearby_mandis.length : 4;
      const vClean = currentProfile.village ? currentProfile.village.split('/')[0].split('(')[0].trim() : (data.village || 'बेड़ाखेड़ी');
      const tClean = currentProfile.tehsil ? currentProfile.tehsil.split('(')[0].trim() : (data.tehsil || 'सोनकच्छ');
      const dClean = currentProfile.district_name_hi ? currentProfile.district_name_hi.split('(')[0].trim() : (currentProfile.district ? currentProfile.district.toUpperCase() : (data.district || 'देवास'));

      if (document.getElementById('dash-mandi-subtitle')) {
        const subStr = data.nearby_mandis && data.nearby_mandis.length 
          ? data.nearby_mandis.map(m => `${m.short_name.split(' ')[0]} (${m.distance_km}km)`).join(' • ')
          : `${data.mandi_name} (${data.sub_mandi_context})`;
        document.getElementById('dash-mandi-subtitle').innerText = subStr;
      }
      if (document.getElementById('mandi-doc-loc-badge')) {
        document.getElementById('mandi-doc-loc-badge').innerText = `${dClean} (${tClean} - ${vClean}) • नजदीकी ${mandiCount} मंडियां`;
      }
      if (document.getElementById('mandi-comparison-loc-badge')) {
        document.getElementById('mandi-comparison-loc-badge').innerText = `ग्राम ${vClean} (${tClean}) से नजदीकी ${mandiCount} मंडियां`;
      }
      if (document.getElementById('mandi-sync-time')) {
        document.getElementById('mandi-sync-time').innerText = `अद्यतन: ${data.time}`;
      }

      // Render Dashboard cards using crop comparison
      renderMandiDashboardCards(data.crop_comparison);

      // Render Multi-Mandi 4-card comparison
      renderNearbyMandisComparison(data.crop_comparison, data.nearby_mandis);

      // Render full commodities table for primary mandi
      renderMandiFullTable(data.commodities);

      // Calculate freight profit
      calculateFreightProfit();

      if (forceRefresh) {
        showToast(`✓ 4 नजदीकी मंडियों के ताजा भाव लोड हुए`);
      }
    }
  } catch (err) {
    console.error('Failed to load mandi rates', err);
    if (forceRefresh) showToast('मंडी भाव लोड करने में त्रुटि');
  } finally {
    if (refreshBtn) {
      setTimeout(() => refreshBtn.classList.remove('animate-spin'), 400);
    }
  }
}

function selectMandiComparisonCrop(cropKey) {
  selectedComparisonCrop = cropKey;

  // Update dashboard pill buttons
  document.querySelectorAll('.dash-crop-btn').forEach(btn => {
    if (btn.getAttribute('data-crop') === cropKey) {
      btn.className = 'dash-crop-btn px-2.5 py-1 rounded-lg bg-emerald-700 text-white font-bold text-[11px] whitespace-nowrap shadow-sm';
    } else {
      btn.className = 'dash-crop-btn px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-[11px] whitespace-nowrap';
    }
  });

  // Update comparison tab pill buttons
  document.querySelectorAll('.comp-crop-btn').forEach(btn => {
    if (btn.getAttribute('data-crop') === cropKey) {
      btn.className = 'comp-crop-btn px-3 py-1.5 rounded-xl bg-emerald-700 text-white font-bold text-xs whitespace-nowrap shadow-sm';
    } else {
      btn.className = 'comp-crop-btn px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs whitespace-nowrap';
    }
  });

  loadMandiRates();
}

function renderMandiDashboardCards(cropComp) {
  const container = document.getElementById('dash-mandi-cards');
  if (!container || !cropComp || !cropComp.items) return;

  container.innerHTML = cropComp.items.map(m => {
    const isBest = m.is_best_price;
    const diffBadge = m.diff_vs_nearest > 0 
      ? `<span class="text-[10px] font-black text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">+₹${m.diff_vs_nearest} तेज</span>`
      : (m.diff_vs_nearest === 0 ? `<span class="text-[10px] text-slate-500 font-medium">आधार भाव</span>` : `<span class="text-[10px] text-red-600 font-bold">-₹${Math.abs(m.diff_vs_nearest)}</span>`);

    return `
      <div class="p-2.5 rounded-xl border transition ${isBest ? 'bg-emerald-50/80 border-emerald-300 shadow-sm ring-1 ring-emerald-400' : 'bg-slate-50 border-slate-200/80 hover:bg-slate-100/60'}">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1 truncate">
            <span class="font-bold text-slate-900 text-xs truncate">${m.short_name.split(' ')[0]}</span>
            <span class="text-[10px] text-slate-500 font-medium whitespace-nowrap">(${m.distance_km}km)</span>
          </div>
          ${isBest ? '<span class="text-[9px] font-black bg-emerald-700 text-white px-1.5 py-0.2 rounded shadow-xs">सर्वोत्तम</span>' : diffBadge}
        </div>
        <div class="mt-1 flex items-baseline justify-between">
          <span class="text-base font-black text-slate-900 tracking-tight">₹${m.modal_price}</span>
          <span class="text-[10px] text-slate-500">${m.arrival.split(' ')[0]} बोरी</span>
        </div>
        <div class="text-[10px] text-slate-400 truncate mt-0.5">${m.crop}</div>
      </div>
    `;
  }).join('');

  if (document.getElementById('dash-freight-text') && cropComp.freight_advice) {
    document.getElementById('dash-freight-text').innerText = cropComp.freight_advice.replace(/[\*_]/g, '');
  }
}

function renderNearbyMandisComparison(cropComp, nearbyMandis) {
  const container = document.getElementById('mandi-comparison-grid');
  if (!container || !cropComp || !cropComp.items) return;

  container.innerHTML = cropComp.items.map(m => {
    const isBest = m.is_best_price;
    const isNearest = m.is_nearest;
    const trendIcon = m.trend_type === 'up' ? '📈' : (m.trend_type === 'down' ? '📉' : '⚖️');

    return `
      <div class="rounded-2xl p-4 border-2 transition space-y-3 flex flex-col justify-between ${isBest ? 'bg-gradient-to-b from-emerald-50/90 to-white border-emerald-500 shadow-md ring-2 ring-emerald-400/30' : 'bg-white border-slate-200 shadow-sm hover:border-slate-300'}">
        
        <div>
          <!-- Header with Distance & Badges -->
          <div class="flex items-start justify-between gap-1.5">
            <div>
              <div class="inline-flex items-center gap-1 text-[11px] font-bold ${isNearest ? 'text-blue-700 bg-blue-50 border border-blue-200' : 'text-slate-600 bg-slate-100'} px-2 py-0.5 rounded-md">
                <i data-lucide="map-pin" class="w-3 h-3"></i>
                <span>${m.distance_str}</span>
              </div>
              <h4 class="font-black text-slate-900 text-sm mt-1.5 leading-snug">${m.mandi_name}</h4>
              <span class="text-[10px] text-slate-500 block font-medium">${m.grade}</span>
            </div>
            ${isBest ? `
              <span class="bg-emerald-600 text-white text-[10px] font-black px-2 py-1 rounded-full shadow-xs whitespace-nowrap flex items-center gap-0.5">
                <span>⭐</span> सर्वोत्तम भाव
              </span>
            ` : (m.diff_vs_nearest > 0 ? `
              <span class="bg-emerald-100 text-emerald-800 text-[10px] font-black px-2 py-0.5 rounded-full border border-emerald-300 whitespace-nowrap">
                +₹${m.diff_vs_nearest} तेज
              </span>
            ` : `
              <span class="bg-slate-100 text-slate-600 text-[10px] font-bold px-2 py-0.5 rounded-full border border-slate-200 whitespace-nowrap">
                आधार भाव
              </span>
            `)}
          </div>

          <!-- Price Display -->
          <div class="mt-3 bg-slate-50/80 p-3 rounded-xl border border-slate-100 text-center">
            <span class="text-[10px] text-slate-400 font-bold block uppercase tracking-wider">मॉडल (औसत) भाव</span>
            <div class="text-2xl font-black text-slate-900 tracking-tight my-0.5">
              ₹${m.modal_price}
              <span class="text-xs font-normal text-slate-500">/क्विंटल</span>
            </div>
            <div class="text-[11px] text-slate-500 font-medium">दायरा: ₹${m.min_price} - ₹${m.max_price}</div>
          </div>
        </div>

        <!-- Metric strip -->
        <div class="space-y-1.5 pt-2 border-t border-slate-100 text-xs">
          <div class="flex items-center justify-between text-slate-600 text-[11px]">
            <span>दैनिक आवक:</span>
            <span class="font-bold text-slate-800">${m.arrival}</span>
          </div>
          <div class="flex items-center justify-between text-slate-600 text-[11px]">
            <span>बाजार रुझान:</span>
            <span class="font-bold text-slate-800 flex items-center gap-1">${trendIcon} ${m.trend}</span>
          </div>
          ${m.note ? `<p class="text-[10px] text-slate-500 bg-amber-50/60 p-1.5 rounded-lg border border-amber-100 mt-1 leading-tight">💡 ${m.note}</p>` : ''}
        </div>

      </div>
    `;
  }).join('');
}

function calculateFreightProfit() {
  const qtlInput = document.getElementById('transport-qtl-input');
  const qtl = qtlInput ? Math.max(1, parseInt(qtlInput.value, 10) || 30) : 30;

  if (!currentMandiData || !currentMandiData.crop_comparison || !currentMandiData.crop_comparison.items) return;

  const items = currentMandiData.crop_comparison.items;
  const nearest = items.find(i => i.is_nearest) || items[0];
  const best = items.find(i => i.is_best_price) || items[items.length - 1];

  const resultsContainer = document.getElementById('transport-calc-results');
  const adviceBanner = document.getElementById('transport-advice-text');

  const nearestRev = qtl * nearest.modal_price;
  const bestRev = qtl * best.modal_price;
  const grossDiff = bestRev - nearestRev;

  const extraKm = Math.max(0, best.distance_km - nearest.distance_km);
  const extraTrolleyFare = roundFare(extraKm);
  const netExtraProfit = Math.max(0, grossDiff - extraTrolleyFare);

  if (resultsContainer) {
    resultsContainer.innerHTML = `
      <div class="bg-white p-2.5 rounded-xl border border-slate-200">
        <span class="text-[10px] text-slate-400 block">${nearest.short_name} (लोकल)</span>
        <span class="text-sm font-black text-slate-800">₹${nearestRev.toLocaleString('en-IN')}</span>
        <span class="text-[10px] text-slate-500 block">@ ₹${nearest.modal_price}/क्वि.</span>
      </div>
      <div class="bg-white p-2.5 rounded-xl border border-emerald-300">
        <span class="text-[10px] text-emerald-800 block font-bold">${best.short_name} (सर्वोत्तम)</span>
        <span class="text-sm font-black text-emerald-800">₹${bestRev.toLocaleString('en-IN')}</span>
        <span class="text-[10px] text-slate-500 block">@ ₹${best.modal_price}/क्वि.</span>
      </div>
      <div class="bg-white p-2.5 rounded-xl border border-amber-200">
        <span class="text-[10px] text-amber-800 block">अतिरिक्त ट्रैक्टर भाड़ा (${extraKm} km)</span>
        <span class="text-sm font-black text-amber-700">-₹${extraTrolleyFare.toLocaleString('en-IN')}</span>
        <span class="text-[10px] text-slate-400 block">डीजल व समय लागत</span>
      </div>
      <div class="bg-emerald-600 text-white p-2.5 rounded-xl border border-emerald-700 shadow-sm">
        <span class="text-[10px] text-emerald-100 block font-bold">शुद्ध अतिरिक्त बचत / लाभ</span>
        <span class="text-sm font-black text-white">+₹${netExtraProfit.toLocaleString('en-IN')}</span>
        <span class="text-[10px] text-emerald-200 block">भाड़ा काटकर शुद्ध बचत</span>
      </div>
    `;
  }

  if (adviceBanner) {
    if (netExtraProfit > 500) {
      adviceBanner.innerText = `💡 सलाह: ${qtl} क्विंटल माल पर अतिरिक्त भाड़ा (~₹${extraTrolleyFare}) काटकर भी आपको ${best.short_name} में ₹${netExtraProfit.toLocaleString('en-IN')} का शुद्ध अतिरिक्त मुनाफा होगा। माल ${best.short_name} ले जाना अधिक लाभकारी है!`;
    } else {
      adviceBanner.innerText = `💡 सलाह: ${qtl} क्विंटल उपज के लिए अतिरिक्त भाड़े के कारण शुद्ध लाभ सीमित है। स्थानीय ${nearest.short_name} में बेचना अधिक सुविधाजनक व सुरक्षित रहेगा।`;
    }
  }
}

function roundFare(extraKm) {
  if (extraKm <= 0) return 0;
  return Math.round(extraKm * 22) + 200;
}

function renderMandiFullTable(commodities) {
  const container = document.getElementById('mandi-commodities-container');
  if (!container || !commodities) return;

  container.innerHTML = commodities.map(c => {
    const trendIcon = c.trend_type === 'up' ? '📈' : (c.trend_type === 'down' ? '📉' : '⚖️');
    const trendColor = c.trend_type === 'up' ? 'text-emerald-700 bg-emerald-100 border-emerald-300' : (c.trend_type === 'down' ? 'text-rose-700 bg-rose-100 border-rose-300' : 'text-slate-700 bg-slate-100 border-slate-300');
    return `
      <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm hover:shadow-md transition space-y-3">
        <div class="flex items-start justify-between">
          <div>
            <h4 class="font-black text-slate-900 text-sm">${c.crop}</h4>
            <span class="text-[11px] text-slate-500 font-medium">ग्रेड: ${c.quality_grade || 'FAQ'}</span>
          </div>
          <span class="text-xs font-bold px-2 py-0.5 rounded-full border ${trendColor}">
            ${trendIcon} ${c.trend}
          </span>
        </div>

        <div class="bg-slate-50 p-3 rounded-xl border border-slate-100 grid grid-cols-2 gap-2 text-center">
          <div>
            <span class="text-[10px] text-slate-400 block font-medium">मॉडल भाव (औसत)</span>
            <span class="text-xl font-black text-emerald-800">₹${c.modal_price}</span>
            <span class="text-[10px] text-slate-400 block">${c.unit}</span>
          </div>
          <div>
            <span class="text-[10px] text-slate-400 block font-medium">दैनिक आवक</span>
            <span class="text-base font-bold text-slate-800 mt-1 block">${c.arrival}</span>
            <span class="text-[10px] text-slate-400">दायरा: ₹${c.min_price} - ₹${c.max_price}</span>
          </div>
        </div>

        ${c.note ? `<div class="text-[11px] text-slate-600 bg-amber-50/70 p-2 rounded-lg border border-amber-200/50">💡 ${c.note}</div>` : ''}
      </div>
    `;
  }).join('');
}

function filterMandiTable(cropKey) {
  document.querySelectorAll('.mandi-chip').forEach(btn => {
    btn.className = 'mandi-chip px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs transition';
  });
  if (window.event && window.event.target) {
    window.event.target.className = 'mandi-chip px-2.5 py-1 rounded-lg bg-emerald-700 text-white font-bold text-xs transition';
  }

  if (!currentMandiData || !currentMandiData.commodities) return;
  if (cropKey === 'all') {
    renderMandiFullTable(currentMandiData.commodities);
  } else {
    const filtered = currentMandiData.commodities.filter(c => (c.crop_key && c.crop_key === cropKey) || c.crop.toLowerCase().includes(cropKey));
    renderMandiFullTable(filtered);
  }
}

function shareMandiOnWhatsApp() {
  if (currentMandiData) {
    const p = currentProfile || {};
    const vName = p.village ? p.village.split('/')[0].split('(')[0].trim() : (currentMandiData.village || 'बेड़ाखेड़ी');
    const tName = p.tehsil ? p.tehsil.split('(')[0].trim() : (currentMandiData.tehsil || 'सोनकच्छ');
    const comp = currentMandiData.crop_comparison;
    const mandiCount = comp && comp.items ? comp.items.length : 4;

    let lines = [];
    if (comp && comp.items) {
      lines = [
        `🌾 *दैनिक कृषि उपज मंडी भाव - नजदीकी ${mandiCount} मंडियां*`,
        `📍 स्थान: *ग्राम ${vName}, तहसील ${tName}*`,
        `🌱 फसल: *${comp.crop_name}*`,
        `📅 दिनांक: ${currentMandiData.date} (${currentMandiData.time})`,
        `━━━━━━━━━━━━━━━━━━━━`
      ];

      comp.items.forEach((m, idx) => {
        const bestTag = m.is_best_price ? ' 🏆 *सर्वोत्तम भाव!*' : '';
        const diffTag = m.diff_vs_nearest > 0 ? ` (+₹${m.diff_vs_nearest} तेज)` : '';
        lines.push(`${idx + 1}. 🏛️ *${m.short_name}* (${m.distance_str})${bestTag}`);
        lines.push(`   • मॉडल भाव: *₹${m.modal_price} / क्विंटल*${diffTag}`);
        lines.push(`   • दायरा: ₹${m.min_price} - ₹${m.max_price} | आवक: ${m.arrival}`);
        if (m.note) lines.push(`   • _${m.note}_`);
        lines.push('');
      });

      lines.push(`━━━━━━━━━━━━━━━━━━━━`);
      lines.push(comp.freight_advice || '');
      lines.push(`\n_खेतप्रूफ: सही मंडी चुनें, अपनी मेहनत का पूरा मोल पाएं!_`);
    } else {
      lines = [
        `🌾 *दैनिक कृषि उपज मंडी भाव (${currentMandiData.mandi_name})*`,
        `📅 दिनांक: ${currentMandiData.date} (${currentMandiData.time})`,
        `━━━━━━━━━━━━━━━━━━━━`
      ];
      currentMandiData.commodities.forEach(c => {
        lines.push(`🌱 *${c.crop}*: मॉडल भाव *₹${c.modal_price} ${c.unit}* [${c.trend}]`);
      });
    }

    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(lines.join('\n'))}`, '_blank');
  } else {
    showToast('मंडी भाव लोड हो रहे हैं...');
  }
}

function speakMandiRates() {
  if (currentMandiData && currentMandiData.crop_comparison && currentMandiData.crop_comparison.items) {
    const comp = currentMandiData.crop_comparison;
    const best = comp.items.find(i => i.is_best_price) || comp.items[0];
    const nearest = comp.items.find(i => i.is_nearest) || comp.items[0];
    const text = `आज आपके गाँव के पास ${comp.crop_name} का भाव: सोनकच्छ उपमंडी में मॉडल भाव ${nearest.modal_price} रुपए है, जबकि सबसे अधिक भाव ${best.short_name} में ${best.modal_price} रुपए प्रति क्विंटल दर्ज हुआ है। दोनों में ${best.modal_price - nearest.modal_price} रुपए का अंतर है।`;
    speakText(text);
  } else if (currentMandiData && currentMandiData.commodities) {
    const top = currentMandiData.commodities[0];
    const text = `आज मंडी में ${top.crop} का मॉडल भाव ${top.modal_price} रुपए प्रति क्विंटल है। भाव दायरा ${top.min_price} से ${top.max_price} रुपए है।`;
    speakText(text);
  } else {
    showToast('मंडी भाव उपलब्ध नहीं');
  }
}

function switchMandiDoctorSubtab(sub) {
  const btnMandi = document.getElementById('btn-subtab-mandi');
  const btnDoctor = document.getElementById('btn-subtab-doctor');
  const panelMandi = document.getElementById('panel-mandi-rates');
  const panelDoctor = document.getElementById('panel-crop-doctor');

  if (sub === 'mandi') {
    if (panelMandi) panelMandi.classList.remove('hidden');
    if (panelDoctor) panelDoctor.classList.add('hidden');
    if (btnMandi) btnMandi.className = 'py-2.5 px-4 font-bold text-xs sm:text-sm border-b-2 border-emerald-600 text-emerald-800 transition flex items-center gap-1.5';
    if (btnDoctor) btnDoctor.className = 'py-2.5 px-4 font-bold text-xs sm:text-sm border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center gap-1.5';
  } else {
    if (panelMandi) panelMandi.classList.add('hidden');
    if (panelDoctor) panelDoctor.classList.remove('hidden');
    if (btnMandi) btnMandi.className = 'py-2.5 px-4 font-bold text-xs sm:text-sm border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center gap-1.5';
    if (btnDoctor) btnDoctor.className = 'py-2.5 px-4 font-bold text-xs sm:text-sm border-b-2 border-purple-600 text-purple-800 transition flex items-center gap-1.5';
    loadCropDoctor();
  }
}

// ==================== CROP DOCTOR (ICAR-IISR INDORE) ====================
async function loadCropDoctor() {
  try {
    const res = await fetch('/api/crop-doctor?crop=soybean');
    const data = await res.json();
    if (data && data.diseases) {
      currentCropDiseases = data.diseases;
      showDiseaseDetail('yellow_mosaic');
    }
  } catch (err) {
    console.error('Failed to load crop doctor', err);
  }
}

function selectDoctorSymptom(diseaseId) {
  const d = currentCropDiseases.find(item => item.id === diseaseId);
  if (d) {
    if (document.getElementById('dash-doc-disease-name')) {
      document.getElementById('dash-doc-disease-name').innerText = d.name_hi;
    }
    if (document.getElementById('dash-doc-symptom')) {
      document.getElementById('dash-doc-symptom').innerText = d.symptoms_hi;
    }
    if (document.getElementById('dash-doc-chemical')) {
      document.getElementById('dash-doc-chemical').innerText = d.recommendations.chemical_treatment;
    }
    showToast(`✓ चयनित: ${d.name_hi.split(' ')[0]}`);
  }
}

function showDiseaseDetail(diseaseId) {
  const d = currentCropDiseases.find(item => item.id === diseaseId) || (currentCropDiseases.length > 0 ? currentCropDiseases[0] : null);
  if (!d) return;

  const card = document.getElementById('doctor-diagnosis-card');
  if (!card) return;

  const rec = d.recommendations;
  const isEmergency = d.severity === 'EMERGENCY' || d.severity === 'CRITICAL';
  const badgeColor = isEmergency ? 'bg-red-100 text-red-800 border-red-300' : 'bg-amber-100 text-amber-800 border-amber-300';

  card.innerHTML = `
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
      <div>
        <div class="flex items-center gap-2">
          <h3 class="text-base sm:text-lg font-black text-slate-900">${d.name_hi}</h3>
          <span class="text-xs font-black px-2 py-0.5 rounded-full border ${badgeColor}">${d.severity}</span>
        </div>
        <p class="text-xs text-slate-500 mt-0.5">वाहक / कारण: <b>${d.vector}</b></p>
      </div>
      <button onclick="speakText('${d.name_hi}. ${rec.chemical_treatment}')" class="text-xs font-bold bg-purple-50 text-purple-800 px-3 py-1.5 rounded-xl border border-purple-200 hover:bg-purple-100 flex items-center gap-1">
        <i data-lucide="volume-2" class="w-3.5 h-3.5"></i>
        <span>सलाह सुनें</span>
      </button>
    </div>

    <div>
      <h4 class="font-bold text-slate-800 text-xs flex items-center gap-1.5">
        <i data-lucide="eye" class="w-4 h-4 text-purple-700"></i>
        <span>पहचान के मुख्य लक्षण:</span>
      </h4>
      <p class="text-xs text-slate-700 mt-1 leading-relaxed bg-slate-50 p-2.5 rounded-xl border border-slate-200/70">
        ${d.symptoms_hi}
      </p>
    </div>

    <div class="bg-purple-50/80 p-3.5 rounded-2xl border border-purple-200 space-y-2">
      <div class="font-bold text-purple-950 text-xs flex items-center gap-1.5">
        <i data-lucide="check-circle-2" class="w-4 h-4 text-purple-700"></i>
        <span>ICAR अनुमोदित रासायनिक उपचार (सही दवा व मात्रा प्रति एकड़):</span>
      </div>
      <div class="text-xs font-bold text-purple-900 bg-white p-2.5 rounded-xl border border-purple-200">
        💊 ${rec.chemical_treatment}
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-700 pt-1">
        <div>• <b>प्रचलित ब्रांड:</b> ${rec.brand_examples}</div>
        <div>• <b>पानी की मात्रा:</b> ${rec.water_volume}</div>
        <div>• <b>प्रतीक्षा अवधि (PHI):</b> ${rec.phi_days}</div>
        <div>• <b>नोजल:</b> हॉलो-कोन स्प्रे नोजल</div>
      </div>
    </div>

    <div class="bg-emerald-50/70 p-3 rounded-xl border border-emerald-200 text-xs">
      <span class="font-bold text-emerald-950 flex items-center gap-1">
        <i data-lucide="sprout" class="w-3.5 h-3.5 text-emerald-700"></i>
        <span>जैविक व देसी विकल्प:</span>
      </span>
      <p class="text-emerald-900 mt-1">${rec.organic_treatment}</p>
    </div>

    <div class="text-xs bg-amber-50 p-3 rounded-xl border border-amber-200 text-amber-950">
      ${d.expert_warning_hi}
    </div>
  `;

  if (window.lucide) lucide.createIcons();
}

async function runCropDoctorSearch() {
  const input = document.getElementById('doctor-search-input');
  if (!input || !input.value.trim()) {
    showToast('कृपया लक्षण लिखें');
    return;
  }
  const query = input.value.trim();
  try {
    const res = await fetch('/api/crop-doctor/diagnose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query, crop: 'soybean' })
    });
    const data = await res.json();
    if (data && data.diagnosis) {
      showDiseaseDetail(data.diagnosis.id);
      showToast(`✓ रोग पहचाना गया: ${data.diagnosis.name_hi.split(' ')[0]}`);
    }
  } catch (err) {
    showToast('रोग पहचान में त्रुटि');
  }
}

function openCropDoctorModal() {
  switchTab('tab-mandi-doctor');
  switchMandiDoctorSubtab('doctor');
}

// ==================== DISTRICT OFFICERS DIRECTORY ====================
async function loadOfficersDirectory() {
  try {
    const dist = currentProfile.district || 'dewas';
    const res = await fetch(`/api/officers?district=${dist}`);
    const data = await res.json();
    if (data) {
      if (document.getElementById('officers-dist-label')) {
        document.getElementById('officers-dist-label').innerText = data.district || 'देवास';
      }
      if (document.getElementById('officers-insurer-label')) {
        document.getElementById('officers-insurer-label').innerText = data.insurance_company || 'HDFC ERGO';
      }
    }
  } catch (err) {
    console.error('Failed to load officers directory', err);
  }
}

function copyActiveDocText() {
  if (activeDossierDoc === 'legal') {
    if (currentDealerNotice && currentDealerNotice.whatsapp_message) {
      navigator.clipboard.writeText(currentDealerNotice.whatsapp_message).then(() => {
        showToast('कानूनी शिकायत कॉपी हुई! सीधे व्हाट्सएप पर भेजें।');
      });
    }
  } else {
    copyDossierText();
  }
}

// ==================== TOAST NOTIFICATION ====================
function showToast(msg) {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toast-message');
  if (toast && toastMsg) {
    toastMsg.innerText = msg;
    toast.classList.remove('opacity-0', 'translate-y-20', 'pointer-events-none');
    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-20', 'pointer-events-none');
    }, 2800);
  }
}

// ==================== MOBILE CONNECT MODAL ====================
async function openMobileConnectModal() {
  const modal = document.getElementById('modal-mobile-connect');
  if (!modal) return;
  modal.classList.remove('hidden');

  try {
    const res = await fetch('/api/network-info');
    const data = await res.json();
    if (data && data.mobile_url) {
      const input = document.getElementById('mobile-connect-url-input');
      if (input) input.value = data.mobile_url;
      const qrImg = document.getElementById('mobile-qr-img');
      if (qrImg) qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(data.mobile_url)}`;

      const statusBadge = document.getElementById('mobile-status-text');
      const modalTitle = document.getElementById('mobile-modal-title');
      const modalSub = document.getElementById('mobile-modal-subtitle');

      if (data.is_public) {
        if (statusBadge) statusBadge.innerText = '🌐 इंटरनेट लाइव लिंक सक्रिय (हर जगह काम करेगा)';
        if (modalTitle) modalTitle.innerText = 'खेतप्रूफ लाइव वेबसाइट लिंक';
        if (modalSub) modalSub.innerText = 'यह लिंक कोई भी अपने मोबाइल फोन पर कहीं से भी खोल सकता है';
      } else {
        if (statusBadge) statusBadge.innerText = '📶 लोकल वाई-फाई / हॉटस्पॉट लिंक';
        if (modalTitle) modalTitle.innerText = 'मोबाइल फोन पर खोलें';
        if (modalSub) modalSub.innerText = 'फोन और लैपटॉप को एक ही वाई-फाई/हॉटस्पॉट से कनेक्ट रखें';
      }
    }
  } catch (e) {
    console.error('Failed to fetch network info', e);
  }

  if (window.lucide) {
    lucide.createIcons();
  }
}

function closeMobileConnectModal() {
  const modal = document.getElementById('modal-mobile-connect');
  if (modal) modal.classList.add('hidden');
}

function copyMobileUrl() {
  const input = document.getElementById('mobile-connect-url-input');
  if (input) {
    input.select();
    navigator.clipboard.writeText(input.value).then(() => {
      const btnText = document.getElementById('copy-btn-text');
      if (btnText) {
        btnText.innerText = 'कॉपी हुआ ✓';
        setTimeout(() => { btnText.innerText = 'कॉपी'; }, 2000);
      }
      showToast('✓ मोबाइल लिंक कॉपी हो गया! दोस्तों को भेजें।');
    }).catch(() => {
      showToast('लिंक कॉपी करने के लिए टेक्स्ट का चयन करें');
    });
  }
}

function shareMobileUrlOnWhatsApp() {
  const input = document.getElementById('mobile-connect-url-input');
  const url = input ? input.value : window.location.origin;
  const text = `🌾 *खेतप्रूफ (KhetProof) - किसान साथी वेब पोर्टल*\n\nहमारे खेत की फसल सुरक्षा, सटीक मौसम और आसपास की 4-5 मंडियों के लाइव भाव देखने के लिए लिंक खोलें:\n👉 ${url}\n\n(यह लिंक किसी भी मोबाइल पर सीधे खुलता है)`;
  window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
}


