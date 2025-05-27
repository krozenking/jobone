import sys
sys.path.append('.')
import time
import threading
import json
import subprocess
import requests
import os

# Orion Vision Core modüllerini içe aktar
import torch
import numpy
torch.serialization.add_safe_globals([numpy.ndarray])
from orion_vision_core.agents import screen_agent
from orion_vision_core.agents import voice_agent
from orion_vision_core.agents import memory
from langchain_core.runnables import RunnableLambda

def test_screen_agent():
    print("Ekran takibi testi başlatılıyor...")
    # Ekran takibi işlevini test et
    screen_agent.capture_screenshot()
    print("Ekran takibi testi tamamlandı.")

def test_voice_agent():
    print("Sesli etkileşim testi başlatılıyor...")
    # Sesli etkileşim işlevini test et
    voice_agent_instance = voice_agent.VoiceAgent()
    voice_agent_instance.generate_voice("Merhaba Orion")
    print("Sesli etkileşim testi tamamlandı.")

def test_memory_management():
    print("Hafıza yönetimi testi başlatılıyor...")
    # Hafıza yönetimi işlevini test et
    memory_manager = memory.MemoryManager(
        persona_file='orion_vision_core/config/persona.json',
        memory_file='orion_vision_core/memory/orion_memory_v2.json'
    )
    memory_manager.update_memory("Test verisi")
    memory_manager.save_memory('orion_vision_core/memory/orion_memory_v2.json')
    print("Hafıza yönetimi testi tamamlandı.")

def test_llm_integration():
    print("LLM entegrasyonu testi başlatılıyor...")

    # 1. llm_config.json dosyasını okuyarak LLM'lerin öncelik sırasını belirleyin.
    config_path = os.path.join(os.path.dirname(__file__), "config/llm_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        llm_config = json.load(f)
        llm_strategy = llm_config["llm_selection_strategy"]
        prefer_local = llm_strategy["prefer_local"]
        local_model = llm_strategy["local_model"]
        fallback_order = llm_strategy["fallback_order"]
        api_keys = llm_config["api_keys"]

    # 2. Görev bazlı *.alt görevlerini okuyarak LLM'lerin öncelik sırasını güncelleyin (eğer varsa).
    # Bu örnekte, görev bazlı yapılandırma kullanılmıyor.

    # 3. Öncelik sırasına göre LLM'leri deneyin ve başarılı olan ilk LLM'i kullanın.
    def route_llm(prompt):
        llm_priority = []
        if prefer_local:
            llm_priority.append("ollama")
        llm_priority.extend(["openrouter" for _ in fallback_order])  # API modelleri için "openrouter" ekle

        for llm in llm_priority:
            try:
                if llm == "ollama":
                    # Ollama ile LLM'i kullan
                    os.environ['LANG'] = 'tr_TR.UTF-8'
                    command = ["ollama", "run", local_model, prompt]
                    result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
                    response = result.stdout
                elif llm == "openrouter":
                    # OpenRouter ile LLM'i kullan
                    model = fallback_order.pop(0)  # Sıradaki modeli al
                    api_key = api_keys.get(model.split('/')[0])
                    if not api_key:
                        print(f"API anahtarı bulunamadı: {model}")
                        continue  # Bir sonraki modele geç
                    api_url = f"https://openrouter.ai/api/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": model,
                        "prompt": prompt
                    }
                    response = requests.post(api_url, headers=headers, json=data).json().get("choices")[0].get("text")
                else:
                    raise ValueError(f"Bilinmeyen LLM: {llm}")
                return response
            except Exception as e:
                print(f"{llm} ile LLM kullanılırken hata oluştu: {e}")

        # 4. Tüm LLM'ler başarısız olursa, bir hata mesajı döndürün.
        raise ValueError("Hiçbir LLM kullanılamadı.")

    # RunnableLambda örneği
    llm_router = RunnableLambda(route_llm)

    # Görevi LLM'e gönder
    task = "Orion Vision Core nedir?"
    try:
        response = llm_router.invoke(task)
        print(f"LLM yanıtı: {response}")
    except Exception as e:
        print(f"LLM hatası: {e}")

    print("LLM entegrasyonu testi tamamlandı.")

def test_bark_import():
    print("Bark kütüphanesi içe aktarma testi başlatılıyor...")
    try:
        import bark
        print("Bark kütüphanesi başarıyla içe aktarıldı.")
    except ImportError as e:
        print(f"Bark kütüphanesi içe aktarma hatası: {e}")

def main():
    print("Orion Vision Core temel işlev testleri başlatılıyor...")

    # Her bir testi ayrı bir thread'de çalıştır
    bark_thread = threading.Thread(target=test_bark_import)
    screen_thread = threading.Thread(target=test_screen_agent)
    voice_thread = threading.Thread(target=test_voice_agent)
    memory_thread = threading.Thread(target=test_memory_management)
    llm_thread = threading.Thread(target=test_llm_integration)

    bark_thread.start()
    screen_thread.start()
    voice_thread.start()
    memory_thread.start()
    llm_thread.start()

    bark_thread.join()
    screen_thread.join()
    voice_thread.join()
    llm_thread.join()

    print("Orion Vision Core temel işlev testleri tamamlandı.")

if __name__ == "__main__":
    main()
