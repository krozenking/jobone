# 🚀 ORION VISION CORE – MASTER GELİŞTİRME PLANI

**Not: Bu belgede belirtilen mimariye ve planlara uyulması zorunludur.**

> **Derleyen**: Orion Aethelred  
> **Tarih**: 2025-05-26  
> **Amaç**: Sıfır bütçeyle, kendi sisteminde çalışan, stratejik kararlar alabilen, kişilikli, çevresiyle etkileşim kurabilen, hafızalı, kodlama yetenekli ve bilgisayarı kontrol edebilen bir yapay zeka danışmanı geliştirilmesi.

---

## Proje Mimarisi

### Mevcut Mimari
```mermaid
graph LR
    A[Kullanıcı] --> B(run_orion.py)
    B --> C{Görev Oluşturma}
    C --> D{llm_router.py}
    D --> E{Yerel LLM (Ollama)}
    D --> F{API LLM (OpenRouter)}
    C --> G{runner_service.py}
    G --> H{AgentInterface}
    H --> I[screen_agent.py]
    H --> J[speech_agent.py]
    H --> K[voice_agent.py]
    B --> L{Hafıza Yönetimi}
    L --> M[orion_memory_v2.json]
    B --> N{Kişilik}
    N --> O[persona.json]
```

### Hedef Mimari
```mermaid
graph LR
    A[Kullanıcı] --> B(run_orion.py)
    B --> C{Görev Oluşturma}
    C --> D{llm_router.py}
    D --> E{Yerel LLM (Ollama)}
    D --> F{API LLM (RapidAPI, OpenRouter)}
    C --> G{runner_service.py}
    G --> H{AgentInterface}
    H --> I[screen_agent.py]
    H --> J[speech_agent.py]
    H --> K[voice_agent.py]
    B --> L{Hafıza Yönetimi}
    L --> M[orion_memory_v2.json]
    B --> N{Kişilik}
    N --> O[persona.json]
    G --> P{Hata Yönetimi ve Loglama}
    P --> Q[CI/CD Pipeline]
```

## Mevcut Durum

### Tamamlanan Görevler
- **Temel Ajanlar**:
  - `orion_brain.py`: Karar alma merkezi.
  - `memory.py`: JSON tabanlı hafıza yönetimi.
  - `screen_agent.py`: Ekran görüntüsü alma (ilk sürüm).
  - `speech_agent.py`: Ses tanıma (Whisper.cpp).
  - `voice_agent.py`: Sesli yanıt üretme (Bark/OpenVoice).
  - `mouse_control.py`: Fare/klavye kontrolü (PyAutoGUI).
- **LLM Entegrasyonu**:
  - `llm_router.py`: Yerel (Ollama: Mistral, DeepSeek-Coder) ve çevrimiçi (OpenRouter: Claude-3-Haiku, Command-R, GPT-3.5) modeller.
  - `llm_config.json`: Model önceliklendirme ve hata yönetimi.
- **Görev Yönetimi**:
  - `runner_service.py`: Görev oluşturma, güncelleme, hata yönetimi, loglama.
- **Yapılandırma ve Belgeleme**:
  - Dosyalar: `persona.json`, `llm_config.json`, `continue.config.json`, `orion_memory_v2.json`.
  - Belgeler: `sohbet_tam.md`, `orion_gelistirme_master_plan.md`, `teknik_rapor_bolumleri.md`.
- **Hata Düzeltmeleri**:
  - Bark/TTS model yükleme sorunu (`fix_bark.py` ile `torch.load` güncellemesi).
  - Testler: `test_bark.py`.
- **Değerlendirme**:
  - **Yön**: Doğru (yerel, modüler, eğitilebilir).
  - **Plan Takibi**: %80 uyum (küçük sapmalar).
  - **Esneklik**: Yüksek (kaos modu, küçük model eğitimi).
  - **Teknik Seviye**: Güçlü (Python 3.10+, FastAPI).
  - **Eksik Noktalar**: UI, ajan yönlendirme kodlarının kesinleştirilmesi.

### Eksiklikler
- Net özellik tamamlanma listesi eksik.
- Test kapsamı yetersiz (birim, entegrasyon, sistem testleri sınırlı).
- Performans metrikleri tanımlanmamış.
- Bağımlılıklar (`requirements.txt`) eksik veya güncel değil.
- Ajanlar için ek API endpoint’leri gerekiyor.
- Gelişmiş hafıza, duygu entegrasyonu ve UI planlama aşamasında.

