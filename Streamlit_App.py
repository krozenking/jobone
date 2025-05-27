import streamlit as st
import requests
import json  # JSON verilerini daha güzel göstermek için

# API'nin çalıştığı temel URL ve port (8001 olduğundan emin olun!)
API_BASE_URL = "http://localhost:8001"

# --- API Çağrı Fonksiyonları ---

def get_api_status(api_url=f"{API_BASE_URL}/"):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # HTTP hataları için istisna fırlatır (4xx veya 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"API'ye ({api_url}) bağlanılamadı. API'nin çalıştığından emin olun.")
        return {"error": "API Connection Error"}
    except requests.exceptions.RequestException as e:
        st.error(f"API isteği sırasında bir hata oluştu: {e}")
        return {"error": str(e)}

def get_system_state(api_url=f"{API_BASE_URL}/state"):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Sistem durumu alınırken hata: {e}")
        return {"error": str(e)}

# GÖREV TETİKLEME FONKSİYONU (External_API.py'deki yeni /trigger_task endpoint'ine göre güncellendi)
def trigger_task(task_name):
    api_url = f"{API_BASE_URL}/trigger_task"
    # Burası çok önemli: payload, External_API'deki TaskTrigger modeline tam uygun olmalı
    payload = {"task_name": task_name}  # 'task_name' anahtarıyla string değeri gönderiyoruz

    # Hata ayıklama için: Gönderilecek payload'ı ekrana yazdıralım
    st.write(f"API'ye gönderilecek payload: {payload}")
    st.write(f"API URL: {api_url}")

    try:
        # requests.post() çağrısında 'json=payload' kullandığımızdan emin olun.
        # 'data=payload' kullanmayın, bu 422 hatasına yol açabilir.
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # HTTP hataları (4xx veya 5xx) durumunda istisna fırlatır
        st.success(f"'{task_name}' görevi tetiklendi: {response.json().get('message', 'Başarılı')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Görev tetiklenirken hata oluştu: {e}")
        if response is not None:  # Hata durumunda response objesi varsa
            try:
                st.error(f"API'den gelen detaylı hata mesajı: {response.json()}")
            except json.JSONDecodeError:
                st.error(f"API'den gelen raw hata içeriği: {response.text}")


# YENİ: Hata loglarını çeken fonksiyon
def get_error_logs(api_url=f"{API_BASE_URL}/logs/errors"):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Hata logları alınırken hata: {e}")
        return []

# YENİ: Telemetri verilerini çeken fonksiyon
def get_telemetry_data(api_url=f"{API_BASE_URL}/telemetry"):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Telemetri verileri alınırken hata: {e}")
        return {}

# --- Streamlit Uygulama Düzeni ---

st.set_page_config(layout="wide")  # Sayfa genişliğini ayarla
st.title("Orion Sistem Paneli")

# --- Genel API Durumu ---
st.subheader("API Durumu")
api_status = get_api_status()
if "error" in api_status:
    st.write(f"API Durumu: ❌ {api_status['error']}")
else:
    st.write(f"API Durumu: ✅ {api_status['message']}")

st.markdown("---")  # Ayırıcı

# --- Sekmeli Düzen ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Sistem Durumu", "Görev Yönetimi", "Hata Logları", "Telemetri", "Veritabanı"])

with tab1:
    st.header("Sistem Durumu")
    # Her 5 saniyede bir otomatik yenileme (Streamlit'in cache mekanizması ile)
    # veya manuel düğme
    if st.button("Sistem Durumunu Yenile", key="refresh_state"):
        state = get_system_state()
        if "error" not in state:
            st.json(state)
        else:
            st.write("Sistem durumu alınamadı.")

with tab2:
    st.header("Görev Yönetimi")
    st.subheader("Görev Tetikle")
    task_input = st.text_input("Tetiklenecek Görev Adı veya ID'si", "rapor_olustur", key="task_name_input")
    if st.button("Görevi Tetikle", key="trigger_task_button"):
        trigger_task(task_input)

