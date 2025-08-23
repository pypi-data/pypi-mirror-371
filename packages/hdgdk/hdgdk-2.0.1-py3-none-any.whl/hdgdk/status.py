#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 状态机模块封装
提供状态流转与任务执行管理功能，包含状态机控制器、状态机和状态任务三个子模块
"""

import ctypes
from typing import Optional, Callable, Any

from .base_module import HDModuleBase, HDModuleFactory


# 定义回调函数类型
try:
    # 状态回调函数类型
    hdstatus_fun_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p)  # void(*)(HDStatus *pHCStatus)
    # 状态任务回调函数类型
    hdstatustask_fun_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)  # void(*)(HDStatus *pHCStatus, HDStatusTask *pHCStatusTask)
except Exception:
    # 定义为None，避免类型错误
    hdstatus_fun_type = None
    hdstatustask_fun_type = None


class HDStatusModule(HDModuleBase):
    """
    HD GDK 状态机模块
    封装状态机控制器、状态机和状态任务的主要功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化状态机模块
        
        Args:
            dll_path (str, optional): DLL文件路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 获取控制器实例函数
        self._get_hdstatus_controller = self.dll.HCHD_GetHDStatusControler
        self._get_hdstatus_controller.argtypes = []
        self._get_hdstatus_controller.restype = ctypes.c_void_p
        
        # 缓存控制器实例
        self._controller_instance = None
    
    def get_controller(self):
        """
        获取状态机控制器的唯一单例对象
        
        Returns:
            int: 控制器单例对象地址
        """
        if self._controller_instance is None:
            self._controller_instance = self._get_hdstatus_controller()
        return self._controller_instance
    
    def builder_lparam(self, size):
        """
        申请内存构建参数（用于状态机任务传递）
        
        Args:
            size (int): 要申请的内存大小
        
        Returns:
            int: 申请的内存地址
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            # 获取BuilderLparam方法地址
            builder_lparam_func = ctypes.cast(
                ctypes.c_void_p(controller + 0x18),  # 假设偏移量为0x18，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_int32)
            )
            
            # 调用方法
            return builder_lparam_func(size)
        except Exception as e:
            raise Exception(f"构建参数失败: {str(e)}")
    
    def add_status(self, window_index):
        """
        为指定窗口序号（index）添加状态机，返回状态机实例
        
        Args:
            window_index (int): 窗口序号
        
        Returns:
            int: 状态机实例地址
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            # 获取AddStatus方法地址
            add_status_func = ctypes.cast(
                ctypes.c_void_p(controller + 0x20),  # 假设偏移量为0x20，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_int32)
            )
            
            # 调用方法
            return add_status_func(window_index)
        except Exception as e:
            raise Exception(f"添加状态机失败: {str(e)}")
    
    def get_status(self, window_index):
        """
        根据窗口序号获取状态机实例
        
        Args:
            window_index (int): 窗口序号
        
        Returns:
            int: 状态机实例地址
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            # 获取GetStatus方法地址
            get_status_func = ctypes.cast(
                ctypes.c_void_p(controller + 0x28),  # 假设偏移量为0x28，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_int32)
            )
            
            # 调用方法
            return get_status_func(window_index)
        except Exception as e:
            raise Exception(f"获取状态机实例失败: {str(e)}")
    
    def start_status(self, begin_index, end_index=None):
        """
        启动窗口序号范围（beginIndex到endIndex）内的状态机（已启动的不会重复启动）
        或启动指定窗口序号的状态机
        
        Args:
            begin_index (int): 起始窗口序号或单个窗口序号
            end_index (int, optional): 结束窗口序号
        
        Returns:
            int: 操作结果
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            if end_index is None:
                # 启动单个窗口的状态机
                start_status_func = ctypes.cast(
                    ctypes.c_void_p(controller + 0x38),  # 假设偏移量为0x38，实际需根据DLL更新
                    ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32)
                )
                return start_status_func(begin_index)
            else:
                # 启动窗口序号范围内的状态机
                start_status_range_func = ctypes.cast(
                    ctypes.c_void_p(controller + 0x30),  # 假设偏移量为0x30，实际需根据DLL更新
                    ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32)
                )
                return start_status_range_func(begin_index, end_index)
        except Exception as e:
            raise Exception(f"启动状态机失败: {str(e)}")
    
    def pause_status(self, window_index):
        """
        暂停指定窗口序号的状态机
        
        Args:
            window_index (int): 窗口序号
        
        Returns:
            int: 操作结果
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            # 获取PauseStatus方法地址
            pause_status_func = ctypes.cast(
                ctypes.c_void_p(controller + 0x48),  # 假设偏移量为0x48，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32)
            )
            
            # 调用方法
            return pause_status_func(window_index)
        except Exception as e:
            raise Exception(f"暂停状态机失败: {str(e)}")
    
    def recover_status(self, window_index):
        """
        恢复指定窗口序号的状态机
        
        Args:
            window_index (int): 窗口序号
        
        Returns:
            int: 操作结果
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            # 获取RecoverStatus方法地址
            recover_status_func = ctypes.cast(
                ctypes.c_void_p(controller + 0x50),  # 假设偏移量为0x50，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32)
            )
            
            # 调用方法
            return recover_status_func(window_index)
        except Exception as e:
            raise Exception(f"恢复状态机失败: {str(e)}")
    
    def end_status(self, window_index):
        """
        结束指定窗口序号的状态机（会阻塞等待结束）
        
        Args:
            window_index (int): 窗口序号
        
        Returns:
            int: 操作结果
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            # 获取EndStatus方法地址
            end_status_func = ctypes.cast(
                ctypes.c_void_p(controller + 0x58),  # 假设偏移量为0x58，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32)
            )
            
            # 调用方法
            return end_status_func(window_index)
        except Exception as e:
            raise Exception(f"结束状态机失败: {str(e)}")
    
    def attach_status_copy(self, window_index, status_instance):
        """
        将状态机附加到指定窗口，拷贝参数（同窗口序号直接返回原实例）
        
        Args:
            window_index (int): 窗口序号
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 操作结果
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            # 获取AttachStatusCopy方法地址
            attach_status_copy_func = ctypes.cast(
                ctypes.c_void_p(controller + 0x40),  # 假设偏移量为0x40，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_void_p)
            )
            
            # 调用方法
            return attach_status_copy_func(window_index, status_instance)
        except Exception as e:
            raise Exception(f"附加状态机失败: {str(e)}")
    
    def attach_status_copy_all(self, status_instance):
        """
        将状态机附加到所有窗口，拷贝参数
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 操作结果
        """
        try:
            # 获取控制器实例
            controller = self.get_controller()
            if not controller:
                raise Exception("无法获取状态机控制器实例")
            
            # 获取AttachStatusCopyAll方法地址
            attach_status_copy_all_func = ctypes.cast(
                ctypes.c_void_p(controller + 0x48),  # 假设偏移量为0x48，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_void_p)
            )
            
            # 调用方法
            return attach_status_copy_all_func(status_instance)
        except Exception as e:
            raise Exception(f"附加状态机到所有窗口失败: {str(e)}")
    
    # 状态机实例相关方法
    def status_start(self, status_instance):
        """
        启动状态机
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 操作结果
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取Start方法地址
            status_start_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x18),  # 假设偏移量为0x18，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64)
            )
            
            # 调用方法
            return status_start_func()
        except Exception as e:
            raise Exception(f"启动状态机实例失败: {str(e)}")
    
    def status_end(self, status_instance):
        """
        结束状态机（阻塞等待完成）
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 操作结果
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取End方法地址
            status_end_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x20),  # 假设偏移量为0x20，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64)
            )
            
            # 调用方法
            return status_end_func()
        except Exception as e:
            raise Exception(f"结束状态机实例失败: {str(e)}")
    
    def status_switch_status(self, status_instance, status_type):
        """
        切换状态机至指定类型（type为状态标识）
        
        Args:
            status_instance (int): 状态机实例地址
            status_type (int): 状态类型
        
        Returns:
            int: 操作结果
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取SwitchStatus方法地址
            status_switch_status_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x28),  # 假设偏移量为0x28，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32)
            )
            
            # 调用方法
            return status_switch_status_func(status_type)
        except Exception as e:
            raise Exception(f"切换状态失败: {str(e)}")
    
    def status_is_start(self, status_instance):
        """
        判断状态机是否已启动
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 1表示已启动，0表示未启动
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取IsStart方法地址
            status_is_start_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x30),  # 假设偏移量为0x30，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int32)
            )
            
            # 调用方法
            return status_is_start_func()
        except Exception as e:
            raise Exception(f"检查状态机是否启动失败: {str(e)}")
    
    def status_is_end(self, status_instance):
        """
        判断状态机是否已结束
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 1表示已结束，0表示未结束
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取IsEnd方法地址
            status_is_end_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x38),  # 假设偏移量为0x38，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int32)
            )
            
            # 调用方法
            return status_is_end_func()
        except Exception as e:
            raise Exception(f"检查状态机是否结束失败: {str(e)}")
    
    def status_is_running(self, status_instance):
        """
        判断状态机是否正在运行（轮询+状态流转中）
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 1表示正在运行，0表示未运行
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取IsRunning方法地址
            status_is_running_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x40),  # 假设偏移量为0x40，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int32)
            )
            
            # 调用方法
            return status_is_running_func()
        except Exception as e:
            raise Exception(f"检查状态机是否运行失败: {str(e)}")
    
    def status_is_pause(self, status_instance):
        """
        判断状态机是否处于暂停状态
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 1表示暂停，0表示未暂停
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取IsPause方法地址
            status_is_pause_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x48),  # 假设偏移量为0x48，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int32)
            )
            
            # 调用方法
            return status_is_pause_func()
        except Exception as e:
            raise Exception(f"检查状态机是否暂停失败: {str(e)}")
    
    def status_get_cur_type(self, status_instance):
        """
        获取当前状态类型
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 当前状态类型
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取GetCurType方法地址
            status_get_cur_type_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x50),  # 假设偏移量为0x50，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int32)
            )
            
            # 调用方法
            return status_get_cur_type_func()
        except Exception as e:
            raise Exception(f"获取当前状态类型失败: {str(e)}")
    
    def status_get_index(self, status_instance):
        """
        获取绑定的窗口序号
        
        Args:
            status_instance (int): 状态机实例地址
        
        Returns:
            int: 窗口序号
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            
            # 获取GetIndex方法地址
            status_get_index_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x58),  # 假设偏移量为0x58，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int32)
            )
            
            # 调用方法
            return status_get_index_func()
        except Exception as e:
            raise Exception(f"获取窗口序号失败: {str(e)}")
    
    def status_add_status(self, status_instance, status_type, callback):
        """
        为指定状态类型（type）添加状态回调函数（call）
        
        Args:
            status_instance (int): 状态机实例地址
            status_type (int): 状态类型
            callback (callable): 状态回调函数
        
        Returns:
            int: 操作结果
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            if not callable(callback):
                raise Exception("回调函数必须是可调用的")
            
            # 获取AddStatus方法地址
            status_add_status_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x60),  # 假设偏移量为0x60，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_void_p)
            )
            
            # 转换Python回调函数为C函数指针
            c_callback = hdstatus_fun_type(callback)
            
            # 调用方法
            result = status_add_status_func(status_type, c_callback)
            
            # 注意：这里需要保持对c_callback的引用，防止被Python垃圾回收
            # 可以考虑在实例中保存这些回调函数的引用
            if not hasattr(self, '_status_callbacks'):
                self._status_callbacks = []
            self._status_callbacks.append((status_instance, status_type, c_callback))
            
            return result
        except Exception as e:
            raise Exception(f"添加状态回调失败: {str(e)}")
    
    def status_add_status_task(self, status_instance, status_type, callback, lparam=None):
        """
        为指定状态类型添加任务回调函数（call）及参数（lparam），支持覆盖已有任务
        
        Args:
            status_instance (int): 状态机实例地址
            status_type (int): 状态类型
            callback (callable): 状态任务回调函数
            lparam (int, optional): 任务参数地址
        
        Returns:
            int: 操作结果
        """
        try:
            if not status_instance:
                raise Exception("无效的状态机实例")
            if not callable(callback):
                raise Exception("回调函数必须是可调用的")
            
            # 获取AddStatusTask方法地址
            status_add_status_task_func = ctypes.cast(
                ctypes.c_void_p(status_instance + 0x68),  # 假设偏移量为0x68，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p)
            )
            
            # 转换Python回调函数为C函数指针
            c_callback = hdstatustask_fun_type(callback)
            
            # 调用方法
            result = status_add_status_task_func(status_type, c_callback, lparam or 0)
            
            # 注意：这里需要保持对c_callback的引用，防止被Python垃圾回收
            if not hasattr(self, '_task_callbacks'):
                self._task_callbacks = []
            self._task_callbacks.append((status_instance, status_type, c_callback))
            
            return result
        except Exception as e:
            raise Exception(f"添加状态任务失败: {str(e)}")
    
    # 状态任务相关方法
    def task_pause_listener(self, task_instance):
        """
        暂停任务监听（进入循环等待状态）
        
        Args:
            task_instance (int): 状态任务实例地址
        
        Returns:
            bool: 操作结果，True表示成功，False表示失败
        """
        try:
            if not task_instance:
                raise Exception("无效的状态任务实例")
            
            # 获取PauseListener方法地址
            task_pause_listener_func = ctypes.cast(
                ctypes.c_void_p(task_instance + 0x18),  # 假设偏移量为0x18，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_bool)
            )
            
            # 调用方法
            return bool(task_pause_listener_func())
        except Exception as e:
            raise Exception(f"暂停任务监听失败: {str(e)}")
    
    def task_is_stop(self, task_instance):
        """
        检查任务状态是否不一致（不一致则停止任务）
        
        Args:
            task_instance (int): 状态任务实例地址
        
        Returns:
            bool: 操作结果，True表示不一致，False表示一致
        """
        try:
            if not task_instance:
                raise Exception("无效的状态任务实例")
            
            # 获取IsStop方法地址
            task_is_stop_func = ctypes.cast(
                ctypes.c_void_p(task_instance + 0x20),  # 假设偏移量为0x20，实际需根据DLL更新
                ctypes.CFUNCTYPE(ctypes.c_bool)
            )
            
            # 调用方法
            return bool(task_is_stop_func())
        except Exception as e:
            raise Exception(f"检查任务状态失败: {str(e)}")


# 工厂函数
def create_hd_status(dll_path=None, is_debug=None):
    """
    创建状态机模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDStatusModule: 状态机模块实例
    """
    return HDModuleFactory.create_instance(HDStatusModule, dll_path, is_debug)


# 定义常用的状态类型常量
class STATUS_TYPE:
    """状态类型常量"""
    # 可以根据实际需求定义常用的状态类型
    IDLE = 0  # 空闲状态
    RUNNING = 1  # 运行状态
    PAUSED = 2  # 暂停状态
    ERROR = 3  # 错误状态


# 定义默认的回调函数示例
def default_status_callback(status_instance):
    """默认的状态回调函数示例
    
    Args:
        status_instance (int): 状态机实例地址
    """
    print(f"状态回调被调用，状态机实例地址: 0x{status_instance:x}")

def default_task_callback(status_instance, task_instance):
    """默认的状态任务回调函数示例
    
    Args:
        status_instance (int): 状态机实例地址
        task_instance (int): 状态任务实例地址
    """
    print(f"任务回调被调用，状态机实例地址: 0x{status_instance:x}, 任务实例地址: 0x{task_instance:x}")