###注释ai写的
import tkinter as tk
from tkinter import messagebox
import json
import os
from functools import partial
import logging
from tkinter import ttk, font
import sys
import 启动E听说答案提取
import winreg  # 用于读取系统主题

logging.basicConfig(filename='log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
global jiaoji 
global fushu
global biaoda

try:
    with open('ETS答案.txt', 'r', encoding='utf-8') as f:
        pass
except:
    create_file = open('ETS答案.txt', 'w', encoding='utf-8')
    create_file.write("本文本为自动生成")

try:
    with open('info.json', 'r', encoding='utf-8') as f:
        info = json.load(f)   
        ver = info["ver"]
    print(ver + "\n" + "—————BY yuxiaole_awa")
except:
    print("版本号识别失败")
    pass

# 读取设置（含主题）
with open("settings.json", 'r', encoding='utf-8') as f:
    json_load = json.load(f)
    if json_load['filixable'] == 'defaults':
        print("默认设置")
        jiaoji = json_load['defaults']['jiaoji']
        fushu = json_load['defaults']['fushu']
        biaoda = json_load['defaults']['biaoda']
    elif json_load['filixable'] == 'changed':
        print("自定义设置")
        jiaoji = json_load['u_filixable']['jiaoji']
        fushu = json_load['u_filixable']['fushu']
        biaoda = json_load['u_filixable']['biaoda']

def floder_get():
    current_directory = os.getcwd()
    ets_directory = os.path.join(current_directory)
    list_dirs = []
    if not os.path.exists(ets_directory):
        print(f"ERROR:ETS目录不存在: {ets_directory}")

    for root, dir, files in os.walk(ets_directory):
        if 'common' in root.split(os.sep) or '.vscode' in root.split(os.sep) or 'pc_xst_dict' in root.split(os.sep):
            continue
        list_dirs.append(root) 

    filtered_dirs = []
    for dir in list_dirs:
        if dir.count(os.sep) - ets_directory.count(os.sep) == 1:
            for item in os.listdir(dir):
                full_path = os.path.join(dir, item)
            if os.path.isdir(full_path):
                filtered_dirs.append(dir)

    list_dirs = filtered_dirs

    try:
        for root, dirs in os.walk(ets_directory):
            pass
    except Exception as e:
        print(f"WARNING:无法遍历ETS目录: {e}")
    
    print("遍历目录", list_dirs)
    return list_dirs

# 声明全局变量
global content
global question_number
answer = []  # 存储答案的列表
event_answer = {}  # 存储事件答案的字典
files_temporary_data = dict()  # 存储临时文件数据的字典
folder_buttons = {}  # 存储文件夹按钮的字典

def select_folder(folder_path):
    if os.path.isdir(folder_path):
        global content
        content_temporary = []
        content_temporary.append(folder_path)
        content = json.dumps({"root": content_temporary}, ensure_ascii=False, indent=4)
        print("folder_path:", folder_path, "\n", "content:", content)
        messagebox.showinfo("提示", "文件夹路径有效正在解析JSON文件")
        
        # 隐藏文件夹选择相关控件，显示文本框
        folder_frame.pack_forget()
        refresh_btn.pack_forget()
        middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        files_temporary = []
                        
        sub_dirs = dict()
        for root, dirs, files in os.walk(folder_path):
            files_temporary.append(dirs)   
            tmparr = [os.path.join(root, d) for d in dirs]
            sub_dirs[folder_path] = tmparr
            for file in files:
                file_path = os.path.join(root, file)
                print("file_path:", file_path)
            break
    
        content = json.dumps(sub_dirs, ensure_ascii=False, indent=4)
        print(sub_dirs)
        sub_files = dict()

        global files_temporary_data
        
        for i in sub_dirs:
            for root, dirs, files in os.walk(i):
                for file in files:
                    if file.endswith('content2.json'):
                        file_path_json = os.path.join(root, file)  
                        os.chmod(folder_path, 0o644) 
                        with open(file_path_json, 'r', encoding='utf-8') as json_file:
                            data = json.load(json_file)
                        tmparr = data
                        sub_files[file_path_json] = tmparr 

                    elif file.endswith('info.json'):
                        file_path_json_locate = os.path.join(root, file)
                        os.chmod(folder_path, 0o644) 
                        with open(file_path_json_locate, 'r', encoding='utf-8') as json_file:
                            data = json.load(json_file)
                        with open(file_path_json, 'r', encoding='utf-8') as json_file:
                            data_s = json.load(json_file)
                        
                        if data[0]['code_id'] == 'askall':
                            files_temporary_data[file_path_json] = data_s
                        elif data[0]['code_id'] == 'value' and data[1]['code_id'] == 'pic1':
                            files_temporary_data[file_path_json] = data_s
                        elif data[0]['code_id'] == 'pic1':
                            files_temporary_data[file_path_json] = data_s    
    
        if len(files_temporary_data) < 3:
            question_type_helper = 0
            files_temporary_data = dict()
            for i in sub_dirs:
                for root, dirs, files in os.walk(i):
                    for file in files:
                        if file.endswith('content2.json'):
                            question_type_helper += 1
                            if question_type_helper > 5:
                                file_path_json = os.path.join(root, file)  
                                os.chmod(folder_path, 0o644) 
                                with open(file_path_json, 'r', encoding='utf-8') as json_file:
                                    data_s = json.load(json_file)
                                files_temporary_data[file_path_json] = data_s
            print("question_type_helper:", question_type_helper)

    global question_number
    question_number = 0
    content = json.dumps(files_temporary_data, ensure_ascii=False, indent=4)   
    os.chmod('log.log', 0o644)  
    logging.warning(content)
    
    event_buttom.grid(row=0, column=0, padx=5)

def dispaly():
    global content
    global event_answer
    global files_temporary_data
    global question_number
    event_answer_type = list(files_temporary_data.keys())
    
    event_answer = files_temporary_data[event_answer_type[question_number]]
    question_number += 1
    
    try:
        key_ft()
    except:
        try:
            key_reply()
        except Exception as e:
            messagebox.showerror("错误", f"无法解析JSON文件: {e}")
    
    os.chmod('ETS答案.txt', 0o644)
    with open('ETS答案.txt', 'a', encoding='utf-8') as f:
        f.write(''.join(answer))
    event_text.insert(tk.END, ''.join(answer))

    event_buttom.grid_remove()
    event_buttom_go_on.grid(row=0, column=1, padx=5)
    event_buttom_destroy.grid(row=0, column=2, padx=5)

    event.mainloop()

def key_reply():
    global fushu
    global answer
    std_list = event_answer['info']['std']
    answer = []
    n = 0
    for i in std_list:
        n += 1
        if n < float(fushu):
            answered = i['value']
            answered = f"\n第{n}个答案为: {answered}\n"
            answer.append(answered)
    return answer

def key_ft():
    global jiaoji
    global answer
    answer = []
    
    n_n = 0
    for question in event_answer['info']['question']:
        question_values = []
        n = 0
        n_n += 1
        answer.append('\n')
        n_n_inof = f"\n第{n_n}个问题"
        answer.append('-'*60)
        answer.append('\n')
        answer.append(n_n_inof)
        std_list = question['std']
        for item in std_list:
            n += 1
            if n < float(jiaoji):
                answered = item['value'].replace('</br>', '').replace('<br>', '').strip()
                question_values.append(answered)
                answered = f"\n第{n}个答案为: {answered}\n"
                answer.append(answered)

        answer.append('\n')
        answer.append('='*60)
    return answer

def go_on():
    if question_number < 3 and question_number > 0:
        try:
            event_text.delete('1.0', tk.END)
            dispaly()
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON解析错误: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"未知错误: {e}")
    else:
        event_buttom_go_on.grid_remove()
        event_buttom_restart.grid(row=0, column=3, padx=5)

