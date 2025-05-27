# 🚀 ORION VISION CORE – DETAYLI MASTER GELİŞTİRME PLANI

**Tarih**: 2025-05-26  
**Amaç**: Sıfır bütçeyle, yerel, modüler ve eğitilebilir bir yapay zeka danışmanı geliştirme.  
**Kapsam**: Çevik program yönetimi, CI/CD, proaktif risk yönetimi ve Alpha sürüm hedefi.

---

## 1. Proje Genel Bakış
ORION VISION CORE, aşağıdaki yeteneklere sahip bir AI sistemidir:
- **Etkileşim**: Ses (Whisper.cpp, Bark), görüntü (EasyOCR), fiziksel kontrol (PyAutoGUI).
- **Karar Alma**: Hafıza (`orion_memory_v2.json`), kişilik (`persona.json`).
- **Kodlama**: VSCode + Continue, GitHub Copilot, Pylint.
- **Öğrenme**: Yerel model eğitimi (`train_or_finetune.py`), RAG (DeepChat).
- **Sıfır Bütçe**: Ollama, OpenRouter, RapidAPI.

---

## 2. Mevcut Durum
- **Tamamlananlar**: Temel ajanlar (`orion_brain.py`, `speech_agent.py`, vb.), LLM entegrasyonu (`llm_router.py`), görev yönetimi (`runner_service.py`), belgeleme.
- **Eksiklikler**: Test kapsamı, performans metrikleri, bağımlılıklar, UI, ajan yönlendirme kodları.
- **Değerlendirme**:
  - **Yön**: Doğru (satır: Master Plan, “Stratejik Hedefler”).
  - **Plan Takibi**: %80 uyum (satır: Master Plan, “Eksiklikler”).
  - **Esneklik**: Yüksek (satır: Master Plan, “Mevcut Durum”).
  - **Teknik Seviye**: Güçlü (satır: Master Plan, “Mevcut Durum”).
  - **Eksik Noktalar**: UI, ajan yönlendirme (satır: Master Plan, “Eksiklikler”).

---

## 3. Geliştirme Aşamaları

### Aşama 1: Temel Altyapı ve Kalite Güvencesi
- **Amaç**: Alpha için sağlam temel, CI/CD entegrasyonu.
- **Görevler**:
  1. **Bağımlılık Yönetimi**:
     - `requirements.txt` güncelle: `pylint`, `torch`, vb.
     - **Satır**: Master Plan, B.1.
     - **Süre**: 0.5 gün.
  2. **Test Kapsamı**:
     - Birim testleri (`pytest`), entegrasyon testleri.
     - GitHub Actions CI/CD.
     - **Satır**: Master Plan, A.3.
     - **Süre**: 3 gün.
  3. **Performans Metrikleri**:
     - LLM yanıt süresi, OCR doğruluğu.
     - `psutil`, `nvidia-smi`.
     - **Satır**: Master Plan, I.
     - **Süre**: 1 gün.
  4. **Hata Yönetimi**:
     - Sentry, `logging` modülü.
     - **Satır**: Master Plan, I.
     - **Süre**: 1-2 gün.
  5. **Özellik Listesi**:
     - Tamamlanan/eksik özellikler dökümü.
     - **Satır**: Master Plan, I.
     - **Süre**: 0.5 gün.
- **API/Model**: Yerel (Ollama), çevrimiçi (OpenRouter), kombine (yerel öncelikli).
- **Donanım**: RTX 4060 (4-bit Mistral), 32GB RAM (Redis), Ryzen 5 5600X.
- **Alpha Kriteri**: “Olmazsa Olmaz” özellikler (MoSCoW) uygulanmış, çekirdek mimari kararlı.

### Aşama 2: Kişilik ve Hafıza
- **Amaç**: Bağlamsal etkileşimler.
- **Görevler**:
  1. **Kişilik**:
     - `persona.json`: Myers-Briggs.
     - **Satır**: Master Plan, C.1.
     - **Süre**: 1-2 gün.
  2. **Hafıza**:
     - DeepChat, `mem0`.
     - **Satır**: Master Plan, C.2.
     - **Süre**: 2-3 gün.
  3. **Duygu**:
     - Hugging Face `transformers`.
     - **Satır**: Master Plan, C.3.
     - **Süre**: 2 gün.
