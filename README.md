# findata-classify

[English](#english) | [中文](#中文)

---

## 中文

### 概述

`findata-classify` 是一个金融数据分类分级工具，基于《金融信息服务数据分类分级指南》（国信办通字〔2026〕2号）对金融数据进行自动分类（三级分类体系）和分级（四级分级体系）。

支持两种推理模式：
- **精确匹配** — 基于知识库（67 条权威分类 + 用户自定义）的关键字匹配
- **语义推理** — 大模型驱动的语义匹配 + 首原理分级矩阵推理（当关键字匹配无结果时）

可集成于 Claude Code、OpenCode、WorkBuddy 等 AI 助手，通过 `/findata-classify` 命令触发。

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/winsurelab/findata-classify.git
cd findata-classify

# 首次使用：初始化知识库（自动下载 PDF 并提取）
pip install pymupdf
python init.py

# 离线关键字匹配
python classifier.py "身份证号"

# 在 AI 助手中使用
# > /findata-classify 身份证号
```

> **数据来源**：基于国家互联网信息办公室发布的《金融信息服务数据分类分级指南》（国信办通字〔2026〕2号）。
>
> 由于版权原因，PDF 原文及提取的知识库文件（`custom.json` 除外）不随仓库分发。首次使用时，`init.py` 会尝试从官方地址自动下载 PDF；若默认链接失效，脚本会提示 AI 助手**自行通过 WebSearch 搜索并下载**，无需手动寻找。知识库提取完成后，运行时不再依赖 PDF。

### 架构

> **优先级**：`custom.json`（用户自定义）> `authoritative.json`（权威分类）> 大模型语义推理 > 首原理推理

```
输入数据名称
    │
    ├─ Step 1: 关键字匹配（离线）
    │   custom.json ← 最高优先级，命中即返回
    │       ↓ miss
    │   authoritative.json ← 67 条权威分类
    │   → 命中则直接返回
    │
    └─ Step 2: 大模型推理
        ├─ 阶段①: 语义匹配（67 分类中找最接近）
        └─ 阶段②: 首原理推理（影响矩阵 → 级别矩阵 → 定级）
```

### 文件说明

| 文件 | 说明 |
|------|------|
| `classifier.py` | 离线关键字匹配引擎 |
| `build_knowledge.py` | 从 PDF 提取结构化知识库 |
| `init.py` | 初始化编排脚本 |
| `SKILL.md` | AI 助手技能定义 |
| `knowledge/custom.json` | **用户自定义分类（最高优先级，随仓库分发）** |
| `knowledge/authoritative.json` | 67 条权威分类（由 PDF 提取生成） |
| `knowledge/terms.json` | 术语定义（由 PDF 提取生成） |
| `knowledge/category_framework.json` | 三级分类框架（由 PDF 提取生成） |
| `knowledge/impact_matrix.json` | 影响程度判定表（由 PDF 提取生成） |
| `knowledge/grade_matrix.json` | 级别判定矩阵（由 PDF 提取生成） |
| `knowledge/grading_rules.json` | 分级规则（由 PDF 提取生成） |

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

### Overview

`findata-classify` automatically classifies and grades financial data according to the *Financial Information Service Data Classification and Grading Guide* (CAC Notice No. 2, 2026). It outputs a 3-level taxonomy path and a 4-tier sensitivity grade.

Two reasoning modes:
- **Exact match** — keyword lookup against a knowledge base (67 authoritative entries + user custom entries)
- **Semantic reasoning** — LLM-driven semantic matching + first-principles grading matrix reasoning (fallback when keyword search yields no results)

Integrates with AI assistants like Claude Code, OpenCode, and WorkBuddy via the `/findata-classify` command.

### Quick Start

```bash
# Clone
git clone https://github.com/winsurelab/findata-classify.git
cd findata-classify

# First-time setup (auto-downloads the official PDF)
pip install pymupdf
python init.py

# Offline keyword matching
python classifier.py "resident_id_number"

# Use with AI assistants
# > /findata-classify resident_id_number
```

> **Data source**: Based on the *Financial Information Service Data Classification and Grading Guide* (CAC Notice No. 2, 2026) published by the Cyberspace Administration of China.
>
> Due to copyright, the original PDF and extracted knowledge files (except `custom.json`) are **not** distributed with the repo. On first use, `init.py` auto-downloads the PDF from the official URL. If the default link is expired, the script instructs the AI assistant to **search the web** for a valid copy — no manual hunt required. Once extracted, the PDF is no longer needed at runtime.

### Architecture

> **Priority**: `custom.json` (user custom) > `authoritative.json` (official) > LLM semantic matching > first-principles reasoning

```
Input Data Name
    │
    ├─ Step 1: Keyword Match (offline)
    │   custom.json ← highest priority, return on hit
    │       ↓ miss
    │   authoritative.json ← 67 official entries
    │   → Hit → return directly
    │
    └─ Step 2: LLM Reasoning
        ├─ Phase ①: Semantic matching (among 67 entries)
        └─ Phase ②: First-principles reasoning (impact matrix → grade matrix → grade)
```

### Output Format

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
