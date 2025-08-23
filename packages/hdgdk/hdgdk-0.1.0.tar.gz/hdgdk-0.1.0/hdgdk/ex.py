import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase

class HDExCallback:
    """
    HD扩展模块回调基类
    开发者需要继承此类并重写相关方法来实现自定义回调逻辑
    """
    def open_callback(self, windows_index):
        """
        打开回调函数
        :param windows_index: 当前指定序号
        :return: 根据安装方式不同返回不同的值：
                 - 方式一：返回1表示手动打开，返回PID表示自动打开
                 - 方式二：返回PID覆盖传递的PID参数
                 - 方式三：返回窗口句柄覆盖传递的句柄参数
        """
        raise NotImplementedError("必须重写open_callback方法")
    
    def check_callback(self, windows_index, pre_windows_index, pre_pid, error):
        """
        检查回调函数
        :param windows_index: 当前指定序号
        :param pre_windows_index: 之前绑定的序号或错误值
        :param pre_pid: 之前绑定的序号对应的PID
        :param error: 提示值
        :return: 根据error值返回不同结果：
                 - error==5（重连窗口）：返回1表示重连加载环境，0表示新窗口
                 - error==6（重连窗口序号不一致）：返回1表示重连并使用之前绑定的序号加载环境，0表示新窗口
                 - error==8（检查PID存在）：返回>0表示认为prepid存在，一般返回-1或0
                 - 其他情况：返回<0的自定义值可中断流程
        """
        # 默认实现：不进行特殊处理
        return 0

