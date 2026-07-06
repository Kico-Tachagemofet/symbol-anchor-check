---
name: symbol-anchor-check
description: "取象锚点检查 v4.1 — Phase 3 确定性属性层展开 + Phase 3.5 场域称重 + Phase 4 via negativa 收束。先跑 phase3_unfold.py 提取 Book T 属性层，再称整场重心/张力，最后用排出法收束到 narrowed field。易经/骰子/字卡在 Phase 4 的跨符号校验阶段整合。继承 v3.4 的 R1/R2 散文规则作为后检。"
tags: [divination, interpretation, quality-control, tarot, book-t, via-negativa, phase3, phase4, field-weighing]
---

# 取象锚点检查 v4.1

**核心理念变更**：v3.x 是散文风格规则盖在松地基上。v4.0 先跑确定性属性层（Phase 3），再把 LLM 解读约束在属性材料上做 via negativa 收束（Phase 4）。散文规则（R1/R2）作为 Phase 4 输出后的后检保留。

**v4.1**：在 Phase 3 与 Phase 4 之间加入 **Phase 3.5 场域称重（Field-Weighing）**——先称整场的重心/共振/张力/显著度/语言边界，再让 Phase 4 的排出优先级与 answer 收束都落在这一步之后、受它约束。该步为实验性方法，其中「显著度」子步最依赖判断，建议保持人工在环校准（称重结果显式出现在输出里，供使用者当场校）。

## 触发条件

用户对已输出的 5.1 Lite 抽取结果进行追问/要求解读时触发。

## 流程总览

```
spirit_draw_v2 输出 (6 牌 + 补牌 + 骰子 + 易经 + 字卡)
        │
        ▼
Phase 3 ── python3 phase3_unfold.py  ← 确定性，不走 LLM
        │  每张塔罗牌 → 5 层属性展开 + compound_image
        │  奇迹牌 → 核心牌意 + 转化机制
        │  spread_synthesis → 质量轴 + 元素平衡 + 源质模式
        │
        ▼
Phase 3.5 ─ 场域称重 (Field-Weighing)  ← v4.1，每盘默认跑
        │  先称整场：重心 / 共振组 / 张力·假面 / 显著度 / 语言边界
        │  只数客观共现；输出约束 Phase 4 排出优先级 + answer salience + 措辞边界
        │
        ▼
Phase 4 ── LLM via negativa 收束（落在 Phase 3.5 之后、受其约束）
        │  1. 排出：排除不支持的候选，引 Phase 3 原文为证
        │  2. narrowed_field：纯属性语言（不提牌名/行星/源质/星座）
        │  3. 跨符号校验：易经 + 骰子 + 字卡
        │  4. answer：说场景不说牌
        │  5. open_threads：诚实保留未覆盖项
        │
        ▼
后检 ─── R1/R2 散文规则（继承 v3.4）
```

---

## Phase 3 执行

### 命令

```bash
python3 phase3_unfold.py <input.json>
```

### 输入格式

从 spirit_draw_v2.py 的输出构造。将牌名（RWS 格式）和位置填入：

```json
{
  "spread": [
    {"position": "Pos 1 [我的状态]", "card_name": "King of Miracles", "reversed": false},
    {"position": "Pos 2 [他的状态]", "card_name": "King of Pentacles", "reversed": true},
    ...
    {"position": "Supp: Pos 1", "card_name": "Devil", "reversed": true, "supplement": true}
  ]
}
```

### 输出结构

每张标准牌：
```json
{
  "card_name": "Death",
  "card_id": "atu_13_death",
  "card_class": "major_arcana",
  "position": "Pos 6 [他想说的]",
  "reversed": true,
  "property_unfolding": {
    "element_layer": "The sign Scorpio supplies cold+moist as the primary posture...",
    "sephira_layer": "Path 24 links Tiphareth to Netzach...",
    "decan_layer": "No decan is assigned to this trump...",
    "dignity_layer": "...The card is reversed...",
    "position_layer": "Landing on 'Pos 6 [他想说的]'..."
  },
  "compound_image": "The position 'Pos 6 [他想说的]' is touched by the sign Scorpio..."
}
```

