# Sources and Attribution

本页区分传统文献、结构化资料、项目方法与扩展对应。文献提供框架；在具体牌阵中怎样确定主体、关系和支持范围，由当前材料与本项目的解读流程完成。

## Golden Dawn / Book T

标准 78 张数据沿用仓库既有来源说明：

**Israel Regardie, *The Golden Dawn*（Llewellyn 第 6 版），Book T 章节。**

- [`data/tarot/atu.json`](data/tarot/atu.json)：22 张大阿卡纳的归属、路径、品质、标题与短摘要。
- [`data/tarot/pips.json`](data/tarot/pips.json)：40 张数字牌的元素、源质、世界、旬星与尊贵。
- [`data/tarot/courts.json`](data/tarot/courts.json)：16 张宫廷牌的复合元素、黄道跨度、管辖旬星与牌阶资料。

条目中的 `source.primary` 与 `source.section_label` 保留原有出处信息；未填写的页码不在本页补造。JSON 是项目整理的结构化属性和短摘要，不是该书的完整转录。牌名映射用于定位数据条目，实际使用某一牌组的图像时还需辨明版本和图像来源。

## 四元素原典与理论参照

| 原著 | 参照范围 | 本项目中的用途 |
|---|---|---|
| **Aristotle, *On Generation and Corruption*, Book II, Chapters 2–4**（亚里士多德《论生成与消灭》卷二第 2–4 章） | 冷热干湿、性质配对、元素互化及共享性质 | [冷热干湿方法](addons/symbol-field-weighing/references/hot-cold-dry-moist.md)中的共同性质、相对与转换 |
| **Heinrich Cornelius Agrippa, *Three Books of Occult Philosophy*, Book I, Chapter 3**（阿格里帕《隐秘哲学三书》卷一第 3 章） | 元素的自身／中介性质、轻重与主被动，以及三性质的排列 | [三性质方法](addons/symbol-field-weighing/references/three-properties.md)与冷热干湿的框架 |
| **Stephen Arroyo, *Astrology, Psychology, and the Four Elements*, Chapter 12, “Elements in Interpretation”** | 元素不足、强调与组合的心理及行为维度 | [能量模型](addons/symbol-field-weighing/references/element-combinations.md)中的缺乏／强化、两种偏重与六种组合 |

亚里士多德所论的性质与转化见 [Internet Classics Archive 的卷二文本](https://classics.mit.edu/Aristotle/gener_corr.2.ii.html)。阿格里帕的两性质、三性质与元素相接关系见 [Esoteric Archives 的卷一第 3 章](https://esotericarchives.com/agrippa/agrippa1.htm)。这两份在线文本提供原典查阅入口；Arroyo 的章节按书中章节定位，不虚列未经确认的页码或在线全文。

## 项目应用与方法

以下属于本项目的组织、解释或实现：

- Phase 3 五层属性展开，以及来源、牌位和主补参与范围的记录。
- Phase 3.5 从整体场景、问题与视角形成重心，再以共振和张力复核的流程。
- Phase 4 的结构性候选、排除／保留／未定、跨符号核对与表达规则。
- 把三性质用于目的、状态与发展方式，把冷热干湿用于当前参与方式、共享性质与中介的塔罗应用。
- [元素关系方法](addons/symbol-field-weighing/references/element-relations.md)中的风的连接、火因水果、水影响土，以及方法卡中的场景示例。

原著的物性论述、占星心理模型与本项目的牌阵应用各保留自己的语境。方法卡里的工作、情绪、关系或资源例子用于展示推导方式，不作为原作者已经写出的塔罗牌义，也不取代当前牌位与属性证据。

## Miracle 扩展

[`addons/miracle-anchor-addon/`](addons/miracle-anchor-addon/) 处理传统 78 张之外的 Miracle 扩展：

- `miracle.json` 收录项目维护的 14 张核心短释；扩展元素统一为 **Aether**。
- 源质、行星与星座主锚是**项目作者建立的对应**，不属于原 Book T 的赋值，也不以此声称为原牌组作者的官方对应。
- `miracle_unfold.py` 将这些资料展开到与标准牌兼容的属性结构；Q1／Q2 检查增量和语境一致性。
- 仓库未随附牌面美术。核心短释、主锚、程序展开与原牌组图像分别看待。

## 许可与权利说明

仓库 README 的既有许可声明为 **MIT**，本次保留该声明及 Book T 数据的原有来源信息。

原著、现代出版版本、译本及原牌组素材各有其相应权利；本仓库的 MIT 声明不额外授予这些第三方材料的复制或再分发权。本页仅说明来源与本项目的使用方式，不声称已取得原著、出版商或原牌组的额外授权。
