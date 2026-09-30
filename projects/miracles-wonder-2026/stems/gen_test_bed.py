"""Test bed generation: MusicGen-small folk 92 BPM, 10s.
Proves songgeneration local backend works before full assfix.
Run: uv run --directory D:/Dev/repos/songgeneration-mcp python D:/Dev/repos/chitchat/projects/miracles-wonder-2026/stems/gen_test_bed.py
"""
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

MODEL = "facebook/musicgen-small"
OUT = r"D:\Dev\repos\chitchat\projects\miracles-wonder-2026\stems\test-bed.wav"
PROMPT = "dark folk lute fingerpicked 92 BPM A minor, melancholic ballad bed"

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)
processor = AutoProcessor.from_pretrained(MODEL)
model = MusicgenForConditionalGeneration.from_pretrained(MODEL).to(device)
inputs = processor(text=[PROMPT], padding=True, return_tensors="pt").to(device)
with torch.no_grad():
    audio = model.generate(**inputs, max_new_tokens=501)  # ~10s at 50Hz frame rate
samples = audio[0, 0].float().cpu().numpy()
rate = model.config.audio_encoder.sampling_rate
print("samples:", samples.shape, "rate:", rate)

try:
    import soundfile as sf
    sf.write(OUT, samples, rate)
except ImportError:
    from scipy.io import wavfile
    wavfile.write(OUT, rate, samples)
print("wrote:", OUT)
