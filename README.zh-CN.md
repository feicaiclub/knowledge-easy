<div align="center">

[English](README.md) | **简体中文**

# Knowledge Easy

**把道理拍明白。**

[![License: MIT](https://img.shields.io/badge/License-MIT-d8b676)](LICENSE)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill-151c1c)](https://learn.chatgpt.com/docs/build-skills)
[![中英文视频](https://img.shields.io/badge/视频-中文%20%2B%20English-8db7b2)](references/language.md)
[![废才俱乐部](https://img.shields.io/badge/作者-废才俱乐部-2B4CF5)](https://www.feicaiclub.cn)

交给 Codex 一个问题，Knowledge Easy负责调研、写稿、找素材、配音、剪辑和视觉讲解，<br>
把成片放进审片室，等你逐帧提意见。

<img src="assets/showcase/history-question.jpg" alt="荀彧成片中的一帧：辅曹与扶汉，还能是同一件事吗？" width="100%" />

<sub>这里展示的是我们已经做出的成片画面，以及真实操作中的审片界面。</sub>

[安装](#在-codex-里安装) · [成片效果](#先看已经做出的片子) · [视觉包装](#一套视觉语言讲清不同的内容) · [Lazy Studio](#lazy-studio把意见落到具体一帧) · [关于作者](#关于作者)

</div>

## 在 Codex 里安装

**复制下面这段，粘进 Codex 聊天框发送：**

```text
$skill-installer 从 https://github.com/feicaiclub/knowledge-easy 安装仓库根目录（path: .）的 Skill，安装名称为 knowledge-easy。
```

下一轮对话即可使用；如果没有出现，重启 Codex 后再试。这里使用 Codex 自带的 [Skill Installer](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use)。

然后直接告诉它想做什么：

```text
$knowledge-easy 做一条讲“为什么人会合理化自己已经做出的选择”的中文知识短片。用一个具体故事讲清楚，有转折、有反思。沿用系列声线和视觉包装，让素材、音乐和图解跟着内容推进。完成后给我成片，并打开 Lazy Studio 审片。
```

可以让它做完整成片，也可以只要选题、打磨稿子或修改已有视频。依赖在**实际使用时**检查、按需安装，放在 Skill 外。遇到安装问题，Codex 先说明原因并排查，再寻找兼容方案，讲清对效果的影响。

## 先看已经做出的片子

### 历史篇：从人物的选择，走进他的挣扎

荀彧这一篇，讲的是他一路辅佐的人，与他始终想维护的汉室。真实影视镜头、地图、材料和反思，跟着故事依次出现。

<img src="assets/showcase/history-portrait.jpg" alt="荀彧历史短片的实际成片画面" width="100%" />

<table>
<tr><td width="50%"><img src="assets/showcase/history-identity.jpg" alt="先交代人物与位置" width="100%" /><br><b>先交代人物与位置</b></td><td width="50%"><img src="assets/showcase/history-map.jpg" alt="把一次战略选择放到地图上" width="100%" /><br><b>把一次战略选择放到地图上</b></td></tr>
<tr><td width="50%"><img src="assets/showcase/history-context.jpg" alt="在同一张地图上转移叙述重点" width="100%" /><br><b>在同一张地图上转移叙述重点</b></td><td width="50%"><img src="assets/showcase/history-evidence.jpg" alt="让提议与后果同时看得见" width="100%" /><br><b>让提议与后果同时看得见</b></td></tr>
<tr><td width="50%"><img src="assets/showcase/history-relationships.jpg" alt="区分两套权力关系" width="100%" /><br><b>区分两套权力关系</b></td><td width="50%"><img src="assets/showcase/history-roster.jpg" alt="讲到举荐人才时，再让名字出现" width="100%" /><br><b>讲到举荐人才时，再让名字出现</b></td></tr>
</table>

### 心理学篇：从一张电影票，讲到下一次选择

沉没成本这一篇，从一个日常情境展开，延伸到工作、关系和接下来仍能支配的时间。实拍画面让人代入，图解把其中的思路讲清。

<table>
<tr><td width="50%"><img src="assets/showcase/psychology-cost.jpg" alt="回不来的钱，还在付出的时间" width="100%" /><br><b>回不来的钱，还在付出的时间</b></td><td width="50%"><img src="assets/showcase/psychology-loop.jpg" alt="把越陷越深的循环讲清楚" width="100%" /><br><b>把越陷越深的循环讲清楚</b></td></tr>
<tr><td width="50%"><img src="assets/showcase/psychology-future.jpg" alt="把判断重新放回未来" width="100%" /><br><b>把判断重新放回未来</b></td><td width="50%"><img src="assets/showcase/psychology-street.jpg" alt="解释之后，让画面回到生活" width="100%" /><br><b>解释之后，让画面回到生活</b></td></tr>
</table>

以上均为已完成剪辑中的静态截图。底层影视、实拍素材保留原有权利，详见[第三方许可说明](THIRD_PARTY_NOTICES.md)。

## 一套视觉语言，讲清不同的内容

包内有 **21 种可编辑设计、42 张中英文静态预览图**。字体、卡片、关系图、时间线、证据版式和地图来自同一套组件。内容、素材、坐标和出场时机，按每期讲述调整。

<table>
<tr><td width="50%"><img src="assets/packaging/previews/en-US/quote-reveal.jpg" alt="先铺垫，再亮出关键一句" width="100%" /><br><b>先铺垫，再亮出关键一句</b></td><td width="50%"><img src="assets/packaging/previews/zh-CN/map-route.jpg" alt="路线与地理关系" width="100%" /><br><b>路线与地理关系</b></td></tr>
<tr><td width="50%"><img src="assets/packaging/previews/en-US/evidence-sheet.jpg" alt="材料与解释，各有位置" width="100%" /><br><b>材料与解释，各有位置</b></td><td width="50%"><img src="assets/packaging/previews/zh-CN/compare.jpg" alt="把两个观点放在同一尺度上" width="100%" /><br><b>把两个观点放在同一尺度上</b></td></tr>
<tr><td width="50%"><img src="assets/packaging/previews/zh-CN/context.jpg" alt="把细节放回上下文" width="100%" /><br><b>把细节放回上下文</b></td><td width="50%"><img src="assets/packaging/previews/en-US/milestone-pair.jpg" alt="用统一尺度比较两个时刻" width="100%" /><br><b>用统一尺度比较两个时刻</b></td></tr>
</table>

- 安装后在本地打开[视觉包装手册](references/visual-handbook.html)，对照静态图、排版规范和动效顺序。
- 使用[组件源码](assets/packaging/src/README.md)、[调用说明](references/packaging.md)和[动效约定](assets/packaging/src/motion-contract.json)搭建或扩展画面。
- 每次制作仍要检查真实动效：静态图提供构图参考，入场、停留和退场由源码与时间参数决定。

需要解释时再用图解，让素材和旁白承担其余的叙述。

## Lazy Studio：把意见落到具体一帧

### 标记这一帧，直接写意见

暂停，按 **M**，输入意见，再按 **Enter**。版本、帧号、评论和截图保存在一起。

<img src="assets/showcase/studio-mark.png" alt="实际操作 Lazy Studio：标记地图镜头并输入逐帧评论" width="100%" />

### 反馈和自审记录，就放在画面旁边

<table>
<tr><td width="50%"><img src="assets/showcase/studio-feedback.png" alt="保存后的意见带着原始版本和精确帧号" width="100%" /><br><b>保存后的意见带着原始版本和精确帧号</b></td><td width="50%"><img src="assets/showcase/studio-review.png" alt="不用离开成片，就能查看项目审片记录" width="100%" /><br><b>不用离开成片，就能查看项目审片记录</b></td></tr>
</table>

### 两版放在一起，同一时刻看差别

<img src="assets/showcase/studio-compare.png" alt="Lazy Studio 在同一时间点并排显示中英文组件示例" width="100%" />

<sub>这里用中英文示例展示对比界面，不把它包装成一次不存在的修改前后对照。</sub>

### 想专心看画面，就切换专注预览

<img src="assets/showcase/studio-focus.png" alt="Lazy Studio 专注预览模式中的荀彧成片画面" width="100%" />

反馈写进视频项目的 `review/feedback.md`，并关联版本、帧号和截图。回到原来的 Codex 对话，说一句：**“我标记好了，去读反馈并修改。”** 当前通过本地文件对接，不会自动把反馈作为附件塞进聊天框。

以上截图来自独立展示项目中的真实操作，示例评论已经标明；本地原片和原有反馈记录都保留。

## 同一位讲述者，每一篇有不同的表达

默认使用已认可的 **Qwen3-TTS D 声线与 body-v1 后期**。声音身份保持稳定，情绪、重音、速度感和气口随内容变化。

[试听英文旁白样音](assets/voice/english-pilot.wav) · [中文声线参考](assets/voice/reference.wav) · [旁白说明](references/voice.md)

英文样音已经过用户试听认可。自动转写用来核对内容与时间，不能代替对口音和自然度的试听。

## 它负责哪些事

| 环节 | 做什么 |
| --- | --- |
| 调研与写稿 | 找依据、组织故事，让观众听完有更清楚的理解。 |
| 素材与分镜 | 让画面对应内容，安排镜头、音乐变化和图形出场。 |
| 旁白 | 使用固定参考，按完整语义长段生成，检查读音、停连与首尾。 |
| 剪辑与包装 | 调用共享组件源码，根据要解释的问题组织画面。 |
| 音乐与音效 | 多段音乐、重音、衔接与留白，保证旁白清楚。 |
| 自审与返修 | 检查成片、读取逐帧反馈，保留已认可的部分，再交新版。 |

前面已经做出的片子和反复修改的经验，沉淀成质量底线。选题依然决定故事、时长、节奏和创作方式。

## 里面有什么

```text
knowledge-easy/
├── SKILL.md                  唯一的 Skill，整体制作流程
├── references/               视觉手册与制作说明
├── scripts/                  依赖准备、配音、转写、剪辑与审片工具
├── assets/
│   ├── packaging/            包装源码、字体、地图、静态参考
│   ├── voice/                固定参考声线、样音、配置、读音词典
│   ├── lazy-studio/          审片界面
│   └── showcase/            成片截图与真实界面截图
└── package-manifest.json     文件完整性校验
```

只有一个 Skill。运行环境、模型权重、API Key、视频项目和演示视频都不打包。开源手册使用静态图，生产需要的动效保留在源码里。

## 依赖与实际边界

默认沿用已跑通的 **Qwen3-TTS / MLX Audio、MLX Whisper large-v3、HyperFrames、FFmpeg 和共享视觉组件**。具体版本与模型快照在 [runtime-lock.json](scripts/runtime-lock.json)。

原来的旁白和转写实测环境是 Apple Silicon Mac。其他机器可能需要兼容实现，由 Codex 在实际使用时排查适配。本地模型首次下载可能较大，生成速度取决于机器；可选的音乐和音效服务使用你自己的账号与额度。详见[依赖说明](references/runtime.md)。

需要重新渲染通用组件示例集时，用 `catalog --media-dir` 指定有权使用的素材。第三方原始素材不随仓库分发，见[演示素材说明](assets/packaging/demo-media/README.md)。


## 反馈、贡献与许可证

遇到问题可提 [issue](https://github.com/feicaiclub/knowledge-easy/issues)，写明系统、硬件、出错步骤和去除敏感信息后的报错。改视觉组件时，展示入场、阅读顺序、停留和退场，源码与手册一起更新。

提交前运行 `python3 scripts/validate_package.py --manifest` 和 `python3 scripts/validate_package.py --verify-manifest`。仓库 CI 只检查包文件和引用，不下载制作模型。

原创代码与文档采用 [MIT](LICENSE)。字体保留 SIL Open Font License，地图数据来自 Natural Earth。截图里的第三方画面不随 MIT 重新授权，详见[第三方许可说明](THIRD_PARTY_NOTICES.md)。

感谢 Qwen3-TTS、MLX Audio、MLX Whisper、HyperFrames、GSAP、FFmpeg 和 Pedalboard。Lazy Studio 沿用废才既有的审片工具和 UI kit。

## 关于作者

**废才** — 废才俱乐部主理人，AI Builder 与知识分享者，专注 AI Agent、编程和影视创作。工作流先在实际项目里跑通，再把可复用的部分整理开源。

- 著有《驱动 AI 提示词：指令入门与场景应用》（清华大学出版社）。
- 毒舌产品经理系列、Seedance 分镜师系列的开发者。
- 其他开源作品：[广告分镜师](https://github.com/feicaiclub/ad-storyboarder)、[previz](https://github.com/feicaiclub/previz)、[video-spec-builder](https://github.com/feicaiclub/video-spec-builder)、[DeepSeek Harness 白皮书](https://github.com/feicaiclub/deepseek-harness-whitepaper)。

| | |
|:---|:---|
| 🌐 官网 | [www.feicaiclub.cn](https://www.feicaiclub.cn) |
| 𝕏 Twitter | [@zhu185178](https://x.com/zhu185178) |
| 📺 B站 | [废才俱乐部Club](https://space.bilibili.com/3546566589679687) |
| ▶️ YouTube | [@feicaiclub](https://www.youtube.com/@feicaiclub) |
| 📕 小红书 | [废才俱乐部](https://www.xiaohongshu.com/user/profile/5c6ec0c20000000010032d24) |
| 🎵 抖音 | 搜「废才俱乐部」 |
| 💬 公众号 | 微信搜「废才俱乐部」 |

[![废才俱乐部 · AI Builder 实战社区](assets/readme/feicai-club.jpg)](https://www.feicaiclub.cn)
