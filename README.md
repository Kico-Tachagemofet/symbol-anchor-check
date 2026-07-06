# Symbol Anchor Check v4.1

Tarot 解读属性校验 Skill。它用 Golden Dawn / Book T 的属性层检查一段塔罗解读是否站得住：元素、源质、旬星、尊贵状态、路径、宫廷牌跨度和牌位必须共同支持解读方向。

核心在于：先查硬属性，再收束解读。它适合放在抽牌结果和最终解释之间，做一次属性一致性检查。

## 适合谁

- 已经拿到塔罗牌阵，希望检查解读有没有顺着牌名套话。
- 使用 AI Agent 解读塔罗，想减少“看到权杖五就写冲突”这类检索式输出。
- 日常使用 `spirit-communication-system v5.1 Lite` 抽取原始结果，再对塔罗部分做后处理。
- 想把 Book T 属性体系变成可执行的 Agent Skill。

## 它做什么

Symbol Anchor Check 不负责抽牌。它负责在已有牌阵和已有问题语境上做校验：

1. 把牌名映射到 `data/tarot/` 中的 Book T 属性数据。
2. 展开五层属性材料。
3. 排除属性层无法支持的候选解释。
4. 用纯属性语言收窄解释范围。
5. 保留结构性歧义，避免把不收敛的材料硬写成结论。

## v4.1 工作流

| 阶段 | 名称 | 执行者 | 内容 |
|---|---|---|---|
| Phase 3 | 确定性属性展开 | 脚本 / 数据层 | 从 JSON 展开 Book T 属性、复合像、牌位材料 |
| Phase 3.5 | 场域称重 (Field-Weighing) | LLM / Agent | 把整副当一个场先称：重心 / 共振组 / 张力·假面 / 显著度 / 语言边界；只数客观共现，不自由联想 |
| Phase 4 | Via Negativa 收束 | LLM / Agent | 引用 Phase 3 精确材料，排除不支持的解释；排出优先级与措辞受 Phase 3.5 约束 |
| 后检 | R1 / R2 散文规则 | LLM / Agent | 检查指涉对象、跨位偷换和叙事漂移 |

Phase 3.5 是 v4.1 新增：补的是人类占卜师"先称整场往哪沉、再落单张"的那一下。为防 LLM 自由 gestalt 编造，它被放在 Phase 3 客观盘点**之后**，且每条全局判断都必须指得回场上具体的牌/位/骰/字卡。其中「显著度」子步最依赖判断，建议保持人工在环校准。

普通 prompt 可以提醒 AI 谨慎解读；这个 Skill 的优势在于数据、流程和检查点都放在同一套工作台里。

## 属性分层

每张牌都有可验证的属性层。

| 层 | 数字牌 | 大阿卡纳 | 宫廷牌 |
|---|---|---|---|
| 1 | 元素与冷热干湿 | 归属：行星 / 星座 / 元素 | 复合元素 |
| 2 | 源质 × 世界 | 生命之树路径 | 黄道跨度 |
| 3 | 旬星 | 路径两端 | 管辖旬星 |
| 4 | 尊贵状态 | 希伯来字母 | 牌阶功能 |
| 5 | 牌位语境 | 牌位语境 | 牌位语境 |

检查时优先使用属性材料。Book T 标题可以做交叉校验，不能当作推导起点。

## 数据层

```text
symbol-anchor-check/
├── README.md
├── SKILL.md
└── data/
    └── tarot/
        ├── atu.json      # 22 张大阿卡纳
        ├── pips.json     # 40 张数字牌
        └── courts.json   # 16 张宫廷牌
```

`data/tarot/` 包含 78/78 张塔罗牌的 Book T 属性条目。

| 文件 | 内容 |
|---|---|
| `atu.json` | 大阿卡纳：归属类型、路径、元素、品质、Book T 标题 |
| `pips.json` | 数字牌：源质、世界、旬星、尊贵状态 |
| `courts.json` | 宫廷牌：复合元素、黄道跨度、管辖旬星 |

## 推荐搭配

日常推荐搭配：

1. 用 [spirit-communication-system v5.1 Lite](https://github.com/Kico-Tachagemofet/spirit-communication-system-lite) 获取原始塔罗结果。
2. 对塔罗部分调用本 Skill。
3. 如果同一轮里有易经结果，用 [meihua-yishu](https://github.com/Kico-Tachagemofet/meihua-yishu) 处理卦象。
4. 最终解释由使用者结合问题语境、关系边界和现实情况判断。

## Prompt 版与 Skill 版

可以写一个轻量 prompt，提醒 AI 少用牌意检索。但完整流程更适合作为 Skill：

- 需要读取 78 张 Book T JSON 数据。
- 需要处理 RWS 中文牌名与 Book T ID 的映射。
- 需要区分数字牌、大阿卡纳、宫廷牌的属性结构。
- 需要保留属性不收敛的情况。
- 需要在输出前做指涉对象和跨位偷换检查。

当一个任务需要数据、映射和固定检查点，Agent Skill 会比单段 prompt 稳定很多。

## 来源与边界

本项目包含四类内容：

1. 传统来源：Golden Dawn / Book T 塔罗属性体系。
2. 作者整理：五层属性分层、Phase 3 / Phase 4 工作流、Via Negativa 收束规则。
3. 程序生成：从 JSON 数据展开的属性材料。
4. AI 参与：基于属性材料做排除、收束、交叉校验和叙事检查。

Book T 数据来源：Israel Regardie, *The Golden Dawn* (Llewellyn 6th ed.), Book T 章节。

本项目用于塔罗解读的属性一致性校验、符号分析和实验性 Agent 工作流。它不提供现实决策担保，不替代医疗、法律、财务或心理咨询建议。

## License

MIT
