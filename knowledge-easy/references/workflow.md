# 命令与项目文件

制作方法和质量判断统一见 [SKILL.md](../SKILL.md)。本页是接口索引；只改 Skill 时不要执行制作命令。

## 命令入口

`<skill>` 为本 Skill 目录，`<project>` 为外部项目目录。macOS / Linux 使用 `sh "<skill>/scripts/run.sh"`；Windows 使用 `& "<skill>/scripts/run.ps1"`。执行前读取 [运行环境](runtime.md)，voice、render、mix 等制作入口会按需准备依赖，不能当作无副作用的文件检查命令。

下面以 macOS / Linux 为例，按实际任务选用：

```sh
sh "<skill>/scripts/run.sh" init --project "<project>" --language zh-CN
sh "<skill>/scripts/run.sh" voice --project "<project>" --plan voice-plan.json
sh "<skill>/scripts/run.sh" transcribe --project "<project>" --file audio/narration/narration.wav
sh "<skill>/scripts/run.sh" build --project "<project>"
sh "<skill>/scripts/run.sh" preview --project "<project>"
sh "<skill>/scripts/run.sh" mix --project "<project>" --plan music-plan.json
sh "<skill>/scripts/run.sh" render --project "<project>" --output final/film-v1.mp4
```

先填写实际数据，再执行对应命令；若 mix 后改变 film.mix，再 build 后 render。render 不覆盖已存在的目标。字体、图片、代码与音频变化后，旧 build 或旧导出的审查记录不再代表新结果。

## 输入与来源

| 文件 | 实际用途 |
| --- | --- |
| project.json | 项目身份、语言与既有决定 |
| film.json | 场景、组件、素材、字幕、可选 beats/extensions 与 mix |
| voice-plan.json | 完整段落、可选读音修正、每段 direction |
| music-plan.json | narration、duration、cues、混音输出；声音通过 start 或 event/offset 定位 |
| assets.json | 素材来源、使用区间与原始镜头身份 |
| kit/editorial-lock.json | 项目内渲染源码及字体快照 |

当前组件工作坐标为 1920×1080，默认 30 fps。scene.start 为绝对秒数，图层 start、duration 和 cues 为局部时间。不同画幅需要实际适配构图和渲染实现，不能只修改元数据宣称适配。

## 构建与检查产物

| 阶段 | 产物与检查入口 | 能说明什么 |
| --- | --- | --- |
| build | research/component-usage.json、research/build-receipt.json | 实际调用的源码、内容、阅读顺序与版本 |
| render（含技术检查） | review/technical-check.json、review/render-receipt.json | 解码、时长、音轨及导出绑定；不是美学结论 |
| review-visuals | review/visual-review.json 及其引用的比较页面、帧、动作片段 | 待观察的实际导出证据 |
| accept-visuals | 核对上述记录、证据与版本 | 已记录的自审是否完整；不自动评价质量或代替用户认可 |

```sh
sh "<skill>/scripts/run.sh" verify --project "<project>" --file final/film-v1.mp4
sh "<skill>/scripts/run.sh" review-visuals --project "<project>" --file final/film-v1.mp4
sh "<skill>/scripts/run.sh" accept-visuals --project "<project>"
```

render 已自动准备一次审查材料。review-visuals 用于同一导出重新准备；它不会替你观看。记录中的 frames、motion_file、sequence 和整片播放入口覆盖不同观察范围；新增截图不能自动把 pending 改为 pass。

## 可选入口

- `catalog --base`：查看 12 类基础组件；`catalog --art`：查看原创绘图起点。完整扩展示例需要 `--media-dir` 指向可用素材。只为理解参数时直接读源文件，不必生成目录样片。
- `install-pack --update`：有意识地升级已有项目快照，保留旧片版本；不要在普通返修中顺带升级。
- `audit-media`：项目采用移动镜头不重复约定时核对 assets.json；还需对照实际剪入内容，台账不完整时结果不足以证明无重复。
- `register --file final/film-v1.mp4 --label 初版 --id v1`，随后 `studio`：登记已有导出并进入 [Lazy Studio](studio.md)。
