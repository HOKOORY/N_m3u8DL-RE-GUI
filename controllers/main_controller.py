"""
主控制器 - 协调模型和视图之间的交互
"""
from models.task_manager import DownloadManager
from models.config_manager import ConfigManager
from models.task_builder import TaskCommandBuilder
from views.main_view import MainView
import tkinter as tk
from tkinter import messagebox


class MainController:
    """主控制器 - 协调GUI界面和业务逻辑"""
    
    def __init__(self, root):
        self.root = root
        self.selected_task_id = None  # 跟踪当前选中的任务ID
        self.download_manager = DownloadManager(self.update_task_list, self.update_task_log)  # 传递回调函数
        self.config_manager = ConfigManager()
        
        # 创建主视图
        self.view = MainView(root, self)
        
        # 加载配置
        self.load_config()
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_config(self):
        """加载配置到视图"""
        config = self.config_manager.get_config()
        if config:
            self.view.load_config(config)
    
    def save_config(self):
        """保存配置"""
        config = self.view.get_config()
        return self.config_manager.save_config(config)
    
    def add_task(self, url, save_dir, save_name, tmp_dir, config):
        """添加下载任务"""
        if not url.strip():
            messagebox.showerror("错误", "请输入URL或文件路径")
            return
        
        task_id, task = self.download_manager.add_task(url, save_dir, save_name, tmp_dir, config)
        
        # 添加到视图的列表中
        self.view.add_task_to_list(task_id, task)
        
        # 自动开始下载任务
        self.start_task(task_id)
        
        # 自动切换到任务管理选项卡
        self.view.switch_to_task_manager_tab()
    
    def start_task(self, task_id):
        """开始指定任务"""
        self.download_manager.start_task(task_id)
    
    def start_selected_task(self):
        """开始选中的任务"""
        selected_task_ids = self.view.get_selected_task_ids()
        if not selected_task_ids:
            messagebox.showwarning("警告", "请先选择要开始的任务")
            return
        
        for task_id in selected_task_ids:
            self.start_task(task_id)
    
    def start_all_pending_tasks(self):
        """开始所有待开始的任务"""
        self.download_manager.start_all_pending_tasks()
    
    def delete_selected_task(self):
        """删除选中的任务"""
        selected_task_ids = self.view.get_selected_task_ids()
        if not selected_task_ids:
            messagebox.showwarning("警告", "请先选择要删除的任务")
            return
        
        for task_id in selected_task_ids:
            # 从管理器中删除（delete_task会处理停止任务和清理临时文件）
            self.download_manager.delete_task(task_id)
            # 从视图中删除
            self.view.remove_task_from_list(task_id)
    
    def clear_all_tasks(self):
        """清空所有任务"""
        # 清空任务列表（会自动停止运行中的任务并清理临时文件）
        self.download_manager.clear_all_tasks()
        
        # 从视图中清空
        self.view.clear_task_list()
    
    def update_task_list(self):
        """更新任务列表的回调函数"""
        # 在主线程中更新GUI
        self.root.after(0, self.view.update_task_list)
    
    def on_task_select(self, event):
        """任务选择事件处理"""
        selected_task_ids = self.view.get_selected_task_ids()
        if selected_task_ids:
            self.selected_task_id = selected_task_ids[0]
            task = self.download_manager.tasks.get(self.selected_task_id)
            if task:
                self.view.show_task_log(task)
    
    def update_task_log(self, task_id):
        """更新特定任务的日志显示（用于实时更新）"""
        # 检查当前选中的任务是否是正在更新日志的任务
        if self.selected_task_id == task_id:
            task = self.download_manager.tasks.get(task_id)
            if task:
                self.view.append_task_log(task)
    
    def on_closing(self):
        """窗口关闭时的处理"""
        # 检查是否有正在运行的任务
        running_tasks = [task for task in self.download_manager.get_all_tasks().values() if task.is_running]
        if running_tasks:
            # 询问用户是否确定要关闭
            if not messagebox.askyesno("确认关闭", f"有 {len(running_tasks)} 个任务正在运行，确定要关闭程序吗？\n关闭后所有正在运行的任务将被停止。"):
                return  # 用户选择取消关闭
        
        # 停止所有正在运行的任务
        for task in running_tasks:
            self.download_manager.stop_task(task.task_id)
            
        # 保存当前配置
        self.save_config()
        # 退出程序
        self.root.quit()
    
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
