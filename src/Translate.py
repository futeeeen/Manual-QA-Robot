import os
from transformers import MarianMTModel, MarianTokenizer
import torch

# ----------------------------
# 1. 載入翻譯模型 (英文 → 中文)
# ----------------------------
model_name = "Helsinki-NLP/opus-mt-en-zh"
tokenizer_mt = MarianTokenizer.from_pretrained(model_name)
model_mt = MarianMTModel.from_pretrained(model_name)

def translate_to_zh(texts, batch_size=8):
    translations = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        inputs = tokenizer_mt(batch, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            translated = model_mt.generate(**inputs, max_length=512)
        translations += [tokenizer_mt.decode(t, skip_special_tokens=True) for t in translated]
    return translations

# ----------------------------
# 2. 主流程：讀取英文 user guide, 翻譯成中文
# ----------------------------

# 取得目前檔案的目錄
BASE_DIR = os.path.dirname(__file__)

# 拼出 data 資料夾的路徑
file_path = os.path.join(BASE_DIR, "../data/X10-4K.txt")

with open(file_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

# 簡單切段
chunks = [raw_text[i:i+300] for i in range(0, len(raw_text), 300)]

# 翻譯成中文
translated_chunks = translate_to_zh(chunks)

# 拼出 data 資料夾的路徑
output_path = os.path.join(BASE_DIR, "../data/translate/X10-4K_translated.txt")

# 確保資料夾存在
output_dir = os.path.dirname(output_path)
os.makedirs(output_dir, exist_ok=True)

# 存成檔案，給 FAISS 用
with open(output_path, "w", encoding="utf-8") as f:
    for t in translated_chunks:
        f.write(t + "\n")

print(f"翻譯完成，共 {len(translated_chunks)} 個片段，已存到 X10-4K_translated.txt")
