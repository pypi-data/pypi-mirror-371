import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase

class HDEnv(HDModuleBase):
    """
    HD环境模块
    负责处理与环境相关的功能
    """
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 设置函数参数类型和返回值类型
        self.dll.HCEnv_Init.argtypes = [ctypes.c_int32]
        self.dll.HCEnv_Init.restype = ctypes.c_int64
        
        self.dll.HCEnv_InitEx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCEnv_InitEx.restype = ctypes.c_int64
        
        self.dll.HCEnv_Load.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCEnv_Load.restype = ctypes.c_int64
        
        self.dll.HCEnv_LoadEx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.dll.HCEnv_LoadEx.restype = ctypes.c_int64
        
        self.dll.HCEnv_UnLoad.argtypes = [ctypes.c_int32]
        self.dll.HCEnv_UnLoad.restype = ctypes.c_int64
        
        # 新增函数定义
        self.dll.HCEnv_UnLoadEx.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.dll.HCEnv_UnLoadEx.restype = ctypes.c_int64
        
        self.dll.HCEnv_ExitProcess.argtypes = [ctypes.c_int32]
        self.dll.HCEnv_ExitProcess.restype = ctypes.c_int64
        
        self.dll.HCEnv_GetWinExIndex.argtypes = [ctypes.c_int32]
        self.dll.HCEnv_GetWinExIndex.restype = ctypes.c_int64
        
        self.dll.HCEnv_GetGlobalWinExIndex.argtypes = []
        self.dll.HCEnv_GetGlobalWinExIndex.restype = ctypes.c_int64
        
        # 为回调函数定义类型
        HeartFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)
        WindowsSortFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)
        HandleEventFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p)
        ShutDownEventFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32)
        CheckPluginFunType = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)
        
        self.dll.HCEnv_AttachHeart.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCEnv_AttachHeart.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetWindowsSortInfo.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p]
        self.dll.HCEnv_SetWindowsSortInfo.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetScreenCheckHeart.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCEnv_SetScreenCheckHeart.restype = ctypes.c_int64
        
        # 新增的18个函数
        self.dll.HCEnv_DetachHeart.argtypes = []
        self.dll.HCEnv_DetachHeart.restype = ctypes.c_int64
        
        self.dll.HCEnv_Debug.argtypes = [ctypes.c_bool]
        self.dll.HCEnv_Debug.restype = ctypes.c_int64
        
        self.dll.HCEnv_MsgFile.argtypes = [ctypes.c_bool]
        self.dll.HCEnv_MsgFile.restype = ctypes.c_int64
        
        self.dll.HCEnv_AddThread.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCEnv_AddThread.restype = ctypes.c_int64
        
        self.dll.HCEnv_TestCALL_RetValue.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]
        self.dll.HCEnv_TestCALL_RetValue.restype = ctypes.c_int64
        
        self.dll.HCEnv_TestCALL_RetArray.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]
        self.dll.HCEnv_TestCALL_RetArray.restype = ctypes.c_int64
        
        self.dll.HCEnv_TestCALL_RetValueEx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]
        self.dll.HCEnv_TestCALL_RetValueEx.restype = ctypes.c_int64
        
        self.dll.HCEnv_TestCALL_RetArrayEx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]
        self.dll.HCEnv_TestCALL_RetArrayEx.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetProcessType.argtypes = [ctypes.c_int32]
        self.dll.HCEnv_SetProcessType.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetProcessTypeEx.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCEnv_SetProcessTypeEx.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetHandleEventCallBack.argtypes = [ctypes.c_void_p]
        self.dll.HCEnv_SetHandleEventCallBack.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetShutDownCallBack.argtypes = [ctypes.c_void_p]
        self.dll.HCEnv_SetShutDownCallBack.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetPidCheckBack.argtypes = [ctypes.c_void_p]
        self.dll.HCEnv_SetPidCheckBack.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetCheckComItlTime.argtypes = [ctypes.c_int32]
        self.dll.HCEnv_SetCheckComItlTime.restype = ctypes.c_int64
        
        self.dll.HCEnv_SetCheckCallBackTime.argtypes = [ctypes.c_int32]
        self.dll.HCEnv_SetCheckCallBackTime.restype = ctypes.c_int64
        
        self.dll.HCEnv_TerminateThread.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.dll.HCEnv_TerminateThread.restype = ctypes.c_int64
        
        self.dll.HCEnv_TerminateThreadEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_bool]
        self.dll.HCEnv_TerminateThreadEx.restype = ctypes.c_int64
        
        self.dll.HCEnv_ProtectFun.argtypes = [ctypes.c_int64, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCEnv_ProtectFun.restype = ctypes.c_int64
    
    def init(self, time_out=10000):
        """
        HD插件环境加载 (初始化中控环境)
        :param time_out: 通讯超时时间 (毫秒，默认即可)
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCEnv_Init(time_out)
    
    def init_ex(self, time_out=10000, check_interval=20, callback_response=5):
        """
        HD插件环境加载 (初始化中控环境，扩展版本)
        :param time_out: 通讯超时时间 (毫秒，默认即可)
        :param check_interval: 通讯检测间隔毫秒 (默认即可)
        :param callback_response: 回调响应毫秒 (默认即可)
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCEnv_InitEx(time_out, check_interval, callback_response)
    
    def load(self, win_index, pid, game_type=0):
        """
        HD插件环境加载
        :param win_index: 窗口序号 (从1开始)
        :param pid: 目标进程的PID
        :param game_type: 内置游戏接口标识
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCEnv_Load(win_index, pid, game_type)
    
    def load_ex(self, win_index, pid, game_type=0, enable_thread=False):
        """
        HD插件环境加载 (扩展版本，涉及回调)
        :param win_index: 窗口序号 (从1开始)
        :param pid: 目标进程的PID
        :param game_type: 内置游戏接口标识
        :param enable_thread: 是否开启接受线程 (如需开启跨进程回调，设为True)
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCEnv_LoadEx(win_index, pid, game_type, enable_thread)
    
    def unload(self, win_index):
        """
        HD插件环境卸载
        :param win_index: 窗口序号 (从1开始)
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCEnv_UnLoad(win_index)
    
    def unload_ex(self, win_index, b_recon=True):
        """
        HD插件环境卸载 (扩展版本)
        :param win_index: 窗口序号 (从1开始)
        :param b_recon: 是否允许重连 (默认需要)
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCEnv_UnLoadEx(win_index, b_recon)
    
    def exit_process(self, win_index):
        """
        关闭绑定的目标窗口
        :param win_index: 窗口序号 (从1开始)
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCEnv_ExitProcess(win_index)
    
    def get_win_ex_index(self, win_index):
        """
        获取副窗口序号
        :param win_index: 窗口序号
        :return: 副窗口序号（参考HD返回值表）
        """
        return self.dll.HCEnv_GetWinExIndex(win_index)
    
    def get_global_win_ex_index(self):
        """
        获取全局副窗口序号 (全局唯一)
        :return: 全局副窗口序号（参考HD返回值表）
        """
        return self.dll.HCEnv_GetGlobalWinExIndex()
    
    def attach_heart(self, heart_type, fun_callback, time_out_nor=10000, time_out=10000):
        """
        给中控附加心跳检测
        :param heart_type: 心跳类型 (0：正常心跳，含心跳 + 排序回调；1：通讯线程；2：主线程；3：卡屏；6：1+2+3)
        :param fun_callback: 心跳异常回调函数，类型为def callback(窗口索引, type): return 1或0
        :param time_out_nor: 正常心跳间隔时间
        :param time_out: 检测超时时间
        :return: 操作结果（参考HD返回值表）
        """
        # 定义回调函数类型
        HeartFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)
        # 转换Python函数为C回调函数
        c_callback = HeartFunType(fun_callback)
        # 为了防止Python垃圾回收，需要保存回调函数的引用
        self.heart_callback = c_callback
        return self.dll.HCEnv_AttachHeart(heart_type, c_callback, time_out_nor, time_out)
    
    def set_windows_sort_info(self, x, y, offset_x, offset_y, cols, fun_callback=None):
        """
        设置窗口排序信息
        :param x: 屏幕左上角 X 坐标起点
        :param y: 屏幕左上角 Y 坐标起点
        :param offset_x: 每列左上角 X 偏移
        :param offset_y: 每行左上角 Y 偏移
        :param cols: 列数 (-1 表示一排无限窗口)
        :param fun_callback: 排序窗口回调函数，类型为def callback(窗口序号, pid, x, y): return 0或其他
        :return: 操作结果（参考HD返回值表）
        """
        if fun_callback is None:
            # 如果没有提供回调函数，传递None
            return self.dll.HCEnv_SetWindowsSortInfo(x, y, offset_x, offset_y, cols, None)
        
        # 定义回调函数类型
        WindowsSortFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)
        # 转换Python函数为C回调函数
        c_callback = WindowsSortFunType(fun_callback)
        # 为了防止Python垃圾回收，需要保存回调函数的引用
        self.sort_callback = c_callback
        return self.dll.HCEnv_SetWindowsSortInfo(x, y, offset_x, offset_y, cols, c_callback)
    
    def set_screen_check_heart(self, x, y, width, height, max_count, interval_time=1000):
        """
        设置卡屏检测范围和次数 (心跳类型为 3 或 6 时需用)
        :param x: 客户端 X 坐标
        :param y: 客户端 Y 坐标
        :param width: 检测区域宽度
        :param height: 检测区域高度
        :param max_count: 达到该次数则触发回调
        :param interval_time: 截屏前后间隔时间 (默认 1000 毫秒)
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCEnv_SetScreenCheckHeart(x, y, width, height, max_count, interval_time)


    def detach_heart(self):
        """
        脱离中控附加的心跳检测
        :return: 操作结果（参考HD返回值表）
        备注：脱离过程会堵塞，直至成功；一般在中控进程关闭前调用
        """
        return self.dll.HCEnv_DetachHeart()
    
    def debug(self, is_debug=False):
        """
        设置导入接口为调试模式
        :param is_debug: 是否调试模式
        :return: 操作结果（参考HD返回值表）
        备注：使用HDDebug.dll时需设为True；中控初始化时可调用，仅需一次
        """
        return self.dll.HCEnv_Debug(is_debug)
    
    def msg_file(self, is_enable=True):
        """
        设置是否打开文件提示窗口
        :param is_enable: 是否开启文件提示日志
        :return: 操作结果（参考HD返回值表）
        备注：当HD内部导致中控关闭或插件失效时，会以文件形式提示信息
        """
        return self.dll.HCEnv_MsgFile(is_enable)
    
    def add_thread(self, win_index, thread_id, is_debug=0):
        """
        添加线程环境
        :param win_index: 窗口序号 (从1开始)
        :param thread_id: 当前线程ID
        :param is_debug: 是否调试模式
        :return: 操作结果（参考HD返回值表）
        备注：用于测试，开发者一般无需使用
        """
        return self.dll.HCEnv_AddThread(win_index, thread_id, is_debug)
    
    def test_call_ret_value(self, win_index, rcx=0, rdx=0, r8=0, r9=0, lparam5=0, lparam6=0, is_main_thread=False):
        """
        测试通讯是否成功 (返回单一值)
        :param win_index: 窗口序号 (从1开始)
        :param rcx, rdx, r8, r9, lparam5, lparam6: CALL参数
        :param is_main_thread: 是否在主线程调用
        :return: 操作结果（参考HD返回值表）
        备注：用于测试环境是否搭建成功
        """
        return self.dll.HCEnv_TestCALL_RetValue(win_index, rcx, rdx, r8, r9, lparam5, lparam6, is_main_thread)
    
    def test_call_ret_array(self, win_index, rcx=0, rdx=0, r8=0, r9=0, lparam5=0, lparam6=0, is_main_thread=False):
        """
        测试通讯是否成功 (返回JSON字符串)
        :param win_index: 窗口序号 (从1开始)
        :param rcx, rdx, r8, r9, lparam5, lparam6: CALL参数
        :param is_main_thread: 是否在主线程调用
        :return: 操作结果（参考HD返回值表）
        备注：用于测试环境是否搭建成功
        """
        return self.dll.HCEnv_TestCALL_RetArray(win_index, rcx, rdx, r8, r9, lparam5, lparam6, is_main_thread)
    
    def test_call_ret_value_ex(self, win_index, thread_id, rcx=0, rdx=0, r8=0, r9=0, lparam5=0, lparam6=0, is_main_thread=False):
        """
        测试通讯是否成功 (返回单一值，扩展版本)
        :param win_index: 窗口序号 (从1开始)
        :param thread_id: 当前线程ID或指定ID
        :param rcx, rdx, r8, r9, lparam5, lparam6: CALL参数
        :param is_main_thread: 是否在主线程调用
        :return: 操作结果（参考HD返回值表）
        备注：用于测试环境是否搭建成功
        """
        return self.dll.HCEnv_TestCALL_RetValueEx(win_index, thread_id, rcx, rdx, r8, r9, lparam5, lparam6, is_main_thread)
    
    def test_call_ret_array_ex(self, win_index, thread_id, rcx=0, rdx=0, r8=0, r9=0, lparam5=0, lparam6=0, is_main_thread=False):
        """
        测试通讯是否成功 (返回JSON字符串，扩展版本)
        :param win_index: 窗口序号 (从1开始)
        :param thread_id: 当前线程ID或指定ID
        :param rcx, rdx, r8, r9, lparam5, lparam6: CALL参数
        :param is_main_thread: 是否在主线程调用
        :return: 操作结果（参考HD返回值表）
        备注：用于测试环境是否搭建成功
        """
        return self.dll.HCEnv_TestCALL_RetArrayEx(win_index, thread_id, rcx, rdx, r8, r9, lparam5, lparam6, is_main_thread)
    
    def set_process_type(self, process_bits):
        """
        设置目标进程位数 (全局设置)
        :param process_bits: 进程位数 (32或64)
        :return: 操作结果（参考HD返回值表）
        备注：全局生效，设置后所有进程均为此位数，建议使用扩展版本
        """
        return self.dll.HCEnv_SetProcessType(process_bits)
    
    def set_process_type_ex(self, win_index, process_bits):
        """
        指定某个窗口序号绑定的进程位数
        :param win_index: 窗口序号
        :param process_bits: 进程位数 (32或64)
        :return: 操作结果（参考HD返回值表）
        备注：针对特定窗口序号设置进程位数
        """
        return self.dll.HCEnv_SetProcessTypeEx(win_index, process_bits)
    
    def set_handle_event_callback(self, fun_callback):
        """
        设置中控事件处理回调函数
        :param fun_callback: 事件处理函数
        :return: 操作结果（参考HD返回值表）
        备注：自定义模块通知中控时触发
        """
        # 定义回调函数类型
        HandleEventFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p)
        # 转换Python函数为C回调函数
        c_callback = HandleEventFunType(fun_callback)
        # 保存回调函数引用防止垃圾回收
        self.handle_event_callback = c_callback
        return self.dll.HCEnv_SetHandleEventCallBack(c_callback)
    
    def set_shutdown_callback(self, fun_callback):
        """
        设置关闭回调函数
        :param fun_callback: 关闭回调函数
        :return: 操作结果（参考HD返回值表）
        备注：HD功能失效时，中控关闭前触发
        """
        # 定义回调函数类型
        ShutDownEventFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32)
        # 转换Python函数为C回调函数
        c_callback = ShutDownEventFunType(fun_callback)
        # 保存回调函数引用防止垃圾回收
        self.shutdown_callback = c_callback
        return self.dll.HCEnv_SetShutDownCallBack(c_callback)
    
    def set_pid_check_back(self, fun_callback):
        """
        设置PID检查回调
        :param fun_callback: PID检查回调函数
        :return: 操作结果（参考HD返回值表）
        备注：内部检测到PID不存在时触发
        """
        # 定义回调函数类型
        CheckPluginFunType = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)
        # 转换Python函数为C回调函数
        c_callback = CheckPluginFunType(fun_callback)
        # 保存回调函数引用防止垃圾回收
        self.pid_check_callback = c_callback
        return self.dll.HCEnv_SetPidCheckBack(c_callback)
    
    def set_check_com_itl_time(self, interval=20):
        """
        设置通讯检测间隔毫秒
        :param interval: 通讯检测间隔毫秒
        :return: 操作结果（参考HD返回值表）
        备注：值越小响应越快但CPU占用越高
        """
        return self.dll.HCEnv_SetCheckComItlTime(interval)
    
    def set_check_callback_time(self, interval=5):
        """
        设置回调响应毫秒
        :param interval: 回调响应毫秒
        :return: 操作结果（参考HD返回值表）
        备注：值越小响应越快但CPU占用越高
        """
        return self.dll.HCEnv_SetCheckCallBackTime(interval)
    
    def terminate_thread(self, win_index, thread_id, use_lock=True):
        """
        强制结束当前线程
        :param win_index: 强制关闭线程所属的窗口序号
        :param thread_id: 需关闭的线程ID
        :param use_lock: 是否操作锁
        :return: 操作结果（参考HD返回值表）
        备注：谨慎使用，强制关闭可能导致不可预测的BUG
        """
        return self.dll.HCEnv_TerminateThread(win_index, thread_id, use_lock)
    
    def terminate_thread_ex(self, win_index, thread_handle, use_lock=True):
        """
        强制结束当前线程 (扩展版本，通过线程句柄操作)
        :param win_index: 强制关闭线程所属的窗口序号
        :param thread_handle: 需关闭的线程句柄
        :param use_lock: 是否操作锁
        :return: 操作结果（参考HD返回值表）
        备注：谨慎使用，强制关闭可能导致不可预测的BUG
        """
        return self.dll.HCEnv_TerminateThreadEx(win_index, thread_handle, use_lock)
    
    def protect_fun(self, fun_addr, offset, size):
        """
        添加安全函数 (保护指定函数片段)
        :param fun_addr: 函数地址
        :param offset: 基于函数地址的偏移量
        :param size: 保护字节数
        :return: 操作结果（参考HD返回值表）
        备注：调试版本无效，发布版本生效
        """
        return self.dll.HCEnv_ProtectFun(fun_addr, offset, size)


def create_hd_env(dll_path=None, is_debug=None):
    """
    创建HDEnv实例的工厂函数
    :param dll_path: DLL文件所在路径（可选，如果DLL已加载）
    :param is_debug: 是否使用调试版DLL（可选，如果DLL已加载）
    :return: HDEnv实例
    """
    return HDEnv(dll_path, is_debug)