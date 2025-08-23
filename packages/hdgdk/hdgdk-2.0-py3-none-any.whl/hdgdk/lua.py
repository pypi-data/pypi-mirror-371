#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK LUA模块
支持LUA自定义接口及按函数名调用，允许在LUA中使用C语言语法，
提供内存读写、模块获取和json格式化库等功能
"""

from .base_module import HDModuleBase, HDModuleFactory


class HDLua(HDModuleBase):
    """
    HD GDK LUA模块
    提供LUA脚本执行和函数调用功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化LUA模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的LUA相关函数
        """
        # 执行或加载LUA文件
        self.dll.HCLUA_ReadFile = self.dll.HCLUA_ReadFile
        self.dll.HCLUA_ReadFile.argtypes = [
            ctypes.c_int32,  # 窗口序号
            ctypes.c_char_p, # 文件名路径
            ctypes.c_int32,  # LUA标识符
            ctypes.c_bool,   # 是否执行
            ctypes.c_bool,   # 是否需要拿到返回值
            ctypes.c_bool    # 是否主线程调用
        ]
        self.dll.HCLUA_ReadFile.restype = ctypes.c_int64
        
        # 关闭LUA线程
        self.dll.HCLUA_CloseLua = self.dll.HCLUA_CloseLua
        self.dll.HCLUA_CloseLua.argtypes = [
            ctypes.c_int32,  # 窗口序号
            ctypes.c_int32   # LUA标识符 (-1表示退出所有LUA线程)
        ]
        self.dll.HCLUA_CloseLua.restype = ctypes.c_int64
        
        # 执行被注册过的LUA函数
        self.dll.HCLUA_ExcuteCall = self.dll.HCLUA_ExcuteCall
        self.dll.HCLUA_ExcuteCall.argtypes = [
            ctypes.c_int32,  # 窗口序号
            ctypes.c_char_p, # 函数名
            ctypes.c_int32,  # 参数数量
            ctypes.c_int64,  # rcx
            ctypes.c_int64,  # rdx
            ctypes.c_int64,  # r8
            ctypes.c_int64,  # r9
            ctypes.c_int64,  # lparam5
            ctypes.c_int64,  # lparam6
            ctypes.c_bool    # 是否主线程调用
        ]
        self.dll.HCLUA_ExcuteCall.restype = ctypes.c_int64
        
    def read_file(self, window_id, file_path, lua_id, execute=False, need_return=False, main_thread=False):
        """
        执行或加载LUA文件
        
        Args:
            window_id (int): 窗口序号（从1开始）
            file_path (str): LUA文件的路径
            lua_id (int): 任意整数标识（不可重复；当需要返回值时，用作线程标识符，建议在0到100以内）
            execute (bool, optional): 为真时执行并加载LUA；为假时仅加载LUA文件
            need_return (bool, optional): 为真时堵塞至LUA文件执行完毕并获取返回值；为假时开启线程执行
            main_thread (bool, optional): 是否由主线程调用，需先挂接主线程
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        # 确保file_path是字节字符串
        file_path_bytes = file_path.encode('utf-8')
        
        return self.dll.HCLUA_ReadFile(
            window_id, 
            file_path_bytes, 
            lua_id, 
            execute, 
            need_return, 
            main_thread
        )
        
    def close_lua(self, window_id, lua_id=-1):
        """
        关闭LUA线程
        
        Args:
            window_id (int): 窗口序号（从1开始）
            lua_id (int, optional): 与read_file中的LUA标识符一一对应；-1表示退出所有LUA线程
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        return self.dll.HCLUA_CloseLua(window_id, lua_id)
        
    def execute_call(self, window_id, function_name, param_count=0, rcx=0, rdx=0, r8=0, r9=0, lparam5=0, lparam6=0, main_thread=False):
        """
        执行被注册过的LUA函数
        
        Args:
            window_id (int): 窗口序号（从1开始）
            function_name (str): 已注册的LUA函数名
            param_count (int, optional): 传递的参数数量
            rcx (int, optional): 调用参数
            rdx (int, optional): 调用参数
            r8 (int, optional): 调用参数
            r9 (int, optional): 调用参数
            lparam5 (int, optional): 调用参数
            lparam6 (int, optional): 调用参数
            main_thread (bool, optional): 是否由主线程调用，需先挂接主线程
        
        Returns:
            int: 操作结果，以JSON格式返回：{"error":0,"ret":AAA,"data":XXX}
        """
        # 确保function_name是字节字符串
        function_name_bytes = function_name.encode('utf-8')
        
        return self.dll.HCLUA_ExcuteCall(
            window_id, 
            function_name_bytes, 
            param_count, 
            rcx, 
            rdx, 
            r8, 
            r9, 
            lparam5, 
            lparam6, 
            main_thread
        )


# 导入ctypes，这需要放在类定义之后以避免循环导入
import ctypes


# 创建LUA模块实例的工厂函数
def create_hd_lua(dll_path=None, is_debug=None):
    """
    创建HDLua模块实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HDLua: 创建的LUA模块实例
    """
    return HDModuleFactory.create_instance(HDLua, dll_path, is_debug)