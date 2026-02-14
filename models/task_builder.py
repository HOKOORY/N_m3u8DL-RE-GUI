"""
任务命令构建器模型
"""
import sys
import os
from typing import Optional, List


class TaskCommandBuilder:
    """任务命令构建器 - 负责构建N_m3u8DL-RE的命令行参数"""
    
    @staticmethod
    def build_task_command(task) -> Optional[List[str]]:
        """为指定任务构建命令"""
        # 验证必要参数
        if not task.url:
            task.log_queue.put("错误: 任务URL为空")
            return None
            
        # 检查是否在PyInstaller打包环境中
        if getattr(sys, 'frozen', False):
            # 在打包环境中，使用PyInstaller的资源路径
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
        cmd = TaskCommandBuilder._add_advanced_params(cmd, task)
            
        return cmd
    
    @staticmethod
    def _add_advanced_params(cmd: List[str], task) -> List[str]:
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