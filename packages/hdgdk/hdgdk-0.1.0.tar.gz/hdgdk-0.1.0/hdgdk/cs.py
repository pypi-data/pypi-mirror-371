#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD GDK 后台截图模块(CS)
提供后台及前台截图功能，支持多种渲染API和游戏引擎
"""

import ctypes
import json
from typing import Dict, Any, Optional, Tuple, Union

from .base_module import HDModuleBase


class HCCS(HDModuleBase):
    """
    HD GDK 后台截图模块类
    提供后台及前台截图功能，支持多种渲染API和游戏引擎
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化后台截图模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
    
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 截图模式与初始化函数
        self.HCCS_SetType = self.dll.HCCS_SetType
        self.HCCS_SetType.argtypes = [ctypes.c_int32]
        self.HCCS_SetType.restype = ctypes.c_int64
        
        self.HCCS_OpenCS = self.dll.HCCS_OpenCS
        self.HCCS_OpenCS.argtypes = [ctypes.c_int32]
        self.HCCS_OpenCS.restype = ctypes.c_int64
        
        self.HCCS_OpenCSEx = self.dll.HCCS_OpenCSEx
        self.HCCS_OpenCSEx.argtypes = [ctypes.c_int32, ctypes.c_bool, ctypes.c_int32, ctypes.c_int64]
        self.HCCS_OpenCSEx.restype = ctypes.c_int64
        
        self.HCCS_CloseCS = self.dll.HCCS_CloseCS
        self.HCCS_CloseCS.argtypes = [ctypes.c_int32]
        self.HCCS_CloseCS.restype = ctypes.c_int64
        
        self.HCCS_CloseCSEx = self.dll.HCCS_CloseCSEx
        self.HCCS_CloseCSEx.argtypes = [ctypes.c_int32]
        self.HCCS_CloseCSEx.restype = ctypes.c_int64
        
        # 截图数据获取与处理
        self.HCCS_GetCSData = self.dll.HCCS_GetCSData
        self.HCCS_GetCSData.argtypes = [ctypes.c_int32]
        self.HCCS_GetCSData.restype = ctypes.c_int64
        
        self.HCCS_CaptureBmp = self.dll.HCCS_CaptureBmp
        self.HCCS_CaptureBmp.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.HCCS_CaptureBmp.restype = ctypes.c_int64
        
        self.HCCS_GetCaptureBmpData = self.dll.HCCS_GetCaptureBmpData
        self.HCCS_GetCaptureBmpData.argtypes = [ctypes.c_int32]
        self.HCCS_GetCaptureBmpData.restype = ctypes.c_int64
        
        self.HCCS_GetCaptureBmpRangeData = self.dll.HCCS_GetCaptureBmpRangeData
        self.HCCS_GetCaptureBmpRangeData.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, 
                                                   ctypes.c_int32, ctypes.c_int32]
        self.HCCS_GetCaptureBmpRangeData.restype = ctypes.c_int64
        
        # 查看器控制
        self.HCCS_OpenCSFinder = self.dll.HCCS_OpenCSFinder
        self.HCCS_OpenCSFinder.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, 
                                          ctypes.c_int32, ctypes.c_int32]
        self.HCCS_OpenCSFinder.restype = ctypes.c_int64
        
        self.HCCS_CloseCSFinder = self.dll.HCCS_CloseCSFinder
        self.HCCS_CloseCSFinder.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.HCCS_CloseCSFinder.restype = ctypes.c_int64
        
        # 内存管理与容错
        self.HCCS_FreeArray = self.dll.HCCS_FreeArray
        self.HCCS_FreeArray.argtypes = [ctypes.c_void_p]
        self.HCCS_FreeArray.restype = ctypes.c_int64
        
        self.HCCS_FreeMemPool = self.dll.HCCS_FreeMemPool
        self.HCCS_FreeMemPool.argtypes = [ctypes.c_int32, ctypes.c_void_p]
        self.HCCS_FreeMemPool.restype = ctypes.c_int64
        
        self.HCCS_IsCaptureValid = self.dll.HCCS_IsCaptureValid
        self.HCCS_IsCaptureValid.argtypes = [ctypes.c_int64]
        self.HCCS_IsCaptureValid.restype = ctypes.c_int64
    
    def set_type(self, type_value: int = 0) -> int:
        """
        设置截图识别模式（普通/高频）
        
        Args:
            type_value: 0/-1（普通识别模式，默认）；1（高频后台截图模式）
        
        Returns:
            int: 当前是否开启高频模式
        """
        return self.HCCS_SetType(type_value)
    
    def open_cs(self, window_index: int) -> int:
        """
        基础打开截图功能
        
        Args:
            window_index: 窗口序号（从1开始）
        
        Returns:
            int: 操作结果
        """
        return self.HCCS_OpenCS(window_index)
    
    def open_cs_ex(self, window_index: int, is_normal: bool = True, 
                  cap_type: int = 0, hwnd: int = 0) -> int:
        """
        扩展打开截图，支持指定截图模式和窗口句柄
        
        Args:
            window_index: 0表示全屏前台截图（其他参数无效），1+表示窗口截图
            is_normal: 是否启用通常模式（默认TRUE）
            cap_type: 截图模式（CAPTURETYPE枚举）
            hwnd: 目标窗口句柄
        
        Returns:
            int: 操作结果
        """
        return self.HCCS_OpenCSEx(window_index, is_normal, cap_type, hwnd)
    
    def close_cs(self, window_index: int) -> int:
        """
        关闭截图（对应open_cs）
        
        Args:
            window_index: 窗口序号（0表示全屏截图）
        
        Returns:
            int: 操作结果
        """
        return self.HCCS_CloseCS(window_index)
    
    def close_cs_ex(self, window_index: int) -> int:
        """
        关闭截图（对应open_cs_ex）
        
        Args:
            window_index: 窗口序号（0表示全屏截图）
        
        Returns:
            int: 操作结果
        """
        return self.HCCS_CloseCSEx(window_index)
    
    def get_cs_data(self, window_index: int) -> Dict[str, Any]:
        """
        获取截图的原始像素数据（MYA8R8G8B8格式）
        
        Args:
            window_index: 窗口序号
        
        Returns:
            Dict: 包含error、ret等信息的字典，其中ret包含bRet、addr、eleSize、len、w、h等
        """
        result = self.HCCS_GetCSData(window_index)
        return self._parse_json_result(result)
    
    def capture_bmp(self, window_index: int, bmp_path: str, open_after: bool = False) -> Dict[str, Any]:
        """
        将截图数据保存为BMP文件
        
        Args:
            window_index: -1/0表示全局前台截图（需开启前台截图）
            bmp_path: 包含文件名的完整路径
            open_after: 保存后是否打开图片查看
        
        Returns:
            Dict: 包含宽度（w）和高度（h）的字典
        """
        # 转换Python字符串为C字符串
        c_bmp_path = ctypes.c_char_p(bmp_path.encode('utf-8'))
        result = self.HCCS_CaptureBmp(window_index, c_bmp_path, open_after)
        return self._parse_json_result(result)
    
    def get_capture_bmp_data(self, window_index: int) -> Dict[str, Any]:
        """
        获取当前截图的BMP格式数据（含文件头）
        
        Args:
            window_index: 窗口序号
        
        Returns:
            Dict: 包含error、ret等信息的字典，其中ret包含bRet、addr、eleSize、allLen、w、h等
        """
        result = self.HCCS_GetCaptureBmpData(window_index)
        return self._parse_json_result(result)
    
    def get_capture_bmp_range_data(self, window_index: int, x: int = -1, y: int = -1, 
                                  width: int = -1, height: int = -1) -> Dict[str, Any]:
        """
        获取指定范围的BMP数据
        
        Args:
            window_index: 窗口序号
            x: 范围左上角X坐标（-1表示0）
            y: 范围左上角Y坐标（-1表示0）
            width: 范围宽度（-1表示最大）
            height: 范围高度（-1表示最大）
        
        Returns:
            Dict: 包含error、ret等信息的字典
        """
        result = self.HCCS_GetCaptureBmpRangeData(window_index, x, y, width, height)
        return self._parse_json_result(result)
    
    def open_cs_finder(self, window_index: int, x: int, y: int, width: int, height: int) -> int:
        """
        打开截图查看器
        
        Args:
            window_index: 窗口序号
            x: 查看器显示位置X坐标
            y: 查看器显示位置Y坐标
            width: 查看器宽度
            height: 查看器高度
        
        Returns:
            int: 操作结果
        """
        return self.HCCS_OpenCSFinder(window_index, x, y, width, height)
    
    def close_cs_finder(self, window_index: int, pid: int) -> int:
        """
        关闭截图查看器
        
        Args:
            window_index: 窗口序号
            pid: 查看器进程ID
        
        Returns:
            int: 操作结果
        """
        return self.HCCS_CloseCSFinder(window_index, pid)
    
    def free_array(self, addr: int) -> int:
        """
        释放new[]申请的内存
        
        Args:
            addr: 内存地址
        
        Returns:
            int: 操作结果
        """
        return self.HCCS_FreeArray(ctypes.c_void_p(addr))
    
    def free_mem_pool(self, window_index: int, addr: int) -> int:
        """
        释放内存池申请的内存（截图数据专用）
        
        Args:
            window_index: 窗口序号（需与申请时一致）
            addr: 内存地址
        
        Returns:
            int: 操作结果
        """
        return self.HCCS_FreeMemPool(window_index, ctypes.c_void_p(addr))
    
    def is_capture_valid(self, ret_value: int) -> int:
        """
        判断截图数据是否获取失败
        
        Args:
            ret_value: 截图相关接口的返回值
        
        Returns:
            int: 1表示截图数据获取失败（需重新调用识别接口）；0表示识别未找到（非截图问题）
        """
        return self.HCCS_IsCaptureValid(ret_value)
    
    def _parse_json_result(self, result_ptr: int) -> Dict[str, Any]:
        """
        解析DLL返回的JSON字符串结果
        
        Args:
            result_ptr: 指向JSON字符串的指针
        
        Returns:
            Dict: 解析后的JSON字典
        """
        if not result_ptr:
            return {"error": -1, "message": "结果指针为空"}
        
        try:
            # 将指针转换为Python字符串
            result_str = ctypes.string_at(ctypes.c_void_p(result_ptr)).decode('utf-8')
            # 解析JSON
            result_dict = json.loads(result_str)
            return result_dict
        except Exception as e:
            return {"error": -1, "message": f"解析结果失败: {str(e)}"}


