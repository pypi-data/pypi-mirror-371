#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK JSON数据处理模块封装
提供内置的JSON操作接口，支持JSON对象的创建、解析、字段读写、数组操作及内存释放等功能
支持中文处理，适用于引擎中各类JSON格式数据的序列化与反序列化
"""

import ctypes
import contextlib
from typing import Optional, Union, Dict, List, Any, Tuple, Iterator

from .base_module import HDModuleBase, HDModuleFactory


# 定义JSON句柄类型
JSON_HANDLE = ctypes.c_int64


class HDJSON(HDModuleBase):
    """
    HD GDK JSON数据处理模块
    提供内置的JSON操作接口，支持JSON对象的创建、解析、字段读写、数组操作及内存释放等功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化JSON数据处理模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的JSON模块函数
        """
        # 一、JSON对象基础操作
        # 1. 创建与释放
        self.HDJSON_Create = self.dll.HDJSON_Create
        self.HDJSON_Create.argtypes = []
        self.HDJSON_Create.restype = JSON_HANDLE
        
        self.HDJSON_Parse = self.dll.HDJSON_Parse
        self.HDJSON_Parse.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_Parse.restype = ctypes.c_bool
        
        self.HDJSON_Free = self.dll.HDJSON_Free
        self.HDJSON_Free.argtypes = [JSON_HANDLE]
        self.HDJSON_Free.restype = None
        
        self.HDJSON_ToString = self.dll.HDJSON_ToString
        self.HDJSON_ToString.argtypes = [JSON_HANDLE]
        self.HDJSON_ToString.restype = ctypes.c_char_p
        
        self.HDJSON_GetLastError = self.dll.HDJSON_GetLastError
        self.HDJSON_GetLastError.argtypes = []
        self.HDJSON_GetLastError.restype = ctypes.c_char_p
        
        # 2. 字段读取（JSON对象）
        self.HDJSON_GetString = self.dll.HDJSON_GetString
        self.HDJSON_GetString.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_GetString.restype = ctypes.c_char_p
        
        self.HDJSON_GetInt = self.dll.HDJSON_GetInt
        self.HDJSON_GetInt.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_GetInt.restype = ctypes.c_int
        
        self.HDJSON_GetInt64 = self.dll.HDJSON_GetInt64
        self.HDJSON_GetInt64.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_GetInt64.restype = ctypes.c_int64
        
        self.HDJSON_GetFloat = self.dll.HDJSON_GetFloat
        self.HDJSON_GetFloat.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_GetFloat.restype = ctypes.c_float
        
        self.HDJSON_GetDouble = self.dll.HDJSON_GetDouble
        self.HDJSON_GetDouble.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_GetDouble.restype = ctypes.c_double
        
        self.HDJSON_GetBool = self.dll.HDJSON_GetBool
        self.HDJSON_GetBool.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_GetBool.restype = ctypes.c_bool
        
        self.HDJSON_GetArray = self.dll.HDJSON_GetArray
        self.HDJSON_GetArray.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_GetArray.restype = JSON_HANDLE
        
        # 3. 字段设置（JSON对象）
        self.HDJSON_SetString = self.dll.HDJSON_SetString
        self.HDJSON_SetString.argtypes = [JSON_HANDLE, ctypes.c_char_p, ctypes.c_char_p]
        self.HDJSON_SetString.restype = ctypes.c_bool
        
        self.HDJSON_SetInt = self.dll.HDJSON_SetInt
        self.HDJSON_SetInt.argtypes = [JSON_HANDLE, ctypes.c_char_p, ctypes.c_int]
        self.HDJSON_SetInt.restype = ctypes.c_bool
        
        self.HDJSON_SetInt64 = self.dll.HDJSON_SetInt64
        self.HDJSON_SetInt64.argtypes = [JSON_HANDLE, ctypes.c_char_p, ctypes.c_int64]
        self.HDJSON_SetInt64.restype = ctypes.c_bool
        
        self.HDJSON_SetFloat = self.dll.HDJSON_SetFloat
        self.HDJSON_SetFloat.argtypes = [JSON_HANDLE, ctypes.c_char_p, ctypes.c_float]
        self.HDJSON_SetFloat.restype = ctypes.c_bool
        
        self.HDJSON_SetDouble = self.dll.HDJSON_SetDouble
        self.HDJSON_SetDouble.argtypes = [JSON_HANDLE, ctypes.c_char_p, ctypes.c_double]
        self.HDJSON_SetDouble.restype = ctypes.c_bool
        
        self.HDJSON_SetBool = self.dll.HDJSON_SetBool
        self.HDJSON_SetBool.argtypes = [JSON_HANDLE, ctypes.c_char_p, ctypes.c_bool]
        self.HDJSON_SetBool.restype = ctypes.c_bool
        
        self.HDJSON_SetArray = self.dll.HDJSON_SetArray
        self.HDJSON_SetArray.argtypes = [JSON_HANDLE, ctypes.c_char_p, JSON_HANDLE]
        self.HDJSON_SetArray.restype = ctypes.c_bool
        
        # 二、JSON数组操作
        # 1. 数组创建与大小
        self.HDJSON_CreateArray = self.dll.HDJSON_CreateArray
        self.HDJSON_CreateArray.argtypes = []
        self.HDJSON_CreateArray.restype = JSON_HANDLE
        
        self.HDJSON_ArraySize = self.dll.HDJSON_ArraySize
        self.HDJSON_ArraySize.argtypes = [JSON_HANDLE]
        self.HDJSON_ArraySize.restype = ctypes.c_int
        
        # 2. 数组元素读取
        self.HDJSON_ArrayGetString = self.dll.HDJSON_ArrayGetString
        self.HDJSON_ArrayGetString.argtypes = [JSON_HANDLE, ctypes.c_int]
        self.HDJSON_ArrayGetString.restype = ctypes.c_char_p
        
        self.HDJSON_ArrayGetInt = self.dll.HDJSON_ArrayGetInt
        self.HDJSON_ArrayGetInt.argtypes = [JSON_HANDLE, ctypes.c_int]
        self.HDJSON_ArrayGetInt.restype = ctypes.c_int
        
        self.HDJSON_ArrayGetInt64 = self.dll.HDJSON_ArrayGetInt64
        self.HDJSON_ArrayGetInt64.argtypes = [JSON_HANDLE, ctypes.c_int]
        self.HDJSON_ArrayGetInt64.restype = ctypes.c_int64
        
        self.HDJSON_ArrayGetFloat = self.dll.HDJSON_ArrayGetFloat
        self.HDJSON_ArrayGetFloat.argtypes = [JSON_HANDLE, ctypes.c_int]
        self.HDJSON_ArrayGetFloat.restype = ctypes.c_float
        
        self.HDJSON_ArrayGetDouble = self.dll.HDJSON_ArrayGetDouble
        self.HDJSON_ArrayGetDouble.argtypes = [JSON_HANDLE, ctypes.c_int]
        self.HDJSON_ArrayGetDouble.restype = ctypes.c_double
        
        self.HDJSON_ArrayGetBool = self.dll.HDJSON_ArrayGetBool
        self.HDJSON_ArrayGetBool.argtypes = [JSON_HANDLE, ctypes.c_int]
        self.HDJSON_ArrayGetBool.restype = ctypes.c_bool
        
        self.HDJSON_ArrayGetObject = self.dll.HDJSON_ArrayGetObject
        self.HDJSON_ArrayGetObject.argtypes = [JSON_HANDLE, ctypes.c_int]
        self.HDJSON_ArrayGetObject.restype = JSON_HANDLE
        
        # 3. 数组元素添加
        self.HDJSON_ArrayAddString = self.dll.HDJSON_ArrayAddString
        self.HDJSON_ArrayAddString.argtypes = [JSON_HANDLE, ctypes.c_char_p]
        self.HDJSON_ArrayAddString.restype = ctypes.c_bool
        
        self.HDJSON_ArrayAddInt = self.dll.HDJSON_ArrayAddInt
        self.HDJSON_ArrayAddInt.argtypes = [JSON_HANDLE, ctypes.c_int]
        self.HDJSON_ArrayAddInt.restype = ctypes.c_bool
        
        self.HDJSON_ArrayAddInt64 = self.dll.HDJSON_ArrayAddInt64
        self.HDJSON_ArrayAddInt64.argtypes = [JSON_HANDLE, ctypes.c_int64]
        self.HDJSON_ArrayAddInt64.restype = ctypes.c_bool
        
        self.HDJSON_ArrayAddFloat = self.dll.HDJSON_ArrayAddFloat
        self.HDJSON_ArrayAddFloat.argtypes = [JSON_HANDLE, ctypes.c_float]
        self.HDJSON_ArrayAddFloat.restype = ctypes.c_bool
        
        self.HDJSON_ArrayAddDouble = self.dll.HDJSON_ArrayAddDouble
        self.HDJSON_ArrayAddDouble.argtypes = [JSON_HANDLE, ctypes.c_double]
        self.HDJSON_ArrayAddDouble.restype = ctypes.c_bool
        
        self.HDJSON_ArrayAddBool = self.dll.HDJSON_ArrayAddBool
        self.HDJSON_ArrayAddBool.argtypes = [JSON_HANDLE, ctypes.c_bool]
        self.HDJSON_ArrayAddBool.restype = ctypes.c_bool

    # 1. JSON对象基础操作
    def create_json(self) -> JSON_HANDLE:
        """
        创建一个空的JSON对象
        
        Returns:
            JSON_HANDLE: JSON对象句柄
        """
        return self.HDJSON_Create()
    
    def parse_json(self, h_json: JSON_HANDLE, json_str: str) -> bool:
        """
        解析JSON字符串为JSON对象（支持中文）
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            json_str (str): 待解析的JSON字符串
        
        Returns:
            bool: True表示解析成功，False表示失败
        """
        return self.HDJSON_Parse(h_json, json_str.encode('utf-8'))
    
    def free_json(self, h_json: JSON_HANDLE) -> None:
        """
        释放JSON对象句柄及关联内存
        
        Args:
            h_json (JSON_HANDLE): 待释放的JSON对象句柄
        """
        if h_json != 0:
            self.HDJSON_Free(h_json)
    
    def to_string(self, h_json: JSON_HANDLE) -> str:
        """
        将JSON对象转换为字符串形式
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
        
        Returns:
            str: JSON字符串（支持中文）
        """
        result = self.HDJSON_ToString(h_json)
        if result:
            return result.decode('utf-8')
        return ""
    
    def get_last_error(self) -> str:
        """
        获取当前线程最近一次JSON操作的错误信息
        
        Returns:
            str: 错误信息字符串
        """
        result = self.HDJSON_GetLastError()
        if result:
            return result.decode('utf-8')
        return ""

    # 2. JSON对象字段读取
    def get_string(self, h_json: JSON_HANDLE, key: str, default: str = "") -> str:
        """
        通过键名获取字符串字段（支持中文）
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名（不支持中文）
            default (str): 默认值
        
        Returns:
            str: 字符串值，不存在返回默认值
        """
        result = self.HDJSON_GetString(h_json, key.encode('ascii'))
        if result:
            return result.decode('utf-8')
        return default
    
    def get_int(self, h_json: JSON_HANDLE, key: str, default: int = 0) -> int:
        """
        获取4字节整数字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            default (int): 默认值
        
        Returns:
            int: 整数值，不存在返回默认值
        """
        result = self.HDJSON_GetInt(h_json, key.encode('ascii'))
        return result if result != 0 or self.HDJSON_GetLastError() else default
    
    def get_int64(self, h_json: JSON_HANDLE, key: str, default: int = 0) -> int:
        """
        获取8字节整数字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            default (int): 默认值
        
        Returns:
            int: 整数值，不存在返回默认值
        """
        result = self.HDJSON_GetInt64(h_json, key.encode('ascii'))
        return result if result != 0 or self.HDJSON_GetLastError() else default
    
    def get_float(self, h_json: JSON_HANDLE, key: str, default: float = 0.0) -> float:
        """
        获取4字节浮点数字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            default (float): 默认值
        
        Returns:
            float: 浮点数值，不存在返回默认值
        """
        result = self.HDJSON_GetFloat(h_json, key.encode('ascii'))
        return result if result != 0.0 or self.HDJSON_GetLastError() else default
    
    def get_double(self, h_json: JSON_HANDLE, key: str, default: float = 0.0) -> float:
        """
        获取8字节浮点数字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            default (float): 默认值
        
        Returns:
            float: 浮点数值，不存在返回默认值
        """
        result = self.HDJSON_GetDouble(h_json, key.encode('ascii'))
        return result if result != 0.0 or self.HDJSON_GetLastError() else default
    
    def get_bool(self, h_json: JSON_HANDLE, key: str, default: bool = False) -> bool:
        """
        获取布尔类型字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            default (bool): 默认值
        
        Returns:
            bool: 布尔值，不存在返回默认值
        """
        result = self.HDJSON_GetBool(h_json, key.encode('ascii'))
        return bool(result) if self.HDJSON_GetLastError() else default
    
    def get_array(self, h_json: JSON_HANDLE, key: str) -> JSON_HANDLE:
        """
        通过键名获取JSON数组对象
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
        
        Returns:
            JSON_HANDLE: 数组对象句柄，不存在返回无效句柄
        """
        return self.HDJSON_GetArray(h_json, key.encode('ascii'))

    # 3. JSON对象字段设置
    def set_string(self, h_json: JSON_HANDLE, key: str, value: str) -> bool:
        """
        设置字符串类型键值对（支持中文）
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名（不支持中文）
            value (str): 字符串值
        
        Returns:
            bool: True表示设置成功，False表示失败
        """
        return self.HDJSON_SetString(h_json, key.encode('ascii'), value.encode('utf-8'))
    
    def set_int(self, h_json: JSON_HANDLE, key: str, value: int) -> bool:
        """
        设置4字节整数字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            value (int): 整数值
        
        Returns:
            bool: True表示设置成功，False表示失败
        """
        return self.HDJSON_SetInt(h_json, key.encode('ascii'), value)
    
    def set_int64(self, h_json: JSON_HANDLE, key: str, value: int) -> bool:
        """
        设置8字节整数字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            value (int): 整数值
        
        Returns:
            bool: True表示设置成功，False表示失败
        """
        return self.HDJSON_SetInt64(h_json, key.encode('ascii'), value)
    
    def set_float(self, h_json: JSON_HANDLE, key: str, value: float) -> bool:
        """
        设置4字节浮点数字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            value (float): 浮点数值
        
        Returns:
            bool: True表示设置成功，False表示失败
        """
        return self.HDJSON_SetFloat(h_json, key.encode('ascii'), value)
    
    def set_double(self, h_json: JSON_HANDLE, key: str, value: float) -> bool:
        """
        设置8字节浮点数字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            value (float): 浮点数值
        
        Returns:
            bool: True表示设置成功，False表示失败
        """
        return self.HDJSON_SetDouble(h_json, key.encode('ascii'), value)
    
    def set_bool(self, h_json: JSON_HANDLE, key: str, value: bool) -> bool:
        """
        设置布尔类型字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            value (bool): 布尔值
        
        Returns:
            bool: True表示设置成功，False表示失败
        """
        return self.HDJSON_SetBool(h_json, key.encode('ascii'), value)
    
    def set_array(self, h_json: JSON_HANDLE, key: str, h_array: JSON_HANDLE) -> bool:
        """
        设置数组类型字段
        
        Args:
            h_json (JSON_HANDLE): JSON对象句柄
            key (str): 键名
            h_array (JSON_HANDLE): 数组对象句柄
        
        Returns:
            bool: True表示设置成功，False表示失败
        """
        return self.HDJSON_SetArray(h_json, key.encode('ascii'), h_array)

    # 二、JSON数组操作
    def create_array(self) -> JSON_HANDLE:
        """
        创建一个空的JSON数组
        
        Returns:
            JSON_HANDLE: 数组句柄
        """
        return self.HDJSON_CreateArray()
    
    def array_size(self, h_array: JSON_HANDLE) -> int:
        """
        获取数组元素数量
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
        
        Returns:
            int: 数组元素数量
        """
        return self.HDJSON_ArraySize(h_array)
    
    def array_get_string(self, h_array: JSON_HANDLE, index: int, default: str = "") -> str:
        """
        通过索引获取数组中的字符串元素（支持中文）
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            index (int): 元素索引（从0开始）
            default (str): 默认值
        
        Returns:
            str: 字符串元素，不存在返回默认值
        """
        result = self.HDJSON_ArrayGetString(h_array, index)
        if result:
            return result.decode('utf-8')
        return default
    
    def array_get_int(self, h_array: JSON_HANDLE, index: int, default: int = 0) -> int:
        """
        获取数组中的4字节整数元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            index (int): 元素索引
            default (int): 默认值
        
        Returns:
            int: 整数元素，不存在返回默认值
        """
        result = self.HDJSON_ArrayGetInt(h_array, index)
        return result if result != 0 or self.HDJSON_GetLastError() else default
    
    def array_get_int64(self, h_array: JSON_HANDLE, index: int, default: int = 0) -> int:
        """
        获取数组中的8字节整数元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            index (int): 元素索引
            default (int): 默认值
        
        Returns:
            int: 整数元素，不存在返回默认值
        """
        result = self.HDJSON_ArrayGetInt64(h_array, index)
        return result if result != 0 or self.HDJSON_GetLastError() else default
    
    def array_get_float(self, h_array: JSON_HANDLE, index: int, default: float = 0.0) -> float:
        """
        获取数组中的4字节浮点数元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            index (int): 元素索引
            default (float): 默认值
        
        Returns:
            float: 浮点数元素，不存在返回默认值
        """
        result = self.HDJSON_ArrayGetFloat(h_array, index)
        return result if result != 0.0 or self.HDJSON_GetLastError() else default
    
    def array_get_double(self, h_array: JSON_HANDLE, index: int, default: float = 0.0) -> float:
        """
        获取数组中的8字节浮点数元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            index (int): 元素索引
            default (float): 默认值
        
        Returns:
            float: 浮点数元素，不存在返回默认值
        """
        result = self.HDJSON_ArrayGetDouble(h_array, index)
        return result if result != 0.0 or self.HDJSON_GetLastError() else default
    
    def array_get_bool(self, h_array: JSON_HANDLE, index: int, default: bool = False) -> bool:
        """
        获取数组中的布尔元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            index (int): 元素索引
            default (bool): 默认值
        
        Returns:
            bool: 布尔元素，不存在返回默认值
        """
        result = self.HDJSON_ArrayGetBool(h_array, index)
        return bool(result) if self.HDJSON_GetLastError() else default
    
    def array_get_object(self, h_array: JSON_HANDLE, index: int) -> JSON_HANDLE:
        """
        获取数组中的JSON对象元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            index (int): 元素索引
        
        Returns:
            JSON_HANDLE: 对象句柄，不存在返回无效句柄
        """
        return self.HDJSON_ArrayGetObject(h_array, index)
    
    def array_add_string(self, h_array: JSON_HANDLE, value: str) -> bool:
        """
        向数组添加字符串元素（支持中文）
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            value (str): 字符串值
        
        Returns:
            bool: True表示添加成功，False表示失败
        """
        return self.HDJSON_ArrayAddString(h_array, value.encode('utf-8'))
    
    def array_add_int(self, h_array: JSON_HANDLE, value: int) -> bool:
        """
        向数组添加4字节整数元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            value (int): 整数值
        
        Returns:
            bool: True表示添加成功，False表示失败
        """
        return self.HDJSON_ArrayAddInt(h_array, value)
    
    def array_add_int64(self, h_array: JSON_HANDLE, value: int) -> bool:
        """
        向数组添加8字节整数元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            value (int): 整数值
        
        Returns:
            bool: True表示添加成功，False表示失败
        """
        return self.HDJSON_ArrayAddInt64(h_array, value)
    
    def array_add_float(self, h_array: JSON_HANDLE, value: float) -> bool:
        """
        向数组添加4字节浮点数元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            value (float): 浮点数值
        
        Returns:
            bool: True表示添加成功，False表示失败
        """
        return self.HDJSON_ArrayAddFloat(h_array, value)
    
    def array_add_double(self, h_array: JSON_HANDLE, value: float) -> bool:
        """
        向数组添加8字节浮点数元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            value (float): 浮点数值
        
        Returns:
            bool: True表示添加成功，False表示失败
        """
        return self.HDJSON_ArrayAddDouble(h_array, value)
    
    def array_add_bool(self, h_array: JSON_HANDLE, value: bool) -> bool:
        """
        向数组添加布尔元素
        
        Args:
            h_array (JSON_HANDLE): 数组对象句柄
            value (bool): 布尔值
        
        Returns:
            bool: True表示添加成功，False表示失败
        """
        return self.HDJSON_ArrayAddBool(h_array, value)


# 工厂函数
def create_hd_json(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HDJSON:
    """
    创建JSON数据处理模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDJSON: JSON数据处理模块实例
    """
    return HDModuleFactory.create_instance(HDJSON, dll_path, is_debug)


# 提供更友好的模块别名
def get_hd_json_instance(dll_path: Optional[str] = None, is_debug: Optional[bool] = None) -> HDJSON:
    """
    获取JSON数据处理模块实例的别名函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDJSON: JSON数据处理模块实例
    """
    return create_hd_json(dll_path, is_debug)


# 上下文管理器，用于自动释放JSON句柄
@contextlib.contextmanager
def json_handle(json_module: HDJSON) -> Iterator[JSON_HANDLE]:
    """
    JSON句柄上下文管理器，自动创建和释放JSON句柄
    
    Args:
        json_module (HDJSON): JSON模块实例
    
    Yields:
        JSON_HANDLE: JSON对象句柄
    """
    handle = json_module.create_json()
    try:
        yield handle
    finally:
        json_module.free_json(handle)


@contextlib.contextmanager
def array_handle(json_module: HDJSON) -> Iterator[JSON_HANDLE]:
    """
    数组句柄上下文管理器，自动创建和释放数组句柄
    
    Args:
        json_module (HDJSON): JSON模块实例
    
    Yields:
        JSON_HANDLE: 数组句柄
    """
    handle = json_module.create_array()
    try:
        yield handle
    finally:
        json_module.free_json(handle)


# 辅助函数：从Python字典创建JSON对象
def dict_to_json(json_module: HDJSON, py_dict: Dict[str, Any]) -> JSON_HANDLE:
    """
    将Python字典转换为JSON对象
    
    Args:
        json_module (HDJSON): JSON模块实例
        py_dict (dict): Python字典
    
    Returns:
        JSON_HANDLE: JSON对象句柄
    """
    h_json = json_module.create_json()
    
    for key, value in py_dict.items():
        if isinstance(value, str):
            json_module.set_string(h_json, key, value)
        elif isinstance(value, int):
            if abs(value) > 2**31 - 1:
                json_module.set_int64(h_json, key, value)
            else:
                json_module.set_int(h_json, key, value)
        elif isinstance(value, float):
            json_module.set_double(h_json, key, value)
        elif isinstance(value, bool):
            json_module.set_bool(h_json, key, value)
        elif isinstance(value, dict):
            h_sub = dict_to_json(json_module, value)
            json_module.set_string(h_json, key, json_module.to_string(h_sub))
            json_module.free_json(h_sub)
        elif isinstance(value, list):
            h_array = list_to_array(json_module, value)
            json_module.set_array(h_json, key, h_array)
    
    return h_json


# 辅助函数：从Python列表创建JSON数组
def list_to_array(json_module: HDJSON, py_list: List[Any]) -> JSON_HANDLE:
    """
    将Python列表转换为JSON数组
    
    Args:
        json_module (HDJSON): JSON模块实例
        py_list (list): Python列表
    
    Returns:
        JSON_HANDLE: 数组句柄
    """
    h_array = json_module.create_array()
    
    for value in py_list:
        if isinstance(value, str):
            json_module.array_add_string(h_array, value)
        elif isinstance(value, int):
            if abs(value) > 2**31 - 1:
                json_module.array_add_int64(h_array, value)
            else:
                json_module.array_add_int(h_array, value)
        elif isinstance(value, float):
            json_module.array_add_double(h_array, value)
        elif isinstance(value, bool):
            json_module.array_add_bool(h_array, value)
        elif isinstance(value, dict):
            h_sub = dict_to_json(json_module, value)
            json_module.array_add_string(h_array, json_module.to_string(h_sub))
            json_module.free_json(h_sub)
        elif isinstance(value, list):
            h_subarray = list_to_array(json_module, value)
            # 将子数组转换为字符串添加到父数组
            json_module.array_add_string(h_array, json_module.to_string(h_subarray))
            json_module.free_json(h_subarray)
    
    return h_array


# 辅助函数：将JSON对象转换为Python字典
def json_to_dict(json_module: HDJSON, h_json: JSON_HANDLE) -> Dict[str, Any]:
    """
    将JSON对象转换为Python字典
    
    Args:
        json_module (HDJSON): JSON模块实例
        h_json (JSON_HANDLE): JSON对象句柄
    
    Returns:
        dict: Python字典
    """
    result = {}
    json_str = json_module.to_string(h_json)
    if not json_str:
        return result
    
    # 为了简化，这里使用Python内置的json模块来解析字符串
    # 实际使用中可能需要更复杂的解析逻辑，避免依赖Python的json模块
    import json
    try:
        return json.loads(json_str)
    except:
        # 如果解析失败，返回空字典
        return result


# 辅助函数：将JSON数组转换为Python列表
def array_to_list(json_module: HDJSON, h_array: JSON_HANDLE) -> List[Any]:
    """
    将JSON数组转换为Python列表
    
    Args:
        json_module (HDJSON): JSON模块实例
        h_array (JSON_HANDLE): 数组句柄
    
    Returns:
        list: Python列表
    """
    result = []
    array_str = json_module.to_string(h_array)
    if not array_str:
        return result
    
    # 为了简化，这里使用Python内置的json模块来解析字符串
    import json
    try:
        return json.loads(array_str)
    except:
        # 如果解析失败，返回空列表
        return result


# 辅助函数：解析JSON字符串
def parse_json_string(json_module: HDJSON, json_str: str) -> Tuple[bool, JSON_HANDLE]:
    """
    解析JSON字符串并返回结果
    
    Args:
        json_module (HDJSON): JSON模块实例
        json_str (str): JSON字符串
    
    Returns:
        tuple: (成功标志, JSON句柄)
    """
    h_json = json_module.create_json()
    success = json_module.parse_json(h_json, json_str)
    if not success:
        json_module.free_json(h_json)
        return False, 0
    return True, h_json