#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD RPG引擎框架(GDK)VT(HDVT)模块Python封装
基于VT技术实现，提供内存操作、模块信息获取、无痕HOOK、远程执行和注入等功能
注意：不支持AMD CPU，使用前需安装HDVT驱动
"""

import ctypes
from .base_module import HDModuleBase, HDModuleFactory


class HDVT(HDModuleBase):
    """HD RPG引擎框架VT(HDVT)模块的Python封装类"""
    
    def _initialize_functions(self):
        """初始化DLL函数绑定"""
        # 绑定HCHDVT_AllocateMemory函数
        self.HCHDVT_AllocateMemory = self.dll.HCHDVT_AllocateMemory
        self.HCHDVT_AllocateMemory.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.HCHDVT_AllocateMemory.restype = ctypes.c_int64
        
        # 绑定HCHDVT_FreeMemory函数
        self.HCHDVT_FreeMemory = self.dll.HCHDVT_FreeMemory
        self.HCHDVT_FreeMemory.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCHDVT_FreeMemory.restype = ctypes.c_int64
        
        # 绑定HCHDVT_Read函数
        self.HCHDVT_Read = self.dll.HCHDVT_Read
        self.HCHDVT_Read.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int32]
        self.HCHDVT_Read.restype = ctypes.c_int64
        
        # 绑定HCHDVT_Write函数
        self.HCHDVT_Write = self.dll.HCHDVT_Write
        self.HCHDVT_Write.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int32]
        self.HCHDVT_Write.restype = ctypes.c_int64
        
        # 绑定HCHDVT_GetModule函数
        self.HCHDVT_GetModule = self.dll.HCHDVT_GetModule
        self.HCHDVT_GetModule.argtypes = [ctypes.c_int32, ctypes.c_char_p]
        self.HCHDVT_GetModule.restype = ctypes.c_int64
        
        # 绑定HCHDVT_GetModuleFun函数
        self.HCHDVT_GetModuleFun = self.dll.HCHDVT_GetModuleFun
        self.HCHDVT_GetModuleFun.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p]
        self.HCHDVT_GetModuleFun.restype = ctypes.c_int64
        
        # 绑定HCHDVT_Hook函数
        self.HCHDVT_Hook = self.dll.HCHDVT_Hook
        self.HCHDVT_Hook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32]
        self.HCHDVT_Hook.restype = ctypes.c_int64
        
        # 绑定HCHDVT_RemoteCall函数
        self.HCHDVT_RemoteCall = self.dll.HCHDVT_RemoteCall
        self.HCHDVT_RemoteCall.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
        self.HCHDVT_RemoteCall.restype = ctypes.c_int64
        
        # 绑定HCHDVT_InjectX64函数
        self.HCHDVT_InjectX64 = self.dll.HCHDVT_InjectX64
        self.HCHDVT_InjectX64.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
        self.HCHDVT_InjectX64.restype = ctypes.c_int64
        
        # 绑定HCHDVT_InjectX86函数
        self.HCHDVT_InjectX86 = self.dll.HCHDVT_InjectX86
        self.HCHDVT_InjectX86.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
        self.HCHDVT_InjectX86.restype = ctypes.c_int64
        
        # 绑定HCHDVT_InstallPlugX64函数
        self.HCHDVT_InstallPlugX64 = self.dll.HCHDVT_InstallPlugX64
        self.HCHDVT_InstallPlugX64.argtypes = [ctypes.c_int32]
        self.HCHDVT_InstallPlugX64.restype = ctypes.c_int64
        
        # 绑定HCHDVT_InstallPlugX86函数
        self.HCHDVT_InstallPlugX86 = self.dll.HCHDVT_InstallPlugX86
        self.HCHDVT_InstallPlugX86.argtypes = [ctypes.c_int32]
        self.HCHDVT_InstallPlugX86.restype = ctypes.c_int64
    
    def allocate_memory(self, pid, size):
        """
        VT驱动申请内存
        
        参数:
            pid (int): 进程PID
            size (int): 申请内存大小（字节）
        
        返回值:
            int: 操作结果，成功返回申请的内存地址，失败返回错误码
        
        备注:
            需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
        """
        return self.HCHDVT_AllocateMemory(pid, size)
    
    def free_memory(self, pid, addr, size):
        """
        VT驱动释放内存
        
        参数:
            pid (int): 进程PID
            addr (int): 释放地址（由allocate_memory申请的内存地址）
            size (int): 申请内存大小（字节）
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败
        
        备注:
            需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
        """
        return self.HCHDVT_FreeMemory(pid, addr, size)
    
    def read_memory(self, pid, addr, size):
        """
        VT驱动读内存
        
        参数:
            pid (int): 进程PID
            addr (int): 目标地址
            size (int): 读取大小（字节）
        
        返回值:
            tuple: (操作结果, 读取的数据)
                  操作结果：0表示成功，非0表示失败
                  读取的数据：bytes类型，成功时返回读取的数据，失败时返回None
        
        备注:
            需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
        """
        # 创建缓冲区
        buffer = ctypes.create_string_buffer(size)
        # 调用DLL函数
        result = self.HCHDVT_Read(pid, addr, buffer, size)
        # 返回结果和数据
        if result == 0:
            return (result, buffer.raw)
        else:
            return (result, None)
    
    def write_memory(self, pid, addr, data):
        """
        VT驱动写内存
        
        参数:
            pid (int): 进程PID
            addr (int): 目标地址
            data (bytes): 要写入的数据
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败
        
        备注:
            需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
        """
        # 转换数据为指针
        buffer = ctypes.create_string_buffer(data)
        size = len(data)
        # 调用DLL函数
        return self.HCHDVT_Write(pid, addr, buffer, size)
    
    def get_module(self, pid, module_name):
        """
        VT驱动获取模块地址
        
        参数:
            pid (int): 进程PID
            module_name (str): 模块名字（将转换为ASCII编码）
        
        返回值:
            int: 操作结果，成功返回模块基地址，失败返回错误码
        
        备注:
            需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
        """
        # 将模块名转换为ASCII编码
        module_name_asc = module_name.encode('ascii')
        # 调用DLL函数
        return self.HCHDVT_GetModule(pid, module_name_asc)
    
    def get_module_function(self, pid, module_addr, func_name):
        """
        VT驱动获取模块函数地址
        
        参数:
            pid (int): 进程PID
            module_addr (int): 模块地址
            func_name (str): 函数名字（将转换为ASCII编码）
        
        返回值:
            int: 操作结果，成功返回函数地址，失败返回错误码
        
        备注:
            需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
        """
        # 将函数名转换为ASCII编码
        func_name_asc = func_name.encode('ascii')
        # 调用DLL函数
        return self.HCHDVT_GetModuleFun(pid, module_addr, func_name_asc)
    
    def hook(self, pid, addr, data, hook_type):
        """
        VT驱动无痕HOOK，过CRC
        
        参数:
            pid (int): 进程PID
            addr (int): HOOK地址
            data (bytes): 写入数据（若需跳转到自定义函数，应为jmp等跳转指令）
            hook_type (int): 操作类型（0：关闭VT；1：开启VT；2：VT写入；3：VT恢复之前HOOK的地址）
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败
        
        备注:
            - 需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
            - 若需跳转到自定义函数，缓冲区应为jmp等跳转指令，指向自行申请内存中的shellcode
        """
        # 转换数据为指针
        buffer = ctypes.create_string_buffer(data)
        size = len(data)
        # 调用DLL函数
        return self.HCHDVT_Hook(pid, addr, buffer, size, hook_type)
    
    def remote_call(self, pid, shellcode):
        """
        VT驱动远程插入执行
        
        参数:
            pid (int): 进程PID
            shellcode (bytes): 执行shellcode
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败
        
        备注:
            - 需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
            - 内部会拷贝shellcode到目标进程
        """
        # 转换shellcode为指针
        buffer = ctypes.create_string_buffer(shellcode)
        size = len(shellcode)
        # 调用DLL函数
        return self.HCHDVT_RemoteCall(pid, buffer, size)
    
    def inject_x64(self, pid, dll_data):
        """
        VT驱动无痕无模块注入X64 DLL
        
        参数:
            pid (int): 进程PID
            dll_data (bytes): DLL二进制数据
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败
        
        备注:
            - 需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
            - 用于向64位进程注入DLL
        """
        # 转换DLL数据为指针
        buffer = ctypes.create_string_buffer(dll_data)
        size = len(dll_data)
        # 调用DLL函数
        return self.HCHDVT_InjectX64(pid, buffer, size)
    
    def inject_x86(self, pid, dll_data):
        """
        VT驱动无痕无模块注入X86 DLL
        
        参数:
            pid (int): 进程PID
            dll_data (bytes): DLL二进制数据
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败
        
        备注:
            - 需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
            - 用于向32位进程注入DLL
        """
        # 转换DLL数据为指针
        buffer = ctypes.create_string_buffer(dll_data)
        size = len(dll_data)
        # 调用DLL函数
        return self.HCHDVT_InjectX86(pid, buffer, size)
    
    def install_plug_x64(self, pid):
        """
        VT驱动无痕无模块安装X64插件到目标进程中
        
        参数:
            pid (int): 进程PID
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败
        
        备注:
            - 需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
            - 用于向64位进程安装HD插件
        """
        return self.HCHDVT_InstallPlugX64(pid)
    
    def install_plug_x86(self, pid):
        """
        VT驱动无痕无模块安装X86插件到目标进程中
        
        参数:
            pid (int): 进程PID
        
        返回值:
            int: 操作结果，0表示成功，非0表示失败
        
        备注:
            - 需安装HDVT驱动，使用前需调用HCHD_LoadDrv2并传递参数2
            - 用于向32位进程安装HD插件
        """
        return self.HCHDVT_InstallPlugX86(pid)


def create_vt(dll_path=None, is_debug=False):
    """
    创建HDVT模块实例
    
    参数:
        dll_path (str, optional): DLL文件路径，如果为None则使用默认路径
        is_debug (bool, optional): 是否使用调试版DLL，默认为False
    
    返回值:
        HDVT: HDVT模块实例
    
    备注:
        - 不支持AMD CPU
        - 使用前需调用HCHD_LoadDrv2并传递参数2来安装HDVT驱动
    """
    return HDModuleFactory.create_instance(HDVT, dll_path, is_debug)