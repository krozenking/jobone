import json
import subprocess

import json
import subprocess
import os
import requests

import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "../config/llm_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return {
        "strategy": config.get("llm_selection_strategy", {}),
        "api_keys": config.get("api_keys", {}),
        "on_failure": config.get("on_failure", {"return_error": True}),
        "output_format": config.get("output_format", {"text": True})
    }

class LLMRouter:
    def __init__(self, config_path="orion_vision_core/config/llm_config.json", task_config=None):
        self.config = load_config()
        self.task_config = task_config
        self.llm_selection_strategy = self.config["strategy"]
        self.api_keys = self.config["api_keys"]
        self.on_failure = self.config["on_failure"]

    def run_local(self, prompt):
        if not self.llm_selection_strategy.get("prefer_local", True):
            return None
        local_model = self.llm_selection_strategy.get("local_model", "mistral")
        try:
            os.environ['LANG'] = 'tr_TR.UTF-8'
            command = ["ollama", "run", local_model, prompt]
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Yerel modelde hata: {e}")
            return None

    def run_api(self, prompt, model):
        api_key = self.api_keys.get(model.split('/')[0])
        if not api_key:
            print(f"API anahtarı bulunamadı: {model}")
            return None

        if "openrouter" in model:
            api_url = f"https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "prompt": prompt
            }
            try:
                response = requests.post(api_url, headers=headers, json=data)
                response.raise_for_status()
                return response.json().get("choices")[0].get("text")
            except requests.exceptions.RequestException as e:
                print(f"OpenRouter API hatası: {e}")
                return None
        elif "google" in model:
            # Google API modelini çalıştırma mantığı burada olacak
            print("Google API modeli çalıştırılıyor (henüz uygulanmadı)")
            return "Google API modeli yanıtı (henüz uygulanmadı)"
        else:
            print(f"Desteklenmeyen API modeli: {model}")
            return None

    def route(self, prompt):
        # 1. Yerel model
        local_response = self.run_local(prompt)
        if local_response:
            return local_response

        # 2. API modelleri
        fallback_order = self.llm_selection_strategy.get("fallback_order", [])
        for model in fallback_order:
            api_response = self.run_api(prompt, model)
            if api_response:
                return api_response

        # 3. Hata durumu
        if self.on_failure.get("return_error", True):
            return "Hata: Tüm modeller başarısız oldu."
        else:
            return None

if __name__ == '__main__':
    # Örnek kullanım
    task_config = None

    router = LLMRouter(task_config=task_config) # task_config=None olarak ayarlandı
    prompt = "Orion, bana haftalık bir plan öner."
    response = router.route(prompt)
    print(f"Yanıt: {response}")