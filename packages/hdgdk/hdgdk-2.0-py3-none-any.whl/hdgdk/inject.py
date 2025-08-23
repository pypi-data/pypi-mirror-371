import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase

class HDInject(HDModuleBase):
    """
    HD注入模块
    负责处理DLL注入相关的功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化HDInject实例
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
    
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 设置函数参数类型和返回值类型
        self.dll.HCInject_Init.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.dll.HCInject_Init.restype = ctypes.c_int64
        
        self.dll.HCInject_InitEx.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCInject_InitEx.restype = ctypes.c_int64
        
        self.dll.HCInject_InitExx.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool]
        self.dll.HCInject_InitExx.restype = ctypes.c_int64
        
        self.dll.HCInject_GetPid.argtypes = [ctypes.c_int32]
        self.dll.HCInject_GetPid.restype = ctypes.c_int64
        
        self.dll.HCInject_GetPrePid.argtypes = [ctypes.c_int32]
        self.dll.HCInject_GetPrePid.restype = ctypes.c_int64
        
        self.dll.HCInject_GetPreWinIndex.argtypes = [ctypes.c_int32]
        self.dll.HCInject_GetPreWinIndex.restype = ctypes.c_int64
        
        self.dll.HCInject_GetPreWinIndexEx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p]
        self.dll.HCInject_GetPreWinIndexEx.restype = ctypes.c_int64
        
        self.dll.HCInject_GetHwnd.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.c_int32]
        self.dll.HCInject_GetHwnd.restype = ctypes.c_int64
        
        self.dll.HCInject_GetHwndEx.argtypes = [ctypes.c_int32]
        self.dll.HCInject_GetHwndEx.restype = ctypes.c_int64
        
        self.dll.HCInject_Continue.argtypes = [ctypes.c_int32]
        self.dll.HCInject_Continue.restype = ctypes.c_int64
        
        self.dll.HCInject_SetData.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
        self.dll.HCInject_SetData.restype = ctypes.c_int64
        
        self.dll.HCInject_GetData.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
        self.dll.HCInject_GetData.restype = ctypes.c_int64
    
    def init(self, win_index, is_reset=True):
        """
        初始化插件环境
        :param win_index: 窗口序号（从1开始）
        :param is_reset: 是否重置
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCInject_Init(win_index, is_reset)
    
    def init_ex(self, win_index, lua_path=None, is_reset=True):
        """
        初始化插件环境（支持预加载LUA模块）
        :param win_index: 窗口序号（从1开始）
        :param lua_path: 预加载LUA模块全路径
        :param is_reset: 是否重置
        :return: 操作结果（参考HD返回值表）
        """
        if lua_path is not None:
            lua_path_encoded = lua_path.encode('utf-8') if isinstance(lua_path, str) else lua_path
        else:
            lua_path_encoded = None
        return self.dll.HCInject_InitEx(win_index, lua_path_encoded, is_reset)
    
    def init_exx(self, win_index, dll_path=None, lua_path=None, add_type=-1, is_reset=True):
        """
        初始化插件环境（支持预加载DLL和LUA模块）
        :param win_index: 窗口序号（从1开始）
        :param dll_path: 预加载DLL模块全路径
        :param lua_path: 预加载LUA模块全路径
        :param add_type: DLL加载方式（-1/0/1为无痕无模块加载；2为普通加载）
        :param is_reset: 是否重置
        :return: 操作结果（参考HD返回值表）
        """
        if dll_path is not None:
            dll_path_encoded = dll_path.encode('utf-8') if isinstance(dll_path, str) else dll_path
        else:
            dll_path_encoded = None
        
        if lua_path is not None:
            lua_path_encoded = lua_path.encode('utf-8') if isinstance(lua_path, str) else lua_path
        else:
            lua_path_encoded = None
        
        return self.dll.HCInject_InitExx(win_index, dll_path_encoded, lua_path_encoded, add_type, is_reset)
    
    def get_pid(self, win_index):
        """
        获取打开的进程PID
        :param win_index: 窗口序号（从1开始）
        :return: 进程PID（参考HD返回值表）
        """
        return self.dll.HCInject_GetPid(win_index)
    
    def get_pre_pid(self, win_index):
        """
        获取打开的进程之前的PID（可用于重连）
        :param win_index: 窗口序号（从1开始）
        :return: 进程PID（参考HD返回值表）
        """
        return self.dll.HCInject_GetPrePid(win_index)
    
    def get_pre_win_index(self, pid):
        """
        通过进程PID尝试获取绑定的窗口序号
        :param pid: 指定进程PID
        :return: 窗口序号（参考HD返回值表）
        """
        return self.dll.HCInject_GetPreWinIndex(pid)
    
    def get_pre_win_index_ex(self, pid, win_index, check_fun=None):
        """
        通过进程PID尝试获取绑定的窗口序号（支持检查回调）
        :param pid: 进程PID
        :param win_index: 安装插件方式传递的序号
        :param check_fun: 检查回调函数
        :return: 窗口序号（参考HD返回值表）
        """
        # 注意：这里的check_fun需要是一个可调用的函数，并且其参数和返回值需要符合DLL的要求
        # 如果不需要回调，可以传入None
        return self.dll.HCInject_GetPreWinIndexEx(pid, win_index, check_fun)
    
    def get_hwnd(self, win_index, class_name=None, title=None, filter=0, is_fuzzy=False, check_millis=0):
        """
        获取窗口句柄（通过PID获取，需先安装插件到目标进程）
        :param win_index: 窗口序号（从1开始）
        :param class_name: 窗口类名（不指定时为None）
        :param title: 窗口标题（不指定时为None）
        :param filter: 筛选标识（1：标题；2：类名；8：检测是否无父窗口；16：检查窗口句柄是否有效）
        :param is_fuzzy: 匹配方式（True为模糊匹配；False为完全匹配）
        :param check_millis: 循环检查毫秒数（≤0表示不需要循环获取）
        :return: 窗口句柄（参考HD返回值表）
        """
        if class_name is not None:
            class_name_encoded = class_name.encode('utf-8') if isinstance(class_name, str) else class_name
        else:
            class_name_encoded = None
        
        if title is not None:
            title_encoded = title.encode('utf-8') if isinstance(title, str) else title
        else:
            title_encoded = None
        
        return self.dll.HCInject_GetHwnd(win_index, class_name_encoded, title_encoded, filter, is_fuzzy, check_millis)
    
    def get_hwnd_ex(self, win_index):
        """
        获取窗口句柄（内置接口，一般无需调用）
        :param win_index: 窗口序号（从1开始）
        :return: 窗口句柄（参考HD返回值表）
        """
        return self.dll.HCInject_GetHwndEx(win_index)
    
    def continue_(self, win_index):
        """
        继续环境加载操作
        :param win_index: 窗口序号（从1开始）
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCInject_Continue(win_index)
    
    def set_data(self, win_index, data_buffer, data_size):
        """
        存储自定义二进制数据
        :param win_index: 窗口序号（从1开始）
        :param data_buffer: 用户数据缓冲区（可存储字符串、JSON等类型）
        :param data_size: 来源缓冲区中有效数据的大小（总大小限制为1024字节）
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCInject_SetData(win_index, data_buffer, data_size)
    
    def get_data(self, win_index, data_buffer, buffer_size):
        """
        获取自定义二进制数据（对应HCInject_SetData存储的数据）
        :param win_index: 窗口序号（从1开始）
        :param data_buffer: 存储获取数据的缓冲区
        :param buffer_size: 存储缓冲区的大小（不能≤0，内部获取的数据最大为1024字节）
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCInject_GetData(win_index, data_buffer, buffer_size)


def create_hd_inject(dll_path=None, is_debug=None):
    """
    创建HDInject实例的工厂函数
    :param dll_path: DLL文件所在路径。如果为None，则使用已通过DLL管理器初始化的DLL
    :param is_debug: 是否使用调试版DLL。如果为None，则使用已通过DLL管理器初始化的设置
    :return: HDInject实例
    """
    return HDInject(dll_path, is_debug)