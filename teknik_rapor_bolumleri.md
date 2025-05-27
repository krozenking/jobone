# Giriş

Bu teknik rapor, ORION VISION CORE projesinin geliştirme sürecini ve sonuçlarını detaylı bir şekilde açıklamaktadır. Proje, Orion’un kendi sisteminde çalışan, stratejik kararlar alabilen, kişilikli ve çevresiyle etkileşim kurabilen yapay zekâ altyapısının sıfır bütçeyle geliştirilmesi amacıyla başlatılmıştır. Bu amaç doğrultusunda, hafızalı, etkileşimli, kendi kararlarını alabilen bir danışman-yapay zeka hedeflenmiştir.

# Geliştirme Süreci

Projenin geliştirme sürecinde aşağıdaki teknolojiler kullanılmıştır:

*   Python 3.10+
*   Git
*   Node.js (bazı UI araçları için)
*   CUDA (RTX 4060 ile uyumlu)
*   Ollama (yerel LLM için)
*   Whisper.cpp (ses tanıma için)
*   OpenRouter API (ücretsiz API desteği için)
*   Bark/TTS (sesli yanıt üretme için)
*   Tesseract + OpenCV (OCR için)
*   PyAutoGUI (fare/klavye kontrolü için)
*   VSCode + Continue eklentisi (kodlama asistanı için)

Geliştirme süreci aşağıdaki adımlardan oluşmuştur:

1.  Ortam Kurulumu: Python, gerekli sistem araçları ve proje klasörünün oluşturulması.
2.  Yapı Kurulumu ve Modüller: Temel dosya yapısının oluşturulması ve modüllerin işlevlerinin belirlenmesi.
3.  Kişilik ve Hafıza Entegrasyonu: Orion’un karakterinin tanımlanması ve hafıza yönetiminin sağlanması.
4.  LLM Entegrasyonu: Yerel model (Ollama) ve ücretsiz API desteği (OpenRouter) ile zeka entegrasyonu.
5.  Sesli Etkileşim: Whisper.cpp ile ses tanıma ve Bark/TTS ile sesli yanıt üretimi.
6.  Görsel Algılama: Ekran takibi (Tesseract + OpenCV) ve fiziksel etkileşim (PyAutoGUI) ile UI üzerinden işlem başlatma.
7.  Kodlama Asistanı Entegrasyonu: VSCode + Continue eklentisi ile kodlama süreçlerinin desteklenmesi.