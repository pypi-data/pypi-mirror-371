#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD RPG引擎框架(GDK)盾模块(PP)Python封装
提供进程及窗口保护功能，用于过反外挂引擎
"""

import ctypes
from .base_module import HDModuleBase, HDModuleFactory


class HDPP(HDModuleBase):
    """HD RPG引擎框架盾模块(PP)的Python封装类"""
    
    def _initialize_functions(self):
        """初始化DLL函数绑定"""
        # 绑定HCHDPP_Protect函数
        self.HCHDPP_Protect = self.dll.HCHDPP_Protect
        self.HCHDPP_Protect.argtypes = [ctypes.c_int32]
        self.HCHDPP_Protect.restype = ctypes.c_int64
        
        # 绑定HCHDPW_OnProtect函数
        self.HCHDPW_OnProtect = self.dll.HCHDPW_OnProtect
        self.HCHDPW_OnProtect.argtypes = [ctypes.c_int64]
        self.HCHDPW_OnProtect.restype = ctypes.c_int64
        
        # 绑定HCHDPW_OffProtect函数
        self.HCHDPW_OffProtect = self.dll.HCHDPW_OffProtect
        self.HCHDPW_OffProtect.argtypes = []
        self.HCHDPW_OffProtect.restype = ctypes.c_int64
    
    def protect_process(self, pid):
        """
        一键保护进程（包括隐藏等功能）
        
        参数:
            pid (int): 进程PID
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败，具体错误码参考HD返回值表
        
        备注:
            需要调用`HCHD_LoadDrv2`并传递参数3来安装保护盾HDPP驱动
        """
        return self.HCHDPP_Protect(pid)
    
    def on_window_protect(self, hwnd):
        """
        打开窗口保护及子窗口保护
        
        参数:
            hwnd (int): 目标窗口句柄（一般为父窗口句柄）
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败，具体错误码参考HD返回值表
        
        备注:
            - 需要调用`HCHD_LoadDrv2`并传递参数5来安装保护盾HDPW驱动
            - 可多次调用，内部会将指定的保护窗口句柄及其所属子窗口一同保护
        """
        return self.HCHDPW_OnProtect(hwnd)
    
    def off_window_protect(self):
        """
        取消所有已指定保护的窗口保护
        
        参数:
            无
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败，具体错误码参考HD返回值表
        
        备注:
            需要调用`HCHD_LoadDrv2`并传递参数5来安装保护盾HDPW驱动，
            可取消所有通过`on_window_protect`设置的窗口保护
        """
        return self.HCHDPW_OffProtect()


def create_pp(dll_path=None, is_debug=False):
    """
    创建HDPP模块实例
    
    参数:
        dll_path (str, optional): DLL文件路径，如果为None则使用默认路径
        is_debug (bool, optional): 是否使用调试版DLL，默认为False
    
    返回值:
        HDPP: HDPP模块实例
    """
    return HDModuleFactory.create_instance(HDPP, dll_path, is_debug)