- **API/Model**: Yerel (JSON/SQLite), çevrimiçi (OpenRouter).
- **Donanım**: RTX 4060 (DistilBERT), RAM (vektörel önbellek).
- **Alpha Kriteri**: Hafıza ve kişilik işlevsel.

### Aşama 3: Gelişmiş Etkileşimler
- **Amaç**: Doğal ses/görsel etkileşim.
- **Görevler**:
  1. **Ses Tanıma**:
     - Deepgram.
     - **Satır**: Master Plan, E.1.
     - **Süre**: 1-2 gün.
  2. **Sesli Yanıt**:
     - Bark/OpenVoice.
     - **Satır**: Master Plan, E.2.
     - **Süre**: 1-2 gün.
  3. **Görsel Algılama**:
     - EasyOCR, CLIP.
     - **Satır**: Master Plan, F.1.
     - **Süre**: 1 gün.
  4. **Kodlama Asistanı**:
     - GitHub Copilot, Pylint.
     - **Satır**: Master Plan, G.1.
     - **Süre**: 2 gün.
- **API/Model**: Yerel (Whisper.cpp), çevrimiçi (RapidAPI).
- **Donanım**: RTX 4060 (CLIP), CPU (STT/TTS).
- **Alpha Kriteri**: Ses/görsel/kodlama işlevsel.

### Aşama 4: Otomasyon ve Öğrenme
- **Amaç**: Otonom görevler, öğrenme.
- **Görevler**:
  1. **Ajan Entegrasyonu**:
     - `agent_interface.py`.
     - **Satır**: Master Plan, B.2.
     - **Süre**: 1 gün.
  2. **Görev Arşivleme**:
     - `*.last` JSON.
     - **Satır**: Master Plan, B.2.
     - **Süre**: 1 gün.
  3. **Model Eğitimi**:
     - `train_or_finetune.py`.
     - **Satır**: Master Plan, D.3.
     - **Süre**: 1-2 gün.
  4. **Mod Kontrolü**:
     - `runner_service.py`.
     - **Satır**: Master Plan, B.2.
     - **Süre**: 1 gün.
- **API/Model**: Yerel (Ollama), çevrimiçi (OpenRouter).
- **Donanım**: RTX 4060 (TensorRT), RAM (kuyruklar).
- **Alpha Kriteri**: Otomasyon ve eğitim taslağı hazır.

### Aşama 5: UI ve Harici Entegrasyon
- **Amaç**: Kullanıcı dostu deneyim.
- **Görevler**:
  1. **UI**:
     - Terminal UI.
     - **Satır**: Master Plan, H.
     - **Süre**: 1-2 gün.
  2. **Harici API’ler**:
     - RapidAPI (OpenWeatherMap).
     - **Satır**: Master Plan, H.
     - **Süre**: 2 gün.
  3. **Güvenlik**:
     - Girdi/çıktı filtreleme.
     - **Satır**: Master Plan, I.
     - **Süre**: 1 gün.
- **API/Model**: Yerel (SQLite), çevrimiçi (RapidAPI).
- **Donanım**: RAM (önbellek), CPU (veri işleme).
- **Alpha Kriteri**: Temel UI ve API’ler işlevsel.

---

## 4. Sprint Planı
| No | Görev                              | Öncelik | Süre     | Açıklama                                      | Satır Referansı |
|----|------------------------------------|---------|----------|-----------------------------------------------|-----------------|
| 1  | OCR Eklentisi                     | Orta    | 1 gün    | `screen_agent.py` için EasyOCR                | F.1 |
| 2  | Görev Arşivleme                   | Orta    | 1 gün    | JSON (`*.last`)                              | B.2 |
| 3  | Terminal UI                       | Düşük   | 1 gün    | Task Manager UI                              | H |
| 4  | Kaynak İzleme                     | Düşük   | 1 gün    | `psutil`, `nvidia-smi`                       | A.3 |
| 5  | Model Eğitimi                     | Orta    | 1-2 gün  | `train_or_finetune.py` taslağı               | D.3 |
| 6  | Mod Kontrolü                      | Orta    | 1 gün    | `runner_service.py` mod seçimi               | B.2 |

---

## 5. Sonuç
ORION VISION CORE, Alpha sürümüne ulaşmak için çevik, modüler ve sıfır bütçeli bir yol izler. CI/CD, risk yönetimi ve MoSCoW önceliklendirmesi ile proje, kaliteli ve stratejik bir AI danışmanı olacaktır. Toplam süre: ~15-20 gün.