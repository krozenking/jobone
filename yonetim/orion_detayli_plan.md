# 🚀 ORION VISION CORE – DETAYLI MASTER GELİŞTİRME PLANI

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
    P --> Q[log_manager.py]
    P --> R[database_manager.py]
```

#### Not:  
- `log_manager.py` ve `database_manager.py` hata yönetimi ve loglama için ayrı modüller olarak eklenmiştir.
- Modüler mimari, her ana işlevin ayrı bir modül/dosya ile yönetilmesini sağlar.

## Tamamlanan Görevler

*   Temel aracıların (speech, voice, llm_router, memory, screen, mouse_control) uygulanması.
*   Projenin belgelenmesi ve planlanması için gerekli dosyaların oluşturulması (sohbet_tam.md, orion_gelistirme_master_plan.md, teknik_rapor_bolumleri.md).
*   Projenin yapılandırılması için gerekli dosyaların oluşturulması (persona.json, llm_config.json, continue.config.json).
*   Testlerin uygulanması ve hataların giderilmesi (test_bark.py, fix_bark.py).
*   `runner_service.py`'nin tam işlevsel hale getirilmesi (görev oluşturma, güncelleme, hata yönetimi, loglama).
*   `screen_agent.py` modülüne EasyOCR entegrasyonu yapılması.

## Sprint Durumu

**ORION – SONRAKİ SPRINT HEDEF LİSTESİ**

| No | Görev | Öncelik | Tahmini Süre | Açıklama |
|---|---|---|---|---|
| 2 | ✅ agent_interface.py ile agent çağrısı birleştir | Yüksek | 1 gün | Agent endpoint’lerini JSON’dan oku, çağır |
| 3 | ✅ LLM görev yönlendirmesi (llm_router → runner) | Yüksek | 0.5 gün | Komut analiz edip görev olarak runner’a atama ve çoklu LLM seçimi |
| 4 | 🧠 train_or_finetune.py ile küçük model eğitimi | Orta | 1–2 gün | CPU modelleri için görev bazlı fine-tuning başlatıcı |
| 5 | 🧪 mod ve persona seçeneklerini runner üzerinden kontrol et | Orta | 1 gün | Kullanıcı sistem modunu (normal, kaos vb.) belirleyebilsin |
| 7 | 🧑‍💻 Görev geçmişini *.last dosyası gibi arşivle (JSON) | Orta | 1 gün | Görev detayları loglansın, tekrar kullanılabilir olsun |
| 8 | 🧩 agent_endpoints.json yapılandırması oluştur | Düşük | 0.5 gün | Yeni agent’lar kolayca eklensin |
| 9 | 🎛️ Task Manager UI için terminal tabanlı geçici arayüz | Düşük | 1 gün | Görevleri CLI'dan izlemek ve değiştirmek için |
| 10 | 📊 Kaynak kullanım izleme (psutil / nvidia-smi wrapper) | Düşük | 1 gün | CPU/GPU yüküne göre görev/agent seçiminde yardımcı olur |
| 11 | 🗂️ Modüler klasör yapısına geçiş (aura_core_autonomous_modules/src/aura_core/modules/...) | Orta | 1 gün | Her ana işlev için ayrı modül klasörü oluştur |
| 12 | 🛡️ log_manager.py ve database_manager.py ile merkezi loglama | Orta | 1 gün | Hata ve olay yönetimi için merkezi sistem |
| 13 | 🧠 query_optimizer_agent.py ve ai_scheduler_agent.py entegrasyonu | Orta | 1 gün | Akıllı sorgu ve zamanlayıcı ajanları ekle |

**Sprint Sonunda Hedeflenen Durum:**

* ✅ Görevler sistematik şekilde oluşturuluyor
* ✅ Agent’lar otomatik olarak çağrılıyor ve sonuçları döndürülüyor
* ✅ Küçük modeller görev odaklı eğitilmeye hazır hale geliyor
* ✅ Ekran içeriği analiz edilebiliyor, OCR ile destekleniyor
* ✅ Kullanıcı görevleri görebiliyor, yönlendirebiliyor
* ✅ Sistem kaynak kullanımı bilinçli şekilde optimize ediliyor
* ✅ Log ve hata yönetimi merkezi olarak izlenebiliyor
* ✅ Modüler klasör yapısı ile yeni ajan/modül eklemek kolaylaşıyor

## Modüler Dosya ve Klasör Yapısı (Özet)

Aşağıdaki yapı, projenin sürdürülebilir ve genişletilebilir olmasını sağlar:

```
aura_core_autonomous_modules/
├── src/
│   └── aura_core/
│       ├── common/
│       ├── modules/
│       │   ├── AgentManagerModule/
│       │   │   ├── agent_interface.py
│       │   │   ├── agent_endpoints.json
│       │   ├── CognitiveAgentModule/
│       │   │   ├── runner_service.py
│       │   │   ├── ai_scheduler_agent.py
│       │   │   ├── query_optimizer_agent.py
│       │   ├── LLMIntegrationModule/
│       │   │   ├── llm_router.py
│       │   │   ├── train_or_finetune.py
│       │   ├── UserInterfaceModule/
│       │   │   ├── screen_agent.py
│       │   │   ├── terminal_logger.py
│       │   │   ├── streamlit_app.py
│       │   ├── DataManagementModule/
│       │   │   ├── log_manager.py
│       │   │   ├── database_manager.py
│       │   ├── ConfigModule/
│       │   │   ├── config.py
│       │   │   ├── config_manager.py
│       │   ├── TaskManagerModule/
│       │   │   ├── task_manager.py
│       │   │   ├── scheduler.py
│       │   ├── TrainerModule/
│       │   │   ├── trainer.py
│       └── core_app.py
├── config/
│   ├── persona.json
│   ├── llm_config.json
│   ├── continue.config.json
├── data/
│   ├── orion_memory_v2.json
│   ├── *.last
├── docs/
├── scripts/
├── tests/
└── main.py
```

Her modül, kendi içinde servis, arayüz, konfigürasyon ve test dosyalarını barındırır.  
Yeni ajanlar veya işlevler eklemek için ilgili modül klasörüne yeni bir alt klasör/dosya eklemek yeterlidir.

## Dosya ve Klasörlerin Taşınması İçin Yol Haritası

Aşağıdaki eşleştirmeye göre dosyalarınızı taşıyın ve yeniden adlandırın:

```
aura_core_autonomous_modules/
├── src/
│   └── aura_core/
│       ├── common/
│       ├── modules/
│       │   ├── AgentManagerModule/
│       │   │   ├── agent_interface.py
│       │   │   ├── agent_endpoints.json
│       │   ├── CognitiveAgentModule/
│       │   │   ├── runner_service.py
│       │   │   ├── ai_scheduler_agent.py
│       │   │   ├── query_optimizer_agent.py
│       │   ├── LLMIntegrationModule/
│       │   │   ├── llm_router.py
│       │   │   ├── train_or_finetune.py
│       │   ├── UserInterfaceModule/
│       │   │   ├── screen_agent.py
│       │   │   ├── terminal_logger.py
│       │   │   ├── streamlit_app.py
│       │   ├── DataManagementModule/
│       │   │   ├── log_manager.py
│       │   │   ├── database_manager.py
│       │   ├── ConfigModule/
│       │   │   ├── config.py
│       │   │   ├── config_manager.py
│       │   ├── TaskManagerModule/
│       │   │   ├── task_manager.py
│       │   │   ├── scheduler.py
│       │   ├── TrainerModule/
│       │   │   ├── trainer.py
│       └── core_app.py
├── config/
│   ├── persona.json
│   ├── llm_config.json
│   ├── continue.config.json
├── data/
│   ├── orion_memory_v2.json
│   ├── *.last
├── docs/
├── scripts/
├── tests/
└── main.py
```

**Taşıma Önerileri:**
Aşağıdaki terminal komutlarını kullanarak dosyalarınızı yeni mimariye uygun şekilde taşıyabilirsiniz:

```sh
# Ana klasörünüzde çalıştığınızı varsayalım (ör: aura_core_autonomous_modules/)

