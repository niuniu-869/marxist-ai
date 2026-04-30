#!/usr/bin/env python3
"""
sync_frontend_data.py —— 把 data/books/marxists/documents/* 同步到 frontend/public/data/

输出：
  frontend/public/data/index.json          —— 4 个作者卡片
  frontend/public/data/<author>/list.json  —— 作者下文章列表（按年份）
  frontend/public/data/<author>/<id>.json  —— 单文章全量（给文章页）

为减小 build 体积，list.json 只保留 id/title/year/tldr_modern。
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "data" / "books" / "marxists" / "documents"
OUT_DIR = ROOT / "frontend" / "public" / "data"

AUTHORS = [
    {
        "id": "marx",
        "name": "马克思",
        "name_en": "Karl Marx",
        "lifespan": "1818 – 1883",
        "intro": "德国哲学家、政治经济学家。和恩格斯一起，把社会主义思想从空想推进到对资本主义运行规律的系统分析。",
        "key_works": ["《资本论》", "《1844 经济学哲学手稿》", "《关于费尔巴哈的提纲》", "《共产党宣言》"],
    },
    {
        "id": "engels",
        "name": "恩格斯",
        "name_en": "Friedrich Engels",
        "lifespan": "1820 – 1895",
        "intro": "马克思一生的合作者，《资本论》第二、三卷在他手里成书。也是《家庭、私有制和国家的起源》《反杜林论》的作者。",
        "key_works": ["《反杜林论》", "《家庭、私有制和国家的起源》", "《社会主义从空想到科学的发展》"],
    },
    {
        "id": "lenin",
        "name": "列宁",
        "name_en": "Vladimir Lenin",
        "lifespan": "1870 – 1924",
        "intro": "把马克思主义带进 20 世纪。在帝国主义阶段重写了革命策略，1917 年俄国革命的核心理论家。",
        "key_works": ["《国家与革命》", "《帝国主义是资本主义的最高阶段》", "《怎么办？》"],
    },
    {
        "id": "stalin",
        "name": "斯大林",
        "name_en": "Joseph Stalin",
        "lifespan": "1878 – 1953",
        "intro": "苏联第二代领导人，把列宁主义系统化成教科书形态。本站只收他的理论文献。",
        "key_works": ["《论列宁主义基础》", "《辩证唯物主义和历史唯物主义》"],
    },
]


def slim_for_list(doc: dict) -> dict:
    m = doc.get("meta", {}) or {}
    return {
        "id": Path(doc["id"]).stem if doc.get("id") else None,
        "file": doc["__file"],
        "title": doc.get("title", ""),
        "title_local": doc.get("title_local"),
        "year": doc.get("year"),
        "tldr_modern": m.get("tldr_modern", ""),
        "primary_category": m.get("primary_category"),
        "polemic_count": len(m.get("polemic_targets", [])),
        "para_count": len(doc.get("paragraphs", [])),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 写 index.json
    index = {"authors": []}
    for a in AUTHORS:
        a_dir = DOCS_DIR / a["id"]
        n = len(list(a_dir.glob("*.json"))) if a_dir.exists() else 0
        index["authors"].append({**a, "doc_count": n})
    (OUT_DIR / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), "utf-8")

    # 每作者：写 list.json + 每篇 <id>.json
    total_docs = 0
    for a in AUTHORS:
        aid = a["id"]
        src = DOCS_DIR / aid
        dst = OUT_DIR / aid
        dst.mkdir(parents=True, exist_ok=True)
        # 清空旧文件
        for old in dst.glob("*.json"):
            old.unlink()

        items = []
        if src.exists():
            for jf in sorted(src.glob("*.json")):
                try:
                    doc = json.loads(jf.read_text("utf-8"))
                except Exception:
                    continue
                doc["__file"] = jf.stem
                # 写单文件（前端文章页读）
                shutil.copy(jf, dst / jf.name)
                items.append(slim_for_list(doc))
                total_docs += 1
        # 按年份升序（强转 int 容错）
        def _y(x):
            y = x.get("year")
            if isinstance(y, int): return y
            try: return int(str(y))
            except Exception: return 0
        items.sort(key=lambda x: (_y(x), x.get("title") or ""))
        (dst / "list.json").write_text(json.dumps({"author": a, "items": items}, ensure_ascii=False, indent=2), "utf-8")

    print(f"sync_frontend_data: {total_docs} docs synced to {OUT_DIR}")


if __name__ == "__main__":
    main()
