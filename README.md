# findata-classify

基于《金融信息服务数据分类分级指南》（国信办通字〔2026〕2号）对金融数据进行分类分级的 OpenCode 技能。

输入数据名称，输出 JSON 结构化建议（三级分类路径 + 分级 + 升级条件）。

## 依赖

- Python 3.10+
- [PyMuPDF](https://pypi.org/project/PyMuPDF/)（用于从 PDF 提取表格）

```bash
pip install pymupdf
```

## 安装

将 `findata-classify/` 目录复制到 OpenCode 技能路径：

| 平台 | 路径 |
|------|------|
| 全局 | `~/.config/opencode/skills/findata-classify/` |
| 项目 | `.opencode/skills/findata-classify/` |
| Claude 兼容 | `~/.claude/skills/findata-classify/` |

## 用法

```
/findata-classify 身份证号
/findata-classify 股票实时行情
/findata-classify 公司员工姓名
```

也支持命令行直接调用：

```bash
python classifier.py "身份证号"
python classifier.py -o result.json "供应链数据"
python classifier.py --interactive
```

## 数据来源

### 官方文件

《金融信息服务数据分类分级指南》（国信办通字〔2026〕2号）发布在：

- 国家互联网信息办公室官网：http://www.cac.gov.cn
- 全国标准信息公共服务平台：https://std.samr.gov.cn

请自行下载后放入技能目录，文件名需为 `金融信息服务数据分类分级指南.pdf`。

### authoritative.json 制作方法

`knowledge/authoritative.json` 包含 67 条分类记录，使用 `build_knowledge.py` 从 PDF 附录 A 自动提取生成：

```bash
python build_knowledge.py
```

提取逻辑：
1. 用 PyMuPDF `find_tables()` 读取 PDF 第 13 页起（附录 A）的全部表格
2. 每行提取：一级分类、二级分类、三级分类、描述和示例、参考最低级别和升级条件
3. 按 `一级分类|二级分类|三级分类` 去重
4. 过滤掉表头垃圾行（如"分类分级依据"）
5. 输出 JSON 到 `knowledge/authoritative.json`

### 自定义覆盖（custom.json）

`knowledge/custom.json` **优先级最高**，用于处理三类特殊情况：

1. **指南未覆盖的类别** — 企业特有的数据分类（如供应链数据）
2. **规则失效的兜底** — `parse_grade()` 无法正确解析的复杂分级条件，可直接在 custom.json 中写死正确结果
3. **LLM 无法处理的边缘情况** — 大模型语义匹配可能出错的特例，通过 custom.json 精确命中，跳过 LLM 判断

custom.json 遵循与 authoritative.json 相同的 JSON 结构，查询时若关键字完全匹配，直接返回自定义结果，不经过 LLM 语义匹配。

## 文件结构

```
findata-classify/
├── SKILL.md                   # 技能入口
├── classifier.py              # 关键字匹配引擎
├── build_knowledge.py         # 从 PDF 提取知识库
├── knowledge/
│   ├── authoritative.json     # 67 条权威分类（从 PDF 提取）
│   └── custom.json            # 用户自定义覆盖
├── 金融信息服务数据分类分级指南.pdf  # 官方原文件（需自行下载）
└── README.md
```

## 许可证

本技能代码部分采用 MIT 许可证。《金融信息服务数据分类分级指南》版权归其发布机构所有。
