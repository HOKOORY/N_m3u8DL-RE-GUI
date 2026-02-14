import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading
import os
import re
import json
from typing import Dict, List, Optional
import time
import queue

class DownloadTask:
    """下载任务类"""
    def __init__(self, task_id, url, save_dir, save_name, tmp_dir, config):
        self.task_id = task_id
        self.url = url
        self.save_dir = save_dir
        self.save_name = save_name
        self.tmp_dir = tmp_dir
        self.config = config
        self.status = "待开始"  # 待开始, 下载中, 已完成, 已停止, 错误
        self.process = None
        self.is_running = False
        self.log_queue = queue.Queue()
        self.tmp_dir_before_download = set()  # 记录下载前临时目录的文件
        self.current_tmp_dir = ""  # 记录当前使用的临时目录
        self.start_time = None
        self.end_time = None

class M3u8DLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("N_m3u8DL-RE GUI - 多任务版")
        self.root.geometry("1200x800")
        
        # 配置文件路径
        self.config_file = "m3u8dl_config.json"
        
        # 任务管理
        self.tasks = {}  # 任务字典
        self.next_task_id = 1  # 下一个任务ID
        
        # 创建菜单栏
        self.create_menu()
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 创建变量
        self.input_url = tk.StringVar()
        self.save_dir = tk.StringVar()
        self.save_name = tk.StringVar()
        self.tmp_dir = tk.StringVar()
        self.thread_count = tk.StringVar(value="4")
        self.download_retry_count = tk.StringVar(value="3")
        self.http_request_timeout = tk.StringVar(value="100")
        self.log_level = tk.StringVar(value="INFO")
        self.sub_format = tk.StringVar(value="SRT")
        self.ffmpeg_binary_path = tk.StringVar()
        self.decryption_binary_path = tk.StringVar()
        self.decryption_engine = tk.StringVar(value="MP4DECRYPT")
        self.custom_proxy = tk.StringVar()
        self.max_speed = tk.StringVar()
        
        # 加载配置文件
        self.load_config()
        
        # 创建界面元素
        self.create_widgets()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存当前配置", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_instructions)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_widgets(self):
        # 创建笔记本控件（选项卡）
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 添加任务配置选项卡
        self.task_config_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.task_config_frame, text="任务配置")
        
        # 添加任务管理选项卡
        self.task_manager_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.task_manager_frame, text="任务管理")
        
        # 任务配置选项卡内容
        self.create_task_config_widgets()
        
        # 任务管理选项卡内容
        self.create_task_manager_widgets()
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 配置主框架行权重
        self.main_frame.rowconfigure(0, weight=1)
        
        # 配置任务管理框架行权重
        self.task_manager_frame.rowconfigure(1, weight=1)
        self.task_manager_frame.columnconfigure(0, weight=1)

    def create_task_config_widgets(self):
        """创建任务配置界面"""
        # 输入URL区域
        ttk.Label(self.task_config_frame, text="输入URL或文件:").grid(row=0, column=0, sticky=tk.W, pady=2)
        input_frame = ttk.Frame(self.task_config_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        input_frame.columnconfigure(0, weight=1)
        ttk.Entry(input_frame, textvariable=self.input_url, width=80).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 保存目录区域
        ttk.Label(self.task_config_frame, text="保存目录:").grid(row=2, column=0, sticky=tk.W, pady=(10, 2))
        save_dir_frame = ttk.Frame(self.task_config_frame)
        save_dir_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        save_dir_frame.columnconfigure(0, weight=1)
        ttk.Entry(save_dir_frame, textvariable=self.save_dir, width=80).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(save_dir_frame, text="浏览", command=self.browse_save_dir).grid(row=0, column=1)
        
        # 保存文件名
        ttk.Label(self.task_config_frame, text="保存文件名:").grid(row=4, column=0, sticky=tk.W, pady=(10, 2))
        ttk.Entry(self.task_config_frame, textvariable=self.save_name, width=80).grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 临时目录
        ttk.Label(self.task_config_frame, text="临时目录:").grid(row=6, column=0, sticky=tk.W, pady=(10, 2))
        tmp_dir_frame = ttk.Frame(self.task_config_frame)
        tmp_dir_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        tmp_dir_frame.columnconfigure(0, weight=1)
        ttk.Entry(tmp_dir_frame, textvariable=self.tmp_dir, width=80).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(tmp_dir_frame, text="浏览", command=self.browse_tmp_dir).grid(row=0, column=1)
        
        # 线程数
        ttk.Label(self.task_config_frame, text="下载线程数:").grid(row=8, column=0, sticky=tk.W, pady=(10, 2))
        ttk.Entry(self.task_config_frame, textvariable=self.thread_count, width=20).grid(row=8, column=1, sticky=tk.W, pady=2)
        
        # 重试次数
        ttk.Label(self.task_config_frame, text="下载重试次数:").grid(row=9, column=0, sticky=tk.W, pady=(10, 2))
        ttk.Entry(self.task_config_frame, textvariable=self.download_retry_count, width=20).grid(row=9, column=1, sticky=tk.W, pady=2)
        
        # 超时时间
        ttk.Label(self.task_config_frame, text="HTTP请求超时(秒):").grid(row=10, column=0, sticky=tk.W, pady=(10, 2))
        ttk.Entry(self.task_config_frame, textvariable=self.http_request_timeout, width=20).grid(row=10, column=1, sticky=tk.W, pady=2)
        
        # 日志级别
        ttk.Label(self.task_config_frame, text="日志级别:").grid(row=11, column=0, sticky=tk.W, pady=(10, 2))
        log_level_combo = ttk.Combobox(self.task_config_frame, textvariable=self.log_level, values=["DEBUG", "INFO", "WARN", "ERROR", "OFF"], state="readonly", width=17)
        log_level_combo.grid(row=11, column=1, sticky=tk.W, pady=2)
        
        # 字幕格式
        ttk.Label(self.task_config_frame, text="字幕格式:").grid(row=12, column=0, sticky=tk.W, pady=(10, 2))
        sub_format_combo = ttk.Combobox(self.task_config_frame, textvariable=self.sub_format, values=["SRT", "VTT"], state="readonly", width=17)
        sub_format_combo.grid(row=12, column=1, sticky=tk.W, pady=2)
        
        # 代理设置
        ttk.Label(self.task_config_frame, text="自定义代理:").grid(row=13, column=0, sticky=tk.W, pady=(10, 2))
        ttk.Entry(self.task_config_frame, textvariable=self.custom_proxy, width=80).grid(row=14, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 限速
        ttk.Label(self.task_config_frame, text="限速 (如: 15M, 100K):").grid(row=15, column=0, sticky=tk.W, pady=(10, 2))
        ttk.Entry(self.task_config_frame, textvariable=self.max_speed, width=20).grid(row=15, column=1, sticky=tk.W, pady=2)
        
        # 高级设置按钮
        ttk.Button(self.task_config_frame, text="高级设置", command=self.open_advanced_settings).grid(row=16, column=0, pady=(20, 10))
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.task_config_frame)
        button_frame.grid(row=17, column=0, columnspan=2, pady=(20, 10))
        ttk.Button(button_frame, text="添加到任务列表", command=self.add_task).pack(side=tk.LEFT, padx=(0, 10))
        
    def create_task_manager_widgets(self):
        """创建任务管理界面"""
        # 任务列表
        columns = ("ID", "URL", "保存位置", "状态", "开始时间", "结束时间")
        self.task_tree = ttk.Treeview(self.task_manager_frame, columns=columns, show="headings", height=10)
        
        # 定义列标题
        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=150)
        
        # 添加滚动条
        task_scrollbar = ttk.Scrollbar(self.task_manager_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=task_scrollbar.set)
        
        # 布局任务列表
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        task_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 任务操作按钮区域
        task_button_frame = ttk.Frame(self.task_manager_frame)
        task_button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(task_button_frame, text="开始选中任务", command=self.start_selected_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_button_frame, text="删除选中任务", command=self.delete_selected_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_button_frame, text="清空所有任务", command=self.clear_all_tasks).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_button_frame, text="开始所有待开始任务", command=self.start_all_pending_tasks).pack(side=tk.LEFT, padx=(0, 5))
        
        # 任务日志显示区域
        ttk.Label(self.task_manager_frame, text="任务日志:").grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        self.task_log_text = scrolledtext.ScrolledText(self.task_manager_frame, height=15, width=100)
        self.task_log_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        
        # 绑定任务列表选择事件
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        
    def browse_save_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir.set(directory)
            
    def browse_tmp_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.tmp_dir.set(directory)
            
    def open_advanced_settings(self):
        # 检查是否已存在高级设置窗口
        if not hasattr(self, 'advanced_window') or not self.advanced_window or not self.advanced_window.window.winfo_exists():
            self.advanced_window = AdvancedSettingsWindow(self.root, self)
            # 如果有已保存的配置，加载到高级设置窗口
            self.load_advanced_config()
        else:
            # 如果窗口已存在，将其带到前台
            self.advanced_window.window.lift()
            self.advanced_window.window.focus_force()
            
    def start_download(self):
        if self.is_downloading:
            messagebox.showwarning("警告", "下载正在进行中，请先停止当前下载")
            return
            
        # 在新线程中运行下载命令
        threading.Thread(target=self.run_download, daemon=True).start()
        
    def run_download(self):
        # 构建命令
        cmd = self.build_command()
        if not cmd:
            self.update_status("就绪")
            return
        
        self.is_downloading = True
        try:
            # 运行命令并实时显示输出
            self.download_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0  # Windows上隐藏控制台窗口
            )
            
            # 实时读取输出
            while self.is_downloading:
                output = self.download_process.stdout.readline()
                if output == '' and self.download_process.poll() is not None:
                    break
                if output:
                    self.update_log(output.strip())
                
            # 等待进程结束
            return_code = self.download_process.poll()
            if return_code is not None:
                self.update_log(f"\n下载完成，退出码: {return_code}")
                self.update_status(f"下载完成 (退出码: {return_code})")
            else:
                self.update_log("\n下载已停止")
                self.update_status("下载已停止")
        except Exception as e:
            self.update_log(f"下载出错: {str(e)}")
            self.update_status("下载出错")
        finally:
            self.is_downloading = False
            self.download_process = None
    
    def browse_save_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir.set(directory)
            
    def browse_tmp_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.tmp_dir.set(directory)
            
    def open_advanced_settings(self):
        # 检查是否已存在高级设置窗口
        if not hasattr(self, 'advanced_window') or not self.advanced_window or not self.advanced_window.window.winfo_exists():
            self.advanced_window = AdvancedSettingsWindow(self.root, self)
            # 如果有已保存的配置，加载到高级设置窗口
            self.load_advanced_config()
        else:
            # 如果窗口已存在，将其带到前台
            self.advanced_window.window.lift()
            self.advanced_window.window.focus_force()
    
    def run_download_task(self, task):
        """运行指定的下载任务"""
        # 在开始下载前记录临时目录状态
        tmp_dir = task.tmp_dir
        if tmp_dir and os.path.exists(tmp_dir):
            task.current_tmp_dir = tmp_dir
            task.tmp_dir_before_download = set(os.listdir(tmp_dir))
        else:
            # 如果没有设置临时目录，尝试使用默认临时目录
            import tempfile
            default_tmp = tempfile.gettempdir()
            task.current_tmp_dir = default_tmp
            task.tmp_dir_before_download = set(os.listdir(default_tmp))
        
        # 更新任务状态
        task.status = "下载中"
        task.is_running = True
        task.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 更新任务列表中的状态
        self.update_task_list()
        
        # 构建命令
        cmd = self.build_task_command(task)
        if not cmd:
            task.status = "错误"
            self.update_task_list()
            return
        
        try:
            # 确定工作目录，如果指定了保存目录则使用保存目录，否则使用当前目录
            working_dir = task.save_dir if task.save_dir and os.path.exists(task.save_dir) else os.getcwd()
            
            # 运行命令并实时显示输出
            task.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=working_dir,  # 设置工作目录
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0  # Windows上隐藏控制台窗口
            )
            
            # 实时读取输出
            while task.is_running:
                output = task.process.stdout.readline()
                if output == '' and task.process.poll() is not None:
                    break
                if output:
                    task.log_queue.put(output.strip())
                    # 如果当前选中了此任务，也更新日志显示
                    selected_items = self.task_tree.selection()
                    if selected_items:
                        values = self.task_tree.item(selected_items[0], "values")
                        if int(values[0]) == task.task_id:
                            self.root.after(0, self._update_log_gui, output.strip())
                
            # 等待进程结束
            return_code = task.process.poll()
            task.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            if return_code == 0:
                task.status = "已完成"
                task.log_queue.put(f"\n任务 #{task.task_id} 下载完成")
            else:
                task.status = "错误"
                task.log_queue.put(f"\n任务 #{task.task_id} 下载失败，退出码: {return_code}")
        except Exception as e:
            task.status = "错误"
            task.log_queue.put(f"任务 #{task.task_id} 下载出错: {str(e)}")
        finally:
            task.is_running = False
            task.process = None
            
            # 更新任务列表中的状态
            self.update_task_list()
            
            # 更新全局状态
            self.update_status("任务完成")
    
    def build_task_command(self, task) -> Optional[List[str]]:
        """为指定任务构建命令"""
        import sys
        import os
        
        # 验证必要参数
        if not task.url:
            task.log_queue.put("错误: 任务URL为空")
            return None
            
        # 检查是否在PyInstaller打包环境中
        if getattr(sys, 'frozen', False):
            # 在打包环境中，使用PyInstaller的资源路径
            # PyInstaller会在运行时解压资源到临时目录
            application_path = sys._MEIPASS  # PyInstaller临时目录
            n_m3u8dl_path = os.path.join(application_path, "N_m3u8DL-RE.exe")
        else:
            # 在开发环境中，N_m3u8DL-RE.exe位于脚本同目录下
            n_m3u8dl_path = "N_m3u8DL-RE.exe"
        
        # 构建命令
        cmd = [n_m3u8dl_path, task.url]
        
        # 添加参数
        if task.save_dir:
            cmd.extend(["--save-dir", task.save_dir])
        if task.save_name:
            cmd.extend(["--save-name", task.save_name])
        if task.tmp_dir:
            cmd.extend(["--tmp-dir", task.tmp_dir])
        if task.config.get('thread_count'):
            cmd.extend(["--thread-count", task.config['thread_count']])
        if task.config.get('download_retry_count'):
            cmd.extend(["--download-retry-count", task.config['download_retry_count']])
        if task.config.get('http_request_timeout'):
            cmd.extend(["--http-request-timeout", task.config['http_request_timeout']])
        if task.config.get('log_level'):
            cmd.extend(["--log-level", task.config['log_level']])
        if task.config.get('sub_format'):
            cmd.extend(["--sub-format", task.config['sub_format']])
        if task.config.get('custom_proxy'):
            cmd.extend(["--custom-proxy", task.config['custom_proxy']])
        if task.config.get('max_speed'):
            cmd.extend(["-R", task.config['max_speed']])
            
        # 添加高级设置参数
        cmd = self.add_task_advanced_params(cmd, task)
            
        return cmd
    
    def validate_numeric_param(self, value: str, param_name: str) -> bool:
        """验证数字参数"""
        if not value:
            return True  # 空值允许通过
        
        try:
            num = int(value)
            if num <= 0:
                messagebox.showerror("错误", f"{param_name}必须是正整数")
                return False
            return True
        except ValueError:
            messagebox.showerror("错误", f"{param_name}必须是有效的数字")
            return False
    
    def validate_path(self, path: str, param_name: str) -> bool:
        """验证路径参数"""
        if not os.path.exists(path):
            messagebox.showerror("错误", f"{param_name}路径不存在: {path}")
            return False
        return True
    
    def add_task_advanced_params(self, cmd: List[str], task) -> List[str]:
        """为指定任务添加高级设置参数"""
        config = task.config
        
        # 基本设置
        if config.get('auto_select', False):
            cmd.append("--auto-select")
        if config.get('skip_merge', False):
            cmd.append("--skip-merge")
        if config.get('skip_download', False):
            cmd.append("--skip-download")
        if config.get('binary_merge', False):
            cmd.append("--binary-merge")
        if config.get('del_after_done', True):
            cmd.append("--del-after-done")
        if config.get('no_date_info', False):
            cmd.append("--no-date-info")
        if config.get('no_log', False):
            cmd.append("--no-log")
        if not config.get('write_meta_json', True):
            cmd.append("--write-meta-json")
        if config.get('append_url_params', False):
            cmd.append("--append-url-params")
        if config.get('concurrent_download', False):
            cmd.append("-mt")
        if not config.get('auto_subtitle_fix', True):
            cmd.append("--auto-subtitle-fix")
        if not config.get('use_system_proxy', True):
            cmd.append("--use-system-proxy")
        if config.get('live_perform_as_vod', False):
            cmd.append("--live-perform-as-vod")
        if config.get('live_real_time_merge', False):
            cmd.append("--live-real-time-merge")
        if not config.get('live_keep_segments', True):
            cmd.append("--live-keep-segments")
        if config.get('live_pipe_mux', False):
            cmd.append("--live-pipe-mux")
        if config.get('live_fix_vtt_by_audio', False):
            cmd.append("--live-fix-vtt-by-audio")
        if config.get('disable_update_check', False):
            cmd.append("--disable-update-check")
        if config.get('allow_hls_multi_ext_map', False):
            cmd.append("--allow-hls-multi-ext-map")
        
        # 请求头
        headers = config.get('headers', [])
        for key_val, value_val in headers:
            if key_val and value_val:
                cmd.extend(["-H", f'"{key_val}: {value_val}"'])
        
        # 解密设置
        if config.get('decryption_engine_var'):
            cmd.extend(["--decryption-engine", config['decryption_engine_var']])
        if config.get('decryption_path_var', '').strip():
            cmd.extend(["--decryption-binary-path", config['decryption_path_var'].strip()])
        if config.get('decryption_key_var', '').strip():
            keys = config['decryption_key_var'].split(',')
            for key in keys:
                cmd.extend(["--key", key.strip()])
        if config.get('key_file_var', '').strip():
            cmd.extend(["--key-text-file", config['key_file_var'].strip()])
        if config.get('mp4_real_time_decryption', False):
            cmd.append("--mp4-real-time-decryption")
        if config.get('custom_hls_method_var'):
            cmd.extend(["--custom-hls-method", config['custom_hls_method_var']])
        if config.get('custom_hls_key_var', '').strip():
            cmd.extend(["--custom-hls-key", config['custom_hls_key_var'].strip()])
        if config.get('custom_hls_iv_var', '').strip():
            cmd.extend(["--custom-hls-iv", config['custom_hls_iv_var'].strip()])
        
        # 混流设置
        if config.get('mux_after_done_var', '').strip():
            cmd.extend(["-M", config['mux_after_done_var'].strip()])
        if config.get('mux_import_var', '').strip():
            cmd.extend(["--mux-import", config['mux_import_var'].strip()])
        
        # 轨道选择
        if config.get('select_video_var', '').strip():
            cmd.extend(["-sv", config['select_video_var'].strip()])
        if config.get('select_audio_var', '').strip():
            cmd.extend(["-sa", config['select_audio_var'].strip()])
        if config.get('select_subtitle_var', '').strip():
            cmd.extend(["-ss", config['select_subtitle_var'].strip()])
        if config.get('drop_video_var', '').strip():
            cmd.extend(["-dv", config['drop_video_var'].strip()])
        if config.get('drop_audio_var', '').strip():
            cmd.extend(["-da", config['drop_audio_var'].strip()])
        if config.get('drop_subtitle_var', '').strip():
            cmd.extend(["-ds", config['drop_subtitle_var'].strip()])
        
        # 其他设置
        if config.get('base_url_var', '').strip():
            cmd.extend(["--base-url", config['base_url_var'].strip()])
        if config.get('save_pattern_var', '').strip():
            cmd.extend(["--save-pattern", config['save_pattern_var'].strip()])
        if config.get('log_file_path_var', '').strip():
            cmd.extend(["--log-file-path", config['log_file_path_var'].strip()])
        if config.get('urlprocessor_args_var', '').strip():
            cmd.extend(["--urlprocessor-args", config['urlprocessor_args_var'].strip()])
        if config.get('sub_only_var', False):
            cmd.append("--sub-only")
        if config.get('live_record_limit_var', '').strip():
            cmd.extend(["--live-record-limit", config['live_record_limit_var'].strip()])
        if config.get('live_wait_time_var', '').strip():
            cmd.extend(["--live-wait-time", config['live_wait_time_var'].strip()])
        if config.get('live_take_count_var', '').strip():
            cmd.extend(["--live-take-count", config['live_take_count_var'].strip()])
        if config.get('ad_keyword_var', '').strip():
            cmd.extend(["--ad-keyword", config['ad_keyword_var'].strip()])
    
        return cmd
    
    def update_log(self, message):
        # 在主线程中更新日志
        self.root.after(0, self._update_log_gui, message)
        
    def _update_log_gui(self, message):
        # 检查是否在任务管理选项卡中
        # 使用 try-except 避免可能的递归问题
        try:
            # 检查当前选中的标签页
            current_tab = self.notebook.index(self.notebook.select())
            if current_tab == 1:  # 任务管理选项卡
                self.task_log_text.insert(tk.END, message + "\n")
                self.task_log_text.see(tk.END)
        except:
            # 如果出现异常，直接添加到日志中，不依赖选项卡选择
            # 避免递归循环
            self.task_log_text.insert(tk.END, message + "\n")
            self.task_log_text.see(tk.END)
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        
    def add_task(self):
        """添加下载任务到任务列表并自动开始下载"""
        if not self.input_url.get().strip():
            messagebox.showerror("错误", "请输入URL或文件路径")
            return
            
        # 创建任务配置字典
        config = {
            'thread_count': self.thread_count.get().strip(),
            'download_retry_count': self.download_retry_count.get().strip(),
            'http_request_timeout': self.http_request_timeout.get().strip(),
            'log_level': self.log_level.get().strip(),
            'sub_format': self.sub_format.get().strip(),
            'custom_proxy': self.custom_proxy.get().strip(),
            'max_speed': self.max_speed.get().strip(),
            'ffmpeg_binary_path': self.ffmpeg_binary_path.get().strip(),
            'decryption_binary_path': self.decryption_binary_path.get().strip(),
            'decryption_engine': self.decryption_engine.get().strip()
        }
        
        # 如果高级设置窗口存在，也保存其中的设置
        if hasattr(self, 'advanced_window') and self.advanced_window:
            config.update({
                # 基本设置
                'auto_select': self.advanced_window.auto_select.get(),
                'skip_merge': self.advanced_window.skip_merge.get(),
                'skip_download': self.advanced_window.skip_download.get(),
                'binary_merge': self.advanced_window.binary_merge.get(),
                'del_after_done': self.advanced_window.del_after_done.get(),
                'no_date_info': self.advanced_window.no_date_info.get(),
                'no_log': self.advanced_window.no_log.get(),
                'write_meta_json': self.advanced_window.write_meta_json.get(),
                'append_url_params': self.advanced_window.append_url_params.get(),
                'concurrent_download': self.advanced_window.concurrent_download.get(),
                'auto_subtitle_fix': self.advanced_window.auto_subtitle_fix.get(),
                'use_system_proxy': self.advanced_window.use_system_proxy.get(),
                'live_perform_as_vod': self.advanced_window.live_perform_as_vod.get(),
                'live_real_time_merge': self.advanced_window.live_real_time_merge.get(),
                'live_keep_segments': self.advanced_window.live_keep_segments.get(),
                'live_pipe_mux': self.advanced_window.live_pipe_mux.get(),
                'live_fix_vtt_by_audio': self.advanced_window.live_fix_vtt_by_audio.get(),
                'disable_update_check': self.advanced_window.disable_update_check.get(),
                'allow_hls_multi_ext_map': self.advanced_window.allow_hls_multi_ext_map.get(),
                
                # 请求头
                'headers': [(hk.get(), hv.get()) for hk, hv in self.advanced_window.headers_vars if hk.get().strip() and hv.get().strip()],
                
                # 解密设置
                'decryption_engine_var': self.advanced_window.decryption_engine_var.get(),
                'decryption_path_var': self.advanced_window.decryption_path_var.get(),
                'decryption_key_var': self.advanced_window.decryption_key_var.get(),
                'key_file_var': self.advanced_window.key_file_var.get(),
                'mp4_real_time_decryption': self.advanced_window.mp4_real_time_decryption.get(),
                'custom_hls_method_var': self.advanced_window.custom_hls_method_var.get(),
                'custom_hls_key_var': self.advanced_window.custom_hls_key_var.get(),
                'custom_hls_iv_var': self.advanced_window.custom_hls_iv_var.get(),
                
                # 混流设置
                'mux_after_done_var': self.advanced_window.mux_after_done_var.get(),
                'mux_import_var': self.advanced_window.mux_import_var.get(),
                
                # 轨道选择
                'select_video_var': self.advanced_window.select_video_var.get(),
                'select_audio_var': self.advanced_window.select_audio_var.get(),
                'select_subtitle_var': self.advanced_window.select_subtitle_var.get(),
                'drop_video_var': self.advanced_window.drop_video_var.get(),
                'drop_audio_var': self.advanced_window.drop_audio_var.get(),
                'drop_subtitle_var': self.advanced_window.drop_subtitle_var.get(),
                
                # 其他设置
                'base_url_var': self.advanced_window.base_url_var.get(),
                'save_pattern_var': self.advanced_window.save_pattern_var.get(),
                'log_file_path_var': self.advanced_window.log_file_path_var.get(),
                'urlprocessor_args_var': self.advanced_window.urlprocessor_args_var.get(),
                'sub_only_var': self.advanced_window.sub_only.get(),
                'live_record_limit_var': self.advanced_window.live_record_limit_var.get(),
                'live_wait_time_var': self.advanced_window.live_wait_time_var.get(),
                'live_take_count_var': self.advanced_window.live_take_count_var.get(),
                'ad_keyword_var': self.advanced_window.ad_keyword_var.get()
            })
        
        # 创建下载任务
        task_id = self.next_task_id
        task = DownloadTask(
            task_id=task_id,
            url=self.input_url.get().strip(),
            save_dir=self.save_dir.get().strip(),
            save_name=self.save_name.get().strip(),
            tmp_dir=self.tmp_dir.get().strip(),
            config=config
        )
        
        # 添加到任务字典
        self.tasks[task_id] = task
        
        # 添加到任务列表显示
        self.task_tree.insert("", "end", values=(
            task_id,
            task.url,
            task.save_dir,
            task.status,
            "",  # 开始时间
            ""   # 结束时间
        ))
        
        self.next_task_id += 1
        self.update_status(f"已添加任务 #{task_id}，正在开始下载...")
        
        # 自动开始下载任务
        threading.Thread(target=self.run_download_task, args=(task,), daemon=True).start()
        
    def start_selected_task(self):
        """开始选中的任务"""
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要开始的任务")
            return
            
        for item in selected_items:
            # 获取任务ID
            values = self.task_tree.item(item, "values")
            task_id = int(values[0])
            
            # 获取任务对象
            task = self.tasks.get(task_id)
            if task:
                # 在新线程中运行下载任务
                threading.Thread(target=self.run_download_task, args=(task,), daemon=True).start()
                
    def delete_selected_task(self):
        """删除选中的任务（停止任务、清理临时文件并从列表中删除）"""
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的任务")
            return
            
        # 首先获取所有要删除的任务信息（在删除树形项目之前）
        tasks_to_remove = []
        for item in selected_items:
            try:
                # 获取任务ID
                values = self.task_tree.item(item, "values")
                task_id = int(values[0])
                
                # 获取任务对象
                task = self.tasks.get(task_id)
                if task:
                    tasks_to_remove.append((task_id, task, item))
            except (ValueError, IndexError):
                # 如果无法解析任务ID，跳过该项目
                continue
        
        # 处理每个要删除的任务
        for task_id, task, item in tasks_to_remove:
            try:
                # 如果任务正在运行，先停止（停止时会自动清理临时文件）
                if task.is_running:
                    self.stop_task(task_id)
                elif task.status != "已完成":
                    # 如果任务未运行且不是已完成状态，手动清理临时文件
                    # 对于已完成的任务，我们不进行手动清理，因为合并可能仍在进行
                    # 或者用户可能希望保留临时文件（取决于del_after_done设置）
                    self.cleanup_task_temp_files(task)
                    
                # 从任务字典中删除
                if task_id in self.tasks:
                    del self.tasks[task_id]
                    
            except Exception as e:
                print(f"删除任务 {task_id} 时出错: {str(e)}")
        
        # 最后一次性删除所有树形控件项目
        try:
            self.task_tree.delete(*[item for _, _, item in tasks_to_remove])
        except Exception as e:
            print(f"删除树形控件项目时出错: {str(e)}")
            
    def clear_all_tasks(self):
        """清空所有任务"""
        # 先停止所有运行中的任务
        for task_id, task in self.tasks.items():
            if task.is_running:
                self.stop_task(task_id)
                
        # 清空任务字典
        self.tasks.clear()
        
        # 清空任务列表
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
            
    def start_all_pending_tasks(self):
        """开始所有待开始的任务"""
        for task_id, task in self.tasks.items():
            if task.status == "待开始":
                # 在新线程中运行下载任务
                threading.Thread(target=self.run_download_task, args=(task,), daemon=True).start()
                
    def on_task_select(self, event):
        """当任务被选中时，显示该任务的日志"""
        selected_items = self.task_tree.selection()
        if selected_items:
            # 获取任务ID
            values = self.task_tree.item(selected_items[0], "values")
            task_id = int(values[0])
            
            # 获取任务对象
            task = self.tasks.get(task_id)
            if task:
                # 显示任务日志
                self.show_task_log(task)
                
    def show_task_log(self, task):
        """显示指定任务的日志"""
        # 清空当前日志
        self.task_log_text.delete(1.0, tk.END)
        
        # 显示任务日志
        while not task.log_queue.empty():
            log_message = task.log_queue.get()
            self.task_log_text.insert(tk.END, log_message + "\n")
        self.task_log_text.see(tk.END)
        
    def stop_task(self, task_id):
        """停止指定的任务"""
        task = self.tasks.get(task_id)
        if task and task.process and task.is_running:
            try:
                # 尝试优雅地终止进程
                task.process.terminate()
                # 等待一段时间让进程自行退出
                try:
                    task.process.wait(timeout=5)  # 等待最多5秒
                except subprocess.TimeoutExpired:
                    # 如果进程没有在时间内退出，强制杀死
                    task.process.kill()
                    task.process.wait()
            except Exception as e:
                task.log_queue.put(f"停止任务 #{task_id} 时出错: {str(e)}")
            finally:
                task.is_running = False
                task.status = "已停止"
                
                # 添加到任务日志
                task.log_queue.put(f"任务 #{task_id} 已停止")
                
                # 清理临时文件
                self.cleanup_task_temp_files(task)
                
                # 更新任务列表
                self.update_task_list()
        else:
            # 如果任务没有运行，只是更新状态
            if task:
                task.status = "已停止"
                task.log_queue.put(f"任务 #{task_id} 已停止")
                self.update_task_list()
    
    def cleanup_task_temp_files(self, task):
        """清理指定任务的临时文件"""
        try:
            if task.current_tmp_dir and os.path.exists(task.current_tmp_dir):
                import shutil
                # 获取下载后的临时目录文件列表
                if os.path.exists(task.current_tmp_dir):
                    tmp_dir_after = set(os.listdir(task.current_tmp_dir))
                else:
                    tmp_dir_after = set()
                
                # 计算本次下载产生的新文件（差集）
                new_files = tmp_dir_after - task.tmp_dir_before_download
                
                # 删除本次下载产生的临时文件
                for item in new_files:
                    item_path = os.path.join(task.current_tmp_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        task.log_queue.put(f"已删除任务产生的临时文件: {item_path}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        task.log_queue.put(f"已删除任务产生的临时目录: {item_path}")
                
                if new_files:
                    task.log_queue.put(f"已清理任务 #{task.task_id} 产生的临时文件，目录: {task.current_tmp_dir}")
                else:
                    task.log_queue.put(f"临时目录中没有任务 #{task.task_id} 产生的新文件需要清理: {task.current_tmp_dir}")
            else:
                task.log_queue.put(f"任务 #{task.task_id} 没有可清理的临时目录")
        except Exception as e:
            task.log_queue.put(f"清理任务 #{task.task_id} 临时文件时出错: {str(e)}")
    
    def update_task_list(self):
        """更新任务列表显示"""
        # 保存当前选中的项目
        selected_items = self.task_tree.selection()
        
        # 保存选中项目的任务ID
        selected_task_ids = []
        if selected_items:
            values = self.task_tree.item(selected_items[0], "values")
            selected_task_ids.append(int(values[0]))
        
        # 保存当前滚动位置
        current_view = self.task_tree.yview()
        
        # 清空任务列表
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # 重新添加任务
        for task_id, task in self.tasks.items():
            self.task_tree.insert("", "end", values=(
                task_id,
                task.url,
                task.save_dir,
                task.status,
                task.start_time or "",
                task.end_time or ""
            ))
        
        # 恢复滚动位置
        self.task_tree.yview_moveto(current_view[0])
        
        # 如果之前有选中项目，重新选中
        if selected_task_ids:
            for item in self.task_tree.get_children():
                values = self.task_tree.item(item, "values")
                if int(values[0]) in selected_task_ids:
                    self.task_tree.selection_set(item)
                    break

    def show_instructions(self):
        """显示使用说明"""
        instructions = """
N_m3u8DL-RE GUI 使用说明

1. 基本设置：
   - 输入URL或文件：输入要下载的m3u8链接或本地m3u8文件路径
   - 保存目录：选择下载文件的保存位置
   - 保存文件名：指定下载文件的名称（可选）
   - 临时目录：设置临时文件的存储位置（可选）

2. 下载设置：
   - 下载线程数：设置并发下载线程数，默认为CPU线程数
   - 下载重试次数：每个分片下载失败时的重试次数
   - HTTP请求超时：设置HTTP请求超时时间（秒）
   - 限速：限制下载速度，如 15M (15MB/s) 或 100K (100KB/s)

3. 高级设置：
   - 点击"高级设置"按钮可访问更多选项
   - 包括请求头设置、解密设置、轨道选择等功能

4. 操作：
   - 点击"开始下载"启动下载任务
   - 点击"停止下载"终止当前下载
   - 日志区域显示下载过程信息
        """
        messagebox.showinfo("使用说明", instructions)
    
    def on_closing(self):
        """窗口关闭时的处理"""
        # 检查是否有正在运行的任务
        running_tasks = [task for task in self.tasks.values() if task.is_running]
        if running_tasks:
            # 询问用户是否确定要关闭
            if not messagebox.askyesno("确认关闭", f"有 {len(running_tasks)} 个任务正在运行，确定要关闭程序吗？\n关闭后所有正在运行的任务将被停止。"):
                return  # 用户选择取消关闭
        
        # 停止所有正在运行的任务
        for task in running_tasks:
            self.stop_task(task.task_id)
            
        # 保存当前配置
        self.save_full_config()
        # 退出程序
        self.root.quit()
    
    def save_full_config(self):
        """保存完整配置到文件"""
        try:
            config = self.get_all_config()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置文件时出错: {str(e)}")
    
    def load_config(self):
        """从配置文件加载设置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)  # 保存配置数据供高级设置使用
                
                # 加载基本设置
                self.save_dir.set(self.config_data.get('save_dir', ''))
                self.tmp_dir.set(self.config_data.get('tmp_dir', ''))
                self.thread_count.set(self.config_data.get('thread_count', '4'))
                self.download_retry_count.set(self.config_data.get('download_retry_count', '3'))
                self.http_request_timeout.set(self.config_data.get('http_request_timeout', '100'))
                self.log_level.set(self.config_data.get('log_level', 'INFO'))
                self.sub_format.set(self.config_data.get('sub_format', 'SRT'))
                self.custom_proxy.set(self.config_data.get('custom_proxy', ''))
                self.max_speed.set(self.config_data.get('max_speed', ''))
                
                # 加载路径设置
                self.ffmpeg_binary_path.set(self.config_data.get('ffmpeg_binary_path', ''))
                self.decryption_binary_path.set(self.config_data.get('decryption_binary_path', ''))
                self.decryption_engine.set(self.config_data.get('decryption_engine', 'MP4DECRYPT'))
                
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件时出错: {str(e)}")
    
    def load_advanced_config(self):
        """加载高级设置配置"""
        if hasattr(self, 'config_data') and self.config_data:
            # 检查是否存在高级设置窗口
            if hasattr(self, 'advanced_window') and self.advanced_window:
                # 如果存在高级设置窗口，设置其配置
                self.advanced_window.set_config(self.config_data)
    
    def save_config(self):
        """保存设置到配置文件"""
        self.save_full_config()
    
    def get_all_config(self):
        """获取所有配置，包括高级设置"""
        try:
            config = {
                'save_dir': self.save_dir.get(),
                'tmp_dir': self.tmp_dir.get(),
                'thread_count': self.thread_count.get(),
                'download_retry_count': self.download_retry_count.get(),
                'http_request_timeout': self.http_request_timeout.get(),
                'log_level': self.log_level.get(),
                'sub_format': self.sub_format.get(),
                'custom_proxy': self.custom_proxy.get(),
                'max_speed': self.max_speed.get(),
                'ffmpeg_binary_path': self.ffmpeg_binary_path.get(),
                'decryption_binary_path': self.decryption_binary_path.get(),
                'decryption_engine': self.decryption_engine.get()
            }
            
            # 如果高级设置窗口存在，也保存其中的设置
            if hasattr(self, 'advanced_window') and self.advanced_window:
                config.update({
                    # 基本设置
                    'auto_select': self.advanced_window.auto_select.get(),
                    'skip_merge': self.advanced_window.skip_merge.get(),
                    'skip_download': self.advanced_window.skip_download.get(),
                    'binary_merge': self.advanced_window.binary_merge.get(),
                    'del_after_done': self.advanced_window.del_after_done.get(),
                    'no_date_info': self.advanced_window.no_date_info.get(),
                    'no_log': self.advanced_window.no_log.get(),
                    'write_meta_json': self.advanced_window.write_meta_json.get(),
                    'append_url_params': self.advanced_window.append_url_params.get(),
                    'concurrent_download': self.advanced_window.concurrent_download.get(),
                    'auto_subtitle_fix': self.advanced_window.auto_subtitle_fix.get(),
                    'use_system_proxy': self.advanced_window.use_system_proxy.get(),
                    'live_perform_as_vod': self.advanced_window.live_perform_as_vod.get(),
                    'live_real_time_merge': self.advanced_window.live_real_time_merge.get(),
                    'live_keep_segments': self.advanced_window.live_keep_segments.get(),
                    'live_pipe_mux': self.advanced_window.live_pipe_mux.get(),
                    'live_fix_vtt_by_audio': self.advanced_window.live_fix_vtt_by_audio.get(),
                    'disable_update_check': self.advanced_window.disable_update_check.get(),
                    'allow_hls_multi_ext_map': self.advanced_window.allow_hls_multi_ext_map.get(),
                    
                    # 请求头
                    'headers': [(hk.get(), hv.get()) for hk, hv in self.advanced_window.headers_vars if hk.get().strip() and hv.get().strip()],
                    
                    # 解密设置
                    'decryption_engine_var': self.advanced_window.decryption_engine_var.get(),
                    'decryption_path_var': self.advanced_window.decryption_path_var.get(),
                    'decryption_key_var': self.advanced_window.decryption_key_var.get(),
                    'key_file_var': self.advanced_window.key_file_var.get(),
                    'mp4_real_time_decryption': self.advanced_window.mp4_real_time_decryption.get(),
                    'custom_hls_method_var': self.advanced_window.custom_hls_method_var.get(),
                    'custom_hls_key_var': self.advanced_window.custom_hls_key_var.get(),
                    'custom_hls_iv_var': self.advanced_window.custom_hls_iv_var.get(),
                    
                    # 混流设置
                    'mux_after_done_var': self.advanced_window.mux_after_done_var.get(),
                    'mux_import_var': self.advanced_window.mux_import_var.get(),
                    
                    # 轨道选择
                    'select_video_var': self.advanced_window.select_video_var.get(),
                    'select_audio_var': self.advanced_window.select_audio_var.get(),
                    'select_subtitle_var': self.advanced_window.select_subtitle_var.get(),
                    'drop_video_var': self.advanced_window.drop_video_var.get(),
                    'drop_audio_var': self.advanced_window.drop_audio_var.get(),
                    'drop_subtitle_var': self.advanced_window.drop_subtitle_var.get(),
                    
                    # 其他设置
                    'base_url_var': self.advanced_window.base_url_var.get(),
                    'save_pattern_var': self.advanced_window.save_pattern_var.get(),
                    'log_file_path_var': self.advanced_window.log_file_path_var.get(),
                    'urlprocessor_args_var': self.advanced_window.urlprocessor_args_var.get(),
                    'sub_only_var': self.advanced_window.sub_only.get(),
                    'live_record_limit_var': self.advanced_window.live_record_limit_var.get(),
                    'live_wait_time_var': self.advanced_window.live_wait_time_var.get(),
                    'live_take_count_var': self.advanced_window.live_take_count_var.get(),
                    'ad_keyword_var': self.advanced_window.ad_keyword_var.get()
                })
            
            return config
        except Exception as e:
            messagebox.showerror("错误", f"获取配置时出错: {str(e)}")
            return {}
    
    def load_all_config(self, config):
        """加载所有配置，包括高级设置"""
        try:
            # 加载基本设置
            self.save_dir.set(config.get('save_dir', ''))
            self.tmp_dir.set(config.get('tmp_dir', ''))
            self.thread_count.set(config.get('thread_count', '4'))
            self.download_retry_count.set(config.get('download_retry_count', '3'))
            self.http_request_timeout.set(config.get('http_request_timeout', '100'))
            self.log_level.set(config.get('log_level', 'INFO'))
            self.sub_format.set(config.get('sub_format', 'SRT'))
            self.custom_proxy.set(config.get('custom_proxy', ''))
            self.max_speed.set(config.get('max_speed', ''))
            
            # 加载路径设置
            self.ffmpeg_binary_path.set(config.get('ffmpeg_binary_path', ''))
            self.decryption_binary_path.set(config.get('decryption_binary_path', ''))
            self.decryption_engine.set(config.get('decryption_engine', 'MP4DECRYPT'))
            
        except Exception as e:
            messagebox.showerror("错误", f"加载配置时出错: {str(e)}")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
N_m3u8DL-RE GUI

版本：1.0
作者：Assistant
基于 N_m3u8DL-RE (Beta version 20251027) 开发

这是一个图形化界面工具，用于方便地使用 N_m3u8DL-RE 下载m3u8格式的视频流。
        """
        messagebox.showinfo("关于", about_text)


class AdvancedSettingsWindow:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("高级设置")
        self.window.geometry("700x500")
        
        # 当窗口关闭时清理引用
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 创建高级设置界面
        self.create_advanced_widgets()
    
    def winfo_exists(self):
        """检查窗口是否仍然存在"""
        try:
            return self.window.winfo_exists()
        except tk.TclError:
            return False
    
    def on_close(self):
        """当窗口关闭时的处理"""
        # 清理对窗口的引用
        if hasattr(self.main_app, 'advanced_window') and self.main_app.advanced_window == self:
            self.main_app.advanced_window = None
        self.window.destroy()
        
    def create_advanced_widgets(self):
        # 创建笔记本控件（选项卡）
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建各个选项卡
        self.create_basic_tab(notebook)
        self.create_headers_tab(notebook)
        self.create_decryption_tab(notebook)
        self.create_mux_tab(notebook)
        self.create_selection_tab(notebook)
        self.create_other_tab(notebook)
        
    def create_basic_tab(self, notebook):
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本设置")
        
        # 创建变量
        self.auto_select = tk.BooleanVar()
        self.skip_merge = tk.BooleanVar()
        self.skip_download = tk.BooleanVar()
        self.binary_merge = tk.BooleanVar()
        self.del_after_done = tk.BooleanVar()
        self.no_date_info = tk.BooleanVar()
        self.no_log = tk.BooleanVar()
        self.write_meta_json = tk.BooleanVar()
        self.append_url_params = tk.BooleanVar()
        self.concurrent_download = tk.BooleanVar()
        self.auto_subtitle_fix = tk.BooleanVar()
        self.use_system_proxy = tk.BooleanVar()
        self.live_perform_as_vod = tk.BooleanVar()
        self.live_real_time_merge = tk.BooleanVar()
        self.live_keep_segments = tk.BooleanVar()
        self.live_pipe_mux = tk.BooleanVar()
        self.live_fix_vtt_by_audio = tk.BooleanVar()
        self.disable_update_check = tk.BooleanVar()
        self.allow_hls_multi_ext_map = tk.BooleanVar()
        
        # 创建复选框
        ttk.Checkbutton(basic_frame, text="自动选择最佳轨道", variable=self.auto_select).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="跳过合并分片", variable=self.skip_merge).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="跳过下载", variable=self.skip_download).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="二进制合并", variable=self.binary_merge).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="完成后删除临时文件", variable=self.del_after_done).grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="混流时不写入日期信息", variable=self.no_date_info).grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="关闭日志文件输出", variable=self.no_log).grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="输出解析信息到JSON文件", variable=self.write_meta_json).grid(row=7, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="将输入URL参数添加至分片", variable=self.append_url_params).grid(row=8, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="并发下载音视频字幕", variable=self.concurrent_download).grid(row=9, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="自动修正字幕", variable=self.auto_subtitle_fix).grid(row=10, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="使用系统默认代理", variable=self.use_system_proxy).grid(row=11, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="以点播方式下载直播流", variable=self.live_perform_as_vod).grid(row=12, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="录制直播时实时合并", variable=self.live_real_time_merge).grid(row=13, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="保留直播分片", variable=self.live_keep_segments).grid(row=14, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="管道实时混流", variable=self.live_pipe_mux).grid(row=15, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="通过音频修正VTT字幕", variable=self.live_fix_vtt_by_audio).grid(row=16, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="禁用版本更新检测", variable=self.disable_update_check).grid(row=17, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="允许HLS中多个EXT-X-MAP", variable=self.allow_hls_multi_ext_map).grid(row=18, column=0, sticky=tk.W, pady=2)
        
    def create_headers_tab(self, notebook):
        headers_frame = ttk.Frame(notebook, padding="10")
        notebook.add(headers_frame, text="请求头")
        
        self.headers = []
        self.headers_vars = []
        self.add_header_row(headers_frame)
        
        ttk.Button(headers_frame, text="添加请求头", command=lambda: self.add_header_row(headers_frame)).grid(row=1, column=0, pady=5)
        
    def add_header_row(self, parent):
        row = len(self.headers)
        header_key = tk.StringVar()
        header_value = tk.StringVar()
        self.headers_vars.append((header_key, header_value))
        
        ttk.Label(parent, text="键:").grid(row=row+2, column=0, padx=5, pady=2)
        ttk.Entry(parent, textvariable=header_key, width=20).grid(row=row+2, column=1, padx=5, pady=2)
        ttk.Label(parent, text="值:").grid(row=row+2, column=2, padx=5, pady=2)
        ttk.Entry(parent, textvariable=header_value, width=40).grid(row=row+2, column=3, padx=5, pady=2)
        
    def create_decryption_tab(self, notebook):
        decryption_frame = ttk.Frame(notebook, padding="10")
        notebook.add(decryption_frame, text="解密设置")
        
        # 解密引擎
        ttk.Label(decryption_frame, text="解密引擎:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.decryption_engine_var = tk.StringVar(value="MP4DECRYPT")
        decryption_engine_combo = ttk.Combobox(decryption_frame, textvariable=self.decryption_engine_var, 
                                               values=["FFMPEG", "MP4DECRYPT", "SHAKA_PACKAGER"], state="readonly", width=17)
        decryption_engine_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # 解密工具路径
        ttk.Label(decryption_frame, text="解密工具路径:").grid(row=1, column=0, sticky=tk.W, pady=2)
        decryption_path_frame = ttk.Frame(decryption_frame)
        decryption_path_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        decryption_path_frame.columnconfigure(0, weight=1)
        self.decryption_path_var = tk.StringVar()
        ttk.Entry(decryption_path_frame, textvariable=self.decryption_path_var, width=70).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(decryption_path_frame, text="浏览", command=self.browse_decryption_path).grid(row=0, column=1)
        
        # 解密密钥
        ttk.Label(decryption_frame, text="解密密钥 (格式: KID1:KEY1 或直接输入KEY):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.decryption_key_var = tk.StringVar()
        ttk.Entry(decryption_frame, textvariable=self.decryption_key_var, width=80).grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 密钥文件
        ttk.Label(decryption_frame, text="密钥文件:").grid(row=5, column=0, sticky=tk.W, pady=2)
        key_file_frame = ttk.Frame(decryption_frame)
        key_file_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        key_file_frame.columnconfigure(0, weight=1)
        self.key_file_var = tk.StringVar()
        ttk.Entry(key_file_frame, textvariable=self.key_file_var, width=70).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(key_file_frame, text="浏览", command=self.browse_key_file).grid(row=0, column=1)
        
        # 实时解密
        self.mp4_real_time_decryption = tk.BooleanVar()
        ttk.Checkbutton(decryption_frame, text="实时解密MP4分片", variable=self.mp4_real_time_decryption).grid(row=7, column=0, sticky=tk.W, pady=2)
        
        # 自定义HLS设置
        ttk.Label(decryption_frame, text="自定义HLS加密方式:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.custom_hls_method_var = tk.StringVar()
        ttk.Combobox(decryption_frame, textvariable=self.custom_hls_method_var, 
                     values=["AES_128", "AES_128_ECB", "CENC", "CHACHA20", "NONE", "SAMPLE_AES", "SAMPLE_AES_CTR", "UNKNOWN"], 
                     state="readonly", width=17).grid(row=8, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(decryption_frame, text="自定义HLS密钥:").grid(row=9, column=0, sticky=tk.W, pady=2)
        self.custom_hls_key_var = tk.StringVar()
        ttk.Entry(decryption_frame, textvariable=self.custom_hls_key_var, width=80).grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(decryption_frame, text="自定义HLS IV:").grid(row=11, column=0, sticky=tk.W, pady=2)
        self.custom_hls_iv_var = tk.StringVar()
        ttk.Entry(decryption_frame, textvariable=self.custom_hls_iv_var, width=80).grid(row=12, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
    def browse_decryption_path(self):
        file_path = filedialog.askopenfilename(filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")])
        if file_path:
            self.decryption_path_var.set(file_path)
            
    def browse_key_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if file_path:
            self.key_file_var.set(file_path)
        
    def create_mux_tab(self, notebook):
        mux_frame = ttk.Frame(notebook, padding="10")
        notebook.add(mux_frame, text="混流设置")
        
        ttk.Label(mux_frame, text="完成后混流:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.mux_after_done_var = tk.StringVar()
        ttk.Entry(mux_frame, textvariable=self.mux_after_done_var, width=80).grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(mux_frame, text="混流时引入外部媒体:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.mux_import_var = tk.StringVar()
        ttk.Entry(mux_frame, textvariable=self.mux_import_var, width=80).grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
    def create_selection_tab(self, notebook):
        selection_frame = ttk.Frame(notebook, padding="10")
        notebook.add(selection_frame, text="轨道选择")
        
        # 选择视频
        ttk.Label(selection_frame, text="选择视频流 (正则表达式):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.select_video_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.select_video_var, width=80).grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 选择音频
        ttk.Label(selection_frame, text="选择音频流 (正则表达式):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.select_audio_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.select_audio_var, width=80).grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 选择字幕
        ttk.Label(selection_frame, text="选择字幕流 (正则表达式):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.select_subtitle_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.select_subtitle_var, width=80).grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 去除视频
        ttk.Label(selection_frame, text="去除视频流 (正则表达式):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.drop_video_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.drop_video_var, width=80).grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 去除音频
        ttk.Label(selection_frame, text="去除音频流 (正则表达式):").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.drop_audio_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.drop_audio_var, width=80).grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 去除字幕
        ttk.Label(selection_frame, text="去除字幕流 (正则表达式):").grid(row=10, column=0, sticky=tk.W, pady=2)
        self.drop_subtitle_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.drop_subtitle_var, width=80).grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
    def create_other_tab(self, notebook):
        other_frame = ttk.Frame(notebook, padding="10")
        notebook.add(other_frame, text="其他设置")
        
        # 基础URL
        ttk.Label(other_frame, text="基础URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.base_url_var = tk.StringVar()
        ttk.Entry(other_frame, textvariable=self.base_url_var, width=80).grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 保存命名模板
        ttk.Label(other_frame, text="保存文件命名模板:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.save_pattern_var = tk.StringVar()
        ttk.Entry(other_frame, textvariable=self.save_pattern_var, width=80).grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(other_frame, text="<SaveName>, <Id>, <Codecs>, <Language>, <Resolution>, <Bandwidth>, <MediaType>, <Channels>, <FrameRate>, <VideoRange>, <GroupId>, <Ext>").grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 日志文件路径
        ttk.Label(other_frame, text="日志文件路径:").grid(row=5, column=0, sticky=tk.W, pady=2)
        log_file_frame = ttk.Frame(other_frame)
        log_file_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        log_file_frame.columnconfigure(0, weight=1)
        self.log_file_path_var = tk.StringVar()
        ttk.Entry(log_file_frame, textvariable=self.log_file_path_var, width=70).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(log_file_frame, text="浏览", command=self.browse_log_file).grid(row=0, column=1)
        
        # URL处理器参数
        ttk.Label(other_frame, text="URL处理器参数:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.urlprocessor_args_var = tk.StringVar()
        ttk.Entry(other_frame, textvariable=self.urlprocessor_args_var, width=80).grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # 仅字幕轨道
        self.sub_only = tk.BooleanVar()
        ttk.Checkbutton(other_frame, text="只选取字幕轨道", variable=self.sub_only).grid(row=9, column=0, sticky=tk.W, pady=2)
        
        # 录制时长限制
        ttk.Label(other_frame, text="录制时长限制 (HH:mm:ss):").grid(row=10, column=0, sticky=tk.W, pady=2)
        self.live_record_limit_var = tk.StringVar()
        ttk.Entry(other_frame, textvariable=self.live_record_limit_var, width=20).grid(row=10, column=1, sticky=tk.W, pady=2)
        
        # 直播刷新间隔
        ttk.Label(other_frame, text="直播列表刷新间隔:").grid(row=11, column=0, sticky=tk.W, pady=2)
        self.live_wait_time_var = tk.StringVar()
        ttk.Entry(other_frame, textvariable=self.live_wait_time_var, width=20).grid(row=11, column=1, sticky=tk.W, pady=2)
        
        # 首次获取分片数量
        ttk.Label(other_frame, text="首次获取分片数量:").grid(row=12, column=0, sticky=tk.W, pady=2)
        self.live_take_count_var = tk.StringVar(value="16")
        ttk.Entry(other_frame, textvariable=self.live_take_count_var, width=20).grid(row=12, column=1, sticky=tk.W, pady=2)
        
        # 广告关键字
        ttk.Label(other_frame, text="广告分片URL关键字 (正则):").grid(row=13, column=0, sticky=tk.W, pady=2)
        self.ad_keyword_var = tk.StringVar()
        ttk.Entry(other_frame, textvariable=self.ad_keyword_var, width=80).grid(row=14, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
    def browse_log_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if file_path:
            self.log_file_path_var.set(file_path)
    
    def set_config(self, config):
        """根据配置设置控件值"""
        try:
            # 基本设置
            self.auto_select.set(config.get('auto_select', False))
            self.skip_merge.set(config.get('skip_merge', False))
            self.skip_download.set(config.get('skip_download', False))
            self.binary_merge.set(config.get('binary_merge', False))
            self.del_after_done.set(config.get('del_after_done', True))
            self.no_date_info.set(config.get('no_date_info', False))
            self.no_log.set(config.get('no_log', False))
            self.write_meta_json.set(config.get('write_meta_json', True))
            self.append_url_params.set(config.get('append_url_params', False))
            self.concurrent_download.set(config.get('concurrent_download', False))
            self.auto_subtitle_fix.set(config.get('auto_subtitle_fix', True))
            self.use_system_proxy.set(config.get('use_system_proxy', True))
            self.live_perform_as_vod.set(config.get('live_perform_as_vod', False))
            self.live_real_time_merge.set(config.get('live_real_time_merge', False))
            self.live_keep_segments.set(config.get('live_keep_segments', True))
            self.live_pipe_mux.set(config.get('live_pipe_mux', False))
            self.live_fix_vtt_by_audio.set(config.get('live_fix_vtt_by_audio', False))
            self.disable_update_check.set(config.get('disable_update_check', False))
            self.allow_hls_multi_ext_map.set(config.get('allow_hls_multi_ext_map', False))
            
            # 请求头 - 清除现有的行并添加保存的行
            for i in range(len(self.headers_vars)-1, -1, -1):  # 从后往前删除，避免索引问题
                if i < len(self.headers_vars):
                    # 这里我们不实际删除控件，而是简单地清空列表
                    del self.headers_vars[i]
            
            # 重新添加请求头
            headers = config.get('headers', [])
            for header_key_val, header_value_val in headers:
                header_key = tk.StringVar(value=header_key_val)
                header_value = tk.StringVar(value=header_value_val)
                self.headers_vars.append((header_key, header_value))
            
            # 解密设置
            self.decryption_engine_var.set(config.get('decryption_engine_var', 'MP4DECRYPT'))
            self.decryption_path_var.set(config.get('decryption_path_var', ''))
            self.decryption_key_var.set(config.get('decryption_key_var', ''))
            self.key_file_var.set(config.get('key_file_var', ''))
            self.mp4_real_time_decryption.set(config.get('mp4_real_time_decryption', False))
            self.custom_hls_method_var.set(config.get('custom_hls_method_var', ''))
            self.custom_hls_key_var.set(config.get('custom_hls_key_var', ''))
            self.custom_hls_iv_var.set(config.get('custom_hls_iv_var', ''))
            
            # 混流设置
            self.mux_after_done_var.set(config.get('mux_after_done_var', ''))
            self.mux_import_var.set(config.get('mux_import_var', ''))
            
            # 轨道选择
            self.select_video_var.set(config.get('select_video_var', ''))
            self.select_audio_var.set(config.get('select_audio_var', ''))
            self.select_subtitle_var.set(config.get('select_subtitle_var', ''))
            self.drop_video_var.set(config.get('drop_video_var', ''))
            self.drop_audio_var.set(config.get('drop_audio_var', ''))
            self.drop_subtitle_var.set(config.get('drop_subtitle_var', ''))
            
            # 其他设置
            self.base_url_var.set(config.get('base_url_var', ''))
            self.save_pattern_var.set(config.get('save_pattern_var', ''))
            self.log_file_path_var.set(config.get('log_file_path_var', ''))
            self.urlprocessor_args_var.set(config.get('urlprocessor_args_var', ''))
            self.sub_only.set(config.get('sub_only_var', False))
            self.live_record_limit_var.set(config.get('live_record_limit_var', ''))
            self.live_wait_time_var.set(config.get('live_wait_time_var', ''))
            self.live_take_count_var.set(config.get('live_take_count_var', '16'))
            self.ad_keyword_var.set(config.get('ad_keyword_var', ''))
            
        except Exception as e:
            messagebox.showerror("错误", f"设置高级配置时出错: {str(e)}")


def main():
    root = tk.Tk()
    app = M3u8DLGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()