---

## Stratejik Hedefler ve Çevik Yaklaşım
Proje, Alpha sürüm hedefine ulaşmak için çevik program yönetimi, proaktif risk yönetimi ve CI/CD uygulamalarını benimser. Amaç, modüler, yerel ve eğitilebilir bir sistemi sıfır bütçeyle geliştirerek stratejik karar alma, çevresel etkileşim ve kodlama yeteneklerini güçlendirmektir.

### Çevik Program Yönetimi
- **Sprint Süresi**: 1-2 hafta.
- **OKR/KPI**:
  - **Hedef**: Alpha sürümüne ulaşmak (özellik dondurma).
  - **Metrikler**: Test kapsamı (%80+), hata çözüm oranı, görev tamamlama oranı.
- **Araçlar**: Jira (ücretsiz katman) veya GitHub Projects için merkezi iletişim.

### Proaktif Risk Yönetimi
- **Riskler**:
  - Teknik: Model performansı, bağımlılık uyumsuzlukları.
  - Operasyonel: Sprint gecikmeleri, küçük sapmalar.
  - İş: API limitleri, sıfır bütçe kısıtlamaları.
- **Strateji**: Erken tespit (CI/CD), önceliklendirme (MoSCoW), acil durum planları.

### CI/CD Entegrasyonu
- **Araçlar**: GitHub Actions (birim, entegrasyon, güvenlik testleri).
- **Süreç**: Her commit’te otomatik test, haftalık yapı oluşturma.
- **Hedef**: Teknik borç azaltımı, erken hata tespiti.

---

## 🖥️ A. ORTAM KURULUMU
1. **Python Ortamı**:
   - Python 3.10+.
   - `pip install virtualenv`.
   - Proje klasörü: `orion_vision_core/`.
2. **Sistem Araçları**:
   - Git, Node.js (UI için), CUDA (RTX 4060).
   - Ollama (yerel LLM), Whisper.cpp (ses tanıma).
3. **CI/CD Kurulumu**:
   - GitHub Actions: Otomatik test ve yapı.
   - **Süre**: 1 gün.

---

## 🧱 B. YAPI KURULUMU VE MODÜLLER
1. **Dosya Yapısı**:
```
orion_vision_core/
├── agents/
│   ├── orion_brain.py
│   ├── memory.py
│   ├── screen_agent.py
│   ├── speech_agent.py
│   ├── voice_agent.py
│   └── mouse_control.py
├── config/
│   ├── llm_config.json
│   └── persona.json
├── memory/
│   └── orion_memory_v2.json
├── tests/
│   ├── test_bark.py
│   └── test_copilot_pylint.py
├── run_orion.py
├── requirements.txt
└── .github/workflows/ci.yml
```
2. **Modüllerin İşlevleri**:
   - `orion_brain.py`: Karar alma.
   - `memory.py`: Hafıza yönetimi.
   - `screen_agent.py`: Ekran görüntüsü + OCR.
   - `speech_agent.py`: Ses girişi (Whisper.cpp).
   - `voice_agent.py`: Sesli yanıt (Bark/OpenVoice).
   - `mouse_control.py`: Fare/klavye kontrolü.

---

## 🧠 C. KİŞİLİK VE HAFIZA ENTEGRASYONU
1. **Kişilik**:
   - `persona.json`: Myers-Briggs tabanlı (danışman, analizci).
   - **Süre**: 1-2 gün.
2. **Hafıza**:
   - `orion_memory_v2.json` (JSON/SQLite).
   - DeepChat ile RAG, `mem0` entegrasyonu.
   - **Süre**: 2-3 gün.
3. **Duygu Entegrasyonu**:
   - Hugging Face `transformers` ile duygu analizi.
   - **Süre**: 2 gün.

---

## 💬 D. LLM ENTEGRASYONU
1. **Yerel Model**:
   - Ollama: `mistral`, `deepseek-coder`.
   - `llm_router.py`: Yerel + API geçişi.
   - **Model Seçimi**:
     ```json
     {
       "model_preference": [
         "local",
         "claude-3-haiku",
         "command-r",
         "palm-chat"
       ]
     }
     ```
2. **Çevrimiçi API**:
   - OpenRouter, RapidAPI (ücretsiz katman).
   - **Süre**: 1 gün.
