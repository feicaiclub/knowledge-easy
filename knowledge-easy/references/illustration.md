# 绘图与图稿接口

造型、材料、创作自由与效果判断统一见 [SKILL.md](../SKILL.md)。本页列出可调用源码及其真实能力。

## 默认插画预设

用户本轮指定参考后的可编辑图稿：

| 图稿 | 可编辑图层 | 来源状态 |
| --- | --- | --- |
| [reference-portrait.svg](../assets/packaging/illustrations/reference-portrait.svg) | person、thought、connection | 侧面思考人物与原色图形临摹 |
| [reference-balance.svg](../assets/packaging/illustrations/reference-balance.svg) | person、question、answer、balance | 跷板人物与问答构图临摹 |
| [reference-writing.svg](../assets/packaging/illustrations/reference-writing.svg) | paper、idea、hand、window | 书写动作与纸面构图临摹 |

它们已接入当前示例，验收参照分别登记为 art-reference-portrait、art-reference-balance、art-reference-writing。直接复用这些图稿时，源码会按图稿文件选择对应参照；新绘图应明确提供 design_reference。原有三份原创 SVG 仍保留；临摹图稿不宣称原创，来源见 [sources.md](sources.md)。

## 保留的材料与结构研究

| 语言 | 配方 | SVG 源码及可用图层 |
| --- | --- | --- |
| 结构线描 | [etch.md](styles/etch.md) | [etch.svg](../assets/packaging/illustrations/etch.svg)：seed、pod、stem、interior；h 是填充图案定义 |
| 平涂叠色 | [print.md](styles/print.md) | [print.svg](../assets/packaging/illustrations/print.svg)：canopy、shade |
| 淡彩自然 | [wash.md](styles/wash.md) | [wash.svg](../assets/packaging/illustrations/wash.svg)：land、water、river、tributary、bridge |

这些 SVG 是绘画源码，可复制到项目后保留路径和图层继续改造。它们不是已验收的动画，也不指定新片必须出现果荚、门廊或河流。示例配置见 [examples.json](../assets/packaging/src/artwork/examples.json)，先有本片方案再读取相关示例。

这些原有图稿及 examples/ 中的 JavaScript 用于研究构造、笔触和时间控制；默认人物风格使用上面的已选参照，不以技术示例代替最终画面。

## SVG 接入

场景使用 component: "artwork"；data.source 为项目内 .svg 路径。调用器会给图层 ID 加实例前缀，并更新路径、渐变和填充引用。

```json
{
  "id":"inside","start":0,"duration":8,
  "purpose":"完整对象先建立，再看内部结构。",
  "component":"artwork",
  "data":{
    "style":"etch","source":"assets/artwork/subject.svg",
    "description":"本片重新设计的主体与内部关系",
    "motion":[{"target":"interior","type":"fade","at":2.4,"duration":0.7}]
  }
}
```

source 中需真实存在 interior 图层。motion 的 type 为 fade、draw 或 move；move 的 from/to 支持 x、y、scale、rotation、opacity。draw 仅适用于已有描边且能计算长度的路径，不可拿填色图层直接描线。cues 中同名目标可覆盖 at；一个图层只声明一条 motion，复杂多阶段运动用项目绘图或扩展渲染。

当前 SVG 接入保留静态矢量结构，拒绝 script、外部 image、foreignObject 和 SVG 自带的时间动画。剪切、渐变与结构图层保留；运动由项目时间线控制。源 viewBox 与图层实际位置需自行检查。

## JavaScript 接入

data.source 也可指向项目的 assets/artwork/scene.js。该文件是绘图函数体，收到 ctx、t、data、art；t 是组件局部秒数，data 来自 configuration，另注入 duration 和局部 beats。

绘图每帧重置，使用 t 推导姿态，不累积上一帧位置。随机变化使用固定种子的 art.rng，不使用墙上时钟或网络请求。接口当前使用完整 1920×1080 画布与不透明底面，多层组合时注意遮挡。

| 方法 | 参数与作用 | 能力边界 |
| --- | --- | --- |
| path | path(svgPath, fill, stroke, width) | 调用者绘制轮廓，不自动生成造型 |
| line / quadratic | line(points, width, ink, progress)；quadratic(a,control,b,steps) | progress 按采样点展开；匀速需要合理采样 |
| stroke | stroke(points,width,ink,{progress,opacity,profile,seed}) | wash 模式按路径法线形成压力轮廓；其他模式使用等宽线 |
| hatch | hatch(shape,[x,y,w,h],{spacing,bend,width,opacity,ink}) | 在给定形状中裁剪规则曲线；不会自动识别曲面、遮挡或光线 |
| over / plate | over(fn)；plate({x,y,opacity},fn) | multiply 合成；错位由调用者控制，没有自动印刷模拟 |
| camera / pose | camera({x,y,zoom,angle},fn)；pose(keys,t) | 相机和姿态插值；angle 使用弧度，keys 需按 t 排序且结构一致 |
| person / hand / eye | 可调比例、方向、姿态的构造起点 | 不是通用角色或自动表演系统 |
| leaf / foliage / branch | 叶形、叶簇和分枝起点 | foliage 的种子分布不自动匹配枝条，需自行设计支撑关系 |

全部实现位于 [runtime.js](../assets/packaging/src/artwork/runtime.js)。可以直接使用 Canvas 2D 绘制新对象，不受这些辅助方法限制。stroke 在 wash 模式可选 even、trunk、tip、leaf 等轮廓；透明层次与路径几何仍由画面设计决定。

## 色板、文字和来源

data.style 使用 etch / print / wash，或含 engine 与 palette 的对象。palette 支持 paper、ink、accent、secondary，print 可另给 inks。当前引擎使用 Canvas 2D，没有外部笔刷或套色依赖。

文字可留在 data.labels 中：id、text、x、y、width、size、at，可选 end、font、weight、align、color。x/y 等按工作坐标填写；标签与字幕分开，具体边界见 [artwork.py](../assets/packaging/src/artwork.py)。labels 的默认淡入仅是接口起点，需要不同文字动作时使用扩展实现。

composition.py 读取真实源码，记录 drawing_source 和校验值。技术接入成功后，仍按 SKILL.md 检查实际形体、材料、动作和整片表现。
