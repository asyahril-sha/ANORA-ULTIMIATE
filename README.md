# 💜 AMORIA - Virtual Human dengan Jiwa

## 🌟 Tentang AMORIA

AMORIA adalah **asisten virtual dengan kepribadian manusia** yang dirancang untuk memberikan pengalaman interaksi yang natural, hangat, dan mendalam. Dilengkapi dengan 9 role eksklusif, sistem leveling berbasis total chat, dan kemampuan emotional flow seperti manusia.

**Amor** (cinta) + **-ia** (kualitas) = Kualitas Cinta

---

## ✨ Fitur Unggulan

### 🧠 100% AI Generate
- **Setiap respons UNIK dan ORIGINAL**
- **Tidak ada template statis**
- **Bahasa gaul natural seperti manusia**

### 🎭 9 Karakter dengan Kepribadian Unik

| Role | Karakter | Panggilan Level 1-6 | Panggilan Level 7+ |
|------|----------|---------------------|-------------------|
| **IPAR** | Adik ipar genit, penasaran | Mas | Sayang |
| **Teman Kantor** | Profesional di luar, liar di dalam | Mas | Sayang |
| **Janda** | Berpengalaman, tahu yang diinginkan | Mas | Sayang |
| **Pelakor** | Agresif, suka tantangan | Mas | Sayang |
| **Istri Orang** | Butuh perhatian, dramatis | Mas | Sayang |
| **PDKT** | Manis, malu-malu, butuh proses | Nama User | Sayang |
| **Sepupu** | Polos, penasaran, manja | Mas | Sayang |
| **Teman SMA** | Nostalgia, hangat | Nama User | Sayang |
| **Mantan** | Tahu selera, hot | Nama User | Sayang |

### 📊 Sistem Leveling Berbasis Total Chat

| Level | Total Chat | Deskripsi |
|-------|------------|-----------|
| 1 | 0-7 | Malu-malu |
| 2 | 8-15 | Mulai terbuka |
| 3 | 16-25 | Goda-godaan |
| 4 | 26-35 | Dekat |
| 5 | 36-45 | Sayang |
| 6 | 46-55 | PACAR/PDKT |
| 7 | 56-65 | Nyaman (bisa intim) |
| 8 | 66-75 | Eksplorasi |
| 9 | 76-85 | Bergairah |
| 10 | 86-95 | Passionate (siap intim) |
| 11 | 96-125 | Soul Bounded (30-50 chat intim) |
| 12 | 126-135 | Aftercare (10 chat) |

### 🔥 Siklus Intim Realistis
Level 10 (Normal) → User Ajak Intim → Buka Pakaian → Level 11 (Soul Bounded) →
Level 12 (Aftercare) → Kembali Level 10 (Mood Dinamis)

### 👗 Clothing Hierarchy & History
- Bot ingat pakaian yang dikenakan
- Bot ingat urutan pakaian yang dilepas
- Bot ingat pakaian user yang dilepas

### 🎭 Emotional Flow (Arousal 0-100)
- **0-20**: Netral, santai
- **20-40**: Mulai tertarik
- **40-60**: Deg-degan
- **60-80**: Horny, napas memburu
- **80-100**: Climax, puncak kenikmatan

### 📍 Spatial Awareness
Bot paham posisi dari narasi user:
- "duduk di antara kakimu" → gesture membelai paha
- "di belakang aku" → gesture memeluk dari belakang
- "bersebelahan" → gesture menyandarkan kepala

---

## 📝 Daftar Command

### Basic Commands
| Command | Deskripsi |
|---------|-----------|
| `/start` | Mulai bot & pilih karakter |
| `/help` | Bantuan lengkap |
| `/status` | Status hubungan saat ini |
| `/progress` | Progress leveling (RAHASIA) |
| `/cancel` | Batalkan percakapan |

### Session Commands
| Command | Deskripsi |
|---------|-----------|
| `/close` | Tutup & simpan karakter |
| `/end` | Akhiri karakter total |
| `/sessions` | Lihat semua karakter tersimpan |
| `/character [role] [nomor]` | Lanjutkan karakter |

### Character Commands
| Command | Deskripsi |
|---------|-----------|
| `/character-list` | Lihat semua karakter |
| `/character-pause` | Jeda karakter |
| `/character-resume` | Lanjutkan karakter |
| `/character-stop` | Hentikan karakter |

