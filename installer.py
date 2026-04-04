import os
import sys
import json
import shutil
import subprocess
import ctypes
from ctypes import wintypes

# ---------- Windows 消息框 ----------
MB_OK = 0x00000000
MB_YESNO = 0x00000004
MB_ICONERROR = 0x00000010
MB_ICONQUESTION = 0x00000020
MB_ICONWARNING = 0x00000030
MB_ICONINFORMATION = 0x00000040
IDYES = 6
IDNO = 7

def show_msg(text, title, flags=MB_OK):
    return ctypes.windll.user32.MessageBoxW(0, text, title, flags)

def ask_yes_no(title, text):
    return show_msg(text, title, MB_YESNO | MB_ICONQUESTION) == IDYES

def show_error(title, text):
    show_msg(text, title, MB_OK | MB_ICONERROR)

def show_warning(title, text):
    show_msg(text, title, MB_OK | MB_ICONWARNING)

def show_info(title, text):
    show_msg(text, title, MB_OK | MB_ICONINFORMATION)

# ---------- 辅助函数 ----------
def copy_folder(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def get_roaming_path():
    return os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "ETS")

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
        show_error('快捷方式创建失败', f'错误输出：{e.stderr}')
        raise

def get_version_from_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('ver', '0.0.0')
    except:
        return None

# ---------- 主函数 ----------
def main():
    # 版本检查
    current_json_path = resource_path('info.json')
    if not os.path.exists(current_json_path):
        show_error('错误', '内部资源缺失：info.json')
        return
    current_version = get_version_from_json(current_json_path)
    if current_version is None:
        show_error('错误', '无法读取当前版本信息')
        return

    target_dir = get_roaming_path()
    installed_json_path = os.path.join(target_dir, 'info.json')
    installed_version = None
    if os.path.exists(installed_json_path):
        installed_version = get_version_from_json(installed_json_path)

    if installed_version:
        if current_version > installed_version:
            proceed = ask_yes_no("发现新版本", f"当前版本：{current_version}\n已安装版本：{installed_version}\n是否升级？")
        elif current_version < installed_version:
            proceed = ask_yes_no("版本更旧", f"当前版本：{current_version}\n已安装版本：{installed_version}\n您正在安装旧版本，是否继续？")
        else:
            proceed = ask_yes_no("版本相同", f"当前版本：{current_version}\n已安装版本：{installed_version}\n版本相同，是否重新安装？")
        if not proceed:
            return
    else:
        if not ask_yes_no("安装确认", f"将安装 E听说答案提取 版本 {current_version}，是否继续？"):
            return

    # 需要复制的文件/文件夹（包含嵌入式 python310）
    items_to_copy = [
        '启动E听说答案提取.py',
        'E听说答案提取.py',
        '教程.txt',
        'diary.txt',
        'ETS.ico',
        'info.json',
        'python310'
    ]

    os.makedirs(target_dir, exist_ok=True)

    for item in items_to_copy:
        src = resource_path(item)
        dst = os.path.join(target_dir, item)
        if os.path.isdir(src):
            copy_folder(src, dst)
        else:
            if os.path.exists(src):
                shutil.copy2(src, dst)
            else:
                show_warning('警告', f'文件 {item} 未找到，将跳过复制。')

    # 生成卸载脚本 uninstall.bat
        # 生成卸载脚本 uninstall.bat
    uninstall_bat_path = os.path.join(target_dir, 'uninstall.bat')
    with open(uninstall_bat_path, 'w', encoding='utf-8') as f:
        f.write(f'''@echo off
title 卸载 E听说答案提取

:: 请求管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在请求管理员权限...
    powershell start -verb runas '%0'
    exit
)

echo 正在卸载 E听说答案提取...

:: 终止可能正在运行的 Python 进程（启动器或主程序）
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1

:: 删除安装目录下的所有文件（保留卸载脚本自身，最后删除）
cd /d "%~dp0"
del /f /q "启动E听说答案提取.py" 2>nul
del /f /q "E听说答案提取.py" 2>nul
del /f /q "info.json" 2>nul
del /f /q "settings.json" 2>nul
del /f /q "教程.txt" 2>nul
del /f /q "diary.txt" 2>nul
del /f /q "ETS.ico" 2>nul

:: 删除 python310 文件夹（如果存在）
if exist "python310" (
    rmdir /s /q "python310" 2>nul
)

:: 删除桌面快捷方式
del /f /q "%USERPROFILE%\\Desktop\\E听说答案提取.lnk" 2>nul

:: 尝试删除卸载脚本自身
del /f /q "%~f0" 2>nul

:: 删除整个安装目录（如果为空）
cd ..
rmdir /q "%~n0" 2>nul

echo 卸载完成！按任意键退出...
pause >nul
''')

    # 使用嵌入式 python310 中的 pythonw.exe 创建快捷方式
    pythonw_path = os.path.join(target_dir, 'python310', 'pythonw.exe')
    if not os.path.exists(pythonw_path):
        pythonw_path = os.path.join(target_dir, 'python310', 'python.exe')
        if not os.path.exists(pythonw_path):
            show_error('错误', '嵌入式 Python 环境不完整，缺少 python.exe')
            return

    script_path = os.path.join(target_dir, '启动E听说答案提取.py')
    shortcut_path = os.path.join(get_desktop_path(), 'E听说答案提取.lnk')
    icon_path = os.path.join(target_dir, 'ETS.ico')
    try:
        create_shortcut(pythonw_path, f'"{script_path}"', target_dir, shortcut_path, icon_path)
    except Exception as e:
        show_error('错误', f'创建快捷方式失败：{e}')
        return

    # 打开教程文件
    tutorial_path = os.path.join(target_dir, '教程.txt')
    if os.path.exists(tutorial_path):
        os.startfile(tutorial_path)

    show_info("安装完毕", "安装完成，请从桌面快捷方式启动应用。\n如需卸载，请运行安装目录下的 uninstall.bat")

if __name__ == '__main__':
    main()