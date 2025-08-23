#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD RPG引擎框架(GDK)智能识字模块(RC)Python封装
提供识别服务器管理、智能识字和CPU优化等功能
"""

import ctypes
from .base_module import HDModuleBase, HDModuleFactory


class HCRC(HDModuleBase):
    """HD RPG引擎框架智能识字模块(RC)的Python封装类"""
    
    def _initialize_functions(self):
        """初始化DLL函数绑定"""
        # 识别服务器管理函数
        self.HCRC_InitRCServer = self.dll.HCRC_InitRCServer
        self.HCRC_InitRCServer.argtypes = [ctypes.c_int32, ctypes.c_char_p]
        self.HCRC_InitRCServer.restype = ctypes.c_int64
        
        self.HCRC_OpenRCServer = self.dll.HCRC_OpenRCServer
        self.HCRC_OpenRCServer.argtypes = [ctypes.c_int32]
        self.HCRC_OpenRCServer.restype = ctypes.c_int64
        
        self.HCRC_StopRCServer = self.dll.HCRC_StopRCServer
        self.HCRC_StopRCServer.argtypes = [ctypes.c_int32]
        self.HCRC_StopRCServer.restype = ctypes.c_int64
        
        self.HCRC_SwitchRCServer = self.dll.HCRC_SwitchRCServer
        self.HCRC_SwitchRCServer.argtypes = [ctypes.c_int32, ctypes.c_char_p]
        self.HCRC_SwitchRCServer.restype = ctypes.c_int64
        
        # 智能识字函数 - 基础识字
        self.HCRC_RecognitionCharA = self.dll.HCRC_RecognitionCharA
        self.HCRC_RecognitionCharA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool]
        self.HCRC_RecognitionCharA.restype = ctypes.c_int64
        
        self.HCRC_RecognitionCharW = self.dll.HCRC_RecognitionCharW
        self.HCRC_RecognitionCharW.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool]
        self.HCRC_RecognitionCharW.restype = ctypes.c_int64
        
        # 智能识字函数 - 指定范围识字
        self.HCRC_RecognitionCharExA = self.dll.HCRC_RecognitionCharExA
        self.HCRC_RecognitionCharExA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool]
        self.HCRC_RecognitionCharExA.restype = ctypes.c_int64
        
        self.HCRC_RecognitionCharExW = self.dll.HCRC_RecognitionCharExW
        self.HCRC_RecognitionCharExW.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool]
        self.HCRC_RecognitionCharExW.restype = ctypes.c_int64
        
        # 智能识字函数 - 内存数据识字
        self.HCRC_RecognitionCharByMemoryA = self.dll.HCRC_RecognitionCharByMemoryA
        self.HCRC_RecognitionCharByMemoryA.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool]
        self.HCRC_RecognitionCharByMemoryA.restype = ctypes.c_int64
        
        self.HCRC_RecognitionCharByMemoryW = self.dll.HCRC_RecognitionCharByMemoryW
        self.HCRC_RecognitionCharByMemoryW.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool]
        self.HCRC_RecognitionCharByMemoryW.restype = ctypes.c_int64
        
        # CPU优化模块函数
        self.HC_OpenCPU = self.dll.HC_OpenCPU
        self.HC_OpenCPU.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.HC_OpenCPU.restype = ctypes.c_int64
        
        self.HC_CloseCPU = self.dll.HC_CloseCPU
        self.HC_CloseCPU.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.HC_CloseCPU.restype = ctypes.c_int64
        
        self.HC_SetFPS = self.dll.HC_SetFPS
        self.HC_SetFPS.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.HC_SetFPS.restype = ctypes.c_int64
        
        self.HC_SetCpuDwonMs = self.dll.HC_SetCpuDwonMs
        self.HC_SetCpuDwonMs.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.HC_SetCpuDwonMs.restype = ctypes.c_int64
    
    def init_rc_server(self, window_index, language_file):
        """
        初始化识别服务器，加载指定语言库
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            language_file (str): 全局语言路径中的语言库文件名
            
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        return self.HCRC_InitRCServer(window_index, language_file.encode('utf-8'))
        
    def open_rc_server(self, window_index):
        """
        打开已初始化的识别服务器
        
        参数:
            window_index (int): 窗口序号（从1开始）
            
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        return self.HCRC_OpenRCServer(window_index)
        
    def stop_rc_server(self, window_index):
        """
        停止当前识别服务器
        
        参数:
            window_index (int): 窗口序号（从1开始）
            
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        return self.HCRC_StopRCServer(window_index)
        
    def switch_rc_server(self, window_index, language_file):
        """
        切换语言库（内部自动停止、重新初始化并打开服务器）
        
        参数:
            window_index (int): 目标窗口序号
            language_file (str): 新语言库文件名
            
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        return self.HCRC_SwitchRCServer(window_index, language_file.encode('utf-8'))
        
    def recognition_char(self, window_index, image_name, threshold=127, confidence=80, use_gray=True, show_viewer=False, is_wide_char=False):
        """
        从图片中识别文字
        
        参数:
            window_index (int): 窗口序号
            image_name (str): 待识别图片路径（支持绝对/相对路径）
            threshold (int, optional): 二值化阈值（0-255，默认127）
            confidence (int, optional): 置信度（0-100，默认80）
            use_gray (bool, optional): 是否开启灰度图（默认True）
            show_viewer (bool, optional): 是否打开查看器（默认False）
            is_wide_char (bool, optional): 是否使用宽字符版本（默认False）
            
        返回值:
            int: 操作结果，返回JSON格式数据，具体参考API文档
        """
        if is_wide_char:
            return self.HCRC_RecognitionCharW(window_index, image_name, threshold, confidence, use_gray, show_viewer)
        else:
            return self.HCRC_RecognitionCharA(window_index, image_name.encode('utf-8'), threshold, confidence, use_gray, show_viewer)
        
    def recognition_char_ex(self, window_index, image_name, x1=-1, y1=-1, x2=-1, y2=-1, threshold=127, confidence=80, use_gray=True, show_viewer=False, is_wide_char=False):
        """
        在图片的指定矩形范围内识别文字
        
        参数:
            window_index (int): 窗口序号
            image_name (str): 待识别图片路径
            x1, y1, x2, y2 (int, optional): 识别范围的坐标（默认-1表示全图）
            threshold (int, optional): 二值化阈值
            confidence (int, optional): 置信度
            use_gray (bool, optional): 是否开启灰度图
            show_viewer (bool, optional): 是否打开查看器
            is_wide_char (bool, optional): 是否使用宽字符版本
            
        返回值:
            int: 操作结果，返回JSON格式数据，具体参考API文档
        """
        if is_wide_char:
            return self.HCRC_RecognitionCharExW(window_index, image_name, x1, y1, x2, y2, threshold, confidence, use_gray, show_viewer)
        else:
            return self.HCRC_RecognitionCharExA(window_index, image_name.encode('utf-8'), x1, y1, x2, y2, threshold, confidence, use_gray, show_viewer)
        
    def recognition_char_by_memory(self, window_index, p_data, width, height, x1=-1, y1=-1, x2=-1, y2=-1, threshold=127, confidence=80, use_gray=True, show_viewer=False, is_wide_char=False):
        """
        从内存中的图片数据（MYA8R8G8B8格式）识别文字
        
        参数:
            window_index (int): 窗口序号
            p_data (int): 内存图片数据首地址
            width (int): 图片宽度
            height (int): 图片高度
            x1, y1, x2, y2 (int, optional): 识别范围的坐标
            threshold (int, optional): 二值化阈值
            confidence (int, optional): 置信度
            use_gray (bool, optional): 是否开启灰度图
            show_viewer (bool, optional): 是否打开查看器
            is_wide_char (bool, optional): 是否使用宽字符版本
            
        返回值:
            int: 操作结果，返回JSON格式数据，具体参考API文档
        """
        if is_wide_char:
            return self.HCRC_RecognitionCharByMemoryW(window_index, p_data, width, height, x1, y1, x2, y2, threshold, confidence, use_gray, show_viewer)
        else:
            return self.HCRC_RecognitionCharByMemoryA(window_index, p_data, width, height, x1, y1, x2, y2, threshold, confidence, use_gray, show_viewer)
        
    def open_cpu(self, window_index, is_main_thread=False):
        """
        开启CPU优化功能
        
        参数:
            window_index (int): 目标窗口序号
            is_main_thread (bool, optional): 是否由主线程执行（默认False）
            
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        return self.HC_OpenCPU(window_index, is_main_thread)
        
    def close_cpu(self, window_index, is_main_thread=False):
        """
        关闭CPU优化功能
        
        参数:
            window_index (int): 目标窗口序号
            is_main_thread (bool, optional): 是否由主线程执行
            
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        return self.HC_CloseCPU(window_index, is_main_thread)
        
    def set_fps(self, window_index, fps=0):
        """
        设置帧数（用于动态优化CPU消耗，绑定后台属性有效）
        
        参数:
            window_index (int): 目标窗口序号
            fps (int, optional): 帧数（>120表示关闭优化，默认0）
            
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
            
        备注:
            非实际帧数，仅作为优化参考，默认30；挂接主线程时会动态调整检查频率
        """
        return self.HC_SetFPS(window_index, fps)
        
    def set_cpu_down_ms(self, window_index, down_ms=0):
        """
        设置延迟时间（用于调节CPU消耗，绑定后台属性有效）
        
        参数:
            window_index (int): 目标窗口序号
            down_ms (int, optional): 延迟毫秒数（1-50ms为宜，默认0）
            
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
            
        备注:
            挂接主线程时会动态调整检查频率
        """
        return self.HC_SetCpuDwonMs(window_index, down_ms)


# 创建工厂函数
def create_rc(dll_path=None, is_debug=None):
    """
    创建智能识字模块(RC)实例的工厂函数
    
    参数:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    返回值:
        HCRC: 智能识字模块实例
    """
    return HDModuleFactory.create_instance(HCRC, dll_path, is_debug)


# 模块导出
export_dict = {
    'HCRC': HCRC,
    'create_rc': create_rc
}

__all__ = list(export_dict.keys())

# 将导出的对象添加到模块的全局命名空间
globals().update(export_dict)