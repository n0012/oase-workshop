#!/usr/bin/env python3
"""Synthesize all 21 human scientist turns and 7 AI wingman turns across Chapters 1-7.

Human turns use Vertex AI Gemini 3.8 Live Avatar (`gemini-3.8-live` via
`google-genai` `BidiGenerateContent` WebSocket stream on `us-central1`) with the
Squadron camaraderie verbatim system prompt documented in
`prompts/avatar-live-system-prompt.md`, producing phase-locked `30.000 fps` CFR
video + `48 kHz` stereo PCM WAV clips (`slot_frames * 1600` integer samples).

Specialist AI wingman turns (`@science-program-lead`, `@computational-biologist`,
`@structural-biologist`, `@medicinal-chemist`, `@admet-dmpk-scientist`,
`@finding-validator`) use `gemini-3.8-flash-tts` with `110 ms` comm-link lead-in
and EBU R128 loudness normalization (`-16 LUFS`).
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import concurrent.futures
import datetime
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
import wave
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = REPO_ROOT / "scripts" / "pilot_chapters_spec.json"

VERBATIM_CAMARADERIE_PROMPT = (
    "You are an upbeat, warm, witty sci-fi mission teammate chatting live over "
    "squadron comms with close colleagues solving an exciting problem together. "
    "Smile naturally, bring fun, energetic camaraderie and lively vocal "
    "inflection, never a stiff narrator tone. Speak ONLY the exact words inside "
    "<script>...</script> verbatim from start to finish; do NOT add any extra "
    "words, greetings, commentary, or answers."
)

FPS = 30
AUDIO_SR = 48000
SAMPLES_PER_FRAME = AUDIO_SR // FPS  # 1600
BREATH_GAP_S = 0.65
LEAD_IN_S = 0.12

MEAN_VOL_RE = re.compile(r"mean_volume:\s*(-?[0-9.]+)\s*dB")
MAX_VOL_RE = re.compile(r"max_volume:\s*(-?[0-9.]+)\s*dB")
SILENCE_START_RE = re.compile(r"silence_start:\s*([0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*([0-9.]+)")

_NUM_WORDS = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    14: "fourteen",
}

_BIOPHARMA_PHONETIC_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bADMET\b"), "add-met"),
    (re.compile(r"\bDMPK\b"), "D-M-P-K"),
    (re.compile(r"\bhERG\b", re.IGNORECASE), "herg"),
    (re.compile(r"\bgnomAD\b", re.IGNORECASE), "gnome-add"),
    (re.compile(r"\bfpocket\b", re.IGNORECASE), "F-pocket"),
    (re.compile(r"\bChEMBL\b", re.IGNORECASE), "kem-bull"),
    (re.compile(r"\bHypEx\b", re.IGNORECASE), "hype-ex"),
    (re.compile(r"\bcLogP\b", re.IGNORECASE), "see-log-P"),
    (re.compile(r"\bTPSA\b"), "T-P-S-A"),
    (re.compile(r"\bLipE\b"), "lip-E"),
    (re.compile(r"\bpIC50\b", re.IGNORECASE), "P-I-C-fifty"),
    (re.compile(r"\bIC50\b", re.IGNORECASE), "I-C-fifty"),
    (re.compile(r"\bEC50\b", re.IGNORECASE), "E-C-fifty"),
    (re.compile(r"\bpLDDT\b", re.IGNORECASE), "P-L-D-D-T"),
    (re.compile(r"\bipTM\b", re.IGNORECASE), "I-P-T-M"),
    (re.compile(r"\bpTM\b"), "P-T-M"),
    (re.compile(r"\bGTEx\b", re.IGNORECASE), "G-tex"),
    (re.compile(r"\bLOEUF\b", re.IGNORECASE), "low-uff"),
    (re.compile(r"\bpLI\b"), "P-L-I"),
    (re.compile(r"\bLoF\b"), "loss of function"),
    (re.compile(r"\beQTL\b", re.IGNORECASE), "E-Q-T-L"),
    (re.compile(r"\bscRNA-seq\b", re.IGNORECASE), "single-cell R-N-A-seek"),
    (re.compile(r"\bRNA-seq\b", re.IGNORECASE), "R-N-A-seek"),
    (re.compile(r"\bATAC-seq\b", re.IGNORECASE), "ay-tack-seek"),
    (re.compile(r"\bPCSK9\b", re.IGNORECASE), "P-C-S-K-nine"),
    (re.compile(r"\bcGAS-STING\b", re.IGNORECASE), "see-gas sting"),
    (re.compile(r"\bcGAS\b", re.IGNORECASE), "see-gas"),
    (re.compile(r"\bcGAMP\b", re.IGNORECASE), "see-gamp"),
    (re.compile(r"\bENPP1\b", re.IGNORECASE), "E-N-P-P-one"),
    (re.compile(r"\bADAR1\b", re.IGNORECASE), "ay-dar-one"),
    (re.compile(r"\bPTPN2\b", re.IGNORECASE), "P-T-P-N-two"),
    (re.compile(r"\bTREX1\b", re.IGNORECASE), "T-rex-one"),
    (re.compile(r"\bKDM1A\b", re.IGNORECASE), "K-D-M-one-A"),
    (re.compile(r"\bLSD1\b", re.IGNORECASE), "L-S-D-one"),
    (re.compile(r"\bZBP1\b", re.IGNORECASE), "Z-B-P-one"),
    (re.compile(r"\bMDA5\b", re.IGNORECASE), "M-D-A-five"),
    (re.compile(r"\bCXCL9\b", re.IGNORECASE), "C-X-C-L-nine"),
    (re.compile(r"\bCXCL10\b", re.IGNORECASE), "C-X-C-L-ten"),
    (re.compile(r"\bELISA\b"), "uh-lie-zuh"),
    (re.compile(r"\bMC38\b", re.IGNORECASE), "M-C-thirty-eight"),
    (re.compile(r"\bCT26\b", re.IGNORECASE), "C-T-twenty-six"),
    (re.compile(r"\bCD8\+(?=\s|$|[.,;:])"), "C-D-eight positive"),
    (re.compile(r"\bCD8\b"), "C-D-eight"),
    (re.compile(r"\bcDC1\b"), "see-D-C-one"),
    (re.compile(r"\bPD-L1\b", re.IGNORECASE), "P-D-L-one"),
    (re.compile(r"\bPD-1\b", re.IGNORECASE), "P-D-one"),
    (re.compile(r"\bIFN-gamma\b", re.IGNORECASE), "interferon gamma"),
    (re.compile(r"\bIFN-I\b"), "type one interferon"),
    (re.compile(r"\bTCGA\b"), "T-C-G-A"),
    (re.compile(r"\bWOs\b"), "Work Orders"),
    (re.compile(r"\bWO\b"), "Work Order"),
]


def _replace_wo_match(m: re.Match[str]) -> str:
    n = int(m.group(1))
    word = _NUM_WORDS.get(n, str(n))
    rev = m.group(2)
    if rev:
        rnum = int(rev)
        rword = _NUM_WORDS.get(rnum, str(rnum))
        return f"Work Order {word} revision {rword}"
    return f"Work Order {word}"


def _replace_dec_match(m: re.Match[str]) -> str:
    n = int(m.group(1))
    word = _NUM_WORDS.get(n, str(n))
    return f"Decision {word}"


def normalize_biopharma_tts_text(text: str) -> str:
    """Rewrite biopharma acronyms & IDs into credible spoken phonetics for TTS/Avatar."""
    out = re.sub(r"\bWO-0*([1-9][0-9]*)(?:-r0*([1-9][0-9]*))?\b", _replace_wo_match, text)
    out = re.sub(r"\bDEC-0*([1-9][0-9]*)\b", _replace_dec_match, out)
    out = re.sub(r"\bDEC-OVERRIDE-0*([1-9][0-9]*)\b", lambda m: f"Decision Override {_NUM_WORDS.get(int(m.group(1)), m.group(1))}", out)
    for pat, repl in _BIOPHARMA_PHONETIC_RULES:
        out = pat.sub(repl, out)
    return out


def split_for_avatar(text: str, max_words: int = 24) -> list[str]:
    """Split long dialogue into <= max_words sentence/clause chunks for Live Avatar."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    chunks: list[str] = []
    cur: list[str] = []
    cur_words = 0
    for sent in sentences:
        words = sent.split()
        if len(words) > max_words:
            if cur:
                chunks.append(" ".join(cur))
                cur, cur_words = [], 0
            clauses = [c.strip() for c in re.split(r"(?<=[,;—])\s+", sent) if c.strip()]
            sub: list[str] = []
            sub_w = 0
            for cl in clauses:
                cw = len(cl.split())
                if sub and sub_w + cw > max_words:
                    chunks.append(" ".join(sub))
                    sub, sub_w = [cl], cw
                else:
                    sub.append(cl)
                    sub_w += cw
            if sub:
                chunks.append(" ".join(sub))
            continue
        if cur and cur_words + len(words) > max_words:
            chunks.append(" ".join(cur))
            cur, cur_words = [sent], len(words)
        else:
            cur.append(sent)
            cur_words += len(words)
    if cur:
        chunks.append(" ".join(cur))
    return chunks or [text.strip()]


