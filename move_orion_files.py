import os
import shutil
import sys

# Kök dizin (bu scriptin bulunduğu yer)
ROOT = os.path.dirname(os.path.abspath(__file__))

# Taşıma haritası: kaynak dosya adı -> hedef klasör (modüler yapı)
MOVE_MAP = {
    # DataManagementModule
    "log_manager.py": "src/aura_core/modules/DataManagementModule/",
    "database_manager.py": "src/aura_core/modules/DataManagementModule/",
    # LLMIntegrationModule
    "llm_router.py": "src/aura_core/modules/LLMIntegrationModule/",
    "train_or_finetune.py": "src/aura_core/modules/LLMIntegrationModule/",
    # CognitiveAgentModule
    "runner_service.py": "src/aura_core/modules/CognitiveAgentModule/",
    "ai_scheduler_agent.py": "src/aura_core/modules/CognitiveAgentModule/",
    "query_optimizer_agent.py": "src/aura_core/modules/CognitiveAgentModule/",
    # UserInterfaceModule
    "screen_agent.py": "src/aura_core/modules/UserInterfaceModule/",
    "terminal_logger.py": "src/aura_core/modules/UserInterfaceModule/",
    "streamlit_app.py": "src/aura_core/modules/UserInterfaceModule/",
    # ConfigModule
    "config.py": "src/aura_core/modules/ConfigModule/",
    "config_manager.py": "src/aura_core/modules/ConfigModule/",
    # TaskManagerModule
    "task_manager.py": "src/aura_core/modules/TaskManagerModule/",
    "scheduler.py": "src/aura_core/modules/TaskManagerModule/",
    # TrainerModule
    "trainer.py": "src/aura_core/modules/TrainerModule/",
    # AgentManagerModule
    "agent_interface.py": "src/aura_core/modules/AgentManagerModule/",
    "agent_endpoints.json": "src/aura_core/modules/AgentManagerModule/",
    # Config dosyaları
    "persona.json": "config/",
    "llm_config.json": "config/",
    "continue.config.json": "config/",
    # Data dosyaları
    "orion_memory_v2.json": "data/",
    # Çekirdek ve ana dosya
    "core_app.py": "src/aura_core/",
    "main.py": ".",
}

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

def run_as_admin():
    if sys.platform.startswith('win'):
        import ctypes
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1)
        sys.exit(0)

def move_files():
    moved = []
    for fname, rel_target in MOVE_MAP.items():
        # Dosya kökte mi, src/aura_core'da mı, başka yerde mi kontrol et
        possible_paths = [
            os.path.join(ROOT, fname),
            os.path.join(ROOT, "src", "aura_core", fname),
            os.path.join(ROOT, "src", "aura_core", "modules", fname),
        ]
        src_path = next((p for p in possible_paths if os.path.isfile(p)), None)
        if not src_path:
            continue  # Dosya yok, atla
        target_dir = os.path.join(ROOT, rel_target)
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, fname)
        if os.path.abspath(src_path) == os.path.abspath(target_path):
            continue  # Zaten doğru yerde
        shutil.move(src_path, target_path)
        moved.append((src_path, target_path))
    # *.last dosyalarını data/ klasörüne taşı
    for fname in os.listdir(ROOT):
        if fname.endswith(".last") and os.path.isfile(os.path.join(ROOT, fname)):
            os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
            shutil.move(os.path.join(ROOT, fname), os.path.join(ROOT, "data", fname))
    # Unicode uyumlu çıktı
    try:
        print("Taşınan dosyalar:".encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))
        for src, dst in moved:
            print(f"{src} -> {dst}")
    except UnicodeEncodeError:
        print("Tasınan dosyalar:")
        for src, dst in moved:
            print(f"{src} -> {dst}")

if __name__ == "__main__":
    if not is_admin():
        print("Yönetici izni gereklidir, script yeniden başlatılıyor...")
        run_as_admin()
    try:
        move_files()
    except PermissionError:
        print("Bazı dosyalar taşınamadı. Lütfen bu scripti yönetici olarak çalıştırın.")

# Bu scripti çalıştırmak için terminal veya komut istemcisinde aşağıdaki adımları izleyin:
#
# 1. Terminali veya Komut İstemcisini açın.
# 2. Scriptin bulunduğu klasöre gidin:
#    ```sh
#    cd "c:\Users\ozy\Desktop\orion\Orion_B"
#    ```
# 3. Scripti çalıştırın:
#    ```sh
#    python move_orion_files.py
#    ```
# 4. Eğer yönetici izni gerekiyorsa, script otomatik olarak kendini yönetici olarak yeniden başlatacaktır. Onay vermeniz gerekebilir.
#
# > Not: Python 3 yüklü olmalı ve PATH'e eklenmiş olmalı.
