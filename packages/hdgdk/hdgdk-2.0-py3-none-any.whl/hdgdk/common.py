import ctypes
import os

# 导入基础模块
from .base_module import HDModuleBase

class HDCommon(HDModuleBase):
    """
    HD通用模块
    提供所有模块共用的通用功能
    """
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 初始化获取最近错误函数
        self.dll.HCEnv_GetLastError.argtypes = []
        self.dll.HCEnv_GetLastError.restype = ctypes.c_int64
        
        # 初始化通用CALL函数（X64）
        self.dll.HC_CALL.argtypes = [
            ctypes.c_int32,  # 窗口序号
            ctypes.c_int64,  # CALL地址
            ctypes.c_int64,  # rcx
            ctypes.c_int64,  # rdx
            ctypes.c_int64,  # r8
            ctypes.c_int64,  # r9
            ctypes.c_int64,  # lparam5
            ctypes.c_int64,  # lparam6
            ctypes.c_int64,  # lparam7
            ctypes.c_int64,  # lparam8
            ctypes.c_bool    # 是否主线程调用
        ]
        self.dll.HC_CALL.restype = ctypes.c_int64
        
        # 初始化通用CALL函数（X86）
        self.dll.HC_CALLX86.argtypes = [
            ctypes.c_int32,  # 窗口序号
            ctypes.c_int32,  # CALL地址
            ctypes.c_int32,  # ecx
            ctypes.c_int32,  # lparam1
            ctypes.c_int32,  # lparam2
            ctypes.c_int32,  # lparam3
            ctypes.c_int32,  # lparam4
            ctypes.c_int32,  # lparam5
            ctypes.c_int32,  # lparam6
            ctypes.c_int32,  # lparam7
            ctypes.c_int32,  # lparam8
            ctypes.c_int32,  # lparamNum
            ctypes.c_int32,  # addEsp
            ctypes.c_bool    # 是否主线程调用
        ]
        self.dll.HC_CALLX86.restype = ctypes.c_int64
        
        # 初始化主线程挂接函数
        self.dll.HC_HookMainThread.argtypes = [
            ctypes.c_int32,  # 窗口序号
            ctypes.c_int64   # 窗口句柄
        ]
        self.dll.HC_HookMainThread.restype = ctypes.c_int64
    
    def get_last_error(self):
        """
        获取最近一次调用WIN32 API的错误值
        :return: 错误值（查看返回值表HD返回值表）
        """
        return self.dll.HCEnv_GetLastError()
    
    def call(self, windows_index, call_address, rcx=0, rdx=0, r8=0, r9=0, lparam5=0, lparam6=0, lparam7=0, lparam8=0, is_main_thread=False):
        """
        通用CALL（适合X64），支持0-8个参数
        :param windows_index: 窗口序号（从1开始）
        :param call_address: 调用的地址
        :param rcx: 第一个参数
        :param rdx: 第二个参数
        :param r8: 第三个参数
        :param r9: 第四个参数
        :param lparam5: 第五个参数
        :param lparam6: 第六个参数
        :param lparam7: 第七个参数
        :param lparam8: 第八个参数
        :param is_main_thread: 是否在主线程调用（需挂接主线程）
        :return: 调用结果（查看返回值表HD返回值表）
        """
        return self.dll.HC_CALL(
            windows_index,
            call_address,
            rcx,
            rdx,
            r8,
            r9,
            lparam5,
            lparam6,
            lparam7,
            lparam8,
            is_main_thread
        )
    
    def call_x86(self, windows_index, call_address, ecx=0, lparam1=0, lparam2=0, lparam3=0, lparam4=0, lparam5=0, lparam6=0, lparam7=0, lparam8=0, lparam_num=0, add_esp=-1, is_main_thread=False):
        """
        通用CALL（适合X86），支持0-8个参数
        :param windows_index: 窗口序号（从1开始）
        :param call_address: 4字节接口地址
        :param ecx: 对象参数
        :param lparam1: 第一个参数
        :param lparam2: 第二个参数
        :param lparam3: 第三个参数
        :param lparam4: 第四个参数
        :param lparam5: 第五个参数
        :param lparam6: 第六个参数
        :param lparam7: 第七个参数
        :param lparam8: 第八个参数
        :param lparam_num: 传递的参数数量（0-8个）
        :param add_esp: 内平栈置为-1，外平栈设置为参数数量（lparam_num）*0x4
        :param is_main_thread: 是否在主线程调用（需挂接主线程）
        :return: 调用结果（查看返回值表HD返回值表）
        """
        return self.dll.HC_CALLX86(
            windows_index,
            call_address,
            ecx,
            lparam1,
            lparam2,
            lparam3,
            lparam4,
            lparam5,
            lparam6,
            lparam7,
            lparam8,
            lparam_num,
            add_esp,
            is_main_thread
        )
    
    def hook_main_thread(self, windows_index, window_handle):
        """
        挂接主线程
        :param windows_index: 窗口序号（从1开始）
        :param window_handle: 窗口句柄
        :return: 操作结果（查看返回值表HD返回值表）
        """
        return self.dll.HC_HookMainThread(windows_index, window_handle)


# 工厂函数
def create_hd_common(dll_path=None, is_debug=None):
    """
    创建HDCommon实例
    :param dll_path: DLL文件所在路径（可选，如果DLL已加载）
    :param is_debug: 是否使用调试版DLL（可选，如果DLL已加载）
    :return: HDCommon实例
    """
    return HDCommon(dll_path, is_debug)