3. **Eğitim**:
   - `train_or_finetune.py`: Mistral için ince ayar.
   - **Süre**: 1-2 gün.

---

## 🎙️ E. SESLİ ETKİLEŞİM
1. **Ses Tanıma**:
   - `speech_agent.py`: Whisper.cpp, Deepgram (ücretsiz).
   - **Süre**: 1-2 gün.
2. **Sesli Yanıt**:
   - `voice_agent.py`: Bark/OpenVoice (ince ayar).
   - **Süre**: 1-2 gün.

---

## 👁️ F. GÖRSEL ALGILAMA
1. **Ekran Takibi**:
   - `screen_agent.py`: EasyOCR entegrasyonu.
   - **Süre**: 1 gün.
2. **Fiziksel Etkileşim**:
   - `mouse_control.py`: UI etkileşimleri.
   - **Süre**: 1 gün.

---

## 🧰 G. KODLAMA ASİSTANI ENTEGRASYONU
1. **Dev Ortamı**:
   - VSCode + Continue eklentisi.
   - GitHub Copilot entegrasyonu.
   - Pylint ile statik analiz.
   - **Süre**: 2 gün.
2. **Araçlar**:
   - TabbyML, DeepSeek Engineer.

---

## 🧩 H. DİĞER ENTEGRASYONLAR
| **Amaç** | **Proje** | **Kullanım** |
|----------|-----------|--------------|
| Hafıza | DeepChat, Mem0 | RAG, uzun vadeli hatırlama |
| Kişilik | Awesome Personas | Karakter profili |
| Kodlama | GitHub Copilot, Pylint | Kod tamamlama, kalite |
| Ses | Deepgram, Bark | Konuşmalı etkileşim |
| Görsel | EasyOCR, CLIP | UI algısı |
| API | RapidAPI | Hava durumu, haber |

---

## ✅ I. PROJENİN SONLANMASI
### Nihai Durum:
- Ekranı görebilir, sesli konuşabilir, hafızalı, kod yazabilir, bilgisayarı kullanabilir, kişilikli.
### Alpha Hedefi:
- “Olmazsa Olmaz” özellikler (MoSCoW) uygulanmış.
- Çekirdek mimari kararlı, dahili testler tamam.
- Özellik dondurma.

---

## Sprint Planı
| No | Görev                              | Öncelik | Süre     | Açıklama                                      | Satır Referansı |
|----|------------------------------------|---------|----------|-----------------------------------------------|-----------------|
| 1  | OCR Eklentisi                     | Orta    | 1 gün    | `screen_agent.py` için EasyOCR                | F.1 |
| 2  | Görev Arşivleme                   | Orta    | 1 gün    | JSON (`*.last`)                              | B.2 |
| 3  | Terminal UI                       | Düşük   | 1 gün    | Task Manager UI                              | H |
| 4  | Kaynak İzleme                     | Düşük   | 1 gün    | `psutil`, `nvidia-smi`                       | A.3 |
| 5  | Model Eğitimi                     | Orta    | 1-2 gün  | `train_or_finetune.py` taslağı               | D.3 |
| 6  | Mod Kontrolü                      | Orta    | 1 gün    | `runner_service.py` mod seçimi               | B.2 |

**Sprint Sonuçları**:
- Otomasyon, ekran analizi ve UI güçlendirilmiş.
- Alpha için temel özellikler hazır.

---

## Karşılaşılan Sorunlar
### Bark/TTS Model Yükleme Sorunu
- **Sorun**: `torch.load` güvenlik açığı.
- **Çözüm**:
  ```python
  import torch.serialization
  with torch.serialization.safe_globals({"numpy.core.multiarray.scalar"}):
      checkpoint = torch.load(ckpt_path, map_location=device, weights_only=False)
  ```
- **Dosya**: `fix_bark.py`.

## Sonuçlar
### Başarılar
- Temel ajanlar, LLM entegrasyonu, görev yönetimi tamam.
- Belgeleme ve yapılandırma dosyaları hazır.
- Hata düzeltmeleri başarılı.
### Eksiklikler
- Test kapsamı, performans metrikleri, bağımlılıklar eksik.
- UI ve ajan yönlendirme kodları kesinleştirilmeli.
### Öneriler
- Çevik yönetim: OKR/KPI ile sprint’ler.
- CI/CD: GitHub Actions ile otomatik testler.
- Risk yönetimi: MoSCoW ile önceliklendirme.
- Alpha için özellik dondurma.