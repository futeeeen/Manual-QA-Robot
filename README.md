# Manual QA Robot (RAG + Line Bot)

這是一個基於 **RAG (Retrieval-Augmented Generation)** 技術的自動問答機器人專案。
專案能夠讀取英文操作手冊 (`.txt`)，利用 AI 模型自動翻譯成中文，並建立向量索引資料庫。最後透過 **Line Bot** 介面，讓使用者能用自然語言查詢手冊內容。

---

## 📂 專案架構

```text
Manual-QA-Robot/
├── data/                  # [資料儲存區]
│   ├── X10-4K.txt         # 原始英文操作手冊
│   ├── translate/         # (自動生成) 翻譯後的中文手冊
│   └── index/             # (自動生成) FAISS 向量索引檔 (.faiss, .pkl)
├── src/                   # [程式碼區]
│   ├── Embedding.py       # 向量化模組 (BAAI/bge-large-zh)
│   ├── FAISS.py           # 建庫模組 (建立向量索引)
│   ├── Translate.py       # 翻譯模組 (Helsinki-NLP/opus-mt-en-zh)
│   ├── QA_LINE_Robot.py   # Line Bot Server (Flask)
│   └── run_pipeline.py    # 自動化執行腳本
├── .env                   # 環境變數設定檔 (需自行建立)
├── requirements.txt       # Python 套件依賴清單
└── README.md              # 專案說明文件
```

---

## 🛠️ 環境準備與安裝
### 1. 建立並啟動虛擬環境 (建議)
為了避免套件衝突，建議在專案根目錄下建立虛擬環境。

### 2. 安裝依賴套件
請確保 requirements.txt 位於當前目錄，執行以下指令安裝所有必要套件：

```Bash
pip install -r requirements.txt
```
主要套件包含： flask, line-bot-sdk (服務端), torch, transformers, sentencepiece (AI 模型), faiss-cpu (向量檢索)。

### 3. 安裝ngrok 並註冊 Line Bot
請參考document下的 "串接LINE BOT.pdf"


### 4. 設定環境變數 (.env)
請在專案根目錄或 src/ 資料夾下建立一個名為 .env 的檔案，內容如下：

```Ini, TOML
CHANNEL_ACCESS_TOKEN=你的LineBot_Channel_Access_Token
CHANNEL_SECRET=你的LineBot_Channel_Secret
```
這些資訊請從 Line Developers Console 取得。

## 🌐 Line Bot 與 Ngrok 連線設定
由於 Line Bot 需要公開的 HTTPS 網址才能傳送訊息給您的 Server，本地開發時需透過 ngrok 進行轉發。

### 1. 啟動 ngrok
開啟終端機，執行以下指令 (對應 Flask 預設 Port 5000)：

```Bash
ngrok http 5000
```

### 2. 取得 Forwarding URL
ngrok 啟動後，複製視窗中顯示的 HTTPS 網址，例如： https://abcd-123-456.ngrok-free.app

### 3. 設定 Line Developer Console
進入 Line Developers Console。

選擇您的 Provider 與 Channel。

切換到 Messaging API 分頁。

在 Webhook URL 欄位填入：

```Plaintext

https://你的ngrok網址/callback
```
(注意：網址後方必須加上 /callback，這是程式中設定的路由)

點擊 Verify 檢查連線是否成功。

開啟 Use webhook 功能。

## 🚀 執行專案
本專案提供 自動化腳本 與 手動分步執行 兩種方式。

### 方式 A：一鍵全自動執行 (推薦)
此腳本會自動檢查並依序執行：翻譯 -> 建立索引 -> 啟動 Line Bot Server。

#### 進入程式碼目錄：

```Bash
cd src
```
#### 執行自動化腳本：

```Bash
python run_pipeline.py
```
### 方式 B：手動分步執行
若需單獨測試特定階段，可依序執行：

#### 翻譯文件 (將英文手冊轉為中文)：

```Bash
python src/Translate.py
```
#### 建立向量索引 (將中文文本轉為向量資料庫)：

```Bash
python src/FAISS.py
```
#### 啟動問答服務 (開啟 Flask Server)：

```Bash
python src/QA_LINE_Robot.py
```



## 📝 程式功能詳解
### 1. Translate.py (文件翻譯)
模型：使用 Helsinki-NLP/opus-mt-en-zh 進行英翻中。

流程：讀取 data/X10-4K.txt，將長文本切分為片段 (chunks)，批次翻譯後存入 data/translate/。

### 2. Embedding.py (向量化核心)
模型：使用 BAAI/bge-large-zh，這是針對中文優化的 Embedding 模型。

功能：提供 get_embeddings() 函式，將文字輸入轉換為高維度的向量數值，供其他程式呼叫。

### 3. FAISS.py (建立索引)
流程：

讀取翻譯後的中文文本。

呼叫 Embedding.py 將文本轉為向量。

使用 Facebook 的 FAISS 套件建立高效搜尋索引 (IndexFlatL2)。

將索引檔 (index.faiss) 與對應的文字內容 (chunks.pkl) 儲存至 data/index/。

### 4. QA_LINE_Robot.py (問答服務)
框架：使用 Flask 架設 Web Server。

運作原理：

啟動時載入 FAISS 索引與 Pickle 文字檔。

當收到 Line 訊息 (/callback) 時，將使用者的問題轉為向量。

在 FAISS 資料庫中搜尋最相似的 3 個手冊片段。

將這些片段組合成回答，回傳給使用者。

### 5. run_pipeline.py (自動化腳本)
功能：流程控制腳本。利用 subprocess 依序執行上述 Python 程式，簡化操作步驟。
