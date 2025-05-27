# 🚀 ORION VISION CORE – MASTER GELİŞTİRME PLANI

**Not: Bu belgede belirtilen mimariye ve planlara uyulması zorunludur.**

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
```

## Tamamlanan Görevler

*   Temel aracıların (speech, voice, llm_router, memory, screen, mouse_control) uygulanması.
*   Projenin belgelenmesi ve planlanması için gerekli dosyaların oluşturulması (sohbet_tam.md, orion_gelistirme_master_plan.md, teknik_rapor_bolumleri.md).
*   Projenin yapılandırılması için gerekli dosyaların oluşturulması (persona.json, llm_config.json, continue.config.json).
*   Testlerin uygulanması ve hataların giderilmesi (test_bark.py, fix_bark.py).
*   `runner_service.py`'nin tam işlevsel hale getirilmesi (görev oluşturma, güncelleme, hata yönetimi, loglama).

# 🚀 ORION VISION CORE – MASTER GELİŞTİRME PLANI
> Derleyen: Orion Aethelred
> Tarih: 2025-05-21
> Amaç: Orion’un kendi sisteminde çalışan, stratejik kararlar alabilen, kişilikli ve çevresiyle etkileşim kurabilen yapay zekâ altyapısının sıfır bütçeyle geliştirilmesi.

---

## 🖥️ A. BAŞLANGIÇ: ORTAM KURULUMU (Kendi Bilgisayarında)

### 1. Python Ortamı Kurulumu
- Python 3.10+ kurulmalı
- `pip install virtualenv`
- Proje klasörü: `orion_vision_core/`

### 2. Gerekli Sistem Araçları
- Git
- Node.js (bazı UI araçları için)
- CUDA (sistem zaten RTX 4060 ile uyumlu)
- [Ollama](https://ollama.com/) kurulmalı (yerel LLM için)
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) kurulmalı (ses tanıma için)

---

## 🧱 B. YAPI KURULUMU VE MODÜLLER

### 1. Temel Dosya Yapısı
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
├── run_orion.py
└── requirements.txt
```

### 2. Modüllerin İşlevleri
- `orion_brain.py`: Tüm karar ve cevapların üretildiği merkez
- `memory.py`: Hafıza dosyalarının yönetimi
- `screen_agent.py`: Ekran görüntüsü + OCR işlemleri
- `speech_agent.py`: Mikrofon dinleme + Whisper STT
- `voice_agent.py`: Bark/TTS kullanarak sesli yanıt üretme
- `mouse_control.py`: PyAutoGUI ile fare/klavye kontrolü

---

## 🧠 C. KİŞİLİK ve HAFIZA ENTEGRASYONU

### 1. Orion’un Karakteri
- `Awesome Personas` ve `AI Persona Lab` kullanılarak tanımlanacak
- `persona.json` içinde:
  - Ton: Dürüst, stratejik, sakin
  - Roller: Danışman, analizci, teknik asistan

### 2. Hafıza Yönetimi
- `orion_memory_v2.json` temel hafıza
- `DeepChat` ile vektörel belge sorgulama (RAG)
- `mem0` ile uzun süreli hafıza deneysel olarak eklenebilir

---

## 💬 D. LLM ENTEGRASYONU (ZEKÂ)

### 1. Yerel Model
- Ollama kurulumu:
  ```
  ollama run mistral
  ollama run deepseek-coder
  ```
- `llm_router.py` ile yerel + API geçişi yapılır
  - `llm_router.py` artık hem yerel (Ollama) hem de çevrimiçi (OpenRouter, Google API gibi) LLM’ler ile çalışabiliyor.
  - Her görev için öncelik sırasına göre model deneniyor:
    1. Yerel model (örn: Mistral)
    2. API sırasıyla: `claude-3-haiku`, `command-r`, `palm-chat`
    3. Hepsi başarısızsa: hata mesajı döner
  - Kullanıcının bu sıralamayı `llm_config.json` veya görev bazlı `*.alt` görevlerinde tanımlayabileceği.

### 2. Ücretsiz API Desteği
- OpenRouter API anahtarı alınır
- `llm_config.json`:
  - Claude 3 Haiku
  - Command R
  - GPT 3.5
- Yedekleme: Together.ai, Groq

---

## 🎙️ E. SESLİ ETKİLEŞİM

### 1. STT – Ses Tanıma
- `speech_agent.py` ile Whisper.cpp üzerinden ses girişi
- Prompt üretimine yönlendirilir

### 2. TTS – Sesli Yanıt
- `voice_agent.py` içinde Bark ya da OpenVoice kullanılır

---

## 👁️ F. GÖRSEL ALGILAMA

