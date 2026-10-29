# Prompt & Persona Registry (`prompts/`)

Every LLM system instruction, live Webchat prompt, voice synthesis script, container task prompt, and visual diagram prompt used to build the **GCP-OASE 7-Chapter Team Discovery Pilot** is recorded in Git across the files below.

---

## 1. Complete Prompt Inventory

| Prompt Layer | Version-Controlled Path | Model / Runtime Target | Purpose |
| :--- | :--- | :--- | :--- |
| **7-Chapter Multi-Persona Dialogue, Callsigns & Live Q&A Prompts** | [`scripts/pilot_chapters_spec.json`](../scripts/pilot_chapters_spec.json) | Scion Webchat + `gemini-3.8-live` + `gemini-3.8-flash-tts` | All **28 turns** (`21` human scientist turns + `7` specialist AI wingman turns) across Chapters `1`–`7`, dual-layer `chat_text` (verbatim metrics + SHA-256 citations) and `tts_text` (100/200-level spoken script), plus copyable live Webchat Q&A prompts. |
| **Native `Gemini 3.8 Live Avatar` Verbatim Camaraderie Prompt** | [`prompts/avatar-live-system-prompt.md`](avatar-live-system-prompt.md) & [`scripts/render-live-avatars.py`](../scripts/render-live-avatars.py) | `gemini-3.8-live` (`us-central1` `BidiGenerateContent`) | System instruction, `<script>...</script>` turn wrapper, retry prompt, presenter-to-voice map (`Ingrid`/`Leda`..`Vera`/`Pulcherrima`), and 6-wingman `gemini-3.8-flash-tts` voice IDs. |
| **11 Scion Grove Specialist Agent Personas & Container Task Prompts** | [`prompts/grove-agent-personas.md`](grove-agent-personas.md) & [`scripts/seed-pilot-chapters.py`](../scripts/seed-pilot-chapters.py) | `gemini-3.8-flash`, `gemini-3.1-pro-preview`, `Claude`, `OpenAI` inside Scion Docker containers | T-shaped specialist role definitions, two-phase CLI execution rules (`never compute metrics in prose`), mandatory epistemic relay requirements, and live Webchat standby prompts for `ch0`..`ch7`. |
| **Standalone Portal SSML Voiceover Script** | [`docs/video-scenes.json`](../docs/video-scenes.json) & [`scripts/record-demo-video.py`](../scripts/record-demo-video.py) | Google Cloud Text-to-Speech (`SSML` + IPA `<phoneme>` tags) | Scene-by-scene SSML narration and pronunciation tags (`OASE`, `Elo`, `ADMET`, `hERG`) for the single-narrator portal walkthrough. |
| **Architecture & Pillar Visual Infographic Prompts** | [`prompts/visual-infographic-prompts.md`](visual-infographic-prompts.md) | Image generation (`assets/oase_*.jpg` / `.png`) | Structured visual layout prompts used to generate the 4-pillar architecture, 5-layer artifact funnel, stage-gate workflow, and workshop blueprint diagrams in [`assets/`](../assets/). |
