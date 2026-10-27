# 按需准备运行环境

只有执行制作时才准备对应依赖。写稿、改 Skill 和阅读设计说明不触发下载。

macOS / Linux 使用 scripts/run.sh，Windows 使用 scripts/run.ps1。doctor 默认只检查，显式 --install 才安装。core 用于媒体检查，render 用于渲染，voice 用于旁白，audio 用于混音，asr 用于转写，download 用于获取素材。

| 依赖 | 使用方式 |
| --- | --- |
| Python 3.12 与 Python 库 | 先检查已有环境，缺失时在用户缓存创建独立环境 |
| Node.js | 复用兼容的 Node 22+，必要时准备用户本地版本 |
| FFmpeg / ffprobe | 复用版本匹配的工具对，缺失时在用户缓存准备 |
| HyperFrames / GSAP | 安装到用户缓存中的 npm 环境；成片需要的浏览器文件放入该项目 |
| Chromium | 由 HyperFrames 管理浏览器缓存 |
| Qwen / ASR 模型 | 首次使用时下载至用户的 Hugging Face 缓存 |

版本与模型修订以 scripts/runtime-lock.json 为准。默认旁白使用 Qwen3-TTS CustomVoice 1.7B 8bit，声线与原生表达配置见 assets/voice/profile.json；模型锁定与声线记录须一致。node_modules、虚拟环境、浏览器、模型权重、下载缓存和成片均不应放入 Skill 目录。

macOS 缓存默认在 ~/Library/Caches/FEICAI/vibe-knowledge-video；Windows 使用 LOCALAPPDATA 下的 FEICAI/vibe-knowledge-video；Linux 使用 XDG_CACHE_HOME 或 ~/.cache 下的 feicai/vibe-knowledge-video。VIBE_RUNTIME_HOME 可指定外部位置，原有缓存命名保留以避免重复下载。

VIBE_PYTHON、VIBE_FFMPEG 和 VIBE_FFPROBE 可指定现有工具，仍需检查实际兼容性。默认 MLX 旁白和转写实现需要 Apple Silicon；遇到不同机器时先诊断能力和版本，必要时在用户授权的执行范围内寻找兼容实现，不静默换声线或宣称效果等同。

运行环境准备不等于视觉、动作或旁白验收。用户自行试跑时，交付文件即可，不替其安装或执行。
