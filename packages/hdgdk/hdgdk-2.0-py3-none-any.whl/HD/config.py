from typing import Optional
import ctypes
import os
from enum import Enum
from .hd_dll_manager import get_dll_manager

class HD配置(Enum):
    """HD配置枚举类"""
    HD缓冲区大小 = 1024 * 200
    HD多开数量 = 62

class Config:
    """HD配置类，管理DLL加载和全局配置"""
    _hd = None  # 静态变量存储DLL实例
    _dll_path = None  # 存储已加载的DLL路径
    _is_debug = False  # 存储调试模式状态
    _dll_manager = None  # DLL管理器实例

    @staticmethod
    def _get_manager():
        """\获取DLL管理器实例"""
        if Config._dll_manager is None:
            Config._dll_manager = get_dll_manager()
        return Config._dll_manager

    @staticmethod
    def load_dll(dll_path: str, is_debug: bool = False) -> bool:
        """
        加载DLL文件
        Args:
            dll_path: DLL文件路径
            is_debug: 是否加载调试版本的DLL
        Returns:
            bool: 是否加载成功
        """
        try:
            # 保存路径和调试模式
            # 规范化路径，确保与DLL管理器中的路径一致
            normalized_path = os.path.normpath(dll_path)
            Config._dll_path = os.path.dirname(normalized_path) if os.path.isfile(normalized_path) else normalized_path
            Config._is_debug = is_debug
            
            # 使用DLL管理器加载DLL
            manager = Config._get_manager()
            
            # 初始化DLL管理器
            dll_instance = manager.initialize(Config._dll_path, Config._is_debug)
            Config._hd = dll_instance
            print(f"成功加载DLL: {Config._dll_path}, 调试模式: {Config._is_debug}")
            return True
        except FileNotFoundError as e:
            print(f"DLL文件不存在: {e}")
            Config._hd = None
            Config._dll_path = None
            Config._is_debug = False
            return False
        except Exception as e:
            print(f"加载DLL时发生其他错误: {e}")
            Config._hd = None
            Config._dll_path = None
            Config._is_debug = False
            return False

    @staticmethod
    def get_hd():
        """
        获取DLL实例
        Returns:
            加载的DLL实例，如果未加载则抛出异常
        """
        if Config._hd is None:
            raise RuntimeError("DLL未加载，请先调用HD_Path设置DLL路径")
        return Config._hd

    @staticmethod
    def is_dll_loaded() -> bool:
        """
        检查DLL是否已加载
        Returns:
            bool: 是否已加载
        """
        return Config._hd is not None

    @staticmethod
    def get_loaded_dll_path() -> Optional[str]:
        """
        获取已加载的DLL路径
        Returns:
            str: DLL路径，如果未加载则返回None
        """
        return Config._dll_path

    @staticmethod
    def get_debug_mode() -> bool:
        """
        获取当前调试模式
        Returns:
            bool: 是否为调试模式
        """
        return Config._is_debug


# ============================================自动转码
def auto_encode(text: str) -> bytes:
    """
    自动编码函数，根据文本内容选择合适的编码方式
    Args:
        text: 要编码的字符串
    Returns:
        bytes: 编码后的字节数组
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text)}")
    
    try:
        # 检查是否包含中文字符
        if any('\u4e00' <= ch <= '\u9fff' for ch in text):
            return text.encode('gbk')
        else:
            return text.encode('utf-8')
    except UnicodeEncodeError:
        # 如果GBK编码失败，尝试UTF-8
        try:
            return text.encode('utf-8')
        except UnicodeEncodeError:
            # 如果UTF-8也失败，使用错误替换策略
            return text.encode('utf-8', errors='replace')