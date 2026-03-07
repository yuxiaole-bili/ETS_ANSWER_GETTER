###注释ai写的
# 这是一个用于启动和管理"E听说答案提取"程序的图形界面脚本
# 功能包括：启动/停止目标程序、删除题目文件、删除缓存文件、打开程序目录、设置、黑夜模式切换
###
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
import shutil
import subprocess
import sys
from tkinter import font
import winreg

current_dir = os.path.dirname(os.path.abspath(__file__))

ver = "未知"
try:
    with open('info.json', 'r', encoding='utf-8') as f:
        info = json.load(f)
        ver = info.get("ver", "未知")
    print(ver + "\n" + "—————BY yuxiaole_awa")
except:
    print("版本号识别失败")

if not os.path.exists('settings.json'):
    json_save_defaults = {
        "filixable": "defaults",
        "defaults": {"jiaoji": "8", "fushu": "4", "biaoda": "4"},
        "u_filixable": {"jiaoji": "", "fushu": "", "biaoda": ""},
        "theme": "light",
        "follow_system_theme": False
    }
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(json_save_defaults, f, ensure_ascii=False, indent=4)

process = None

light_colors = {
    'bg': '#f5f5f5',
    'fg': '#333333',
    'button_bg': '#e0e0e0',
    'button_fg': '#000000',
    'text_bg': '#ffffff',
    'text_fg': '#000000',
    'select_bg': '#0078d7',
    'select_fg': '#ffffff',
    'frame_bg': '#eaeaea',
}
dark_colors = {
    'bg': '#2d2d2d',
    'fg': '#f0f0f0',
    'button_bg': '#3c3c3c',
    'button_fg': '#ffffff',
    'text_bg': '#1e1e1e',
    'text_fg': '#cccccc',
    'select_bg': '#264f78',
    'select_fg': '#ffffff',
    'frame_bg': '#252525',
}
current_colors = light_colors

def get_system_theme():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return 'light' if value == 1 else 'dark'
    except:
        return 'light'

def load_theme_from_settings():
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
    follow_system = data.get('follow_system_theme', False)
    if follow_system:
        return get_system_theme()
    else:
        return data.get('theme', 'light')

def save_theme_settings(manual_theme, follow_system):
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
    data['theme'] = manual_theme
    data['follow_system_theme'] = follow_system
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def apply_colors(colors):
    global current_colors
    current_colors = colors
    event_s.configure(bg=colors['bg'])
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', background=colors['button_bg'], foreground=colors['button_fg'])
    style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
    style.configure('TFrame', background=colors['frame_bg'])
    
    def update_children(widget):
        try:
            if not isinstance(widget, ttk.Frame) and not isinstance(widget, ttk.Label) and not isinstance(widget, ttk.Button):
                widget.configure(bg=colors['bg'], fg=colors['fg'])
        except:
            pass
        for child in widget.winfo_children():
            update_children(child)
    update_children(event_s)
    
    # 更新所有设置窗口
    if hasattr(event_s, 'settings_windows'):
        for win in event_s.settings_windows:
            win.apply_colors(colors)
    
    event_s.update_idletasks()

def toggle_dark_mode():
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
    if data.get('follow_system_theme', False):
        messagebox.showinfo("提示", "当前为跟随系统主题模式，无法手动切换。\n请先在设置中关闭“跟随系统主题”。")
        return
    current_theme = data.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    new_colors = dark_colors if new_theme == 'dark' else light_colors
    apply_colors(new_colors)
    save_theme_settings(new_theme, False)

def on_focus_in(event):
    actual_theme = load_theme_from_settings()
    global current_colors
    expected_colors = dark_colors if actual_theme == 'dark' else light_colors
    if current_colors != expected_colors:
        apply_colors(expected_colors)

