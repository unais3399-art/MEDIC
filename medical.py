"""MEDIC — Medical knowledge base: recommendations, warnings & urgency logic."""


def get_recommendations(disease, confidence):
    disease_data = {
        'Flu': {
            'medications': ['Paracetamol (fever reducer)', 'Ibuprofen (pain relief)', 'Antihistamines (if congestion)'],
            'diet': ['Warm fluids (tea, soup)', 'Honey and lemon in warm water', 'Light nutritious food'],
            'lifestyle': ['Get 8-10 hours of sleep', 'Cold compress for fever', 'Use a humidifier'],
            'urgency': 'Medium',
            'warning': '⚠️ Watch for: high fever (>103°F), difficulty breathing, confusion.',
            'doctor': '👨‍⚕️ Consult a General Physician if symptoms persist beyond 3 days.',
            'emergency': '🚨 Call emergency services if: severe dehydration, chest pain, difficulty breathing.',
        },
        'Malaria': {
            'medications': ['Anti-malarial medication (prescription required)', 'Antipyretics for fever'],
            'diet': ['Plenty of fluids', 'Easy-to-digest foods', 'Electrolyte drinks'],
            'lifestyle': ['Complete bed rest', 'Use a mosquito net to prevent spread'],
            'urgency': 'High',
            'warning': '⚠️ DANGER: Malaria can be fatal if not treated promptly!',
            'doctor': '🚨 Visit an ER or Infectious Disease Specialist immediately.',
            'emergency': '🚨 EMERGENCY: Call an ambulance or go to the nearest ER immediately!',
        },
        'Cold': {
            'medications': ['Decongestants (stuffy nose)', 'Antihistamines (runny nose)', 'Pain relievers'],
            'diet': ['Ginger tea with honey', 'Chicken soup', 'Vitamin C rich foods'],
            'lifestyle': ['Rest for 2-3 days', 'Saline nasal spray', 'Stay hydrated'],
            'urgency': 'Low',
            'warning': '⚠️ Monitor for: fever >101°F or symptoms lasting >7 days.',
            'doctor': '👨‍⚕️ Consult a doctor if symptoms worsen or persist beyond 7 days.',
            'emergency': '🚨 Emergency if: difficulty breathing, confusion, persistent high fever.',
        },
        'Diabetes': {
            'medications': ['Insulin or oral medication (as prescribed)', 'Metformin (common first-line)'],
            'diet': ['Low-sugar, high-fiber diet', 'Complex carbohydrates', 'Lean protein', 'Vegetables'],
            'lifestyle': ['Regular exercise (30 min daily)', 'Monitor blood sugar regularly', 'Stay hydrated'],
            'urgency': 'High',
            'warning': '⚠️ DANGER: Untreated diabetes causes serious complications!',
            'doctor': '👨‍⚕️ Consult an Endocrinologist immediately.',
            'emergency': '🚨 EMERGENCY if: blood sugar >300, confusion, difficulty breathing.',
        },
        'Cancer': {
            'medications': ['Chemotherapy (if diagnosed)', 'Pain management medication', 'Immunotherapy'],
            'diet': ['High-protein, nutrient-rich foods', 'Antioxidant-rich foods (berries, leafy greens)'],
            'lifestyle': ['Stress management techniques', 'Join support groups'],
            'urgency': 'Critical',
            'warning': '⚠️ URGENT: Early detection is critical for cancer treatment!',
            'doctor': '🆘 URGENT — Consult an Oncologist immediately.',
            'emergency': '🚨 EMERGENCY: Call emergency services if severe pain or sudden changes occur.',
        },
        'Pneumonia': {
            'medications': ['Antibiotics (prescription required)', 'Fever reducers', 'Cough medication'],
            'diet': ['High fluid intake', 'Warm soups', 'Electrolyte drinks'],
            'lifestyle': ['Complete bed rest', 'Monitor oxygen levels'],
            'urgency': 'Critical',
            'warning': '⚠️ DANGER: Pneumonia can be life-threatening!',
            'doctor': '🆘 EMERGENCY — Go to hospital / call an ambulance immediately.',
            'emergency': '🚨 EMERGENCY: Difficulty breathing is a medical emergency. Call now!',
        },
        'Heart_Disease': {
            'medications': ['Nitroglycerin (for chest pain)', 'Blood pressure medication', 'Aspirin'],
            'diet': ['Low-sodium, low-fat diet', 'Heart-healthy foods (oats, nuts, fish)'],
            'lifestyle': ['Rest with head elevated', 'Monitor blood pressure'],
            'urgency': 'Critical',
            'warning': '⚠️ CRITICAL: Heart disease is a medical emergency!',
            'doctor': '🆘 EMERGENCY — Seek immediate medical help.',
            'emergency': '🚨 CALL EMERGENCY IMMEDIATELY! Chest pain + breathing difficulty = emergency.',
        },
    }

    default = {
        'medications': ['Follow prescribed medication', 'Avoid self-medication'],
        'diet': ['Maintain a balanced diet', 'Stay well-hydrated', 'Eat regular meals'],
        'lifestyle': ['Get adequate rest', 'Regular exercise', 'Stress management'],
        'urgency': 'Medium',
        'warning': '⚠️ Monitor your symptoms and consult a doctor if they worsen.',
        'doctor': '👨‍⚕️ Consult a healthcare professional for personalized advice.',
        'emergency': '🚨 Call emergency if: severe pain, difficulty breathing, confusion.',
    }

    result = dict(disease_data.get(disease, default))

    if confidence < 60:
        result['disclaimer'] = '⚠️ Low confidence prediction (<60%). Please consult a doctor for an accurate diagnosis.'
    elif confidence < 80:
        result['disclaimer'] = '⚕️ Moderate confidence (60–80%). Consider a second opinion if concerned.'
    else:
        result['disclaimer'] = '✅ High confidence prediction (>80%). Follow recommendations and see a doctor if symptoms persist.'
    return result