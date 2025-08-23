import ctypes
import os
import sys

# 导入基础模块
from .base_module import HDModuleBase

class HDMT(HDModuleBase):
    """
    HD多线程模块
    负责处理多线程相关的功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化HDMT实例
        
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
        self.UIFunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p)
        self.FunType = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32)
        self.MsgFunType = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p)
        self.HCMTStatusFunType = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int64)
        
        # 初始化函数参数和返回值类型
        # 基础初始化函数
        self.dll.HCMT_InitProcess.argtypes = [ctypes.c_int64, ctypes.c_void_p, ctypes.c_void_p, 
                                             ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        self.dll.HCMT_InitProcess.restype = ctypes.c_int64
        
        self.dll.HCMT_InitProcessEx.argtypes = [ctypes.c_int64, ctypes.c_void_p, ctypes.c_void_p, 
                                               ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, 
                                               ctypes.c_void_p, ctypes.c_void_p]
        self.dll.HCMT_InitProcessEx.restype = ctypes.c_int64
        
        self.dll.HCMT_InitOperate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        self.dll.HCMT_InitOperate.restype = ctypes.c_int64
        
        # 消息处理函数
        self.dll.HCMT_RegisterMessage.argtypes = [ctypes.c_int32, ctypes.c_void_p]
        self.dll.HCMT_RegisterMessage.restype = ctypes.c_int64
        
        self.dll.HCMT_MsgSend.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p]
        self.dll.HCMT_MsgSend.restype = ctypes.c_int64
        
        self.dll.HCMT_MsgPost.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p]
        self.dll.HCMT_MsgPost.restype = ctypes.c_int64
        
        # 窗口操作函数
        self.dll.HCMT_MsgStart.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.dll.HCMT_MsgStart.restype = ctypes.c_int64
        
        self.dll.HCMT_MsgStop.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.dll.HCMT_MsgStop.restype = ctypes.c_int64
        
        self.dll.HCMT_MsgReStart.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.dll.HCMT_MsgReStart.restype = ctypes.c_int64
        
        self.dll.HCMT_MsgReStartEx.argtypes = [ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
        self.dll.HCMT_MsgReStartEx.restype = ctypes.c_int64
        
        self.dll.HCMT_Start.argtypes = [ctypes.c_int32]
        self.dll.HCMT_Start.restype = ctypes.c_int64
        
        # 状态管理函数
        self.dll.HCMT_GetState.argtypes = [ctypes.c_int32]
        self.dll.HCMT_GetState.restype = ctypes.c_int64
        
        self.dll.HCMT_GetStateString.argtypes = [ctypes.c_int32]
        self.dll.HCMT_GetStateString.restype = ctypes.c_char_p
        
        # 暂停/恢复/停止函数
        self.dll.HCMT_SetAllPause.argtypes = []
        self.dll.HCMT_SetAllPause.restype = ctypes.c_int64
        
        self.dll.HCMT_SetAllRecover.argtypes = []
        self.dll.HCMT_SetAllRecover.restype = ctypes.c_int64
        
        self.dll.HCMT_SetAllStop.argtypes = []
        self.dll.HCMT_SetAllStop.restype = ctypes.c_int64
        
        self.dll.HCMT_SetPause.argtypes = [ctypes.c_int32]
        self.dll.HCMT_SetPause.restype = ctypes.c_int64
        
        self.dll.HCMT_SetPauseEx.argtypes = [ctypes.c_int32]
        self.dll.HCMT_SetPauseEx.restype = ctypes.c_int64
        
        self.dll.HCMT_SetRecover.argtypes = [ctypes.c_int32]
        self.dll.HCMT_SetRecover.restype = ctypes.c_int64
        
        self.dll.HCMT_SetRecoverEx.argtypes = [ctypes.c_int32]
        self.dll.HCMT_SetRecoverEx.restype = ctypes.c_int64
        
        self.dll.HCMT_SetStop.argtypes = [ctypes.c_int32]
        self.dll.HCMT_SetStop.restype = ctypes.c_int64
        
        # 睡眠与运行检查函数
        self.dll.HCMT_IsRunning.argtypes = []
        self.dll.HCMT_IsRunning.restype = ctypes.c_int64
        
        self.dll.HCMT_Sleep.argtypes = [ctypes.c_int32]
        self.dll.HCMT_Sleep.restype = ctypes.c_int64
        
        self.dll.HCMT_SleepEx.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.dll.HCMT_SleepEx.restype = ctypes.c_int64
        
        # 多线程状态机函数
        self.dll.HCMT_StartStatus.argtypes = []
        self.dll.HCMT_StartStatus.restype = ctypes.c_int64
        
        self.dll.HCMT_AddStatus.argtypes = [ctypes.c_void_p, ctypes.c_int64, ctypes.c_bool, ctypes.c_int32]
        self.dll.HCMT_AddStatus.restype = ctypes.c_int64
        
        self.dll.HCMT_ChangeStatus.argtypes = [ctypes.c_int32]
        self.dll.HCMT_ChangeStatus.restype = ctypes.c_int64
        
        self.dll.HCMT_RetraceStatus.argtypes = [ctypes.c_bool]
        self.dll.HCMT_RetraceStatus.restype = ctypes.c_int64
        
        self.dll.HCMT_IsStatus.argtypes = []
        self.dll.HCMT_IsStatus.restype = ctypes.c_int64
        
        self.dll.HCMT_StatusSleep.argtypes = [ctypes.c_int32]
        self.dll.HCMT_StatusSleep.restype = ctypes.c_int64
    
    def init_process(self, hwnd, update_ui_callback=None, login_callback=None, 
                    first_callback=None, second_callback=None, end_callback=None, restart_pre_callback=None):
        """
        初始化多线程设置相关流程回调
        :param hwnd: 中控 UI 的窗口主句柄（内部会 HOOK 窗口过程）
        :param update_ui_callback: UIFUNTYPE UI 回调
        :param login_callback: FUNTYPE 登录回调（唯一锁，多窗口有序启动；返回≥1 正常，≤0/-1 登录失败结束，-2 登录失败内置重启）
        :param first_callback: FUNTYPE 第一执行回调（需循环配合 HCMT_Sleep () 和 HCMT_IsRunning ()，不主动返回）
        :param second_callback: FUNTYPE 第二执行回调（同第一执行回调）
        :param end_callback: FUNTYPE 结束回调
        :param restart_pre_callback: FUNTYPE 重启前回调
        :return: 操作结果（参考HD返回值表）
        """
        # 存储回调函数引用，防止被Python垃圾回收
        self.callbacks['update_ui'] = update_ui_callback
        self.callbacks['login'] = login_callback
        self.callbacks['first'] = first_callback
        self.callbacks['second'] = second_callback
        self.callbacks['end'] = end_callback
        self.callbacks['restart_pre'] = restart_pre_callback
        
        # 将Python函数转换为C回调函数
        c_update_ui_callback = self.UIFunType(update_ui_callback) if update_ui_callback else None
        c_login_callback = self.FunType(login_callback) if login_callback else None
        c_first_callback = self.FunType(first_callback) if first_callback else None
        c_second_callback = self.FunType(second_callback) if second_callback else None
        c_end_callback = self.FunType(end_callback) if end_callback else None
        c_restart_pre_callback = self.FunType(restart_pre_callback) if restart_pre_callback else None
        
        return self.dll.HCMT_InitProcess(hwnd, c_update_ui_callback, c_login_callback, 
                                        c_first_callback, c_second_callback, c_end_callback, c_restart_pre_callback)
    
    def init_process_ex(self, hwnd, update_ui_callback_ex=None, login_callback=None, 
                       first_callback=None, second_callback=None, end_callback=None, 
                       restart_pre_callback=None, lparam=None):
        """
        初始化多线程流程回调（可绑定全局参数）
        :param hwnd: 中控 UI 的窗口主句柄
        :param update_ui_callback_ex: UIFUNTYPEEX UI回调（可获取lparam参数）
        :param login_callback: FUNTYPE 登录回调
        :param first_callback: FUNTYPE 第一执行回调
        :param second_callback: FUNTYPE 第二执行回调
        :param end_callback: FUNTYPE 结束回调
        :param restart_pre_callback: FUNTYPE 重启前回调
        :param lparam: 绑定全局参数，一般为 UI 对象地址
        :return: 操作结果（参考HD返回值表）
        """
        # 存储回调函数引用
        self.callbacks['update_ui_ex'] = update_ui_callback_ex
        self.callbacks['login'] = login_callback
        self.callbacks['first'] = first_callback
        self.callbacks['second'] = second_callback
        self.callbacks['end'] = end_callback
        self.callbacks['restart_pre'] = restart_pre_callback
        self.callbacks['lparam'] = lparam
        
        # 将Python函数转换为C回调函数
        c_update_ui_callback_ex = self.UIFunType(update_ui_callback_ex) if update_ui_callback_ex else None
        c_login_callback = self.FunType(login_callback) if login_callback else None
        c_first_callback = self.FunType(first_callback) if first_callback else None
        c_second_callback = self.FunType(second_callback) if second_callback else None
        c_end_callback = self.FunType(end_callback) if end_callback else None
        c_restart_pre_callback = self.FunType(restart_pre_callback) if restart_pre_callback else None
        
        return self.dll.HCMT_InitProcessEx(hwnd, c_update_ui_callback_ex, c_login_callback, 
                                          c_first_callback, c_second_callback, c_end_callback, 
                                          c_restart_pre_callback, lparam)
    
    def init_operate(self, end_bind_callback=None, pause_bind_callback=None, recover_bind_callback=None):
        """
        初始化多线程结束/暂停/恢复状态的操作回调
        :param end_bind_callback: FUNTYPE 结束绑定回调（HCMT_SetStop/HCMT_SetAllStop 触发）
        :param pause_bind_callback: FUNTYPE 暂停绑定回调（HCMT_SetPause/HCMT_SetAllPause 触发）
        :param recover_bind_callback: FUNTYPE 恢复绑定回调（HCMT_SetRecover/HCMT_SetAllRecover 触发）
        :return: 操作结果（参考HD返回值表）
        """
        # 存储回调函数引用
        self.callbacks['end_bind'] = end_bind_callback
        self.callbacks['pause_bind'] = pause_bind_callback
        self.callbacks['recover_bind'] = recover_bind_callback
        
        # 将Python函数转换为C回调函数
        c_end_bind_callback = self.FunType(end_bind_callback) if end_bind_callback else None
        c_pause_bind_callback = self.FunType(pause_bind_callback) if pause_bind_callback else None
        c_recover_bind_callback = self.FunType(recover_bind_callback) if recover_bind_callback else None
        
        return self.dll.HCMT_InitOperate(c_end_bind_callback, c_pause_bind_callback, c_recover_bind_callback)
    
    def register_message(self, msg, msg_callback):
        """
        注册窗口消息
        :param msg: 自定义消息整数值（内部自动加 41123，如 msg=1→41124）
        :param msg_callback: MSGFUNTYPE 消息回调
        :return: 操作结果（参考HD返回值表）
        """
        # 存储回调函数引用
        self.callbacks[f'msg_{msg}'] = msg_callback
        
        # 将Python函数转换为C回调函数
        c_msg_callback = self.MsgFunType(msg_callback) if msg_callback else None
        
        return self.dll.HCMT_RegisterMessage(msg, c_msg_callback)
    
    def msg_send(self, msg, wparam=None, lparam=None):
        """
        发送消息（同步）
        :param msg: 注册的消息值（内部为 msg+41123）
        :param wparam: 自定义参数
        :param lparam: 自定义参数
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_MsgSend(msg, wparam, lparam)
    
    def msg_post(self, msg, wparam=None, lparam=None):
        """
        发送消息（异步）
        :param msg: 注册的消息值（内部为 msg+41123）
        :param wparam: 自定义参数
        :param lparam: 自定义参数
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_MsgPost(msg, wparam, lparam)
    
    def msg_start(self, windows_index, is_asyn=False):
        """
        通过消息开启窗口操作
        :param windows_index: 窗口序号
        :param is_asyn: 是否异步发送
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_MsgStart(windows_index, is_asyn)
    
    def msg_stop(self, windows_index, is_asyn=False):
        """
        通过消息停止窗口操作
        :param windows_index: 窗口序号
        :param is_asyn: 是否异步发送
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_MsgStop(windows_index, is_asyn)
    
    def msg_restart(self, windows_index, is_asyn=False):
        """
        通过消息重启窗口操作
        :param windows_index: 窗口序号
        :param is_asyn: 是否异步发送
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_MsgReStart(windows_index, is_asyn)
    
    def msg_restart_ex(self, windows_index, is_unload=True, is_recon=True, is_asyn=False):
        """
        通过消息重启窗口操作（Ex 版本支持卸载环境设置）
        :param windows_index: 窗口序号
        :param is_unload: 是否卸载环境
        :param is_recon: 卸载后是否重连
        :param is_asyn: 是否异步发送
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_MsgReStartEx(windows_index, is_unload, is_recon, is_asyn)
    
    def start(self, windows_index):
        """
        直接开启窗口操作
        :param windows_index: 窗口序号
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_Start(windows_index)
    
    def get_state(self, index):
        """
        获取主副序号对应的线程状态值
        :param index: 主副序号
        :return: 返回 1 为状态值，其他值参考返回值表
        """
        return self.dll.HCMT_GetState(index)
    
    def get_state_string(self, thread_state):
        """
        获取状态值对应的字符串
        :param thread_state: 状态值
        :return: 返回状态字符串
        """
        result = self.dll.HCMT_GetStateString(thread_state)
        # 将C字符串转换为Python字符串
        if result:
            return result.decode('utf-8')
        return ""
    
    def set_all_pause(self):
        """
        设置所有窗口暂停
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_SetAllPause()
    
    def set_all_recover(self):
        """
        设置所有窗口恢复
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_SetAllRecover()
    
    def set_all_stop(self):
        """
        设置所有窗口停止
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_SetAllStop()
    
    def set_pause(self, windows_index):
        """
        设置指定窗口线程暂停
        :param windows_index: 窗口序号
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_SetPause(windows_index)
    
    def set_pause_ex(self, index):
        """
        设置指定主副序号线程暂停
        :param index: 主副序号
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_SetPauseEx(index)
    
    def set_recover(self, windows_index):
        """
        设置指定窗口线程恢复
        :param windows_index: 窗口序号
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_SetRecover(windows_index)
    
    def set_recover_ex(self, index):
        """
        设置指定主副序号线程恢复
        :param index: 主副序号
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_SetRecoverEx(index)
    
    def set_stop(self, windows_index):
        """
        设置指定窗口线程停止
        :param windows_index: 窗口序号
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_SetStop(windows_index)
    
    def set_stop_ex(self, index):
        """
        设置指定主副序号线程停止
        :param index: 主副序号
        :return: 操作结果（参考HD返回值表）
        """
        # 注意：DLL中没有HCMT_SetStopEx函数，使用HCMT_SetStop代替
        return self.dll.HCMT_SetStop(index)
    
    def is_running(self):
        """
        检查当前线程是否结束（在第一/第二回调中调用）
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_IsRunning()
    
    def sleep(self, mis):
        """
        延迟函数（自带暂停/结束/恢复检查）
        :param mis: 毫秒
        :return: 1（正常）、2（线程结束）、3（线程暂停过）
        """
        return self.dll.HCMT_Sleep(mis)
    
    def sleep_ex(self, mis, is_status=False):
        """
        延迟函数（自带暂停/结束/恢复检查，支持状态机检查）
        :param mis: 毫秒
        :param is_status: 是否在状态机回调中调用
        :return: 1（正常）、2（线程结束）、3（线程暂停过）、4（状态改变）
        """
        return self.dll.HCMT_SleepEx(mis, is_status)
    
    def start_status(self):
        """
        开启状态机
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_StartStatus()
    
    def add_status(self, fun_callback=None, lparam=0, is_enable=True, status_type=-1):
        """
        添加状态机（绑定状态值与回调）
        :param fun_callback: 状态回调（HCMTStatusFunType类型）
        :param lparam: 额外参数（回调时传递）
        :param is_enable: 状态是否有效
        :param status_type: 自定义状态值（-1为无状态，值越大优先级越高）
        :return: 操作结果（参考HD返回值表）
        """
        # 存储回调函数引用
        self.callbacks[f'status_{status_type}'] = fun_callback
        
        # 将Python函数转换为C回调函数
        c_fun_callback = self.HCMTStatusFunType(fun_callback) if fun_callback else None
        
        return self.dll.HCMT_AddStatus(c_fun_callback, lparam, is_enable, status_type)
    
    def change_status(self, status_type):
        """
        改变状态机状态
        :param status_type: 自定义状态值
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_ChangeStatus(status_type)
    
    def retrace_status(self, is_clear=False):
        """
        回溯状态（清除栈缓存）
        :param is_clear: 是否清除所有栈缓存
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_RetraceStatus(is_clear)
    
    def is_status(self):
        """
        检查当前状态是否有效（在状态回调中调用）
        :return: 操作结果（参考HD返回值表）
        """
        return self.dll.HCMT_IsStatus()
    
    def status_sleep(self, mis):
        """
        状态机延迟函数（带状态检查）
        :param mis: 延迟毫秒
        :return: 1（正常）、2（线程结束）、3（暂停）、4（状态改变）
        """
        return self.dll.HCMT_StatusSleep(mis)


