# Knowledge Easy

废才 FEICAI 的中文知识视频 Skill。覆盖文稿、素材选择、视觉设计、插画、剪辑、配音、声音与审片，也可只完成其中一个环节。

## 安装

本机有 Node.js / npm（含 npx）与 Git 后，运行：

```bash
npx -y skills add feicaiclub/knowledge-easy --agent codex --global --yes
```

更新时如需先卸载旧版：

```bash
npx -y skills remove knowledge-easy --agent codex --global --yes
npx -y skills add feicaiclub/knowledge-easy --agent codex --global --yes
```

Codex 的安装目录为 `~/.agents/skills/knowledge-easy/`。仓库只有一个 Skill，安装命令会找到 `knowledge-easy/SKILL.md`；仓库根目录的说明、校验工具和测试不会进入 Skill。

使用时可以直接说：

```text
用 Knowledge Easy 制作一条中文知识视频。先根据这个选题和稿子确定视觉方案，使用组件源码与插画工具完成画面，按稿意安排配音和剪辑，最后检查导出的画面、动作和完整声音。
```

也可以明确只写稿、改图或审阅源码，Skill 按请求范围执行。

## 文件夹与分享

可以直接将整个 [knowledge-easy](knowledge-easy/) 文件夹发给别人。接收方将它放入兼容 Agent 的 Skill 目录，保留文件夹内的相对路径即可。

```text
knowledge-easy/
├── SKILL.md      中文制作方法与验收要求，底部保留 FEICAI 启动标识
├── assets/       组件和插画源码、字体、地图、参考音频、Lazy Studio
├── references/   接口、制作说明、运行方式、许可与来源
└── scripts/      环境准备、构建、配音、转写、混音与审查工具
```

不需要发送研究目录、预览网页、测试成片、缓存或本机环境。运行依赖、浏览器与模型权重在使用对应功能时准备，放在 Skill 之外。影视和库存素材不随 Skill 提供，制作时另行选择；组件目录中的视频文件名是可替换的素材槽位。

## 当前内容

- 12 类基础组件和 15 个变体，可按内容组合，或注册项目自己的扩展。
- 动态素材背景、原生虚化与明暗处理，清晰前景、中文字体和受光文字材质；纸面插画与清晰影像按镜头用途选择。
- 分层 SVG 插画示例，以及线描、叠色和淡彩绘图工具。新题材需要重新设计对象、构图和动作，不只替换文字。
- 默认旁白为已选定的「沉稳男声·紧凑重音版」：Qwen3-TTS CustomVoice 的 Ryan 预设配原生表达指令。各段仍需根据文稿调整重音、停顿和情绪，并独立听审。
- Lazy Studio 保留 M → 评论 → Enter 的逐帧反馈方式；回到原对话读取反馈并返修。

完整制作指令见 [SKILL.md](knowledge-easy/SKILL.md)，命令见 [工作流](knowledge-easy/references/workflow.md)。

## 环境与检查边界

默认本地配音和转写依赖 MLX，需要 Apple Silicon Mac。其他系统使用这两项能力需要兼容实现，不能把复制文件夹当作所有平台均已验证。其余依赖与版本见 [运行环境](knowledge-easy/references/runtime.md) 和 [版本锁定](knowledge-easy/scripts/runtime-lock.json)。

技术检查、视觉自审和用户确认分别记录。`accept-visuals` 校验审查证据、填写情况和版本对应，不自动判断审美，也不代表整套素材、配音与混音已经自动验收。源码和预设检查通过，不等于每个新题材的成片质量已经通过。

维护仓库时，可以运行以下检查；它们不安装制作模型或合成旁白：

```bash
python3 -B tools/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -q
```

媒体审片测试需要已有 FFmpeg / ffprobe，仓库 CI 会准备它们。

## 许可与来源

本项目自行编写的代码与说明遵循 [MIT License](LICENSE)。字体、地图、模型输出及视觉临摹示例的来源与适用边界见 [许可与来源](knowledge-easy/references/sources.md)；第三方角色与构图不作为本项目原创或纳入代码许可。运行库、浏览器和模型不打包进 Skill。

FEICAI 名称与启动标识保留为作者品牌，代码许可不表示作者为衍生项目背书。
