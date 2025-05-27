# ORION VISION CORE – DETAYLI MASTER GELİŞTİRME PLANI

Bu detaylı master plan, projenin mevcut durumunu, tamamlanan görevleri ve gelecekteki geliştirme hedeflerini yapılandırılmış bir şekilde özetler. Ana Plan Güncellemesi belgesindeki çevik program yönetimi, CI/CD, risk yönetimi ve sürüm yaşam döngüsü önerileri, plana entegre edilmiştir. Plan, Alpha sürüm hedefine ulaşmayı ve sıfır bütçe kısıtlamalarını dikkate alarak çevik sprint'lerle ilerlemeyi hedefler.

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

## Sprint Durumu

**ORION – SONRAKİ SPRINT HEDEF LİSTESİ**

| No | Görev | Öncelik | Tahmini Süre | Açıklama |
|---|---|---|---|---|
| 1 | ✅ runner_service.py'yi tam işlevsel hale getir | Yüksek | 1–2 gün | Görev oluşturma, güncelleme, hata yönetimi, loglama |
| 2 | ✅ agent_interface.py ile agent çağrısı birleştir | Yüksek | 1 gün | Agent endpoint’lerini JSON’dan oku, çağır |
| 3 | ✅ LLM görev yönlendirmesi (llm_router → runner) | Yüksek | 0.5 gün | Komut analiz edip görev olarak runner’a atama ve çoklu LLM seçimi |
| 4 | 🧠 Küçük model eğitim sistemi için train_or_finetune.py taslağı | Orta | 1–2 gün | CPU modelleri için görev bazlı fine-tuning başlatıcı |
| 5 | 🧪 mod ve persona seçeneklerini runner üzerinden kontrol et | Orta | 1 gün | Kullanıcı sistem modunu (normal, kaos vb.) belirleyebilsin |
| 6 | 🖼️ screen_agent.py için OCR eklentisi (Tesseract/EasyOCR) | Orta | 1 gün | Ekrandan yazı okuyabilmek için |
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

Bu detaylı master plan, projenin geliştirme sürecini daha iyi yönetmenize ve Alpha sürüm hedefine ulaşmanıza yardımcı olacaktır.