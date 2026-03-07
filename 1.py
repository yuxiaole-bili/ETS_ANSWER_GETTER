import os
import sys
import shutil
import subprocess
import json
from tkinter import messagebox, Tk

def resource_path(relative_path):
    """获取打包后资源文件的路径（兼容开发环境和 PyInstaller 打包后）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def get_roaming_path():
    home = os.path.expanduser("~")
    return os.path.join(home, "AppData", "Roaming", "ETS")

def find_interpreter():
    for cmd in ['py', 'python']:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
            return cmd
        except:
            continue
    return 'python'

def create_shortcut(target, arguments, working_dir, shortcut_path, icon_path=None):
    ps_script = f'''
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target}'
$Shortcut.Arguments = '{arguments}'
$Shortcut.WorkingDirectory = '{working_dir}'
'''
    if icon_path and os.path.exists(icon_path):
        ps_script += f'$Shortcut.IconLocation = "{icon_path},0"\n'
    ps_script += '$Shortcut.Save()'
    try:
        subprocess.run(['powershell', '-Command', ps_script], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror('快捷方式创建失败', f'错误输出：{e.stderr}')
        raise

def get_version_from_json(json_path):
    """从 info.json 读取版本号，返回版本字符串或 None"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('ver', '0.0.0')
    except Exception:
        return None

def main():
    # 1. 获取当前安装包的版本
    current_json_path = resource_path('info.json')
    if not os.path.exists(current_json_path):
        messagebox.showerror('错误', '内部资源缺失：info.json')
        return
    current_version = get_version_from_json(current_json_path)
    if current_version is None:
        messagebox.showerror('错误', '无法读取当前版本信息')
        return

    # 2. 目标目录
    target_dir = get_roaming_path()
    installed_json_path = os.path.join(target_dir, 'info.json')
    installed_version = None
    if os.path.exists(installed_json_path):
        installed_version = get_version_from_json(installed_json_path)

    # 3. 版本比较逻辑
    action = "install"  # 默认执行安装
    if installed_version:
        # 简单版本比较（字符串比较，建议使用 packaging.version 更严谨，但这里简化）
        if current_version > installed_version:
            action = "upgrade"
            proceed = messagebox.askyesno("发现新版本", 
                f"当前版本：{current_version}\n已安装版本：{installed_version}\n是否升级？")
        elif current_version < installed_version:
            proceed = messagebox.askyesno("版本更旧", 
                f"当前版本：{current_version}\n已安装版本：{installed_version}\n您正在安装旧版本，是否继续？")
        else:
            proceed = messagebox.askyesno("版本相同", 
                f"当前版本：{current_version}\n已安装版本：{installed_version}\n版本相同，是否重新安装？")
        if not proceed:
            return  # 用户取消
    else:
        # 首次安装，直接询问
        if not messagebox.askyesno("安装确认", f"将安装 E听说答案提取 版本 {current_version}，是否继续？"):
            return

    # 4. 原有的安装逻辑（复制文件、创建快捷方式等）
    files_to_extract = ['启动E听说答案提取.py', 'E听说答案提取.py', '教程.txt', 'diary.txt', 'ETS.ico', 'info.json']
    os.makedirs(target_dir, exist_ok=True)

    for filename in files_to_extract:
        src = resource_path(filename)
        dst = os.path.join(target_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            messagebox.showwarning('警告', f'文件 {filename} 未找到，将跳过复制。')

    interpreter = find_interpreter()
    script_path = os.path.join(target_dir, '启动E听说答案提取.py')
    shortcut_path = os.path.join(get_desktop_path(), 'E听说答案提取.lnk')
    icon_path = os.path.join(target_dir, 'ETS.ico')

    try:
        create_shortcut(interpreter, f'"{script_path}"', target_dir, shortcut_path, icon_path)
    except Exception as e:
        messagebox.showerror('错误', f'创建快捷方式失败：{e}')
        return

    # 打开教程文件（首次安装或升级时打开）
    tutorial_path = os.path.join(target_dir, '教程.txt')
    if os.path.exists(tutorial_path):
        os.startfile(tutorial_path)

    root = Tk()
    root.withdraw()
    if messagebox.askyesno('安装完成', '程序已安装/更新到 Roaming 目录，并创建了桌面快捷方式。是否立即运行？'):
        subprocess.Popen([interpreter, script_path], cwd=target_dir)
    root.destroy()

if __name__ == '__main__':
    main()