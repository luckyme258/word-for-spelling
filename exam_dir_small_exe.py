import os
import sys
import glob
import pygame
import tkinter as tk
from tkinter import filedialog, scrolledtext
import platform
from ctypes import byref, windll, c_long

# 尝试导入Windows标题栏修改所需模块
try:
    if platform.system() == "Windows":
        import win32gui
        windows_theme_support = True
    else:
        windows_theme_support = False
except ImportError:
    windows_theme_support = False

class SpellingApp:
    def __init__(self, root):
        # 初始化核心变量
        self.root = root
        self.words = []
        self.current_index = 0
        self.error_count = 0
        self.max_errors = 3
        self.is_playing = False
        self.is_completed = False
        self.wrong_words = []
        self.current_folder = ""
        
        # 初始化音频模块
        pygame.mixer.init()
        
        # 初始化UI（含隐藏标题栏）
        self.init_ui()
        self.log("请选择包含MP3文件的文件夹开始练习")

    def init_ui(self):
        """初始化UI：隐藏标题栏、完全居中、纯黑背景"""
        # 1. Windows隐藏系统标题栏（核心新增代码）
        self.root.overrideredirect(True)  # 隐藏系统默认标题栏（含关闭/最大化按钮）
        
        # 2. 窗口基础设置（纯黑背景）
        self.root.title("单词拼写练习")  # 隐藏后标题不显示，仅作标识
        self.root.geometry("850x650")    # 固定初始尺寸
        self.root.minsize(800, 600)      # 限制最小尺寸，避免控件挤压
        self.root.configure(bg="#000000")# 窗体背景设为纯黑色

        # 3. 新增自定义标题栏（替代系统标题栏，含关闭功能）
        custom_title_frame = tk.Frame(self.root, bg="#1e1e1e", height=30)
        custom_title_frame.pack(fill=tk.X)
        # 自定义标题文字（浅色字体）
        title_label = tk.Label(
            custom_title_frame,
            text="单词拼写练习 - 暗黑模式",
            bg="#1e1e1e",
            fg="white",
            font=("Microsoft YaHei", 11)
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=5)
        # 自定义关闭按钮（替代系统关闭）
        close_btn = tk.Button(
            custom_title_frame,
            text="×",
            bg="#1e1e1e",
            fg="white",
            bd=0,
            font=("Consolas", 12),
            width=3,
            command=self.cleanup_and_quit,
            activebackground="#ff4444"  #  hover时红色提示
        )
        close_btn.pack(side=tk.RIGHT)

        # 字体配置（浅色字体适配黑色背景）
        self.console_font = ("Consolas", 14)
        self.button_font = ("Microsoft YaHei", 12)

        # 主容器（统一纯黑背景，避免杂色）
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)  # 顶部留10px与自定义标题栏分隔

        # 4. 控制台区域（限制高度，解决比例过大问题）
        console_frame = tk.Frame(main_frame, bg="#000000")
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            font=self.console_font,
            bg="#1e1e1e",
            fg="#e0e0e0",
            bd=1,
            relief=tk.SUNKEN,
            highlightbackground="#555",
            highlightcolor="#555",
            wrap=tk.WORD,
            height=18
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.config(state=tk.DISABLED)

        # 5. 输入区域
        input_frame = tk.Frame(main_frame, bg="#000000")
        input_frame.pack(fill=tk.X, pady=(10, 10))
        
        self.input_label = tk.Label(
            input_frame,
            text=">",
            font=("Consolas", 16),
            fg="cyan",
            bg="#000000",
            width=2
        )
        self.input_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry = tk.Entry(
            input_frame,
            font=self.console_font,
            bg="#2d2d2d",
            fg="white",
            bd=1,
            relief=tk.SUNKEN,
            highlightbackground="#555",
            highlightcolor="#555",
            insertbackground="white"
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.entry.bind("<Return>", lambda event: self.check_spelling())

        # 6. 按钮区域（底部对齐）
        button_frame = tk.Frame(main_frame, bg="#000000")
        button_frame.pack(fill=tk.X, pady=(10, 0), anchor=tk.S)
        
        button_style = {
            "font": self.button_font,
            "bg": "#3c3c3c",
            "fg": "white",
            "bd": 0,
            "padx": 12,
            "pady": 8,
            "relief": tk.FLAT,
            "activebackground": "#4c4c4c",
            "activeforeground": "white"
        }

        # 功能按钮
        self.select_btn = tk.Button(button_frame, text="选择文件夹", **button_style, command=self.select_folder)
        self.select_btn.pack(side=tk.LEFT, padx=4)
        
        self.replay_btn = tk.Button(button_frame, text="重新播放", **button_style, command=self.replay_current)
        self.replay_btn.pack(side=tk.LEFT, padx=4)
        
        self.quit_btn = tk.Button(button_frame, text="退出", **button_style, command=self.cleanup_and_quit)
        self.quit_btn.pack(side=tk.LEFT, padx=4)

        # 练习完成后显示的按钮（初始隐藏）
        self.restart_btn = tk.Button(button_frame, text="再来一次", **button_style, command=self.restart_practice)
        self.copy_btn = tk.Button(button_frame, text="复制错词", **button_style, command=self.copy_wrong_words)

        # 7. 窗口完全居中（上下+左右）
        self.center_window()

    def center_window(self):
        """优化：确保Windows启动时完全上下左右居中"""
        self.root.update_idletasks()  # 强制刷新窗口尺寸，避免计算偏差
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        # 获取屏幕真实可用尺寸（排除任务栏）
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # 计算居中坐标（左右：(屏幕宽-窗口宽)/2；上下：(屏幕高-窗口高)/2）
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        self.root.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # ---------------------- 原有核心功能逻辑（保持不变） ----------------------
    def log(self, message):
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def play_audio(self, file_path):
        if not os.path.exists(file_path):
            self.log(f"❌ 文件不存在: {file_path}")
            return False
        if self.is_playing:
            self.stop_audio()
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.is_playing = True
            return True
        except Exception as e:
            self.log(f"❌ 播放错误: {str(e)}")
            return False

    def stop_audio(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False

    def select_folder(self):
        folder = filedialog.askdirectory(title="选择包含MP3文件的文件夹")
        if folder:
            self.current_folder = folder
            self.load_words(folder)

    def load_words(self, folder):
        self.words = []
        self.is_completed = False
        self.wrong_words = []
        try:
            mp3_files = set(glob.glob(os.path.join(folder, "*.mp3")) + glob.glob(os.path.join(folder, "*.MP3")))
            for file_path in mp3_files:
                word = os.path.splitext(os.path.basename(file_path))[0]
                self.words.append({"word": word, "path": file_path})
            self.words.sort(key=lambda x: x["word"].lower())
            if self.words:
                self.log(f"✅ 已加载 {len(self.words)} 个单词")
                self.current_index = 0
                self.error_count = 0
                self.hide_completion_buttons()
                self.play_current_word()
            else:
                self.log("❌ 未找到MP3文件")
        except Exception as e:
            self.log(f"❌ 加载错误: {str(e)}")

    def play_current_word(self):
        if not self.is_completed and self.current_index < len(self.words):
            word_data = self.words[self.current_index]
            self.log(f"🔊 播放第 {self.current_index + 1}/{len(self.words)} 个单词...")
            self.play_audio(word_data["path"])

    def replay_current(self):
        if not self.is_completed and self.current_index < len(self.words):
            self.stop_audio()
            self.play_current_word()

    def check_spelling(self):
        if self.is_completed:
            return
        user_input = self.entry.get().strip()
        if not user_input or not self.words:
            return
        self.entry.delete(0, tk.END)
        self.log(f"> {user_input}")
        current_word = self.words[self.current_index]["word"]

        if user_input.lower() == current_word.lower():
            self.log("✅ 拼写正确！")
            self.current_index += 1
            self.error_count = 0
            if self.current_index < len(self.words):
                self.play_current_word()
            else:
                self.complete_practice()
        else:
            self.error_count += 1
            if self.error_count >= self.max_errors:
                self.log(f"❌ 已连续{self.error_count}次错误")
                self.log(f"💡 正确答案: {current_word}")
                self.wrong_words.append(current_word)
                self.current_index += 1
                self.error_count = 0
                if self.current_index < len(self.words):
                    self.play_current_word()
                else:
                    self.complete_practice()
            else:
                self.log(f"❌ 拼写错误（第{self.error_count}次），请重新尝试")
                self.replay_current()

    def complete_practice(self):
        self.is_completed = True
        self.log("🎉 所有单词练习完成！")
        if self.wrong_words:
            self.log("\n📝 最终答错的单词：")
            for i, word in enumerate(self.wrong_words, 1):
                self.log(f"  {i}. {word}")
            self.log(f"\n总共答错 {len(self.wrong_words)} 个单词")
        else:
            self.log("🎊 太棒了！所有单词都答对了！")
        self.show_completion_buttons()

    def show_completion_buttons(self):
        self.restart_btn.pack(side=tk.LEFT, padx=4)
        self.copy_btn.pack(side=tk.LEFT, padx=4)

    def hide_completion_buttons(self):
        self.restart_btn.pack_forget()
        self.copy_btn.pack_forget()

    def restart_practice(self):
        if self.current_folder:
            self.load_words(self.current_folder)
            self.log("🔄 重新开始练习...")
        else:
            self.log("❌ 请先选择文件夹")

    def copy_wrong_words(self):
        if self.wrong_words:
            wrong_text = "\n".join(self.wrong_words)
            self.root.clipboard_clear()
            self.root.clipboard_append(wrong_text)
            self.log("✅ 错词已复制到剪贴板")
        else:
            self.log("💡 没有错词可复制")

    def cleanup_and_quit(self):
        self.stop_audio()
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpellingApp(root)
    root.mainloop()
