---
name: symbol-anchor-check
description: "取象锚点检查 — Book T 属性分层版。用结构化数据层 + 五层属性分层（元素→源质→旬星→尊贵→牌位）做 tarot 解读的属性一致性核查。可与任何塔罗抽牌系统配合使用。"
tags: [divination, interpretation, quality-control, tarot, book-t]
---

# 取象锚点检查（Book T 分层版）

## 方法论锚

**事件才是模型，牌是事件的投影。** 不把牌当作可检索的现成含义。本检查器的全部工作都在**性质材料**（元素 / 源质 / 旬星 / 尊贵 / 牌位 / 复合像）上做"从不是到是"的排除；不在牌名 / 牌意 / 流派 lore 上做检索式回拉。

## 定位

本文件是一个**追问场景下的属性一致性核查器**——用户已抽过牌、已得到一份解读、想追问或要复核，Agent 在回复前用本文件的五步做一次属性锚定，发现解读违反某层属性就标出并要求重写。

- **不替代**完整的 via negativa 解读管线（建模→属性展开→收敛）。
- **不负责**初始解读的生成。
- **只做**属性一致性 gate check。

## 适用场景

- 与任何 tarot 抽牌系统配合：抽牌 → 初始解读 → 用户追问 → **本检查器介入**
- 推荐与 `spirit-communication-system v5.1 Lite` 配合：Lite 输出原始符号数据，用户在拿到数据后追问解读时触发本检查
- 也可独立使用：任何 tarot spread 的结果解读，只要牌名能映射到 Book T 体系，都可跑本检查

## 依赖

| 依赖 | 位置 | 说明 |
|------|------|------|
| Book T 大阿卡纳数据 | `data/tarot/atu.json` | 22 张，含归属、路径、元素、品质 |
| Book T 小阿卡纳数据 | `data/tarot/pips.json` | 40 张，含源质、世界、旬星、尊贵 |
| Book T 宫廷牌数据 | `data/tarot/courts.json` | 16 张，含复合元素、黄道跨度 |

所有数据源自 Israel Regardie, *The Golden Dawn* (Llewellyn 6th ed.) Book T 章节。78/78 条目完整，`_status: "ok"`。

---

## 牌名 → JSON ID 映射

Agent 从抽牌结果拿到牌名后，使用以下映射查找 JSON 条目。

### 小阿卡纳数字牌

```
中文牌名 → JSON id
权杖一 → ace_wands      圣杯一 → ace_cups      宝剑一 → ace_swords      星币一 → ace_disks
权杖二 → 2_wands        圣杯二 → 2_cups        宝剑二 → 2_swords        星币二 → 2_disks
...（全部 40 张，完整映射见上表模式）

英文：X of Wands/Cups/Swords/Pentacles → 同上规则。Pentacles = Disks。
```

### 宫廷牌

```
中文牌名              → JSON id              备注
权杖国王              → king_of_wands         Book T 「火之火」
权杖王后              → queen_of_wands        Book T 「水之火」
权杖骑士              → prince_of_wands       ⚠️ 中文"骑士"=Book T Prince（非 King）
权杖侍从              → princess_of_wands     ⚠️ 中文"侍从"=Book T Princess
（其余三个花色同理）

⚠️ 关键陷阱：中文"骑士"=RWS Knight=Book T Prince；
   中文"国王"=RWS King=Book T King。
   脚本输出"权杖骑士"，查 prince_of_wands，不是 king_of_wands。

英文（RWS 常用）：King → king_of / Queen → queen_of / Knight → prince_of / Page → princess_of
```

### 大阿卡纳

```
中文 / 英文                            → JSON id
愚者 / The Fool                        → atu_00_fool
魔术师 / The Magician                  → atu_01_magician
女祭司 / The High Priestess            → atu_02_high_priestess
...（全部 22 张）

⚠️ Book T/GD 使用 Justice=VIII / Fortitude(Strength)=XI。
   RWS 常见牌面编号交换。JSON 内部用 Book T/GD 编号。查牌时用牌名匹配，不要用数字匹配。
```

---

## 检查流程（五步）

### 第〇步：牌名解析 & JSON 查找

1. 提取每张牌的**名称**和**正逆位**
2. 用映射表找到 JSON id
3. 加载 `book_t` 字段
4. `_status: "ok"`（当前 78/78 全部为此状态）：使用所有非空字段

### 第一步：五层属性展开

**数字牌（Minor Pip）**——五层：
- Layer 1 [元素]： element + primary_qualities（如 Fire [hot, dry]）
- Layer 2 [源质×世界]： sephira + sephira_qualities + world（如 Geburah of Atziluth）
- Layer 3 [旬星]： decan.planet in decan.sign + span_degrees
- Layer 4 [尊贵]： decan_dignity（如 Saturn in detriment in Leo）
- Layer 5 [牌位]： position_label