def chose_folder():
    global list_dirs
    global folder_buttons

    for widget in folder_frame.winfo_children():
        widget.destroy()

    folder_buttons = dict()
    
    cols = 5
    row = 0
    col = 0
    
    for folder_path in list_dirs:
        folder_name = os.path.basename(folder_path)
        folder_button = tk.Button(folder_frame, width=10, height=2, text=folder_name,
                                   command=partial(select_folder, folder_path))
        folder_buttons[folder_path] = folder_button
        folder_button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        col += 1
        if col >= cols:
            col = 0
            row += 1
    
    for i in range(cols):
        folder_frame.columnconfigure(i, weight=1)
    
    folder_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
    refresh_btn.pack(side=tk.TOP, pady=5)
    middle_frame.pack_forget()
    
    event_buttom.grid_remove()
    event_buttom_go_on.grid_remove()
    event_buttom_destroy.grid_remove()
    event_buttom_restart.grid_remove()
    
    # 应用当前主题颜色到新创建的按钮
    apply_colors(current_colors)

def refresh_floders():
    global list_dirs
    global egg_fresh_foldertimes
    if floder_get() == list_dirs:
        egg_fresh_foldertimes += 1
    else:
        list_dirs = floder_get()
        chose_folder()
    if egg_fresh_foldertimes > 100:
        while True:
            messagebox.showwarning("你刷你麻痹！！！！！！！", "fuck u")
            messagebox.showinfo("测呐", "ублдок матьтво, а ну, иди сда,говHоcoБauьe! PemЙko mнenesrь? Tel, зacpaнeЩвоноЧий, Mать Tвo, a? Hy, MaW cma,пoпробуй менЯ трахнуты! Ятебйсамтрахнублгодок, онанист цертов„будь ть прокйытИди, идиот, трахать тебЯмве тво семьГовно собацье, Жлоб вонций,дерьмо, сукападла!Йди срда, мерзавец, негодЯй,гацИди сда, ты, говно, Жопа!")

