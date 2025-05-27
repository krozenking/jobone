import torch
import numpy as np

torch.serialization.add_safe_globals([
    np.ndarray,
    np.float32,
    np.int64,
    np.dtype,
    np.generic,
])
import bark
import scipy.io.wavfile
import os

class VoiceAgent:
    def __init__(self, voice="v2/en_speaker_6"):
        # Bark modelini yükle
        try:
            bark.preload_models()
            print("Bark modelleri başarıyla yüklendi.")
        except Exception as e:
            print(f"Bark modelleri yüklenirken hata oluştu: {e}")
        self.voice = voice

    def generate_voice(self, text, output_path="output.wav"):
        try:
            # Metinden ses üret
            audio_array = bark.generate_audio(text)

            # Ses verisini WAV dosyasına kaydet
            sample_rate = bark.SAMPLE_RATE
            scipy.io.wavfile.write(output_path, sample_rate, audio_array)

            return output_path
        except Exception as e:
            print(f"Ses üretimi sırasında hata oluştu: {e}")
            return None

if __name__ == '__main__':
    # Örnek kullanım
    voice_agent = VoiceAgent()
    text = "Merhaba, bu bir test sesidir."
    output_path = voice_agent.generate_voice(text)

    if output_path:
        print(f"Ses dosyası oluşturuldu: {output_path}")
        # Ses dosyasını çal (isteğe bağlı)
        os.system(f"start {output_path}")
    else:
        print("Ses üretimi başarısız.")
