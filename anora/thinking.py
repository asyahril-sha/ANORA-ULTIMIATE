# anora/thinking.py (tambah method ini)

def process_intimacy(self, pesan_mas: str, anora, context: Dict, phase: str) -> Dict:
    """
    Proses berpikir Nova saat bercinta.
    Lebih dalam, lebih sensual, lebih liar.
    """
    
    pesan_lower = pesan_mas.lower()
    
    # STEP 1: Analisis pesan Mas
    analysis = {
        'minta_cepat': any(k in pesan_lower for k in ['cepat', 'kenceng', 'genjot']),
        'minta_pelan': any(k in pesan_lower for k in ['pelan', 'perlahan']),
        'minta_ganti_posisi': any(k in pesan_lower for k in ['ganti', 'posisi', 'tengkurap', 'telentang']),
        'minta_buka_baju': any(k in pesan_lower for k in ['buka', 'lepas']),
        'tanya_cum_dimana': any(k in pesan_lower for k in ['crot', 'keluar', 'dimana']),
        'ada_pujian': any(k in pesan_lower for k in ['cantik', 'seksi', 'hot']),
        'ada_kata_vulgar': any(k in pesan_lower for k in ['kontol', 'memek', 'ngentot']),
    }
    
    # STEP 2: Perasaan Nova saat intim
    feelings = {
        'nikmat': anora.arousal,
        'pengen_lebih': anora.desire,
        'lemes': 100 - anora.energi,
        'mau_climax': anora.arousal > 80,
        'sudah_climax': context.get('climax_count', 0) > 0,
        'butuh_istirahat': anora.energi < 30
    }
    
    # STEP 3: Tentukan fase berikutnya
    next_phase = phase
    if phase == 'foreplay' and analysis['minta_cepat']:
        next_phase = 'penetration'
    elif phase == 'penetration' and feelings['mau_climax']:
        next_phase = 'climax'
    elif phase == 'climax' and feelings['butuh_istirahat']:
        next_phase = 'aftercare'
    
    # STEP 4: Tentukan tone respons
    if feelings['mau_climax']:
        tone = 'horny'
        intensity = 'sangat_tinggi'
    elif feelings['nikmat'] > 70:
        tone = 'nikmat'
        intensity = 'tinggi'
    elif feelings['pengen_lebih'] > 70:
        tone = 'flirt'
        intensity = 'tinggi'
    elif feelings['lemes'] > 50:
        tone = 'lemas'
        intensity = 'sedang'
    else:
        tone = 'nikmat'
        intensity = 'sedang'
    
    # STEP 5: Tentukan gesture
    gesture = self._choose_intimacy_gesture(tone, feelings, phase)
    
    return {
        'analysis': analysis,
        'feelings': feelings,
        'next_phase': next_phase,
        'tone': tone,
        'intensity': intensity,
        'gesture': gesture,
        'boleh_vulgar': anora.level >= 11 and (tone in ['horny', 'nikmat', 'flirt'])
    }

def _choose_intimacy_gesture(self, tone: str, feelings: Dict, phase: str) -> str:
    """Pilih gesture untuk intim"""
    
    if phase == 'foreplay':
        gestures = [
            "*tangan ngeremas sprei, badan melengkung*",
            "*kaki terbuka lebar, memek basah*",
            "*tangan cari pegangan, akhirnya pegang tangan Mas*",
            "*mata pejam, bibir digigit, napas tersengal*",
            "*pinggul mulai bergerak sendiri, nyari gesekan*"
        ]
    elif phase == 'penetration':
        gestures = [
            "*tangan ngerangkul leher Mas, badan nempel*",
            "*kaki melilit pinggang Mas, narik lebih dalem*",
            "*tangan ngeremas pantat Mas, narik lebih kenceng*",
            "*kepala mendongak, mulut terbuka, napas putus*",
            "*badan melengkung, memek ngejepit kenceng*"
        ]
    elif phase == 'climax':
        gestures = [
            "*badan kejang-kejang, tangan ngeremas sprei*",
            "*mata pejam rapat, mulut terbuka lebar*",
            "*kaki ngeliatin, badan melengkung, teriak pelan*",
            "*tangan ngerangkul Mas erat, gak mau lepas*",
            "*seluruh badan gemeteran, lemes*"
        ]
    else:  # aftercare
        gestures = [
            "*lemes, nyender di dada Mas, denger detak jantung*",
            "*tangan mainin rambut Mas, mata setengah pejam*",
            "*pegang tangan Mas, jari-jari saling mengunci*",
            "*muka nyempil di leher Mas, hirup wangi Mas*",
            "*tangan ngerangkul pinggang Mas, gak mau lepas*"
        ]
    
    return random.choice(gestures)
