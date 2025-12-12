import os
import torch
import faiss
import pickle
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
#FAQ_03 = index2
from Embedding import get_embeddings

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os
from dotenv import load_dotenv
# ----------------------------
# LINE BOT 設定
# ----------------------------
# 讀取 .env（如果有）
load_dotenv()

# 從環境變數讀取
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise ValueError("請先在環境變數或 .env 裡設定 CHANNEL_ACCESS_TOKEN 和 CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)

# --- 路徑設定 ---
BASE_DIR = os.path.dirname(__file__)  # src 底下
TRN_DIR = os.path.join(BASE_DIR, "../data/translate")
INDEX_DIR = os.path.join(BASE_DIR, "../data/index")

# FAISS 與 chunks 存檔
faiss_index_file = os.path.join(INDEX_DIR, "index.faiss")
chunks_pickle_file = os.path.join(INDEX_DIR, "chunks.pkl")

# ----------------------------
# 載入 FAISS 檔案
# ----------------------------
index = faiss.read_index(faiss_index_file)
with open(chunks_pickle_file, "rb") as f:
    translated_chunks = pickle.load(f)
print(f"✅ FAISS 已讀入（{index.ntotal} 筆）")


# ----------------------------
# RAG 搜尋函式
# ----------------------------
def search(query, top_k=3):
    query_emb = get_embeddings([query])
    distances, ids = index.search(query_emb, top_k)
    context = "\n".join([translated_chunks[i] for i in ids[0]])
    return context

# ----------------------------
# LINE Webhook 路由
# ----------------------------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# ----------------------------
# 處理文字訊息事件
# ----------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    print(f"🗨️ 使用者問題: {user_msg}")

    try:
		    #這邊可以客製化調整
		    #目前是調用search處理使用者的問題，取得檢索內容
        answer = search(user_msg, top_k=3)
        reply = answer[:1000]  # LINE 限制訊息長度
    except Exception as e:
        reply = f"發生錯誤：{str(e)}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ----------------------------
# 主程式入口
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
