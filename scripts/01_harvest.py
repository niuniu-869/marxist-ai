#!/usr/bin/env python3
"""
01_harvest.py —— 抓 marxists.org/chinese 的马恩列斯文集

策略：
- 编码：网页声明 gb2312，实际是 gb18030 超集 → 统一用 gb18030 解码
- 限速：单线程，每请求 1.2-1.8s（站点是志愿者维护，不能并发）
- 缓存：raw HTML 永远不重复抓（除非 --force）
- 范围：4 位作者 index.htm 中"著作"区域（不抓 PDF/书信/参考）

输出：
- data/raw/<author>/<slug>.html  —— 已转 UTF-8 的 raw
- data/raw/manifest.json         —— 索引：author/title/url/local_path/year/priority
"""

import json
import os
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests

BASE = "https://www.marxists.org/chinese/"
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
MANIFEST = RAW_DIR / "manifest.json"
USER_AGENT = "Mozilla/5.0 (Marxist_ai research; xuejia.xue@students.mq.edu.au)"

AUTHORS = {
    "marx":   {"index": "marx/index.htm",   "name": "马克思"},
    "engels": {"index": "engels/index.htm", "name": "恩格斯"},
    "lenin":  {"index": "lenin/index.htm",  "name": "列宁"},
    "stalin": {"index": "stalin/index.htm", "name": "斯大林"},
}

# 优先抓的核心文献（slug 关键词）—— 这些先跑，断点失败时优先保住核心产出
PRIORITY_KEYWORDS = [
    # 马克思
    "1845", "feuerbach", "1844", "communist", "01.htm", "06.htm", "1875",
    "1847-1849", "1851-1852", "capital", "1850", "1871", "manifesto", "gotha",
    # 恩格斯
    "anti-duhring", "duhring", "ludwig", "ursprung", "utopian", "scientific",
    "anti", "naturedialektik", "feuerbach-ende",
    # 列宁
    "state-revolution", "imperialism", "what-to-be-done", "1917", "1916", "1902",
    "two-tactics", "leftwing", "materialism-empiriocriticism",
    # 斯大林
    "leninism", "dialectical", "historical-materialism",
]


def fetch(url: str, sleep_min: float = 1.2, sleep_max: float = 1.8) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            time.sleep(random.uniform(sleep_min, sleep_max))
            return resp.content
        except Exception as e:
            print(f"  ! fetch failed ({attempt+1}/3) {url}: {e}")
            time.sleep(5)
    raise RuntimeError(f"fetch failed after 3 retries: {url}")


def decode(data: bytes) -> str:
    return data.decode("gb18030", errors="replace")


def slug_from_url(url: str) -> str:
    # 取 url 末段 + 去扩展名
    path = url.replace(BASE, "").replace("https://www.marxists.org/chinese/", "")
    path = path.replace("/", "_").replace(".htm", "").replace(".html", "")
    # 移除非法文件名字符
    path = re.sub(r'[^a-zA-Z0-9._\-]', '_', path)
    return path[:200]  # 文件名长度限制


