import tkinter as tk
from tkinter import ttk
import time
import threading
import pyautogui
import pyperclip

class HackerClipboardApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.countdown_active = False
        self.stop_flag = False
        self.injection_thread = None
        
        # 设置pyautogui参数
        pyautogui.PAUSE = 0.01
        pyautogui.FAILSAFE = True
        
    def setup_window(self):
        self.root.title(">>> CLIPBOARD INJECTOR v2.3")
        
        # 先创建一个临时窗口来测量内容
        self.root.configure(bg='#000000')
        self.root.resizable(True, True)
        
        # 绑定ESC键为紧急停止
        self.root.bind('<Escape>', lambda e: self.emergency_stop())
        
    def setup_variables(self):
        self.always_on_top = tk.BooleanVar()
        self.countdown_text = tk.StringVar(value="[READY]")
        self.status_text = tk.StringVar(value=">>> System Ready | Press ESC for emergency stop")
        self.input_method = tk.StringVar(value="paste")
        self.input_speed = tk.DoubleVar(value=0.02)
        
    def create_widgets(self):
        # 主容器 - 使用固定padding
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="◢◤ CLIPBOARD INJECTOR v2.3 ◥◣",
            font=("Courier New", 16, "bold"),
            fg="#00ff00",
            bg="#000000"
        )
        title_label.pack(pady=(0, 10))
        
        # 分割线
        separator1 = tk.Label(
            main_frame,
            text="═" * 50,
            font=("Courier New", 10),
            fg="#333333",
            bg="#000000"
        )
        separator1.pack(pady=(0, 15))
        
        # 倒计时显示
        self.countdown_label = tk.Label(
            main_frame,
            textvariable=self.countdown_text,
            font=("Courier New", 22, "bold"),
            fg="#ff0000",
            bg="#000000",
            height=2
        )
        self.countdown_label.pack(pady=(0, 15))
        
        # 状态显示
        self.status_label = tk.Label(
            main_frame,
            textvariable=self.status_text,
            font=("Courier New", 10),
            fg="#00ffff",
            bg="#000000",
            wraplength=500,
            justify=tk.CENTER,
            height=2
        )
        self.status_label.pack(pady=(0, 20))
        
        # 配置框架
        config_frame = tk.LabelFrame(
            main_frame,
            text=" ⚙ CONFIGURATION ",
            font=("Courier New", 11, "bold"),
            fg="#ffff00",
            bg="#000000",
            bd=2,
            relief="groove",
            padx=15,
            pady=10
        )
        config_frame.pack(pady=(0, 20), fill=tk.X)
        
        # 输入方式选择
        method_frame = tk.Frame(config_frame, bg="#000000")
        method_frame.pack(pady=(5, 10), fill=tk.X)
        
        tk.Label(
            method_frame,
            text="INPUT METHOD:",
            font=("Courier New", 10, "bold"),
            fg="#ffff00",
            bg="#000000"
        ).grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        paste_radio = tk.Radiobutton(
            method_frame,
            text="PASTE (Fast)",
            variable=self.input_method,
            value="paste",
            font=("Courier New", 10),
            fg="#00ff00",
            bg="#000000",
            selectcolor="#333333",
            activebackground="#000000",
            activeforeground="#00ff00"
        )
        paste_radio.grid(row=0, column=1, sticky="w", padx=(0, 30))
        
        type_radio = tk.Radiobutton(
            method_frame,
            text="TYPE (Compatible)",
            variable=self.input_method,
            value="type",
            font=("Courier New", 10),
            fg="#00ff00",
            bg="#000000",
            selectcolor="#333333",
            activebackground="#000000",
            activeforeground="#00ff00"
        )
        type_radio.grid(row=0, column=2, sticky="w")
        
        # 输入速度控制
        speed_frame = tk.Frame(config_frame, bg="#000000")
        speed_frame.pack(pady=(0, 5), fill=tk.X)
        
        tk.Label(
            speed_frame,
            text="TYPE SPEED:",
            font=("Courier New", 10, "bold"),
            fg="#ffff00",
            bg="#000000"
        ).grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        speed_scale = tk.Scale(
            speed_frame,
            from_=0.001,
            to=0.1,
            resolution=0.001,
            orient=tk.HORIZONTAL,
            variable=self.input_speed,
            font=("Courier New", 9),
            fg="#00ff00",
            bg="#000000",
            troughcolor="#333333",
            highlightbackground="#000000",
            length=180
        )
        speed_scale.grid(row=0, column=1, sticky="w", padx=(0, 15))
        
        tk.Label(
            speed_frame,
            text="sec/char",
            font=("Courier New", 9),
            fg="#666666",
            bg="#000000"
        ).grid(row=0, column=2, sticky="w")
        
        # 控制按钮框架
        control_frame = tk.Frame(main_frame, bg="#000000")
        control_frame.pack(pady=(0, 20))
        
        # 置顶复选框
        topmost_check = tk.Checkbutton(
            control_frame,
            text="📌 ALWAYS ON TOP",
            variable=self.always_on_top,
            command=self.toggle_topmost,
            font=("Courier New", 11),
            fg="#ffff00",
            bg="#000000",
            selectcolor="#333333",
            activebackground="#000000",
            activeforeground="#ffff00"
        )
        topmost_check.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # 按钮行
        self.start_button = tk.Button(
            control_frame,
            text="▶ EXECUTE",
            command=self.start_injection,
            font=("Courier New", 12, "bold"),
            fg="#000000",
            bg="#00ff00",
            activebackground="#00aa00",
            activeforeground="#000000",
            relief="raised",
            bd=2,
            padx=20,
            pady=5,
            width=12
        )
        self.start_button.grid(row=1, column=0, padx=(0, 15))
        
        self.stop_button = tk.Button(
            control_frame,
            text="⏹ STOP",
            command=self.emergency_stop,
            font=("Courier New", 12, "bold"),
            fg="#ffffff",
            bg="#ff0000",
            activebackground="#aa0000",
            activeforeground="#ffffff",
            relief="raised",
            bd=2,
            padx=20,
            pady=5,
            width=12,
            state="disabled"
        )
        self.stop_button.grid(row=1, column=1)
        
        # 底部信息框架
        info_frame = tk.LabelFrame(
            main_frame,
            text=" ℹ USAGE INSTRUCTIONS ",
            font=("Courier New", 10, "bold"),
            fg="#666666",
            bg="#000000",
            bd=1,
            relief="groove",
            padx=15,
            pady=8
        )
        info_frame.pack(fill=tk.X)
        
        # 使用网格布局来更好地控制信息显示
        instructions = [
            "1. Copy your text to clipboard first",
            "2. Click EXECUTE and position cursor within 5 seconds",
            "3. PASTE mode: Uses Ctrl+V (recommended for speed)",
            "4. TYPE mode: Character by character (for compatibility)",
            "5. Press ESC or STOP button for emergency stop"
        ]
        
        for i, instruction in enumerate(instructions):
            tk.Label(
                info_frame,
                text=instruction,
                font=("Courier New", 9),
                fg="#888888",
                bg="#000000",
                anchor="w"
            ).grid(row=i, column=0, sticky="w", pady=1)
        
        # 设置窗口大小以适应内容
        self.root.update_idletasks()  # 确保所有组件都已渲染
        
        # 计算所需的窗口大小
        required_width = main_frame.winfo_reqwidth() + 50  # 额外的边距
        required_height = main_frame.winfo_reqheight() + 40  # 额外的边距
        
        # 设置窗口大小和位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 居中显示
        x = (screen_width - required_width) // 2
        y = (screen_height - required_height) // 2
        
        self.root.geometry(f"{required_width}x{required_height}+{x}+{y}")
        self.root.minsize(required_width, required_height)
        
    def toggle_topmost(self):
        self.root.attributes('-topmost', self.always_on_top.get())
        
    def emergency_stop(self):
        """紧急停止功能 - 强制中断"""
        if self.countdown_active:
            self.stop_flag = True
            self.countdown_text.set("[EMERGENCY STOP]")
            self.status_text.set(">>> EMERGENCY STOP ACTIVATED! Operation terminated.")
            
            # 强制停止pyautogui操作
            try:
                pyautogui.FAILSAFE = True
                # 移动鼠标到屏幕角落触发failsafe
                pyautogui.moveTo(0, 0)
            except:
                pass
            
            # 立即重置界面
            self.root.after(100, self.reset_interface)
            
    def reset_interface(self):
        """重置界面状态"""
        self.countdown_active = False
        self.stop_flag = False
        self.start_button.config(state="normal", text="▶ EXECUTE", bg="#00ff00")
        self.stop_button.config(state="disabled")
        
        # 延迟重置显示
        self.root.after(2000, lambda: (
            self.countdown_text.set("[READY]"),
            self.status_text.set(">>> System Ready | Press ESC for emergency stop")
        ))
        
    def start_injection(self):
        if self.countdown_active:
            return
            
        # 检查剪切板
        try:
            clipboard_content = pyperclip.paste()
            if not clipboard_content:
                self.status_text.set(">>> ERROR: Clipboard is empty!")
                return
        except Exception as e:
            self.status_text.set(f">>> ERROR: {str(e)}")
            return
            
        # 显示剪切板内容预览和方法
        preview = clipboard_content[:35] + "..." if len(clipboard_content) > 35 else clipboard_content
        method = self.input_method.get().upper()
        char_count = len(clipboard_content)
        self.status_text.set(f">>> TARGET: {preview} | METHOD: {method} | LENGTH: {char_count}")
        
        # 更新按钮状态
        self.start_button.config(state="disabled", text="◉ ARMED", bg="#ff6600")
        self.stop_button.config(state="normal")
        self.countdown_active = True
        self.stop_flag = False
        
        # 在新线程中运行倒计时
        self.injection_thread = threading.Thread(target=self.countdown_and_inject, daemon=True)
        self.injection_thread.start()
        
    def countdown_and_inject(self):
        try:
            # 倒计时阶段 - 每0.1秒检查一次停止标志
            for i in range(5, 0, -1):
                for j in range(10):  # 将1秒分成10个0.1秒
                    if self.stop_flag:
                        return
                    time.sleep(0.1)
                
                if self.stop_flag:
                    return
                    
                self.countdown_text.set(f"[{i}]")
                self.root.update()
            
            if self.stop_flag:
                return
                
            # 执行注入
            self.countdown_text.set("[INJECTING...]")
            self.status_text.set(">>> INJECTING PAYLOAD... Press STOP to abort!")
            self.root.update()
            
            clipboard_content = pyperclip.paste()
            
            if self.input_method.get() == "paste":
                if not self.stop_flag:
                    self.paste_content()
            else:
                self.type_content(clipboard_content)
            
            if not self.stop_flag:
                self.countdown_text.set("[COMPLETE]")
                self.status_text.set(">>> INJECTION SUCCESSFUL!")
                time.sleep(2)
            
        except Exception as e:
            if not self.stop_flag:
                self.countdown_text.set("[ERROR]")
                self.status_text.set(f">>> INJECTION FAILED: {str(e)}")
                time.sleep(2)
        finally:
            if not self.stop_flag:
                self.reset_interface()
    
    def paste_content(self):
        """使用Ctrl+V粘贴"""
        if not self.stop_flag:
            pyautogui.hotkey('ctrl', 'v')
    
    def type_content(self, content):
        """逐字符输入，支持实时中断"""
        interval = self.input_speed.get()
        total_chars = len(content)
        
        for i, char in enumerate(content):
            # 每个字符都检查停止标志
            if self.stop_flag:
                self.status_text.set(f">>> STOPPED at character {i+1}/{total_chars}")
                break
                
            try:
                pyautogui.write(char, interval=0)  # 立即输入字符
                time.sleep(interval)  # 然后等待间隔时间
            except:
                if self.stop_flag:
                    break
                continue
            
            # 每10个字符更新一次进度
            if i % 10 == 0 or i == total_chars - 1:
                if self.stop_flag:
                    break
                progress = int((i + 1) / total_chars * 100)
                self.status_text.set(f">>> TYPING... {progress}% ({i+1}/{total_chars})")
                self.root.update()
                
            # 在间隔期间也检查停止标志
            for _ in range(int(interval * 100)):  # 将间隔分成更小的片段
                if self.stop_flag:
                    return
                time.sleep(0.01)
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HackerClipboardApp()
    app.run()
