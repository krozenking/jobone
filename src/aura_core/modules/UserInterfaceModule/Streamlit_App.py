import streamlit as st
import requests
import json
import pandas as pd # pandas'ı burada tanımlıyoruz, böylece her yerde import etmeye gerek kalmaz

# API'nin çalıştığı temel URL ve port (8001 olduğundan emin olun!)
API_BASE_URL = "http://localhost:8001"

# --- API Çağrı Fonksiyonları ---

def get_api_status(api_url=f"{API_BASE_URL}/"):
    """API'nin genel durumunu kontrol eder."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"API'ye ({api_url}) bağlanılamadı. API'nin çalıştığından emin olun.")
        return {"error": "API Connection Error"}
    except requests.exceptions.RequestException as e:
        st.error(f"API isteği sırasında bir hata oluştu: {e}")
        return {"error": str(e)}

def get_system_state(api_url=f"{API_BASE_URL}/state"):
    """Sistem durumu verilerini çeker."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Sistem durumu alınırken hata: {e}")
        return {"error": str(e)}

def trigger_task(task_name):
    """Belirtilen görevi API üzerinden tetikler."""
    api_url = f"{API_BASE_URL}/trigger_task"
    payload = {"task_name": task_name}

    st.write(f"API'ye gönderilecek payload: {payload}")
    st.write(f"API URL: {api_url}")

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        st.success(f"'{task_name}' görevi tetiklendi: {response.json().get('message', 'Başarılı')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Görev tetiklenirken hata oluştu: {e}")
        if response is not None:
            try:
                st.error(f"API'den gelen detaylı hata mesajı: {response.json()}")
            except json.JSONDecodeError:
                st.error(f"API'den gelen raw hata içeriği: {response.text}")

def get_task_status(task_id):
    """Belirli bir görev ID'sinin durumunu sorgular."""
    api_url = f"{API_BASE_URL}/task_status/{task_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Görev durumu alınırken hata oluştu: {e}")
        return {"error": str(e)}

def call_ai_service(prompt_text, api_url=f"{API_BASE_URL}/ai_service"):
    """AI servisine bir istem gönderir ve yanıtı alır."""
    payload = {"prompt": prompt_text}
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"AI servisi çağrılırken hata oluştu: {e}")
        if response is not None:
            try:
                st.error(f"API'den gelen detaylı hata mesajı: {response.json()}")
            except json.JSONDecodeError:
                st.error(f"API'den gelen raw hata içeriği: {response.text}")
        return {"error": str(e)}

def get_error_logs(api_url=f"{API_BASE_URL}/logs/errors"):
    """Hata loglarını çeker."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Hata logları alınırken hata: {e}")
        return []

def get_telemetry_data(api_url=f"{API_BASE_URL}/telemetry"):
    """Telemetri verilerini çeker."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Telemetri verileri alınırken hata: {e}")
        return {}

