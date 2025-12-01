from fastapi import FastAPI, Query, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import Any, Dict

from .seo_analyzer import fetch_html, analyze_html

#型態定義
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

#網站渲染
templates = Jinja2Templates(directory="templates")


#網站狀態檢查
@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


# ========== JSON API 版本 ==========
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


# ========== 網頁版：表單 + 結果 ==========
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # 一開始只顯示表單，沒有結果
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "error": None,
            "input_url": "",
        },
    )


@app.post("/analyze_form", response_class=HTMLResponse)
async def analyze_form(request: Request, url: str = Form(...)):
    # 這裡處理使用者從表單送出的網址，並回傳網頁
    try:
        # 先用 Pydantic 檢查網址格式
        valid_url = HttpUrl(url)  # 這行會在格式錯誤時丟錯
    except ValidationError:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error": "網址格式不正確，請確認是否包含 http:// 或 https://",
                "input_url": url,
            },
        )

    try:
        html = fetch_html(str(valid_url)) #目前是用request獲取
        result: Dict[str, Any] = analyze_html(str(valid_url), html) #分析方法
        result["basic_suggestions"] = [
            s for s in result.get("basic_suggestions", []) if s
        ]
        return templates.TemplateResponse(  #渲染網頁
            "index.html",
            {
                "request": request,
                "result": result,
                "error": None,
                "input_url": str(valid_url),
            },
        )
    except Exception as e:
        # 這裡捕捉 requests error / parsing error 等
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error": f"分析失敗：{e}",
                "input_url": str(valid_url),
            },
        )