import logging
import os
from fastapi import FastAPI
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

@app.post("/ai_service")
async def ai_service(prompt: str):
    return {"result": f"AI service result for prompt: {prompt}"}

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