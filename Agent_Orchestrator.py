import asyncio
import logging
from typing import Dict, List, Callable, Any

# Temel Ajan Sınıfı (Örnek)
class Agent:
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.status = "idle"  # idle, working, paused, error

    async def execute_task(self, task: Dict):
        """
        Ajanın görevi yürütme mantığı.
        """
        self.status = "working"
        logging.info(f"Ajan {self.name}: Görev yürütülüyor: {task['description']}")
        await asyncio.sleep(2)  # Görevi simüle et
        self.status = "idle"
        logging.info(f"Ajan {self.name}: Görev tamamlandı: {task['description']}")
        return {"status": "completed", "result": "Görev başarıyla tamamlandı."}

# Görev Yöneticisi Sınıfı
class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}  # görev_id: görev
        self.task_queue: asyncio.Queue = asyncio.Queue()

    async def create_task(self, description: str, agent_constraints: List[str]) -> str:
        """
        Yeni bir görev oluşturur ve görev kuyruğuna ekler.
        """
        task_id = f"task-{len(self.tasks) + 1}"
        task = {
            "task_id": task_id,
            "description": description,
            "agent_constraints": agent_constraints,
            "status": "pending",  # pending, assigned, completed, failed
            "result": None,
        }
        self.tasks[task_id] = task
        await self.task_queue.put(task)
        logging.info(f"Görev oluşturuldu: {task_id} - {description}")
        return task_id

    async def get_next_task(self) -> Dict:
        """
        Kuyruktan bir sonraki görevi alır.
        """
        task = await self.task_queue.get()
        return task

    def update_task_status(self, task_id: str, status: str, result: Any = None):
        """
        Görev durumunu günceller.
        """
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if result:
                self.tasks[task_id]["result"] = result
            logging.info(f"Görev durumu güncellendi: {task_id} - {status}")
        else:
            logging.warning(f"Görev bulunamadı: {task_id}")

# Ajan Orkestratörü Sınıfı
class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}  # agent_name: Ajan
        self.task_manager = TaskManager()
        self.running = True

    def register_agent(self, agent: Agent):
        """
        Yeni bir ajanı orkestratöre kaydeder.
        """
        self.agents[agent.name] = agent
        logging.info(f"Ajan kaydedildi: {agent.name} - Yetenekler: {agent.capabilities}")

    def unregister_agent(self, agent_name: str):
        """
        Bir ajanı orkestratörden kaldırır.
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            logging.info(f"Ajan kaldırıldı: {agent_name}")
        else:
            logging.warning(f"Ajan bulunamadı: {agent_name}")

    async def assign_task_to_agent(self, task: Dict):
        """
        Bir görevi uygun bir ajana atar.
        """
        task_id = task["task_id"]
        agent_constraints = task["agent_constraints"]

        available_agents = [
            agent
            for agent in self.agents.values()
            if agent.status == "idle"
            and all(capability in agent.capabilities for capability in agent_constraints)
        ]

        if available_agents:
            agent = available_agents[0]  # İlk uygun ajanı seç
            logging.info(f"Görev {task_id}, ajana atandı: {agent.name}")
            self.task_manager.update_task_status(task_id, "assigned")
            result = await agent.execute_task(task)
            self.task_manager.update_task_status(task_id, "completed", result)
        else:
            logging.warning(f"Görev {task_id} için uygun ajan bulunamadı.")
            self.task_manager.update_task_status(task_id, "failed", "Uygun ajan bulunamadı.")

    async def run(self):
        """
        Orkestratörü çalıştırır ve görevleri yönetir.
        """
        logging.info("Ajan Orkestratörü çalışıyor...")
        while self.running:
            task = await self.task_manager.get_next_task()
            if task:
                await self.assign_task_to_agent(task)
                self.task_manager.task_queue.task_done()  # Görevi kuyruktan kaldır
            else:
                await asyncio.sleep(1)  # Görev yoksa bekle

    def stop(self):
        """
        Orkestratörü durdurur.
        """
        self.running = False
        logging.info("Ajan Orkestratörü durduruldu.")

# --- Örnek Kullanım ---
async def main():
    # Logging yapılandırması
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    orchestrator = AgentOrchestrator()

    # Ajanları oluştur
    agent1 = Agent("SesAjanı", ["ses", "metin"])
    agent2 = Agent("EkranAjanı", ["ekran", "görüntü"])
    orchestrator.register_agent(agent1)
    orchestrator.register_agent(agent2)

    # Görevleri oluştur
    task1_id = await orchestrator.task_manager.create_task(
        "Bir ses dosyasını analiz et.", ["ses"]
    )
    task2_id = await orchestrator.task_manager.create_task(
        "Ekran görüntüsünü al ve metni çıkar.", ["ekran", "görüntü", "metin"]
    )

    # Orkestratörü çalıştır
    asyncio.create_task(orchestrator.run())

    # Bir süre çalışmasını bekle
    await asyncio.sleep(10)

    # Orkestratörü durdur
    orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())