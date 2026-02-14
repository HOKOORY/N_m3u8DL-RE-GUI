"""
配置管理器模型
"""
import json
import os
from typing import Dict, Any


class ConfigManager:
    """配置管理器 - 负责处理配置文件的读取和保存"""
    
    def __init__(self, config_file: str = "m3u8dl_config.json"):
        self.config_file = config_file
        self.config_data = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """从配置文件加载设置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件时出错: {str(e)}")
                return {}
        return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            self.config_data = config  # 更新内存中的配置
            return True
        except Exception as e:
            print(f"保存配置文件时出错: {str(e)}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config_data
    
    def update_config(self, key: str, value: Any):
        """更新特定配置项"""
        self.config_data[key] = value
    
    def get(self, key: str, default=None):
        """获取配置项的值"""
        return self.config_data.get(key, default)