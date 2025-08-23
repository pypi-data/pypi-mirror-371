#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 全局资源设置模块封装
用于配置引擎所需的资源路径，包括图片、字库、语言文件等资源的查找路径
"""

import ctypes
from typing import Optional

from .base_module import HDModuleBase, HDModuleFactory


class HCRES(HDModuleBase):
    """
    HD GDK 全局资源设置模块
    用于配置引擎所需的资源路径，包括图片、字库、语言文件等资源的查找路径
    支持全局设置和窗口序号关联的局部设置
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化全局资源设置模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的RES模块函数
        """
        # 设置全局资源路径 - ANSI版本
        self.HCRES_SetResPathA = self.dll.HCRES_SetResPathA
        self.HCRES_SetResPathA.argtypes = [ctypes.c_char_p]
        self.HCRES_SetResPathA.restype = None
        
        # 设置全局资源路径 - 宽字符版本
        self.HCRES_SetResPathW = self.dll.HCRES_SetResPathW
        self.HCRES_SetResPathW.argtypes = [ctypes.c_wchar_p]
        self.HCRES_SetResPathW.restype = None
        
        # 为指定窗口序号设置专属资源路径
        self.HCRES_SetResPathEx = self.dll.HCRES_SetResPathEx
        self.HCRES_SetResPathEx.argtypes = [ctypes.c_int32, ctypes.c_char_p]
        self.HCRES_SetResPathEx.restype = None
        
        # 设置语言/字体资源路径 - ANSI版本
        self.HCRES_SetLanguageResPathA = self.dll.HCRES_SetLanguageResPathA
        self.HCRES_SetLanguageResPathA.argtypes = [ctypes.c_char_p]
        self.HCRES_SetLanguageResPathA.restype = None
        
        # 设置语言/字体资源路径 - 宽字符版本
        self.HCRES_SetLanguageResPathW = self.dll.HCRES_SetLanguageResPathW
        self.HCRES_SetLanguageResPathW.argtypes = [ctypes.c_wchar_p]
        self.HCRES_SetLanguageResPathW.restype = None
    
    def set_res_path(self, path: str, is_wide_char: bool = False) -> None:
        """
        设置全局资源路径（适用于所有窗口）
        图片、字库等文件将在此路径下查找
        
        Args:
            path (str): 资源路径（如"D:\\resources\\"）
            is_wide_char (bool): 是否使用宽字符版本
        """
        if is_wide_char:
            # 使用宽字符版本
            self.HCRES_SetResPathW(path)
        else:
            # 使用ANSI版本
            self.HCRES_SetResPathA(path.encode('ascii'))
    
    def set_res_path_ex(self, wind_index: int, path: str) -> None:
        """
        为指定窗口序号设置专属资源路径
        
        Args:
            wind_index (int): 窗口序号（-1表示设置全局资源路径，≥0表示为该窗口设置专属路径）
            path (str): 资源路径
        
        Notes:
            - 当wind_index≥0时，首次调用会同时设置该窗口的专属路径和全局资源路径
            - 窗口优先使用自身专属路径，未找到资源时会fallback到全局路径
        """
        self.HCRES_SetResPathEx(wind_index, path.encode('ascii'))
    
    def set_language_res_path(self, path: str, is_wide_char: bool = False) -> None:
        """
        设置语言文件或字体文件的专属资源路径
        用于加载多语言包、字体库等资源
        
        Args:
            path (str): 语言/字体资源路径（如"D:\\languages\\"）
            is_wide_char (bool): 是否使用宽字符版本
        """
        if is_wide_char:
            # 使用宽字符版本
            self.HCRES_SetLanguageResPathW(path)
        else:
            # 使用ANSI版本
            self.HCRES_SetLanguageResPathA(path.encode('ascii'))


# 工厂函数
def create_hd_res(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HCRES:
    """
    创建全局资源设置模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HCRES: 全局资源设置模块实例
    """
    return HDModuleFactory.create_instance(HCRES, dll_path, is_debug)


# 提供更友好的模块别名
def get_hd_res_instance(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HCRES:
    """
    获取全局资源设置模块实例的别名函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HCRES: 全局资源设置模块实例
    """
    return create_hd_res(dll_path, is_debug)


# 辅助函数：规范化资源路径

def normalize_path(path: str, ensure_trailing_slash: bool = True) -> str:
    """
    规范化资源路径，确保路径格式正确
    
    Args:
        path (str): 原始路径
        ensure_trailing_slash (bool): 是否确保路径末尾有斜杠
    
    Returns:
        str: 规范化后的路径
    """
    # 处理不同操作系统的路径分隔符
    normalized = path.replace('/', '\\')
    
    # 确保路径末尾有斜杠
    if ensure_trailing_slash and not normalized.endswith('\\'):
        normalized += '\\'
    
    return normalized


# 辅助函数：设置多窗口资源路径
def set_multi_window_res_paths(res_instance: HCRES, window_paths: dict) -> None:
    """
    一次性设置多个窗口的资源路径
    
    Args:
        res_instance (HCRES): RES模块实例
        window_paths (dict): 窗口序号到资源路径的映射字典
    """
    for window_index, path in window_paths.items():
        res_instance.set_res_path_ex(window_index, path)


# 预定义的常用资源路径类型
def create_resource_config(root_path: str) -> dict:
    """
    创建常用的资源配置结构
    
    Args:
        root_path (str): 资源根目录
    
    Returns:
        dict: 包含各种资源路径的配置字典
    """
    root = normalize_path(root_path)
    
    return {
        'root': root,
        'images': normalize_path(root + 'images'),
        'fonts': normalize_path(root + 'fonts'),
        'languages': normalize_path(root + 'languages'),
        'sounds': normalize_path(root + 'sounds'),
        'scripts': normalize_path(root + 'scripts'),
        'textures': normalize_path(root + 'textures'),
        'configs': normalize_path(root + 'configs')
    }