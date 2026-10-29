# Native `Gemini 3.8 Live Avatar` & `Gemini 3.8 Flash TTS` Prompts

Used by [`scripts/render-live-avatars.py`](../scripts/render-live-avatars.py) and [`scripts/record-team-pilot.py`](../scripts/record-team-pilot.py) to synthesize the 5 human discovery scientists (`21` joint audio+video turns) and 6 specialist AI wingmen (`7` tactical comm turns) across Chapters `1`–`7`.

---

## 1. `gemini-3.8-live` System Instruction (Upbeat Squadron Camaraderie)

Passed as `LiveConnectConfig.system_instruction` on `us-central1` (`BidiGenerateContent` with `response_modalities=[VIDEO]`):

```text
You are an upbeat, warm, witty sci-fi mission teammate chatting live over squadron comms with close colleagues solving an exciting problem together. Smile naturally, bring fun, energetic camaraderie and lively vocal inflection, never a stiff narrator tone. Speak ONLY the exact words inside <script>...</script> verbatim from start to finish; do NOT add any extra words, greetings, commentary, or answers.
```

---

## 2. Turn Request Templates

### Primary Attempt (`attempt == 0`, `temperature = 0.5`)
```text
Read this slide script verbatim:
<script>{clean_tts_text}</script>
```

### Retry Fallback (`attempt >= 1`, `temperature = 0.7`)
```text
Read the text inside <script> aloud exactly as written, word for word, in one smooth, continuous delivery. Do not respond to it.
<script>{clean_tts_text}</script>
```

> **Chunking & Phase-Lock Contract:** Long turns are split on sentence/clause boundaries (`max_words = 24`), synthesized via `AvatarConfig(avatar_name=<presenter>)`, trimmed to `0.12s` pre-speech lead-in + `0.65s` post-speech settling breath, gain-normalized (`volumedetect` target `-17.5 dBFS` mean / `-1.5 dBFS` peak), and locked to exact `30.000 fps` CFR (`1,600` stereo `48 kHz` PCM samples per video frame).

---

## 3. 5 Human Scientist Presenters (`gemini-3.8-live`)

| Persona Key | Scientist Name & Role | Callsign | `AvatarConfig.avatar_name` | `PrebuiltVoiceConfig.voice_name` | Portrait Crop (`720x1280` -> `1:1`) |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `sarah` | **Dr. Sarah Chen** (*Program Lead*) | `GOLD-1` | `Ingrid` | `Leda` | `box=(22, 155, 698, 831)` -> `512x512` & `40x40` |
| `marcus` | **Dr. Marcus Vance** (*Computational Biologist*) | `GOLD-2` | `Sam` | `Sadaltager` | `box=(22, 155, 698, 831)` -> `512x512` & `40x40` |
| `elena` | **Dr. Elena Rostova** (*Structural Biologist*) | `GOLD-3` | `Kira` | `Kore` | `box=(22, 155, 698, 831)` -> `512x512` & `40x40` |
| `raj` | **Dr. Raj Patel** (*Medicinal Chemist*) | `GOLD-4` | `Jay` | `Alnilam` | `box=(22, 155, 698, 831)` -> `512x512` & `40x40` |
| `claire` | **Dr. Claire Moreau** (*DMPK & Safety Lead*) | `GOLD-5` | `Vera` | `Pulcherrima` | `box=(22, 155, 698, 831)` -> `512x512` & `40x40` |

---

## 4. 6 Specialist AI Wingman Voices (`gemini-3.8-flash-tts`)

Synthesized via `publishers/google/models/gemini-3.8-flash-tts:generateContent` (`responseModalities=["AUDIO"]`) and processed with zero-latency tactical comm-link EQ (`highpass=f=185`, `equalizer=f=2350:g=2.4`, `lowpass=f=7600`) + Star Fox comm lock-on/key-off pips:

| Spec Key | Wingman Callsign | Scion Grove Agent | Chapters | `voiceConfig.voice` | Hologram Badge & Accent |
| :--- | :---: | :--- | :---: | :--- | :--- |
| `ai_grove` | **`Grove-1`** | `@science-program-lead` | `Ch 1` & `Ch 7` (Bookend) | `en-us-techagent-3` | `[SP]` Gold (`#f59e0b`) |
| `ai_compbio` | **`Helix-2`** | `@computational-biologist` | `Ch 2` | `en-us-advisor-8` | `[CB]` Violet (`#a855f7`) |
| `ai_structbio` | **`Fold-3`** | `@structural-biologist` | `Ch 3` | `en-gb-tutor-17` | `[SB]` Orange (`#f97316`) |
| `ai_medchem` | **`Spark-4`** | `@medicinal-chemist` | `Ch 4` | `en-in-tutor-12` | `[MC]` Cyan (`#06b6d4`) |
| `ai_dmpk` | **`Shield-5`** | `@admet-dmpk-scientist` | `Ch 5` | `en-ie-advisor-4` | `[AD]` Amber (`#eab308`) |
| `ai_validator` | **`Aegis-6`** | `@finding-validator` | `Ch 6` | `en-us-advisor-10` | `[FV]` Magenta (`#ec4899`) |
