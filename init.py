"""
findata-classify 技能初始化脚本

首次使用前运行： python init.py [--url PDF下载地址]

功能：
  1. 检查 PyMuPDF 依赖
  2. 下载 PDF（如缺失）
  3. 调用 build_knowledge.py 提取全部结构化知识库（6 个 JSON 文件）
  4. 验证完整性
"""
import os, sys, subprocess, urllib.request

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
KNOW_DIR = os.path.join(SKILL_DIR, "knowledge")
PDF_PATH = os.path.join(SKILL_DIR, "金融信息服务数据分类分级指南.pdf")
PDF_FILENAME = "金融信息服务数据分类分级指南.pdf"
DEFAULT_URL = "https://www.cac.gov.cn/rootimages/uploadimg/1783104513081660/1783104513081660.pdf"

REQUIRED = {
    "authoritative.json": "附录A 67条分类记录",
    "terms.json": "术语定义（Section 3）",
    "impact_matrix.json": "影响程度判定表（表1）",
    "grade_matrix.json": "数据级别判定标准（表2）",
    "category_framework.json": "分类框架描述（Section 4）",
    "grading_rules.json": "分级规则（Sections 5.2-5.6, 6）",
}


def log(msg):
    print(f"  [OK] {msg}")


def err(msg):
    print(f"  [X] {msg}")


# =============================================================
# 1) 依赖检查
# =============================================================

def check_deps():
    try:
        import fitz
        return True
    except ImportError:
        print("需要安装 PyMuPDF 才能从 PDF 提取知识库。")
        ans = input("是否现在安装？(y/n): ").strip().lower()
        if ans == "y":
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
            log("PyMuPDF 安装完成")
            return True
        err("请手动执行: pip install pymupdf")
        return False


# =============================================================
# 2) PDF 下载
# =============================================================

def download_pdf(url):
    print(f"\n正在下载 PDF（约 1-2 MB）...")
    print(f"  来源: {url}")
    try:
        urllib.request.urlretrieve(url, PDF_PATH)
        size = os.path.getsize(PDF_PATH)
        log(f"下载完成: {PDF_FILENAME} ({size/1024:.0f} KB)")
        return True
    except Exception as e:
        err(f"下载失败: {e}")
        print(f"默认下载地址可能已失效。请使用 WebSearch / WebFetch 能力搜索")
        print(f"「金融信息服务数据分类分级指南 PDF 国信办通字〔2026〕2号」")
        print(f"找到有效下载链接后，将 PDF 保存到: {PDF_PATH}")
        print(f"然后重新运行本脚本： python \"{__file__}\"")
        return False


def ensure_pdf(url):
    if os.path.isfile(PDF_PATH):
        log(f"PDF 已存在: {PDF_FILENAME} ({os.path.getsize(PDF_PATH)/1024:.0f} KB)")
        return True
    return download_pdf(url)


# =============================================================
# 3) 验证
# =============================================================

def verify():
    print("\n--- 验证 ---")
    all_ok = True
    for name, desc in REQUIRED.items():
        path = os.path.join(KNOW_DIR, name)
        if os.path.isfile(path):
            log(f"{name}: {os.path.getsize(path):,} bytes")
        else:
            err(f"{name}: 缺失")
            all_ok = False
    return all_ok


# =============================================================
# main
# =============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="findata-classify 技能初始化")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"PDF 下载地址")
    args = parser.parse_args()

    print("=" * 50)
    print("findata-classify 技能初始化")
    print("=" * 50)

    if not check_deps():
        sys.exit(1)

    if not ensure_pdf(args.url):
        sys.exit(1)

    # 委托 build_knowledge.py 执行提取
    build_script = os.path.join(SKILL_DIR, "build_knowledge.py")
    if os.path.isfile(build_script):
        print(f"\n--- 调用 build_knowledge.py ---")
        result = subprocess.run(
            [sys.executable, build_script],
            cwd=SKILL_DIR,
            capture_output=True,
            text=True,
        )
        # 透传 build_knowledge 的输出
        for line in result.stdout.split("\n"):
            if line.strip():
                print(f"  {line.strip()}")
        if result.stderr.strip():
            print(f"  stderr: {result.stderr.strip()}")
        if result.returncode != 0:
            err("build_knowledge.py 执行失败")
            sys.exit(1)
    else:
        err(f"找不到 {build_script}")
        sys.exit(1)

    if verify():
        print("\n知识库初始化完成。现在可以使用技能了。")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
