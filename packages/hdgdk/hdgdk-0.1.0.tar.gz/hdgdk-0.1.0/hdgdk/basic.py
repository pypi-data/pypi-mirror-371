#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 基础功能模块
提供HD引擎的基础功能调用接口
"""

import ctypes
from .base_module import HDModuleBase, HDModuleFactory


class HDBasic(HDModuleBase):
    """
    HD GDK 基础功能模块类
    提供HD引擎的基础功能调用接口
    """
    def _initialize_functions(self):
        """
        初始化DLL中的基础函数
        """
        # 函数 1：HCHD_GetVersion - 获取当前插件版本号
        self.HCHD_GetVersion = self.dll.HCHD_GetVersion
        self.HCHD_GetVersion.restype = ctypes.c_int64
        
        # 函数 2：HCEnv_GetRetJson - 获取最近一次调用接口返回的json字符串
        self.HCEnv_GetRetJson = self.dll.HCEnv_GetRetJson
        self.HCEnv_GetRetJson.argtypes = [ctypes.c_int32]
        self.HCEnv_GetRetJson.restype = ctypes.c_char_p
        
        # 函数 3：HCEnv_GetRetValue - 获取最近一次调用接口返回的值
        self.HCEnv_GetRetValue = self.dll.HCEnv_GetRetValue
        self.HCEnv_GetRetValue.argtypes = [ctypes.c_int32]
        self.HCEnv_GetRetValue.restype = ctypes.c_int64
        
        # 函数 4：HCEnv_GetErrorStr - 通过传递HD返回值获取字符串信息
        self.HCEnv_GetErrorStr = self.dll.HCEnv_GetErrorStr
        self.HCEnv_GetErrorStr.argtypes = [ctypes.c_int32]
        self.HCEnv_GetErrorStr.restype = ctypes.c_char_p
        
        # 函数 5：HCEnv_GetLastError - 获取最近一次调用 WIN32 API错误值
        self.HCEnv_GetLastError = self.dll.HCEnv_GetLastError
        self.HCEnv_GetLastError.restype = ctypes.c_int64
        
        # 函数 6：HCEnv_GetMaxWindowNum - 获取最大窗口数
        self.HCEnv_GetMaxWindowNum = self.dll.HCEnv_GetMaxWindowNum
        self.HCEnv_GetMaxWindowNum.restype = ctypes.c_int64
        
        # 函数 7：HCInject_GetLastInfo - 获取当前环境搭建流程中的操作信息
        self.HCInject_GetLastInfo = self.dll.HCInject_GetLastInfo
        self.HCInject_GetLastInfo.argtypes = [ctypes.c_int32]
        self.HCInject_GetLastInfo.restype = ctypes.c_int64
        
        # 函数 8：HCEnv_GetExcuteEnvInfo - 获取通讯插件所绑定的目标进程的执行线程环境信息
        self.HCEnv_GetExcuteEnvInfo = self.dll.HCEnv_GetExcuteEnvInfo
        self.HCEnv_GetExcuteEnvInfo.argtypes = [ctypes.c_int32]
        self.HCEnv_GetExcuteEnvInfo.restype = ctypes.c_int64
        
        # 函数 9：HCInject_SetPlugin - 设置插件信息
        self.HCInject_SetPlugin = self.dll.HCInject_SetPlugin
        self.HCInject_SetPlugin.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.HCInject_SetPlugin.restype = ctypes.c_int64
    
    def get_version(self):
        """
        获取当前插件版本号
        
        Returns:
            int: 返回值即是版本号，长整数型（8字节）
        """
        return self.HCHD_GetVersion()
    
    def get_ret_json(self, window_index=0):
        """
        获取最近一次调用接口返回的json字符串
        
        Args:
            window_index (int): 窗口序号，可以包含0表示中控
            
        Returns:
            str: 返回的JSON字符串
        """
        result = self.HCEnv_GetRetJson(window_index)
        if result:
            return result.decode('utf-8')
        return ""
    
    def get_ret_value(self, window_index=0):
        """
        获取最近一次调用接口返回的值（用于检测是否有错）
        
        Args:
            window_index (int): 窗口序号，可以包含0表示中控
            
        Returns:
            int: 返回值（参考HD返回值表）
        """
        return self.HCEnv_GetRetValue(window_index)
    
    def get_error_str(self, ret):
        """
        通过传递HD返回值获取字符串信息
        
        Args:
            ret (int): HD返回值（参考HD返回值表）
            
        Returns:
            str: 错误信息字符串
        """
        result = self.HCEnv_GetErrorStr(ret)
        if result:
            return result.decode('utf-8')
        return ""
    
    def get_last_error(self):
        """
        获取最近一次调用 WIN32 API错误值
        
        Returns:
            int: WIN32 API错误值
        """
        return self.HCEnv_GetLastError()
    
    def get_max_window_num(self):
        """
        获取最大窗口数
        
        Returns:
            int: 最大窗口数
        """
        return self.HCEnv_GetMaxWindowNum()
    
    def get_last_inject_info(self, window_index=0):
        """
        获取当前环境搭建流程中的操作信息
        
        Args:
            window_index (int): 窗口序号，从1开始
            
        Returns:
            int: HD状态信息
        """
        return self.HCInject_GetLastInfo(window_index)
    
    def get_execute_env_info(self, window_index=0):
        """
        获取通讯插件所绑定的目标进程的执行线程环境信息
        
        Args:
            window_index (int): 窗口序号，从1开始
            
        Returns:
            str: 执行环境信息字符串
        """
        # 调用函数获取返回值
        ret_code = self.HCEnv_GetExcuteEnvInfo(window_index)
        # 通过get_ret_json获取详细信息
        env_info = self.get_ret_json(window_index)
        return env_info
    
    def set_plugin(self, release_dll=None, debug_dll=None):
        """
        设置插件信息
        
        Args:
            release_dll (str, optional): 发布版本DLL名，为空则使用内置名字
            debug_dll (str, optional): 调试版本DLL名，为空则使用内置名字
            
        Returns:
            int: 操作结果（参考HD返回值表）
        """
        # 转换为C字符串
        release_dll_c = ctypes.c_char_p(release_dll.encode('utf-8')) if release_dll else None
        debug_dll_c = ctypes.c_char_p(debug_dll.encode('utf-8')) if debug_dll else None
        
        return self.HCInject_SetPlugin(release_dll_c, debug_dll_c)


# 工厂函数
def create_hd_basic(dll_path=None, is_debug=None):
    """
    创建基础功能模块实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HDBasic: 基础功能模块实例
    """
    return HDModuleFactory.create_instance(HDBasic, dll_path, is_debug)