### 1. Ekran Takibi
- `screen_agent.py` ile ekran görüntüsü alınır
- Tesseract + OpenCV ile OCR yapılır
- UI öğeleri tanımlanır

### 2. Fiziksel Etkileşim
- `mouse_control.py` ile tıklama/yazma yapılır
- Orion, gördüğü UI üzerinden işlem başlatabilir

---

## 🧰 G. KODLAMA ASİSTANI ENTEGRASYONU

### 1. Dev Ortamı
- VSCode + Continue eklentisi
- Ollama entegre edilir
- Orion’un hafızası continue.config.json ile bağlanabilir

### 2. Proje Yardımcıları
- `TabbyML`, `GPT-Engineer`, `SWE-Agent`, `DeepSeek Engineer`

---

## 🧩 H. PROJEYE ENTEGRE EDİLEBİLECEK DİĞER ARAÇLAR

| Amaç | Proje | Kullanım |
|------|--------|----------|
| Hafıza | DeepChat, Mem0 | Belge bağlamı + uzun vadeli hatırlama |
| Kişilik | Awesome Personas, Persona Mirror | Orion karakter profili |
| Kodlama | Tabby, Continue | Kod tamamlama + refactor |
| Sesli Asistan | Whisper Voice Assistant, Bark | Konuşmalı etkileşim |
| Ekran Takibi | screen_agent (custom) | UI algısı |
| Stratejik Karar | LLM + Hafıza | Rol tabanlı cevap üretimi |

---

## ✅ I. PROJENİN SONLANMASI

### Nihai Durum:
- Orion ekranı görebilir
- Sesli konuşabilir
- Yazılı hafızası vardır
- Kod yazabilir
- Bilgisayarı kullanabilir
- Kendi karakterine sahiptir

### Son Hedef:
- Hafızalı, etkileşimli, kendi kararlarını alabilen bir danışman-yapay zeka.

---

İstersen bu planı da `.md` veya `.pdf` olarak sana verebilirim.

## Karşılaşılan Sorunlar

### Bark/TTS Model Yükleme Sorunu

**Sorun:** Bark/TTS kütüphanesi kullanılırken, model yükleme sırasında bir güvenlik sorunuyla karşılaşıldı. Bu sorun, `torch.load` fonksiyonunun güvenli olmayan bir şekilde kullanılması nedeniyle ortaya çıktı.

**Çözüm:** `fix_bark.py` dosyası kullanılarak `generation.py` dosyası güncellendi. Bu güncelleme, `torch.load` fonksiyonuna `weights_only=False` parametresini ekleyerek ve `safe_globals` bağlamında çalıştırarak güvenlik sorununu çözdü.

```python
import torch.serialization
with torch.serialization.safe_globals({"numpy.core.multiarray.scalar"}):
    checkpoint = torch.load(ckpt_path, map_location=device, weights_only=False)
```

Bu düzeltme, Bark/TTS kütüphanesinin güvenli bir şekilde kullanılmasını sağladı.

## Sonuçlar

### Başarılar

* Temel aracıların (speech, voice, llm_router, memory, screen, mouse_control) uygulanması.
* Projenin belgelenmesi ve planlanması için gerekli dosyaların oluşturulması (sohbet_tam.md, orion_gelistirme_master_plan.md, teknik_rapor_bolumleri.md).
* Projenin yapılandırılması için gerekli dosyaların oluşturulması (persona.json, llm_config.json, continue.config.json).
* Testlerin uygulanması ve hataların giderilmesi (test_bark.py, fix_bark.py).

### Eksiklikler

* Projenin tam olarak hangi özelliklerinin tamamlandığı ve hangilerinin eksik olduğu belirsiz.
* Projenin test kapsamı hakkında yeterli bilgi yok.
* Projenin performans metrikleri hakkında bilgi yok.
* Projenin bağımlılıkları hakkında yeterli bilgi yok (requirements.txt).

### Öneriler

* Projenin özelliklerinin tamamlanma durumunu net bir şekilde belirten bir liste oluşturulmalı.
* Projenin test kapsamını artırmak için daha fazla test yazılmalı.
* Projenin performansını ölçmek için metrikler belirlenmeli ve düzenli olarak izlenmeli.
* Projenin bağımlılıkları güncel tutulmalı ve belgelenmeli.

## Öneriler

### Genel İyileştirmeler

