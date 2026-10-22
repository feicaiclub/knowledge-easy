# Runtime setup

Run `scripts/run.sh` from this Skill's actual location. On Windows, use `scripts/run.ps1`. `<skill>` and `<project>` below stand for absolute paths on the current user's machine.

```sh
sh "<skill>/scripts/run.sh" doctor --features core,render,voice --install
```

Commands check for existing tools before installing missing ones. Writing alone does not trigger downloads. Request only the features needed: `core` for media inspection and review; `render` for HyperFrames; `voice` for narration; `audio` for mixing; `asr` for transcription; and `download` for acquiring footage. Production commands select their own requirements. `doctor` without `--install` checks without installing.

| Dependency | Where it goes |
| --- | --- |
| Python 3.12 and Python packages | A user-managed interpreter and an isolated environment in the user's cache |
| Node.js | Reuses Node 22+ when available; otherwise downloads a user-local copy from nodejs.org and checks its SHA256 |
| FFmpeg and ffprobe | Reuses a working, matching pair; otherwise prepares a separate user-local pair |
| HyperFrames and GSAP | An npm environment in the user's cache; browser-side files needed by a film are copied into that film's project |
| Chromium | HyperFrames' browser cache |
| Qwen and ASR weights | The user's Hugging Face cache, downloaded on first use |
| Fonts, maps, and the voice reference | Bundled creative assets, not runtime installations |

Default runtime directories are `~/Library/Caches/FEICAI/vibe-knowledge-video` on macOS, `%LOCALAPPDATA%/FEICAI/vibe-knowledge-video` on Windows, and `$XDG_CACHE_HOME/feicai/vibe-knowledge-video` or `~/.cache/feicai/vibe-knowledge-video` on Linux. `VIBE_RUNTIME_HOME` can override the location, but must remain outside the Skill. Existing Hugging Face and uv caches are reused. The original `vibe-knowledge-video` cache namespace and `VIBE_RUNTIME_HOME` override are retained so installing Knowledge Easy does not trigger duplicate model or dependency downloads.

`VIBE_FFMPEG` and `VIBE_FFPROBE` can point to an existing tool pair. `VIBE_PYTHON` can select an existing environment; its version and packages are still checked. No virtual environment, node_modules, browser, model weights, or download cache belongs in the Skill folder. Outputs belong in the selected film project.

Pinned versions and model revisions are in `scripts/runtime-lock.json`. Start with this proven production stack:

| Task | Approved implementation |
| --- | --- |
| Narration | MLX Audio 0.6.1, Qwen3-TTS 1.7B Base bf16, bundled D reference, body-v1 finishing |
| Transcription | MLX Whisper 0.4.3, `mlx-community/whisper-large-v3-mlx`, word timestamps enabled, previous-text conditioning disabled |
| Video rendering | HyperFrames 0.8.185, the bundled editorial renderer, and GSAP 3.13.0 |
| Music and effects | The approved film used ElevenLabs `music_v2_5` and `sound-generation`; choose and time separate cues for each story |

The original narration and transcription implementations use MLX and require Apple Silicon. That is a requirement of these implementations, not a restriction on who may use the Skill. Resolve machine-specific compatibility when someone uses the Skill; testing every platform is not a prerequisite for packaging it. The production baseline was exercised on an Apple Silicon Mac.

When a capability is first used, check the recipient's machine for compatible tools and install only what is missing outside the Skill. If setup fails, identify the actual cause, such as hardware support, a version conflict, network access, or permissions. Try to repair the original setup first. If it cannot run there, investigate suitable dependencies or a compatible implementation, preferably retaining the same model, voice reference, and finishing settings. Explain meaningful differences in output, performance, or cost, and check a small representative result on that machine before full production. Save the working configuration and any adaptations in that film project so later runs can reuse them. Keep this package's proven defaults intact.

Do not silently change the voice or claim an untested alternative produces identical results. If no workable alternative is available, explain what remains blocked. External music services are optional. Read credentials from the user's environment; never put them in this package or logs.

Sources: [uv installer options](https://docs.astral.sh/uv/reference/installer/), [Node.js releases](https://nodejs.org/dist/), [Qwen3-TTS Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base).
