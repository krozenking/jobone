import logging
import os
from fastapi import FastAPI, HTTPException
from Log_Manager import setup_logging, process_log, ERROR_ARCHIVE_DIR
from Database_Manager import DatabaseManager
from pydantic import BaseModel

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Log_Manager örneğini oluştur
setup_logging()
log_manager = DatabaseManager()
log_manager.connect()

class TaskTrigger(BaseModel):
    task_name: str

class AIPrompt(BaseModel):
    prompt: str

@app.post("/trigger_task")
async def trigger_task(task: TaskTrigger):
    # Log_Manager veya Time_Based_Execution_Engine'a görevi tetikleme mantığı burada olacak
    # Örnek olarak, sadece log kaydı yapıyoruz
    task_name = task.task_name
    logging.info(f"Tetiklenen görev: {task_name}")
    return {"message": f"'{task_name}' görevi başarıyla tetiklendi."}

@app.get("/task_status/{task_id}")
async def task_status(task_id: int):
    return {"status": f"Status of task {task_id}"}

import time
@app.post("/ai_service")
async def ai_service(ai_request: AIPrompt): # Artık AIPrompt modelini bekliyoruz
    # Gerçek uygulamada, Query_Optimization_Agent veya AI_Root_Cause_Agent gibi bir ajana yönlendirilecek.
    logging.info(f"AI servisi istemi alındı: {ai_request.prompt}") # ai_request.prompt olarak erişin
    # Basit bir yanıt dönüyoruz
    ai_response = f"AI servisi, isteminizi aldı: '{ai_request.prompt}'. Bu, gelecekte daha gelişmiş bir yanıt olacak."
    return {"result": ai_response, "timestamp": time.time()}

@app.get("/")
async def read_root():
    return {"message": "Orion External API"}

@app.get("/state")
async def get_system_state():
    # Örnek sistem durumu verileri
    current_state = {
        "cpu_usage": 30,
        "memory_usage": 60,
        "active_tasks": ["task1", "task2"],
        "last_update": "2023-10-27T10:00:00Z"
    }
    return current_state

@app.get("/logs/errors")
async def get_error_logs():
    error_logs = []
    for filename in os.listdir(ERROR_ARCHIVE_DIR):
        if filename.startswith("error_") and filename.endswith(".log"):
            filepath = os.path.join(ERROR_ARCHIVE_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as log_file:
                    log_content = log_file.read()
                    error_logs.append({"filename": filename, "content": log_content})
            except Exception as e:
                logging.error(f"Hata logu okunurken hata oluştu {filename}: {e}")
                error_logs.append({"filename": filename, "error": str(e)})
    return error_logs

@app.get("/database/data")
async def get_database_data():
    try:
        # Gerçek Database_Manager'dan veri çekme mantığı buraya gelecek.
        # Şu anda sadece örnek veriler döndürüyoruz.
        # Örneğin, DatabaseManager'ınızın 'fetch_all_data' gibi bir metodu varsa:
        # data = log_manager.fetch_all_data() # Log_Manager örneği DatabaseManager ise
        # Veya DatabaseManager'dan başka bir instance oluşturup kullanabilirsiniz.

        # Şimdilik, Database_Manager'dan çekilmiş gibi örnek veri döndürelim:
        sample_db_data = [
            {"id": 1, "type": "event", "description": "Sistem başlatıldı", "timestamp": "2023-10-27T10:00:01Z", "agent_id": "system"},
            {"id": 2, "type": "log", "level": "INFO", "message": "Görev rapor_olustur tetiklendi", "timestamp": "2023-10-27T10:05:30Z", "agent_id": "streamlit"},
            {"id": 3, "type": "telemetry", "metric": "cpu_usage", "value": 35, "timestamp": "2023-10-27T10:06:00Z", "agent_id": "agent1"},
            {"id": 4, "type": "error", "message": "Veritabanı bağlantı hatası", "timestamp": "2023-10-27T10:07:15Z", "agent_id": "database_manager"}
        ]
        return {"data": sample_db_data, "message": "Veritabanı verileri başarıyla alındı."}
    except Exception as e:
        logging.error(f"Veritabanı verileri alınırken hata oluştu: {e}")
        raise HTTPException(status_code=500, detail=f"Veritabanı verileri alınamadı: {str(e)}")

from Agent_Telemetry_Injector import AgentTelemetryInjector
from Environment_Monitoring_Agent import EnvironmentMonitoringAgent

# Telemetri verilerini almak için uç nokta
@app.get("/telemetry")
async def get_telemetry_data():
    # İzlenecek ajanların listesi
    agents = [
        EnvironmentMonitoringAgent(log_manager),
    ]

    # Telemetri enjektörü örneği oluştur
    telemetry_injector = AgentTelemetryInjector(log_manager, agents, interval=10)

    # Metrikleri topla
    telemetry_data = telemetry_injector.collect_metrics()
    return telemetry_data