# 创建HDMT实例的工厂函数
def create_hd_mt(dll_path=None, is_debug=None):
    """
    创建HDMT实例的工厂函数
    :param dll_path: DLL文件所在路径，如果为None，则使用已通过DLL管理器初始化的DLL
    :param is_debug: 是否使用调试版DLL，如果为None，则使用已通过DLL管理器初始化的设置
    :return: HDMT实例
    """
    return HDMT(dll_path, is_debug)


# 定义回调函数的包装类，方便用户继承实现自己的回调逻辑
class HDMTCallback:
    """
    HD多线程模块回调函数的基类，用户可以继承此类并重写相应的方法
    """
    def __init__(self):
        # 空实现，用户可以在子类中重写
        pass
    
    def update_ui(self, windows_index, lparam):
        """
        UI回调函数
        :param windows_index: 窗口序号
        :param lparam: 自定义参数
        :return: 操作结果
        """
        return 0
    
    def login(self, windows_index):
        """
        登录回调函数
        :param windows_index: 窗口序号
        :return: 返回≥1 正常，≤0/-1 登录失败结束，-2 登录失败内置重启
        """
        return 1
    
    def first(self, windows_index):
        """
        第一执行回调函数
        :param windows_index: 窗口序号
        :return: 操作结果
        """
        return 0
    
    def second(self, windows_index):
        """
        第二执行回调函数
        :param windows_index: 窗口序号
        :return: 操作结果
        """
        return 0
    
    def end(self, windows_index):
        """
        结束回调函数
        :param windows_index: 窗口序号
        :return: 操作结果
        """
        return 0
    
    def restart_pre(self, windows_index):
        """
        重启前回调函数
        :param windows_index: 窗口序号
        :return: 操作结果
        """
        return 0
    
    def end_bind(self, index):
        """
        结束绑定回调函数
        :param index: ≥多开限制数为副序号，< 为住序号
        :return: 操作结果
        """
        return 0
    
    def pause_bind(self, index):
        """
        暂停绑定回调函数
        :param index: ≥多开限制数为副序号，< 为住序号
        :return: 操作结果
        """
        return 0
    
    def recover_bind(self, index):
        """
        恢复绑定回调函数
        :param index: ≥多开限制数为副序号，< 为住序号
        :return: 操作结果
        """
        return 0
    
    def message(self, msg, wparam, lparam):
        """
        消息回调函数
        :param msg: 消息ID
        :param wparam: 消息参数
        :param lparam: 消息参数
        :return: 操作结果
        """
        return 0
    
    def status(self, windows_index, lparam):
        """
        状态回调函数
        :param windows_index: 窗口序号
        :param lparam: 额外参数
        :return: 操作结果
        """
        return 0