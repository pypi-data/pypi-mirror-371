#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD RPG引擎框架(GDK)内核(NT)模块封装

该模块提供基于R3层内核版本的窗口进程ID获取功能，可绕过部分检测机制。
"""
from ctypes import c_int64
from .base_module import HDModuleBase


class HDNT(HDModuleBase):
    """内核(NT)模块封装类"""
    
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化内核(NT)模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """初始化DLL中的函数"""
        self._bind_functions()
        
    def _bind_functions(self):
        """绑定DLL函数"""
        # 获取窗口进程ID函数
        try:
            self._get_window_process_id = getattr(self.dll, "HCNT_GetWindowProcessId")
            self._get_window_process_id.argtypes = [c_int64]
            self._get_window_process_id.restype = c_int64
        except AttributeError:
            self._get_window_process_id = None
    
    def get_window_process_id(self, hwnd):
        """
        获取目标窗口句柄的进程ID（R3层内核版本）
        
        Args:
            hwnd (int): 窗口句柄
        
        Returns:
            int: 操作结果，成功时返回进程ID，失败时返回错误码，参考HD返回值表
        
        Notes:
            可绕过一些检测（如NP等）
        """
        if not self._get_window_process_id:
            raise NotImplementedError("DLL中未找到HCNT_GetWindowProcessId函数")
        
        return self._get_window_process_id(hwnd)


# 工厂函数
def create_nt(dll_path=None, is_debug=None):
    """
    创建内核(NT)模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版本的DLL
    
    Returns:
        HDNT: 内核(NT)模块实例
    """
    return HDNT(dll_path, is_debug)