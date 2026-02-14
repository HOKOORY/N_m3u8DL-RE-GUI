"""
主视图 - GUI界面层
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from views.advanced_settings_view import AdvancedSettingsView

class MainView:
    """主视图类 - 负责GUI界面的展示和用户交互"""
    
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        # 设置窗口
        self.root.title("N_m3u8DL-RE GUI - 多任务版")
        self.root.geometry("1200x800")
        
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
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 创建界面元素
        self.create_widgets()
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 配置主框架行权重
        self.main_frame.rowconfigure(0, weight=1)

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存当前配置", command=self.controller.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.controller.show_instructions)
        help_menu.add_command(label="关于", command=self.controller.show_about)
    
    def create_widgets(self):
        """创建界面组件"""
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
        ttk.Label(self.task_config_frame, text="限速 (如: 15M, 100K): ").grid(row=15, column=0, sticky=tk.W, pady=(10, 2))
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
        
        ttk.Button(task_button_frame, text="开始选中任务", command=self.controller.start_selected_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_button_frame, text="删除选中任务", command=self.controller.delete_selected_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_button_frame, text="清空所有任务", command=self.controller.clear_all_tasks).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_button_frame, text="开始所有待开始任务", command=self.controller.start_all_pending_tasks).pack(side=tk.LEFT, padx=(0, 5))
        
        # 任务日志显示区域
        ttk.Label(self.task_manager_frame, text="任务日志:").grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        self.task_log_text = scrolledtext.ScrolledText(self.task_manager_frame, height=15, width=100)
        self.task_log_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        
        # 绑定任务列表选择事件
        self.task_tree.bind("<<TreeviewSelect>>", self.controller.on_task_select)
        
    def browse_save_dir(self):
        """浏览保存目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir.set(directory)
            
    def browse_tmp_dir(self):
        """浏览临时目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.tmp_dir.set(directory)
    
    def open_advanced_settings(self):
        """打开高级设置窗口"""
        # 检查是否已存在高级设置窗口
        if not hasattr(self, 'advanced_window') or not self.advanced_window or not self.advanced_window.window.winfo_exists():
            self.advanced_window = AdvancedSettingsView(self.root, self)
            # 如果有已保存的配置，加载到高级设置窗口
            config = self.controller.config_manager.get_config()
            if config:
                self.advanced_window.set_config(config)
        else:
            # 如果窗口已存在，将其带到前台
            self.advanced_window.window.lift()
            self.advanced_window.window.focus_force()
    
    def add_task(self):
        """添加任务到列表"""
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
            config.update(self.advanced_window.get_config())
        
        # 添加任务到控制器
        self.controller.add_task(
            self.input_url.get(),
            self.save_dir.get(),
            self.save_name.get(),
            self.tmp_dir.get(),
            config
        )
    
    def add_task_to_list(self, task_id, task):
        """在任务列表中添加任务"""
        self.task_tree.insert("", "end", values=(
            task_id,
            task.url,
            task.save_dir,
            task.status,
            "",  # 开始时间
            ""   # 结束时间
        ))
    
    def remove_task_from_list(self, task_id):
        """从任务列表中移除任务"""
        for item in self.task_tree.get_children():
            values = self.task_tree.item(item, "values")
            if int(values[0]) == task_id:
                self.task_tree.delete(item)
                break
    
    def update_task_list(self):
        """更新整个任务列表显示"""
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
        for task_id, task in self.controller.download_manager.get_all_tasks().items():
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
    
    def update_task_status(self, task_id, status, start_time=None, end_time=None):
        """更新特定任务的状态"""
        for item in self.task_tree.get_children():
            values = self.task_tree.item(item, "values")
            if int(values[0]) == task_id:
                # 保留现有的URL和保存位置，只更新状态和时间
                updated_values = (task_id, values[1], values[2], status, 
                                 start_time or values[4], end_time or values[5])
                self.task_tree.item(item, values=updated_values)
                break
    
    def get_selected_task_ids(self):
        """获取选中的任务ID列表"""
        selected_items = self.task_tree.selection()
        task_ids = []
        for item in selected_items:
            values = self.task_tree.item(item, "values")
            task_ids.append(int(values[0]))
        return task_ids
    
    def clear_task_list(self):
        """清空任务列表"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
    
    def show_task_log(self, task):
        """显示指定任务的完整日志"""
        # 清空当前日志（因为这是切换任务时的完整日志显示）
        self.task_log_text.delete(1.0, tk.END)
        
        # 显示任务的完整日志
        for log_message in task.full_log:
            self.task_log_text.insert(tk.END, log_message + "\n")
        self.task_log_text.see(tk.END)
    
    def append_task_log(self, task):
        """追加显示指定任务的新日志"""
        new_log_count = 0
        # 显示任务的新日志（不删除现有日志）
        while not task.log_queue.empty():
            log_message = task.log_queue.get()
            self.task_log_text.insert(tk.END, log_message + "\n")
            new_log_count += 1
        
        if new_log_count > 0:
            self.task_log_text.see(tk.END)
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
    
    def load_config(self, config):
        """从配置加载设置"""
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
    
    def get_config(self):
        """获取当前配置"""
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
            config.update(self.advanced_window.get_config())
        
        return config
    
    def switch_to_task_manager_tab(self):
        """切换到任务管理选项卡"""
        self.notebook.select(self.task_manager_frame)