class HDEx(HDModuleBase):
    """
    HD扩展模块
    提供扩展功能的支持
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化HD扩展模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
        self._callback_instances = {}
    
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """

        # 初始化HDEX_InstallPlugin1函数
        self.HDEX_InstallPlugin1 = self.dll.HDEX_InstallPlugin1
        self.HDEX_InstallPlugin1.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, 
                                           ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_void_p, 
                                           ctypes.c_void_p, ctypes.c_int]
        self.HDEX_InstallPlugin1.restype = ctypes.c_longlong

        # 初始化HDEX_InstallPlugin2函数
        self.HDEX_InstallPlugin2 = self.dll.HDEX_InstallPlugin2
        self.HDEX_InstallPlugin2.argtypes = [ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_int, 
                                           ctypes.c_int, ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, 
                                           ctypes.c_int]
        self.HDEX_InstallPlugin2.restype = ctypes.c_longlong

        # 初始化HDEX_InstallPlugin3函数
        self.HDEX_InstallPlugin3 = self.dll.HDEX_InstallPlugin3
        self.HDEX_InstallPlugin3.argtypes = [ctypes.c_int32, ctypes.c_int, ctypes.c_longlong, ctypes.c_int, 
                                           ctypes.c_int, ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, 
                                           ctypes.c_int]
        self.HDEX_InstallPlugin3.restype = ctypes.c_longlong

        # 初始化HDEX_InstallPluginVM函数
        self.HDEX_InstallPluginVM = self.dll.HDEX_InstallPluginVM
        self.HDEX_InstallPluginVM.argtypes = [ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_int, 
                                            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        self.HDEX_InstallPluginVM.restype = ctypes.c_longlong

    def _create_open_callback(self, callback_instance):
        """
        创建打开回调函数
        :param callback_instance: HDExCallback实例
        :return: 回调函数指针
        """
        # 保存回调实例引用，防止被垃圾回收
        callback_id = id(callback_instance)
        self._callback_instances[callback_id] = callback_instance

        @ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_int)
        def open_callback(windows_index):
            try:
                # 调用用户实现的回调方法
                return callback_instance.open_callback(windows_index)
            except Exception as e:
                print(f"打开回调执行错误: {str(e)}")
                return -1  # 返回错误值中断操作
        
        return open_callback

    def _create_check_callback(self, callback_instance):
        """
        创建检查回调函数
        :param callback_instance: HDExCallback实例
        :return: 回调函数指针
        """
        # 保存回调实例引用，防止被垃圾回收
        callback_id = id(callback_instance)
        self._callback_instances[callback_id] = callback_instance

        @ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
        def check_callback(windows_index, pre_windows_index, pre_pid, error):
            try:
                # 调用用户实现的回调方法
                return callback_instance.check_callback(windows_index, pre_windows_index, pre_pid, error)
            except Exception as e:
                print(f"检查回调执行错误: {str(e)}")
                return -1  # 返回错误值中断操作
        
        return check_callback

    def install_plugin1(self, win_index, app, app_type, inject_type, mem_type, game_type, b_accept, 
                       callback_instance, time_out=30000):
        """
        第一种通讯安装插件方式（安装插件再打开进程）
        :param win_index: 窗口序号
        :param app: 进程名
        :param app_type: 进程类型（32/64）
        :param inject_type: 注入类型（0、1、2）
        :param mem_type: 内存模式（0、1、2）
        :param game_type: 游戏类型（一般为0即可）
        :param b_accept: 是否开启接受线程
        :param callback_instance: HDExCallback实例，必须重写open_callback方法
        :param time_out: 超时时间（默认30000）
        :return: 可查看HD返回值表
        """
        # 验证callback_instance
        if not isinstance(callback_instance, HDExCallback):
            raise TypeError("callback_instance必须是HDExCallback类型")

        app_c = ctypes.c_char_p(app.encode('utf-8'))
        open_callback_func = self._create_open_callback(callback_instance)
        check_callback_func = self._create_check_callback(callback_instance)

        return self.HDEX_InstallPlugin1(win_index, app_c, app_type, inject_type, mem_type, game_type, 
                                       b_accept, open_callback_func, check_callback_func, time_out)

    def install_plugin2(self, win_index, fun_type, pid, app_type, game_type, b_accept, 
                       callback_instance=None, time_out=30000):
        """
        第二种通讯安装插件方式（打开进程然后安装插件），通过PID
        :param win_index: 窗口序号
        :param fun_type: 内部安装插件接口类型（支持2、4、6）
        :param pid: 指定PID（可为0，但需指定打开回调）
        :param app_type: 进程类型（32/64）
        :param game_type: 游戏类型（一般为0即可）
        :param b_accept: 是否开启接受线程
        :param callback_instance: HDExCallback实例（可选）
        :param time_out: 超时时间（默认30000）
        :return: 可查看HD返回值表
        """
        open_callback_func = None
        check_callback_func = None

        if callback_instance is not None:
            if not isinstance(callback_instance, HDExCallback):
                raise TypeError("callback_instance必须是HDExCallback类型")
            open_callback_func = self._create_open_callback(callback_instance)
            check_callback_func = self._create_check_callback(callback_instance)

        return self.HDEX_InstallPlugin2(win_index, fun_type, pid, app_type, game_type, b_accept, 
                                       open_callback_func, check_callback_func, time_out)

    def install_plugin3(self, win_index, fun_type, hwnd, app_type, game_type, b_accept, 
                       callback_instance=None, time_out=30000):
        """
        第三种通讯安装插件方式（打开进程然后安装插件），通过窗口句柄
        :param win_index: 窗口序号
        :param fun_type: 内部安装插件接口类型（支持3、5、7）
        :param hwnd: 指定窗口句柄（可为0，但需指定打开回调）
        :param app_type: 进程类型（32/64）
        :param game_type: 游戏类型（一般为0即可）
        :param b_accept: 是否开启接受线程
        :param callback_instance: HDExCallback实例（可选）
        :param time_out: 超时时间（默认30000）
        :return: 可查看HD返回值表
        """
        open_callback_func = None
        check_callback_func = None

        if callback_instance is not None:
            if not isinstance(callback_instance, HDExCallback):
                raise TypeError("callback_instance必须是HDExCallback类型")
            open_callback_func = self._create_open_callback(callback_instance)
            check_callback_func = self._create_check_callback(callback_instance)

        return self.HDEX_InstallPlugin3(win_index, fun_type, hwnd, app_type, game_type, b_accept, 
                                       open_callback_func, check_callback_func, time_out)

    def install_plugin_vm(self, win_index, fun_type, vm_pid, vnc_port, app_type, 
                         callback_instance=None, time_out=30000):
        """
        打开后通过PID安装，针对虚拟机内部自动关联虚拟机
        :param win_index: 窗口序号
        :param fun_type: 内部安装插件接口类型（支持3、5、7）
        :param vm_pid: 虚拟机PID（或由打开回调指定）
        :param vnc_port: 虚拟机VNC端口（-1表示不连接；>0表示连接并断开重连；0表示使用之前缓存端口）
        :param app_type: 进程类型（32/64）
        :param callback_instance: HDExCallback实例（可选）
        :param time_out: 超时时间（默认30000）
        :return: 可查看HD返回值表
        """
        open_callback_func = None
        check_callback_func = None

        if callback_instance is not None:
            if not isinstance(callback_instance, HDExCallback):
                raise TypeError("callback_instance必须是HDExCallback类型")
            open_callback_func = self._create_open_callback(callback_instance)
            check_callback_func = self._create_check_callback(callback_instance)

        return self.HDEX_InstallPluginVM(win_index, fun_type, vm_pid, vnc_port, app_type, 
                                        open_callback_func, check_callback_func, time_out)


def create_hd_ex(dll_path=None, is_debug=None):
    """
    创建HDEx实例的工厂函数

    Args:
        dll_path (str, optional): HD GDK DLL的路径。如果为None，则使用已通过DLL管理器初始化的DLL
        is_debug (bool, optional): 是否使用调试版本的DLL。如果为None，则使用已通过DLL管理器初始化的设置

    Returns:
        HDEx: HDEx实例
    """
    return HDEx(dll_path, is_debug)