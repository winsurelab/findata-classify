# findata-classify

[English](#english) | [中文](#中文)

---

## 中文

基于《金融信息服务数据分类分级指南》（国信办通字〔2026〕2号）对金融数据自动分类（三级）和分级（四级）。可集成于 Claude Code、OpenCode、WorkBuddy 等 AI 助手，通过 `/findata-classify` 触发。

### 快速开始

```bash
git clone https://github.com/winsurelab/findata-classify.git && cd findata-classify
pip install pymupdf && python init.py   # 首次：自动下载 PDF 并提取知识库
python classifier.py "身份证号"          # 离线关键字匹配
```

> **数据来源**：国家网信办官方 PDF。`init.py` 自动下载；若链接失效，AI 助手会自行 WebSearch 搜索。版权原因，PDF 及生成知识文件不随仓库分发（`custom.json` 除外）。知识库提取后不再依赖 PDF。

### 架构

**分类**：三级体系（一级 → 二级 → 三级），按业务领域逐级归入。**分级**：基于「影响对象 × 影响程度」矩阵判定（核心 > 重要 > 敏感一般 > 常规一般）。

匹配优先级依次降级：

```
输入名称 → custom.json（最高优先级）→ authoritative.json（67条）→ 语义推理 → 首原理推理
```

多匹配时按分降序取前 20 条；离线仅返侯选列表，AI 模式下 LLM 从侯选中判定最佳。

### 文件

| 文件 | 说明 |
|------|------|
| `classifier.py` | 离线关键字匹配引擎 |
| `build_knowledge.py` | 从 PDF 提取知识库 |
| `init.py` | 初始化脚本 |
| `SKILL.md` | AI 助手技能定义 |
| `knowledge/custom.json` | **用户自定义（最高优先级，随仓库分发）** |
| `knowledge/authoritative.json` | 67 条权威分类（由 PDF 生成） |
| `knowledge/terms.json` | 术语定义（由 PDF 生成） |
| `knowledge/category_framework.json` | 三级分类框架（由 PDF 生成） |
| `knowledge/impact_matrix.json` | 影响程度判定表（由 PDF 生成） |
| `knowledge/grade_matrix.json` | 级别判定矩阵（由 PDF 生成） |
| `knowledge/grading_rules.json` | 分级规则（由 PDF 生成） |

### 输出格式

```json
{
  "数据名称": "身份证号",
  "语义匹配度": 90,
  "分类": { "一级": "用户数据", "二级": "个人用户数据", "三级": "个人用户基本信息" },
  "分级": "敏感一般数据",
  "升级条件": ["当1000万人及以上的个人用户基本信息数据集 → 重要数据"],
  "理由": "依据《金融信息服务数据分类分级指南》附录A，身份证号属于..."
}
```

---

## English

Classify & grade financial data per the *Financial Information Service Data Classification and Grading Guide* (CAC Notice No. 2, 2026). Works with Claude Code, OpenCode, and WorkBuddy via `/findata-classify`.

### Quick Start

```bash
git clone https://github.com/winsurelab/findata-classify.git && cd findata-classify
pip install pymupdf && python init.py   # first run: auto-download PDF & build knowledge
python classifier.py "resident_id_number"  # offline keyword match
```

> **Data source**: Official CAC PDF. `init.py` auto-downloads; if the link expires, the AI assistant searches the web. Due to copyright, only `custom.json` is distributed with the repo.

### Architecture

**Classification**: 3-level taxonomy (L1 → L2 → L3). **Grading**: impact object × impact degree matrix (core > important > sensitive > general).

Priority chain: `custom.json` (highest) → `authoritative.json` (67 entries) → LLM semantic → first-principles reasoning.

Multiple matches: sorted by score descending, top 20 returned. Offline mode returns candidate list; AI mode lets the LLM pick the best.

### Output

```json
{
  "数据名称": "resident_id_number",
  "语义匹配度": 90,
  "分类": { "一级": "user_data", "二级": "individual_user_data", "三级": "basic_info" },
  "分级": "sensitive_general_data",
  "升级条件": ["≥10M records → important_data"],
  "理由": "Per Appendix A of the Guide, resident ID numbers are classified as..."
}
```

### License

MIT