class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.title("设置")
        self.win.geometry("400x200")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()
        
        # 注册到父窗口
        if not hasattr(parent, 'settings_windows'):
            parent.settings_windows = []
        parent.settings_windows.append(self)
        
        self.jiaoji_var = tk.StringVar()
        self.fushu_var = tk.StringVar()
        self.follow_system_var = tk.BooleanVar()
        
        self.create_widgets()
        self.load_current_settings()
        # 应用当前主题
        self.apply_colors(current_colors)
        
    def create_widgets(self):
        row = 0
        ttk.Checkbutton(self.win, text="跟随系统主题（自动切换黑夜/白天）",
                        variable=self.follow_system_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        row += 1
        ttk.Separator(self.win, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1
        ttk.Button(self.win, text="重置所有设置", command=self.reset).grid(row=row, column=0, columnspan=2, pady=5, padx=5)
        row += 1
        ttk.Label(self.win, text="交际每题答案获取数:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(self.win, textvariable=self.jiaoji_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1
        ttk.Label(self.win, text="复述与表达每题答案获取数:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(self.win, textvariable=self.fushu_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1
        btn_frame = ttk.Frame(self.win)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="退出", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
    def load_current_settings(self):
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data['filixable'] == 'changed':
                self.jiaoji_var.set(data['u_filixable']['jiaoji'])
                self.fushu_var.set(data['u_filixable']['fushu'])
            else:
                self.jiaoji_var.set(data['defaults']['jiaoji'])
                self.fushu_var.set(data['defaults']['fushu'])
            self.follow_system_var.set(data.get('follow_system_theme', False))
        except:
            pass
    
    def reset(self):
        defaults = {"jiaoji": "8", "fushu": "4", "biaoda": "4"}
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            theme = data.get('theme', 'light')
            follow = data.get('follow_system_theme', False)
        except:
            theme = 'light'
            follow = False
        new_data = {
            "filixable": "defaults",
            "defaults": defaults,
            "u_filixable": {"jiaoji": "", "fushu": "", "biaoda": ""},
            "theme": theme,
            "follow_system_theme": follow
        }
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
        self.jiaoji_var.set(defaults['jiaoji'])
        self.fushu_var.set(defaults['fushu'])
        messagebox.showinfo("提示", "已重置为默认设置（主题设置保持不变）")
    
    def save(self):
        jiaoji = self.jiaoji_var.get().strip()
        fushu = self.fushu_var.get().strip()
        if not (jiaoji.isdigit() and fushu.isdigit()):
            messagebox.showerror("错误", "请输入数字")
            return
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
        theme = data.get('theme', 'light')
        data['filixable'] = 'changed'
        data.setdefault('u_filixable', {})
        data['u_filixable']['jiaoji'] = jiaoji
        data['u_filixable']['fushu'] = fushu
        data['u_filixable']['biaoda'] = "4"
        data['theme'] = theme
        data['follow_system_theme'] = self.follow_system_var.get()
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("提示", "保存成功")
        self.destroy()
    
    def destroy(self):
        # 从父窗口的列表中移除
        if hasattr(self.parent, 'settings_windows') and self in self.parent.settings_windows:
            self.parent.settings_windows.remove(self)
        self.win.destroy()
    
    def apply_colors(self, colors):
        # 应用颜色到本窗口的所有控件
        self.win.configure(bg=colors['bg'])
        def update_children(widget):
            try:
                if not isinstance(widget, ttk.Frame) and not isinstance(widget, ttk.Label) and not isinstance(widget, ttk.Button):
                    widget.configure(bg=colors['bg'], fg=colors['fg'])
            except:
                pass
            for child in widget.winfo_children():
                update_children(child)
        update_children(self.win)

def main():
    global process, event_s
    event_s = tk.Tk()
    event_s.title("E听说答案提取启动器")
    event_s.geometry("300x250")
    try:
        event_s.iconbitmap(default='ETS.ico')
    except:
        try:
            icon = tk.PhotoImage(file='ETS.png')
            event_s.iconphoto(True, icon)
        except:
            pass
    
    # 初始化设置窗口列表
    event_s.settings_windows = []
    
    try:
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10, family="微软雅黑")
    except:
        pass
    
    event_s.bind("<FocusIn>", on_focus_in)
    
    init_theme = load_theme_from_settings()
    global current_colors
    current_colors = dark_colors if init_theme == 'dark' else light_colors
    apply_colors(current_colors)
    
    title_label = ttk.Label(event_s, text=f"E听说答案提取启动器 v{ver}", font=('微软雅黑', 11, 'bold'))
    title_label.grid(row=0, column=0, columnspan=3, pady=10)
    
    author_label = ttk.Label(event_s, text="BY yuxiaole_awa", foreground='gray')
    author_label.grid(row=1, column=0, columnspan=3)
    
    buttons = [
        ("启动", run, 2, 0),
        ("停止", stop, 2, 1),
        ("🌙 黑夜模式", toggle_dark_mode, 2, 2),
        ("删除题目文件", lambda: delete_folder(current_dir), 3, 0),
        ("删除缓存文件", delete_file, 3, 1),
        ("打开ETS目录", open_folder, 3, 2),
        ("设置", settings, 4, 1),
    ]
    
    for text, cmd, row, col in buttons:
        btn = ttk.Button(event_s, text=text, command=cmd)
        btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
    
    for i in range(3):
        event_s.columnconfigure(i, weight=1)
    event_s.grid_rowconfigure(5, weight=1)
    
    event_s.mainloop()

def run():
    global process
    target_file = os.path.join(current_dir, "E听说答案提取.py")
    try:
        process = subprocess.Popen([sys.executable, target_file])
    except Exception as e:
        messagebox.showerror("错误", f"启动失败: {e}")

def stop():
    global process
    if process and process.poll() is None:
        process.terminate()
        process = None
        messagebox.showinfo("提示", "已停止")
        
    else:
        messagebox.showinfo("提示", "程序未运行")
    event_s.destroy()
def delete_folder(root_dir):
    if not messagebox.askyesno("确认", "确定删除所有题目文件？该操作不可逆！"):
        return
    deleted = []
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and item.isdigit():
            try:
                shutil.rmtree(item_path)
                deleted.append(item)
            except Exception as e:
                print(f"删除失败 {item_path}: {e}")
    if deleted:
        messagebox.showinfo("提示", f"已删除目录:\n" + "\n".join(deleted))
    else:
        messagebox.showinfo("提示", "未找到数字命名的目录")

def delete_file():
    deleted = []
    for fname in ["ETS答案.txt", "log.log"]:
        fpath = os.path.join(current_dir, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
                deleted.append(fname)
            except Exception as e:
                print(f"删除失败 {fpath}: {e}")
    if deleted:
        messagebox.showinfo("提示", f"已删除文件:\n" + "\n".join(deleted))
    else:
        messagebox.showinfo("提示", "没有需要删除的缓存文件")

def open_folder():
    os.startfile(current_dir)

def settings():
    SettingsWindow(event_s)
if __name__ == "__main__":
    main()