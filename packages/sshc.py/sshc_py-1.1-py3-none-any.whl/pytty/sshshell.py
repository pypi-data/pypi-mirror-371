import os
import json
import threading
import tkinter as tk
from tkinter import messagebox
import getpass

# -------------------- 檔案路徑 --------------------
save_json = os.path.join(os.getcwd(), "sshinfo.json")

# -------------------- 公用函式 --------------------
def save_config(host, port, user, password):
    data = {"host": host, "port": port, "user": user, "password": password}
    with open(save_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_config():
    if not os.path.exists(save_json):
        return None
    try:
        with open(save_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def warn_terminal(root=None):
    """提醒使用者檢查終端訊息"""
    if root:  # GUI 模式
        messagebox.showwarning("提醒", "請檢查終端訊息", parent=root)
    else:      # CLI 模式
        print("[警告] 請檢查終端訊息")

# -------------------- SSH 執行 --------------------
def run_ssh(host, port, user):
    if not port.isdigit():
        port = "22"
    ssh_command = f"ssh {host} -l {user} -p {port}"
    os.system(ssh_command)

def summon_command_and_run(host, port, user):
    threading.Thread(target=run_ssh, args=(host, port, user), daemon=True).start()

# -------------------- CLI 模式 --------------------
def cli_mode():
    data = load_config()
    if data:
        use_saved = input(f"偵測到存檔 {data['host']}:{data['port']}，是否使用? (y/n): ").strip().lower()
        if use_saved in ["y", "yes"]:
            summon_command_and_run(data["host"], data["port"], data["user"])
            warn_terminal()  # 提醒查看終端訊息
            return

    host = input("請輸入 SSH 主機地址: ").strip()
    port = input("請輸入 SSH 連接阜號 (預設22): ").strip() or "22"
    user = input("請輸入 SSH 使用者名稱: ").strip()
    passwd = getpass.getpass("請輸入 SSH 使用者密碼: ").strip()

    save_choice = input("是否儲存設定 (y/n)? ").strip().lower()
    if save_choice in ["y", "yes", "ok", "1", "true"]:
        save_config(host, port, user, passwd)
        print("[OK] 設定已儲存到 sshinfo.json")
         # CLI 提醒

    summon_command_and_run(host, port, user)
    warn_terminal()

# -------------------- GUI 模式 --------------------
def gui_mode():
    root = tk.Tk()
    root.title("SSH 連線工具")
    root.geometry("600x400")

    tk.Label(root, text="Host").grid(row=0, column=0)
    tk.Label(root, text="Port").grid(row=1, column=0)
    tk.Label(root, text="User").grid(row=2, column=0)
    tk.Label(root, text="Password").grid(row=3, column=0)

    host_entry = tk.Entry(root)
    port_entry = tk.Entry(root)
    user_entry = tk.Entry(root)
    passwd_entry = tk.Entry(root, show="#")
    
    host_entry.grid(row=0, column=1)
    port_entry.grid(row=1, column=1)
    user_entry.grid(row=2, column=1)
    passwd_entry.grid(row=3, column=1)

    # 嘗試自動載入存檔
    data = load_config()
    if data:
        host_entry.insert(0, data.get("host", ""))
        port_entry.insert(0, data.get("port", "22"))
        user_entry.insert(0, data.get("user", ""))
        passwd_entry.insert(0, data.get("password", ""))

    def save_btn():
        save_config(host_entry.get(), port_entry.get(), user_entry.get(), passwd_entry.get())
        messagebox.showinfo("成功", "設定已儲存！")
        
    def close_window():
        root.withdraw()
    def load_btn():
        data = load_config()
        if not data:
            messagebox.showerror("錯誤", "沒有找到設定檔！")
            return
        host_entry.delete(0, tk.END); host_entry.insert(0, data.get("host", ""))
        port_entry.delete(0, tk.END); port_entry.insert(0, data.get("port", "22"))
        user_entry.delete(0, tk.END); user_entry.insert(0, data.get("user", ""))
        passwd_entry.delete(0, tk.END); passwd_entry.insert(0, data.get("password", ""))
        messagebox.showinfo("成功", "已載入設定檔")
        

    def connect_btn():
        summon_command_and_run(host_entry.get().strip(),
                               port_entry.get().strip(),
                               user_entry.get().strip())
        warn_terminal(root)
        close_window()

    tk.Button(root, text="存檔", command=save_btn).grid(row=4, column=0)
    tk.Button(root, text="載入存檔", command=load_btn).grid(row=4, column=1)
    tk.Button(root, text="連線", command=connect_btn).grid(row=5, column=0, columnspan=2)

    root.mainloop()


def reget():
    # 重新顯示 GUI 視窗
    import tkinter as tk
    try:
        root = tk._default_root
        if root:
            root.deiconify()
    except Exception:
        pass

# -------------------- 主程式 --------------------
def run():    
    print("請選擇模式：")
    print("1. CLI 模式")
    print("2. GUI 模式")
    mode = input("> ").strip()

    if mode == "1":
        try:
            cli_mode()
        except KeyboardInterrupt as e:
            print("error")
            exit()
    elif mode == "2":
        try:
            gui_mode()
        except KeyboardInterrupt as e:
            print("error")
            reget()
    else:
        print("無效的模式")
    exit()
if __name__ == "__main__":
    run()