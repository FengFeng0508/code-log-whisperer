# 👻 Code-Log-Whisperer (代码报错翻译官)

> **Stop pasting errors. Let AI whisper the fix.**
> 告别繁琐的复制粘贴，让 AI 成为你的专属 Debug 助手。

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey.svg)]()

当你面对晦涩冗长的系统报错、Traceback 或内存溢出日志时，还在手动打开浏览器问 AI 吗？
**Code-Log-Whisperer** 是一个极度轻量级的后台守护程序。只需**复制**报错文本，它便会在后台静默呼叫大模型，并在屏幕中央弹出“大白话”诊断结果与修复建议。

![演示GIF占位符](https://via.placeholder.com/800x400?text=Replace+this+with+your+demo+GIF)
*(💡 建议在这里录制一张 GIF：演示你复制了一段代码报错，几秒后屏幕弹出清晰中文建议的全过程。)*

## ✨ 核心特性 (Features)

- 🚀 **Zero-Click 无缝触发：** 后台静默监听剪贴板，检测到 `Traceback` 等报错关键词立即触发，绝不打断你的心流。
- 🧠 **大白话翻译：** 将复杂的异常堆栈翻译成直接的代码修复建议。
- 🔌 **万能模型适配：** 原生兼容 OpenAI 接口规范，一键切换 DeepSeek、Kimi、通义千问等，更完美支持 **Ollama 本地私有模型**。
- ☕ **极致轻量：** 依托系统托盘 (System Tray) 运行，内存占用极低，随时通过右键菜单彻底退出。

## 📦 快速启动 (Quick Start)

### 方式一：直接运行 (推荐普通用户)
进入 [Releases](#) 页面，下载最新打包好的 `.exe` 或 Mac 应用，双击即可运行。首次启动将引导你配置 API Key。

### 方式二：通过源码运行 (推荐开发者)

**1. 克隆仓库**
```bash
git clone [https://github.com/yourusername/code-log-whisperer.git](https://github.com/yourusername/code-log-whisperer.git)
cd code-log-whisperer