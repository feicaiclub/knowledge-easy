# 项目设计记录与时间接口

完整导演方法、设计标准与验收顺序在 [SKILL.md](../SKILL.md)。这里说明项目决定如何进入实际输入文件，不维护另一套流程。

## 设计记录

沿用项目已有笔记；没有时可写 research/design.md。记录观众的核心疑问与理解变化、本片呈现方式及取舍、参考品质、视觉语言和镜头意图。记录是制作依据，不是新的固定片型。

镜头表可以使用以下列：

| 语句或论证位置 | 主体与景别 | 动作前 → 变化 → 结果 | 实现与材料 | 时间依据 |
| --- | --- | --- | --- | --- |
| 当前要解释的因果 | 观众先看哪里、需要多近 | 可见变化与结论怎样成立 | 来源区间、组件或原创文件 | 实际口播、动作完成和阅读需要 |

画面参照写清比较的品质。进入 film.json 的 design_reference 应使用已登记组件 ID、art-etch / art-print / art-wash，或包含 src 与 reason 的项目图片对象；不要把 Markdown 笔记路径放进图片字段。项目记下的风险在实际制作时进入相应镜头的审查观察。

<a id="one-event-clock"></a>
## 同一个语意事件

film.json 的 beats 是全片绝对秒数，ID 唯一：

```json
{"beats":[{"id":"finding","time":6.2,"purpose":"两个对象形成可见联系"}]}
```

scene.start 是全片时间；components[].start 相对场景；cues 和绘图 t 相对组件。脚本把组件覆盖区间中的事件转换为 data.beats：事件局部时间 = beats.time − scene.start − component.start。

例如场景从 4 秒开始，组件晚 0.5 秒进入，则 finding 在绘图中的时间为 1.7 秒。图形围绕该值设计动作；音效在 music-plan.json 中用 event: "finding"、offset: 0 对齐。

```json
{"src":"assets/audio/contact.wav","role":"sfx","event":"finding","offset":0,"duration":0.35,"gain_db":-14,"fade_in":0.01,"fade_out":0.08}
```

同一声音条目使用 event 或 start 其中一个；offset 可表达提前进入或延后，但最终时间不能早于全片起点。调整事件后重新 build 与 mix，不能只改画面。事件只负责共同落点，不强制镜头服从音乐节拍。

实际解析位于 [event_clock.py](../scripts/event_clock.py)、[composition.py](../scripts/composition.py) 和 [mix.py](../scripts/mix.py)。
