from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Any, Dict

from .seo_analyzer import fetch_html, analyze_html


class SEOAnalysisResponse(BaseModel):
    url: HttpUrl
    title: str | None
    title_length: int
    title_length_score: str

    meta_description: str | None
    meta_description_length: int
    meta_description_length_score: str

    canonical_url: str | None
    h1_tags: list[str]
    h2_tags: list[str]
    word_count: int
    images_total: int
    images_without_alt: int
    basic_suggestions: list[str]


app = FastAPI(
    title="SEO Page Analyzer",
    description="Simple API for analyzing basic on-page SEO info.",
    version="0.1.0",
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/analyze", response_model=SEOAnalysisResponse)
def analyze(url: HttpUrl = Query(..., description="Page URL to analyze")):
    try:
        html = fetch_html(str(url))
        result: Dict[str, Any] = analyze_html(str(url), html)
        # 移除空字串建議
        result["basic_suggestions"] = [
            s for s in result.get("basic_suggestions", []) if s
        ]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))