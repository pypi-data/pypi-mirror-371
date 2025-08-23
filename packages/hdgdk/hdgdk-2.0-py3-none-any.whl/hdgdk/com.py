#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 自定义插件模块(Com)
提供自定义组件的添加、卸载、接口调用及进程间通信功能，支持X86/X64架构
"""

from .base_module import HDModuleBase, HDModuleFactory
import ctypes
from typing import Optional, Tuple, Union, List


class HDCOM(HDModuleBase):
    """
    HD GDK 自定义插件模块(Com)封装类
    提供自定义组件的添加、卸载、接口调用及进程间通信功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化自定义插件模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
    
    def _initialize_functions(self):
        """
        初始化DLL中的自定义插件模块函数
        """
        # 核心组件管理函数
        self.dll.HCModule_AddComponent = self.dll.HCModule_AddComponent
        self.dll.HCModule_AddComponent.argtypes = [
            ctypes.c_int32,            # 窗口序号
            ctypes.c_char_p,           # 账号
            ctypes.c_char_p,           # 密码
            ctypes.c_char_p,           # 组件绝对路径
            ctypes.c_int64,            # rcx
            ctypes.c_int64,            # rdx
            ctypes.c_int64,            # r8
            ctypes.c_int64,            # r9
            ctypes.c_int64,            # l5
            ctypes.c_int64,            # l6
            ctypes.c_int64,            # addType
            ctypes.c_bool,             # 是否自动初始化
            ctypes.c_bool              # 是否主线程调用
        ]
        self.dll.HCModule_AddComponent.restype = ctypes.c_int64
        
        self.dll.HCModule_DeleteComponent = self.dll.HCModule_DeleteComponent
        self.dll.HCModule_DeleteComponent.argtypes = [
            ctypes.c_int32,            # 窗口序号
            ctypes.c_char_p,           # 组件名
            ctypes.c_bool              # 是否主线程调用
        ]
        self.dll.HCModule_DeleteComponent.restype = ctypes.c_int64
        
        self.dll.HCModule_CALL = self.dll.HCModule_CALL
        self.dll.HCModule_CALL.argtypes = [
            ctypes.c_int32,            # 窗口序号
            ctypes.c_char_p,           # 组件名
            ctypes.c_char_p,           # 函数名字
            ctypes.c_int64,            # rcx
            ctypes.c_int64,            # rdx
            ctypes.c_int64,            # r8
            ctypes.c_int64,            # r9
            ctypes.c_int64,            # l5
            ctypes.c_int64,            # l6
            ctypes.c_bool              # 是否主线程调用
        ]
        self.dll.HCModule_CALL.restype = ctypes.c_int64
        
        self.dll.HCModule_CALLEx = self.dll.HCModule_CALLEx
        self.dll.HCModule_CALLEx.argtypes = [
            ctypes.c_int32,            # 窗口序号
            ctypes.c_char_p,           # 组件名
            ctypes.c_char_p,           # 函数名字
            ctypes.c_int64,            # rcx
            ctypes.c_int64,            # rdx
            ctypes.c_int64,            # r8
            ctypes.c_int64,            # r9
            ctypes.c_int64,            # l5
            ctypes.c_int64,            # l6
            ctypes.c_char_p,           # buffer
            ctypes.c_int,              # bufferSize
            ctypes.c_bool              # 是否主线程调用
        ]
        self.dll.HCModule_CALLEx.restype = ctypes.c_int64
        
        # 插件包装器函数
        self.dll.HCCOM_Load = self.dll.HCCOM_Load
        self.dll.HCCOM_Load.argtypes = [
            ctypes.c_char_p,           # 组件名
            ctypes.c_int32,            # 组件索引
            ctypes.c_int32             # timeOutMs
        ]
        self.dll.HCCOM_Load.restype = ctypes.c_int64
        
        self.dll.HCCOM_Register = self.dll.HCCOM_Register
        self.dll.HCCOM_Register.argtypes = [
            ctypes.c_char_p,           # 函数名
            ctypes.c_int64             # 函数地址
        ]
        self.dll.HCCOM_Register.restype = ctypes.c_int64
        
        self.dll.HCCOM_NotifyToTarget = self.dll.HCCOM_NotifyToTarget
        self.dll.HCCOM_NotifyToTarget.argtypes = [
            ctypes.c_int32,            # 插件序号
            ctypes.c_int32,            # callType
            ctypes.c_bool,             # 堵塞
            ctypes.c_int32,            # 超时毫秒
            ctypes.c_char_p,           # 字符串信息1
            ctypes.c_char_p,           # 字符串信息2
            ctypes.c_int64,            # CALL地址
            ctypes.c_int64,            # rcx
            ctypes.c_int64,            # rdx
            ctypes.c_int64,            # r8
            ctypes.c_int64,            # r9
            ctypes.c_int64,            # l5
            ctypes.c_bool              # 是否主线程调用
        ]
        self.dll.HCCOM_NotifyToTarget.restype = ctypes.c_int64
        
        self.dll.HCCOM_NotifyToController = self.dll.HCCOM_NotifyToController
        self.dll.HCCOM_NotifyToController.argtypes = [
            ctypes.c_int32,            # 插件序号
            ctypes.c_int32,            # callType
            ctypes.c_bool,             # 堵塞
            ctypes.c_int32,            # 超时毫秒
            ctypes.c_char_p,           # 字符串信息1
            ctypes.c_char_p,           # 字符串信息2
            ctypes.c_int64,            # CALL地址
            ctypes.c_int64,            # rcx
            ctypes.c_int64,            # rdx
            ctypes.c_int64,            # r8
            ctypes.c_int64,            # r9
            ctypes.c_int64,            # l5
            ctypes.c_bool              # 是否主线程调用
        ]
        self.dll.HCCOM_NotifyToController.restype = ctypes.c_int64
        
        self.dll.HCCOM_GetRetJson = self.dll.HCCOM_GetRetJson
        self.dll.HCCOM_GetRetJson.argtypes = [ctypes.c_int32]
        self.dll.HCCOM_GetRetJson.restype = ctypes.c_char_p
        
        self.dll.HCCOM_FindCode = self.dll.HCCOM_FindCode
        self.dll.HCCOM_FindCode.argtypes = [
            ctypes.c_char_p,           # 特征码字符串地址
            ctypes.c_int32,            # 偏移
            ctypes.c_int32,            # 次数
            ctypes.c_int32,            # type
            ctypes.c_char_p            # 模块名字
        ]
        self.dll.HCCOM_FindCode.restype = ctypes.c_int64
        
        self.dll.HCCOM_PrintLog = self.dll.HCCOM_PrintLog
        self.dll.HCCOM_PrintLog.argtypes = [ctypes.c_bool]
        self.dll.HCCOM_PrintLog.restype = ctypes.c_int64
        
        self.dll.HCCOM_GetVersion = self.dll.HCCOM_GetVersion
        self.dll.HCCOM_GetVersion.restype = ctypes.c_int64
    
    # 核心组件管理方法
    def add_component(
        self, 
        window_index: int, 
        account: str, 
        password: str, 
        component_path: str, 
        rcx: int = 0, 
        rdx: int = 0, 
        r8: int = 0, 
        r9: int = 0, 
        l5: int = 0, 
        l6: int = 0, 
        add_type: int = -1, 
        auto_init: bool = True, 
        main_thread_call: bool = False
    ) -> int:
        """
        添加并初始化自定义组件（如DLL）
        
        Args:
            window_index (int): 目标窗口序号
            account (str): 自定义组件的验证信息
            password (str): 自定义组件的验证信息
            component_path (str): 组件文件路径（禁止中文路径）
            rcx-rdx-r8-r9-l5-l6: 传递给组件初始化函数的6个参数
            add_type (int): 添加方式（-1/1为无痕加载，不可卸载；2为普通加载，可卸载）
            auto_init (bool): 是否自动调用组件的HDDataInit初始化接口
            main_thread_call (bool): 需配合HC_HookMainThread挂接主线程
            
        Returns:
            int: 操作结果，详见HD返回值表
        """
        return self.dll.HCModule_AddComponent(
            window_index,
            account.encode('utf-8') if account else None,
            password.encode('utf-8') if password else None,
            component_path.encode('utf-8'),
            rcx, rdx, r8, r9, l5, l6,
            add_type,
            auto_init,
            main_thread_call
        )
        
    def delete_component(
        self, 
        window_index: int, 
        component_name: str, 
        main_thread_call: bool = False
    ) -> int:
        """
        卸载指定插件组件
        
        Args:
            window_index (int): 目标窗口序号
            component_name (str): 组件文件名（不含.dll后缀）
            main_thread_call (bool): 是否在主线程调用
            
        Returns:
            int: 操作结果，详见HD返回值表
        """
        return self.dll.HCModule_DeleteComponent(
            window_index,
            component_name.encode('utf-8'),
            main_thread_call
        )
        
    def call_component_function(
        self, 
        window_index: int, 
        component_name: str, 
        function_name: str, 
        rcx: int = 0, 
        rdx: int = 0, 
        r8: int = 0, 
        r9: int = 0, 
        l5: int = 0, 
        l6: int = 0, 
        main_thread_call: bool = False
    ) -> int:
        """
        调用自定义组件中的指定接口
        
        Args:
            window_index (int): 目标窗口序号
            component_name (str): 目标组件文件名（不含后缀）
            function_name (str): 组件中待调用的函数名
            rcx-rdx-r8-r9-l5-l6: 传递给函数的6个参数
            main_thread_call (bool): 是否在主线程调用
            
        Returns:
            int: 函数返回值
        """
        return self.dll.HCModule_CALL(
            window_index,
            component_name.encode('utf-8'),
            function_name.encode('utf-8'),
            rcx, rdx, r8, r9, l5, l6,
            main_thread_call
        )
        
    def call_component_function_ex(
        self, 
        window_index: int, 
        component_name: str, 
        function_name: str, 
        rcx: int = 0, 
        rdx: int = 0, 
        r8: int = 0, 
        r9: int = 0, 
        l5: int = 0, 
        l6: int = 0, 
        buffer: Optional[str] = None, 
        buffer_size: int = 0, 
        main_thread_call: bool = False
    ) -> int:
        """
        扩展接口调用，支持传递缓冲区参数（适用于复杂数据类型）
        
        Args:
            window_index (int): 目标窗口序号
            component_name (str): 目标组件文件名（不含后缀）
            function_name (str): 组件中待调用的函数名
            rcx-rdx-r8-r9-l5-l6: 传递给函数的6个参数
            buffer (str, optional): 缓冲区地址（存放输入/输出数据）
            buffer_size (int): 缓冲区有效大小（最大1024*100字节）
            main_thread_call (bool): 是否在主线程调用
            
        Returns:
            int: 函数返回值
        """
        buffer_ptr = ctypes.c_char_p(buffer.encode('utf-8')) if buffer else None
        return self.dll.HCModule_CALLEx(
            window_index,
            component_name.encode('utf-8'),
            function_name.encode('utf-8'),
            rcx, rdx, r8, r9, l5, l6,
            buffer_ptr,
            buffer_size,
            main_thread_call
        )
        
    # 插件包装器方法
    def load_component(
        self, 
        component_name: str, 
        component_index: int, 
        timeout_ms: int = 300000
    ) -> int:
        """
        加载自定义组件
        
        Args:
            component_name (str): 组件文件名（不含后缀，如hdmad.dll对应hdmad）
            component_index (int): 1-2（最多加载2个组件）
            timeout_ms (int): 堵塞模式下的超时时间（默认5分钟）
            
        Returns:
            int: 操作结果，详见HD返回值表
        """
        return self.dll.HCCOM_Load(
            component_name.encode('utf-8'),
            component_index,
            timeout_ms
        )
        
    def register_function(
        self, 
        function_name: str, 
        function_address: int
    ) -> int:
        """
        注册组件中的接口（需在组件加载时调用）
        
        Args:
            function_name (str): 接口函数名（初始化函数固定为HDDataInit）
            function_address (int): 接口函数的内存地址
            
        Returns:
            int: 操作结果，详见HD返回值表
        """
        return self.dll.HCCOM_Register(
            function_name.encode('utf-8'),
            function_address
        )
        
    def notify_to_target(
        self, 
        plugin_index: int, 
        call_type: int, 
        block: bool = False, 
        timeout_ms: int = 10000, 
        str_info1: Optional[str] = None, 
        str_info2: Optional[str] = None, 
        call_address: int = 0, 
        rcx: int = 0, 
        rdx: int = 0, 
        r8: int = 0, 
        r9: int = 0, 
        l5: int = 0, 
        main_thread_call: bool = False
    ) -> int:
        """
        自定义模块向目标进程发送通知
        
        Args:
            plugin_index (int): 1-2（对应加载的组件）
            call_type (int): 接口编号（需向管理员获取）
            block (bool): 是否等待返回
            timeout_ms (int): 超时毫秒数
            str_info1 (str, optional): 字符串信息1
            str_info2 (str, optional): 字符串信息2
            call_address (int): CALL地址
            rcx-rdx-r8-r9-l5: 自定义传递的数值参数
            main_thread_call (bool): 是否在主线程调用
            
        Returns:
            int: 操作结果，详见HD返回值表
        """
        return self.dll.HCCOM_NotifyToTarget(
            plugin_index,
            call_type,
            block,
            timeout_ms,
            str_info1.encode('utf-8') if str_info1 else None,
            str_info2.encode('utf-8') if str_info2 else None,
            call_address,
            rcx, rdx, r8, r9, l5,
            main_thread_call
        )
        
    def notify_to_controller(
        self, 
        plugin_index: int, 
        call_type: int, 
        block: bool = False, 
        timeout_ms: int = 10000, 
        str_info1: Optional[str] = None, 
        str_info2: Optional[str] = None, 
        call_address: int = 0, 
        rcx: int = 0, 
        rdx: int = 0, 
        r8: int = 0, 
        r9: int = 0, 
        l5: int = 0, 
        main_thread_call: bool = False
    ) -> int:
        """
        自定义模块向中控进程发送通知
        
        Args:
            plugin_index (int): 1-2（对应加载的组件）
            call_type (int): 自定义编号（0-999）
            block (bool): 是否等待返回
            timeout_ms (int): 超时毫秒数
            str_info1 (str, optional): 字符串信息1
            str_info2 (str, optional): 字符串信息2
            call_address (int): CALL地址
            rcx-rdx-r8-r9-l5: 自定义传递的数值参数
            main_thread_call (bool): 是否在主线程调用
            
        Returns:
            int: 操作结果，详见HD返回值表
        """
        return self.dll.HCCOM_NotifyToController(
            plugin_index,
            call_type,
            block,
            timeout_ms,
            str_info1.encode('utf-8') if str_info1 else None,
            str_info2.encode('utf-8') if str_info2 else None,
            call_address,
            rcx, rdx, r8, r9, l5,
            main_thread_call
        )
        
    def get_ret_json(
        self, 
        plugin_index: int
    ) -> str:
        """
        获取中控进程返回的字符串结果
        
        Args:
            plugin_index (int): 1-2（对应加载的组件）
            
        Returns:
            str: 返回自定义的JSON字符串结果
        """
        result_ptr = self.dll.HCCOM_GetRetJson(plugin_index)
        if result_ptr:
            return result_ptr.decode('utf-8')
        return ""
        
    def find_code(
        self, 
        pattern_str: str, 
        offset: int = 0, 
        count: int = 0, 
        search_type: int = 1, 
        module_name: Optional[str] = None
    ) -> int:
        """
        在组件中执行特征码查找
        
        Args:
            pattern_str (str): 特征码字符串地址
            offset (int): 偏移
            count (int): 次数
            search_type (int): 搜索类型（默认1）
            module_name (str, optional): 模块名字
            
        Returns:
            int: 查找到的地址或结果
        """
        return self.dll.HCCOM_FindCode(
            pattern_str.encode('utf-8'),
            offset,
            count,
            search_type,
            module_name.encode('utf-8') if module_name else None
        )
        
    def print_log(
        self, 
        enable: bool
    ) -> int:
        """
        控制debugview调试日志的开关
        
        Args:
            enable (bool): TRUE开启日志，FALSE关闭日志
            
        Returns:
            int: 当前日志状态
        """
        return self.dll.HCCOM_PrintLog(enable)
        
    def get_version(self) -> int:
        """
        获取自定义内存插件的版本号
        
        Returns:
            int: 版本号
        """
        return self.dll.HCCOM_GetVersion()


# 工厂函数
def create_hd_com(dll_path=None, is_debug=None) -> HDCOM:
    """
    创建自定义插件模块实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HDCOM: 自定义插件模块实例
    """
    return HDModuleFactory.create_instance(HDCOM, dll_path, is_debug)


# 模块常量定义
# 添加组件类型常量
ADD_COMPONENT_TYPE = {
    -1: "无痕加载（不可卸载，不支持C++11及异常捕捉）",
    1: "无痕加载（不可卸载，不支持C++11及异常捕捉）",
    2: "普通加载（可卸载）"
}

# 组件索引常量
COMPONENT_INDEX = {
    1: "组件1",
    2: "组件2"
}

# 通知类型常量（中控）
CONTROLLER_NOTIFY_TYPE = {
    # 0-999 自定义编号
    # 用户可根据需要自行定义
}

# 默认超时时间常量（毫秒）
DEFAULT_TIMEOUT = 300000  # 5分钟
NOTIFY_TIMEOUT = 10000    # 10秒

# 搜索类型常量
SEARCH_TYPE = {
    1: "默认搜索类型"
}