#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 虚拟机DMA模块[VMDMA]
通过直接内存访问（DMA）技术与虚拟机交互，支持内存读写、进程管理、截图、键鼠控制及特定游戏的定制化操作。
"""

import ctypes
from typing import Optional, Union, List, Tuple

from .base_module import HDModuleBase


# 定义VMDMA相关常量
VMDMA_DEFAULT_IP = "127.0.0.1"
VMDMA_DEFAULT_PORT = 6532
VMDMA_MAX_BYTE_SIZE = 1024
VMDMA_MAX_UNICODE_LENGTH = 100
VMDMA_MAX_ASCII_LENGTH = 200

# 内存大小类型
size_t = ctypes.c_size_t


class HDVMDMA(HDModuleBase):
    """
    HD GDK 虚拟机DMA模块[VMDMA]
    提供虚拟机内存访问、进程管理、键鼠控制等功能的Python封装
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化VMDMA模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 一、DMA服务器管理
        # 版本查询
        self.HCVMDMA_GetVersion = self.dll.HCVMDMA_GetVersion
        self.HCVMDMA_GetVersion.argtypes = [ctypes.c_int32]
        self.HCVMDMA_GetVersion.restype = ctypes.c_int64
        
        self.HCVMDMA_IsVersion = self.dll.HCVMDMA_IsVersion
        self.HCVMDMA_IsVersion.argtypes = [ctypes.c_int32]
        self.HCVMDMA_IsVersion.restype = ctypes.c_int64
        
        # 服务器启停与状态
        self.HCVMDMA_StartServer = self.dll.HCVMDMA_StartServer
        self.HCVMDMA_StartServer.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
        self.HCVMDMA_StartServer.restype = ctypes.c_int64
        
        self.HCVMDMA_CloseServer = self.dll.HCVMDMA_CloseServer
        self.HCVMDMA_CloseServer.restype = ctypes.c_int64
        
        self.HCVMDMA_ServerIsStart = self.dll.HCVMDMA_ServerIsStart
        self.HCVMDMA_ServerIsStart.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.HCVMDMA_ServerIsStart.restype = ctypes.c_int64
        
        # 二、虚拟机初始化与关联
        self.HCVMDMA_Init = self.dll.HCVMDMA_Init
        self.HCVMDMA_Init.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.HCVMDMA_Init.restype = ctypes.c_int64
        
        self.HCVMDMA_Close = self.dll.HCVMDMA_Close
        self.HCVMDMA_Close.argtypes = [ctypes.c_int32]
        self.HCVMDMA_Close.restype = ctypes.c_int64
        
        # 三、内存操作
        # 内存读取
        self.HCVMDMA_Read = self.dll.HCVMDMA_Read
        self.HCVMDMA_Read.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCVMDMA_Read.restype = ctypes.c_int64
        
        self.HCVMDMA_ReadFloat = self.dll.HCVMDMA_ReadFloat
        self.HCVMDMA_ReadFloat.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]
        self.HCVMDMA_ReadFloat.restype = ctypes.c_float
        
        self.HCVMDMA_ReadDouble = self.dll.HCVMDMA_ReadDouble
        self.HCVMDMA_ReadDouble.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]
        self.HCVMDMA_ReadDouble.restype = ctypes.c_double
        
        self.HCVMDMA_ReadBytes = self.dll.HCVMDMA_ReadBytes
        self.HCVMDMA_ReadBytes.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32]
        self.HCVMDMA_ReadBytes.restype = ctypes.c_int64
        
        # 内存写入
        self.HCVMDMA_Write = self.dll.HCVMDMA_Write
        self.HCVMDMA_Write.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.HCVMDMA_Write.restype = ctypes.c_int64
        
        self.HCVMDMA_WriteFloat = self.dll.HCVMDMA_WriteFloat
        self.HCVMDMA_WriteFloat.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_float, ctypes.c_int64]
        self.HCVMDMA_WriteFloat.restype = ctypes.c_int64
        
        self.HCVMDMA_WriteDouble = self.dll.HCVMDMA_WriteDouble
        self.HCVMDMA_WriteDouble.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double, ctypes.c_int64]
        self.HCVMDMA_WriteDouble.restype = ctypes.c_int64
        
        self.HCVMDMA_WriteBytes = self.dll.HCVMDMA_WriteBytes
        self.HCVMDMA_WriteBytes.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32]
        self.HCVMDMA_WriteBytes.restype = ctypes.c_int64
        
        # 四、进程与模块信息
        self.HCVMDMA_GetPid = self.dll.HCVMDMA_GetPid
        self.HCVMDMA_GetPid.argtypes = [ctypes.c_int32, ctypes.c_char_p]
        self.HCVMDMA_GetPid.restype = ctypes.c_int64
        
        self.HCVMDMA_GetBaseModule = self.dll.HCVMDMA_GetBaseModule
        self.HCVMDMA_GetBaseModule.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.HCVMDMA_GetBaseModule.restype = ctypes.c_int64
        
        self.HCVMDMA_GetModule = self.dll.HCVMDMA_GetModule
        self.HCVMDMA_GetModule.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
        self.HCVMDMA_GetModule.restype = ctypes.c_int64
        
        self.HCVMDMA_GetProcAddr = self.dll.HCVMDMA_GetProcAddr
        self.HCVMDMA_GetProcAddr.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p]
        self.HCVMDMA_GetProcAddr.restype = ctypes.c_int64
        
        # 五、ShellCode执行
        # 执行环境初始化
        self.HCVMDMA_ShellCodeInitX64 = self.dll.HCVMDMA_ShellCodeInitX64
        self.HCVMDMA_ShellCodeInitX64.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCVMDMA_ShellCodeInitX64.restype = ctypes.c_int64
        
        self.HCVMDMA_ShellCodeInitX86 = self.dll.HCVMDMA_ShellCodeInitX86
        self.HCVMDMA_ShellCodeInitX86.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.HCVMDMA_ShellCodeInitX86.restype = ctypes.c_int64
        
        # 运行ShellCode
        self.HCVMDMA_RunShellCodeX64 = self.dll.HCVMDMA_RunShellCodeX64
        self.HCVMDMA_RunShellCodeX64.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p]
        self.HCVMDMA_RunShellCodeX64.restype = ctypes.c_int64
        
        self.HCVMDMA_RunShellCodeX86 = self.dll.HCVMDMA_RunShellCodeX86
        self.HCVMDMA_RunShellCodeX86.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
        self.HCVMDMA_RunShellCodeX86.restype = ctypes.c_int64
        
        # 六、特征码搜索
        # x86架构
        self.HCVMDMA_FindCodeX86 = self.dll.HCVMDMA_FindCodeX86
        self.HCVMDMA_FindCodeX86.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
        self.HCVMDMA_FindCodeX86.restype = ctypes.c_int64
        
        self.HCVMDMA_FindCodeX86Ex = self.dll.HCVMDMA_FindCodeX86Ex
        self.HCVMDMA_FindCodeX86Ex.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.HCVMDMA_FindCodeX86Ex.restype = ctypes.c_int64
        
        # x64架构
        self.HCVMDMA_FindCodeX64 = self.dll.HCVMDMA_FindCodeX64
        self.HCVMDMA_FindCodeX64.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
        self.HCVMDMA_FindCodeX64.restype = ctypes.c_int64
        
        self.HCVMDMA_FindCodeX64Ex = self.dll.HCVMDMA_FindCodeX64Ex
        self.HCVMDMA_FindCodeX64Ex.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.HCVMDMA_FindCodeX64Ex.restype = ctypes.c_int64
        
        # 七、截图功能
        self.HCVMDMA_InitCapture = self.dll.HCVMDMA_InitCapture
        self.HCVMDMA_InitCapture.argtypes = [ctypes.c_int32]
        self.HCVMDMA_InitCapture.restype = ctypes.c_int64
        
        self.HCVMDMA_Capture = self.dll.HCVMDMA_Capture
        self.HCVMDMA_Capture.argtypes = [ctypes.c_int32, ctypes.c_int64]
        self.HCVMDMA_Capture.restype = ctypes.c_int64
        
        self.HCVMDMA_OpenCapture = self.dll.HCVMDMA_OpenCapture
        self.HCVMDMA_OpenCapture.argtypes = [ctypes.c_int32, ctypes.c_int64]
        self.HCVMDMA_OpenCapture.restype = ctypes.c_int64
        
        self.HCVMDMA_CloseCapture = self.dll.HCVMDMA_CloseCapture
        self.HCVMDMA_CloseCapture.argtypes = [ctypes.c_int32]
        self.HCVMDMA_CloseCapture.restype = ctypes.c_int64
        
        # 八、键鼠控制
        # 环境初始化
        self.HCVMDMA_InitMouseKey = self.dll.HCVMDMA_InitMouseKey
        self.HCVMDMA_InitMouseKey.argtypes = [ctypes.c_int32]
        self.HCVMDMA_InitMouseKey.restype = ctypes.c_int64
        
        # 鼠标操作
        self.HCVMDMA_MoveTo = self.dll.HCVMDMA_MoveTo
        self.HCVMDMA_MoveTo.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]
        self.HCVMDMA_MoveTo.restype = ctypes.c_int64
        
        # 点击/双击函数
        self.HCVMDMA_LeftDown = self.dll.HCVMDMA_LeftDown
        self.HCVMDMA_LeftDown.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCVMDMA_LeftDown.restype = ctypes.c_int64
        
        self.HCVMDMA_LeftUp = self.dll.HCVMDMA_LeftUp
        self.HCVMDMA_LeftUp.argtypes = [ctypes.c_int32, ctypes.c_int64]
        self.HCVMDMA_LeftUp.restype = ctypes.c_int64
        
        self.HCVMDMA_LeftClick = self.dll.HCVMDMA_LeftClick
        self.HCVMDMA_LeftClick.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCVMDMA_LeftClick.restype = ctypes.c_int64
        
        self.HCVMDMA_LeftDoubleClick = self.dll.HCVMDMA_LeftDoubleClick
        self.HCVMDMA_LeftDoubleClick.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCVMDMA_LeftDoubleClick.restype = ctypes.c_int64
        
        # 中键和右键操作类似，省略部分函数声明
        self.HCVMDMA_MiddleDown = self.dll.HCVMDMA_MiddleDown
        self.HCVMDMA_MiddleDown.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCVMDMA_MiddleDown.restype = ctypes.c_int64
        
        self.HCVMDMA_RightDown = self.dll.HCVMDMA_RightDown
        self.HCVMDMA_RightDown.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCVMDMA_RightDown.restype = ctypes.c_int64
        
        # 键盘操作
        self.HCVMDMA_KeyDown = self.dll.HCVMDMA_KeyDown
        self.HCVMDMA_KeyDown.argtypes = [ctypes.c_int32, ctypes.c_int, ctypes.c_int64]
        self.HCVMDMA_KeyDown.restype = ctypes.c_int64
        
        self.HCVMDMA_KeyUp = self.dll.HCVMDMA_KeyUp
        self.HCVMDMA_KeyUp.argtypes = [ctypes.c_int32, ctypes.c_int, ctypes.c_int64]
        self.HCVMDMA_KeyUp.restype = ctypes.c_int64
        
        self.HCVMDMA_KeyClick = self.dll.HCVMDMA_KeyClick
        self.HCVMDMA_KeyClick.argtypes = [ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_int64]
        self.HCVMDMA_KeyClick.restype = ctypes.c_int64
        
        # 字符串发送
        self.HCVMDMA_SendUnicode = self.dll.HCVMDMA_SendUnicode
        self.HCVMDMA_SendUnicode.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_int64]
        self.HCVMDMA_SendUnicode.restype = ctypes.c_int64
        
        self.HCVMDMA_SendAscii = self.dll.HCVMDMA_SendAscii
        self.HCVMDMA_SendAscii.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int64]
        self.HCVMDMA_SendAscii.restype = ctypes.c_int64
        
        # 九、进程列表管理
        self.HCVMDMA_GetPidList = self.dll.HCVMDMA_GetPidList
        self.HCVMDMA_GetPidList.argtypes = [ctypes.c_int32]
        self.HCVMDMA_GetPidList.restype = ctypes.c_int64
        
        self.HCVMDMA_IsExistPid = self.dll.HCVMDMA_IsExistPid
        self.HCVMDMA_IsExistPid.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.HCVMDMA_IsExistPid.restype = ctypes.c_int64
        
        # 十、定制游戏接口（剑灵2台服）
        # 人物与状态信息
        self.HB2_GetPlayerInfo = self.dll.HB2_GetPlayerInfo
        self.HB2_GetPlayerInfo.argtypes = [ctypes.c_int32]
        self.HB2_GetPlayerInfo.restype = ctypes.c_int64
        
        self.HB2_GetPlayerXYZ = self.dll.HB2_GetPlayerXYZ
        self.HB2_GetPlayerXYZ.argtypes = [ctypes.c_int32]
        self.HB2_GetPlayerXYZ.restype = ctypes.c_int64
        
        # 省略部分游戏定制接口
    
    # 以下是Python友好的API封装
    def get_version(self, windows_index: int) -> int:
        """
        获取DMA服务器版本号
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            int: 版本号（格式：240401 表示24年04版本01小版本）
        """
        return self.HCVMDMA_GetVersion(windows_index)
    
    def is_version_match(self, windows_index: int) -> bool:
        """
        检查HD插件与DMA服务器的版本是否一致
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            bool: True表示版本一致，False表示不一致
        """
        return bool(self.HCVMDMA_IsVersion(windows_index))
    
    def start_server(self, ip: str = VMDMA_DEFAULT_IP, port: int = VMDMA_DEFAULT_PORT, 
                    server_root_path: str = "") -> int:
        """
        启动DMA服务器
        
        Args:
            ip (str): 服务器IP（默认127.0.0.1）
            port (int): 端口（默认6532）
            server_root_path (str): 服务器根目录（默认中控exe目录）
        
        Returns:
            int: 操作结果（参考HD返回值表）
        """
        # 转换参数为C类型
        c_ip = ip.encode('utf-8')
        c_server_root_path = server_root_path.encode('utf-8')
        return self.HCVMDMA_StartServer(c_ip, port, c_server_root_path)
    
    def close_server(self) -> int:
        """
        关闭DMA服务器并结束进程
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_CloseServer()
    
    def is_server_started(self, ip: str = VMDMA_DEFAULT_IP, port: int = VMDMA_DEFAULT_PORT) -> bool:
        """
        检查服务器是否已启动
        
        Args:
            ip (str): 服务器IP
            port (int): 端口
        
        Returns:
            bool: True表示已启动，False表示未启动
        """
        c_ip = ip.encode('utf-8')
        return bool(self.HCVMDMA_ServerIsStart(c_ip, port))
    
    def init_vm(self, windows_index: int, vm_pid: int, time_out: int = 10000) -> int:
        """
        初始化并关联虚拟机（需先启动服务器）
        
        Args:
            windows_index (int): 窗口序号
            vm_pid (int): 虚拟机PID（进程名vmware-vmx.exe，0表示重连已关联的虚拟机）
            time_out (int): 超时时间（毫秒）
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_Init(windows_index, vm_pid, time_out)
    
    def close_vm(self, windows_index: int) -> int:
        """
        卸载并关闭虚拟机连接
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_Close(windows_index)
    
    def read_memory(self, windows_index: int, target_pid: int, addr: int, addr_size: int) -> int:
        """
        读取虚拟机内进程的内存（支持1/2/4/8字节）
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            addr (int): 内存地址
            addr_size (int): 读取大小（1/2/4/8）
        
        Returns:
            int: 读取的内存值
        """
        return self.HCVMDMA_Read(windows_index, target_pid, addr, addr_size)
    
    def read_float(self, windows_index: int, target_pid: int, addr: int) -> float:
        """
        读取单浮点数
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            addr (int): 内存地址
        
        Returns:
            float: 读取的浮点数
        """
        return self.HCVMDMA_ReadFloat(windows_index, target_pid, addr)
    
    def read_double(self, windows_index: int, target_pid: int, addr: int) -> float:
        """
        读取双浮点数
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            addr (int): 内存地址
        
        Returns:
            float: 读取的双精度浮点数
        """
        return self.HCVMDMA_ReadDouble(windows_index, target_pid, addr)
    
    def read_bytes(self, windows_index: int, target_pid: int, addr: int, read_size: int) -> bytes:
        """
        读取字节集（最大1024字节）
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            addr (int): 内存地址
            read_size (int): 读取大小
        
        Returns:
            bytes: 读取的字节集
        """
        if read_size > VMDMA_MAX_BYTE_SIZE:
            raise ValueError(f"读取大小不能超过{VMDMA_MAX_BYTE_SIZE}字节")
        
        # 创建缓冲区
        buffer = (ctypes.c_ubyte * read_size)()
        result = self.HCVMDMA_ReadBytes(windows_index, target_pid, addr, buffer, read_size)
        
        if result != 0:
            # 读取成功，返回缓冲区内容
            return bytes(buffer)
        else:
            # 读取失败
            return bytes()
    
    def write_memory(self, windows_index: int, target_pid: int, value: int, addr: int, addr_size: int) -> int:
        """
        写入内存（支持1/2/4/8字节）
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            value (int): 要写入的值
            addr (int): 内存地址
            addr_size (int): 写入大小（1/2/4/8）
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_Write(windows_index, target_pid, value, addr, addr_size)
    
    def write_float(self, windows_index: int, target_pid: int, value: float, addr: int) -> int:
        """
        写入单浮点数
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            value (float): 要写入的浮点数
            addr (int): 内存地址
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_WriteFloat(windows_index, target_pid, value, addr)
    
    def write_double(self, windows_index: int, target_pid: int, value: float, addr: int) -> int:
        """
        写入双浮点数
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            value (float): 要写入的双精度浮点数
            addr (int): 内存地址
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_WriteDouble(windows_index, target_pid, value, addr)
    
    def write_bytes(self, windows_index: int, target_pid: int, addr: int, buffer: bytes) -> int:
        """
        写入字节集（最大1024字节）
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            addr (int): 内存地址
            buffer (bytes): 要写入的字节集
        
        Returns:
            int: 操作结果
        """
        write_size = len(buffer)
        if write_size > VMDMA_MAX_BYTE_SIZE:
            raise ValueError(f"写入大小不能超过{VMDMA_MAX_BYTE_SIZE}字节")
        
        # 转换bytes为C数组
        c_buffer = (ctypes.c_ubyte * write_size).from_buffer_copy(buffer)
        return self.HCVMDMA_WriteBytes(windows_index, target_pid, addr, c_buffer, write_size)
    
    def get_pid(self, windows_index: int, process_name: str) -> int:
        """
        通过进程名获取虚拟机内进程PID
        
        Args:
            windows_index (int): 窗口序号
            process_name (str): 进程名
        
        Returns:
            int: 进程PID
        """
        c_process_name = process_name.encode('utf-8')
        return self.HCVMDMA_GetPid(windows_index, c_process_name)
    
    def get_base_module(self, windows_index: int, target_pid: int) -> int:
        """
        获取主模块的基地址
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
        
        Returns:
            int: 模块基地址
        """
        return self.HCVMDMA_GetBaseModule(windows_index, target_pid)
    
    def get_module(self, windows_index: int, target_pid: int, module_name: str) -> int:
        """
        获取指定模块的基地址
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            module_name (str): 模块名
        
        Returns:
            int: 模块基地址
        """
        c_module_name = module_name.encode('utf-8')
        return self.HCVMDMA_GetModule(windows_index, target_pid, c_module_name)
    
    def get_proc_addr(self, windows_index: int, target_pid: int, module_name: str, proc_name: str) -> int:
        """
        获取模块内函数地址
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            module_name (str): 模块名
            proc_name (str): 函数名
        
        Returns:
            int: 函数地址
        """
        c_module_name = module_name.encode('utf-8')
        c_proc_name = proc_name.encode('utf-8')
        return self.HCVMDMA_GetProcAddr(windows_index, target_pid, c_module_name, c_proc_name)
    
    def init_shellcode_x64(self, windows_index: int, target_pid: int, hook_addr: int, hook_addr_size: int) -> int:
        """
        初始化x64进程的ShellCode执行环境
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            hook_addr (int): Hook地址（如频繁调用的函数）
            hook_addr_size (int): 破坏的汇编字节数（x64需8字节）
        
        Returns:
            int: 执行环境句柄（8字节）
        """
        return self.HCVMDMA_ShellCodeInitX64(windows_index, target_pid, hook_addr, hook_addr_size)
    
    def run_shellcode_x64(self, windows_index: int, target_pid: int, execute_env_addr: int, shellcode_str: str) -> int:
        """
        通过执行环境句柄运行ShellCode (x64)
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            execute_env_addr (int): 执行环境句柄（0表示使用内置保存的句柄）
            shellcode_str (str): 汇编机器码字符串
        
        Returns:
            int: 操作结果
        """
        c_shellcode = shellcode_str.encode('utf-8')
        return self.HCVMDMA_RunShellCodeX64(windows_index, target_pid, execute_env_addr, c_shellcode)
    
    def find_code_x86(self, windows_index: int, target_pid: int, code: str, offset: int, 
                     num: int, type: int = 1, module_name: Optional[str] = None) -> int:
        """
        在指定模块/地址范围搜索特征码（x86）
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            code (str): 特征码
            offset (int): 偏移量
            num (int): 序号
            type (int): 类型（默认为1）
            module_name (str, optional): 模块名
        
        Returns:
            int: 找到的地址
        """
        c_code = code.encode('utf-8')
        c_module_name = module_name.encode('utf-8') if module_name else None
        return self.HCVMDMA_FindCodeX86(windows_index, target_pid, c_code, offset, num, type, c_module_name)
    
    def find_code_x64(self, windows_index: int, target_pid: int, code: str, offset: int, 
                     num: int, type: int = 1, module_name: Optional[str] = None) -> int:
        """
        在指定模块/地址范围搜索特征码（x64）
        
        Args:
            windows_index (int): 窗口序号
            target_pid (int): 虚拟机内目标进程PID
            code (str): 特征码
            offset (int): 偏移量
            num (int): 序号
            type (int): 类型（默认为1）
            module_name (str, optional): 模块名
        
        Returns:
            int: 找到的地址
        """
        c_code = code.encode('utf-8')
        c_module_name = module_name.encode('utf-8') if module_name else None
        return self.HCVMDMA_FindCodeX64(windows_index, target_pid, c_code, offset, num, type, c_module_name)
    
    def init_capture(self, windows_index: int) -> int:
        """
        初始化截图环境
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            int: 截图句柄（一个虚拟机唯一）
        """
        return self.HCVMDMA_InitCapture(windows_index)
    
    def capture(self, windows_index: int, capture_env_addr: int = 0) -> int:
        """
        单次截图（获取虚拟机全屏数据）
        
        Args:
            windows_index (int): 窗口序号
            capture_env_addr (int): 截图句柄，0表示使用内置句柄
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_Capture(windows_index, capture_env_addr)
    
    def open_capture(self, windows_index: int, capture_env_addr: int) -> int:
        """
        开启循环截图（内部线程循环调用HCVMDMA_Capture）
        
        Args:
            windows_index (int): 窗口序号
            capture_env_addr (int): 截图句柄
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_OpenCapture(windows_index, capture_env_addr)
    
    def close_capture(self, windows_index: int) -> int:
        """
        关闭循环截图
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_CloseCapture(windows_index)
    
    def init_mouse_key(self, windows_index: int) -> int:
        """
        初始化键鼠环境
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            int: 键鼠句柄（一个虚拟机唯一）
        """
        return self.HCVMDMA_InitMouseKey(windows_index)
    
    def move_to(self, windows_index: int, x: int, y: int, mkb_env_addr: int) -> int:
        """
        鼠标移动（无轨迹）
        
        Args:
            windows_index (int): 窗口序号
            x (int): 目标X坐标
            y (int): 目标Y坐标
            mkb_env_addr (int): 键鼠句柄
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_MoveTo(windows_index, x, y, mkb_env_addr)
    
    def left_click(self, windows_index: int, mkb_env_addr: int, mis: int = 50) -> int:
        """
        鼠标左键单击
        
        Args:
            windows_index (int): 窗口序号
            mkb_env_addr (int): 键鼠句柄
            mis (int): 点击间隔毫秒
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_LeftClick(windows_index, mkb_env_addr, mis)
    
    def key_click(self, windows_index: int, key_code: int, mis: int, mkb_env_addr: int) -> int:
        """
        键盘敲击
        
        Args:
            windows_index (int): 窗口序号
            key_code (int): 按键代码
            mis (int): 按键间隔毫秒
            mkb_env_addr (int): 键鼠句柄
        
        Returns:
            int: 操作结果
        """
        return self.HCVMDMA_KeyClick(windows_index, key_code, mis, mkb_env_addr)
    
    def send_unicode(self, windows_index: int, text: str, mkb_env_addr: int) -> int:
        """
        发送Unicode字符串（最大100字符）
        
        Args:
            windows_index (int): 窗口序号
            text (str): 要发送的Unicode文本
            mkb_env_addr (int): 键鼠句柄
        
        Returns:
            int: 操作结果
        """
        if len(text) > VMDMA_MAX_UNICODE_LENGTH:
            raise ValueError(f"Unicode文本长度不能超过{VMDMA_MAX_UNICODE_LENGTH}字符")
        
        # 使用wchar_p处理Unicode字符串
        return self.HCVMDMA_SendUnicode(windows_index, text, mkb_env_addr)
    
    def send_ascii(self, windows_index: int, text: str, mkb_env_addr: int) -> int:
        """
        发送ASCII字符串（最大200字符）
        
        Args:
            windows_index (int): 窗口序号
            text (str): 要发送的ASCII文本
            mkb_env_addr (int): 键鼠句柄
        
        Returns:
            int: 操作结果
        """
        if len(text) > VMDMA_MAX_ASCII_LENGTH:
            raise ValueError(f"ASCII文本长度不能超过{VMDMA_MAX_ASCII_LENGTH}字符")
        
        c_text = text.encode('utf-8')
        return self.HCVMDMA_SendAscii(windows_index, c_text, mkb_env_addr)
    
    def get_pid_list(self, windows_index: int) -> List[Tuple[int, str]]:
        """
        获取虚拟机内进程PID列表
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            List[Tuple[int, str]]: 进程列表，每个元素为(pid, name)元组
        """
        result = self.HCVMDMA_GetPidList(windows_index)
        # 假设返回的是JSON格式的字符串地址，这里简化处理
        # 实际使用时需要根据具体实现解析结果
        # 这里返回空列表，实际实现时需要根据DLL返回值解析
        return []
    
    def is_exist_pid(self, windows_index: int, pid: int) -> bool:
        """
        检查虚拟机内进程是否存在
        
        Args:
            windows_index (int): 窗口序号
            pid (int): 进程PID
        
        Returns:
            bool: True表示存在，False表示不存在
        """
        return bool(self.HCVMDMA_IsExistPid(windows_index, pid))
    
    # 游戏定制接口
    def get_player_info(self, windows_index: int) -> dict:
        """
        获取剑灵2台服人物信息（姓名、等级、HP/MP、金币等）
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            dict: 人物信息字典
        """
        result = self.HB2_GetPlayerInfo(windows_index)
        # 实际使用时需要根据返回值解析具体信息
        # 这里返回空字典，实际实现时需要根据DLL返回值解析
        return {}
    
    def get_player_xyz(self, windows_index: int) -> Tuple[float, float, float]:
        """
        获取剑灵2台服人物坐标（x,y,z）
        
        Args:
            windows_index (int): 窗口序号
        
        Returns:
            Tuple[float, float, float]: 人物坐标(x, y, z)
        """
        result = self.HB2_GetPlayerXYZ(windows_index)
        # 实际使用时需要根据返回值解析坐标信息
        # 这里返回默认值，实际实现时需要根据DLL返回值解析
        return (0.0, 0.0, 0.0)


# 工厂函数
def create_hd_vmdma(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HDVMDMA:
    """
    创建VMDMA模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版本的DLL
    
    Returns:
        HDVMDMA: VMDMA模块实例
    """
    from .base_module import HDModuleFactory
    return HDModuleFactory.create_instance(HDVMDMA, dll_path, is_debug)


# 模块版本信息
__version__ = "1.0.0"


# 如果直接运行此脚本，提供一个简单的演示
if __name__ == "__main__":
    try:
        # 创建VMDMA模块实例
        vmdma = create_hd_vmdma()
        print("VMDMA模块初始化成功")
        
        # 此处可以添加演示代码
        print("VMDMA模块演示完成")
    except Exception as e:
        print(f"VMDMA模块演示失败: {str(e)}")