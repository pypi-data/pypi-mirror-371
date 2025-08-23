# HD RPG引擎框架(GDK)注入模块(Normal)的Python封装
# 本模块用于学习交流完全合规

import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase, HDModuleFactory

class HDNormal(HDModuleBase):
    """
    HD注入模块
    提供多种插件及DLL注入功能，涵盖普通注入（无需驱动）和驱动级别注入，
    支持X86和X64架构，适用于不同场景下的进程注入需求。
    """
    def __init__(self, dll_path=None, is_debug=False):
        """
        初始化HDNormal模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
        # 存储回调函数引用，防止被Python垃圾回收器回收
        self._callbacks = {}
    
    def _initialize_functions(self):
        """初始化DLL中的函数"""
        # 普通注入（无需驱动）
        self.HCN_NormalInstallPlugX86 = self.dll.HCN_NormalInstallPlugX86
        self.HCN_NormalInstallPlugX86.argtypes = [ctypes.c_int32]
        self.HCN_NormalInstallPlugX86.restype = ctypes.c_int64
        
        self.HCN_NormalInstallPlugX86Ex = self.dll.HCN_NormalInstallPlugX86Ex
        self.HCN_NormalInstallPlugX86Ex.argtypes = [ctypes.c_int64]
        self.HCN_NormalInstallPlugX86Ex.restype = ctypes.c_int64
        
        self.HCN_NormalInstallPlugX64 = self.dll.HCN_NormalInstallPlugX64
        self.HCN_NormalInstallPlugX64.argtypes = [ctypes.c_int32]
        self.HCN_NormalInstallPlugX64.restype = ctypes.c_int64
        
        self.HCN_NormalInstallPlugX64Ex = self.dll.HCN_NormalInstallPlugX64Ex
        self.HCN_NormalInstallPlugX64Ex.argtypes = [ctypes.c_int64]
        self.HCN_NormalInstallPlugX64Ex.restype = ctypes.c_int64
        
        # 驱动级别注入（需预先安装HD驱动）
        self.HCHD_NormalInstallPlugX86X64 = self.dll.HCHD_NormalInstallPlugX86X64
        self.HCHD_NormalInstallPlugX86X64.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.HCHD_NormalInstallPlugX86X64.restype = ctypes.c_int64
        
        self.HCHD_NormalInjectX86X64ByFile = self.dll.HCHD_NormalInjectX86X64ByFile
        self.HCHD_NormalInjectX86X64ByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.HCHD_NormalInjectX86X64ByFile.restype = ctypes.c_int64
        
        self.HCHD_NormalInstallPlugX86X64Ex = self.dll.HCHD_NormalInstallPlugX86X64Ex
        self.HCHD_NormalInstallPlugX86X64Ex.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.HCHD_NormalInstallPlugX86X64Ex.restype = ctypes.c_int64
        
        self.HCHD_NormalInjectX86X64ByFileEx = self.dll.HCHD_NormalInjectX86X64ByFileEx
        self.HCHD_NormalInjectX86X64ByFileEx.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.HCHD_NormalInjectX86X64ByFileEx.restype = ctypes.c_int64
    
    # 普通注入（无需驱动）方法
    def normal_install_plug_x86(self, pid):
        """
        普通注入插件（X86），无需安装驱动，非无痕注入，仅支持32位进程
        
        Args:
            pid (int): 进程PID
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        return self.HCN_NormalInstallPlugX86(pid)
    
    def normal_install_plug_x86_ex(self, hwnd):
        """
        普通注入插件（X86），无需驱动，非无痕注入，通过窗口句柄指定目标
        
        Args:
            hwnd (int): 进程窗口句柄
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        return self.HCN_NormalInstallPlugX86Ex(hwnd)
    
    def normal_install_plug_x64(self, pid):
        """
        普通注入插件（X64），无需安装驱动，非无痕注入，仅支持64位进程
        
        Args:
            pid (int): 进程PID
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        return self.HCN_NormalInstallPlugX64(pid)
    
    def normal_install_plug_x64_ex(self, hwnd):
        """
        普通注入插件（X64），无需驱动，非无痕注入，通过窗口句柄指定目标
        
        Args:
            hwnd (int): 进程窗口句柄
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        return self.HCN_NormalInstallPlugX64Ex(hwnd)
    
    # 驱动级别注入（需预先安装HD驱动）方法
    def normal_install_plug_x86x64(self, pid, dll_bits, b_wait=True):
        """
        安装HD插件（注入方式1），需驱动，支持X86/X64
        
        Args:
            pid (int): 进程PID
            dll_bits (int): 进程位数（32/64）
            b_wait (bool, optional): 暂无效，可忽略
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        return self.HCHD_NormalInstallPlugX86X64(pid, dll_bits, b_wait)
    
    def normal_inject_x86x64_by_file(self, pid, dll_path, b_wait=True):
        """
        安装指定DLL（注入方式1），需驱动，支持X86/X64
        
        Args:
            pid (int): 进程PID
            dll_path (str): 需加载的DLL全路径
            b_wait (bool, optional): 暂无效，可忽略
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        # 将字符串转换为C类型的字符指针
        dll_path_bytes = dll_path.encode('utf-8')
        return self.HCHD_NormalInjectX86X64ByFile(pid, dll_path_bytes, b_wait)
    
    def normal_install_plug_x86x64_ex(self, pid, dll_bits, b_wait=True):
        """
        安装HD插件（注入方式2），需驱动，支持X86/X64
        
        Args:
            pid (int): 进程PID
            dll_bits (int): 进程位数（32/64）
            b_wait (bool, optional): 暂无效，可忽略
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        return self.HCHD_NormalInstallPlugX86X64Ex(pid, dll_bits, b_wait)
    
    def normal_inject_x86x64_by_file_ex(self, pid, dll_path, b_wait=True):
        """
        安装指定DLL（注入方式2），需驱动，支持X86/X64
        
        Args:
            pid (int): 进程PID
            dll_path (str): 需加载的DLL全路径
            b_wait (bool, optional): 暂无效，可忽略
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        # 将字符串转换为C类型的字符指针
        dll_path_bytes = dll_path.encode('utf-8')
        return self.HCHD_NormalInjectX86X64ByFileEx(pid, dll_path_bytes, b_wait)

# 工厂函数
def create_normal(dll_path=None, is_debug=False):
    """
    创建HDNormal实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HDNormal: 创建的Normal模块实例
    """
    return HDModuleFactory.create_instance(HDNormal, dll_path, is_debug)