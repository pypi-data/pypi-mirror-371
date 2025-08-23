import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase

class HDLogin(HDModuleBase):
    """
    HD登录模块
    负责处理与登录相关的功能
    """
    
    def _initialize_functions(self):
        """初始化DLL中的函数"""

        # 初始化HCHD_Login函数
        self.HCHD_Login = self.dll.HCHD_Login
        self.HCHD_Login.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool]
        self.HCHD_Login.restype = ctypes.c_longlong

        # 初始化HCHD_GetLastLoginFYI函数
        self.HCHD_GetLastLoginFYI = self.dll.HCHD_GetLastLoginFYI
        self.HCHD_GetLastLoginFYI.argtypes = []
        self.HCHD_GetLastLoginFYI.restype = ctypes.c_longlong

        # 初始化HCHD_GetExpiredTimeStamp函数
        self.HCHD_GetExpiredTimeStamp = self.dll.HCHD_GetExpiredTimeStamp
        self.HCHD_GetExpiredTimeStamp.argtypes = []
        self.HCHD_GetExpiredTimeStamp.restype = ctypes.c_longlong

        # 初始化HCHD_GetFYI函数
        self.HCHD_GetFYI = self.dll.HCHD_GetFYI
        self.HCHD_GetFYI.argtypes = []
        self.HCHD_GetFYI.restype = ctypes.c_longlong

        # 初始化HCHD_GetOpenMaxNum函数
        self.HCHD_GetOpenMaxNum = self.dll.HCHD_GetOpenMaxNum
        self.HCHD_GetOpenMaxNum.argtypes = []
        self.HCHD_GetOpenMaxNum.restype = ctypes.c_longlong

    def login(self, account, password, app_name, app_lparam, auto_update=False, show_msg_box=False):
        """
        HD登录验证接口
        :param account: 账号
        :param password: 密码
        :param app_name: 中控进程名字
        :param app_lparam: 打开中控的启动参数
        :param auto_update: 是否自动更新
        :param show_msg_box: 如果需要更新是否弹出消息框提醒
        :return: 大于0表示版本号，具体可查看HD返回值表
        """
        # 将字符串转换为C类型的字符指针
        account_c = ctypes.c_char_p(account.encode('utf-8'))
        password_c = ctypes.c_char_p(password.encode('utf-8'))
        app_name_c = ctypes.c_char_p(app_name.encode('utf-8'))
        app_lparam_c = ctypes.c_char_p(app_lparam.encode('utf-8'))

        # 调用DLL函数
        return self.HCHD_Login(account_c, password_c, app_name_c, app_lparam_c, auto_update, show_msg_box)

    def get_last_login_fyi(self):
        """
        获取最近登录时候的点数
        :return: 可查看HD返回值表
        """
        return self.HCHD_GetLastLoginFYI()

    def get_expired_time_stamp(self):
        """
        获取最近登录时间戳
        :return: 可查看HD返回值表
        """
        return self.HCHD_GetExpiredTimeStamp()

    def get_fyi(self):
        """
        获取点数
        :return: 可查看HD返回值表
        """
        return self.HCHD_GetFYI()

    def get_open_max_num(self):
        """
        获取最大多少开
        :return: 可查看HD返回值表
        """
        return self.HCHD_GetOpenMaxNum()


def create_hd_login(dll_path=None, is_debug=None):
    """
    创建HD登录实例
    :param dll_path: DLL文件所在路径（可选，如果DLL已加载）
    :param is_debug: 是否为调试版（可选，如果DLL已加载）
    :return: HDLogin实例
    """
    return HDLogin(dll_path, is_debug)