def gcloud_access_token(gcloud_config: str | None) -> str:
    env = os.environ.copy()
    if gcloud_config:
        env["CLOUDSDK_ACTIVE_CONFIG_NAME"] = gcloud_config
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True, env=env
    ).strip()


def ffprobe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def ffprobe_video_frames(path: Path) -> int:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-count_frames",
            "-show_entries",
            "stream=nb_read_frames",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return int(out)


def detect_speech_bounds(path: Path) -> tuple[float, float, float]:
    """Return (speech_start_s, speech_end_s, full_duration_s) via ffmpeg silencedetect."""
    dur = ffprobe_duration(path)
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-vn",
            "-af",
            "silencedetect=noise=-38dB:d=0.18",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    stderr = proc.stderr or ""
    starts = [float(m.group(1)) for m in SILENCE_START_RE.finditer(stderr)]
    ends = [float(m.group(1)) for m in SILENCE_END_RE.finditer(stderr)]

    speech_start = 0.0
    if starts and ends and starts[0] < 0.05:
        speech_start = min(dur * 0.5, ends[0])

    speech_end = dur
    if starts and starts[-1] > speech_start + 0.35:
        if len(ends) < len(starts) or (ends and abs(ends[-1] - dur) < 0.12):
            speech_end = starts[-1]
    return speech_start, speech_end, dur