# DataManagementModule
mkdir -p src/aura_core/modules/DataManagementModule
mv log_manager.py src/aura_core/modules/DataManagementModule/
mv database_manager.py src/aura_core/modules/DataManagementModule/

# LLMIntegrationModule
mkdir -p src/aura_core/modules/LLMIntegrationModule
mv llm_router.py src/aura_core/modules/LLMIntegrationModule/
mv train_or_finetune.py src/aura_core/modules/LLMIntegrationModule/

# CognitiveAgentModule
mkdir -p src/aura_core/modules/CognitiveAgentModule
mv runner_service.py src/aura_core/modules/CognitiveAgentModule/
mv ai_scheduler_agent.py src/aura_core/modules/CognitiveAgentModule/
mv query_optimizer_agent.py src/aura_core/modules/CognitiveAgentModule/

# UserInterfaceModule
mkdir -p src/aura_core/modules/UserInterfaceModule
mv screen_agent.py src/aura_core/modules/UserInterfaceModule/
mv terminal_logger.py src/aura_core/modules/UserInterfaceModule/
mv streamlit_app.py src/aura_core/modules/UserInterfaceModule/

# ConfigModule
mkdir -p src/aura_core/modules/ConfigModule
mv config.py src/aura_core/modules/ConfigModule/
mv config_manager.py src/aura_core/modules/ConfigModule/