* **Modülerlik ve Yeniden Kullanılabilirlik:** Projede kullanılan modüllerin (örneğin, `screen_agent.py`, `speech_agent.py`) daha modüler ve yeniden kullanılabilir hale getirilmesi, gelecekteki geliştirmeleri kolaylaştıracaktır. Bu, her bir modülün daha spesifik görevlere odaklanmasını ve farklı projelerde kullanılabilmesini sağlayacaktır.
* **Hata Yönetimi ve İzleme:** Projede kapsamlı bir hata yönetimi ve izleme sistemi kurulması, hataların daha hızlı tespit edilmesini ve çözülmesini sağlayacaktır. Bu, Sentry veya benzeri bir araç kullanılarak yapılabilir.
* **Test Kapsamının Artırılması:** Projenin test kapsamının artırılması, kodun kalitesini ve güvenilirliğini artıracaktır. Bu, birim testleri, entegrasyon testleri ve sistem testleri yazılarak yapılabilir.
* **Performans Optimizasyonu:** Projenin performansının düzenli olarak ölçülmesi ve optimize edilmesi, daha hızlı ve verimli çalışmasını sağlayacaktır. Bu, profil oluşturma araçları kullanılarak yapılabilir.
* **Bağımlılık Yönetimi:** Projenin bağımlılıklarının düzenli olarak güncellenmesi ve yönetilmesi, güvenlik açıklarının ve uyumsuzluk sorunlarının önlenmesini sağlayacaktır. Bu, `requirements.txt` dosyasının düzenli olarak güncellenmesi ve `pip-tools` gibi bir araç kullanılarak yapılabilir.

### Kişilik ve Hafıza

* **Daha Gelişmiş Kişilik Modelleri:** Orion'un kişiliğini daha zengin ve çeşitli hale getirmek için, farklı kişilik modelleri (örneğin, Myers-Briggs, Enneagram) ve bu modellerin LLM'ler ile entegrasyonu araştırılabilir.
* **Duygu Entegrasyonu:** Orion'un duygusal tepkiler verebilmesi için, duygu tanıma ve ifade yetenekleri entegre edilebilir. Bu, metin analizi ve ses analizi teknikleri kullanılarak yapılabilir.
* **Uzun Süreli Hafıza İyileştirmeleri:** Orion'un uzun süreli hafızasını daha etkili hale getirmek için, vektörel veri tabanları (örneğin, Pinecone, Weaviate) ve gelişmiş RAG (Retrieval-Augmented Generation) teknikleri kullanılabilir.

### LLM Entegrasyonu

* **Model Seçimi ve Yönetimi:** Farklı LLM'lerin (hem yerel hem de API tabanlı) performansını ve maliyetini düzenli olarak karşılaştırmak ve en uygun modeli dinamik olarak seçmek için bir sistem kurulabilir.
* **Prompt Mühendisliği:** Orion'un cevaplarının kalitesini artırmak için, prompt mühendisliği teknikleri (örneğin, zincirleme düşünme, az sayıda öğrenme) kullanılabilir.
* **Güvenlik ve Etik:** LLM'lerin güvenli ve etik bir şekilde kullanılmasını sağlamak için, girdi ve çıktı filtreleme mekanizmaları uygulanabilir. Bu, zararlı veya uygunsuz içeriklerin tespit edilmesini ve engellenmesini sağlayacaktır.

### Sesli ve Görsel Etkileşim

* **Gelişmiş Ses Tanıma:** Whisper.cpp'nin daha yeni versiyonları veya alternatif ses tanıma teknolojileri (örneğin, AssemblyAI, Deepgram) kullanılarak ses tanıma doğruluğu artırılabilir.
* **Doğal Dil Üretimi İyileştirmeleri:** Bark/TTS veya OpenVoice gibi metinden sese teknolojilerinin daha doğal ve insana benzer sesler üretmesi için ince ayar yapılabilir.
* **Görsel Algılama Geliştirmeleri:** Tesseract + OpenCV ile yapılan OCR işlemlerinin doğruluğunu artırmak için, daha gelişmiş OCR teknolojileri (örneğin, Google Cloud Vision API, Amazon Rekognition) veya derin öğrenme tabanlı nesne tanıma modelleri kullanılabilir.

### Kodlama Asistanı

* **Otomatik Kod Üretimi ve Tamamlama:** Orion'un otomatik olarak kod üretebilmesi ve tamamlayabilmesi için, daha gelişmiş kodlama asistanı araçları (örneğin, GitHub Copilot, Tabnine) entegre edilebilir.
* **Kod Kalitesi Analizi:** Orion'un yazdığı kodun kalitesini otomatik olarak analiz etmek ve iyileştirmek için, statik analiz araçları (örneğin, SonarQube, Pylint) kullanılabilir.
* **Test Otomasyonu:** Orion'un yazdığı kod için otomatik olarak testler oluşturmak ve çalıştırmak için, test otomasyonu araçları (örneğin, pytest, Selenium) kullanılabilir.