**大阿卡纳（Major Arcana）**——四层（无旬星）：
- Layer 1 [归属]： attribution.type + attribution.value + primary_qualities
- Layer 2 [路径]： path_on_tree + path_between（如 path 11, Kether→Chokmah）
- Layer 3 [牌位]： position_label
- Layer 4 [希伯来字母]： hebrew_letter（锚点；字面含义不在 JSON 内，需要时引外部参照）

**宫廷牌（Court）**——四层（无旬星/源质）：
- Layer 1 [复合元素]： element_compound + primary_qualities（外层 rank 元素的性质）
- Layer 2 [黄道跨度]： zodiacal_span 或 celestial_quadrant（Princess 专属）
- Layer 3 [牌位]： position_label
- Layer 4 [管辖旬星]： rules_decans（可选）

### 第二步：硬属性一致性检查

逐层检查解读是否违反属性：

1. **元素层**：解读的"姿态"是否匹配 primary_qualities？
   - Fire [hot, dry] → 向外、意志驱动。不能"被动"、"接受"。
   - Water [cold, moist] → 向内、情感驱动。不能"精确"、"锐利"。
   - Air [hot, moist] → 轻、穿透、方向不明。不能"沉重"、"静止"。
   - Earth [cold, dry] → 致密、静止、晦暗。不能"运动"、"轻盈"。

2. **源质层**：sephira 的结构性约束
   - Geburah（5）→ 严厉、限制。不是丰盛。
   - Chesed（4）→ 扩张、建构。不是收缩。
   - Tiphareth（6）→ 平衡、中心。不是极端。

3. **旬星层**：行星×星座组合
   - Saturn in Leo → 不能忽略 Saturn 重量
   - Venus in Aries → 不能套"Venus=温柔"默认

4. **尊贵层**：dignity 是调节器，不是独立含义
   - Rulership → 清洁高效 / Detriment → 别扭受阻
   - Exaltation → 过度强化 / Fall → 虚弱压制

5. **牌位层**：属性→场景，不是标签→标签
   - 禁止"他的态度=冲突"式直接等式

**禁用句式 regex 检查**：
- `"[牌名]代表"` / `"[牌名]意味着"` / `"[牌名]表示"` / `"[牌名]象征"`
- `"这张牌是关於"` / `"[牌名]是……的牌"`
- `"在塔罗中"` / `"传统上"` / `"在韦特传统中"`
- `"Book T 说"` / `"按 Book T"`
- 英文：`represents` / `means that` / `indicates` / `canonically` / `traditionally`
- 单字标签：`"= 冲突"` `"= 成功"` 等

### 第三步：Book T Title 交叉校验（三档极性）

从 JSON 提取 `book_t_title`（如 "Lord of Strife"）。

**三档**：
- **converges**：属性推导极性方向与 Book T 标题极性一致
- **tension**：属性推导与标题极性相反 —— **不是错误，是诊断信号**。该牌在该位置"表面是 X，底层载着 Y"，必须保留双层读法
- **mixed**：一方或两方极性中性/不清

**铁律**：Book T 标题只能出现在交叉校验中，**禁止**作为推导起点（"Lord of Strife → 所以冲突"）。

### 第四步：空是允许的

五层属性无法收敛时，输出`[属性层不收敛；结构性歧义]`。禁止从通用塔罗知识借"常见牌意"填补。

### 第五步：用户实践语境覆盖

检查解读极性是否被主流塔罗默认值污染：

| 符号 | 默认读法 | 非主流实践覆盖后 |
|------|---------|----------------|
| Hierophant 逆位 | 师承失灵=警告 | 异教/PGM 语境基线——事实陈述 |
| Devil | 束缚=负面 | 左手路径=神圣存在 |
| Tower | 崩塌=危机 | 结构破除=必要清场 |
| 死神 | 终结=中性偏负 | 死亡崇拜实践=正向召请 |

---

## 输出格式

执行时不展示检查过程。通过后直接输出解读。

如果发现违反：
```
（之前的理解有偏差：[哪一层属性被违反]）
更正：[基于属性重新推导的解读]
```

如果属性层不收敛：
```
（属性层未收敛。歧义点：[...] 需要进一步对话澄清。）
```

---

## 禁止

- 跳过五层属性展开，直接用"牌意"套牌位
- 使用禁用句式 regex 中的任何模式
- 用 Book T title 替代属性推导
- 把 tension 卡读成单一方向（必须保留双层）
- 从通用塔罗知识借"常见牌意"填补空位
- 行星归属的大阿卡纳跳过 quality 层
- 在非主流实践语境中仍按主流极性读出"警告"
