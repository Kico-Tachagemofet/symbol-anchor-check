# Symbol Anchor Check v4.2

面向 AI Agent 的塔罗属性与解读 Skill。它以 Golden Dawn / Book T 属性为底稿，先看整场怎样运作，再比较事件解释，最后把有依据的部分写成人能理解的答案。

本 Skill 用于已完成的 **5.1 Lite 完整符号包**及其追问：塔罗主牌与补牌、字卡、占星骰子、易经。它处理已有材料，不负责抽取。随附的 Phase 3 脚本也可以单独展开标准塔罗牌阵的属性；只有属性输出时，工作尚未到达解读终点。

## v4.2 改了什么

- **把已有称重流程完整随包提供。** v4.1 已有 Phase 3.5；v4.2 将 `symbol-field-weighing` 作为 bundled addon，明确每盘读取并执行：整场印象 → 问题与位格 → 当事人视角 → 重心 → 共振、张力与显著度。
- **加入按需使用的四元素框架。** 风的连接、火因水果、水影响土、三性质、冷热干湿，以及能量的缺乏／强化与六种组合，分别提供框架表和短例。实际判断写回共振或张力，无需为每个模型额外填一张表。
- **明确材料的参与范围。** 主牌参与整场汇总与跨位关系；补牌完整展开后澄清父位。输入兼容牌数组、`spread`、独立 `supplements` 与内联补牌；宫廷外层作用与内层场域分开，Aether 单列。
- **保留完整方法与输出契约。** 结构性候选分为排除／保留／未定，逆位保留原内容后辨认表达。属性表、称重、候选检验、跨符号核对、answer 与 open_threads 各有明确产物；可选口吻段落保留触发条件、来源与精度要求。
- **拆出 Miracle 扩展。** 原主脚本中的奇迹牌专用内容移入 `addons/miracle-anchor-addon/`，随附数据、展开逻辑及 Q1 增量／Q2 一致性检查。含奇迹牌时才执行 Phase 4.5；标准 78 张独立可用。
- **区分原典与项目应用。** 四元素与 Book T 的文献出处、塔罗应用和项目自定对应见 [SOURCES.md](SOURCES.md)。

公开版本的具体变化见 [CHANGELOG.md](CHANGELOG.md)。

## 工作流

| 阶段 | 执行者 | 产物 |
|---|---|---|
| Phase 3 属性展开 | Python 脚本 | 逐牌五层属性、原始对应、主补归属与主牌汇总 |
| Phase 3.5 场域称重 | LLM / Agent 读取 addon | 整场、重心、共振、张力、语言边界与暂定显著度 |
| Phase 4 Via Negativa | LLM / Agent | 有来源的候选检验、纯属性场描述、跨符号核对 |
| Phase 4.5（含 Miracle） | LLM / Agent 读取 addon | 逐张 Q1 增量与 Q2 一致性，决定贡献的去向 |
| answer 与 R1/R2 | LLM / Agent | 回答原问的自然段、具体未决点与表达检查 |
| 口吻段落（可选） | LLM / Agent | 对最终 answer 的第一人称语气转换，保留原有确定程度 |

**脚本只产 Phase 3。** Agent 还需要真正读取 [SKILL.md](SKILL.md)，执行 Phase 3.5、Phase 4，以及适用时的 Phase 4.5。脚本生成的 `compound_image` 是属性文字，不是实际牌图。

口吻段落按用户要求、符号解读中的明确同意，或亲密／强烈态度／关怀型语境选用；纯技术查询直接呈现解读。它在 answer 完成后生成，呈现时可放在技术解读前。完整条件见 [口吻段落说明](references/voice-paragraph.md)。

## 安装与使用

需要 **Python 3.10+**，脚本只使用标准库；完整解读还需要能够读取文件并执行 Skill 的 AI Agent。

下载或克隆整个仓库，保留 `data/`、`addons/` 与 `references/` 的相对位置。可以把完整目录作为一个 `symbol-anchor-check` Skill 安装，或让 Agent 从该目录的 `SKILL.md` 开始读取。

```text
symbol-anchor-check/
├── SKILL.md
├── phase3_unfold.py
├── references/                  # 输入、图像与可选口吻
├── data/
│   ├── tarot/                   # 标准 78 张：atu / pips / courts
│   └── yijing/                  # 易经参考数据
└── addons/
    ├── symbol-field-weighing/   # 每盘使用的场域称重及元素方法
    └── miracle-anchor-addon/   # Miracle 数据、展开与条件质检
```

`data/tarot/` 自含 22 张大阿卡纳、40 张数字牌和 16 张宫廷牌的属性条目。标准 78 张无需 Miracle 数据或外部资料目录。

下面只演示 Phase 3 的输入结构；完整 Skill 仍需原问题、位格和原始符号包：

```json
{
  "spread": [
    {"position": "Pos 2", "card_name": "Knight of Pentacles", "reversed": false},
    {"position": "Pos 4", "card_name": "Ace of Cups", "reversed": true}
  ],
  "supplements": [
    {"for_position": "Pos 4", "card_name": "Eight of Swords", "reversed": false}
  ]
}
```

保存为 `input.json`，在仓库目录运行：

```bash
python phase3_unfold.py input.json
```

输出 JSON 的 `per_card` 保留逐牌属性，`spread_synthesis` 给出主牌汇总与参与口径。将该输出连同原问和原包交给 Agent，要求它继续读取 Skill 并完成后续流程。更多输入形式与证据规则见 [输入与证据接口](references/input-and-evidence.md)。

可选环境变量：

| 变量 | 覆盖内容 |
|---|---|
| `SYMBOL_ANCHOR_DATA` | 含 `atu.json`、`pips.json`、`courts.json` 的目录；默认是仓库的 `data/tarot/` |
| `MIRACLE_ADDON_DIR` | 含 `miracle_unfold.py` 与 `miracle.json` 的扩展目录；默认使用随包 addon |

## 验证范围

本版通过 28 项程序检查，覆盖输入兼容、主补归属，以及以下独立运行场景：标准 78 张 × 正逆位在不带 Miracle 模块的目录中展开；14 张 Miracle × 正逆位使用 bundled addon 展开；混合包的 Aether、宫廷质量与统计范围；缺少 Miracle 模块时，对应输入明确失败且不输出部分结果。JSON 文件与标准输入两种入口均已覆盖。

这些检查验证程序行为与数据接口。LLM 的整场判断、候选推导和最终解释仍需要实际执行 Skill，并接受使用者校准。

## 适用范围与来源

可与 [Spirit Communication System v5.1 Lite](https://github.com/Kico-Tachagemofet/spirit-communication-system-lite) 配合：Lite 提供原始符号，本 Skill 完成属性展开后的整场分析与收束。完整包中的易经、骰子和字卡参与跨符号核对；独立易经或其他单独符号问题使用相应的专门方法。

Book T 数据来源沿用 **Israel Regardie, *The Golden Dawn*（Llewellyn 第 6 版），Book T 章节**。五层展开、场域称重、候选检验与元素在具体情境中的应用属于项目方法；Miracle 的源质、行星与星座主锚是项目自定对应。原著与应用的区别见 [SOURCES.md](SOURCES.md)。

本项目用于符号分析与实验性 Agent 工作流，不提供现实决策担保，也不替代医疗、法律、财务或心理咨询建议。

## License

MIT。第三方原著、出版文本与原牌组素材的权利说明见 [SOURCES.md](SOURCES.md)。