def compute_zero_latency_gain_db(path: Path, start_s: float, end_s: float) -> float:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-ss",
            f"{start_s:.4f}",
            "-to",
            f"{end_s:.4f}",
            "-i",
            str(path),
            "-vn",
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    m_mean = MEAN_VOL_RE.search(proc.stderr or "")
    m_max = MAX_VOL_RE.search(proc.stderr or "")
    mean_db = float(m_mean.group(1)) if m_mean else -18.0
    max_db = float(m_max.group(1)) if m_max else -2.0
    gain = min(-1.5 - max_db, -17.5 - mean_db)
    return max(-6.0, min(9.0, gain))


async def synthesize_live_chunk(
    chunk_text: str,
    avatar_name: str,
    voice_id: str,
    gcp_project: str,
    location: str,
    gcloud_config: str | None,
    out_mp4: Path,
) -> Path:
    from google import genai
    from google.genai import types
    import google.auth.credentials

    class GcloudTokenCredentials(google.auth.credentials.Credentials):
        def __init__(self, cfg: str | None) -> None:
            super().__init__()
            self._cfg = cfg
            self.refresh(None)

        def refresh(self, request) -> None:
            self.token = gcloud_access_token(self._cfg)
            self.expiry = datetime.datetime.now(datetime.timezone.utc).replace(
                tzinfo=None
            ) + datetime.timedelta(minutes=30)

    client = genai.Client(
        vertexai=True,
        project=gcp_project,
        location=location,
        credentials=GcloudTokenCredentials(gcloud_config),
    )
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.VIDEO],
        avatar_config=types.AvatarConfig(avatar_name=avatar_name),
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_id)
            )
        ),
        temperature=0.1,
        output_audio_transcription=types.AudioTranscriptionConfig(),
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=VERBATIM_CAMARADERIE_PROMPT)]
        ),
    )
    prompt = f"Read this slide script verbatim:\n<script>{chunk_text}</script>"
    expected_words = re.findall(r"[a-z0-9]+", chunk_text.lower())
    tail_phrase = (
        " ".join(expected_words[-2:])
        if len(expected_words) >= 2
        else (expected_words[-1] if expected_words else "")
    )

    last_err: Exception | None = None
    for attempt in range(1, 5):
        video_buf = bytearray()
        transcripts: list[str] = []
        try:
            async def _stream_once() -> None:
                nonlocal speech_done_at
                async with client.aio.live.connect(model="gemini-3.8-live", config=config) as session:
                    await session.send_realtime_input(text=prompt)
                    async for msg in session.receive():
                        sc = getattr(msg, "server_content", None)
                        if not sc:
                            continue
                        turn = getattr(sc, "model_turn", None)
                        for part in getattr(turn, "parts", None) or []:
                            inline = getattr(part, "inline_data", None)
                            if inline and inline.data and "video/mp4" in (inline.mime_type or ""):
                                video_buf.extend(inline.data)
                        tr = getattr(sc, "output_transcription", None)
                        if tr and getattr(tr, "text", None):
                            transcripts.append(tr.text)
                            spoken_words = re.findall(r"[a-z0-9]+", "".join(transcripts).lower())
                            spoken_norm = " ".join(spoken_words)
                            if (
                                tail_phrase
                                and len(spoken_words) >= max(1, len(expected_words) - 3)
                                and tail_phrase in spoken_norm
                                and speech_done_at is None
                            ):
                                speech_done_at = time.monotonic()
                        if getattr(sc, "turn_complete", False):
                            break
                        if speech_done_at and (time.monotonic() - speech_done_at) > 2.0:
                            break

            speech_done_at: float | None = None
            await asyncio.wait_for(_stream_once(), timeout=45.0)

            if not video_buf:
                raise RuntimeError(f"Empty video stream returned for {avatar_name}/{voice_id}")
            out_mp4.write_bytes(bytes(video_buf))

            spoken_words = re.findall(r"[a-z0-9]+", "".join(transcripts).lower())
            min_words = max(4, int(len(expected_words) * 0.72))
            max_words = max(len(expected_words) + 6, int(len(expected_words) * 1.40))
            if len(spoken_words) < min_words or len(spoken_words) > max_words:
                raise RuntimeError(
                    f"Transcript word-count mismatch ({len(spoken_words)} vs expected {len(expected_words)}): {' '.join(spoken_words)}"
                )
            s_start, s_end, full_dur = detect_speech_bounds(out_mp4)
            spoken_span = s_end - s_start
            vproc = subprocess.run(
                ["ffmpeg", "-hide_banner", "-nostats", "-i", str(out_mp4), "-vn", "-af", "volumedetect", "-f", "null", "-"],
                capture_output=True,
                text=True,
                check=False,
            )
            m_mean = MEAN_VOL_RE.search(vproc.stderr or "")
            mean_db = float(m_mean.group(1)) if m_mean else -91.0
            min_span_s = max(2.2, min(4.2, len(expected_words) * 0.20))
            if mean_db < -34.0 or spoken_span < min_span_s or spoken_span > 26.5:
                raise RuntimeError(
                    f"Audio quality gate failed (mean_db={mean_db:.1f} dB, spoken_span={spoken_span:.2f}s, full={full_dur:.2f}s)"
                )
            # Multimodal prosody gate via Gemini 3.1 Pro: block robotic vowel stretches, stutters, or repetitions
            qa_wav = out_mp4.with_suffix(".qa.wav")
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(out_mp4), "-vn", "-ac", "1", "-ar", "16000", str(qa_wav)],
                check=True,
            )
            qa_client = genai.Client(
                vertexai=True,
                project=gcp_project,
                location="global",
                credentials=GcloudTokenCredentials(gcloud_config),
                http_options=types.HttpOptions(timeout=30000),
            )
            qa_resp = qa_client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=[
                    types.Part.from_bytes(data=qa_wav.read_bytes(), mime_type="audio/wav"),
                    (
                        f"Listen carefully to this voice clip. Expected script: {chunk_text!r}. "
                        "Return JSON with keys: verbatim_transcript (string), delivery_issues "
                        "('none' if natural and clean, otherwise describe any robotic glitch, elongated word, "
                        "false start, stutter, repetition, or cutoff), rating_1_to_10 (int)."
                    ),
                ],
                config=types.GenerateContentConfig(temperature=0.0, response_mime_type="application/json"),
            )
            qa_wav.unlink(missing_ok=True)
            qa_data = json.loads((qa_resp.text or "{}").strip())
            qa_rating = int(qa_data.get("rating_1_to_10", 0))
            qa_issues = str(qa_data.get("delivery_issues", "")).strip()
            if qa_rating < 9 or (qa_issues and qa_issues.lower() != "none"):
                raise RuntimeError(
                    f"Prosody QA gate rejected clip (rating={qa_rating}/10, issues={qa_issues!r}, heard={qa_data.get('verbatim_transcript')!r})"
                )
            print(f"  [PROSODY QA PASS {qa_rating}/10] {avatar_name}/{voice_id}: {qa_data.get('verbatim_transcript')}", flush=True)
            return out_mp4
        except Exception as exc:
            last_err = exc
            print(f"  [RETRY {attempt}/4] {avatar_name}/{voice_id}: {exc}", flush=True)
            await asyncio.sleep(1.5 * attempt)

    raise RuntimeError(f"Failed live avatar synthesis after 4 attempts: {last_err}")


