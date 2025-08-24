import json
import os
import sys
import platformdirs

# 配置文件名称
CONFIG_FILE_NAME = 'sqlite3-prompt-config.json'
APP_NAME = "sqlite3-prompt"

# 默认配置
DEFAULT_CONFIG = {
    'language': 'zh_CN',
    'db_history': []
}

# 动态判断配置文件存放位置
def get_config_file_path():
    """获取用户专属的、跨平台的配置文件路径"""
    config_dir = platformdirs.user_config_dir(APP_NAME)
    return os.path.join(config_dir, CONFIG_FILE_NAME)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_path = get_config_file_path()
        self._config = None
        self.load_config()
    
    def load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                    # 确保所有默认配置项都存在
                    for key, value in DEFAULT_CONFIG.items():
                        if key not in self._config:
                            self._config[key] = value
            else:
                # 配置文件不存在，创建默认配置
                self._config = DEFAULT_CONFIG.copy()
                self.save_config()
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"配置文件加载失败: {e}")
            print("使用默认配置...")
            self._config = DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 确保用户配置目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
                
        except IOError as e:
            print(f"配置文件保存失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """设置配置项并保存"""
        self._config[key] = value
        self.save_config()
    
    def get_all(self):
        """获取所有配置"""
        return self._config.copy()

    def add_to_db_history(self, db_path, max_history=100):
        """
        添加一个数据库路径到历史记录的顶部。
        - 确保路径唯一
        - 保持最近使用的在最前
        - 限制历史记录的总长度
        """
        history = self.get('db_history', [])
        
        # 如果路径已存在，先移除旧的记录
        if db_path in history:
            history.remove(db_path)
        
        # 将新路径插入到列表的最前面
        history.insert(0, db_path)
        
        # 限制历史记录的长度，并更新配置
        self._config['db_history'] = history[:max_history]
        self.save_config()


# 创建全局配置管理器实例
config = ConfigManager()



