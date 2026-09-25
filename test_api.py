import unittest
import json
from app import app

class TestKhetProof(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'KhetProof', res.data)

    def test_districts(self):
        res = self.client.get('/api/districts')
        self.assertEqual(res.status_code, 200)
        districts = json.loads(res.data)
        self.assertEqual(len(districts), 55, "All 55 MP districts must be loaded")
        dist_ids = [d['id'] for d in districts]
        self.assertIn('raisen', dist_ids)
        self.assertIn('vidisha', dist_ids)
        self.assertIn('indore', dist_ids)
        self.assertIn('ujjain', dist_ids)
        self.assertIn('jabalpur', dist_ids)
        self.assertIn('gwalior', dist_ids)
        self.assertIn('niwari', dist_ids)
        self.assertIn('mauganj', dist_ids)
        self.assertIn('maihar', dist_ids)
        self.assertIn('pandhurna', dist_ids)

    def test_scan_label(self):
        res = self.client.post('/api/scan-label', json={"sample_type": "weedicide"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['ocr_result']['batch_no'], 'SWB-7721-RAI')
        self.assertTrue(data['verification']['is_hazardous'])

    def test_imd_push_alert(self):
        res = self.client.post('/api/whatsapp/push-imd-alert')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('IMD', data['alert']['badge'])

    def test_icar_verification(self):
        # Test verified product
        res = self.client.post('/api/inputs/verify', json={"product_name": "IFFCO Sagarika"})
        data = json.loads(res.data)
        self.assertTrue(data['is_verified'])
        self.assertEqual(data['status'], 'VERIFIED')

        # Test fake/spurious weedicide (Raisen case)
        res_fake = self.client.post('/api/inputs/verify', json={"product_name": "Super Weed Burn 24D Mix"})
        data_fake = json.loads(res_fake.data)
        self.assertFalse(data_fake['is_verified'])
        self.assertTrue(data_fake['is_hazardous'])
        self.assertIn('नकली', data_fake['alert_title'])

    def test_calamity_and_timer(self):
        res = self.client.get('/api/calamity/status')
        self.assertEqual(res.status_code, 200)
        calamity = json.loads(res.data)
        self.assertTrue(calamity['active'])
        self.assertIn('seconds_left', calamity)

    def test_dossier_generation(self):
        res = self.client.get('/api/dossier')
        self.assertEqual(res.status_code, 200)
        dossier = json.loads(res.data)
        self.assertIn('dossier_id', dossier)
        self.assertIn(dossier['farmer']['name'], dossier['whatsapp_text'])

    def test_live_weather_api(self):
        # Test weather resolution for Dewas -> Sonkatch -> Berakhedi
        res = self.client.get('/api/weather?district=dewas&tehsil=Sonkatch&village=Berakhedi')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('temperature', data)
        self.assertIn('apparent_temp', data)
        self.assertIn('humidity', data)
        self.assertIn('advisory_hi', data)
        self.assertIn('forecast_3day', data)
        self.assertEqual(len(data['forecast_3day']), 3)
        self.assertTrue('Berakhedi' in data['location'] or 'देवास' in data['district'])

    def test_dewas_sonkatch_berakhedi(self):
        # 1. Verify Dewas exists with Sonkatch and Berakhedi
        res = self.client.get('/api/districts')
        self.assertEqual(res.status_code, 200)
        districts = json.loads(res.data)
        dewas = next((d for d in districts if d['id'] == 'dewas'), None)
        self.assertIsNotNone(dewas, "Dewas district must exist")
        self.assertEqual(len(dewas['tehsils']), 8, "Dewas must have 8 tehsils")

        # 2. Verify Sonkatch tehsil exists
        sonkatch = next((t for t in dewas['tehsils'] if 'Sonkatch' in t['name_en']), None)
        self.assertIsNotNone(sonkatch, "Sonkatch tehsil must exist in Dewas")

        # 3. Verify Berakhedi village exists in Sonkatch
        has_berakhedi = any('Berakhedi' in v or 'बेड़ाखेड़ी' in v for v in sonkatch['villages'])
        self.assertTrue(has_berakhedi, "Berakhedi must be present in Sonkatch villages")

        # 4. Update profile to Dewas, Sonkatch, Berakhedi
        up_res = self.client.post('/api/profile', json={
            "district": "dewas",
            "tehsil": "सोनकच्छ (Sonkatch)",
            "village": "बेड़ाखेड़ी / बेरखेड़ी (Berakhedi)"
        })
        self.assertEqual(up_res.status_code, 200)

        # 5. Check generated dossier
        dos_res = self.client.get('/api/dossier')
        self.assertEqual(dos_res.status_code, 200)
        dos = json.loads(dos_res.data)
        self.assertEqual(dos['farmer']['district'], 'dewas')
        self.assertIn('HDFC ERGO', dos['legal_notice']['submission_target'])
        self.assertIn('बेड़ाखेड़ी', dos['whatsapp_text'])
        self.assertIn('सोनकच्छ', dos['whatsapp_text'])
        self.assertIn('देवास', dos['whatsapp_text'].lower())

    def test_network_info(self):
        res = self.client.get('/api/network-info')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('lan_ip', data)
        self.assertIn('mobile_url', data)
        self.assertEqual(data['port'], 5000)

    def test_whatsapp_webhook_handshake(self):
        # Meta verification handshake
        res = self.client.get('/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=khetproof_mp_farmer_token_2026&hub.challenge=test_challenge_123')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.decode('utf-8'), 'test_challenge_123')

    def test_whatsapp_webhook_incoming_twilio(self):
        # Simulated Twilio WhatsApp incoming POST
        res = self.client.post('/api/whatsapp/webhook', data={
            'From': 'whatsapp:+919826145892',
            'Body': 'मेरी 4 बीघा सोयाबीन में पानी भर गया'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'<Response>', res.data)
        self.assertIn(b'<Body>', res.data)

    def test_voice_extract(self):
        res = self.client.post('/api/voice-extract', json={
            "speech_text": "कल रात की तेज बारिश से मेरी 5 बीघा सोयाबीन में पानी भर गया, पूरी फसल डूब गई",
            "auto_trigger": True
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('अतिवृष्टि', data['extracted']['calamity_type'])
        self.assertIn('सोयाबीन', data['extracted']['crop'])
        self.assertTrue(data['calamity_state']['active'])

    def test_dealer_legal_notice(self):
        res = self.client.get('/api/legal-notice/dealer')
        self.assertEqual(res.status_code, 200)
        notice = json.loads(res.data)
        self.assertIn('notice_no', notice)
        self.assertIn('कीटनाशी अधिनियम 1968', notice['whatsapp_message'])
        self.assertIn('whatsapp_share_url', notice)
        self.assertTrue(any('धारा 21' in c['act'] for c in notice['legal_clauses']))
        self.assertTrue(any('धारा 29' in c['act'] for c in notice['legal_clauses']))

    def test_sync_offline(self):
        import uuid
        sample_offline_input = {
            "id": f"inp_off_{uuid.uuid4().hex[:6]}",
            "product_name": "IFFCO सागरिका दानेदार",
            "batch_no": "SG-OFF-99",
            "category": "Bio-stimulant",
            "dealer_name": "सोनकच्छ कृषि केंद्र",
            "dealer_invoice_no": "SON-101",
            "purchase_date": "2026-06-20"
        }
        res = self.client.post('/api/sync-offline', json={

            "inputs": [sample_offline_input],
            "calamity": {
                "district": "dewas",
                "calamity_type": "ओलावृष्टि (Hailstorm)",
                "notes": "ऑफ़लाइन खेत से दर्ज",
                "crop": "सोयाबीन"
            }
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['synced_inputs'], 1)

    def test_mandi_rates_api(self):
        res = self.client.get('/api/mandi-rates?district=dewas&tehsil=सोनकच्छ&village=बेड़ाखेड़ी&crop=soybean')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('commodities', data)
        self.assertGreater(len(data['commodities']), 3)
        self.assertIn('nearby_mandis', data)
        self.assertEqual(len(data['nearby_mandis']), 4, "Must resolve 4 nearby mandis for Dewas/Sonkatch")
        
        # Check nearby mandi properties
        mandi_names = [m['short_name'] for m in data['nearby_mandis']]
        self.assertTrue(any('सोनकच्छ' in n for n in mandi_names))
        self.assertTrue(any('देवास' in n for n in mandi_names))
        self.assertTrue(any('उज्जैन' in n for n in mandi_names))
        self.assertTrue(any('इंदौर' in n for n in mandi_names))

        # Check distances
        distances = [m['distance_km'] for m in data['nearby_mandis']]
        self.assertEqual(distances, [9, 32, 54, 68])

        # Check crop comparison
        self.assertIn('crop_comparison', data)
        comp = data['crop_comparison']
        self.assertEqual(len(comp['items']), 4)
        self.assertIn('इंदौर', comp['best_mandi'])
        self.assertEqual(comp['best_modal'], 4890)
        self.assertIn('freight_advice', comp)

    def test_multi_crop_mandi_comparison(self):
        # Test Garlic comparison (Ujjain should be highest or premium)
        res_garlic = self.client.get('/api/mandi-rates?district=dewas&tehsil=सोनकच्छ&village=बेड़ाखेड़ी&crop=garlic')
        self.assertEqual(res_garlic.status_code, 200)
        data_g = json.loads(res_garlic.data)
        comp_g = data_g['crop_comparison']
        self.assertIn('उज्जैन', comp_g['best_mandi'])
        self.assertGreaterEqual(comp_g['best_modal'], 15500)

    def test_crop_doctor_api(self):
        # 1. Get database
        res = self.client.get('/api/crop-doctor?crop=soybean')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(len(data['diseases']), 4)

        # 2. Diagnose symptom: Yellow mosaic / Semilooper
        diag_res = self.client.post('/api/crop-doctor/diagnose', json={
            "symptom": "पीला मोज़ेक",
            "crop": "सोयाबीन"
        })
        self.assertEqual(diag_res.status_code, 200)
        diag = json.loads(diag_res.data)
        self.assertTrue(diag['matched'])
        self.assertIn('chemical_treatment', diag['diagnosis']['recommendations'])
        self.assertIn('organic_treatment', diag['diagnosis']['recommendations'])

    def test_officers_directory_api(self):
        res = self.client.get('/api/officers?district=dewas')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('HDFC ERGO', data['insurer'])
        helplines = data['helplines']
        numbers = [h['number'] for h in helplines]
        self.assertIn('14447', numbers)
        self.assertIn('1800-180-1551', numbers)
        self.assertIn('181', numbers)

    def test_whatsapp_mandi_and_crop_doctor_simulation(self):
        # 1. Mandi Bhav inquiry via WhatsApp simulation
        res_mandi = self.client.post('/api/whatsapp/message', json={
            "text": "देवास मंडी में सोयाबीन भाव क्या है"
        })
        self.assertEqual(res_mandi.status_code, 200)
        data_m = json.loads(res_mandi.data)
        replies_m = data_m['replies']
        self.assertTrue(any('मंडी' in r['text'] or 'सोयाबीन' in r['text'] for r in replies_m))

        # 2. Crop Doctor inquiry via WhatsApp simulation
        res_doc = self.client.post('/api/whatsapp/message', json={
            "text": "सोयाबीन में इल्ली का प्रकोप है क्या दवा डालें"
        })
        self.assertEqual(res_doc.status_code, 200)
        data_d = json.loads(res_doc.data)
        replies_d = data_d['replies']
        self.assertTrue(any('इल्ली' in r['text'] or 'ICAR' in r['text'] or 'दवा' in r['text'] for r in replies_d))

    def test_dossier_claim_token(self):
        res = self.client.get('/api/dossier')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('claim_token', data)
        self.assertTrue(data['claim_token'].startswith('MP/PMFBY/2026/72H-'))
        self.assertIn('token_issue_time', data)

    def test_bhopal_nearby_mandis(self):
        # When farmer selects a village near Bhopal (e.g. Huzur / Khajuri Sadak)
        res = self.client.get('/api/mandi-rates?district=bhopal&tehsil=Huzur&village=Khajuri%20Sadak&crop=soybean')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['district'], 'bhopal')
        
        # Primary mandi must be Bhopal Karond
        self.assertIn('भोपाल करोंद', data['short_name'])
        
        # Must resolve 5 nearby mandis around Bhopal
        nearby_names = [m['short_name'] for m in data['nearby_mandis']]
        self.assertTrue(any('भोपाल करोंद' in n for n in nearby_names), "Must include Bhopal Karond Mandi")
        self.assertTrue(any('सीहोर' in n for n in nearby_names), "Must include Sehore Mandi")
        self.assertTrue(any('बैरसिया' in n for n in nearby_names), "Must include Berasia Mandi")
        self.assertTrue(any('रायसेन' in n for n in nearby_names), "Must include Raisen Mandi")
        self.assertTrue(any('विदिशा' in n for n in nearby_names), "Must include Vidisha Mandi")

        # Crucial check: Must NOT contain Sonkatch / Berakhedi fallback!
        self.assertFalse(any('सोनकच्छ' in n for n in nearby_names), "Bhopal must NOT fall back to Sonkatch")
        self.assertFalse(any('देवास' in n for n in nearby_names), "Bhopal must NOT fall back to Dewas")

    def test_bhopal_berasia_nearby_mandis(self):
        # When farmer selects Tehsil Berasia in Bhopal
        res = self.client.get('/api/mandi-rates?district=bhopal&tehsil=Berasia&village=Gunga&crop=wheat')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')

        # Primary nearest mandi must be Berasia (8 km)
        self.assertIn('बैरसिया', data['short_name'])
        self.assertEqual(data['distance_km'], 8)

        # Nearby mandis should include Bhopal, Vidisha, Sehore, Raisen
        nearby_names = [m['short_name'] for m in data['nearby_mandis']]
        self.assertTrue(any('बैरसिया' in n for n in nearby_names))
        self.assertTrue(any('भोपाल करोंद' in n for n in nearby_names))
        self.assertTrue(any('विदिशा' in n for n in nearby_names))

    def test_universal_district_mandi_switching(self):
        # Test Mandis for Sagar
        res_sag = self.client.get('/api/mandi-rates?district=sagar&tehsil=Sagar&village=Bina')
        self.assertEqual(res_sag.status_code, 200)
        data_sag = json.loads(res_sag.data)
        sag_names = [m['short_name'] for m in data_sag['nearby_mandis']]
        self.assertTrue(any('सागर' in n for n in sag_names))
        self.assertFalse(any('सोनकच्छ' in n for n in sag_names))

    def test_network_info(self):
        res = self.client.get('/api/network-info')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('mobile_url', data)
        self.assertIn('lan_ip', data)
        self.assertTrue(data['mobile_url'].startswith('http'))

    def test_pmfby_claim_payout_calculation(self):
        # 6.5 acres Soybean @ 65% loss
        res = self.client.get('/api/claim/calculate-payout?acres=6.5&loss_percent=65&crop=soybean')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['payout']['acres'], 6.5)
        self.assertEqual(data['payout']['hectares'], 2.63)
        self.assertEqual(data['payout']['sum_insured_per_ha'], 48000)
        self.assertEqual(data['payout']['estimated_payout'], 82056)
        self.assertIn('कंडिका 21.4', data['clause']['clause'])

        # Wheat 10 acres @ 50% loss
        res_wheat = self.client.get('/api/claim/calculate-payout?acres=10&loss_percent=50&crop=wheat')
        self.assertEqual(res_wheat.status_code, 200)
        data_wheat = json.loads(res_wheat.data)
        self.assertEqual(data_wheat['payout']['sum_insured_per_ha'], 55000)
        # 10 / 2.47105 = 4.047 ha * 55000 = 222585 * 0.50 = 111292
        self.assertTrue(data_wheat['payout']['estimated_payout'] > 100000)

    def test_pmfby_dossier_enhanced_evidence(self):
        res = self.client.get('/api/dossier')
        self.assertEqual(res.status_code, 200)
        d = json.loads(res.data)
        
        # Verify payout information
        self.assertIn('payout_info', d)
        self.assertIn('estimated_payout_formatted', d['payout_info'])
        
        # Verify satellite weather evidence
        self.assertIn('satellite_evidence', d)
        self.assertTrue(d['satellite_evidence']['surveyor_verified'])
        self.assertEqual(d['satellite_evidence']['recorded_rainfall_mm'], 84.6)
        
        # Verify SMS intimation
        self.assertIn('sms_intimation', d)
        self.assertEqual(d['sms_intimation']['target_number'], '14447')
        self.assertTrue(d['sms_intimation']['text'].startswith('PMFBY 72H CLAIM:'))
        
        # Verify call script
        self.assertIn('telephonic_operator_script', d)
        self.assertTrue(len(d['telephonic_operator_script']['script_points']) >= 4)
        
        # Verify photo evidence slots
        self.assertIn('photo_evidence_slots', d)
        self.assertEqual(len(d['photo_evidence_slots']), 3)

if __name__ == '__main__':
    unittest.main()