# TaskManagerModule
mkdir -p src/aura_core/modules/TaskManagerModule
mv task_manager.py src/aura_core/modules/TaskManagerModule/
mv scheduler.py src/aura_core/modules/TaskManagerModule/

# TrainerModule
mkdir -p src/aura_core/modules/TrainerModule
mv trainer.py src/aura_core/modules/TrainerModule/

# AgentManagerModule
mkdir -p src/aura_core/modules/AgentManagerModule
mv agent_interface.py src/aura_core/modules/AgentManagerModule/
mv agent_endpoints.json src/aura_core/modules/AgentManagerModule/

# Config ve data dosyaları
mkdir -p config
mv persona.json config/
mv llm_config.json config/
mv continue.config.json config/

mkdir -p data
mv orion_memory_v2.json data/
mv *.last data/

# Çekirdek ve ana dosya
mv core_app.py src/aura_core/
mv main.py .

# Ortak, dokümantasyon, script ve test klasörleri
mkdir -p src/aura_core/common
mkdir -p docs
mkdir -p scripts
mkdir -p tests
```

Her dosyayı yukarıdaki yapıya uygun şekilde taşıyın.  
Yeni dosya eklerken veya mevcut dosyaları taşırken, modül isimlendirmelerine ve klasör hiyerarşisine dikkat edin.

## Çevik Program Yönetimi, CI/CD, Risk Yönetimi ve Sürüm Yaşam Döngüsü Önerileri

Bu bölümde, projenin çevik program yönetimi, CI/CD, risk yönetimi ve sürüm yaşam döngüsü süreçleri için öneriler sunulmaktadır.

### Çevik Program Yönetimi

* Sprint Planlama: Her sprint'in başında, sprint hedefleri ve görevleri net bir şekilde tanımlanmalıdır. Görevler, SMART (Specific, Measurable, Achievable, Relevant, Time-bound) kriterlerine uygun olmalıdır.
* Günlük Scrum: Her gün kısa bir scrum toplantısı yapılarak, takım üyelerinin ilerlemesi, karşılaşılan sorunlar ve bir sonraki adımdaki hedefler belirlenmelidir.
* Sprint Değerlendirme: Her sprint'in sonunda, sprint hedeflerine ne kadar ulaşıldığı değerlendirilmelidir. Tamamlanamayan görevler, bir sonraki sprint'e taşınabilir veya öncelikleri değiştirilebilir.
* Retrospektif: Her sprint'in sonunda, takımın çalışma şekli ve süreçleri değerlendirilerek, iyileştirme alanları belirlenmelidir.

### CI/CD (Sürekli Entegrasyon/Sürekli Teslimat)

* Otomatik Testler: Kodun her değişikliğinde otomatik olarak çalışan birim testleri, entegrasyon testleri ve sistem testleri oluşturulmalıdır.
* Otomatik Derleme: Kodun her değişikliğinde otomatik olarak derlenmesi ve paketlenmesi sağlanmalıdır.
* Otomatik Dağıtım: Kodun test ortamına ve üretim ortamına otomatik olarak dağıtılması sağlanmalıdır.
* Sürüm Kontrolü: Tüm kod değişiklikleri, Git gibi bir sürüm kontrol sistemi ile takip edilmelidir.

### Risk Yönetimi

* Risk Değerlendirmesi: Projenin başında ve her sprint'in başında, potansiyel riskler belirlenmeli ve olasılıkları/etkileri değerlendirilmelidir.
* Risk Azaltma: Belirlenen riskleri azaltmak için önlemler alınmalıdır. Örneğin, kritik bir bağımlılığın riskini azaltmak için alternatif bir bağımlılık araştırılabilir.
* Risk İzleme: Riskler düzenli olarak izlenmeli ve yeni riskler tespit edilmelidir.

### Sürüm Yaşam Döngüsü

* Anlamsal Sürümleme: Sürüm numaraları, Anlamsal Sürümleme (Semantic Versioning) kurallarına uygun olarak belirlenmelidir (örn: 1.0.0).
* Sürüm Etiketleme: Her sürüm, Git'te bir etiket (tag) ile işaretlenmelidir.
* Sürüm Notları: Her sürüm için, yapılan değişiklikleri, düzeltilen hataları ve eklenen yeni özellikleri açıklayan sürüm notları hazırlanmalıdır.