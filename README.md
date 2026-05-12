# Symbol Anchor Check — Book T 属性分层版

一套用于 tarot 解读的**属性一致性核查器**。不查"牌意"，只查属性。

## 核心理念

**事件才是模型，牌是事件的投影。**

传统的 tarot 解读倾向于"检索牌意"——看到权杖五就想到"冲突"，看到圣杯二就想到"恋爱"。这个 skill 拒绝这种工作方式。

它做的事情是：

1. 每张牌携带一组**硬属性**（元素、源质、旬星、尊贵），这些属性来自 Golden Dawn 的 Book T
2. 解读必须从属性**推导**出来，不能从牌名或传统 lore **检索**出来
3. 如果解读违反了某层属性，就被判定为不合格，退回重写

这不是"另一种解读方法"，这是一个 **gate check**——在你已有的解读和你已有的抽牌之间，做一次属性一致性验证。

## 方法论

### 五层属性分层

每张牌有五层可验证的硬属性：

| 层 | 数字牌 | 大阿卡纳 | 宫廷牌 |
|---|--------|---------|--------|
| 1 | 元素 [hot/dry 等] | 归属 [planet/sign/element] | 复合元素 [Fire of Water 等] |
| 2 | 源质×世界 [Geburah of Atziluth] | 路径 [Kether→Chokmah] | 黄道跨度 |
| 3 | 旬星 [Saturn in Leo] | — | — |
| 4 | 尊贵 [detriment/fall 等] | — | — |
| 5 | 牌位 | 牌位 | 牌位 |

### 从不是到是（Via Negativa）

解读不靠"这张牌意味着什么"，而是靠排除：属性层不支持的解读方向先被排除，剩下的才能进入下一步考虑。一张牌在不同的 spread 位置、不同的问题语境里，属性层给出的"允许区间"不同——同一张权杖五在"他的态度"位和在"原因"位是两套合法解读。

### Book T 交叉校验（三档极性）

Book T 给每张牌一个标题（如 "Lord of Strife"、"Lord of Love"），但这些标题**不能作为推导起点**。它们只做交叉校验：

- **converges**：属性推导方向与标题一致
- **tension**：属性推导与标题极性相反 —— 不是错误，是双层信号
- **mixed**：一方或两方极性中性

tension 是最有价值的状态：它告诉你这张牌在该位置"表面是一个方向，底层载着另一个方向"。不允许把 tension 平均掉。

## 数据层

`data/tarot/` 下三个 JSON 文件，包含全部 78 张牌的 Book T 属性：

| 文件 | 内容 |
|------|------|
| `atu.json` | 22 张大阿卡纳：归属类型、路径、元素、品质、Book T 标题 |
| `pips.json` | 40 张数字牌：源质、世界、旬星（行星×星座）、尊贵状态 |
| `courts.json` | 16 张宫廷牌：复合元素、黄道跨度、管辖旬星 |

数据源：Israel Regardie, *The Golden Dawn* (Llewellyn 6th ed.), Book T 章节。78/78 条目完整。

## 使用方式

### 与 v5.1 Lite 配合（推荐）

1. 运行 `spirit-communication-system v5.1 Lite`，拿到原始符号数据
2. 用户对结果进行追问（"这个牌什么意思""为什么是这个卦"）
3. Agent 加载本 skill，执行五步属性检查
4. 输出通过检查的解读

### 独立使用

任何 tarot spread 的结果，只要牌名能映射到 Book T 体系（标准 RWS 中文/英文牌名），都可以跑本检查。

## 文件结构

```
symbol-anchor-check/
├── README.md          # 本文件
├── SKILL.md           # 主 skill 文件
└── data/
    └── tarot/
        ├── atu.json   # 大阿卡纳
        ├── pips.json  # 数字牌
        └── courts.json # 宫廷牌
```

## License

MIT
