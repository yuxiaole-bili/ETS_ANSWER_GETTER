# E听说答案提取

[![Windows](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/yuxiaole-bili/ETS_ANSWER_GETTER)
[![Release](https://img.shields.io/github/v/release/yuxiaole-bili/ETS_ANSWER_GETTER)](https://github.com/yuxiaole-bili/ETS_ANSWER_GETTER/releases)

一个用于提取 **E听说（ETS）** 练习题本地答案的图形化工具。支持自动解析题目缓存文件，提取交际、复述与表达等题型答案，并提供个性化设置、深色模式以及**一键卸载**功能。

**✨ 现已提供一键安装程序**：内置嵌入式 Python 3.10 环境，无需用户安装 Python，下载安装后即可直接运行。

---

## 📦 下载与安装

### 方法一：一键安装（推荐）
1. 前往 [发布](https://github.com/yuxiaole-bili/ETS_ANSWER_GETTER/releases) 下载最新版安装包：`E听说答案提取_Setup_v1.0.0.exe`
2. 双击运行，按提示完成安装。
3. 安装结束后，桌面会自动生成“E听说答案提取”快捷方式，双击即可打开启动器。

### 方法二：源码运行（适合开发者）
1. 确保已安装 Python 3.6 或更高版本。
2. 克隆或下载本仓库所有文件到本地：
   ```bash
   git clone https://github.com/yuxiaole-bili/ETS_ANSWER_GETTER.git
   ```
3. 进入目录，运行 `启动E听说答案提取.py` 即可开始使用。

---

## 🗑️ 如何卸载

安装程序会自动在安装目录（`%AppData%\Roaming\ETS`）中生成 `uninstall.bat` 卸载脚本。**卸载方法**：
- 打开文件资源管理器，在地址栏输入 `%AppData%\Roaming\ETS` 并回车。
- 双击 `uninstall.bat`，按提示操作即可**彻底删除**所有程序文件、快捷方式及嵌入式 Python 环境。

---

## 🚀 快速上手

### 启动器界面
双击桌面快捷方式或运行 `启动E听说答案提取.py`，打开启动器（窗口大小 300×250）：

| 按钮 | 功能 |
|------|------|
| **启动** | 使用内置 Python 环境打开主程序（答案提取界面），**无控制台窗口** |
| **停止** | 关闭主程序并退出启动器 |
| **🌙 黑夜模式** | 手动切换深色/浅色主题 |
| **删除题目文件** | 删除当前目录下所有纯数字命名的文件夹（ETS 题目缓存） |
| **删除缓存文件** | 删除生成的 `ETS答案.txt` 和日志文件 `log.log` |
| **打开ETS目录** | 打开程序所在文件夹 |
| **设置** | 自定义答案数量、主题跟随等 |

### 主程序操作步骤
1. 在启动器中点击 **启动**，打开主窗口（标题“E听说答案提取”，大小 1000×600）。
2. 主程序自动扫描当前目录，顶部区域会显示所有可用的文件夹按钮（通常是 ETS 生成的数字文件夹）。
3. 点击对应的文件夹，程序开始解析其中的 JSON 文件。
4. 点击 **显示答案**，答案会显示在文本框中，并自动保存到 `ETS答案.txt`。
5. 如果文件夹内有多个题目，可点击 **继续** 查看下一题；点击 **退出** 关闭窗口。
6. 所有题目显示完毕后，点击 **重新开始** 返回文件夹选择界面。

---

## ⚙️ 设置说明

在启动器中点击 **设置** 打开设置窗口：

- **交际每题答案获取数**：控制“交际”题型每题显示的答案数量（默认 8）。
- **复述与表达每题答案获取数**：控制“复述”与“表达”题型每题显示的答案数量（默认 4）。
- **跟随系统主题**：勾选后，程序会自动跟随 Windows 系统主题切换深色/浅色模式。
- **重置所有设置**：恢复答案数量的默认值（主题设置不变）。

设置保存后立即生效。

---

## 📝 更新日志

### v1.0.0（稳定版）
- ✨ **新增一键卸载功能**：安装程序自动生成 `uninstall.bat` 脚本，双击即可彻底删除程序及所有相关文件。
- 🔧 **安装程序重构**：改用原生 Windows API 消息框，移除 Tkinter 依赖，安装更轻量可靠。
- 🚀 **无窗口启动**：桌面快捷方式直接使用 `pythonw.exe`，主程序启动不再弹出黑色控制台窗口。
- 🐛 **修复停止按钮错误**：修正 `process = Non` 拼写问题，避免启动器崩溃。
- 📝 **增加错误日志**：启动失败时记录详细堆栈到 `launcher_error.log`，便于排查。

（完整更新记录请查看仓库中的 [diary.txt](diary.txt)）

---

## ❓ 常见问题

**Q: 点击“显示答案”后没有反应？**  
A: 请确认选择的文件夹确实是 ETS 生成的题目文件夹（包含 `info.json`、`content2.json` 等文件）。若仍有问题，请查看同目录下的 `log.log` 日志文件。

**Q: 如何彻底卸载？**  
A: 打开 `%AppData%\Roaming\ETS` 目录，双击 `uninstall.bat` 即可。卸载脚本会自动终止 Python 进程、删除所有文件及桌面快捷方式。

**Q: 是否需要安装 Python？**  
A: 如果使用一键安装版（EXE），无需安装 Python（已内置）。如果使用源码运行，则需要 Python 3.6+。

**Q: 支持哪些题型？**  
A: 目前已测试支持“交际”、“复述”、“表达”等常见题型。如遇新题型无法提取，欢迎反馈。

---

## 👤 作者与反馈

- 作者：**YuXiaoLe_awe** (GitHub: [yuxiaole-bili](https://github.com/yuxiaole-bili))
- 项目主页：[ETS_ANSWER_GETTER](https://github.com/yuxiaole-bili/ETS_ANSWER_GETTER)
- 问题反馈：[议题](https://github.com/yuxiaole-bili/ETS_ANSWER_GETTER/issues)

---

## 📄 许可证

本项目基于 MIT 许可证开源。

---

**如果这个工具对你有帮助，欢迎在仓库主页点亮 ⭐ Star 支持一下！**
