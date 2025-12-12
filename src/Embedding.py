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

