import re
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup


def fetch_html(url: str, timeout: int = 10) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_text(soup: BeautifulSoup) -> str:
    # 去掉 script / style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    # 簡單壓縮空白
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def analyze_html(url: str, html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = desc_tag.get("content", "").strip() if desc_tag else None

    canonical_tag = soup.find("link", rel="canonical")
    canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else None

    h1_tags: List[str] = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2_tags: List[str] = [h.get_text(strip=True) for h in soup.find_all("h2")]

    # 計算字數
    text = extract_text(soup)
    words = [w for w in re.split(r"\s+", text) if w]
    word_count = len(words)

    # 沒有 alt 的圖片數量
    img_tags = soup.find_all("img")
    img_without_alt = [
        img for img in img_tags
        if not img.get("alt") or not img.get("alt").strip()
    ]

    # 簡單建議：title、description 長度
    def length_score(text: Optional[str], min_len: int, max_len: int) -> str:
        if text is None:
            return "missing"
        n = len(text)
        if n < min_len:
            return f"too_short ({n})"
        if n > max_len:
            return f"too_long ({n})"
        return f"good ({n})"

    return {
        "url": url,
        "title": title,
        "title_length": len(title) if title else 0,
        "title_length_score": length_score(title, 20, 60),

        "meta_description": meta_description,
        "meta_description_length": len(meta_description) if meta_description else 0,
        "meta_description_length_score": length_score(meta_description, 50, 160),

        "canonical_url": canonical_url,
        "h1_tags": h1_tags,
        "h2_tags": h2_tags,
        "word_count": word_count,
        "images_total": len(img_tags),
        "images_without_alt": len(img_without_alt),

        # "basic_suggestions": [
        #     "Add a <title> tag." if not title else "",
        #     "Add a meta description." if not meta_description else "",
        #     "Use 1 main <h1> for the core topic." if len(h1_tags) == 0 else "",
        #     "Reduce number of <h1> tags to 1–2." if len(h1_tags) > 2 else "",
        #     "Add alt text to important images." if len(img_without_alt) > 0 else "",
        # ],
        "basic_suggestions": [
            "請加入 <title> 標題標籤。" if not title else "",
            "請加入 meta description（頁面描述）。" if not meta_description else "",
            "建議至少使用 1 個主要的 <h1> 來定義頁面主題。" if len(h1_tags) == 0 else "",
            "建議將 <h1> 標籤數量控制在 1～2 個之間。" if len(h1_tags) > 2 else "",
            "建議為重要圖片加入 alt 說明文字。" if len(img_without_alt) > 0 else "",
        ],

    }