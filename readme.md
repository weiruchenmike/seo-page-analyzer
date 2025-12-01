# SEO Page Analyzer

一個簡易的 FastAPI 項目，用於分析任何給定 URL 的頁面基本 SEO 資訊。

## Features

- 取得頁面 HTML

- 提取 `<title>` 標籤、元描述和規格 URL

- 收集所有 `<h1>` / `<h2>` 標籤文本

- 統計頁面字數

- 統計不含 `alt` 標籤的圖片數量

- 為標題和描述提供簡單的長度評分

- JSON API + Swagger UI

檢測 :
    1. <title> 標題標籤。
    2. <meta description>（頁面描述）。
    3. 主要的 <h1> 來定義頁面主題 並計算 <h1> 數量。
    4. 圖片是否有 alt 說明文字
    
## Quick Start

```bash
- 安裝套件 : pip install -r requirements.txt
- 在該專案資料夾啟動 : uvicorn app.main:app --reload
- 在瀏覽器輸入 : http://127.0.0.1:8000/analyze?url={url} 就可以得到對應分析資料 {url} 為你想要分析網址
- http://127.0.0.1:8000/docs 會有圖形化介面可以做使用
# 後來有做成網頁版
- http://127.0.0.1:8000/