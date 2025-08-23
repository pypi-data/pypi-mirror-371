import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase

class HDShellCode(HDModuleBase):
    """
    HD ShellCode模块
    负责处理ShellCode相关的功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化HDShellCode实例
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
    
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 初始化获取ShellCode函数
        self.dll.HCSH_GetShellCode.argtypes = [
            ctypes.c_int32,      # 模式：32位模式填4，64位模式填8
            ctypes.c_char_p,     # 汇编文本
            ctypes.POINTER(ctypes.c_ubyte),  # 机器码缓冲区
            ctypes.c_int32,      # 机器码缓冲区大小
            ctypes.POINTER(ctypes.c_int32),  # 返回机器码字节大小的地址
            ctypes.POINTER(ctypes.c_int32),  # 错误1变量的地址
            ctypes.POINTER(ctypes.c_int32)   # 错误2变量的地址
        ]
        self.dll.HCSH_GetShellCode.restype = ctypes.c_int64
        
        # 初始化写入ShellCode函数
        self.dll.HCSH_WriteShellCode.argtypes = [
            ctypes.c_int32,      # 目标进程的PID
            ctypes.POINTER(ctypes.c_ubyte),  # 机器码缓冲区
            ctypes.c_int32,      # 机器码缓冲区大小
            ctypes.POINTER(ctypes.c_int64)   # 返回变量的地址
        ]
        self.dll.HCSH_WriteShellCode.restype = ctypes.c_int64
    
    def get_shell_code(self, mode, assembly_text):
        """
        将汇编文本转换为机器码
        :param mode: 模式：32位模式填4，64位模式填8
        :param assembly_text: 汇编文本字符串
        :return: (结果码, 机器码(bytes), 机器码大小, 错误行号, 错误信息代码)
        """
        # 为机器码分配足够大的缓冲区
        buffer_size = 1024 * 1024  # 1MB的缓冲区
        shell_code_buffer = (ctypes.c_ubyte * buffer_size)()
        
        # 准备输出参数
        shell_code_size = ctypes.c_int32(0)
        error_line = ctypes.c_int32(0)
        error_code = ctypes.c_int32(0)
        
        # 调用DLL函数
        result = self.dll.HCSH_GetShellCode(
            mode,
            ctypes.c_char_p(assembly_text.encode('utf-8')),
            shell_code_buffer,
            buffer_size,
            ctypes.byref(shell_code_size),
            ctypes.byref(error_line),
            ctypes.byref(error_code)
        )
        
        # 提取机器码
        if result > 0 and shell_code_size.value > 0:
            shell_code = bytes(shell_code_buffer[:shell_code_size.value])
        else:
            shell_code = bytes()
        
        return result, shell_code, shell_code_size.value, error_line.value, error_code.value
    
    def write_shell_code(self, pid, shell_code):
        """
        将机器码写入到指定进程
        :param pid: 目标进程的PID
        :param shell_code: 机器码（bytes类型）
        :return: (结果码, 写入地址)
        """
        # 准备输入参数
        shell_code_buffer = (ctypes.c_ubyte * len(shell_code))(*shell_code)
        
        # 准备输出参数
        write_address = ctypes.c_int64(0)
        
        # 调用DLL函数
        result = self.dll.HCSH_WriteShellCode(
            pid,
            shell_code_buffer,
            len(shell_code),
            ctypes.byref(write_address)
        )
        
        return result, write_address.value


# 工厂函数
def create_hd_shell_code(dll_path=None, is_debug=None):
    """
    创建HDShellCode实例
    :param dll_path: DLL文件所在路径（可选，如果为None，则使用已通过DLL管理器初始化的DLL）
    :param is_debug: 是否使用调试版DLL（可选，如果为None，则使用已通过DLL管理器初始化的设置）
    :return: HDShellCode实例
    """
    return HDShellCode(dll_path, is_debug)