def get_database_data(api_url=f"{API_BASE_URL}/database/data"):
    """Veritabanı verilerini çeker."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        db_data = response.json().get("data", [])
        return db_data
    except requests.exceptions.RequestException as e:
        st.error(f"Veritabanı verileri alınırken hata oluştu: {e}")
        return []

# --- Streamlit Uygulama Düzeni ---

st.set_page_config(layout="wide")
st.title("Orion Sistem Paneli")

# --- Genel API Durumu ---
st.subheader("API Durumu")
api_status = get_api_status()
if "error" in api_status:
    st.write(f"API Durumu: ❌ {api_status['error']}")
else:
    st.write(f"API Durumu: ✅ {api_status['message']}")

st.markdown("---")

# --- Sekmeli Düzen ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Sistem Durumu", "Görev Yönetimi", "Hata Logları",
    "Telemetri", "Veritabanı", "AI Etkileşimi"
])

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

    st.markdown("---") # Ayırıcı ekleyelim

    st.subheader("Görev Durumu Sorgula")
    # 'value' parametresi int türünde olmalı, bu nedenle varsayılan olarak bir int veriyoruz
    task_id_to_check = st.number_input("Durumu sorgulanacak Görev ID'si", min_value=1, value=1, key="task_status_id_input")
    if st.button("Durumu Getir", key="get_task_status_button"):
        status_data = get_task_status(task_id_to_check)
        if "error" not in status_data:
            st.json(status_data)
        else:
            st.write("Görev durumu alınamadı.")

with tab3:
    st.header("Hata Logları")
    logs = get_error_logs()
    if logs:
        df = pd.DataFrame(logs)

        # Dosya adını (modül) filtreleme
        if 'filename' in df.columns:
            module_filter = st.multiselect("Modüle göre filtrele", options=df['filename'].unique(), key="module_filter")
            if module_filter:
                df = df[df['filename'].isin(module_filter)]

        # Hata mesajına göre arama
        if 'content' in df.columns:
            search_term = st.text_input("Hata mesajına göre ara", key="search_term")
            if search_term:
                df = df[df['content'].str.contains(search_term, case=False, na=False)]

        # Zaman damgasına göre sıralama (varsa)
        if 'timestamp' in df.columns:
            sort_by_timestamp = st.checkbox("Zaman damgasına göre sırala", key="sort_by_timestamp")
            if sort_by_timestamp:
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp']) # Zaman damgasını datetime'a çevir
                    df = df.sort_values(by='timestamp', ascending=False)
                except Exception as e:
                    st.warning(f"Zaman damgası sütunu dönüştürülemedi: {e}")

        st.dataframe(df)
    else:
        st.info("Henüz hata logu bulunamadı.")

with tab4:
    st.header("Telemetri Verileri")
    telemetry = get_telemetry_data()
    if telemetry:
        df_data = []
        for agent_name, metrics in telemetry.items():
            row = {"Agent": agent_name}
            row.update(metrics)
            df_data.append(row)

        df = pd.DataFrame(df_data)

        st.subheader("Ham Telemetri Verileri")
        st.dataframe(df)

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if 'cpu_usage' in numeric_cols:
            st.subheader("CPU Kullanımı")
            st.line_chart(df[['cpu_usage']], height=300)

        if 'memory_usage' in numeric_cols:
            st.subheader("Bellek Kullanımı")
            st.line_chart(df[['memory_usage']], height=300)

        if 'temperature' in numeric_cols:
            st.subheader("Sıcaklık")
            st.line_chart(df[['temperature']], height=300)

        if 'humidity' in numeric_cols:
            st.subheader("Nem")
            st.line_chart(df[['humidity']], height=300)

        if 'pressure' in numeric_cols:
            st.subheader("Basınç")
            st.line_chart(df[['pressure']], height=300)

        other_metrics = [col for col in numeric_cols if col not in ['cpu_usage', 'memory_usage', 'temperature', 'humidity', 'pressure']]
        if other_metrics:
            st.subheader("Diğer Sayısal Metrikler")
            for metric in other_metrics:
                st.line_chart(df[[metric]], height=200)

        st.subheader("Tüm Telemetri Verileri (JSON)")
        st.json(telemetry)
    else:
        st.info("Telemetri verisi alınamadı.")

with tab5:
    st.header("Veritabanı Verileri")
    st.write("Orion Sisteminin merkezi veritabanından çekilen veriler.")

    if st.button("Veritabanı Verilerini Yükle", key="load_db_data_button"):
        db_data = get_database_data()
        if db_data:
            df_db = pd.DataFrame(db_data)
            st.subheader("Veritabanı İçeriği")
            st.dataframe(df_db)

            if 'type' in df_db.columns:
                st.subheader("Veri Tipi Dağılımı")
                type_counts = df_db['type'].value_counts()
                st.bar_chart(type_counts)

            if 'timestamp' in df_db.columns:
                try:
                    df_db['timestamp'] = pd.to_datetime(df_db['timestamp'])
                    df_db = df_db.sort_values('timestamp')
                    st.subheader("Zaman Çizgisi")
                    st.line_chart(df_db.set_index('timestamp').resample('H').size())
                except Exception as e:
                    st.warning(f"Zaman damgası işlenirken hata oluştu: {e}")
                    st.dataframe(df_db)
        else:
            st.info("Veritabanından veri alınamadı veya veritabanı boş.")

with tab6:
    st.header("Yapay Zeka (AI) Etkileşimi")
    st.write("Orion AI servisleri ile sohbet edin veya sorgular gönderin.")

    ai_prompt_input = st.text_area("Yapay Zeka'ya Sorgunuz:", "Sistemdeki son 5 hatayı özetle ve olası nedenlerini belirt.", height=150, key="ai_prompt_text_area")

    if st.button("Sorguyu Gönder", key="send_ai_prompt_button"):
        if ai_prompt_input:
            with st.spinner("Yapay zeka yanıtı bekleniyor..."):
                ai_response = call_ai_service(ai_prompt_input)
            if "error" not in ai_response:
                st.subheader("AI Yanıtı:")
                # AI yanıtı 'result' anahtarında ise onu göster, değilse tüm yanıtı göster
                if "result" in ai_response:
                    st.write(ai_response["result"])
                else:
                    st.json(ai_response)
            else:
                st.error("AI servisinden yanıt alınamadı.")
        else:
            st.warning("Lütfen bir sorgu girin.")

# --- Otomatik Test ---
def run_tests():
    test_results = {}

    api_status = get_api_status()
    test_results["API Durumu"] = "✅" if "error" not in api_status else "❌"

    system_state = get_system_state()
    test_results["Sistem Durumu"] = "✅" if "error" not in system_state else "❌"

    error_logs = get_error_logs()
    test_results["Hata Logları"] = "✅" if error_logs is not None else "❌"

    telemetry_data = get_telemetry_data()
    test_results["Telemetri Verileri"] = "✅" if telemetry_data is not None else "❌"

    db_data = get_database_data()
    test_results["Veritabanı Verileri"] = "✅" if db_data is not None else "❌" # Veritabanı testi eklendi

    return test_results

if st.button("Otomatik Testleri Çalıştır"):
    test_results = run_tests()
    st.subheader("Test Sonuçları")
    for test, result in test_results.items():
        st.write(f"{test}: {result}")

# --- Performans Metrikleri ve XAI (Daha sonra geliştirilecek) ---
# st.header("Performans Metrikleri")
# st.header("Açıklanabilir Yapay Zeka (XAI) Görselleştirmeleri")