def parse_index(author_id: str, html: str, base_url: str) -> list[dict]:
    """从作者 index.htm 抽取所有文章链接"""
    items = []
    # 简单粗暴地抓 <a href="...">...</a>(年份)
    # 排除：图片链接、外站、PDF、index 自身、参考链接（biography/review）
    pattern = re.compile(
        r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE
    )
    seen = set()
    for m in pattern.finditer(html):
        href = m.group(1).strip()
        title_html = m.group(2).strip()
        # 去掉嵌套标签
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        title = re.sub(r'\s+', ' ', title)
        if not title or len(title) < 2:
            continue
        # 过滤
        if href.startswith("#") or href.startswith("mailto:"):
            continue
        if any(x in href for x in [".pdf", ".chm", ".jpg", ".png", ".gif", "javascript:"]):
            continue
        if href.startswith("http") and "marxists.org/chinese" not in href:
            continue
        # 跳过 index/biography/memory/review 等导航
        if any(x in href.lower() for x in [
            "index.htm", "/pdf/", "/abc/", "/memory/", "/review/", "biography",
            "feed.xml", "search/", "who_we_are", "whoweare/", "../index", "rss"
        ]):
            continue
        # 跳过非 .htm/.html
        if not (href.endswith(".htm") or href.endswith(".html") or href.endswith("/")):
            continue
        # 跳过返回上级
        if href in ["..", "../", "/"]:
            continue
        full_url = urljoin(base_url, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        # 提取年份（从前后文）
        # 简单做法：title 后跟着 (YYYY...)
        year = None
        ctx_start = max(0, m.start() - 50)
        ctx_end = min(len(html), m.end() + 200)
        ctx = html[ctx_start:ctx_end]
        ym = re.search(r'(\d{4})\s*年', ctx)
        if ym:
            year = int(ym.group(1))
        # 优先级
        priority = 1
        for kw in PRIORITY_KEYWORDS:
            if kw in href.lower() or kw in title:
                priority = 0
                break
        items.append({
            "author": author_id,
            "title": title,
            "url": full_url,
            "year": year,
            "priority": priority,
        })
    return items


def main():
    force = "--force" in sys.argv
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    if MANIFEST.exists() and not force:
        manifest = json.loads(MANIFEST.read_text("utf-8"))
        print(f"已存在 manifest，{len(manifest)} 条；--force 重抓")

    # Step 1: 抓 4 个作者 index
    all_items = []
    for aid, info in AUTHORS.items():
        idx_url = BASE + info["index"]
        idx_path = RAW_DIR / aid / "_index.html"
        if idx_path.exists() and not force:
            print(f"[index][{aid}] 已抓，跳过")
            html = idx_path.read_text("utf-8")
        else:
            print(f"[index][{aid}] 抓 {idx_url}")
            try:
                html = decode(fetch(idx_url))
                idx_path.parent.mkdir(parents=True, exist_ok=True)
                idx_path.write_text(html, "utf-8")
            except Exception as e:
                print(f"  ! index fetch failed: {e}")
                continue
        items = parse_index(aid, html, idx_url)
        print(f"  → 抽到 {len(items)} 条链接")
        all_items.extend(items)

    # Step 2: 按优先级排序
    all_items.sort(key=lambda x: (x["priority"], x["author"], -(x["year"] or 0)))
    print(f"\n总计 {len(all_items)} 条候选；优先级 0（核心）{sum(1 for x in all_items if x['priority']==0)} 条\n")

    # Step 3: 逐个抓
    new_count = 0
    for i, item in enumerate(all_items):
        slug = slug_from_url(item["url"])
        local_path = RAW_DIR / item["author"] / f"{slug}.html"
        item["local_path"] = str(local_path.relative_to(ROOT))

        if local_path.exists() and not force:
            # 已抓过，跳过但保留 manifest
            manifest.append(item)
            continue

        print(f"[{i+1}/{len(all_items)}] {item['author']} | {item['title'][:60]}")
        try:
            data = fetch(item["url"])
            text = decode(data)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(text, "utf-8")
            manifest.append(item)
            new_count += 1
            # 每抓 20 篇落一次 manifest
            if new_count % 20 == 0:
                MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), "utf-8")
        except Exception as e:
            print(f"  ! failed: {e}")
            continue

    # 去重 manifest（按 url）
    seen_urls = set()
    dedup = []
    for it in manifest:
        if it["url"] in seen_urls:
            continue
        seen_urls.add(it["url"])
        dedup.append(it)
    MANIFEST.write_text(json.dumps(dedup, ensure_ascii=False, indent=2), "utf-8")
    print(f"\n抓取完成：新增 {new_count}，manifest 共 {len(dedup)} 条")


if __name__ == "__main__":
    main()
