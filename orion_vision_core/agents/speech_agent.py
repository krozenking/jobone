import whispercpp
import io
import numpy as np

class SpeechAgent:
    def __init__(self, model_path="whisper/models/ggml-base.en.bin"):
        try:
            self.model = whispercpp.Whisper()
            print("Whisper modeli başarıyla yüklendi.")
        except Exception as e:
            print(f"Whisper modeli yüklenirken hata oluştu: {e}")
            self.model = None

    def transcribe_audio(self, audio_data):
        try:
            # Ses verisini NumPy dizisine dönüştür
            audio_np = np.frombuffer(audio_data, dtype=np.float32)

            # Ses verisini transkribe et
            if self.model:
                text = self.model.transcribe(audio_np.tolist())
            else:
                print("Model yüklenemediği için transkripsiyon yapılamıyor.")
                return None

            return text
        except Exception as e:
            print(f"Transkripsiyon sırasında hata oluştu: {e}")
            return None

    def process_audio_file(self, audio_file_path):
        try:
            # Ses dosyasını oku
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()

            # Ses verisini transkribe et
            text = self.transcribe_audio(audio_data)

            return text
        except Exception as e:
            print(f"Ses dosyası işlenirken hata oluştu: {e}")
            return None

if __name__ == '__main__':
    # Örnek kullanım
    speech_agent = SpeechAgent()
    # Ses dosyası yolu (örneğin, "audio.wav")
    audio_file_path = "audio.wav"
    transcription = speech_agent.process_audio_file(audio_file_path)

    if transcription:
        print(f"Transkripsiyon: {transcription}")
    else:
        print("Transkripsiyon başarısız.")
