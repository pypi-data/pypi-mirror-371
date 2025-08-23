#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD RPG引擎框架(GDK)后台键鼠(MKB)模块Python封装
提供前台及后台的鼠标和键盘模拟功能，支持窗口绑定、键鼠操作、轨迹模拟等
"""

import ctypes
from .base_module import HDModuleBase

class HDMKB(HDModuleBase):
    """
    HD RPG引擎框架后台键鼠(MKB)模块的Python封装类
    提供窗口绑定、鼠标操作、键盘操作等功能
    """
    def _initialize_functions(self):
        """初始化DLL函数绑定"""
        # ========================= 窗口绑定管理函数 =========================
        # 基础绑定函数
        self.dll.HCMKB_Bind.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p]
        self.dll.HCMKB_Bind.restype = ctypes.c_int64
        
        # 扩展绑定函数
        self.dll.HCMKB_BindEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32]
        self.dll.HCMKB_BindEx.restype = ctypes.c_int64
        
        self.dll.HCMKB_BindModeEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_BindModeEx.restype = ctypes.c_int64
        
        # 绑定切换与管理
        self.dll.HCMKB_SwitchBind.argtypes = [ctypes.c_int32, ctypes.c_int64]
        self.dll.HCMKB_SwitchBind.restype = ctypes.c_int64
        
        self.dll.HCMKB_SwitchBindEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.dll.HCMKB_SwitchBindEx.restype = ctypes.c_int64
        
        self.dll.HCMKB_SwitchBindModeEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_SwitchBindModeEx.restype = ctypes.c_int64
        
        self.dll.HCMKB_PauseBind.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_PauseBind.restype = ctypes.c_int64
        
        self.dll.HCMKB_UnBind.argtypes = [ctypes.c_int32]
        self.dll.HCMKB_UnBind.restype = ctypes.c_int64
        
        # ========================= 鼠标操作函数 =========================
        # 鼠标移动
        self.dll.HCMKB_MoveTo.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_MoveTo.restype = ctypes.c_int64
        
        self.dll.HCMKB_MoveR.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_MoveR.restype = ctypes.c_int64
        
        # 左键操作
        self.dll.HCMKB_LeftDown.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_LeftDown.restype = ctypes.c_int64
        
        self.dll.HCMKB_LeftUp.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_LeftUp.restype = ctypes.c_int64
        
        self.dll.HCMKB_LeftClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_LeftClick.restype = ctypes.c_int64
        
        self.dll.HCMKB_LeftDoubleClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_LeftDoubleClick.restype = ctypes.c_int64
        
        # 右键操作
        self.dll.HCMKB_RightDown.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_RightDown.restype = ctypes.c_int64
        
        self.dll.HCMKB_RightUp.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_RightUp.restype = ctypes.c_int64
        
        self.dll.HCMKB_RightClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_RightClick.restype = ctypes.c_int64
        
        self.dll.HCMKB_RightDoubleClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_RightDoubleClick.restype = ctypes.c_int64
        
        # 中键操作
        self.dll.HCMKB_MiddleDown.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_MiddleDown.restype = ctypes.c_int64
        
        self.dll.HCMKB_MiddleUp.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_MiddleUp.restype = ctypes.c_int64
        
        self.dll.HCMKB_MiddleClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_MiddleClick.restype = ctypes.c_int64
        
        self.dll.HCMKB_MiddleDoubleClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_MiddleDoubleClick.restype = ctypes.c_int64
        
        # 滚轮操作
        self.dll.HCMKB_WheelUp.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_WheelUp.restype = ctypes.c_int64
        
        self.dll.HCMKB_WheelDown.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_WheelDown.restype = ctypes.c_int64
        
        # ========================= 键盘操作函数 =========================
        # 单键操作
        self.dll.HCMKB_KeyDown.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_KeyDown.restype = ctypes.c_int64
        
        self.dll.HCMKB_KeyUp.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_KeyUp.restype = ctypes.c_int64
        
        self.dll.HCMKB_KeyPress.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_KeyPress.restype = ctypes.c_int64
        
        # 字符串发送
        self.dll.HCMKB_KeyPressA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_KeyPressA.restype = ctypes.c_int64
        
        self.dll.HCMKB_KeyPressW.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_KeyPressW.restype = ctypes.c_int64
        
        self.dll.HCMKB_SendStringA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_SendStringA.restype = ctypes.c_int64
        
        self.dll.HCMKB_SendStringW.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_SendStringW.restype = ctypes.c_int64
        
        # 剪切板相关
        self.dll.HCMKB_SendPaste.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_SendPaste.restype = ctypes.c_int64
        
        self.dll.HCMKB_SendPasteEx.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_SendPasteEx.restype = ctypes.c_int64
        
        self.dll.HCMKB_SetClipboard.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_SetClipboard.restype = ctypes.c_int64
        
        self.dll.HCMKB_GetClipboard.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_GetClipboard.restype = ctypes.c_int64
        
        # 特殊窗口发送
        self.dll.HCMKB_SendStringF.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32]
        self.dll.HCMKB_SendStringF.restype = ctypes.c_int64
        
        self.dll.HCMKB_SendKeyDownF.argtypes = [ctypes.c_int64, ctypes.c_int32]
        self.dll.HCMKB_SendKeyDownF.restype = ctypes.c_int64
        
        self.dll.HCMKB_SendKeyUpF.argtypes = [ctypes.c_int64, ctypes.c_int32]
        self.dll.HCMKB_SendKeyUpF.restype = ctypes.c_int64
        
        self.dll.HCMKB_SendKeyPressF.argtypes = [ctypes.c_int64, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCMKB_SendKeyPressF.restype = ctypes.c_int64
        
        self.dll.HCMKB_SendDeleteTextF.argtypes = [ctypes.c_int64]
        self.dll.HCMKB_SendDeleteTextF.restype = ctypes.c_int64
        
        # ========================= 辅助功能函数 =========================
        self.dll.HCMKB_SetRealMouse.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.dll.HCMKB_SetRealMouse.restype = ctypes.c_int64
        
        self.dll.HCMKB_GetMousePos.argtypes = [ctypes.c_int32]
        self.dll.HCMKB_GetMousePos.restype = ctypes.c_int64
    
    # ========================= 窗口绑定管理函数实现 =========================
    def bind(self, window_index, hwnd, bind_attr=None):
        """
        绑定窗口，设置操作模式及输入属性
        
        Args:
            window_index (int): 目标窗口序号（1-61为窗口模式，-1/0为全屏前台模式）
            hwnd (int): 目标窗口句柄
            bind_attr (str, optional): 20位字符串（格式"0|0|...|0|"），每一位控制一项输入属性
        
        Returns:
            int: 操作结果
        """
        attr_ptr = ctypes.c_char_p(bind_attr.encode('utf-8')) if bind_attr else None
        return self.dll.HCMKB_Bind(window_index, hwnd, attr_ptr)
    
    def bind_ex(self, window_index, hwnd, bind_attr=None, b_ret_move=1):
        """
        扩展绑定函数，支持刷新窗口
        
        Args:
            window_index (int): 目标窗口序号
            hwnd (int): 目标窗口句柄
            bind_attr (str, optional): 绑定属性字符串
            b_ret_move (int): 是否刷新窗口（1为是，0为否）
        
        Returns:
            int: 操作结果
        """
        attr_ptr = ctypes.c_char_p(bind_attr.encode('utf-8')) if bind_attr else None
        return self.dll.HCMKB_BindEx(window_index, hwnd, attr_ptr, b_ret_move)
    
    def bind_mode_ex(self, window_index, hwnd, bind_attr=None, b_ret_move=1, mode=0):
        """
        扩展绑定函数，支持刷新窗口和模式选择
        
        Args:
            window_index (int): 目标窗口序号
            hwnd (int): 目标窗口句柄
            bind_attr (str, optional): 绑定属性字符串
            b_ret_move (int): 是否刷新窗口
            mode (int): 绑定模式（0通用模式，1/2/3为备选模式）
        
        Returns:
            int: 操作结果
        """
        attr_ptr = ctypes.c_char_p(bind_attr.encode('utf-8')) if bind_attr else None
        return self.dll.HCMKB_BindModeEx(window_index, hwnd, attr_ptr, b_ret_move, mode)
    
    def switch_bind(self, window_index, hwnd):
        """
        切换绑定到子窗口句柄
        
        Args:
            window_index (int): 窗口序号
            hwnd (int): 新的窗口句柄
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCMKB_SwitchBind(window_index, hwnd)
    
    def switch_bind_ex(self, window_index, hwnd, b_ret_move=1):
        """
        切换绑定到子窗口句柄（支持刷新窗口）
        
        Args:
            window_index (int): 窗口序号
            hwnd (int): 新的窗口句柄
            b_ret_move (int): 是否刷新窗口
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCMKB_SwitchBindEx(window_index, hwnd, b_ret_move)
    
    def switch_bind_mode_ex(self, window_index, hwnd, b_ret_move=1, mode=0):
        """
        切换绑定到子窗口句柄（支持刷新窗口和模式选择）
        
        Args:
            window_index (int): 窗口序号
            hwnd (int): 新的窗口句柄
            b_ret_move (int): 是否刷新窗口
            mode (int): 绑定模式
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCMKB_SwitchBindModeEx(window_index, hwnd, b_ret_move, mode)
    
    def pause_bind(self, window_index, b_pause=True, b_ret_move=1):
        """
        暂停或恢复后台绑定
        
        Args:
            window_index (int): 窗口序号
            b_pause (bool): True暂停，False恢复
            b_ret_move (int): 是否刷新窗口
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCMKB_PauseBind(window_index, 1 if b_pause else 0, b_ret_move)
    
    def unbind(self, window_index):
        """
        解绑窗口
        
        Args:
            window_index (int): 窗口序号
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCMKB_UnBind(window_index)
    
    # ========================= 鼠标操作函数实现 =========================
    def move_to(self, window_index, x, y, simulate_track=True, track_type=-1, window_state=-1):
        """
        鼠标绝对移动到窗口客户区指定坐标
        
        Args:
            window_index (int): 窗口序号
            x (int): 目标X坐标
            y (int): 目标Y坐标
            simulate_track (bool): 是否模拟鼠标轨迹
            track_type (int): 轨迹类型（-1/1随机轨迹，2直线轨迹，3直线波动轨迹）
            window_state (int): 窗口状态
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCMKB_MoveTo(window_index, x, y, simulate_track, track_type, window_state)
    
    def move_r(self, window_index, dx, dy, simulate_track=True, track_type=-1, window_state=-1):
        """
        鼠标相对移动（基于当前位置偏移）
        
        Args:
            window_index (int): 窗口序号
            dx (int): X轴偏移量
            dy (int): Y轴偏移量
            simulate_track (bool): 是否模拟鼠标轨迹
            track_type (int): 轨迹类型
            window_state (int): 窗口状态
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCMKB_MoveR(window_index, dx, dy, simulate_track, track_type, window_state)
    
    # 左键操作
    def left_down(self, window_index, window_state=-1):
        """左键按下"""
        return self.dll.HCMKB_LeftDown(window_index, window_state)
    
    def left_up(self, window_index, window_state=-1):
        """左键弹起"""
        return self.dll.HCMKB_LeftUp(window_index, window_state)
    
    def left_click(self, window_index, delay_ms=50, window_state=-1):
        """左键点击"""
        return self.dll.HCMKB_LeftClick(window_index, delay_ms, window_state)
    
    def left_double_click(self, window_index, delay_ms=50, window_state=-1):
        """左键双击"""
        return self.dll.HCMKB_LeftDoubleClick(window_index, delay_ms, window_state)
    
    # 右键操作
    def right_down(self, window_index, window_state=-1):
        """右键按下"""
        return self.dll.HCMKB_RightDown(window_index, window_state)
    
    def right_up(self, window_index, window_state=-1):
        """右键弹起"""
        return self.dll.HCMKB_RightUp(window_index, window_state)
    
    def right_click(self, window_index, delay_ms=50, window_state=-1):
        """右键点击"""
        return self.dll.HCMKB_RightClick(window_index, delay_ms, window_state)
    
    def right_double_click(self, window_index, delay_ms=50, window_state=-1):
        """右键双击"""
        return self.dll.HCMKB_RightDoubleClick(window_index, delay_ms, window_state)
    
    # 中键操作
    def middle_down(self, window_index, window_state=-1):
        """中键按下"""
        return self.dll.HCMKB_MiddleDown(window_index, window_state)
    
    def middle_up(self, window_index, window_state=-1):
        """中键弹起"""
        return self.dll.HCMKB_MiddleUp(window_index, window_state)
    
    def middle_click(self, window_index, delay_ms=50, window_state=-1):
        """中键点击"""
        return self.dll.HCMKB_MiddleClick(window_index, delay_ms, window_state)
    
    def middle_double_click(self, window_index, delay_ms=50, window_state=-1):
        """中键双击"""
        return self.dll.HCMKB_MiddleDoubleClick(window_index, delay_ms, window_state)
    
    # 滚轮操作
    def wheel_up(self, window_index, window_state=-1):
        """鼠标滚轮向上滚动"""
        return self.dll.HCMKB_WheelUp(window_index, window_state)
    
    def wheel_down(self, window_index, window_state=-1):
        """鼠标滚轮向下滚动"""
        return self.dll.HCMKB_WheelDown(window_index, window_state)
    
    # ========================= 键盘操作函数实现 =========================
    # 单键操作
    def key_down(self, window_index, virtual_key, window_state=-1):
        """键盘按键按下"""
        return self.dll.HCMKB_KeyDown(window_index, virtual_key, window_state)
    
    def key_up(self, window_index, virtual_key, window_state=-1):
        """键盘按键弹起"""
        return self.dll.HCMKB_KeyUp(window_index, virtual_key, window_state)
    
    def key_press(self, window_index, virtual_key, delay_ms=20, window_state=-1):
        """键盘按键点击"""
        return self.dll.HCMKB_KeyPress(window_index, virtual_key, delay_ms, window_state)
    
    # 字符串发送
    def key_press_a(self, window_index, text, delay_ms=20, window_state=-1):
        """连续按键输入ASCII字符串（逐个按键发送）"""
        return self.dll.HCMKB_KeyPressA(window_index, text.encode('utf-8'), delay_ms, window_state)
    
    def key_press_w(self, window_index, text, delay_ms=20, window_state=-1):
        """连续按键输入Unicode字符串（逐个按键发送）"""
        return self.dll.HCMKB_KeyPressW(window_index, text, delay_ms, window_state)
    
    def send_string_a(self, window_index, text, delay_ms=20, window_state=-1):
        """发送ASCII字符串（非逐个按键，效率更高）"""
        return self.dll.HCMKB_SendStringA(window_index, text.encode('utf-8'), delay_ms, window_state)
    
    def send_string_w(self, window_index, text, delay_ms=20, window_state=-1):
        """发送Unicode字符串（非逐个按键，效率更高）"""
        return self.dll.HCMKB_SendStringW(window_index, text, delay_ms, window_state)
    
    # 剪切板相关
    def send_paste(self, window_index, buffer, buffer_size, text_type=1):
        """发送剪切板内容到窗口"""
        buffer_ptr = (ctypes.c_ubyte * buffer_size)(*buffer)
        return self.dll.HCMKB_SendPaste(window_index, buffer_ptr, buffer_size, text_type)
    
    def send_paste_ex(self, window_index, buffer, buffer_size, text_type=1, b_send=1):
        """扩展发送剪切板内容到窗口"""
        buffer_ptr = (ctypes.c_ubyte * buffer_size)(*buffer)
        return self.dll.HCMKB_SendPasteEx(window_index, buffer_ptr, buffer_size, text_type, b_send)
    
    def set_clipboard(self, buffer, buffer_size, text_type=1):
        """设置剪切板字符串"""
        buffer_ptr = (ctypes.c_ubyte * buffer_size)(*buffer)
        return self.dll.HCMKB_SetClipboard(buffer_ptr, buffer_size, text_type)
    
    def get_clipboard(self, buffer_size=4096, text_type=1):
        """获取剪切板字符串"""
        buffer = (ctypes.c_ubyte * buffer_size)()
        result = self.dll.HCMKB_GetClipboard(buffer, buffer_size, text_type)
        # 转换缓冲区内容为字符串
        if text_type == 1:  # ASCII
            content = bytes(buffer[:result]).decode('ascii', errors='ignore')
        else:  # Unicode
            content = bytes(buffer[:result*2]).decode('utf-16le', errors='ignore')
        return result, content
    
    # 特殊窗口发送
    def send_string_f(self, hwnd, text, delay_ms=20):
        """向指定窗口发送字符串（无需绑定通讯）"""
        return self.dll.HCMKB_SendStringF(hwnd, text.encode('utf-8'), delay_ms)
    
    def send_key_down_f(self, hwnd, virtual_key):
        """向指定窗口发送按键按下（无需绑定通讯）"""
        return self.dll.HCMKB_SendKeyDownF(hwnd, virtual_key)
    
    def send_key_up_f(self, hwnd, virtual_key):
        """向指定窗口发送按键弹起（无需绑定通讯）"""
        return self.dll.HCMKB_SendKeyUpF(hwnd, virtual_key)
    
    def send_key_press_f(self, hwnd, virtual_key, delay_ms=20):
        """向指定窗口发送按键点击（无需绑定通讯）"""
        return self.dll.HCMKB_SendKeyPressF(hwnd, virtual_key, delay_ms)
    
    def send_delete_text_f(self, hwnd):
        """清空子窗口内容（如edit/richedit控件）"""
        return self.dll.HCMKB_SendDeleteTextF(hwnd)
    
    # ========================= 辅助功能函数实现 =========================
    def set_real_mouse(self, step_length=30, step_count=100, step_delay=20, debug=False):
        """设置鼠标轨迹参数"""
        return self.dll.HCMKB_SetRealMouse(step_length, step_count, step_delay, debug)
    
    def get_mouse_pos(self, window_index):
        """获取后台/前台鼠标位置"""
        result = self.dll.HCMKB_GetMousePos(window_index)
        # 解析返回值，低4字节是X坐标，高4字节是Y坐标
        x = result & 0xFFFFFFFF
        y = (result >> 32) & 0xFFFFFFFF
        return result, x, y

# 工厂函数
def create_hd_mkb(dll_path=None, is_debug=None):
    """
    创建HDMKB实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HDMKB: MKB模块实例
    """
    return HDMKB(dll_path, is_debug)