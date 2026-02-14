"""
高级设置视图
"""
import tkinter as tk
from tkinter import ttk, filedialog


class AdvancedSettingsView:
    """高级设置视图类"""
    
    def __init__(self, parent, main_view):
        self.parent = parent
        self.main_view = main_view
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
        if hasattr(self.main_view, 'advanced_window') and self.main_view.advanced_window == self:
            self.main_view.advanced_window = None
        self.window.destroy()
        
    def create_advanced_widgets(self):
        """创建高级设置界面组件"""
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
        """创建基本设置选项卡"""
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
        """创建请求头选项卡"""
        headers_frame = ttk.Frame(notebook, padding="10")
        notebook.add(headers_frame, text="请求头")
        
        self.headers = []
        self.headers_vars = []
        self.add_header_row(headers_frame)
        
        ttk.Button(headers_frame, text="添加请求头", command=lambda: self.add_header_row(headers_frame)).grid(row=1, column=0, pady=5)
    
    def add_header_row(self, parent):
        """添加请求头行"""
        row = len(self.headers)
        header_key = tk.StringVar()
        header_value = tk.StringVar()
        self.headers_vars.append((header_key, header_value))
        
        ttk.Label(parent, text="键:").grid(row=row+2, column=0, padx=5, pady=2)
        ttk.Entry(parent, textvariable=header_key, width=20).grid(row=row+2, column=1, padx=5, pady=2)
        ttk.Label(parent, text="值:").grid(row=row+2, column=2, padx=5, pady=2)
        ttk.Entry(parent, textvariable=header_value, width=40).grid(row=row+2, column=3, padx=5, pady=2)
    
    def create_decryption_tab(self, notebook):
        """创建解密设置选项卡"""
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
        """浏览解密工具路径"""
        file_path = filedialog.askopenfilename(filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")])
        if file_path:
            self.decryption_path_var.set(file_path)
    
    def browse_key_file(self):
        """浏览密钥文件"""
        file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if file_path:
            self.key_file_var.set(file_path)
    
    def create_mux_tab(self, notebook):
        """创建混流设置选项卡"""
        mux_frame = ttk.Frame(notebook, padding="10")
        notebook.add(mux_frame, text="混流设置")
        
        ttk.Label(mux_frame, text="完成后混流:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.mux_after_done_var = tk.StringVar()
        ttk.Entry(mux_frame, textvariable=self.mux_after_done_var, width=80).grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(mux_frame, text="混流时引入外部媒体:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.mux_import_var = tk.StringVar()
        ttk.Entry(mux_frame, textvariable=self.mux_import_var, width=80).grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
    
    def create_selection_tab(self, notebook):
        """创建轨道选择选项卡"""
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
        """创建其他设置选项卡"""
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
        """浏览日志文件"""
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
    
    def get_config(self):
        """获取当前配置"""
        config = {
            # 基本设置
            'auto_select': self.auto_select.get(),
            'skip_merge': self.skip_merge.get(),
            'skip_download': self.skip_download.get(),
            'binary_merge': self.binary_merge.get(),
            'del_after_done': self.del_after_done.get(),
            'no_date_info': self.no_date_info.get(),
            'no_log': self.no_log.get(),
            'write_meta_json': self.write_meta_json.get(),
            'append_url_params': self.append_url_params.get(),
            'concurrent_download': self.concurrent_download.get(),
            'auto_subtitle_fix': self.auto_subtitle_fix.get(),
            'use_system_proxy': self.use_system_proxy.get(),
            'live_perform_as_vod': self.live_perform_as_vod.get(),
            'live_real_time_merge': self.live_real_time_merge.get(),
            'live_keep_segments': self.live_keep_segments.get(),
            'live_pipe_mux': self.live_pipe_mux.get(),
            'live_fix_vtt_by_audio': self.live_fix_vtt_by_audio.get(),
            'disable_update_check': self.disable_update_check.get(),
            'allow_hls_multi_ext_map': self.allow_hls_multi_ext_map.get(),
            
            # 请求头
            'headers': [(hk.get(), hv.get()) for hk, hv in self.headers_vars if hk.get().strip() and hv.get().strip()],
            
            # 解密设置
            'decryption_engine_var': self.decryption_engine_var.get(),
            'decryption_path_var': self.decryption_path_var.get(),
            'decryption_key_var': self.decryption_key_var.get(),
            'key_file_var': self.key_file_var.get(),
            'mp4_real_time_decryption': self.mp4_real_time_decryption.get(),
            'custom_hls_method_var': self.custom_hls_method_var.get(),
            'custom_hls_key_var': self.custom_hls_key_var.get(),
            'custom_hls_iv_var': self.custom_hls_iv_var.get(),
            
            # 混流设置
            'mux_after_done_var': self.mux_after_done_var.get(),
            'mux_import_var': self.mux_import_var.get(),
            
            # 轨道选择
            'select_video_var': self.select_video_var.get(),
            'select_audio_var': self.select_audio_var.get(),
            'select_subtitle_var': self.select_subtitle_var.get(),
            'drop_video_var': self.drop_video_var.get(),
            'drop_audio_var': self.drop_audio_var.get(),
            'drop_subtitle_var': self.drop_subtitle_var.get(),
            
            # 其他设置
            'base_url_var': self.base_url_var.get(),
            'save_pattern_var': self.save_pattern_var.get(),
            'log_file_path_var': self.log_file_path_var.get(),
            'urlprocessor_args_var': self.urlprocessor_args_var.get(),
            'sub_only_var': self.sub_only.get(),
            'live_record_limit_var': self.live_record_limit_var.get(),
            'live_wait_time_var': self.live_wait_time_var.get(),
            'live_take_count_var': self.live_take_count_var.get(),
            'ad_keyword_var': self.ad_keyword_var.get()
        }
        
        return config