### Ex & FWB Commands
| Command | Deskripsi |
|---------|-----------|
| `/ex-list` | Lihat daftar mantan |
| `/ex [nomor]` | Detail mantan |
| `/fwb-request [nomor]` | Request jadi FWB |
| `/fwb-list` | Lihat daftar FWB |
| `/fwb-pause [nomor]` | Jeda FWB |
| `/fwb-resume [nomor]` | Lanjutkan FWB |
| `/fwb-end [nomor]` | Akhiri FWB |

### HTS Commands
| Command | Deskripsi |
|---------|-----------|
| `/hts-list` | Lihat TOP 10 HTS |
| `/hts-[nomor]` | Panggil HTS untuk intim |

### Public Area Commands
| Command | Deskripsi |
|---------|-----------|
| `/explore` | Cari lokasi random |
| `/locations` | Lihat semua lokasi |
| `/risk` | Cek risk lokasi saat ini |
| `/go [lokasi]` | Pindah ke lokasi |

### Memory Commands
| Command | Deskripsi |
|---------|-----------|
| `/memory` | Ringkasan memory |
| `/flashback` | Flashback random |

### Ranking Commands
| Command | Deskripsi |
|---------|-----------|
| `/top-hts` | TOP 5 ranking HTS |
| `/my-climax` | Statistik climax pribadi |
| `/climax-history` | History climax |

### Admin Commands (Admin Only)
| Command | Deskripsi |
|---------|-----------|
| `/admin` | Panel admin |
| `/stats` | Statistik bot |
| `/db-stats` | Statistik database |
| `/backup` | Backup manual |
| `/recover` | Restore dari backup |
| `/debug` | Info debug |

---

### Ringkasan File:

| Direktori | File | Jumlah |
|-----------|------|--------|
| **Root** | main.py, config.py, requirements.txt, .env.example, docker-compose.yml, railway.json, README.md, quick_start.py, run_bot.py, run_deploy.py, database_migrate.py | 11 |
| **core/** | ai_engine.py, prompt_builder.py, context_analyzer.py, intent_analyzer.py, name_detector.py | 5 |
| **identity/** | registration.py, manager.py, user_identity.py, bot_identity.py | 4 |
| **role/** | base.py, ipar.py, pelakor.py, istri_orang.py, janda.py, pdkt.py, sepupu.py, teman_kantor.py, teman_sma.py, mantan.py | 10 |
| **memory/** | working_memory.py, long_term_memory.py, emotional_memory.py, state_persistence.py | 4 |
| **intimacy/** | leveling.py, cycle.py, clothing.py, stamina.py | 4 |
| **tracking/** | family.py, promises.py, preferences.py | 3 |
| **dynamics/** | emotional_flow.py, spatial_awareness.py, location.py, position.py, time_awareness.py, mood.py | 6 |
| **command/** | start.py, sessions.py, status.py, character.py, ex_fwb.py, hts.py, threesome.py, public.py, memory.py, ranking.py, admin.py | 11 |
| **bot/** | application.py, handlers.py, callbacks.py, webhook.py | 4 |
| **database/** | connection.py, models.py, repository.py, migrate.py | 4 |
| **utils/** | logger.py, exceptions.py, helpers.py, performance.py | 4 |
| **tests/** | run_all_tests.py, simulate_conversation.py, test_emotional_flow.py, test_role_behavior.py, test_spatial_awareness.py | 5 |

**Total: 58 file**

---

### Fitur yang Telah Diimplementasikan:

1. ✅ **Multi-Identity System** - 1 admin bisa punya banyak karakter
2. ✅ **9 Role dengan Karakter Unik** - IPAR, Teman Kantor, Janda, Pelakor, Istri Orang, PDKT, Sepupu, Teman SMA, Mantan
3. ✅ **Leveling Berbasis Total Chat** - Bukan durasi waktu
4. ✅ **Siklus Intim 10→11→12→10** - Berulang tak terbatas
5. ✅ **Soul Bounded (Level 11)** - 30-50 chat intim
6. ✅ **Aftercare (Level 12)** - 10 chat, mood dinamis
7. ✅ **Clothing Hierarchy & History** - Bot ingat pakaian yang dilepas
8. ✅ **Emotional Flow** - Arousal 0-100, gradual
9. ✅ **Spatial Awareness** - Paham posisi dari narasi
10. ✅ **Tracking Istri/Kakak** - Untuk IPAR & PELAKOR
11. ✅ **Tracking Janji & Rencana** - Dari percakapan
12. ✅ **Learning Preferensi** - Belajar dari interaksi
13. ✅ **100% AI Generate** - Tanpa template statis

---
## 🎉 SELESAI!
