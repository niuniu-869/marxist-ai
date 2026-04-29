#!/usr/bin/env python3
"""
01b_split.py —— HTML 正文清洗 + 段落切分 + 单页多文献切分

输出：data/intermediate/01b_split/<author>/<slug>.json
{
  "_prompt_version": "...",
  "source_url": "...",
  "title": "...",
  "author": "...",
  "year": ...,
  "is_multi_doc": false,         // 整页只有一个文献
  "subdocs": [                   // 多个文献时拆开
    {
      "subdoc_id": "1845_marx_original",
      "label": "马克思 1845 原始稿本",
      "title_local": "...",
      "paragraphs": [
        { "n": 1, "original_html": "...", "original_plain": "..." }
      ],
      "footnotes_text": "...",
      "provenance_text": "..."
    }
  ]
}

切分启发式：
- HTML 转纯文本（保留 <i><b><em><strong> 强调标记）
- 顶级标题 (h1-h3) 视为新 subdoc 开端
- 段首 　　 (两个全角空格) 是马列旧译典型段首；据此切段
- "卡·马克思写于..." / "原文是..." / "选自《...》" 触发 provenance 块
- "[1]" "[2]" 编号注释 → 收集到 footnotes
- 提纲式（"一" "二" ... "十一"）按数字标题切段
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "intermediate" / "01b_split"
MANIFEST = RAW_DIR / "manifest.json"

sys.path.insert(0, str(Path(__file__).parent))
from prompts import PROMPT_VERSION  # noqa: E402

# 段落分隔标记（旧译典型）
PARA_LEADING = "　　"  # 两个全角空格
# 强调标签保留
KEEP_TAGS = re.compile(r'<(/)?(?:i|b|em|strong|u)\b[^>]*>', re.IGNORECASE)
ANY_TAG = re.compile(r'<[^>]+>')


def html_entities(text: str) -> str:
    """常见 HTML 实体替换"""
    repl = {
        "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&#160;": " ",
        "&ldquo;": "“", "&rdquo;": "”",
        "&lsquo;": "‘", "&rsquo;": "’",
        "&hellip;": "…", "&middot;": "·",
        "&mdash;": "—", "&ndash;": "–",
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    # 数字实体
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
    # 残留 &xxx; 不识别就丢
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    return text


def clean_html(html: str) -> str:
    """提取 <body>，去掉无关 block，保留强调标签"""
    # 取 body 内容
    bm = re.search(r'<body[^>]*>(.*?)</body>', html, re.IGNORECASE | re.DOTALL)
    if bm:
        html = bm.group(1)
    # 去 script/style/nav 等
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<noscript\b[^>]*>.*?</noscript>', '', html, flags=re.IGNORECASE | re.DOTALL)
    return html


def html_to_paragraphs(html: str) -> list[dict]:
    """分段：把 <p>/<br><br>/<pre> 切开。保留强调标签为简化标记。"""
    html = html_entities(html)
    # 把 <br> <br/> 当段分隔
    html = re.sub(r'<br\s*/?>\s*<br\s*/?>', '\n\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    # </p> 段分隔
    html = re.sub(r'</p\s*>', '\n\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<p[^>]*>', '\n\n', html, flags=re.IGNORECASE)
    # </h\d> 段分隔（heading 文本本身保留，前后断段）
    html = re.sub(r'</h\d\s*>', '\n\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<h\d[^>]*>', '\n\n', html, flags=re.IGNORECASE)
    # </tr> 段分隔
    html = re.sub(r'</(?:tr|li)\s*>', '\n', html, flags=re.IGNORECASE)
    # 简化强调标签
    html = re.sub(r'<(?:i|em)\b[^>]*>', '<em>', html, flags=re.IGNORECASE)
    html = re.sub(r'</(?:i|em)\s*>', '</em>', html, flags=re.IGNORECASE)
    html = re.sub(r'<(?:b|strong)\b[^>]*>', '<strong>', html, flags=re.IGNORECASE)
    html = re.sub(r'</(?:b|strong)\s*>', '</strong>', html, flags=re.IGNORECASE)
    html = re.sub(r'<u\b[^>]*>', '<u>', html, flags=re.IGNORECASE)
    html = re.sub(r'</u\s*>', '</u>', html, flags=re.IGNORECASE)
    # 其他所有标签去掉
    html = re.sub(r'<(?!/?(?:em|strong|u)\b)[^>]+>', '', html, flags=re.IGNORECASE)

    # 切段
    paras = re.split(r'\n\s*\n+', html)
    out = []
    for p in paras:
        text = p.strip()
        if not text:
            continue
        # 去除两端 &nbsp; 等等已处理
        # 纯文本（用于 LLM）：去掉强调标签
        plain = re.sub(r'</?(?:em|strong|u)\s*>', '', text)
        plain = re.sub(r'\s+', ' ', plain).strip()
        if len(plain) < 2:
            continue
        out.append({
            "original_html": text,
            "original_plain": plain,
        })
    return out


# 单页多文献切分启发式：寻找版本/章节标题
SUBDOC_HEADING_PATTERNS = [
    # 关于费尔巴哈的提纲
    (r'^关于费尔巴哈的提纲(?:\[1\])?$', '1845_marx_original', '马克思 1845 年原始稿本'),
    (r'^马克思论费尔巴哈$', '1888_engels', '恩格斯 1888 年整理发表版'),
    # 共产党宣言
    (r'^\d+年[德俄英波意法]文版序言', None, None),
    (r'^一、资产者和无产者$', 'manifesto_ch1', '第一章 资产者和无产者'),
    (r'^二、无产者和共产党人$', 'manifesto_ch2', '第二章 无产者和共产党人'),
    (r'^三、社会主义的和共产主义的文献$', 'manifesto_ch3', '第三章 社会主义的和共产主义的文献'),
    (r'^四、共产党人对各种反对党派的态度$', 'manifesto_ch4', '第四章 共产党人对各种反对党派的态度'),
    (r'^人名索引$', 'persons_index', '人名索引'),
    # 哥达纲领批判
    (r'^[Ⅰ一]$', None, None),
]


def detect_subdoc_starts(paras: list[dict]) -> list[tuple[int, str, str]]:
    """检测段落级 subdoc 起点。返回 [(para_idx, subdoc_id, label), ...]"""
    starts = []
    for i, p in enumerate(paras):
        plain = p["original_plain"]
        for pat, sid, label in SUBDOC_HEADING_PATTERNS:
            m = re.match(pat, plain)
            if m:
                # 自动 ID
                if sid is None:
                    sid = f"section_{i:03d}_" + re.sub(r'[^a-zA-Z0-9_]', '_', plain)[:30]
                if label is None:
                    label = plain[:50]
                starts.append((i, sid, label))
                break
    return starts


def extract_provenance_text(paras: list[dict]) -> tuple[str, list[int]]:
    """识别 provenance 块（写作时间/出处/原文语言/选自《...》）。返回 (text, indices_to_remove)"""
    keywords = [
        "写于", "原文是", "原文为德文", "选自《", "载于", "首次发表",
        "中文马克思主义文库", "人民出版社", "马克思恩格斯全集", "马克思恩格斯选集",
        "列宁全集", "列宁选集", "斯大林全集",
    ]
    indices = []
    parts = []
    for i, p in enumerate(paras):
        plain = p["original_plain"]
        if any(kw in plain for kw in keywords) and len(plain) < 300:
            indices.append(i)
            parts.append(plain)
    return "\n".join(parts), indices


def extract_footnotes(paras: list[dict]) -> tuple[list[dict], list[int]]:
    """识别页脚 [1] [2] 注释。返回 (footnotes, indices_to_remove)"""
    fns = []
    indices = []
    fn_pat = re.compile(r'^\[(\d+)\]\s*(.+)', re.DOTALL)
    for i, p in enumerate(paras):
        plain = p["original_plain"]
        m = fn_pat.match(plain)
        if m:
            n = int(m.group(1))
            text = m.group(2).strip()
            # 通常 footnote 在文末
            fns.append({"n": n, "text": text})
            indices.append(i)
    return fns, indices


def split_one(html_path: Path, manifest_item: dict) -> dict:
    html = html_path.read_text("utf-8")
    html = clean_html(html)
    paras = html_to_paragraphs(html)
    # 过滤过短或导航类
    filtered = []
    nav_words = {"中文马克思主义文库", "马克思", "恩格斯", "列宁", "斯大林",
                 "马克思 恩格斯", "马克思　恩格斯", "->", "-&gt;",
                 "首页", "返回", "上一页", "下一页", "目录", "返回目录"}
    for p in paras:
        plain = p["original_plain"]
        if plain in nav_words:
            continue
        if re.match(r'^\s*[\->·　\s]+\s*$', plain):
            continue
        if len(plain) < 2:
            continue
        # 过滤纯英文 metadata
        if plain.startswith("Karl Marx") or plain.startswith("Lenin") or plain.startswith("Engels"):
            if len(plain) < 50:
                continue
        filtered.append(p)

    # 找 subdoc 起点
    subdoc_starts = detect_subdoc_starts(filtered)

    # provenance & footnotes
    prov_text, prov_idx = extract_provenance_text(filtered)
    fns, fn_idx = extract_footnotes(filtered)
    skip_indices = set(prov_idx) | set(fn_idx)

    # 构建 subdocs
    if not subdoc_starts:
        # 单文献模式：所有段落归一篇
        body_paras = []
        for i, p in enumerate(filtered):
            if i in skip_indices:
                continue
            body_paras.append({
                "n": len(body_paras) + 1,
                "original_html": p["original_html"],
                "original_plain": p["original_plain"],
            })
        subdocs = [{
            "subdoc_id": "main",
            "label": manifest_item["title"],
            "title_local": manifest_item["title"],
            "paragraphs": body_paras,
            "footnotes": fns,
            "provenance_text": prov_text,
        }]
    else:
        # 多文献：按 subdoc_starts 切片
        subdocs = []
        # 把 starts 按 idx 排序，相邻 start 之间是同一 subdoc
        n_paras = len(filtered)
        for k, (s_idx, s_id, s_label) in enumerate(subdoc_starts):
            next_idx = subdoc_starts[k + 1][0] if k + 1 < len(subdoc_starts) else n_paras
            chunk = []
            for j in range(s_idx + 1, next_idx):  # 跳过标题段本身
                if j in skip_indices:
                    continue
                p = filtered[j]
                chunk.append({
                    "n": len(chunk) + 1,
                    "original_html": p["original_html"],
                    "original_plain": p["original_plain"],
                })
            subdocs.append({
                "subdoc_id": s_id,
                "label": s_label,
                "title_local": filtered[s_idx]["original_plain"],
                "paragraphs": chunk,
                "footnotes": fns if k == 0 else [],  # footnotes 通常归第一段
                "provenance_text": prov_text if k == 0 else "",
            })

    return {
        "_prompt_version": PROMPT_VERSION,
        "source_url": manifest_item["url"],
        "author": manifest_item["author"],
        "title": manifest_item["title"],
        "year": manifest_item.get("year"),
        "is_multi_doc": len(subdocs) > 1,
        "subdocs": subdocs,
    }


def main():
    if not MANIFEST.exists():
        print("ERR: 先跑 01_harvest.py")
        sys.exit(1)
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ok, skip, fail = 0, 0, 0
    for item in manifest:
        local_path = ROOT / item["local_path"]
        if not local_path.exists():
            continue
        out_path = OUT_DIR / item["author"] / (local_path.stem + ".json")
        if out_path.exists():
            try:
                existing = json.loads(out_path.read_text("utf-8"))
                if existing.get("_prompt_version") == PROMPT_VERSION:
                    skip += 1
                    continue
            except Exception:
                pass
        try:
            result = split_one(local_path, item)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), "utf-8")
            ok += 1
        except Exception as e:
            print(f"  ! split failed {item['title'][:40]}: {e}")
            fail += 1
    print(f"split: ok={ok} skip={skip} fail={fail}")


if __name__ == "__main__":
    main()
