import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase

class HDHK(HDModuleBase):
    """
    HD钩子模块
    负责处理API钩子相关的功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化HDHK实例
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
        # 存储回调函数的引用，防止被Python垃圾回收
        self.callbacks = {}
    
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 定义回调函数类型
        # API拦截回调类型
        self.HandleCallBackFunType_Send = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p)
        self.HandleCallBackFunType_SendTo = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_void_p)
        self.HandleCallBackFunType_Recv = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
        self.HandleCallBackFunType_RecvFrom = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
        
        # 通用回调类型
        self.HandleCallBackFunType = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
        
        # 初始化API HOOK相关函数
        self.dll.HDHK_InterceptApi.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        self.dll.HDHK_InterceptApi.restype = ctypes.c_int64
        
        self.dll.HDHK_PauseInterceptApi.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HDHK_PauseInterceptApi.restype = ctypes.c_int64
        
        self.dll.HDHK_RecoverInterceptApi.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HDHK_RecoverInterceptApi.restype = ctypes.c_int64
        
        self.dll.HDHK_UnInterceptApi.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HDHK_UnInterceptApi.restype = ctypes.c_int64
        
        # 初始化Send/Recv相关API函数
        self.dll.HDHK_SendApi.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.dll.HDHK_SendApi.restype = ctypes.c_int64
        
        self.dll.HDHK_SendToApi.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.dll.HDHK_SendToApi.restype = ctypes.c_int64
        
        # 初始化回调修改函数（X86和X64）
        # X86回调修改函数
        self.dll.HDHK_SetProcessCallBackLparamSendX86.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessCallBackLparamSendX86.restype = ctypes.c_int64
        
        self.dll.HDHK_SetProcessCallBackLparamRecvX86.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessCallBackLparamRecvX86.restype = ctypes.c_int64
        
        self.dll.HDHK_SetProcessCallBackLparamSendToX86.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessCallBackLparamSendToX86.restype = ctypes.c_int64
        
        self.dll.HDHK_SetProcessCallBackLparamRecvFromX86.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessCallBackLparamRecvFromX86.restype = ctypes.c_int64
        
        # X64回调修改函数
        self.dll.HDHK_SetProcessCallBackLparamSendX64.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessCallBackLparamSendX64.restype = ctypes.c_int64
        
        self.dll.HDHK_SetProcessCallBackLparamRecvX64.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessCallBackLparamRecvX64.restype = ctypes.c_int64
        
        self.dll.HDHK_SetProcessCallBackLparamSendToX64.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessCallBackLparamSendToX64.restype = ctypes.c_int64
        
        self.dll.HDHK_SetProcessCallBackLparamRecvFromX64.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessCallBackLparamRecvFromX64.restype = ctypes.c_int64
        
        # 初始化Address HOOK相关函数
        self.dll.HDHK_Hook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        self.dll.HDHK_Hook.restype = ctypes.c_int64
        
        self.dll.HDHK_HookEx.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int64, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        self.dll.HDHK_HookEx.restype = ctypes.c_int64
        
        self.dll.HDHK_HookExx.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int64, ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        self.dll.HDHK_HookExx.restype = ctypes.c_int64
        
        self.dll.HDHK_HookExxx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        self.dll.HDHK_HookExxx.restype = ctypes.c_int64
        
        # 初始化HOOK控制函数
        self.dll.HDHK_PauseHook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_bool]
        self.dll.HDHK_PauseHook.restype = ctypes.c_int64
        
        self.dll.HDHK_RecoverHook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_bool]
        self.dll.HDHK_RecoverHook.restype = ctypes.c_int64
        
        self.dll.HDHK_UnHook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_bool]
        self.dll.HDHK_UnHook.restype = ctypes.c_int64
        
        # 初始化HOOK回调修改函数
        self.dll.HDHK_SetProcessHookCallBackLparam.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32]
        self.dll.HDHK_SetProcessHookCallBackLparam.restype = ctypes.c_int64
    
    def intercept_api(self, windows_index, module_name, api_name, break_bytes, callback_func, lparam=0, is_main_thread=False):
        """
        设置拦截API（内置插件，支持X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param module_name: 接口所在dll模块名（仅支持"ws2_32.dll"）
        :param api_name: 接口名（仅支持"send"、"sendto"、"recv"、"recvfrom"，小写）
        :param break_bytes: X86中send/recv/sendto/recvfrom为5；X64中send/recv为5，sendto/recvfrom为7
        :param callback_func: 符合特定类型的回调函数
        :param lparam: 自定义参数（传递给回调）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 存储回调函数引用，防止被垃圾回收
        callback_key = f"intercept_api_{windows_index}_{module_name}_{api_name}"
        
        # 根据API名称选择正确的回调类型
        if api_name == "send":
            callback_ptr = self.HandleCallBackFunType_Send(callback_func)
        elif api_name == "sendto":
            callback_ptr = self.HandleCallBackFunType_SendTo(callback_func)
        elif api_name == "recv":
            callback_ptr = self.HandleCallBackFunType_Recv(callback_func)
        elif api_name == "recvfrom":
            callback_ptr = self.HandleCallBackFunType_RecvFrom(callback_func)
        else:
            raise ValueError("不支持的API名称，仅支持'send'、'sendto'、'recv'、'recvfrom'")
        
        self.callbacks[callback_key] = callback_ptr
        
        # 调用DLL函数
        return self.dll.HDHK_InterceptApi(
            windows_index,
            module_name.encode('utf-8'),
            api_name.encode('utf-8'),
            break_bytes,
            callback_ptr,
            lparam,
            is_main_thread
        )
    
    def pause_intercept_api(self, windows_index, module_name, api_name, is_main_thread=False):
        """
        暂停拦截API（内置插件，支持X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param module_name: 接口所在dll模块名（仅支持"ws2_32.dll"）
        :param api_name: 接口名（仅支持"send"、"sendto"、"recv"、"recvfrom"，小写）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        return self.dll.HDHK_PauseInterceptApi(
            windows_index,
            module_name.encode('utf-8'),
            api_name.encode('utf-8'),
            is_main_thread
        )
    
    def recover_intercept_api(self, windows_index, module_name, api_name, is_main_thread=False):
        """
        恢复拦截API（内置插件，支持X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param module_name: 接口所在dll模块名（仅支持"ws2_32.dll"）
        :param api_name: 接口名（仅支持"send"、"sendto"、"recv"、"recvfrom"，小写）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        return self.dll.HDHK_RecoverInterceptApi(
            windows_index,
            module_name.encode('utf-8'),
            api_name.encode('utf-8'),
            is_main_thread
        )
    
    def un_intercept_api(self, windows_index, module_name, api_name, is_main_thread=False):
        """
        卸载拦截API（内置插件，支持X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param module_name: 接口所在dll模块名（仅支持"ws2_32.dll"）
        :param api_name: 接口名（仅支持"send"、"sendto"、"recv"、"recvfrom"，小写）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 移除回调函数引用
        callback_key = f"intercept_api_{windows_index}_{module_name}_{api_name}"
        if callback_key in self.callbacks:
            del self.callbacks[callback_key]
        
        return self.dll.HDHK_UnInterceptApi(
            windows_index,
            module_name.encode('utf-8'),
            api_name.encode('utf-8'),
            is_main_thread
        )
    
    def send_api(self, windows_index, socket, buffer, buffer_size, flag=0, is_main_thread=False):
        """
        在目标进程中调用Send API（X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param socket: socket套接字
        :param buffer: 缓冲区地址或字节数据
        :param buffer_size: 缓冲区大小
        :param flag: flag参数
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 处理buffer参数
        if isinstance(buffer, bytes):
            buffer_ptr = ctypes.cast(buffer, ctypes.c_void_p)
        else:
            buffer_ptr = buffer
        
        return self.dll.HDHK_SendApi(
            windows_index,
            socket,
            buffer_ptr,
            buffer_size,
            flag,
            is_main_thread
        )
    
    def sendto_api(self, windows_index, socket, buffer, buffer_size, flag=0, port=0, ip=0, is_main_thread=False):
        """
        在目标进程中调用SendTo API（X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param socket: socket套接字
        :param buffer: 缓冲区地址或字节数据
        :param buffer_size: 缓冲区大小
        :param flag: flag参数
        :param port: 目标端口
        :param ip: 网络字节序IP（如"127.0.0.1"对应0x0100007F）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 处理buffer参数
        if isinstance(buffer, bytes):
            buffer_ptr = ctypes.cast(buffer, ctypes.c_void_p)
        else:
            buffer_ptr = buffer
        
        return self.dll.HDHK_SendToApi(
            windows_index,
            socket,
            buffer_ptr,
            buffer_size,
            flag,
            port,
            ip,
            is_main_thread
        )
    
    def set_process_callback_lparam_x86(self, windows_index, api_type, l1, l2, l3, l4, l5, l6, ebp, esp, eip, mark):
        """
        设置X86 API回调参数（根据api_type选择对应的函数）
        :param windows_index: 窗口序号
        :param api_type: API类型（'send'、'recv'、'sendto'、'recvfrom'）
        :param l1-l6: 寄存器值
        :param ebp, esp, eip: 寄存器值
        :param mark: 修改掩码，2的倍数，如1|2表示修改l1、l2
        :return: 0（不修改，走原流程）、1（修改，走原流程，适用于包长度一致）、2（修改，走自定义流程，适用于包长度不一致）
        """
        if api_type == 'send':
            return self.dll.HDHK_SetProcessCallBackLparamSendX86(
                windows_index, l1, l2, l3, l4, l5, l6, ebp, esp, eip, mark
            )
        elif api_type == 'recv':
            return self.dll.HDHK_SetProcessCallBackLparamRecvX86(
                windows_index, l1, l2, l3, l4, l5, l6, ebp, esp, eip, mark
            )
        elif api_type == 'sendto':
            return self.dll.HDHK_SetProcessCallBackLparamSendToX86(
                windows_index, l1, l2, l3, l4, l5, l6, ebp, esp, eip, mark
            )
        elif api_type == 'recvfrom':
            return self.dll.HDHK_SetProcessCallBackLparamRecvFromX86(
                windows_index, l1, l2, l3, l4, l5, l6, ebp, esp, eip, mark
            )
        else:
            raise ValueError("不支持的API类型")
    
    def set_process_callback_lparam_x64(self, windows_index, api_type, rcx, rdx, r8, r9, l5, l6, rbp, rsp, rip, mark):
        """
        设置X64 API回调参数（根据api_type选择对应的函数）
        :param windows_index: 窗口序号
        :param api_type: API类型（'send'、'recv'、'sendto'、'recvfrom'）
        :param rcx, rdx, r8, r9, l5, l6, rbp, rsp, rip: 寄存器值
        :param mark: 修改掩码，2的倍数，如1|2表示修改rcx、rdx
        :return: 0（不修改，走原流程）、1（修改，走原流程，适用于包长度一致）、2（修改，走自定义流程，适用于包长度不一致）
        """
        if api_type == 'send':
            return self.dll.HDHK_SetProcessCallBackLparamSendX64(
                windows_index, rcx, rdx, r8, r9, l5, l6, rbp, rsp, rip, mark
            )
        elif api_type == 'recv':
            return self.dll.HDHK_SetProcessCallBackLparamRecvX64(
                windows_index, rcx, rdx, r8, r9, l5, l6, rbp, rsp, rip, mark
            )
        elif api_type == 'sendto':
            return self.dll.HDHK_SetProcessCallBackLparamSendToX64(
                windows_index, rcx, rdx, r8, r9, l5, l6, rbp, rsp, rip, mark
            )
        elif api_type == 'recvfrom':
            return self.dll.HDHK_SetProcessCallBackLparamRecvFromX64(
                windows_index, rcx, rdx, r8, r9, l5, l6, rbp, rsp, rip, mark
            )
        else:
            raise ValueError("不支持的API类型")
    
    def hook(self, windows_index, hook_address, break_bytes, callback_func, lparam=0, is_main_thread=False):
        """
        任意地址HOOK（内置插件，支持X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param hook_address: 目标HOOK地址（需符合X86/X64 HOOK地址规则）
        :param break_bytes: 涉及的汇编字节数
        :param callback_func: HandleCallBackFunType类型回调函数
        :param lparam: 自定义参数（传递给回调）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 存储回调函数引用，防止被垃圾回收
        callback_key = f"hook_{windows_index}_{hook_address}"
        callback_ptr = self.HandleCallBackFunType(callback_func)
        self.callbacks[callback_key] = callback_ptr
        
        return self.dll.HDHK_Hook(
            windows_index,
            hook_address,
            break_bytes,
            callback_ptr,
            lparam,
            is_main_thread
        )
    
    def hook_ex(self, windows_index, module_name, hook_address, break_bytes, callback_func, lparam=0, is_main_thread=False):
        """
        任意地址HOOK（扩展版本，主要针对X64）
        :param windows_index: 窗口序号（从1开始）
        :param module_name: 所属模块名字
        :param hook_address: 目标HOOK地址
        :param break_bytes: 涉及的汇编字节数
        :param callback_func: HandleCallBackFunType类型回调函数
        :param lparam: 自定义参数（传递给回调）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 存储回调函数引用，防止被垃圾回收
        callback_key = f"hook_ex_{windows_index}_{module_name}_{hook_address}"
        callback_ptr = self.HandleCallBackFunType(callback_func)
        self.callbacks[callback_key] = callback_ptr
        
        return self.dll.HDHK_HookEx(
            windows_index,
            module_name.encode('utf-8'),
            hook_address,
            break_bytes,
            callback_ptr,
            lparam,
            is_main_thread
        )
    
    def hook_exx(self, windows_index, module_name, module_base, module_size, hook_address, break_bytes, callback_func, lparam=0, is_main_thread=False):
        """
        任意地址HOOK（扩展版本，主要针对X64）
        :param windows_index: 窗口序号（从1开始）
        :param module_name: 所属模块名字
        :param module_base: 模块首地址
        :param module_size: 模块大小
        :param hook_address: 目标HOOK地址
        :param break_bytes: 涉及的汇编字节数
        :param callback_func: HandleCallBackFunType类型回调函数
        :param lparam: 自定义参数（传递给回调）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 存储回调函数引用，防止被垃圾回收
        callback_key = f"hook_exx_{windows_index}_{module_name}_{hook_address}"
        callback_ptr = self.HandleCallBackFunType(callback_func)
        self.callbacks[callback_key] = callback_ptr
        
        return self.dll.HDHK_HookExx(
            windows_index,
            module_name.encode('utf-8'),
            module_base,
            module_size,
            hook_address,
            break_bytes,
            callback_ptr,
            lparam,
            is_main_thread
        )
    
    def hook_exxx(self, windows_index, hook_address, module_name, jmp13_address, asm_address, break_bytes, callback_func, lparam=0, is_main_thread=False):
        """
        任意地址HOOK（扩展版本，主要针对X64）
        :param windows_index: 窗口序号（从1开始）
        :param hook_address: 目标HOOK地址
        :param module_name: 所属模块名字
        :param jmp13_address: jmp13空白地址
        :param asm_address: 保留汇编地址
        :param break_bytes: 涉及的汇编字节数
        :param callback_func: HandleCallBackFunType类型回调函数
        :param lparam: 自定义参数（传递给回调）
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 存储回调函数引用，防止被垃圾回收
        callback_key = f"hook_exxx_{windows_index}_{module_name}_{hook_address}"
        callback_ptr = self.HandleCallBackFunType(callback_func)
        self.callbacks[callback_key] = callback_ptr
        
        return self.dll.HDHK_HookExxx(
            windows_index,
            hook_address,
            module_name.encode('utf-8'),
            jmp13_address,
            asm_address,
            break_bytes,
            callback_ptr,
            lparam,
            is_main_thread
        )
    
    def pause_hook(self, windows_index, hook_address, is_main_thread=False):
        """
        暂停任意地址HOOK（X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param hook_address: 目标HOOK地址
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        return self.dll.HDHK_PauseHook(
            windows_index,
            hook_address,
            is_main_thread
        )
    
    def recover_hook(self, windows_index, hook_address, is_main_thread=False):
        """
        恢复任意地址HOOK（X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param hook_address: 目标HOOK地址
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        return self.dll.HDHK_RecoverHook(
            windows_index,
            hook_address,
            is_main_thread
        )
    
    def un_hook(self, windows_index, hook_address, is_main_thread=False):
        """
        卸载任意地址HOOK（X86/X64）
        :param windows_index: 窗口序号（从1开始）
        :param hook_address: 目标HOOK地址
        :param is_main_thread: 是否主线程调用
        :return: 查看返回值表HD返回值表
        """
        # 移除回调函数引用
        callback_key = f"hook_{windows_index}_{hook_address}"
        if callback_key in self.callbacks:
            del self.callbacks[callback_key]
        
        # 检查其他可能的回调键名
        for key in list(self.callbacks.keys()):
            if f"hook_ex" in key and str(hook_address) in key and str(windows_index) in key:
                del self.callbacks[key]
        
        return self.dll.HDHK_UnHook(
            windows_index,
            hook_address,
            is_main_thread
        )
    
    def set_process_hook_callback_lparam(self, windows_index, plugin_index, rax, rbx, rcx, rdx, r8, r9, r10, r11, rbp, rsp, rip, mark):
        """
        修改HOOK回调返回参数（X86/X64通用）
        :param windows_index: 窗口序号
        :param plugin_index: 插件序号
        :param rax, rbx, rcx, rdx, r8, r9, r10, r11, rbp, rsp, rip: 寄存器值
        :param mark: 修改掩码，如1|2表示修改rax、rbx
        :return: 查看返回值表HD返回值表
        """
        return self.dll.HDHK_SetProcessHookCallBackLparam(
            windows_index,
            plugin_index,
            rax,
            rbx,
            rcx,
            rdx,
            r8,
            r9,
            r10,
            r11,
            rbp,
            rsp,
            rip,
            mark
        )


# 定义回调基类
class HDHKCallback:
    """
    HDHOOK模块回调基类，用户可以继承此类并实现自己的回调方法
    """
    def handle_send(self, windows_index, socket, buffer, buffer_size, flag, lparam):
        """
        send API拦截回调
        :param windows_index: 窗口序号
        :param socket: socket套接字
        :param buffer: 缓冲区地址
        :param buffer_size: 缓冲区大小
        :param flag: flag参数
        :param lparam: 附加参数
        :return: 1表示需要修改
        """
        return 0
        
    def handle_sendto(self, windows_index, socket, buffer, buffer_size, flag, to_addr, to_len, lparam):
        """
        sendto API拦截回调
        :param windows_index: 窗口序号
        :param socket: socket套接字
        :param buffer: 缓冲区地址
        :param buffer_size: 缓冲区大小
        :param flag: flag参数
        :param to_addr: 目标地址
        :param to_len: 地址长度
        :param lparam: 附加参数
        :return: 1表示需要修改
        """
        return 0
        
    def handle_recv(self, windows_index, socket, buffer, buffer_size_ptr, flags_ptr, lparam):
        """
        recv API拦截回调
        :param windows_index: 窗口序号
        :param socket: socket套接字
        :param buffer: 缓冲区地址
        :param buffer_size_ptr: 缓冲区大小指针
        :param flags_ptr: flags指针
        :param lparam: 附加参数
        :return: 1表示需要修改
        """
        return 0
        
    def handle_recvfrom(self, windows_index, socket, buffer, buffer_size_ptr, flags_ptr, from_addr, from_len_ptr, lparam):
        """
        recvfrom API拦截回调
        :param windows_index: 窗口序号
        :param socket: socket套接字
        :param buffer: 缓冲区地址
        :param buffer_size_ptr: 缓冲区大小指针
        :param flags_ptr: flags指针
        :param from_addr: 来源地址
        :param from_len_ptr: 地址长度指针
        :param lparam: 附加参数
        :return: 1表示需要修改
        """
        return 0
        
    def handle_hook(self, windows_index, plugin_index, rax, rbx, rcx, rdx, r8, r9, r10, r11, rbp, rsp, rip):
        """
        任意地址HOOK回调
        :param windows_index: 窗口序号
        :param plugin_index: 插件序号
        :param rax, rbx, rcx, rdx, r8, r9, r10, r11, rbp, rsp, rip: 寄存器值
        :return: 0（忽视被破坏语句，跳至下一句）、1（走原流程）、2（修改值+跳至下一句）、3（修改值+走原流程）
        """
        return 1


# 工厂函数
def create_hd_hk(dll_path=None, is_debug=None):
    """
    创建HDHK实例
    :param dll_path: DLL文件所在路径。如果为None，则使用已通过DLL管理器初始化的DLL
    :param is_debug: 是否使用调试版DLL。如果为None，则使用已通过DLL管理器初始化的设置
    :return: HDHK实例
    """
    return HDHK(dll_path, is_debug)