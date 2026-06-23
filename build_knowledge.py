"""
从 PDF 提取附录 A 表格，构建权威知识库
"""
import json, os, sys
import fitz

PDF_NAME = "金融信息服务数据分类分级指南.pdf"
OUTPUT = "knowledge/authoritative.json"


def extract(pdf_path):
    doc = fitz.open(pdf_path)
    rows = []
    l1, l2 = "", ""

    for pn in range(12, len(doc)):
        page = doc[pn]
        for t in page.find_tables():
            data = t.extract()
            for row in data[1:]:
                cells = [str(c).strip().replace("\n", " ").replace("\r", "") if c else "" for c in row]
                while len(cells) < 5:
                    cells.append("")
                c1, c2, c3, desc, grade = cells[:5]
                if c1: l1 = c1.replace(" ", "")
                if c2: l2 = c2.replace(" ", "")
                if c3:
                    c3 = c3.strip().replace(" ", "")
                    if c3 in ("分类分级依据",):
                        continue
                    rows.append({
                        "一级分类": l1,
                        "二级分类": l2,
                        "三级分类": c3,
                        "描述": desc,
                        "参考级别和条件": grade,
                    })
    doc.close()
    return rows


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, PDF_NAME)
    if not os.path.isfile(pdf_path):
        print(f"错误: 找不到 {PDF_NAME}")
        sys.exit(1)

    rows = extract(pdf_path)
    out_path = os.path.join(script_dir, OUTPUT)

    # 去重（同页跨行合并导致的重复）
    seen = set()
    unique = []
    for r in rows:
        key = f"{r['一级分类']}|{r['二级分类']}|{r['三级分类']}"
        if key not in seen:
            seen.add(key)
            unique.append(r)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"提取完成: {len(unique)} 条记录 → {out_path}")
    # 打印分类统计
    l1_count = {}
    for r in unique:
        l1_count[r["一级分类"]] = l1_count.get(r["一级分类"], 0) + 1
    for k, v in l1_count.items():
        print(f"  {k}: {v} 条")
