# BUILD - Miracles and Wonder 2026
Date: 2026-09-30
Goal: 5:00 intense, original music only, no Suno dependency.

## Fleet chain
1. songgeneration-mcp :10885 (web 10884) - draft beds + vocal guides
   Local ACE-Step 1.5 :8001 MIT ~2GB, Stable Audio 3 local, Lyria if GCP set, Studio :10930
2. stems-mcp :11126 - split drafts to vocals/drums/bass/other
3. reaper-mcp - assemble + mix + render. OSC 8000 in / 8001 out, backend 10797, frontend 10796
4. mixx-dj-mcp :11116 (web 11117) - test BPM/key/transitions
5. audiotool-nexus :10900 optional modular

## Step 0 - backends up
```powershell
# songgeneration
cd D:\Dev\repos\songgeneration-mcp; uv sync; uv run uvicorn songgeneration_mcp.server:app --port 10885
# ACE-Step local (separate shell)
uv run acestep-api  # :8001
# stems
cd D:\Dev\repos\stems-mcp; uv sync; uv run stems-mcp --mode http  # :11126
# reaper: open Reaper, prefs Control/OSC/web Add 127.0.0.1 listen 8000 remote 8001 Send all feedback
```

## Step 1 - beds (Stable Audio / ACE instrumental)
POST http://127.0.0.1:10885/api/v1/generate
- folk92: {"prompt": "dark folk 92 BPM A minor, fingerpicked lute + fretless bass homage, 6/8 lilt Greensleeves-shape but original, dry, 40s", "duration": 40}
- wonder: {"prompt": "hymnal folk lift 95 BPM Dorian, glass harmonica + choir pad, JWST awe, 40s", "duration": 40}
- list110: {"prompt": "patter folk-rock 110 BPM, driving acoustic + toms, listy verses, 40s", "duration": 40}
- kharkiv120: {"prompt": "doom folk 120 BPM, siren wash + low drone + FPV whine, winter black, 30s", "duration": 30}
- huddle138: {"prompt": "tense electro-folk 138 BPM, detuned clicks + sub pulse + children choir detuned, 30s", "duration": 30}
- ball-hits: {"prompt": "atonal staccato hits, strings clusters minor 2nds, no beat, rolling dread, 20s", "duration": 20}
- coda60: {"prompt": "60 BPM kalimba + brush + butterflies, A major pentatonic resolve, tape hiss, 30s", "duration": 30}

## Step 2 - vocals (ACE + RVC, no clone)
- Guide via ACE-Step vocal prompts: "mature suave narrator baritone Price-style, talk-sung" for choruses, "breathy anxious tenor Lorre-style" for dark.
- Hire clean takes, convert via RVC/Applio to style-of timbres, keep breath. Label style-of always.
- 18+ alt: finds -> kills take for late cut.

## Step 3 - split
POST http://127.0.0.1:11126 stems_separate separate folder with drafts. Keep vocal, rebuild band with FluidSynth PD lute/organ.

## Step 4 - assemble in Reaper
- reaper_orchestrator stem_import stems_folder="D:/Dev/repos/chitchat/projects/miracles-wonder-2026/stems"
- reaper_project marker regions: [SC1 00:00-00:40] [SC4 00:40-01:40] [SC7 02:20-03:00] [SC8 03:00-03:40] [SC9 03:40-04:20] [SC10+CODA 04:20-05:00]
- accelerando real: 92 to 138 automation, ball no-click staccato.
- friction: timing +-12ms, detune +-8c, second ALWAYS +10c sharp late 30ms.
- reaper_project render wav high.

## Step 5 - test
Load render to mixx deck 1: POST http://127.0.0.1:11116/api/v1/deck/1/load {"track_path": "render.wav"}. Check BPM drift, key, energy curve.

## FOSS to steal
- ACE-Step 1.5 MIT local song + LoRA
- Stable Audio Open timing conditioning
- MusicGen open beds
- RVC MIT voice convert
- Demucs MIT split (already)
- Essentia key/BPM
- FluidSynth PD soundfonts medieval

## Out
render.wav 48k + stems/ + regions.txt for video edit.
