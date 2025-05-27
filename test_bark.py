from bark import generate_audio, SAMPLE_RATE
import numpy as np
import scipy.io.wavfile

text_prompt = "Merhaba! Ben Orion."
audio_array = generate_audio(text_prompt)

scipy.io.wavfile.write("orion_cikis.wav", SAMPLE_RATE, audio_array)