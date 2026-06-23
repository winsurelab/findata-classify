"""
金融信息服务数据分类分级助手
基于《金融信息服务数据分类分级指南》（国信办通字〔2026〕2号）

三层匹配：
  1. custom.json（用户自定义，优先级最高）
  2. authoritative.json（从 PDF 自动提取，权威数据源）
  3. 原始 PDF（PyMuPDF find_tables()，兜底语义匹配）

用法：
  python classifier.py "数据名称"
  python classifier.py --interactive
"""
import sys
import json
import re
import os
import fitz

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(SKILL_DIR, "knowledge")
AUTHORITATIVE_FILE = os.path.join(KNOWLEDGE_DIR, "authoritative.json")
CUSTOM_FILE = os.path.join(KNOWLEDGE_DIR, "custom.json")
PDF_FILE = os.path.join(SKILL_DIR, "金融信息服务数据分类分级指南.pdf")


# =============================================================
# 知识库加载
# =============================================================

def load_json(path):
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_knowledge():
    """加载权威 + 自定义知识库，自定义优先级更高"""
    auth = load_json(AUTHORITATIVE_FILE)
    custom = load_json(CUSTOM_FILE)

    # 构建去重索引：三级分类存在 custom 时覆盖 authoritative
    merged = {}
    for r in auth:
        key = f"{r['一级分类']}|{r['二级分类']}|{r['三级分类']}"
        merged[key] = {**r, "_source": "authoritative"}

    for r in custom:
        key = f"{r['一级分类']}|{r['二级分类']}|{r['三级分类']}"
        merged[key] = {**r, "_source": "custom"}

    return list(merged.values())


# =============================================================
# 关键字索引
# =============================================================

def build_index(rows):
    index = []
    for row in rows:
        l1, l2, l3 = row["一级分类"], row["二级分类"], row["三级分类"]
        for kw in [l3, l2, l1]:
            if kw:
                index.append((kw, row))
        desc = row.get("描述", "")
        for part in re.split(r'[，。、；：\s]', desc):
            part = part.strip()
            if len(part) >= 4:
                index.append((part, row))
    return index


def score_match(query: str, keyword: str) -> int:
    q, k = query.lower(), keyword.lower()
    if q == k:
        return 100
    if k in q:
        return 80
    if q in k:
        return 60
    # Split CJK char by char, ASCII words as whole tokens
    qw = set(re.findall(r'[a-z0-9_]+|[\u4e00-\u9fff\u3400-\u4dbf]', q))
    kw = set(re.findall(r'[a-z0-9_]+|[\u4e00-\u9fff\u3400-\u4dbf]', k))
    common = qw & kw
    return len(common) * 10 if common else 0


def keyword_search(query: str, rows: list) -> list:
    """关键字匹配，返回侯选列表"""
    index = build_index(rows)
    hits = {}
    for keyword, row in index:
        s = score_match(query, keyword)
        if s > 0:
            key = f"{row['一级分类']}|{row['二级分类']}|{row['三级分类']}"
            if key not in hits or s > hits[key][0]:
                hits[key] = (s, row)
    result = sorted(hits.values(), key=lambda x: -x[0])
    return result


# =============================================================
# PDF 兜底语义搜索
# =============================================================

def read_all_pdf_rows() -> list:
    """读取 PDF 附录A 全部表格行（供大模型语义匹配使用）"""
    if not os.path.isfile(PDF_FILE):
        return []

    doc = fitz.open(PDF_FILE)
    rows = []
    l1, l2 = "", ""
    for pn in range(12, len(doc)):
        page = doc[pn]
        for t in page.find_tables():
            for row in t.extract()[1:]:
                cells = [str(c).strip().replace("\n", " ").replace("\r", "") if c else "" for c in row]
                while len(cells) < 5:
                    cells.append("")
                c1, c2, c3, desc, grade = [c.replace(" ", "") if i < 3 else c for i, c in enumerate(cells[:5])]
                if c1: l1 = c1
                if c2: l2 = c2
                if c3:
                    rows.append({
                        "一级分类": l1, "二级分类": l2, "三级分类": c3,
                        "描述": desc, "参考级别和条件": grade,
                    })
    doc.close()
    return rows


# =============================================================
# 分级解析
# =============================================================

def parse_grade(row: dict) -> dict:
    raw = row.get("参考级别和条件", "")
    # Normalize spaces within CJK text (PDF extraction artifact)
    raw = re.sub(r'(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])', '', raw)
    grades = ["核心数据", "重要数据", "敏感一般数据", "常规一般数据"]

    # Default = last mentioned grade (the "其他" fallback case)
    mentioned = [g for g in grades if g in raw]
    default_grade = mentioned[-1] if mentioned else "常规一般数据"

    rules = []
    parts = re.split(r'[；;]\s*', raw)
    for p in parts:
        p = re.sub(r'^[\d.、 ]+', '', p.strip())
        if not p:
            continue
        for g in grades:
            if g in p and g != default_grade:
                cond = p.replace(g, "").strip("。，；;、. ")
                cond = cond.rstrip("属于")
                if cond:
                    rules.append((cond, g))
                break

    return {"default_grade": default_grade, "rules": rules}


# =============================================================
# 主查询
# =============================================================

MAX_CANDIDATES = 20


def result_json(query: str) -> dict:
    # 1) 关键字匹配知识库（优先）
    knowledge_rows = load_knowledge()
    matches = keyword_search(query, knowledge_rows)

    if matches:
        seen = set()
        candidates = []
        for score, row in matches:
            if len(candidates) >= MAX_CANDIDATES:
                break
            key = f"{row['一级分类']}|{row['二级分类']}|{row['三级分类']}"
            if key in seen:
                continue
            seen.add(key)
            g = parse_grade(row)
            candidates.append({
                "关键字匹配度": score,
                "来源": row.get("_source", "authoritative"),
                "分类": {"一级": row["一级分类"], "二级": row["二级分类"], "三级": row["三级分类"]},
                "描述": row.get("描述", ""),
                "参考最低级别": g["default_grade"],
                "升级条件": [f"当{cond} → {grade}" for cond, grade in g["rules"]],
            })
        return {"query": query, "candidates": candidates}

    # 2) 兜底：关键字未命中，由大模型用 PyMuPDF 直接读 PDF 做语义匹配
    return {"query": query, "candidates": []}


def interactive():
    kn = len(load_knowledge())
    print("金融信息服务数据分类分级助手")
    print(f"知识库: {kn} 条（含自定义）")
    print("输入数据名称查询，输入 q 退出\n")
    while True:
        try:
            q = input("数据名称 > ").strip()
            if q.lower() in ("q", "quit", "exit"):
                break
            if not q:
                continue
            result = result_json(q)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="金融信息服务数据分类分级助手 - 基于《金融信息服务数据分类分级指南》"
    )
    parser.add_argument("query", nargs="*", help="待分类的数据名称（多个词自动拼接）")
    parser.add_argument("-i", "--interactive", action="store_true", help="交互模式")
    parser.add_argument("-o", "--output", help="输出到文件（JSON）")

    args = parser.parse_args()

    if args.interactive or (not args.query and not args.output):
        interactive()
    elif args.query:
        result = result_json(" ".join(args.query))
        out = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out)
        else:
            print(out)
    else:
        parser.print_help()
