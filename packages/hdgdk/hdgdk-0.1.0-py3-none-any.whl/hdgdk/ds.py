#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 调试绘制模块封装
提供调试辅助功能，包括可视化标注颜色设置、窗口绘制、异常捕捉及控制台附加
"""

import ctypes
from typing import Optional, Union

from .base_module import HDModuleBase, HDModuleFactory


# 定义默认颜色常量
class DS_COLORS:
    """调试绘制模块的默认颜色常量"""
    # XRGB格式 (4字节)
    RED = 0x00FF0000          # 红色
    GREEN = 0x0000FF00        # 绿色
    BLUE = 0x000000FF         # 蓝色
    YELLOW = 0x00FFFF00       # 黄色
    CYAN = 0x0000FFFF         # 青色
    MAGENTA = 0x00FF00FF      # 洋红色
    WHITE = 0x00FFFFFF        # 白色
    BLACK = 0x00000000        # 黑色
    LIGHT_GREEN = 0x0000FF00  # 浅绿色 (默认线色)
    YELLOW_GREEN = 0x00FFFF00 # 黄绿色 (默认文本色)


# 定义绘制类型常量
class DS_DRAW_TYPE:
    """调试绘制类型常量"""
    BORDER = 0  # 绘制边框
    FILL = 1    # 填充矩形


class HCDS(HDModuleBase):
    """
    HD GDK 调试绘制模块
    提供调试辅助功能，包括可视化标注颜色设置、窗口绘制、异常捕捉及控制台附加
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化调试绘制模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的DS模块函数
        """
        # 设置全局可视化标注的颜色
        self.HCSD_SetColor = self.dll.HCSD_SetColor
        self.HCSD_SetColor.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.HCSD_SetColor.restype = ctypes.c_int64
        
        # 设置调试窗口跟随的目标进程窗口信息
        self.HCSD_SetFollowClassTitleName = self.dll.HCSD_SetFollowClassTitleName
        self.HCSD_SetFollowClassTitleName.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, ctypes.c_char_p]
        self.HCSD_SetFollowClassTitleName.restype = ctypes.c_int64
        
        # 为指定窗口绘制边框或填充矩形
        self.HCSD_DrawWinodws = self.dll.HCSD_DrawWinodws
        self.HCSD_DrawWinodws.argtypes = [ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.HCSD_DrawWinodws.restype = ctypes.c_int64
        
        # 开启或关闭异常捕捉功能
        self.HCHD_CatchException = self.dll.HCHD_CatchException
        self.HCHD_CatchException.argtypes = [ctypes.c_bool]
        self.HCHD_CatchException.restype = ctypes.c_int64
        
        # 附加或关闭控制台，用于输出调试信息
        self.HCSD_SetAttachConsole = self.dll.HCSD_SetAttachConsole
        self.HCSD_SetAttachConsole.argtypes = [ctypes.c_bool]
        self.HCSD_SetAttachConsole.restype = ctypes.c_int64
    
    def set_color(self, line_color: int = DS_COLORS.LIGHT_GREEN, 
                  text_color: int = DS_COLORS.YELLOW_GREEN, 
                  back_color: int = DS_COLORS.BLACK) -> int:
        """
        设置全局可视化标注的颜色（线色、文本色、背景色）
        
        Args:
            line_color (int): 线颜色（默认0x0000FF00，绿色）
            text_color (int): 文本颜色（默认0x00FFFF00，黄绿色）
            back_color (int): 背景颜色（默认0x00000000，黑色）
        
        Returns:
            int: 操作结果，0表示成功
        """
        return self.HCSD_SetColor(line_color, text_color, back_color)
    
    def set_follow_window(self, pid: int, hwnd: Optional[int] = None, 
                         class_name: Optional[str] = None, 
                         title_name: Optional[str] = None) -> int:
        """
        设置调试窗口跟随的目标进程窗口信息
        
        Args:
            pid (int): 目标进程PID，结合className或titleName查找窗口句柄
            hwnd (int, optional): 直接指定窗口句柄（指定后其他参数无效）
            class_name (str, optional): 窗口类名
            title_name (str, optional): 窗口标题名
        
        Returns:
            int: 操作结果，0表示成功
        """
        # 转换字符串参数为C风格字符串
        c_class_name = ctypes.c_char_p(class_name.encode('ascii')) if class_name else None
        c_title_name = ctypes.c_char_p(title_name.encode('ascii')) if title_name else None
        
        # 处理hwnd参数，确保是整数类型
        hwnd_value = hwnd or 0
        
        return self.HCSD_SetFollowClassTitleName(pid, hwnd_value, c_class_name, c_title_name)
    
    def draw_window(self, hwnd: int, line_color: int, line_size: int, 
                   draw_type: int = DS_DRAW_TYPE.BORDER, 
                   fill_color: int = 0) -> int:
        """
        为指定窗口绘制边框或填充矩形（用于调试标注）
        
        Args:
            hwnd (int): 目标窗口句柄
            line_color (int): 线条颜色（XRGB格式）
            line_size (int): 线条粗细
            draw_type (int): 绘制类型（0为边框，1为填充矩形）
            fill_color (int): 填充颜色（仅type=1时有效，XRGB格式）
        
        Returns:
            int: 操作结果，0表示成功
        """
        return self.HCSD_DrawWinodws(hwnd, line_color, line_size, draw_type, fill_color)
    
    def catch_exception(self, is_open: bool = True) -> int:
        """
        开启或关闭异常捕捉功能
        
        Args:
            is_open (bool): True开启异常捕捉，False关闭
        
        Returns:
            int: 操作结果，0表示成功
        """
        return self.HCHD_CatchException(is_open)
    
    def set_attach_console(self, is_open: bool) -> int:
        """
        附加或关闭控制台，用于输出调试信息
        
        Args:
            is_open (bool): True附加控制台，False关闭
        
        Returns:
            int: 返回当前控制台是否已打开
        """
        return self.HCSD_SetAttachConsole(is_open)


# 工厂函数
def create_hd_ds(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HCDS:
    """
    创建调试绘制模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HCDS: 调试绘制模块实例
    """
    return HDModuleFactory.create_instance(HCDS, dll_path, is_debug)


# 提供更友好的模块别名
def get_hd_ds_instance(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HCDS:
    """
    获取调试绘制模块实例的别名函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HCDS: 调试绘制模块实例
    """
    return create_hd_ds(dll_path, is_debug)


# 辅助函数：创建颜色值
def create_color(r: int, g: int, b: int) -> int:
    """
    根据RGB值创建XRGB格式的颜色
    
    Args:
        r (int): 红色分量 (0-255)
        g (int): 绿色分量 (0-255)
        b (int): 蓝色分量 (0-255)
    
    Returns:
        int: XRGB格式的颜色值
    """
    # XRGB格式，高8位为0，然后是R、G、B各8位
    return 0x00000000 | ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)


# 辅助函数：获取颜色分量
def get_color_components(color: int) -> tuple:
    """
    从XRGB格式颜色值中提取R、G、B分量
    
    Args:
        color (int): XRGB格式的颜色值
    
    Returns:
        tuple: (r, g, b) 颜色分量
    """
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (r, g, b)


# 辅助函数：将颜色转换为字符串表示
def color_to_string(color: int) -> str:
    """
    将颜色值转换为字符串表示
    
    Args:
        color (int): XRGB格式的颜色值
    
    Returns:
        str: 颜色的字符串表示
    """
    r, g, b = get_color_components(color)
    return f"XRGB(0x{color:08X}) [R:{r}, G:{g}, B:{b}]"