每张奇迹牌：
```json
{
  "card_name": "King of Miracles",
  "card_class": "miracle",
  "property_unfolding": {
    "miracle_core": "空性再生 — 斩常见与断见的中道...",
    "miracle_mechanism": "超越自我有限性...",
    "miracle_direction": "正位: 放下对「我」的执着...",
    "position_layer": "..."
  },
  "compound_image": "..."
}
```

---

## Phase 3.5 — 场域称重 (Field-Weighing)（v4.1，默认步）

Phase 3 出完属性层后、进 Phase 4 排出**之前**，把整副牌当**一个场**先称一遍：重心 / 共振组 / 张力·假面 / 显著度 / 语言边界，称完再落单张。无须条件——**每盘都跑**。

### 它解决什么

Phase 3 → Phase 4 是**自下而上**的：逐张展属性、逐位排除。后果是**张力只能当逐位分析的副产品**，重心常摆错——承重的东西被丢进 open_threads、被好看的牌骗、salience 摊平。人类占卜师反过来：**先看整场往哪沉、哪里是假面，再读单张**。本步把那一下补进流程。

**为什么放在 Phase 3 之后（而不是像人类那样最先）**：人类 gestalt 可靠，可以先 gestalt 后细节；LLM 自由先 gestalt 会**编**。所以顺序倒过来——先让 Phase 3 把客观盘点抓在手里，再在**有据**的基础上做 gestalt。同样的零件，顺序按失败模式调。

### 铁律（让 LLM 做全局而不编的唯一护栏）

**不自由联想，只检测客观共振。** 每条全局判断都必须**数得出来**——指回场上实际的牌/位/骰子/字卡，数不出就不能说。共振是「场 × 符号网」的客观属性，本步只**发现**它，不**制造**它。

- 重心 / 张力 / 共振组，每条都附"哪几张 / 哪几位 / 哪颗骰子"为证（重心 ≥3 项共现）。
- **核心牌意可用**（不限元素/属性层）：但只能用**依逻辑推导**的那一个核心（正逆是其变体），不查逆位牌意、不用牌意书。
- **不预定义"族 / granularity"**——抱团是自然语义判断，skill 不规定边界。
- 编不出的共振宁可留空。宁缺勿造。

### 五步（重心由前三步生出；张力管语言边界）

1. **illustrate 场景** — 把整副当**一幅画 / 一个场**来看（不是逐张）。用整张牌的核心 + 元素/族的抱团，说出这个场**整体什么调、往哪沉**。点出贡献的牌/位/骰子。
2. **locate 问题 + pos 功能** — 锚定**这次到底问什么**，以及每个 pos 在这副里**干什么活**。把场景对准问题和位格。
3. **当事人 lens + position** — 这盘从**谁的视角 / 太极点**读？当事人的 lens 与 position 的性质，决定场里的元素**怎么落**。
   → **重心** ＝ 以上三步的产物：场往哪沉 × 对准问题 × 经当事人 lens 之后，**承重落在哪**（列 ≥3 项共现为证）。
4. **共振组** — 哪几位共享同一元素 / 族 / 核心味 → 合并出什么质。点位 + 共享项为证。（范例：Pos2 水 + Pos4 土 + Pos5 杯骑士"接住别人需求" → 接受姿态。）
5. **找张力 / 假面 + 框定语言边界** — 哪里**表里不一**（看着安稳、底下沉；好牌当面值、难牌全压逆位）。引结构事实（正逆分布、主质量 vs 单张面值）。**张力框定语言的边界**：它划出这盘 answer **能说什么、不能说什么**——是表达的负空间，不只是一条 finding。

### 输出格式（喂给 Phase 4）

