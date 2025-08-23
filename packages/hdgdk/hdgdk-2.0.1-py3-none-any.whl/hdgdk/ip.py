import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase

class HDIP(HDModuleBase):
    """
    HD IP模块
    负责处理与IP相关的功能
    """
    def _initialize_functions(self):
        """初始化DLL中的函数"""

        # 初始化HCIP_YMSetRootPath函数
        self.HCIP_YMSetRootPath = self.dll.HCIP_YMSetRootPath
        self.HCIP_YMSetRootPath.argtypes = [ctypes.c_char_p]
        self.HCIP_YMSetRootPath.restype = ctypes.c_longlong

        # 初始化HCIP_YMAddIP函数
        self.HCIP_YMAddIP = self.dll.HCIP_YMAddIP
        self.HCIP_YMAddIP.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
        self.HCIP_YMAddIP.restype = ctypes.c_longlong

        # 初始化HCIP_YMAddProcess函数
        self.HCIP_YMAddProcess = self.dll.HCIP_YMAddProcess
        self.HCIP_YMAddProcess.argtypes = [ctypes.c_char_p]
        self.HCIP_YMAddProcess.restype = ctypes.c_longlong

        # 初始化HCIP_YMOpen函数
        self.HCIP_YMOpen = self.dll.HCIP_YMOpen
        self.HCIP_YMOpen.argtypes = [ctypes.c_int]
        self.HCIP_YMOpen.restype = ctypes.c_longlong

        # 初始化HCIP_YMIsOpen函数
        self.HCIP_YMIsOpen = self.dll.HCIP_YMIsOpen
        self.HCIP_YMIsOpen.argtypes = [ctypes.c_int]
        self.HCIP_YMIsOpen.restype = ctypes.c_longlong

        # 初始化HCIP_YMClose函数
        self.HCIP_YMClose = self.dll.HCIP_YMClose
        self.HCIP_YMClose.argtypes = [ctypes.c_int]
        self.HCIP_YMClose.restype = ctypes.c_longlong

    def ym_set_root_path(self, path):
        """
        设置有米软件路径（EXE路径）
        :param path: 路径
        :return: 可查看HD返回值表
        """
        path_c = ctypes.c_char_p(path.encode('utf-8'))
        return self.HCIP_YMSetRootPath(path_c)

    def ym_add_ip(self, ip, port, account, password, type, kfp=1, pro_name=None):
        """
        添加IP
        :param ip: IP，如：127.0.0.1
        :param port: 端口
        :param account: 对于type==1是账号，如："555555"；对于type==2是加密方式，如："aes-256gcm"
        :param password: 密码
        :param type: 1为socket5，2为ss
        :param kfp: 是否可分配（一般为空，默认1即可）
        :param pro_name: 进程名（一般为空，默认NULL即可）
        :return: 可查看HD返回值表
        """
        ip_c = ctypes.c_char_p(ip.encode('utf-8'))
        port_c = ctypes.c_int(port)
        account_c = ctypes.c_char_p(account.encode('utf-8'))
        password_c = ctypes.c_char_p(password.encode('utf-8'))
        type_c = ctypes.c_int(type)
        kfp_c = ctypes.c_int(kfp)
        pro_name_c = ctypes.c_char_p(pro_name.encode('utf-8')) if pro_name else None
        
        return self.HCIP_YMAddIP(ip_c, port_c, account_c, password_c, type_c, kfp_c, pro_name_c)

    def ym_add_process(self, pro_name):
        """
        添加代理的进程名
        :param pro_name: 进程名，如：Game.exe
        :return: 可查看HD返回值表
        """
        pro_name_c = ctypes.c_char_p(pro_name.encode('utf-8'))
        return self.HCIP_YMAddProcess(pro_name_c)

    def ym_open(self, type):
        """
        打开有米软件
        :param type: 0为国内IP，1为国外IP
        :return: 可查看HD返回值表
        """
        type_c = ctypes.c_int(type)
        return self.HCIP_YMOpen(type_c)

    def ym_is_open(self, type):
        """
        判断有米软件是否已经打开
        :param type: 0为国内IP，1为国外IP
        :return: 可查看HD返回值表
        """
        type_c = ctypes.c_int(type)
        return self.HCIP_YMIsOpen(type_c)

    def ym_close(self, type):
        """
        关闭有米软件
        :param type: 0为国内IP，1为国外IP
        :return: 可查看HD返回值表
        """
        type_c = ctypes.c_int(type)
        return self.HCIP_YMClose(type_c)


def create_hd_ip(dll_path=None, is_debug=None):
    """
    创建HD IP实例
    :param dll_path: DLL文件所在路径（可选，如果DLL已加载）
    :param is_debug: 是否为调试版（可选，如果DLL已加载）
    :return: HDIP实例
    """
    return HDIP(dll_path, is_debug)