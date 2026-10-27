# 组件输入与实际调用

设计选择、复用质量和验收要求在 [SKILL.md](../SKILL.md)。本页对应当前源码接口。

## 找到真实实现

| 需要 | 先读取的接口与实现 |
| --- | --- |
| 12 类基础布局 | [输入示例](../assets/packaging/src/base-examples.json)、[base_catalog.py](../assets/packaging/src/base_catalog.py)、[pack.css](../assets/packaging/src/pack.css) |
| 扩展组件 | [renderer-contract.json](../assets/packaging/src/renderer-contract.json) 的 public_variants、[editorial.py](../assets/packaging/src/editorial.py)、[editorial.css](../assets/packaging/src/editorial.css) |
| SVG / 自定义绘图 | [绘图接口](illustration.md)、[artwork.py](../assets/packaging/src/artwork.py)、[runtime.js](../assets/packaging/src/artwork/runtime.js) |
| 新的布局与渲染 | film.extensions，加载方式见 [composition.py](../scripts/composition.py) |

基础组件 ID 为 hero、compare、chapter、evidence、relation、feedback、quantity、timeline、map-focus、map-route、map-period、context。扩展包括 evidence-sheet、relation-bridge、feedback-loop、context-reveal 等，名称与实际字段以源码为准。示例中的素材路径、文字和场景顺序须换成本片需要的内容。

## 文字与人物的新增版式

实现见 [type_designs.py](../assets/packaging/src/type_designs.py) 与 [type.css](../assets/packaging/src/type.css)。

- lit-title：image、left、right，可选 caption；每个字的字面、受光边缘、暗边和细颗粒分层绘制。
- medallion-labels：image、2–4 项 labels，可选 title、caption；薄金属边、半透明圆章与受光文字。
- editorial-portrait：image、title，可选 caption、accent；纸面上的人物近景与独立文字区。

图像支持 image.fit（cover / contain）和 image.focus。纸面人物预设以完整图像靠下对齐，避免图形被裁掉或半身悬空。媒体的淡入、位移和缩放作用于外层容器；圆章背景直接使用共享 backdrop，避免前景动效干扰媒体处理层。

示例以现有 Noto Serif SC 实现受光宋体效果，不将其标为参考视频的确切原字体。参数仍由项目内容提供，使用方式与其他扩展组件一致。

## 场景输入

下面是 compare 的有效字段形状，素材文件需由项目提供，示例时长需按实际口播调整：

```json
{
  "id":"distinction","start":0,"duration":8,
  "purpose":"在共同尺度下看清两种判断的差别。",
  "background":{"src":"assets/media/environment.mp4","treatment":"cinematic"},
  "component":"compare",
  "data":{
    "text":{"a-label":"可见行为","b-label":"真实动机","ta":"观察","tb":"推断","q":"已有证据能支持哪一步？","ghost":"辨"},
    "media":{"a-film":{"src":"assets/media/observation.mp4","type":"video"},"b-film":{"src":"assets/media/evidence.mp4","type":"video"}}
  },
  "cues":{}
}
```

`data.text`、`data.media` 的槽位随基础组件变化；扩展组件使用各自结构，不能把同一组字段套给全部类型。`cues` 的键也来自该组件实际调用的 cue 名称。`data.appearance` 可覆盖 foreground、accent、secondary、muted；它只改颜色，不重新设计版式。

`background` 默认使用 cinematic 虚化动态素材，由 [backdrop.py](../assets/packaging/src/backdrop.py) 提供明暗、饱和度、Blur 和遮罩参数。正式 build 与预览调用同一个 render_background；效果通过 HyperFrames 原生 data-color-grading 执行。仅背景接受该处理，前景组件与素材保持清晰。

背景可通过 grading/shade 覆盖具体参数；需要清晰全景时使用 treatment: "raw" 或 footage。纸面、纯色与原创画布用于明确选定的相应设计，不再作为影视包装的默认替代。预设里的素材路径需要按新内容更换。

## 自由组合与时间

一个 scene 使用 component 或非空 components 数组，二者互斥。components 中每层含唯一 id、component、data，以及可选的 purpose、cues、start、duration、frame、design_reference。

- start 相对场景，duration 不超出场景；cues 相对该层。
- frame 为 [x,y,width,height]，以 1920×1080 为工作坐标，按等比例居中放置。它不会重新排版，不能用缩小整张设计解决所有组合需求。
- 数组后面的层在上面；不透明的满幅画布会遮住先前图层。确认绘画底面、前景、文字和字幕的遮挡关系后再组合。
- 阅读区与字幕区由实际布局共同判断，不能只靠 frame 没越界来判定可读。

## 项目扩展

在 film.extensions 中声明扩展：

```json
{"id":"decision-space","source":"components/decision_space.py","design_reference":{"src":"assets/references/composition.png","reason":"比较主体尺度、轮廓层次和连接线空间。"},"reason":"本段需要连续的空间变形，现有布局不适用。"}
```

项目 Python 文件提供 `render(kit, prefix, duration, data, cues, locale)`，返回 html、js、reading_order，可另返回 layout。reading_order 每项使用唯一元素 id、role、enter_at、settle_at、depends_on。所有元素 ID 使用 prefix，时间由可寻址的局部时间线控制。扩展可以组合调用 kit.render，也可以实现新的绘画；共享库函数不作内存替换。

基础调用入口为 `render(component, instance_id, duration, data, cues, locale)`。返回记录包括 component、parent、version、implementation、design_reference。项目扩展由 composition.py 补充这些来源字段。

## 设计参照与来源记录

参照可以是组件 ID、登记的插画 ID，或项目图片的 src 与 reason。当前人物预设使用 art-reference-portrait、art-reference-balance、art-reference-writing；art-etch / art-print / art-wash 保留给对应的材料研究。读取优先级为图层 → 场景 → 全片 → 渲染器返回的默认参照。更换参照需要能解释新的比较目标，不能只为避开已有差距。

research/component-usage.json 中 provenance 记录库快照来源；原创绘图另有 drawing_source/drawing_sha256，扩展记录 source/sha256/reason。reading_order 是实际渲染返回值。source_signature 把相关源码和引用文件关联到导出。

<a id="visual-review"></a>
## 与验收相连

review-visuals 为实际导出准备参照、抽帧与 motion_file；完整 sequence 用于检查整片。内置组件没有配套截图时，按当前真实实现和本片设计要求判断，不读取旧预览图代替。

审查使用 hierarchy、composition、material、motion、explanation，以及整片 direction、rhythm、sound。具体观察方法与返修原则统一见 SKILL.md。accept-visuals 只核对记录与证据，不具备自动审美评分能力。
