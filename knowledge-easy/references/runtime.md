# On-Demand Runtime Setup

Prepare dependencies only when the corresponding production step runs. Writing, editing the Skill, and reading design guidance do not trigger downloads.

Use scripts/run.sh on macOS / Linux and scripts/run.ps1 on Windows. doctor checks by default and installs only with an explicit --install. core supports media inspection, render handles rendering, voice handles narration, audio handles mixing, asr handles transcription, and download handles media acquisition.

| Dependency | Setup behavior |
| --- | --- |
| Python 3.12 and Python libraries | Check existing environments first; create an isolated environment in the user's cache if needed |
| Node.js | Reuse a compatible Node 22+ installation, or prepare a user-local version when needed |
| FFmpeg / ffprobe | Reuse a matching tool pair, or prepare one in the user's cache |
| HyperFrames / GSAP | Install in a cached npm environment; place browser-side files needed by a film in that film's project |
| Chromium | HyperFrames manages the browser cache |
| Qwen / ASR models | Download to the user's Hugging Face cache on first use |

scripts/runtime-lock.json is authoritative for versions and model revisions. The default narrator uses Qwen3-TTS CustomVoice 1.7B 8bit. Voice identity and native delivery settings are in assets/voice/profile.json; the profile and model lock must agree. Keep node_modules, virtual environments, browsers, model weights, download caches, and finished films outside the Skill directory.

The default macOS cache is ~/Library/Caches/FEICAI/vibe-knowledge-video. Windows uses FEICAI/vibe-knowledge-video under LOCALAPPDATA. Linux uses XDG_CACHE_HOME or ~/.cache, under feicai/vibe-knowledge-video. VIBE_RUNTIME_HOME can select another external location. The existing cache name is retained to avoid duplicate downloads.

VIBE_PYTHON, VIBE_FFMPEG, and VIBE_FFPROBE can select existing tools, subject to compatibility checks. The default MLX narration and transcription implementations require Apple Silicon. On a different machine, first inspect capabilities and versions, then find a compatible implementation if needed within the user's authorized scope. Do not silently change the voice or claim equivalent results.

A prepared runtime does not establish visual, motion, or narration quality. When the user plans to run their own trial, deliver the files without installing or executing the workflow for them.
