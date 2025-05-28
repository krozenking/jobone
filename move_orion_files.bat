@echo off
REM Yönetici olarak çalıştırılması önerilir

REM DataManagementModule
mkdir src\aura_core\modules\DataManagementModule
move log_manager.py src\aura_core\modules\DataManagementModule\
move database_manager.py src\aura_core\modules\DataManagementModule\

REM LLMIntegrationModule
mkdir src\aura_core\modules\LLMIntegrationModule
move llm_router.py src\aura_core\modules\LLMIntegrationModule\
move train_or_finetune.py src\aura_core\modules\LLMIntegrationModule\

REM CognitiveAgentModule
mkdir src\aura_core\modules\CognitiveAgentModule
move runner_service.py src\aura_core\modules\CognitiveAgentModule\
move ai_scheduler_agent.py src\aura_core\modules\CognitiveAgentModule\
move query_optimizer_agent.py src\aura_core\modules\CognitiveAgentModule\

REM UserInterfaceModule
mkdir src\aura_core\modules\UserInterfaceModule
move screen_agent.py src\aura_core\modules\UserInterfaceModule\
move terminal_logger.py src\aura_core\modules\UserInterfaceModule\
move streamlit_app.py src\aura_core\modules\UserInterfaceModule\

REM ConfigModule
mkdir src\aura_core\modules\ConfigModule
move config.py src\aura_core\modules\ConfigModule\
move config_manager.py src\aura_core\modules\ConfigModule\

REM TaskManagerModule
mkdir src\aura_core\modules\TaskManagerModule
move task_manager.py src\aura_core\modules\TaskManagerModule\
move scheduler.py src\aura_core\modules\TaskManagerModule\

REM TrainerModule
mkdir src\aura_core\modules\TrainerModule
move trainer.py src\aura_core\modules\TrainerModule\

REM AgentManagerModule
mkdir src\aura_core\modules\AgentManagerModule
move agent_interface.py src\aura_core\modules\AgentManagerModule\
move agent_endpoints.json src\aura_core\modules\AgentManagerModule\

REM Config dosyaları
mkdir config
move persona.json config\
move llm_config.json config\
move continue.config.json config\

REM Data dosyaları
mkdir data
move orion_memory_v2.json data\
move *.last data\

REM Çekirdek ve ana dosya
mkdir src\aura_core
move core_app.py src\aura_core\
move main.py .

echo Tüm dosyalar taşındı.
pause
