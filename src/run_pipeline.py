import subprocess
import sys
import os
import time

def run_script(script_name, wait_for_completion=True):
    """
    執行 Python script 的輔助函式
    """
    print(f"\n{'='*10} 正在執行: {script_name} {'='*10}")
    
    # 取得目前檔案所在的目錄 (src)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, script_name)

    if not os.path.exists(script_path):
        print(f"❌ 錯誤: 找不到檔案 {script_name}")
        return False

    try:
        # 使用目前的 python 解譯器執行
        if wait_for_completion:
            result = subprocess.run([sys.executable, script_path], check=True)
            if result.returncode == 0:
                print(f"✅ {script_name} 執行成功！")
                return True
            else:
                print(f"❌ {script_name} 執行失敗 (Code: {result.returncode})")
                return False
        else:
            # 用於啟動 Server (不會自動結束)
            process = subprocess.Popen([sys.executable, script_path])
            print(f"🚀 {script_name} 已啟動 (PID: {process.pid})")
            return process
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 執行 {script_name} 時發生錯誤:\n{e}")
        return False

def main():
    print("🚀 開始執行 QA Robot 自動化流程...")

    # Step 1: 翻譯
    print("\n--- 步驟 1: 翻譯文件 (Translate.py) ---")
    if not run_script("Translate.py"):
        print("❌ 翻譯失敗，流程終止。")
        return

    # Step 2: 建立索引
    print("\n--- 步驟 2: 建立向量索引 (FAISS.py) ---")
    if not run_script("FAISS.py"):
        print("❌ 建立索引失敗，流程終止。")
        return

    # Step 3: 啟動 Line Bot Server
    print("\n--- 步驟 3: 啟動 Line Bot Server (QA_LINE_Robot.py) ---")
    print("⚠️  請確保你已經開啟 ngrok 並設定好 Webhook URL")
    print("⚠️  按下 Ctrl+C 可停止服務")
    
    server_process = run_script("QA_LINE_Robot.py", wait_for_completion=False)

    try:
        # 讓主程式持續運行，直到使用者按下 Ctrl+C
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服務...")
        server_process.terminate()
        print("✅ 服務已關閉。")

if __name__ == "__main__":
    main()