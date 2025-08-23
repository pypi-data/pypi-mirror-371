#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD GDK 黑屏优化模块
提供黑屏功能的开启、设置及关闭操作，通过过滤指定范围的模型序号实现黑屏效果
"""

import ctypes
from typing import Optional

from .base_module import HDModuleBase


class HDBS(HDModuleBase):
    """
    HD GDK 黑屏优化模块类
    提供黑屏功能的开启、设置及关闭操作
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化黑屏优化模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
    
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 打开黑屏功能
        self.HC_OpenBS = self.dll.HC_OpenBS
        self.HC_OpenBS.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.HC_OpenBS.restype = ctypes.c_int64
        
        # 设置模型序号的过滤范围
        self.HC_SetBs = self.dll.HC_SetBs
        self.HC_SetBs.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.HC_SetBs.restype = ctypes.c_int64
        
        # 关闭黑屏功能
        self.HC_CloseBS = self.dll.HC_CloseBS
        self.HC_CloseBS.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.HC_CloseBS.restype = ctypes.c_int64
    
    def open_bs(self, window_index: int, min_index: int = 0, max_index: int = 0, 
                is_main_thread: bool = False) -> int:
        """
        打开黑屏功能
        
        Args:
            window_index: 目标窗口序号（从1开始）
            min_index: 最小模型序号（用于过滤模型范围）
            max_index: 最大模型序号（用于过滤模型范围）
            is_main_thread: 是否需要主线程执行该操作
        
        Returns:
            int: 操作结果（参考HD返回值表）
        """
        return self.HC_OpenBS(window_index, min_index, max_index, is_main_thread)
    
    def set_bs(self, window_index: int, min_index: int = 0, max_index: int = 0) -> int:
        """
        设置模型序号的过滤范围（用于调整黑屏效果）
        
        Args:
            window_index: 目标窗口序号（从1开始）
            min_index: 最小模型序号
            max_index: 最大模型序号
        
        Returns:
            int: 操作结果（参考HD返回值表）
        """
        return self.HC_SetBs(window_index, min_index, max_index)
    
    def close_bs(self, window_index: int, is_main_thread: bool = False) -> int:
        """
        关闭黑屏功能
        
        Args:
            window_index: 目标窗口序号（从1开始）
            is_main_thread: 是否需要主线程执行该操作
        
        Returns:
            int: 操作结果（参考HD返回值表）
        """
        return self.HC_CloseBS(window_index, is_main_thread)


# 工厂函数
def create_hd_bs(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HDBS:
    """
    创建黑屏优化模块实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HDBS: 黑屏优化模块实例
    """
    return HDBS(dll_path, is_debug)