```
## Phase 3.5 场域称重
- 场景：[一句整场的画/调]
- 重心：[承重落点] — 证据：[≥3 项共现]
- 共振组：[位×位 → 合并质] — 证据：[共享项]
- 张力/假面：[表里不一处] — 证据：[结构事实]；语言边界：[answer 不许越过的边]
- 显著度（主梁→末节）：[排序]（按卦判 · 供人工当场校）
```

### 对 Phase 4 的约束（这是挂它的目的）

- **排出优先级 / answer salience** 按称重的「显著度」走；标为**主梁**的禁落 `open_threads`。
- **answer 收束**在本步**之后**完成，措辞守称重划出的「语言边界」（＝ via negativa 在全局层的延伸）。

### 状态（诚实标注）

本步为实验性方法。其中**「显著度」是最虚、最易偏的一步**——排显著度时把"内容"（WHAT 在传递）与"姿态"（HOW 在递）摊出来并排看，别让姿态味（收着 / 微妙 / 平静）自动顶成主梁；但**不立"内容压姿态"的定律**——姿态有时是包装（底下另有独立内容承重），有时就是答案本身（拒答即答），**按卦判**。称重结果必须**显式出现在输出里**（不藏），供使用者当场校准。

---

## Phase 4 — Via Negativa 收束

### 方法论

**事件是模型，牌是事件的投影。** Phase 3 已经把牌展开成了属性语言（元素/源质/旬星/尊贵/位置/复合意象/交叉校验）。Phase 4 的工作是操作这些属性材料，不是回忆罐头牌意。

### 第1步：排出

对每个 Phase 1 未知项（本系统的固定未知项见下），从 Phase 3 属性材料出发，**排除至少一个该材料不支持的候选答案**。

**候选必须是结构性候选**（"一次平滑、低摩擦的接收""被动、漠不关心的回应"），不能是牌意否定（"不是冲突的牌""不是代表爱的牌"）。

**每条排除必须附带证据**，引用 Phase 3 输出的**精确子串**。格式：

```
排除: [候选描述]
证据:
  - card: Death, layer: element_layer, quote: "cold+moist as the primary posture"
  - card: Death, layer: sephira_layer, quote: "links Tiphareth to Netzach"
```

### 逆位消去禁令（R0）

逆位卡不构成对正位属性的否定。Phase 3 的 dignity_layer 已声明逆位是「the same energy expressed through its negative form: repression, immaturity, or an out-of-control variant」——同一种能量，换了表达方式，不是能量消失。

在排出步骤中，**禁止以「牌是逆位」为由消去其正位属性所支持的结构性候选**。

| 正位 | 逆位不是 |
|------|---------|
| 权杖9：紧张的戒备、steady force under tension | 力量消失、不戒备 |
| 皇后：外在的照顾/滋养 | 不照顾、滋养消失 |
| 魔术师：技能/意志/通道流通 | 没有技能、意志缺席 |
| 世界：完成、循环闭合 | 什么都没完成 |

逆位的正确排出方式：保留正位的属性基础（力量/照顾/流通/完成），**排除「该属性以饱满、外向、无阻力方式运作」的候选**。逆位把同一属性折向内、压住、或换了一条不显眼的路——但属性本身没有蒸发。

### 本系统的固定未知项

spirit_draw_v2 的 6 位牌阵对应以下未知项：

1. **他的状态** (Pos 2)：他在做什么/处于什么能量状态
2. **他的态度** (Pos 4)：他对当前语境持什么姿态
3. **态度原因** (Pos 5)：为什么是这个态度
4. **他想说的** (Pos 6)：他想传达什么
5. **当前语境** (Pos 3)：两人之间正在发生什么（可用补牌锁定）
6. **我的状态（他视角下）** (Pos 1)：他怎么看你当前的状态

### 第2步：narrowed_field

在排除后，用**纯属性语言**描述收窄后的场域。1-3 句。

**可以使用**的词汇：姿势、压力、方向、重量、运动、接受性、限制、开放性、凝聚、轮廓、推进、静止、收缩、膨胀、传递、持有、边界。

