"""
下载任务模型
"""
import subprocess
import threading
import os
import json
import time
import queue
from typing import Dict, List, Optional

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
        self.full_log = []  # 保存完整的日志列表
        self.tmp_dir_before_download = set()  # 记录下载前临时目录的文件
        self.current_tmp_dir = ""  # 记录当前使用的临时目录
        self.start_time = None
        self.end_time = None

class DownloadManager:
    """下载管理器 - 业务逻辑层"""
    
    def __init__(self, update_task_list_callback=None, update_task_log_callback=None):
        self.tasks = {}  # 任务字典
        self.next_task_id = 1  # 下一个任务ID
        self.update_task_list_callback = update_task_list_callback  # 用于更新GUI的回调函数
        self.update_task_log_callback = update_task_log_callback  # 用于更新任务日志的回调函数
        
    def add_task(self, url: str, save_dir: str, save_name: str, tmp_dir: str, config: dict):
        """添加下载任务"""
        task = DownloadTask(
            task_id=self.next_task_id,
            url=url.strip(),
            save_dir=save_dir.strip(),
            save_name=save_name.strip(),
            tmp_dir=tmp_dir.strip(),
            config=config
        )
        
        # 添加到任务字典
        self.tasks[self.next_task_id] = task
        
        task_id = self.next_task_id
        self.next_task_id += 1
        
        return task_id, task
    
    def start_task(self, task_id: int):
        """开始指定的下载任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False
            
        # 在新线程中运行下载任务
        threading.Thread(target=self._run_download_task, args=(task,), daemon=True).start()
        return True
    
    def _run_download_task(self, task):
        """运行指定的下载任务（内部方法）"""
        from .task_builder import TaskCommandBuilder  # 延迟导入避免循环依赖
        
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
        
        # 如果有回调函数，通知状态改变
        if self.update_task_list_callback:
            self.update_task_list_callback()
        
        # 构建命令
        cmd = TaskCommandBuilder.build_task_command(task)
        if not cmd:
            task.status = "错误"
            if self.update_task_list_callback:
                self.update_task_list_callback()
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
                    output = output.strip()
                    task.log_queue.put(output)
                    task.full_log.append(output)  # 同时添加到完整日志列表
                    # 如果当前任务被选中，实时更新GUI中的日志显示
                    # 这需要调用日志更新回调函数
                    if self.update_task_log_callback:
                        # 使用after方法确保在主线程中更新GUI
                        self.update_task_log_callback(task.task_id)
                
            # 读取进程结束后可能剩余的输出
            # 这一步很重要，确保读取所有缓冲区中的输出
            remaining_output = task.process.stdout.read()
            if remaining_output:
                for line in remaining_output.splitlines():
                    if line.strip():
                        task.log_queue.put(line.strip())
                        task.full_log.append(line.strip())  # 同时添加到完整日志列表
                        # 同样实时更新GUI
                        if self.update_task_log_callback:
                            self.update_task_log_callback(task.task_id)
                
            # 等待进程结束
            return_code = task.process.wait()  # 使用wait()确保进程完全结束
            task.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            if return_code == 0:
                task.status = "已完成"
                final_message = f"任务 #{task.task_id} 下载完成，退出码: {return_code}"
                task.log_queue.put(final_message)
                task.full_log.append(final_message)  # 同时添加到完整日志列表
            else:
                task.status = "错误"
                final_message = f"任务 #{task.task_id} 下载失败，退出码: {return_code}"
                task.log_queue.put(final_message)
                task.full_log.append(final_message)  # 同时添加到完整日志列表
        except Exception as e:
            task.status = "错误"
            task.log_queue.put(f"任务 #{task.task_id} 下载出错: {str(e)}")
        finally:
            task.is_running = False
            task.process = None
            # 状态改变，通知回调函数更新GUI
            if self.update_task_list_callback:
                self.update_task_list_callback()
    
    def start_all_pending_tasks(self):
        """开始所有待开始的任务"""
        for task_id, task in self.tasks.items():
            if task.status == "待开始":
                self.start_task(task_id)
    
    def delete_task(self, task_id: int):
        """删除指定任务"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            # 如果任务正在运行，先停止（停止时会自动清理临时文件）
            if task.is_running:
                self.stop_task(task_id)
            else:
                # 如果任务未运行，手动清理临时文件
                self.cleanup_task_temp_files(task)
            # 从任务字典删除
            del self.tasks[task_id]
            return True
        return False
    
    def stop_task(self, task_id: int):
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
                error_msg = f"停止任务 #{task_id} 时出错: {str(e)}"
                task.log_queue.put(error_msg)
                task.full_log.append(error_msg)  # 同时添加到完整日志列表
            finally:
                task.is_running = False
                task.status = "已停止"
                
                # 添加到任务日志
                stop_msg = f"任务 #{task_id} 已停止"
                task.log_queue.put(stop_msg)
                task.full_log.append(stop_msg)  # 同时添加到完整日志列表
                # 状态改变，通知回调函数更新GUI
                if self.update_task_list_callback:
                    self.update_task_list_callback()
        else:
            # 如果任务没有运行，只是更新状态
            if task:
                task.status = "已停止"
                task.log_queue.put(f"任务 #{task_id} 已停止")
                # 状态改变，通知回调函数更新GUI
                if self.update_task_list_callback:
                    self.update_task_list_callback()
        
        # 无论任务是否正在运行，在停止后都应该清理临时文件
        if task:
            self.cleanup_task_temp_files(task)
    
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
                        log_msg = f"已删除任务产生的临时文件: {item_path}"
                        task.log_queue.put(log_msg)
                        task.full_log.append(log_msg)  # 同时添加到完整日志列表
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        log_msg = f"已删除任务产生的临时目录: {item_path}"
                        task.log_queue.put(log_msg)
                        task.full_log.append(log_msg)  # 同时添加到完整日志列表
                
                if new_files:
                    log_msg = f"已清理任务 #{task.task_id} 产生的临时文件，目录: {task.current_tmp_dir}"
                    task.log_queue.put(log_msg)
                    task.full_log.append(log_msg)  # 同时添加到完整日志列表
                else:
                    log_msg = f"临时目录中没有任务 #{task.task_id} 产生的新文件需要清理: {task.current_tmp_dir}"
                    task.log_queue.put(log_msg)
                    task.full_log.append(log_msg)  # 同时添加到完整日志列表
            else:
                log_msg = f"任务 #{task.task_id} 没有可清理的临时文件"
                task.log_queue.put(log_msg)
                task.full_log.append(log_msg)  # 同时添加到完整日志列表
        except Exception as e:
            log_msg = f"清理任务 #{task.task_id} 临时文件时出错: {str(e)}"
            task.log_queue.put(log_msg)
            task.full_log.append(log_msg)  # 同时添加到完整日志列表
    
    def get_all_tasks(self):
        """获取所有任务"""
        return self.tasks

    def clear_all_tasks(self):
        """清空所有任务"""
        # 先停止所有运行中的任务（会自动清理临时文件）
        for task_id, task in self.tasks.items():
            if task.is_running:
                self.stop_task(task_id)
        
        # 对于未运行的任务，手动清理临时文件
        for task_id, task in self.tasks.items():
            if not task.is_running:
                self.cleanup_task_temp_files(task)
                
        # 清空任务字典
        self.tasks.clear()
