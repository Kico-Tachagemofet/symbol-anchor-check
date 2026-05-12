# Symbol Anchor Check v4 — Deterministic Property Anchoring + Via Negativa

一套用于 tarot 解读的**属性一致性核查器**。不查"牌意"，只查属性。

## 核心理念

**事件才是模型，牌是事件的投影。**

传统的 tarot 解读倾向于"检索牌意"——看到权杖五就想到"冲突"，看到圣杯二就想到"恋爱"。这个 skill 拒绝这种工作方式。

v4.0 的做法分两阶段：

**Phase 3 — 确定性属性展开**：`phase3_unfold.py` 脚本（不走 LLM）将每张牌展开为 Book T 五层属性（元素/源质/旬星/尊贵/位置）+ compound_image + spread_synthesis。

**Phase 4 — Via Negativa 收束**：LLM 在 Phase 3 的属性材料上做五步收束——(1) 排除不支持的候选，引原文为证、(2) narrowed_field 纯属性语言、(3) 跨符号校验（易经/骰子/字卡）、(4) answer 说场景不说牌、(5) open_threads 保留未覆盖项。

后检保留 R1（指涉对象规则）+ R2（隐式跨位）散文规则。

## 与 v3.x 的关键区别

v3.x 是散文风格规则盖在松地基上。v4.0 先跑确定性属性层（Phase 3），再把 LLM 解读约束在属性材料上做 via negativa 收束（Phase 4）。散文规则降级为后检。

## 方法论

### 五层属性分层

每张牌有五层可验证的硬属性：

| 层 | 数字牌 | 大阿卡纳 | 宫廷牌 |
|---|--------|---------|--------|
| 1 | 元素 [hot/dry 等] | 归属 [planet/sign/element] | 复合元素 [Fire of Water 等] |
| 2 | 源质×世界 [Geburah of Assiah] | 路径 [Chokmah→Tiphareth] | 黄道跨度 |
| 3 | 旬星 [Moon in Taurus] | — | — |
| 4 | 尊贵 [exaltation/detriment 等] | — | — |
| 5 | 牌位 | 牌位 | 牌位 |

### 从不是到是（Via Negativa）

解读不靠"这张牌意味着什么"，而是靠排除：属性层不支持的解读方向先被排除，剩下的才能进入下一步。排出必须引用 Phase 3 输出的精确子串作为证据。

### narrowed_field — 纯属性语言

排除后用纯属性语言描述收窄后的场域。禁止出现牌名、行星名、星座名、源质名、路径名——只说压力、方向、运动、接受性、边界。

## 数据层

`data/tarot/` 下三个 JSON 文件，包含全部 78 张牌的 Book T 属性：

| 文件 | 内容 |
|------|------|
| `atu.json` | 22 张大阿卡纳：归属类型、路径、元素、品质、Book T 标题 |
| `pips.json` | 40 张数字牌：源质、世界、旬星（行星×星座）、尊贵状态 |
| `courts.json` | 16 张宫廷牌：复合元素、黄道跨度、管辖旬星 |

数据源：Israel Regardie, *The Golden Dawn* (Llewellyn 6th ed.), Book T 章节。78/78 条目完整。

## 使用方式

任何 tarot spread 的结果，只要牌名能映射到 Book T 体系（标准 RWS 中文/英文牌名），都可以跑本检查。

1. 拿到 tarot spread 原始抽取结果
2. 用户追问或要求解读
3. Agent 加载本 skill，先跑 Phase 3 属性展开，再执行 Phase 4 via negativa
4. 输出通过检查的解读

## 文件结构

```
symbol-anchor-check/
├── README.md          # 本文件
├── SKILL.md           # 主 skill 文件（v4.0）
└── data/
    └── tarot/
        ├── atu.json   # 大阿卡纳
        ├── pips.json  # 数字牌
        └── courts.json # 宫廷牌
```

## License

MIT
