# 许可与来源

## 本项目原创内容

本项目自行编写的代码、说明与原有原创 SVG 插画遵循 [MIT License](licenses/MIT.txt)。当前绘图工具使用原生 Canvas 2D，未包含参考项目的笔刷、套色实现或示例画面。

## 默认旁白参考

assets/voice/reference.wav 是用户选定的「沉稳男声·紧凑重音版」，由 Qwen3-TTS CustomVoice 的 Ryan 预设生成，未使用真人参考录音，也未做变速、降调或音色后处理。文本、模型修订、参数和文件校验值见 [声线记录](../assets/voice/profile.json)。模型及其输出的适用条款按模型来源处理，本项目代码许可不替代外部模型条款。

## 字体与地理数据

以下字体保留原许可：

- [Noto Serif SC](../assets/packaging/fonts/notoserifsc-OFL.txt)
- [Noto Sans SC](../assets/packaging/fonts/notosanssc-OFL.txt)
- [Barlow Condensed](../assets/packaging/fonts/barlow-OFL.txt)

地图几何来自公共领域的 Natural Earth，记录见 [地理数据来源](../assets/packaging/src/maps/source.json)。历史名称、时期、疆界和路径仍需按具体内容核对。

## 实拍素材

Skill 不包含旧版组件截图或第三方影视片段。实际制作应提供适合本次用途的素材，参见 [素材选择](assets.md) 和 [示例素材槽位](../assets/packaging/demo-media/README.md)。

## 外部运行依赖

运行库、浏览器和模型通过环境准备在使用时安装，继续适用各自许可与条款。它们没有作为运行环境直接放入 Skill 源码目录。

## 临摹研究图稿

reference-portrait.svg、reference-balance.svg、reference-writing.svg 为用户明确要求的视觉临摹研究，参考 [BUCK / Notion — Think it. Make it.](https://buck.co/work/notion-think-it-make-it) 的人物、构图与图形语言。它们由本地矢量路径重新绘制，保留分层便于改稿；不将第三方角色与构图宣称为本项目原创，也不以本项目代码许可替代原作品权利。

lit-title 与 medallion-labels 的文字材质对照用户指定视频中的宋体、字面受光与投影。当前以现有可用的 Noto Serif SC 调整字重与材质实现；未确认原视频的确切字体名称，不宣称字库完全相同。
