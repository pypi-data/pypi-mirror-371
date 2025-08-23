#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 实时绘制模块封装
用于在指定窗口上实时绘制各类信息，包括识别结果、yolov检测信息及键鼠操作轨迹等
支持配置绘制内容和更新频率，适用于可视化调试场景
"""

import ctypes
from typing import Optional, Dict, Any, Union

from .base_module import HDModuleBase, HDModuleFactory


class HDDW(HDModuleBase):
    """
    HD GDK 实时绘制模块
    用于在指定窗口上实时绘制各类信息，包括识别结果、yolov检测信息及键鼠操作轨迹等
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化实时绘制模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的DW模块函数
        """
        # 一、实时绘制开关
        self.HDDW_Open = self.dll.HDDW_Open
        self.HDDW_Open.argtypes = [ctypes.c_int32, ctypes.c_int64]
        self.HDDW_Open.restype = ctypes.c_int64
        
        self.HDDW_Close = self.dll.HDDW_Close
        self.HDDW_Close.argtypes = [ctypes.c_int32]
        self.HDDW_Close.restype = ctypes.c_int64
        
        # 二、绘制配置设置
        self.HDDW_SetSetting = self.dll.HDDW_SetSetting
        self.HDDW_SetSetting.argtypes = [ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_int32, ctypes.c_char_p]
        self.HDDW_SetSetting.restype = ctypes.c_int64

    # 一、实时绘制开关
    def open_drawing(self, wind_index: int, attach_hwnd: int) -> int:
        """
        打开实时绘制功能，将绘制内容附加到指定窗口
        
        Args:
            wind_index (int): 窗口序号
            attach_hwnd (int): 需要附加绘制的目标窗口句柄
        
        Returns:
            int: 操作结果，0表示成功
        """
        return self.HDDW_Open(wind_index, attach_hwnd)
    
    def close_drawing(self, wind_index: int, max_attempts: int = 10, delay_ms: int = 100) -> bool:
        """
        关闭实时绘制功能
        
        Args:
            wind_index (int): 窗口序号
            max_attempts (int): 最大尝试次数（默认10次）
            delay_ms (int): 每次尝试间隔时间（毫秒，默认100ms）
        
        Returns:
            bool: 是否成功关闭
        
        Notes:
            需循环调用直至关闭成功（通常1秒内可完成）
        """
        import time
        
        for _ in range(max_attempts):
            result = self.HDDW_Close(wind_index)
            if result == 0:
                return True
            time.sleep(delay_ms / 1000.0)
        
        return False
    
    # 二、绘制配置设置
    def set_setting(self, draw_recognition: bool = True, 
                   draw_yolo: bool = True, 
                   draw_mkbd: bool = True, 
                   update_time: int = 30, 
                   extra_config: Optional[Dict[str, Any]] = None) -> int:
        """
        配置实时绘制的内容及更新参数
        
        Args:
            draw_recognition (bool): 是否绘制识别信息（默认True开启）
            draw_yolo (bool): 是否绘制yolov检测信息（默认True开启）
            draw_mkbd (bool): 是否绘制键鼠操作信息（默认True开启）
            update_time (int): 绘制内容的更新间隔时间（毫秒，默认30ms）
            extra_config (dict, optional): 额外JSON配置，例如：
                {'bgc': 0xFFFFFFFF}  // 窗口背景色（含透明度，RGBA格式）
        
        Returns:
            int: 操作结果，0表示成功
        """
        # 处理额外配置参数
        lparam = None
        if extra_config:
            import json
            try:
                config_str = json.dumps(extra_config)
                lparam = config_str.encode('utf-8')
            except:
                # 如果JSON序列化失败，则不使用额外配置
                lparam = None
        
        # 调用DLL函数
        return self.HDDW_SetSetting(draw_recognition, draw_yolo, draw_mkbd, update_time, lparam)


# 工厂函数
def create_hd_dw(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HDDW:
    """
    创建实时绘制模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDDW: 实时绘制模块实例
    """
    return HDModuleFactory.create_instance(HDDW, dll_path, is_debug)


# 提供更友好的模块别名
def get_hd_dw_instance(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HDDW:
    """
    获取实时绘制模块实例的别名函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDDW: 实时绘制模块实例
    """
    return create_hd_dw(dll_path, is_debug)


# 预定义的绘制配置模板
def get_default_drawing_config() -> dict:
    """
    获取默认的绘制配置
    
    Returns:
        dict: 默认配置字典
    """
    return {
        'draw_recognition': True,
        'draw_yolo': True,
        'draw_mkbd': True,
        'update_time': 30,
        'extra_config': None
    }


def get_minimal_drawing_config() -> dict:
    """
    获取最小化绘制的配置（仅必要信息）
    
    Returns:
        dict: 最小化配置字典
    """
    return {
        'draw_recognition': True,
        'draw_yolo': False,
        'draw_mkbd': False,
        'update_time': 50,
        'extra_config': None
    }


def get_high_performance_config() -> dict:
    """
    获取高性能模式的绘制配置
    
    Returns:
        dict: 高性能配置字典
    """
    return {
        'draw_recognition': True,
        'draw_yolo': False,
        'draw_mkbd': False,
        'update_time': 100,
        'extra_config': None
    }


def get_complete_debug_config() -> dict:
    """
    获取完整调试模式的绘制配置（包含所有信息）
    
    Returns:
        dict: 完整调试配置字典
    """
    return {
        'draw_recognition': True,
        'draw_yolo': True,
        'draw_mkbd': True,
        'update_time': 20,
        'extra_config': {'bgc': 0x001E1E1E}  # 半透明黑色背景
    }


# 辅助函数：创建额外配置

def create_extra_config(background_color: int = 0x00000000, **kwargs) -> dict:
    """
    创建额外的JSON配置
    
    Args:
        background_color (int): 窗口背景色（含透明度，RGBA格式，默认0x00000000透明）
        **kwargs: 其他配置项
    
    Returns:
        dict: 额外配置字典
    """
    config = {'bgc': background_color}
    config.update(kwargs)
    return config


# 预定义颜色常量（RGBA格式）
class DW_COLORS:
    """实时绘制模块的颜色常量（RGBA格式）"""
    # 透明颜色
    TRANSPARENT = 0x00000000          # 完全透明
    # 基本颜色
    WHITE = 0xFFFFFFFF                # 白色
    BLACK = 0xFF000000                # 黑色
    RED = 0xFFFF0000                  # 红色
    GREEN = 0xFF00FF00                # 绿色
    BLUE = 0xFF0000FF                 # 蓝色
    YELLOW = 0xFFFFFF00               # 黄色
    CYAN = 0xFF00FFFF                 # 青色
    MAGENTA = 0xFFFF00FF              # 洋红色
    # 半透明颜色
    SEMI_TRANSPARENT_BLACK = 0x80000000  # 半透明黑色
    SEMI_TRANSPARENT_WHITE = 0x80FFFFFF  # 半透明白色
    SEMI_TRANSPARENT_RED = 0x80FF0000    # 半透明红色
    SEMI_TRANSPARENT_GREEN = 0x8000FF00  # 半透明绿色


# 上下文管理器，用于自动打开和关闭绘制功能
class DrawingContext:
    """
    实时绘制上下文管理器，自动打开和关闭绘制功能
    """
    def __init__(self, dw_module: HDDW, wind_index: int, attach_hwnd: int, 
                 config: Optional[dict] = None):
        """
        初始化绘制上下文管理器
        
        Args:
            dw_module (HDDW): 实时绘制模块实例
            wind_index (int): 窗口序号
            attach_hwnd (int): 附加窗口句柄
            config (dict, optional): 绘制配置
        """
        self.dw_module = dw_module
        self.wind_index = wind_index
        self.attach_hwnd = attach_hwnd
        self.config = config or get_default_drawing_config()
        
    def __enter__(self):
        """进入上下文管理器，打开绘制功能"""
        # 打开绘制功能
        result = self.dw_module.open_drawing(self.wind_index, self.attach_hwnd)
        if result != 0:
            raise Exception(f"Failed to open drawing: error code {result}")
        
        # 设置绘制配置
        self.dw_module.set_setting(
            draw_recognition=self.config.get('draw_recognition', True),
            draw_yolo=self.config.get('draw_yolo', True),
            draw_mkbd=self.config.get('draw_mkbd', True),
            update_time=self.config.get('update_time', 30),
            extra_config=self.config.get('extra_config', None)
        )
        
        return self.dw_module
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器，关闭绘制功能"""
        self.dw_module.close_drawing(self.wind_index)
        return False  # 不抑制异常


# 辅助函数：获取窗口句柄

def get_window_handle_by_title(title: str) -> Optional[int]:
    """
    通过窗口标题获取窗口句柄
    
    Args:
        title (str): 窗口标题
    
    Returns:
        int: 窗口句柄，如果未找到返回None
    """
    try:
        # 使用win32gui模块获取窗口句柄
        import win32gui
        hwnd = win32gui.FindWindow(None, title)
        return hwnd if hwnd != 0 else None
    except ImportError:
        # 如果没有安装pywin32，可以尝试使用ctypes调用Windows API
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, title)
        return hwnd if hwnd != 0 else None


# 辅助函数：获取当前活动窗口句柄
def get_active_window_handle() -> int:
    """
    获取当前活动窗口句柄
    
    Returns:
        int: 活动窗口句柄
    """
    user32 = ctypes.windll.user32
    return user32.GetForegroundWindow()