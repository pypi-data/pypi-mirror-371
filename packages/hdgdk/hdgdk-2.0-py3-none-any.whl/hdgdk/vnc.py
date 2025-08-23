#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD RPG引擎框架(GDK)VNC(HDVNC)模块封装

该模块支持全虚拟机版本，可通过连接虚拟机端口控制虚拟机的键盘和鼠标操作
使用前需确保虚拟机已开启VNC并设置好端口
"""
from ctypes import c_int64, c_int32, c_bool, c_char_p, byref, POINTER
from .base_module import HDModuleBase


class HDVNC(HDModuleBase):
    """VNC模块封装类"""
    
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化VNC模块
        
        Args:
            dll_path: DLL文件所在路径
            is_debug: 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        self._bind_functions()
        
    def _initialize_functions(self):
        """初始化DLL中的函数"""
        self._bind_functions()
        
    def _bind_functions(self):
        """绑定DLL函数"""
        # 连接虚拟机
        try:
            self._connect = getattr(self.dll, "HCVnc_Connect")
            self._connect.argtypes = [c_int32, c_int32]
            self._connect.restype = c_int64
        except AttributeError:
            self._connect = None
        
        # 关闭与虚拟机的连接
        try:
            self._close = getattr(self.dll, "HCVnc_Close")
            self._close.argtypes = [c_int32]
            self._close.restype = c_int64
        except AttributeError:
            self._close = None
        
        # 鼠标绝对移动
        try:
            self._move_to = getattr(self.dll, "HCVnc_MoveTo")
            self._move_to.argtypes = [c_int32, c_int32, c_int32]
            self._move_to.restype = c_int64
        except AttributeError:
            self._move_to = None
        
        # 鼠标相对移动
        try:
            self._move_to_offset = getattr(self.dll, "HCVnc_MoveToOffset")
            self._move_to_offset.argtypes = [c_int32, c_int32, c_int32]
            self._move_to_offset.restype = c_int64
        except AttributeError:
            self._move_to_offset = None
        
        # 鼠标左键操作
        try:
            self._left_click = getattr(self.dll, "HCVnc_LeftClick")
            self._left_click.argtypes = [c_int32]
            self._left_click.restype = c_int64
        except AttributeError:
            self._left_click = None
        
        try:
            self._left_down = getattr(self.dll, "HCVnc_LeftDown")
            self._left_down.argtypes = [c_int32]
            self._left_down.restype = c_int64
        except AttributeError:
            self._left_down = None
        
        try:
            self._left_up = getattr(self.dll, "HCVnc_LeftUp")
            self._left_up.argtypes = [c_int32]
            self._left_up.restype = c_int64
        except AttributeError:
            self._left_up = None
        
        try:
            self._left_double_click = getattr(self.dll, "HCVnc_LeftDoubleClick")
            self._left_double_click.argtypes = [c_int32]
            self._left_double_click.restype = c_int64
        except AttributeError:
            self._left_double_click = None
        
        # 鼠标右键操作
        try:
            self._right_click = getattr(self.dll, "HCVnc_RightClick")
            self._right_click.argtypes = [c_int32]
            self._right_click.restype = c_int64
        except AttributeError:
            self._right_click = None
        
        try:
            self._right_down = getattr(self.dll, "HCVnc_RightDown")
            self._right_down.argtypes = [c_int32]
            self._right_down.restype = c_int64
        except AttributeError:
            self._right_down = None
        
        try:
            self._right_up = getattr(self.dll, "HCVnc_RightUp")
            self._right_up.argtypes = [c_int32]
            self._right_up.restype = c_int64
        except AttributeError:
            self._right_up = None
        
        # 鼠标滚轮操作
        try:
            self._wheel_down = getattr(self.dll, "HCVnc_WheelDown")
            self._wheel_down.argtypes = [c_int32]
            self._wheel_down.restype = c_int64
        except AttributeError:
            self._wheel_down = None
        
        try:
            self._wheel_up = getattr(self.dll, "HCVnc_WheelUp")
            self._wheel_up.argtypes = [c_int32]
            self._wheel_up.restype = c_int64
        except AttributeError:
            self._wheel_up = None
        
        # 键盘操作
        try:
            self._key_press = getattr(self.dll, "HCVnc_KeyPress")
            self._key_press.argtypes = [c_int32, c_int32, c_bool]
            self._key_press.restype = c_int64
        except AttributeError:
            self._key_press = None
        
        try:
            self._key_down = getattr(self.dll, "HCVnc_KeyDown")
            self._key_down.argtypes = [c_int32, c_int32]
            self._key_down.restype = c_int64
        except AttributeError:
            self._key_down = None
        
        try:
            self._key_up = getattr(self.dll, "HCVnc_KeyUp")
            self._key_up.argtypes = [c_int32, c_int32]
            self._key_up.restype = c_int64
        except AttributeError:
            self._key_up = None
        
        try:
            self._key_press_str = getattr(self.dll, "HCVnc_KeyPressStr")
            self._key_press_str.argtypes = [c_int32, c_char_p, c_bool]
            self._key_press_str.restype = c_int64
        except AttributeError:
            self._key_press_str = None
        
        try:
            self._send_string = getattr(self.dll, "HCVnc_SendString")
            self._send_string.argtypes = [c_int32, c_char_p]
            self._send_string.restype = c_int64
        except AttributeError:
            self._send_string = None
        
        # 截图操作
        try:
            self._open_capture = getattr(self.dll, "HCVnc_OpenCapture")
            self._open_capture.argtypes = [c_int32]
            self._open_capture.restype = c_int64
        except AttributeError:
            self._open_capture = None
        
        try:
            self._close_capture = getattr(self.dll, "HCVnc_CloseCapture")
            self._close_capture.argtypes = [c_int32]
            self._close_capture.restype = c_int64
        except AttributeError:
            self._close_capture = None
    
    def connect(self, windows_index, port):
        """
        连接虚拟机
        
        Args:
            windows_index: 窗口序号（每个窗口序号可绑定一个虚拟机VNC端口；指定0表示重连）
            port: 虚拟机开启VNC设置的端口
        
        Returns:
            int: 操作结果，参考HD返回值表
        
        Notes:
            - 对应的虚拟机需开启VNC并设置好端口
            - 安装插件形式连接VNC时，port==0表示重连
            - 未安装插件形式连接VNC时，port不能为0
        """
        if self._connect:
            return self._connect(windows_index, port)
        return -1
    
    def close(self, windows_index):
        """
        关闭与虚拟机的连接
        
        Args:
            windows_index: 窗口序号（每个窗口序号可绑定一个虚拟机VNC端口）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._close:
            return self._close(windows_index)
        return -1
    
    def move_to(self, windows_index, x, y):
        """
        VNC鼠标绝对移动（自带移动轨迹直线波动防检测）
        
        Args:
            windows_index: 窗口序号
            x: 虚拟机屏幕坐标X
            y: 虚拟机屏幕坐标Y
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._move_to:
            return self._move_to(windows_index, x, y)
        return -1
    
    def move_to_offset(self, windows_index, x, y):
        """
        VNC鼠标相对移动（自带移动轨迹直线波动防检测）
        
        Args:
            windows_index: 窗口序号
            x: 虚拟机屏幕相对坐标X
            y: 虚拟机屏幕相对坐标Y
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._move_to_offset:
            return self._move_to_offset(windows_index, x, y)
        return -1
    
    def left_click(self, windows_index):
        """
        VNC鼠标左键点击
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._left_click:
            return self._left_click(windows_index)
        return -1
    
    def left_down(self, windows_index):
        """
        VNC鼠标左键按下
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._left_down:
            return self._left_down(windows_index)
        return -1
    
    def left_up(self, windows_index):
        """
        VNC鼠标左键弹起
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._left_up:
            return self._left_up(windows_index)
        return -1
    
    def left_double_click(self, windows_index):
        """
        VNC鼠标左键双击
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._left_double_click:
            return self._left_double_click(windows_index)
        return -1
    
    def right_click(self, windows_index):
        """
        VNC鼠标右键点击
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._right_click:
            return self._right_click(windows_index)
        return -1
    
    def right_down(self, windows_index):
        """
        VNC鼠标右键按下
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._right_down:
            return self._right_down(windows_index)
        return -1
    
    def right_up(self, windows_index):
        """
        VNC鼠标右键弹起
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._right_up:
            return self._right_up(windows_index)
        return -1
    
    def wheel_down(self, windows_index):
        """
        VNC鼠标滚轮滚下
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._wheel_down:
            return self._wheel_down(windows_index)
        return -1
    
    def wheel_up(self, windows_index):
        """
        VNC鼠标滚轮滚上
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._wheel_up:
            return self._wheel_up(windows_index)
        return -1
    
    def key_press(self, windows_index, keycode, is_keypad=False):
        """
        VNC键盘按键敲击
        
        Args:
            windows_index: 窗口序号
            keycode: VK键值
            is_keypad: 是否为数字小键盘（默认False）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._key_press:
            return self._key_press(windows_index, keycode, is_keypad)
        return -1
    
    def key_down(self, windows_index, keycode):
        """
        VNC键盘按键按下
        
        Args:
            windows_index: 窗口序号
            keycode: VK键值
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._key_down:
            return self._key_down(windows_index, keycode)
        return -1
    
    def key_up(self, windows_index, keycode):
        """
        VNC键盘按键弹起
        
        Args:
            windows_index: 窗口序号
            keycode: VK键值
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._key_up:
            return self._key_up(windows_index, keycode)
        return -1
    
    def key_press_str(self, windows_index, text, is_keypad=False):
        """
        VNC键盘连续按键字符串（数字+字母）
        
        Args:
            windows_index: 窗口序号
            text: 字符串（ascii编码，如"1234567890qwerty~!@#$%^&*()_+{}|:"<>?"）
            is_keypad: 是否为数字小键盘（默认False）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._key_press_str:
            text_ptr = c_char_p(text.encode('utf-8'))
            return self._key_press_str(windows_index, text_ptr, is_keypad)
        return -1
    
    def send_string(self, windows_index, text):
        """
        VNC键盘输入字符串（中文+数字+符号+字母）
        
        Args:
            windows_index: 窗口序号
            text: 字符串（ascii编码，如"1234567890qwerty~!@#$%^&*()_+{}|:"<>?欢迎使用HD插件"）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if self._send_string:
            text_ptr = c_char_p(text.encode('utf-8'))
            return self._send_string(windows_index, text_ptr)
        return -1
    
    def open_capture(self, windows_index):
        """
        开启截图（内部开启线程循环获取虚拟机画面）
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        
        Notes:
            - 可调用close_capture结束截图线程
        """
        if self._open_capture:
            return self._open_capture(windows_index)
        return -1
    
    def close_capture(self, windows_index):
        """
        关闭截图（结束开启截图时产生的线程）
        
        Args:
            windows_index: 窗口序号
        
        Returns:
            int: 操作结果，参考HD返回值表
        
        Notes:
            - 可能需要多次调用直至关闭成功，通常一次即可
        """
        if self._close_capture:
            return self._close_capture(windows_index)
        return -1


def create_vnc(dll_path=None, is_debug=None):
    """
    创建VNC模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDVNC: VNC模块实例
    """
    return HDVNC(dll_path, is_debug)