# BUILD - Miracles and Wonder 2026
Date: 2026-09-30
Goal: 5:00 intense, original music only, no Suno dependency.

## Fleet chain
1. songgeneration-mcp :10885 (web 10884) - draft beds + vocal guides
   Proven: MusicGen-small (CPU, stems/test-bed.wav). Next: Stable Audio Open after ~3GB download. Studio :10930 optional.
   Not used: ACE-Step (not in install script, unproven), Lyria (no GCP project, pay-per-use). See TEST-REPORT.md.
   No local vocal engine proven: vocals = hired impressionists + RVC.
2. stems-mcp :11126 - split drafts to vocals/drums/bass/other (needs uv sync + gpu extra + htdemucs download)
3. reaper-mcp - assemble + mix + render. Reaper UDP OSC 8000 in / 8001 out (Reaper's own, not web ports), backend 10797, frontend 10796
   Reaper exe: C:\Program Files\REAPER (x64)\reaper.exe (nonstandard path)
4. mixx-dj-mcp :11116 (web 11117) - test BPM/key/transitions
5. audiotool-nexus-mcp :11172 optional modular (moved off 10900, see WEBAPP_PORTS.md)

## Step 0 - backends up
```powershell
# songgeneration
cd D:\Dev\repos\songgeneration-mcp; uv sync; uv run uvicorn songgeneration_mcp.server:app --port 10885
# stems
cd D:\Dev\repos\stems-mcp; uv sync; uv run stems-mcp --mode http  # :11126
# reaper: open C:\Program Files\REAPER (x64)\reaper.exe, prefs Control/OSC/web Add 127.0.0.1 listen 8000 remote 8001 Send all feedback
```

## Step 1 - beds (MusicGen-small now, Stable Audio Open after download; instrumental only)
POST http://127.0.0.1:10885/api/v1/generate
- folk92: {"prompt": "dark folk 92 BPM A minor, fingerpicked lute + fretless bass homage, 6/8 lilt Greensleeves-shape but original, dry, 40s", "duration": 40}
- wonder: {"prompt": "hymnal folk lift 95 BPM Dorian, glass harmonica + choir pad, JWST awe, 40s", "duration": 40}
- list110: {"prompt": "patter folk-rock 110 BPM, driving acoustic + toms, listy verses, 40s", "duration": 40}
- kharkiv120: {"prompt": "doom folk 120 BPM, siren wash + low drone + FPV whine, winter black, 30s", "duration": 30}
- huddle138: {"prompt": "tense electro-folk 138 BPM, detuned clicks + sub pulse + children choir detuned, 30s", "duration": 30}
- ball-hits: {"prompt": "atonal staccato hits, strings clusters minor 2nds, no beat, rolling dread, 20s", "duration": 20}
- coda60: {"prompt": "60 BPM kalimba + brush + butterflies, A major pentatonic resolve, tape hiss, 30s", "duration": 30}

## Step 2 - vocals (hired takes + RVC, no clone)
- Direction for hired impressionists: "mature suave narrator baritone Price-style, talk-sung" for choruses, "breathy anxious tenor Lorre-style" for dark.
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
- Stable Audio Open timing conditioning
- MusicGen open beds
- RVC MIT voice convert
- Demucs MIT split (already)
- Essentia key/BPM
- FluidSynth PD soundfonts medieval

## Out
render.wav 48k + stems/ + regions.txt for video edit.