# 工厂函数
def create_hd_cs(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HCCS:
    """
    创建后台截图模块实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HCCS: 后台截图模块实例
    """
    return HCCS(dll_path, is_debug)


# 定义常用的截图模式常量
class CAPTURETYPE:
    """\截图模式枚举"""
    # D3D9 - 32位
    D3D9_1_x86 = 1  # UE引擎
    D3D9_2_x86 = 2  # U3D引擎
    D3D9_3_x86 = 3  # RGBX通用
    D3D9_Steam_x86 = 4  # Steam游戏
    
    # D3D9 - 64位
    D3D9_1_x64 = 101  # UE引擎
    D3D9_2_x64 = 102  # U3D引擎
    D3D9_3_x64 = 103  # RGBX通用
    D3D9_Steam_x64 = 104  # Steam游戏
    
    # D3D9 - 扩展版本（Ex，虚拟机窗口）
    D3D9_3_x86Ex = 203
    D3D9_3_x64Ex = 303
    
    # D3D11 - 32位
    D3D11_1_x86 = 5  # UE引擎
    D3D11_2_x86 = 6  # U3D引擎
    D3D11_3_x86 = 7  # RGBX通用
    D3D11_NC_x86 = 8  # NC游戏
    
    # D3D11 - 64位
    D3D11_1_x64 = 105  # UE引擎
    D3D11_2_x64 = 106  # U3D引擎
    D3D11_3_x64 = 107  # RGBX通用
    D3D11_NC_x64 = 108  # NC游戏
    
    # D3D11 - 扩展版本
    D3D11_3_x86Ex = 207
    D3D11_3_x64Ex = 307
    
    # D3D12 - 32位
    D3D12_1_x86 = 9  # UE引擎
    D3D12_2_x86 = 10  # U3D引擎
    D3D12_3_x86 = 11  # RGBX通用
    
    # D3D12 - 64位
    D3D12_1_x64 = 109  # UE引擎
    D3D12_2_x64 = 110  # U3D引擎
    D3D12_3_x64 = 111  # RGBX通用
    
    # D3D12 - 扩展版本
    D3D12_3_x86Ex = 211
    D3D12_3_x64Ex = 311
    
    # OpenGL
    OPENGL_2_x86 = 12  # 模拟器，GL_BGRA
    OPENGL_2_x64 = 112  # 模拟器，GL_BGRA