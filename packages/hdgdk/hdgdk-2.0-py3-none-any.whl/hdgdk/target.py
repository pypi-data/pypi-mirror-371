#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD RPG引擎框架(GDK)后台键鼠模块(TARGET)封装

该模块用于实现后台鼠标和键盘操作，支持在不激活目标窗口的情况下进行精准的
鼠标点击、移动、键盘输入等操作，适用于各类需要后台控制的场景，且具备较强的防检测能力。
"""
from ctypes import c_int64, c_int32, c_char_p
from .base_module import HDModuleBase


class HDTARGET(HDModuleBase):
    """后台键鼠模块封装类"""
    
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化后台键鼠模块
        
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
        # 鼠标移动函数
        try:
            self._move_to = getattr(self.dll, "HCMouse_MoveTo")
            self._move_to.argtypes = [c_int32, c_int32, c_int32]
            self._move_to.restype = c_int64
        except AttributeError:
            self._move_to = None
        
        # 鼠标左键点击函数
        try:
            self._left_click = getattr(self.dll, "HCMouse_LeftClick")
            self._left_click.argtypes = [c_int32, c_int32, c_int32, c_int32]
            self._left_click.restype = c_int64
        except AttributeError:
            self._left_click = None
        
        # 鼠标右键点击函数
        try:
            self._right_click = getattr(self.dll, "HCMouse_RightClick")
            self._right_click.argtypes = [c_int32, c_int32, c_int32, c_int32]
            self._right_click.restype = c_int64
        except AttributeError:
            self._right_click = None
        
        # 键盘按键函数
        try:
            self._key_press = getattr(self.dll, "HCKey_Press")
            self._key_press.argtypes = [c_int32, c_int32, c_int32]
            self._key_press.restype = c_int64
        except AttributeError:
            self._key_press = None
        
        # 键盘发送字符串函数
        try:
            self._send_string = getattr(self.dll, "HCKey_SendString")
            self._send_string.argtypes = [c_int32, c_char_p, c_int32]
            self._send_string.restype = c_int64
        except AttributeError:
            self._send_string = None
    
    def move_to(self, window_index, x, y):
        """
        后台鼠标移动到目标窗口客户区指定坐标
        
        Args:
            window_index (int): 目标窗口的序号（从1开始）
            x (int): 目标窗口客户区X坐标
            y (int): 目标窗口客户区Y坐标
        
        Returns:
            int: 操作结果，参考HD返回值表
        
        Notes:
            移动过程自带模拟人工轨迹，降低被检测风险
        """
        if not self._move_to:
            raise NotImplementedError("DLL中未找到HCMouse_MoveTo函数")
        
        return self._move_to(window_index, x, y)
    
    def left_click(self, window_index, x, y, delay=50):
        """
        后台鼠标左键点击目标窗口客户区指定坐标
        
        Args:
            window_index (int): 目标窗口的序号
            x (int): 目标窗口客户区X坐标
            y (int): 目标窗口客户区Y坐标
            delay (int, optional): 点击后延迟毫秒数（默认50ms）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._left_click:
            raise NotImplementedError("DLL中未找到HCMouse_LeftClick函数")
        
        return self._left_click(window_index, x, y, delay)
    
    def right_click(self, window_index, x, y, delay=50):
        """
        后台鼠标右键点击目标窗口客户区指定坐标
        
        Args:
            window_index (int): 目标窗口的序号
            x (int): 目标窗口客户区X坐标
            y (int): 目标窗口客户区Y坐标
            delay (int, optional): 点击后延迟毫秒数（默认50ms）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._right_click:
            raise NotImplementedError("DLL中未找到HCMouse_RightClick函数")
        
        return self._right_click(window_index, x, y, delay)
    
    def key_press(self, window_index, vk_code, delay=50):
        """
        后台键盘按下并弹起指定虚拟键
        
        Args:
            window_index (int): 目标窗口的序号
            vk_code (int): 虚拟键码（如VK_RETURN代表回车键）
            delay (int, optional): 按键后延迟毫秒数（默认50ms）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._key_press:
            raise NotImplementedError("DLL中未找到HCKey_Press函数")
        
        return self._key_press(window_index, vk_code, delay)
    
    def send_string(self, window_index, string, interval=100):
        """
        后台向目标窗口发送字符串
        
        Args:
            window_index (int): 目标窗口的序号
            string (str): 要发送的字符串（ASCII编码）
            interval (int, optional): 字符间输入间隔毫秒数（默认100ms）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._send_string:
            raise NotImplementedError("DLL中未找到HCKey_SendString函数")
        
        # 确保字符串是ASCII编码
        try:
            string_bytes = string.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError("字符串必须是ASCII编码")
        
        return self._send_string(window_index, string_bytes, interval)


# 工厂函数
def create_target(dll_path=None, is_debug=None):
    """
    创建后台键鼠模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版本的DLL
    
    Returns:
        HDTARGET: 后台键鼠模块实例
    """
    return HDTARGET(dll_path, is_debug)