# /// script
# requires-python = ">=3.11"
# dependencies = ["torch", "transformers", "soundfile", "numpy"]
#
# [tool.uv.sources]
# torch = { index = "pytorch-cu128" }
#
# [[tool.uv.index]]
# name = "pytorch-cu128"
# url = "https://download.pytorch.org/whl/cu128"
# explicit = true
# ///
"""Render the 7 BUILD.md Step 1 beds with MusicGen-small on CUDA.

Run: uv run D:/Dev/repos/chitchat/projects/miracles-wonder-2026/stems/gen_beds.py [bed ...]
MusicGen caps one pass at 30s, so 40s beds are rendered at 30s (extend in Reaper).
"""
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

MODEL = "facebook/musicgen-small"
OUT_DIR = Path(__file__).parent
FRAME_RATE = 50  # tokens per second
MAX_SECONDS = 30

BEDS = {
    "folk92": ("dark folk 92 BPM A minor, fingerpicked lute + fretless bass, 6/8 lilt, dry", 30),
    "wonder": ("hymnal folk lift 95 BPM Dorian, glass harmonica + choir pad, awe", 30),
    "list110": ("patter folk-rock 110 BPM, driving acoustic + toms, listy verses", 30),
    "kharkiv120": ("doom folk 120 BPM, siren wash + low drone + FPV whine, winter black", 30),
    "huddle138": ("tense electro-folk 138 BPM, detuned clicks + sub pulse + children choir detuned", 30),
    "ball-hits": ("atonal staccato hits, strings clusters minor 2nds, no beat, rolling dread", 20),
    "coda60": ("60 BPM kalimba + brush + butterflies, A major pentatonic resolve, tape hiss", 30),
}

names = sys.argv[1:] or list(BEDS)
unknown = [n for n in names if n not in BEDS]
if unknown:
    sys.exit(f"unknown bed(s): {unknown}; choose from {list(BEDS)}")

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device, torch.cuda.get_device_name(0) if device == "cuda" else "")
processor = AutoProcessor.from_pretrained(MODEL)
model = MusicgenForConditionalGeneration.from_pretrained(MODEL).to(device)
rate = model.config.audio_encoder.sampling_rate

for name in names:
    prompt, seconds = BEDS[name]
    seconds = min(seconds, MAX_SECONDS)
    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
    start = time.time()
    with torch.no_grad():
        audio = model.generate(**inputs, max_new_tokens=seconds * FRAME_RATE, do_sample=True, guidance_scale=3.0)
    samples = audio[0, 0].float().cpu().numpy()
    path = OUT_DIR / f"{name}.wav"
    sf.write(path, samples, rate)
    print(f"{name}: {len(samples) / rate:.1f}s @ {rate}Hz in {time.time() - start:.1f}s -> {path}")
