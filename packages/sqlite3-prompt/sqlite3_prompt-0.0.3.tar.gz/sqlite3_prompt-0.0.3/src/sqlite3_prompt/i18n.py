import gettext
import os
import sys
import importlib.resources
from sqlite3_prompt.helpers_config import config

# 默认语言
DEFAULT_LANG = 'zh'
# 支持的语言列表 (语言代码: 显示名称)
SUPPORTED_LANGUAGES = {
    'zh': '中文',
    'en': 'English'
}


# 2025-06-16 13:54:48 修改
# 动态判断程序运行环境，并设置正确的执行目录 (EXEC_DIR)
if getattr(sys, 'frozen', False):
    # 如果程序被 PyInstaller 打包（即 sys.frozen 为 True）
    # _MEIPASS 是 PyInstaller 在运行时创建的临时文件夹，所有文件都在这里
    temp_EXEC_DIR = sys._MEIPASS
else:
    # 如果是在开发环境中直接运行 .py 文件
    # 我们需要从当前文件 (__file__) 的位置向上回溯三级目录
    # .../src/utils/helpers_config.py -> .../src/utils -> .../src -> .../ (项目根目录)
    temp_EXEC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# 使用 importlib.resources 定位数据文件，这是 PyPI 包的标准做法
try:
    # 查找正确的 localedir 路径
    with importlib.resources.path('sqlite3_prompt', 'locales') as p:
        LOCALE_DIR = str(p)
except (ModuleNotFoundError, FileNotFoundError):
    # 作为备选方案，在开发环境中直接定位
    print("[I18N WARNING] Could not find 'locales' via importlib.resources, falling back to file path method. This is normal in development.")
    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOCALE_DIR = os.path.join(_project_root, 'locales')


# 初始化一个“什么都不做”的翻译函数作为备用，并使其成为全局可访问的
_ = lambda s: s

def setup_translation():
    """根据配置文件设置当前的翻译语言，并更新全局的 _ 函数"""
    global _
    # 尝试从配置中获取语言设置，如果没有则使用默认语言
    lang = config.get('language', DEFAULT_LANG)
    
    try:
        # 查找并加载对应的 .mo 翻译文件
        # fallback=True 确保在找不到翻译文件时，程序不会崩溃，而是返回原文
        t = gettext.translation('messages', localedir=LOCALE_DIR, languages=[lang], fallback=True)
        # 获取并更新全局的翻译函数
        _ = t.gettext
    except Exception as e:
        print(f"[I18N ERROR] An unexpected error occurred: {e}")
        # 出现异常时，确保 _ 仍然是一个有效的函数
        _ = lambda s: s

def get_translator():
    """返回当前的翻译函数，方便其他模块调用（尽管现在我们倾向于直接使用全局 _）"""
    return _

def get_supported_languages():
    """返回支持的语言字典"""
    return SUPPORTED_LANGUAGES