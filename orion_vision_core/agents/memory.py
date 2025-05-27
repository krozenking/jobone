import json

class MemoryManager:
    def __init__(self, persona_file, memory_file):
        self.persona = self.load_json(persona_file)
        self.memory = self.load_json(memory_file)

    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_persona(self):
        return self.persona

    def get_memory(self):
        return self.memory

    def update_memory(self, new_memory):
        self.memory = new_memory

    def save_memory(self, memory_file):
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    # Örnek kullanım
    memory_manager = MemoryManager(
        persona_file='orion_vision_core/config/persona.json',
        memory_file='orion_vision_core/memory/orion_memory_v2.json'
    )

    # Kişiliği al
    persona = memory_manager.get_persona()
    print("Kişilik:", persona)

    # Hafızayı al
    memory = memory_manager.get_memory()
    print("Hafıza:", memory)

    # Hafızayı güncelle
    new_memory = {
        "amac": "Orion Vision Core'un amacı, kullanıcılara görsel verileri analiz etme ve yorumlama konusunda daha da iyi yardımcı olmaktır.",
        "temel_bilgiler": [
            "Orion Vision Core, en son yapay zeka algoritmalarını kullanır.",
            "Proje, gerçek zamanlı veri işleme ve analiz yeteneklerine sahiptir.",
            "Kullanıcı dostu ve özelleştirilebilir bir arayüz sunar."
        ]
    }
    memory_manager.update_memory(new_memory)

    # Hafızayı kaydet
    memory_manager.save_memory('orion_vision_core/memory/orion_memory_v2.json')
    print("Hafıza güncellendi ve kaydedildi.")
