import os
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np

from tqdm import tqdm
import pickle

# ----------------------------
# 1. 載入向量模型 (bge-large-zh)
# ----------------------------
embed_model_name = "BAAI/bge-large-zh"
embed_tokenizer = AutoTokenizer.from_pretrained(embed_model_name)
embed_model = AutoModel.from_pretrained(embed_model_name)

# --- 路徑設定 ---
BASE_DIR = os.path.dirname(__file__)  # src 底下
TRN_DIR = os.path.join(BASE_DIR, "../data/translate")
INDEX_DIR = os.path.join(BASE_DIR, "../data/index")

# 確保資料夾存在
os.makedirs(TRN_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# FAISS 與 chunks 存檔
faiss_index_file = os.path.join(INDEX_DIR, "index.faiss")
chunks_pickle_file = os.path.join(INDEX_DIR, "chunks.pkl")

def get_embeddings(texts, batch_size=8):
    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Embedding 批次處理中"):
        batch = texts[i:i+batch_size]
        inputs = embed_tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = embed_model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :]  # CLS 向量
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        all_embeddings.append(embeddings.cpu().numpy())
    return np.vstack(all_embeddings)

def build_faiss_index(embeddings, texts):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

# ----------------------------
# 2. 主流程：讀取翻譯後檔案，建立 FAISS 索引
# ----------------------------

# 來源翻譯檔
translated_file = os.path.join(TRN_DIR, "X10-4K_translated.txt")

with open(translated_file, "r", encoding="utf-8") as f:
    translated_chunks = [line.strip() for line in f if line.strip()]

embeddings = get_embeddings(translated_chunks)
index = build_faiss_index(embeddings, translated_chunks)

print("已建立 RAG 資料庫")
print(f"總共 {len(translated_chunks)} 個片段被索引")

# ----------------------------
# 2-1. 將RAG資料庫存成檔案
# ----------------------------


faiss.write_index(index, faiss_index_file)
with open(chunks_pickle_file,"wb") as f:
    pickle.dump(translated_chunks, f)

print("✅ 已存檔：my_index.faiss + chunks.pkl")


# ----------------------------
# 3. 測試檢索
# ----------------------------
def search(query, top_k=3):
    query_emb = get_embeddings([query])
    distances, ids = index.search(query_emb, top_k)
    results = [translated_chunks[i] for i in ids[0]]
    return results

# 測試
query = "如何遠端控制？"
results = search(query, top_k=3)
print("檢索結果:")
for r in results:
    print("-", r)