def main():
    global list_dirs
    list_dirs = floder_get()
    chose_folder()
    event.mainloop()

def restart():
    try:
        启动E听说答案提取.run()
        event.destroy()
        logging.info("Tkinter 窗口已销毁")
        os._exit(0)
    except Exception as e:
        logging.error(f"重启失败: {e}")
        messagebox.showerror("错误", f"重启失败: {e}")

def apply_colors(colors):
    # 设置窗口背景
    event.configure(bg=colors['bg'])
    # 设置 ttk 样式
    style.configure('TButton', background=colors['button_bg'], foreground=colors['button_fg'])
    style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
    style.configure('TFrame', background=colors['frame_bg'])
    # 设置 Text 组件颜色
    event_text.configure(bg=colors['text_bg'], fg=colors['text_fg'],
                         selectbackground=colors['select_bg'],
                         selectforeground=colors['select_fg'])
    # 设置文件夹框架背景
    folder_frame.configure(bg=colors['bg'])
    # 设置所有文件夹按钮颜色
    for btn in folder_buttons.values():
        try:
            btn.configure(bg=colors['button_bg'], fg=colors['button_fg'])
        except:
            pass
    # 设置刷新按钮样式
    refresh_btn.configure(style='TButton')
    # 设置顶部标签
    event_cf_label.configure(background=colors['bg'], foreground=colors['fg'])
    # 递归更新其他 tk 控件
    def update_children(widget):
        try:
            if widget not in folder_buttons.values() and not isinstance(widget, ttk.Frame):
                widget.configure(bg=colors['bg'], fg=colors['fg'])
        except:
            pass
        for child in widget.winfo_children():
            update_children(child)
    update_children(event)
    event.update()

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

def on_focus_in(event):
    actual_theme = load_theme_from_settings()
    global current_colors
    expected_colors = dark_colors if actual_theme == 'dark' else light_colors
    if current_colors != expected_colors:
        apply_colors(expected_colors)

# 创建Tkinter窗口
event = tk.Tk()
style = ttk.Style()
style.theme_use('clam')
event.title("E听说答案提取")
event.geometry("1000x600")

# 顶部标签
top_frame = ttk.Frame(event)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
event_cf_label = ttk.Label(top_frame, text="请选择目标文件夹", font=('微软雅黑', 12))
event_cf_label.pack()

# 文件夹选择按钮框架
folder_frame = tk.Frame(event, bg='#f5f5f5')

# 刷新按钮
refresh_btn = ttk.Button(event, text="刷新", command=refresh_floders)

# 中间文本框框架（初始隐藏）
middle_frame = ttk.Frame(event)
event_text = tk.Text(middle_frame, wrap=tk.WORD, width=100, height=30)
scrollbar = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL, command=event_text.yview)
event_text.configure(yscrollcommand=scrollbar.set)
event_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 底部按钮区域
bottom_frame = ttk.Frame(event)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

event_buttom = ttk.Button(bottom_frame, text="显示答案", command=dispaly)
event_buttom.grid(row=0, column=0, padx=5)
event_buttom.grid_remove()

event_buttom_go_on = ttk.Button(bottom_frame, text="继续", command=go_on)
event_buttom_go_on.grid(row=0, column=1, padx=5)
event_buttom_go_on.grid_remove()

event_buttom_destroy = ttk.Button(bottom_frame, text="退出", command=event.destroy)
event_buttom_destroy.grid(row=0, column=2, padx=5)
event_buttom_destroy.grid_remove()

event_buttom_restart = ttk.Button(bottom_frame, text="重新开始", command=restart)
event_buttom_restart.grid(row=0, column=3, padx=5)
event_buttom_restart.grid_remove()

egg_fresh_foldertimes = 0   

# 颜色定义
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

# 设置窗口图标
try:
    event.iconbitmap(default='ETS.ico')
except:
    pass

# 设置默认字体
default_font = font.nametofont("TkDefaultFont")
default_font.configure(size=10, family="微软雅黑")

# 绑定焦点事件
event.bind("<FocusIn>", on_focus_in)

# 初始加载主题
init_theme = load_theme_from_settings()
current_colors = dark_colors if init_theme == 'dark' else light_colors
apply_colors(current_colors)

if __name__ == "__main__":
    print("程序开始运行...")
    main()