**禁止出现**：
- 牌名、花色、数字、大牌/小牌
- 行星名、星座名、源质名、路径名、世界名
- "意味着""代表了""象征着""传统上""Book T 说"
- 任何形式的"这张牌是..."

### 第3步：跨符号校验

将 tarot narrowed field 与其他三套符号系统交叉验证：

**易经**（本卦 + 变爻 + 之卦）：
- 本卦核心意象 → 与 narrowed field 同向/反向/张力？
- 变爻爻辞的动作 → 补充了什么？
- 之卦走向 → 最终落在什么状态？

**占星骰子**（行星 + 星座 + 宫位 + 飞星）：
- 行星本性 → 什么力量在底层
- 星座性质 → 什么模式
- 宫位领域 → 落在哪个场域
- 飞星 → 哪两个领域之间在流动

**字卡**（三张）：
- 每张字卡的内容 + 落点（在场景的哪个位置/主体/动作上）
- 必须显式引用字卡内容并给出落点

跨符号校验的结果写入 narrowed_field 之后的一小段（2-4 句），说明**多源同向/张力/补充**。

### 第4步：answer

2-6 句。说场景不说牌。使用与问题语言一致的口语。

**禁止**：牌名、花色、行星、星座、源质、路径。禁止"这张牌说""塔罗显示"。说人话。

### 第5步：open_threads

诚实列出 Phase 4 未能完全覆盖的未知项。不确定就是不确定——保留空档比编造要好。

---

## 后检：R1/R2 散文规则（继承 v3.4）

answer 和 narrowed_field 写完后自检：

### R1：指涉对象规则

- 禁止抽象属性名词做施事主语（如"湿润带来""静止导致"）
- 禁止元素拟人化
- 每句必须能通过「朴素听者测试」——不知道牌阵的人也能听懂谁在做什么
- 用位置语义角色指代（"她那一位上""他态度底下的那张"）

### R2：隐式跨位

- 讨论某位置时延伸到关联位置，需要该位置自身的属性层支持

### 禁止句式

- 「不是……而是……」
- 「既……又……」
- 连续 3 句以上纯并列无逻辑连词
- 「这意味着」「代表了」「象征着」

---

## 输出模板

```markdown
## Phase 3 属性层

[per_card 表格：位置 | 牌 | 元素层 | 源质/路径层 | 旬星层 | 尊贵层]
[spread_synthesis：质量轴 + 元素平衡 + 源质模式]

## Phase 3.5 场域称重
- 场景：[一句整场的画/调]
- 重心：[承重落点] — 证据：[≥3 项共现]
- 共振组：[位×位 → 合并质] — 证据：[共享项]
- 张力/假面：[表里不一处] — 证据：[结构事实]；语言边界：[answer 不许越过的边]
- 显著度（主梁→末节）：[排序]（按卦判 · 供人工当场校）

## Phase 4 Via Negativa

### 排出
- 排除: [候选] — 证据: card X, layer Y, quote "..."

### narrowed_field
[纯属性语言 1-3 句]

### 跨符号校验
[易经 + 骰子 + 字卡 交叉验证]

### answer
[说场景不说牌]

### open_threads
[未覆盖的未知项]
```

---

## Phase 3 数据来源

- 标准 78 张：`data/tarot/{atu,pips,courts}.json`（只读引用）
- 奇迹 14 张：硬编码于 `phase3_unfold.py`（来源：奇迹牌组核心牌意提取.md）
- 易经：`data/yijing/`
- 字卡：spirit_draw_v2.py 输出
- 骰子：spirit_draw_v2.py 输出

## 禁止

- 跳过 Phase 3 属性层直接做解读
- 在排出中做牌意否定（"不是冲突的牌"）
- 在 narrowed_field 或 answer 中出现牌名/行星/星座/源质/路径名
- 编造或虚构 Phase 3 不存在的属性
- 用 bullet 列表替代 prose 段落（answer 必须是散文）
- 在 answer 中使用「不是……而是……」句式