### Genel İyileştirmeler

* **Modülerlik ve Yeniden Kullanılabilirlik:** Projede kullanılan modüllerin (örneğin, `screen_agent.py`, `speech_agent.py`) daha modüler ve yeniden kullanılabilir hale getirilmesi, gelecekteki geliştirmeleri kolaylaştıracaktır. Bu, her bir modülün daha spesifik görevlere odaklanmasını ve farklı projelerde kullanılabilmesini sağlayacaktır.
* **Hata Yönetimi ve İzleme:** Projede kapsamlı bir hata yönetimi ve izleme sistemi kurulması, hataların daha hızlı tespit edilmesini ve çözülmesini sağlayacaktır. Bu, Sentry veya benzeri bir araç kullanılarak yapılabilir.
* **Test Kapsamının Artırılması:** Projenin test kapsamının artırılması, kodun kalitesini ve güvenilirliğini artıracaktır. Bu, birim testleri, entegrasyon testleri ve sistem testleri yazılarak yapılabilir.
* **Performans Optimizasyonu:** Projenin performansının düzenli olarak ölçülmesi ve optimize edilmesi, daha hızlı ve verimli çalışmasını sağlayacaktır. Bu, profil oluşturma araçları kullanılarak yapılabilir.
* **Bağımlılık Yönetimi:** Projenin bağımlılıklarının düzenli olarak güncellenmesi ve yönetilmesi, güvenlik açıklarının ve uyumsuzluk sorunlarının önlenmesini sağlayacaktır. Bu, `requirements.txt` dosyasının düzenli olarak güncellenmesi ve `pip-tools` gibi bir araç kullanılarak yapılabilir.

### Kişilik ve Hafıza

* **Daha Gelişmiş Kişilik Modelleri:** Orion'un kişiliğini daha zengin ve çeşitli hale getirmek için, farklı kişilik modelleri (örneğin, Myers-Briggs, Enneagram) ve bu modellerin LLM'ler ile entegrasyonu araştırılabilir.
* **Duygu Entegrasyonu:** Orion'un duygusal tepkiler verebilmesi için, duygu tanıma ve ifade yetenekleri entegre edilebilir. Bu, metin analizi ve ses analizi teknikleri kullanılarak yapılabilir.
* **Uzun Süreli Hafıza İyileştirmeleri:** Orion'un uzun süreli hafızasını daha etkili hale getirmek için, vektörel veri tabanları (örneğin, Pinecone, Weaviate) ve gelişmiş RAG (Retrieval-Augmented Generation) teknikleri kullanılabilir.

### LLM Entegrasyonu

* **Model Seçimi ve Yönetimi:** Farklı LLM'lerin (hem yerel hem de API tabanlı) performansını ve maliyetini düzenli olarak karşılaştırmak ve en uygun modeli dinamik olarak seçmek için bir sistem kurulabilir.
* **Prompt Mühendisliği:** Orion'un cevaplarının kalitesini artırmak için, prompt mühendisliği teknikleri (örneğin, zincirleme düşünme, az sayıda öğrenme) kullanılabilir.
* **Güvenlik ve Etik:** LLM'lerin güvenli ve etik bir şekilde kullanılmasını sağlamak için, girdi ve çıktı filtreleme mekanizmaları uygulanabilir. Bu, zararlı veya uygunsuz içeriklerin tespit edilmesini ve engellenmesini sağlayacaktır.

### Sesli ve Görsel Etkileşim

* **Gelişmiş Ses Tanıma:** Whisper.cpp'nin daha yeni versiyonları veya alternatif ses tanıma teknolojileri (örneğin, AssemblyAI, Deepgram) kullanılarak ses tanıma doğruluğu artırılabilir.
* **Doğal Dil Üretimi İyileştirmeleri:** Bark/TTS veya OpenVoice gibi metinden sese teknolojilerinin daha doğal ve insana benzer sesler üretmesi için ince ayar yapılabilir.
* **Görsel Algılama Geliştirmeleri:** Tesseract + OpenCV ile yapılan OCR işlemlerinin doğruluğunu artırmak için, daha gelişmiş OCR teknolojileri (örneğin, Google Cloud Vision API, Amazon Rekognition) veya derin öğrenme tabanlı nesne tanıma modelleri kullanılabilir.

### Kodlama Asistanı

