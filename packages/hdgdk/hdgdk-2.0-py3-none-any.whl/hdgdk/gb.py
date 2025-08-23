#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 谷歌内置浏览器模块封装
提供与游戏进程中自带的内置谷歌浏览器交互的功能
支持附加浏览器、脱离浏览器及注入JS代码
"""

import ctypes
import os
from typing import Optional

from .base_module import HDModuleBase, HDModuleFactory


class HDSCBrowserType:
    """浏览器附加模式常量"""
    MODE_1 = 1  # 模式1（监听模式）
    MODE_2 = 2  # 模式2（备选附加模式）


class HDSC(HDModuleBase):
    """
    HD GDK 谷歌内置浏览器模块
    用于与游戏进程中自带的内置谷歌浏览器交互
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化谷歌内置浏览器模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的GB模块函数
        """
        # 附加内置浏览器（模式1）
        self.HCGB_Attach1 = self.dll.HCGB_Attach1
        self.HCGB_Attach1.argtypes = [ctypes.c_int32]
        self.HCGB_Attach1.restype = ctypes.c_int64
        
        # 附加内置浏览器（模式2）
        self.HCGB_Attach2 = self.dll.HCGB_Attach2
        self.HCGB_Attach2.argtypes = [ctypes.c_int32]
        self.HCGB_Attach2.restype = ctypes.c_int64
        
        # 脱离内置浏览器
        self.HCGB_Detach = self.dll.HCGB_Detach
        self.HCGB_Detach.argtypes = [ctypes.c_int32]
        self.HCGB_Detach.restype = ctypes.c_int64
        
        # 注入JS代码
        self.HCGB_InjectJSCode = self.dll.HCGB_InjectJSCode
        self.HCGB_InjectJSCode.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.HCGB_InjectJSCode.restype = ctypes.c_int64
        
        # 从文件注入JS代码
        self.HCGB_ExecuteJSFile = self.dll.HCGB_ExecuteJSFile
        self.HCGB_ExecuteJSFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.HCGB_ExecuteJSFile.restype = ctypes.c_int64
    
    def attach_browser(self, window_index: int, mode: int = HDSCBrowserType.MODE_1) -> int:
        """
        附加内置浏览器
        
        Args:
            window_index (int): 目标窗口序号（从1开始）
            mode (int): 附加模式，默认为模式1
        
        Returns:
            int: 操作结果，0表示成功
        """
        if mode == HDSCBrowserType.MODE_1:
            return self.HCGB_Attach1(window_index)
        elif mode == HDSCBrowserType.MODE_2:
            return self.HCGB_Attach2(window_index)
        else:
            raise ValueError(f"不支持的附加模式: {mode}")
    
    def detach_browser(self, window_index: int) -> int:
        """
        脱离之前附加的内置浏览器
        
        Args:
            window_index (int): 窗口序号（从1开始）
        
        Returns:
            int: 操作结果，0表示成功
        """
        return self.HCGB_Detach(window_index)
    
    def inject_js_code(self, window_index: int, js_code: str, is_main_thread: bool = False) -> int:
        """
        向内置浏览器注入JS代码
        
        Args:
            window_index (int): 窗口序号（从1开始）
            js_code (str): 要注入的JS代码
            is_main_thread (bool): 是否在主线程调用，默认为False
        
        Returns:
            int: 操作结果，0表示成功
        """
        # 将Python字符串转换为C风格的ASCII字符串
        c_js_code = ctypes.c_char_p(js_code.encode('ascii', errors='replace'))
        return self.HCGB_InjectJSCode(window_index, c_js_code, is_main_thread)
    
    def execute_js_file(self, window_index: int, js_file_path: str, is_main_thread: bool = False) -> int:
        """
        向内置浏览器注入指定文件中的JS代码
        
        Args:
            window_index (int): 窗口序号（从1开始）
            js_file_path (str): JS文件路径
            is_main_thread (bool): 是否在主线程调用，默认为False
        
        Returns:
            int: 操作结果，0表示成功
        """
        # 检查文件是否存在
        if not os.path.exists(js_file_path):
            raise FileNotFoundError(f"JS文件不存在: {js_file_path}")
        
        # 将文件路径转换为C风格的ASCII字符串
        c_file_path = ctypes.c_char_p(js_file_path.encode('ascii', errors='replace'))
        return self.HCGB_ExecuteJSFile(window_index, c_file_path, is_main_thread)


# 工厂函数
def create_hd_gb(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HDSC:
    """
    创建谷歌内置浏览器模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDSC: 谷歌内置浏览器模块实例
    """
    return HDModuleFactory.create_instance(HDSC, dll_path, is_debug)


# 提供更友好的模块别名
def get_hd_gb_instance(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HDSC:
    """
    获取谷歌内置浏览器模块实例的别名函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDSC: 谷歌内置浏览器模块实例
    """
    return create_hd_gb(dll_path, is_debug)


# 定义一些常用的JS代码模板
def get_common_js_templates():
    """
    获取常用的JS代码模板字典
    
    Returns:
        dict: 包含常用JS代码模板的字典
    """
    return {
        'alert_message': "alert('{message}');",
        'console_log': "console.log('{message}');",
        'get_element_value': "document.getElementById('{element_id}').value;",
        'set_element_value': "document.getElementById('{element_id}').value = \'{value}\';",
        'click_element': "document.getElementById('{element_id}').click();",
        'inject_jquery': """var jq = document.createElement('script');\njq.src = 'https://code.jquery.com/jquery-3.6.0.min.js';\ndocument.getElementsByTagName('head')[0].appendChild(jq);"""
    }


# 示例函数：构建JS代码
def build_js_code(template_name: str, **kwargs) -> str:
    """
    根据模板名称和参数构建JS代码
    
    Args:
        template_name (str): 模板名称
        **kwargs: 模板中需要替换的参数
    
    Returns:
        str: 构建好的JS代码
    """
    templates = get_common_js_templates()
    if template_name not in templates:
        raise ValueError(f"不支持的模板名称: {template_name}")
    
    try:
        return templates[template_name].format(**kwargs)
    except KeyError as e:
        raise ValueError(f"模板参数缺失: {str(e)}")
    except Exception as e:
        raise Exception(f"构建JS代码失败: {str(e)}")