def stitch_chunks(part_paths: list[Path], stitched_out: Path) -> Path:
    if len(part_paths) == 1:
        return part_paths[0]
    concat_list = stitched_out.with_suffix(".concat.txt")
    concat_list.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in part_paths) + "\n", encoding="utf-8"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list),
            "-c",
            "copy",
            str(stitched_out),
        ],
        check=True,
    )
    concat_list.unlink(missing_ok=True)
    return stitched_out


def render_single_human_turn(
    job: dict,
    live_dir: Path,
    audio_dir: Path,
    work_dir: Path,
    gcp_project: str,
    location: str,
    gcloud_config: str | None,
) -> dict:
    tid = job["turn_id"]
    ch_id = job["chapter"]
    speaker = job["speaker"]
    avatar_name = job["avatar_name"]
    voice_id = job["voice_id"]
    raw_text = job["tts_text"]

    out_mp4 = live_dir / f"{tid}_live30.mp4"
    out_wav = audio_dir / f"{tid}.wav"

    if (
        out_mp4.exists()
        and out_mp4.stat().st_size > 250_000
        and out_wav.exists()
        and out_wav.stat().st_size > 50_000
    ):
        n_frames = ffprobe_video_frames(out_mp4)
        slot_s = n_frames / float(FPS)
        tts_dur = round(max(1.0, slot_s - BREATH_GAP_S), 4)
        print(f"[CACHED] {tid} ({avatar_name}/{voice_id}): {n_frames} frames ({slot_s:.2f}s)", flush=True)
        return {
            "turn_id": tid,
            "chapter": ch_id,
            "speaker": speaker,
            "avatar_name": avatar_name,
            "voice_id": voice_id,
            "duration_s": tts_dur,
            "slot_frames": n_frames,
            "wav": str(out_wav),
            "live_avatar_mp4": str(out_mp4),
        }

    clean_text = re.sub(r"<[^>]+>", " ", raw_text)
    clean_text = normalize_biopharma_tts_text(clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()
    chunks = split_for_avatar(clean_text, max_words=32)

    turn_work = work_dir / tid
    turn_work.mkdir(parents=True, exist_ok=True)
    print(f"[START] {tid} ({speaker} -> {avatar_name}/{voice_id}): {len(chunks)} chunks", flush=True)

    part_paths: list[Path] = []
    for k, chunk_text in enumerate(chunks):
        part_mp4 = turn_work / f"part_{k:02d}.mp4"
        asyncio.run(
            synthesize_live_chunk(
                chunk_text=chunk_text,
                avatar_name=avatar_name,
                voice_id=voice_id,
                gcp_project=gcp_project,
                location=location,
                gcloud_config=gcloud_config,
                out_mp4=part_mp4,
            )
        )
        part_paths.append(part_mp4)

    stitched_src = stitch_chunks(part_paths, turn_work / f"{tid}_stitched24.mp4")
    speech_start, speech_end, full_s = detect_speech_bounds(stitched_src)

    trim_start = max(0.0, speech_start - LEAD_IN_S)
    raw_trim_end = min(full_s, speech_end + BREATH_GAP_S)
    span_s = max(1.5, raw_trim_end - trim_start)
    desired_slot_s = (speech_end - trim_start) + BREATH_GAP_S
    slot_frames = max(45, int(round(desired_slot_s * FPS)))
    exact_slot_s = slot_frames / float(FPS)
    extra_hold_s = max(0.0, exact_slot_s - span_s + 0.15)
    gain_db = compute_zero_latency_gain_db(stitched_src, trim_start, raw_trim_end)

    tpad_expr = f",tpad=stop_mode=clone:stop_duration={extra_hold_s:.3f}" if extra_hold_s > 0.001 else ""
    vf = (
        f"[0:v]trim=start={trim_start:.4f}:end={raw_trim_end:.4f},setpts=PTS-STARTPTS,"
        f"fps={FPS}:start_time=0,settb=1/{FPS},setsar=1,format=yuv420p{tpad_expr}[v];"
        f"[0:a]atrim=start={trim_start:.4f}:end={raw_trim_end:.4f},asetpts=PTS-STARTPTS,"
        f"volume={gain_db:.2f}dB,aresample={AUDIO_SR},pan=stereo|c0=c0|c1=c0,"
        f"apad,atrim=0:{exact_slot_s:.6f}[a]"
    )
    tmp_pcm_wav = turn_work / f"{tid}_exact48k.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(stitched_src),
            "-filter_complex",
            vf,
            "-map",
            "[v]",
            "-frames:v",
            str(slot_frames),
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out_mp4),
            "-map",
            "[a]",
            "-c:a",
            "pcm_s16le",
            "-ar",
            str(AUDIO_SR),
            "-ac",
            "2",
            str(tmp_pcm_wav),
        ],
        check=True,
    )

    with wave.open(str(tmp_pcm_wav), "rb") as wr:
        raw_pcm = wr.readframes(wr.getnframes())
    target_bytes = slot_frames * SAMPLES_PER_FRAME * 4
    if len(raw_pcm) < target_bytes:
        raw_pcm += b"\x00" * (target_bytes - len(raw_pcm))
    else:
        raw_pcm = raw_pcm[:target_bytes]
    with wave.open(str(out_wav), "wb") as ww:
        ww.setnchannels(2)
        ww.setsampwidth(2)
        ww.setframerate(AUDIO_SR)
        ww.writeframes(raw_pcm)
    tmp_pcm_wav.unlink(missing_ok=True)

    muxed_mp4 = turn_work / f"{tid}_muxed30.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(out_mp4),
            "-i",
            str(out_wav),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(AUDIO_SR),
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(muxed_mp4),
        ],
        check=True,
    )
    shutil.move(str(muxed_mp4), str(out_mp4))

    actual_frames = ffprobe_video_frames(out_mp4)
    assert actual_frames == slot_frames, f"{tid}: expected {slot_frames} frames, got {actual_frames}"
    tts_dur = round(exact_slot_s - BREATH_GAP_S, 4)
    print(f"[DONE] {tid} ({avatar_name}/{voice_id}): {slot_frames} frames ({exact_slot_s:.2f}s)", flush=True)
    return {
        "turn_id": tid,
        "chapter": ch_id,
        "speaker": speaker,
        "avatar_name": avatar_name,
        "voice_id": voice_id,
        "duration_s": tts_dur,
        "slot_frames": slot_frames,
        "wav": str(out_wav),
        "live_avatar_mp4": str(out_mp4),
    }