* **Otomatik Kod Üretimi ve Tamamlama:** Orion'un otomatik olarak kod üretebilmesi ve tamamlayabilmesi için, daha gelişmiş kodlama asistanı araçları (örneğin, GitHub Copilot, Tabnine) entegre edilebilir.
* **Kod Kalitesi Analizi:** Orion'un yazdığı kodun kalitesini otomatik olarak analiz etmek ve iyileştirmek için, statik analiz araçları (örneğin, SonarQube, Pylint) kullanılabilir.
* **Test Otomasyonu:** Orion'un yazdığı kod için otomatik olarak testler oluşturmak ve çalıştırmak için, test otomasyonu araçları (örneğin, pytest, Selenium) kullanılabilir.

---

## Sprint Durumu

**ORION – SONRAKİ SPRINT HEDEF LİSTESİ**

| No | Görev | Öncelik | Tahmini Süre | Açıklama |
|---|---|---|---|---|
| 1 | ✅ runner_service.py'yi tam işlevsel hale getir | Yüksek | 1–2 gün | Görev oluşturma, güncelleme, hata yönetimi, loglama |
| 2 | ✅ agent_interface.py ile agent çağrısı birleştir | Yüksek | 1 gün | Agent endpoint’lerini JSON’dan oku, çağır |
| 3 | ✅ LLM görev yönlendirmesi (llm_router → runner) | Yüksek | 0.5 gün | Komut analiz edip görev olarak runner’a atama ve çoklu LLM seçimi |
| 4 | 🧠 Küçük model eğitim sistemi için train_or_finetune.py taslağı | Orta | 1–2 gün | CPU modelleri için görev bazlı fine-tuning başlatıcı |
| 5 | 🧪 mod ve persona seçeneklerini runner üzerinden kontrol et | Orta | 1 gün | Kullanıcı sistem modunu (normal, kaos vb.) belirleyebilsin |
| 6 | ✅ 🖼️ screen_agent.py için OCR eklentisi (Tesseract/EasyOCR) | Orta | 1 gün | Ekrandan yazı okuyabilmek için |
| 7 | 🧑‍💻 Görev geçmişini *.last dosyası gibi arşivle (JSON) | Orta | 1 gün | Görev detayları loglansın, tekrar kullanılabilir olsun |
| 8 | 🧩 agent_endpoints.json yapılandırması oluştur | Düşük | 0.5 gün | Yeni agent’lar kolayca eklensin |
| 9 | 🎛️ Task Manager UI için terminal tabanlı geçici arayüz | Düşük | 1 gün | Görevleri CLI'dan izlemek ve değiştirmek için |
| 10 | 📊 Kaynak kullanım izleme (psutil / nvidia-smi wrapper) | Düşük | 1 gün | CPU/GPU yüküne göre görev/agent seçiminde yardımcı olur |
| 7 | 🧑‍💻 Görev geçmişini *.last dosyası gibi arşivle (JSON) | Orta | 1 gün | Görev detayları loglansın, tekrar kullanılabilir olsun |
| 8 | 🧩 agent_endpoints.json yapılandırması oluştur | Düşük | 0.5 gün | Yeni agent’lar kolayca eklensin |
| 9 | 🎛️ Task Manager UI için terminal tabanlı geçici arayüz | Düşük | 1 gün | Görevleri CLI'dan izlemek ve değiştirmek için |
| 10 | 📊 Kaynak kullanım izleme (psutil / nvidia-smi wrapper) | Düşük | 1 gün | CPU/GPU yüküne göre görev/agent seçiminde yardımcı olur |
| 7 | 🧑‍💻 Görev geçmişini *.last dosyası gibi arşivle (JSON) | Orta | 1 gün | Görev detayları loglansın, tekrar kullanılabilir olsun |
| 8 | 🧩 agent_endpoints.json yapılandırması oluştur | Düşük | 0.5 gün | Yeni agent’lar kolayca eklensin |
| 9 | 🎛️ Task Manager UI için terminal tabanlı geçici arayüz | Düşük | 1 gün | Görevleri CLI'dan izlemek ve değiştirmek için |
| 10 | 📊 Kaynak kullanım izleme (psutil / nvidia-smi wrapper) | Düşük | 1 gün | CPU/GPU yüküne göre görev/agent seçiminde yardımcı olur |

**Sprint Sonunda Hedeflenen Durum:**

* ✅ Görevler sistematik şekilde oluşturuluyor
* ✅ Agent’lar otomatik olarak çağrılıyor ve sonuçları döndürülüyor
* ✅ Küçük modeller görev odaklı eğitilmeye hazır hale geliyor
* ✅ Ekran içeriği analiz edilebiliyor, OCR ile destekleniyor
* ✅ Kullanıcı görevleri görebiliyor, yönlendirebiliyor
* ✅ Sistem kaynak kullanımı bilinçli şekilde optimize ediliyor