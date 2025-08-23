#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 基础模块
提供所有模块共享的DLL加载和初始化逻辑
"""

import ctypes
import os

# 导入DLL管理器
def get_dll_manager():
    """获取DLL管理器（避免循环导入）"""
    from .dll_manager import get_dll_manager as _get_dll_manager
    return _get_dll_manager()


def get_dll(dll_path=None, is_debug=None):
    """获取已加载的DLL实例（避免循环导入）"""
    from .dll_manager import get_dll as _get_dll
    return _get_dll(dll_path, is_debug)


class HDModuleBase:
    """
    HD GDK 模块基类
    提供所有模块共享的DLL加载和初始化逻辑
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化HD模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径。如果为None，则使用已通过DLL管理器初始化的DLL
            is_debug (bool, optional): 是否使用调试版本的DLL。如果为None，则使用已通过DLL管理器初始化的设置
        """
        self.dll_path = dll_path
        self.is_debug = is_debug
        self.dll = None
        
        # 加载DLL并初始化函数
        self._load_dll()
        self._initialize_functions()
    
    def _load_dll(self):
        """
        从DLL管理器获取已加载的DLL
        """
        # 从DLL管理器获取DLL
        try:
            self.dll = get_dll(self.dll_path, self.is_debug)
        except Exception as e:
            raise Exception(f"DLL加载失败: {str(e)}")
        
        if not self.dll:
            raise Exception("DLL未加载成功，无法继续初始化")
    
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        子类必须重写此方法以初始化特定于模块的函数
        """
        raise NotImplementedError("子类必须实现_initialize_functions方法")


class HDModuleFactory:
    """
    HD GDK 模块工厂基类
    提供所有模块共享的工厂函数逻辑
    """
    @staticmethod
    def create_instance(module_class, dll_path=None, is_debug=None):
        """
        创建模块实例的通用工厂方法
        
        Args:
            module_class (class): 要创建的模块类
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
            
        Returns:
            HDModuleBase: 创建的模块实例
        """
        return module_class(dll_path, is_debug)