with tab3:
    st.header("Hata Logları")
    logs = get_error_logs()
    if logs:
        # Hata loglarını bir DataFrame'e dönüştür
        import pandas as pd
        df = pd.DataFrame(logs)

        # Dosya adını (modül) filtreleme
        module_filter = st.multiselect("Modüle göre filtrele", options=df['filename'].unique(), key="module_filter")
        if module_filter:
            df = df[df['filename'].isin(module_filter)]

        # Hata mesajına göre arama
        search_term = st.text_input("Hata mesajına göre ara", key="search_term")
        if search_term:
            df = df[df['content'].str.contains(search_term, case=False, na=False)]

        # Zaman damgasına göre sıralama (varsa)
        if 'timestamp' in df.columns:
            sort_by_timestamp = st.checkbox("Zaman damgasına göre sırala", key="sort_by_timestamp")
            if sort_by_timestamp:
                df = df.sort_values(by='timestamp', ascending=False)

        # DataFrame'i görüntüle
        st.dataframe(df)
    else:
        st.info("Henüz hata logu bulunamadı.")

with tab4:
    st.header("Telemetri Verileri")
    telemetry = get_telemetry_data()
    if telemetry:
        # Telemetri verilerini bir DataFrame'e dönüştür
        import pandas as pd
        # Telemetri verilerini bir DataFrame'e dönüştür
        data = []
        for agent, metrics in telemetry.items():
            # Ajan adını ve metriklerini al
            agent_name = agent
            agent_metrics = metrics
            # Metrikleri data listesine ekle
            data.append(agent_metrics)
        df = pd.DataFrame(data)

        # Verileri görüntüle
        st.dataframe(df)

        # CPU ve bellek kullanımı için çizgi grafikler
        st.subheader("Sıcaklık")
        if 'temperature' in df.columns:
            st.line_chart(df[['temperature']], height=300)
        else:
            st.write("Sıcaklık verisi bulunamadı.")

        st.subheader("Nem")
        if 'humidity' in df.columns:
            st.line_chart(df[['humidity']], height=300)
        else:
            st.write("Nem verisi bulunamadı.")

        st.subheader("Basınç")
        if 'pressure' in df.columns:
            st.line_chart(df[['pressure']], height=300)
        else:
            st.write("Basınç verisi bulunamadı.")

        # Diğer telemetri verilerini JSON olarak göster
        st.subheader("Diğer Veriler")
        st.json(telemetry)
    else:
        st.info("Telemetri verisi alınamadı.")

with tab5:
    st.header("Veritabanı Verileri")
    st.info("Bu bölümde veritabanı verileri External_API üzerinden çekilip görselleştirilecektir.")
    st.write("Veritabanı Verileri (Örnek)")
    st.table([
        {"id": 0, "content": "Örnek veri 1", "embedding": "[0.1, 0.2, 0.3]"},
        {"id": 1, "content": "Örnek veri 2", "embedding": "[0.4, 0.5, 0.6]"}
    ])

# --- Otomatik Test ---
def run_tests():
    test_results = {}

    # API Durumu Testi
    api_status = get_api_status()
    test_results["API Durumu"] = "✅" if "error" not in api_status else "❌"

    # Sistem Durumu Testi
    system_state = get_system_state()
    test_results["Sistem Durumu"] = "✅" if "error" not in system_state else "❌"

    # Hata Logları Testi
    error_logs = get_error_logs()
    test_results["Hata Logları"] = "✅" if error_logs is not None else "❌"

    # Telemetri Verileri Testi
    telemetry_data = get_telemetry_data()
    test_results["Telemetri Verileri"] = "✅" if telemetry_data is not None else "❌"

    return test_results

if st.button("Otomatik Testleri Çalıştır"):
    test_results = run_tests()
    st.subheader("Test Sonuçları")
    for test, result in test_results.items():
        st.write(f"{test}: {result}")

# --- Performans Metrikleri ve XAI (Daha sonra geliştirilecek) ---
# st.header("Performans Metrikleri")
# st.header("Açıklanabilir Yapay Zeka (XAI) Görselleştirmeleri")