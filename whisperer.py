import time
import pyperclip
import json
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from openai import OpenAI

# 导入系统托盘相关的库
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

CONFIG_FILE = "config.json"

PRESET_PROVIDERS = {
    "DeepSeek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "OpenAI": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "Kimi (月之暗面)": {"base_url": "https://api.moonshot.cn/v1", "model": "moonshot-v1-8k"},
    "通义千问 (阿里云)": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus"},
    "Ollama (本地部署)": {"base_url": "http://localhost:11434/v1", "model": "llama3"}
}


def get_or_set_config():
    """读取本地配置，如果没有则弹出高级配置面板"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
                if "model" in config and "base_url" in config:
                    return config
            except json.JSONDecodeError:
                pass

    config = {}

    def save_config():
        config["provider"] = provider_var.get()
        config["api_key"] = key_entry.get().strip()
        config["base_url"] = url_entry.get().strip()
        config["model"] = model_entry.get().strip()

        if not config["api_key"] and "localhost" not in config["base_url"]:
            messagebox.showwarning("提示", "非本地模型通常需要填写 API Key！")
            return

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f)
        setup_win.destroy()

    def on_provider_change(event):
        selected = provider_var.get()
        if selected in PRESET_PROVIDERS:
            url_entry.delete(0, tk.END)
            url_entry.insert(0, PRESET_PROVIDERS[selected]["base_url"])
            model_entry.delete(0, tk.END)
            model_entry.insert(0, PRESET_PROVIDERS[selected]["model"])

            if "localhost" in PRESET_PROVIDERS[selected]["base_url"]:
                key_entry.delete(0, tk.END)
                key_entry.insert(0, "无需API Key")
                key_entry.config(state="disabled")
            else:
                key_entry.config(state="normal")
                if key_entry.get() == "无需API Key":
                    key_entry.delete(0, tk.END)

    setup_win = tk.Tk()
    setup_win.title("⚙️ 首次配置 - Code-Log-Whisperer")
    setup_win.geometry("400x350")
    setup_win.eval('tk::PlaceWindow . center')

    tk.Label(setup_win, text="请配置您的大模型 API", font=("Arial", 12, "bold")).pack(pady=10)

    tk.Label(setup_win, text="选择服务商 (支持自定义):").pack(anchor="w", padx=20)
    provider_var = tk.StringVar()
    provider_combo = ttk.Combobox(setup_win, textvariable=provider_var, values=list(PRESET_PROVIDERS.keys()))
    provider_combo.pack(fill="x", padx=20, pady=5)
    provider_combo.bind("<<ComboboxSelected>>", on_provider_change)

    tk.Label(setup_win, text="Base URL:").pack(anchor="w", padx=20)
    url_entry = tk.Entry(setup_win)
    url_entry.pack(fill="x", padx=20, pady=5)

    tk.Label(setup_win, text="模型名称 (Model):").pack(anchor="w", padx=20)
    model_entry = tk.Entry(setup_win)
    model_entry.pack(fill="x", padx=20, pady=5)

    tk.Label(setup_win, text="API Key:").pack(anchor="w", padx=20)
    key_entry = tk.Entry(setup_win, show="*")
    key_entry.pack(fill="x", padx=20, pady=5)

    provider_combo.current(0)
    on_provider_change(None)

    tk.Button(setup_win, text="保存并启动", command=save_config, bg="#4CAF50", fg="white", font=("Arial", 10)).pack(
        pady=20)
    setup_win.mainloop()

    if not config:
        os._exit(0)
    return config


def show_result_popup(error_text, suggestion):
    """弹出结果窗口"""
    window = tk.Tk()
    window.title("💡 报错诊断结果")
    window.geometry("550x450")
    window.attributes('-topmost', True)

    lbl = tk.Label(window, text="检测到以下报错，这里是修复建议：", font=("Arial", 12, "bold"))
    lbl.pack(pady=10)

    text_area = tk.Text(window, wrap=tk.WORD, font=("Arial", 11), bg="#f5f5f5")
    text_area.pack(expand=True, fill=tk.BOTH, padx=15, pady=5)

    content = f"【原始报错】\n{error_text[:200]}...\n\n{'=' * 40}\n\n【诊断与修复】\n{suggestion}"
    text_area.insert(tk.END, content)
    text_area.config(state=tk.DISABLED)

    btn = tk.Button(window, text="明白了 (关闭窗口)", command=window.destroy, bg="#e0e0e0")
    btn.pack(pady=10)

    window.eval('tk::PlaceWindow . center')
    window.mainloop()


def analyze_error(config, error_text):
    api_key = config["api_key"]
    if not api_key or api_key == "无需API Key":
        api_key = "dummy_key_for_local"

    client = OpenAI(api_key=api_key, base_url=config["base_url"])
    prompt = f"你是一个资深的程序员。请用简短的'大白话'解释下面这段报错的原因，并给出直接的修复建议。不要长篇大论，直击痛点。\n报错内容：\n{error_text}"

    try:
        response = client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API 调用失败！请检查您的网络、Base URL 或 API Key。\n错误详情: {str(e)}"


# ================= 核心修改区域 =================

def clipboard_listener(config):
    """后台独立线程：负责静默监听剪贴板"""
    print("正在后台静默监听剪贴板...")
    last_copied = ""
    trigger_keywords = ["Traceback (most recent call last):", "Exception:", "Error:"]

    while True:
        try:
            current_clipboard = pyperclip.paste().strip()
            is_error = any(keyword in current_clipboard for keyword in trigger_keywords)

            if current_clipboard != last_copied and is_error:
                print(f"👀 检测到报错，正在呼叫 {config['model']}...")
                last_copied = current_clipboard
                suggestion = analyze_error(config, current_clipboard)
                # 触发弹窗
                threading.Thread(target=show_result_popup, args=(current_clipboard, suggestion)).start()
        except Exception:
            pass
        time.sleep(1)


def create_tray_image():
    """动态生成一个绿色的圆形小图标，表示程序在运行"""
    image = Image.new('RGB', (64, 64), color='black')
    dc = ImageDraw.Draw(image)
    # 涂黑背景并画一个绿色的圆
    image.paste((0, 0, 0), [0, 0, image.size[0], image.size[1]])
    dc.ellipse((16, 16, 48, 48), fill='green')
    return image


def quit_app(icon, item):
    """托盘右键菜单：退出程序"""
    print("🛑 正在彻底关闭 Code-Log-Whisperer...")
    icon.stop()
    os._exit(0)  # 强制杀掉包含监听线程在内的整个进程


def main():
    config = get_or_set_config()
    print(f"🚀 Code-Log-Whisperer V4.0 已启动！")
    print(f"当前模型: {config['model']}")

    # 1. 启动剪贴板监听线程 (设为守护线程，主程序退出时它也会退出)
    listener_thread = threading.Thread(target=clipboard_listener, args=(config,), daemon=True)
    listener_thread.start()

    # 2. 配置并启动系统任务栏托盘图标 (占用主线程)
    menu = pystray.Menu(
        item('监听中 (Code-Log-Whisperer)', lambda: None),  # 点击无反应，只做状态展示
        item('❌ 彻底退出', quit_app)
    )

    icon_image = create_tray_image()
    tray_icon = pystray.Icon("CodeLogWhisperer", icon_image, "报错翻译官正在运行", menu)

    print("👇 请查看右下角任务栏托盘，已生成运行图标。")
    tray_icon.run()  # 这行代码会阻塞主线程，维持托盘图标的显示


if __name__ == "__main__":
    main()