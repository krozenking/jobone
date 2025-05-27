import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import asyncio
import httpx

app = FastAPI()

# Görev Durumu Seçenekleri
TASK_STATES = ["pending", "running", "completed", "failed"]

# Task modeli
class Task(BaseModel):
    id: str
    description: str
    agent: str  # screen_agent, speech_agent, vb.
    status: str = "pending"
    result: Optional[dict] = None

# Basit Task Manager
class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, description: str, agent: str) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, description=description, agent=agent)
        self.tasks[task_id] = task
        return task

    def update_task(self, task_id: str, status: str, result: Optional[dict] = None):
        if task_id not in self.tasks:
            raise ValueError("Task not found")
        self.tasks[task_id].status = status
        if result:
            self.tasks[task_id].result = result

    def get_task(self, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def list_tasks(self) -> List[Task]:
        return list(self.tasks.values())

task_manager = TaskManager()

# Agent API çağrıları için soyutlama
class AgentInterface:
    agent_endpoints = {
        "screen_agent": "http://localhost:8001/capture_screen/",
        # Diğer agentlar buraya eklenecek
    }

    async def call_agent(self, agent: str, payload: dict):
        if agent not in self.agent_endpoints:
            raise ValueError("Unknown agent")
        url = self.agent_endpoints[agent]
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

agent_interface = AgentInterface()

@app.post("/tasks/")
async def create_and_run_task(description: str, agent: str):
    try:
        # Görev oluştur
        task = task_manager.create_task(description, agent)
        logger.info(f"Task created with id: {task.id}")

        # Görev durumunu running olarak güncelle
        task_manager.update_task(task.id, "running")
        logger.info(f"Task {task.id} status updated to running")

        # Agent'ı çağır ve sonucu al
        try:
            # Örnek: ekran görüntüsü için bölge bilgisi ya da boş gönderilebilir
            payload = {}
            result = await agent_interface.call_agent(agent, payload)
            task_manager.update_task(task.id, "completed", result)
            logger.info(f"Task {task.id} completed successfully")
        except Exception as e:
            task_manager.update_task(task.id, "failed", {"error": str(e)})
            logger.error(f"Task {task.id} failed: {e}")

        return task_manager.get_task(task.id)
    except Exception as e:
        logger.error(f"Failed to create and run task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/")
def list_all_tasks():
    try:
        tasks = task_manager.list_tasks()
        logger.info("Listing all tasks")
        return tasks
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    try:
        task = task_manager.get_task(task_id)
        logger.info(f"Getting task with id: {task_id}")
        return task
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))