def render_single_agent_turn(
    job: dict,
    audio_dir: Path,
    work_dir: Path,
    gcp_project: str,
    access_token: str,
) -> dict:
    tid = job["turn_id"]
    ch_id = job["chapter"]
    speaker = job["speaker"]
    voice_id = job["voice_id"]
    text = normalize_biopharma_tts_text(job["tts_text"])
    wav_path = audio_dir / f"{tid}.wav"

    if wav_path.exists() and wav_path.stat().st_size > 20_000:
        dur_s = round(ffprobe_duration(wav_path), 3)
        print(f"[CACHED-AI] {tid} ({speaker}/{voice_id}): {dur_s:.2f}s", flush=True)
        return {
            "turn_id": tid,
            "chapter": ch_id,
            "speaker": speaker,
            "avatar_name": "",
            "voice_id": voice_id,
            "duration_s": dur_s,
            "slot_frames": int(round((dur_s + BREATH_GAP_S) * FPS)),
            "wav": str(wav_path),
            "live_avatar_mp4": "",
        }

    url = (
        f"https://aiplatform.googleapis.com/v1beta1/projects/{gcp_project}/locations/global/"
        "publishers/google/models/gemini-3.8-flash-tts:generateContent"
    )
    body = {
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"voice": voice_id}},
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "x-goog-user-project": gcp_project,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    raw_b64 = resp["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    raw_tmp = work_dir / f"{tid}_ai_raw.wav"
    raw_tmp.write_bytes(base64.b64decode(raw_b64))
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(raw_tmp),
            "-af",
            "silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,"
            "areverse,silenceremove=start_periods=1:start_silence=0.08:start_threshold=-45dB,"
            "areverse,adelay=110|110,loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar",
            str(AUDIO_SR),
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(wav_path),
        ],
        check=True,
    )
    raw_tmp.unlink(missing_ok=True)
    dur_s = round(ffprobe_duration(wav_path), 3)
    print(f"[DONE-AI] {tid} ({speaker} -> {voice_id}): {dur_s:.2f}s", flush=True)
    return {
        "turn_id": tid,
        "chapter": ch_id,
        "speaker": speaker,
        "avatar_name": "",
        "voice_id": voice_id,
        "duration_s": dur_s,
        "slot_frames": int(round((dur_s + BREATH_GAP_S) * FPS)),
        "wav": str(wav_path),
        "live_avatar_mp4": "",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gcp-project",
        default=os.environ.get("GCP_PROJECT_ID", ""),
        help="Vertex AI GCP project ID (or set GCP_PROJECT_ID).",
    )
    parser.add_argument(
        "--location",
        default=os.environ.get("VERTEX_AVATAR_LOCATION", "us-central1"),
        help="Vertex AI region for gemini-3.8-live (default: us-central1).",
    )
    parser.add_argument(
        "--gcloud-config",
        default=os.environ.get("GCLOUD_CONFIG", ""),
        help="Optional gcloud configuration name.",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=DEFAULT_SPEC,
        help="Path to scripts/pilot_chapters_spec.json.",
    )
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=Path("/tmp/oase-media-assets"),
        help="Output assets directory containing audio/ and talking-heads/live_turns/.",
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("/tmp/oase-live-avatar-work"),
        help="Scratch working directory for intermediate chunk files.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Parallel synthesis workers (default: 4).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.gcp_project:
        raise SystemExit("Error: pass --gcp-project or set GCP_PROJECT_ID.")

    audio_dir = args.assets_dir / "audio"
    live_dir = args.assets_dir / "talking-heads" / "live_turns"
    live_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    args.work_dir.mkdir(parents=True, exist_ok=True)

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    voices = spec["voices"]
    dur_path = audio_dir / "audio_durations.json"

    agent_jobs: list[dict] = []
    human_jobs: list[dict] = []
    updated_durs: dict[str, dict] = {}

    for ch in spec["chapters"]:
        ch_id = ch["chapter"]
        for t in ch["turns"]:
            tid = t["turn_id"]
            sp = t["speaker"]
            vmeta = voices[sp]
            if vmeta.get("is_agent", False):
                agent_jobs.append(
                    {
                        "turn_id": tid,
                        "chapter": ch_id,
                        "speaker": sp,
                        "voice_id": vmeta["voice_id"],
                        "tts_text": t["tts_text"],
                    }
                )
            else:
                human_jobs.append(
                    {
                        "turn_id": tid,
                        "chapter": ch_id,
                        "speaker": sp,
                        "avatar_name": vmeta["avatar_name"],
                        "voice_id": vmeta["voice_id"],
                        "tts_text": t["tts_text"],
                    }
                )

    print(f"=== Synthesizing {len(agent_jobs)} Specialist AI Wingman Turns via Gemini 3.8 Flash TTS ===", flush=True)
    tok = gcloud_access_token(args.gcloud_config or None)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        afuts = {
            pool.submit(
                render_single_agent_turn,
                j,
                audio_dir,
                args.work_dir,
                args.gcp_project,
                tok,
            ): j["turn_id"]
            for j in agent_jobs
        }
        for fut in concurrent.futures.as_completed(afuts):
            updated_durs[afuts[fut]] = fut.result()

    print(f"=== Synthesizing {len(human_jobs)} Human Turns via Gemini 3.8 Live Avatar ({args.location}) ===", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futs = {
            pool.submit(
                render_single_human_turn,
                j,
                live_dir,
                audio_dir,
                args.work_dir,
                args.gcp_project,
                args.location,
                args.gcloud_config or None,
            ): j["turn_id"]
            for j in human_jobs
        }
        for fut in concurrent.futures.as_completed(futs):
            updated_durs[futs[fut]] = fut.result()

    ordered: dict[str, dict] = {}
    for ch in spec["chapters"]:
        for t in ch["turns"]:
            tid = t["turn_id"]
            ordered[tid] = updated_durs[tid]

    dur_path.write_text(json.dumps(ordered, indent=2), encoding="utf-8")
    print(
        f"\n[SUCCESS] Rendered {len(human_jobs)} Gemini 3.8 Live Avatar clips + {len(agent_jobs)} AI Wingman clips -> {dur_path}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
