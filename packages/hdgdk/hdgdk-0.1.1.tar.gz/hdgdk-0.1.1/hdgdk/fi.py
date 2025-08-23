#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD RPG引擎框架(GDK)智能识图模块(FI)Python封装
提供基于图像匹配的识别功能，支持从目标窗口、本地文件或内存数据中识别指定图像
"""

import ctypes
from .base_module import HDModuleBase, HDModuleFactory


class HCFI(HDModuleBase):
    """HD RPG引擎框架智能识图模块(FI)的Python封装类"""
    
    def _initialize_functions(self):
        """初始化DLL函数绑定"""
        # 基础识图函数（全窗口范围）
        # 返回圆点坐标
        self.HCFI_FindImageA = self.dll.HCFI_FindImageA
        self.HCFI_FindImageA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageA.restype = ctypes.c_int64
        
        self.HCFI_FindImageW = self.dll.HCFI_FindImageW
        self.HCFI_FindImageW.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageW.restype = ctypes.c_int64
        
        # 返回矩形坐标
        self.HCFI_FindImageExA = self.dll.HCFI_FindImageExA
        self.HCFI_FindImageExA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageExA.restype = ctypes.c_int64
        
        self.HCFI_FindImageExW = self.dll.HCFI_FindImageExW
        self.HCFI_FindImageExW.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageExW.restype = ctypes.c_int64
        
        # 范围识图函数
        self.HCFI_FindRangeImageA = self.dll.HCFI_FindRangeImageA
        self.HCFI_FindRangeImageA.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, 
                                             ctypes.c_char_p, ctypes.c_int32, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindRangeImageA.restype = ctypes.c_int64
        
        self.HCFI_FindRangeImageW = self.dll.HCFI_FindRangeImageW
        self.HCFI_FindRangeImageW.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, 
                                             ctypes.c_wchar_p, ctypes.c_int32, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindRangeImageW.restype = ctypes.c_int64
        
        # 高级识图函数（支持多种算法）
        # 全窗口高级识图
        self.HCFI_FindImageTemA = self.dll.HCFI_FindImageTemA
        self.HCFI_FindImageTemA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, 
                                           ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageTemA.restype = ctypes.c_int64
        
        self.HCFI_FindImageTemW = self.dll.HCFI_FindImageTemW
        self.HCFI_FindImageTemW.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_double, ctypes.c_int32, 
                                           ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageTemW.restype = ctypes.c_int64
        
        # 范围高级识图
        self.HCFI_FindRangeImageTemA = self.dll.HCFI_FindRangeImageTemA
        self.HCFI_FindRangeImageTemA.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, 
                                                ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, 
                                                ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindRangeImageTemA.restype = ctypes.c_int64
        
        self.HCFI_FindRangeImageTemW = self.dll.HCFI_FindRangeImageTemW
        self.HCFI_FindRangeImageTemW.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, 
                                                ctypes.c_wchar_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, 
                                                ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindRangeImageTemW.restype = ctypes.c_int64
        
        # 从文件加载图像的识图函数
        # 基础文件识图
        self.HCFI_FindImageByFile = self.dll.HCFI_FindImageByFile
        self.HCFI_FindImageByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, 
                                             ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageByFile.restype = ctypes.c_int64
        
        # 高级文件识图
        self.HCFI_FindImageTemByFile = self.dll.HCFI_FindImageTemByFile
        self.HCFI_FindImageTemByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, 
                                                ctypes.c_double, ctypes.c_int32, ctypes.c_bool, 
                                                ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageTemByFile.restype = ctypes.c_int64
        
        self.HCFI_FindRangeImageTemByFile = self.dll.HCFI_FindRangeImageTemByFile
        self.HCFI_FindRangeImageTemByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, 
                                                     ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, 
                                                     ctypes.c_double, ctypes.c_int32, ctypes.c_bool, 
                                                     ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindRangeImageTemByFile.restype = ctypes.c_int64
        
        # 从内存加载图像的识图函数
        # 基础内存识图
        self.HCFI_FindImageByMem = self.dll.HCFI_FindImageByMem
        self.HCFI_FindImageByMem.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, 
                                            ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageByMem.restype = ctypes.c_int64
        
        # 高级内存识图
        self.HCFI_FindImageTemByMem = self.dll.HCFI_FindImageTemByMem
        self.HCFI_FindImageTemByMem.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, 
                                               ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, 
                                               ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageTemByMem.restype = ctypes.c_int64
        
        self.HCFI_FindRangeImageTemByMem = self.dll.HCFI_FindRangeImageTemByMem
        self.HCFI_FindRangeImageTemByMem.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, 
                                                    ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, 
                                                    ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, 
                                                    ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindRangeImageTemByMem.restype = ctypes.c_int64
        
        # 子图从内存的识图
        self.HCFI_FindImageTemFromMem = self.dll.HCFI_FindImageTemFromMem
        self.HCFI_FindImageTemFromMem.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, 
                                                 ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindImageTemFromMem.restype = ctypes.c_int64
        
        self.HCFI_FindRangeImageTemFromMem = self.dll.HCFI_FindRangeImageTemFromMem
        self.HCFI_FindRangeImageTemFromMem.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, 
                                                      ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, 
                                                      ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
        self.HCFI_FindRangeImageTemFromMem.restype = ctypes.c_int64
        
    def find_image(self, window_index, image_names, sim=0.8, is_gray=False, show_viewer=False, use_wchar=False):
        """
        在目标窗口中识别图像，返回匹配区域的圆点坐标
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            image_names (str): 多个图片名（用`|`分隔，支持绝对/相对路径，如"hd1.bmp|hd2.bmp"）
            sim (float, optional): 相似度（0~1，默认0.8）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            show_viewer (bool, optional): 识别后是否打开查看器
            use_wchar (bool, optional): 是否使用宽字符版本函数
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含匹配点坐标
        """
        if use_wchar:
            return self.HCFI_FindImageW(window_index, image_names, sim, is_gray, show_viewer)
        else:
            return self.HCFI_FindImageA(window_index, image_names.encode('utf-8'), sim, is_gray, show_viewer)
            
    def find_image_ex(self, window_index, image_names, sim=0.8, is_gray=False, show_viewer=False, use_wchar=False):
        """
        在目标窗口中识别图像，返回匹配区域的矩形坐标（左上角x1,y1和右下角x2,y2）
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            image_names (str): 多个图片名（用`|`分隔，支持绝对/相对路径，如"hd1.bmp|hd2.bmp"）
            sim (float, optional): 相似度（0~1，默认0.8）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            show_viewer (bool, optional): 识别后是否打开查看器
            use_wchar (bool, optional): 是否使用宽字符版本函数
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含矩形坐标
        """
        if use_wchar:
            return self.HCFI_FindImageExW(window_index, image_names, sim, is_gray, show_viewer)
        else:
            return self.HCFI_FindImageExA(window_index, image_names.encode('utf-8'), sim, is_gray, show_viewer)
            
    def find_range_image(self, window_index, x, y, w, h, image_names, type=0, sim=0.8, is_gray=False, show_viewer=False, use_wchar=False):
        """
        在指定矩形区域内识别图像，可选择返回圆点或矩形坐标
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            x, y (int): 识别区域左上角坐标
            w, h (int): 识别区域宽度和高度
            image_names (str): 多个图片名（用`|`分隔，支持绝对/相对路径，如"hd1.bmp|hd2.bmp"）
            type (int, optional): 0（返回圆点）、1（返回矩形）
            sim (float, optional): 相似度（0~1，默认0.8）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            show_viewer (bool, optional): 识别后是否打开查看器
            use_wchar (bool, optional): 是否使用宽字符版本函数
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果根据type不同
        """
        if use_wchar:
            return self.HCFI_FindRangeImageW(window_index, x, y, w, h, image_names, type, sim, is_gray, show_viewer)
        else:
            return self.HCFI_FindRangeImageA(window_index, x, y, w, h, image_names.encode('utf-8'), type, sim, is_gray, show_viewer)
            
    def find_image_tem(self, window_index, image_names, sim=0.9, type=5, is_gray=False, return_all=False, show_viewer=False, use_wchar=False):
        """
        支持6种匹配算法，可返回全部匹配结果（去重后）
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            image_names (str): 多个图片名（用`|`分隔，支持绝对/相对路径）
            sim (float, optional): 相似度（0~1，默认0.9）
            type (int, optional): 算法类型（0-5，推荐3或5，其他效率较低）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            return_all (bool, optional): TRUE表示返回所有匹配结果（仅type=3/4/5支持，自动去重矩形）
            show_viewer (bool, optional): 识别后是否打开查看器
            use_wchar (bool, optional): 是否使用宽字符版本函数
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含所有匹配点
        """
        if use_wchar:
            return self.HCFI_FindImageTemW(window_index, image_names, sim, type, is_gray, return_all, show_viewer)
        else:
            return self.HCFI_FindImageTemA(window_index, image_names.encode('utf-8'), sim, type, is_gray, return_all, show_viewer)
            
    def find_range_image_tem(self, window_index, x, y, w, h, image_names, sim=0.9, type=5, is_gray=False, return_all=False, show_viewer=False, use_wchar=False):
        """
        在指定区域内使用多种算法识别图像，支持返回全部结果
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            x, y (int): 识别区域左上角坐标
            w, h (int): 识别区域宽度和高度
            image_names (str): 多个图片名（用`|`分隔，支持绝对/相对路径）
            sim (float, optional): 相似度（0~1，默认0.9）
            type (int, optional): 算法类型（0-5，推荐3或5，其他效率较低）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            return_all (bool, optional): TRUE表示返回所有匹配结果（仅type=3/4/5支持，自动去重矩形）
            show_viewer (bool, optional): 识别后是否打开查看器
            use_wchar (bool, optional): 是否使用宽字符版本函数
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含所有匹配点
        """
        if use_wchar:
            return self.HCFI_FindRangeImageTemW(window_index, x, y, w, h, image_names, sim, type, is_gray, return_all, show_viewer)
        else:
            return self.HCFI_FindRangeImageTemA(window_index, x, y, w, h, image_names.encode('utf-8'), sim, type, is_gray, return_all, show_viewer)
            
    def find_image_by_file(self, window_index, source_image, target_images, sim=0.9, is_gray=False, show_viewer=False):
        """
        从本地文件加载原图，识别指定子图，返回矩形坐标
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            source_image (str): 本地原图路径（支持绝对/相对路径）
            target_images (str): 待识别的子图（用`|`分隔）
            sim (float, optional): 相似度（0~1，默认0.9）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            show_viewer (bool, optional): 识别后是否打开查看器
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含矩形坐标
        """
        return self.HCFI_FindImageByFile(window_index, source_image.encode('utf-8'), target_images.encode('utf-8'), sim, is_gray, show_viewer)
        
    def find_image_tem_by_file(self, window_index, source_image, target_images, sim=0.9, type=5, is_gray=False, return_all=False, show_viewer=False):
        """
        从文件加载原图，使用多种算法识别子图，支持返回全部结果
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            source_image (str): 本地原图路径（支持绝对/相对路径）
            target_images (str): 待识别的子图（用`|`分隔）
            sim (float, optional): 相似度（0~1，默认0.9）
            type (int, optional): 算法类型（0-5，推荐3或5，其他效率较低）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            return_all (bool, optional): TRUE表示返回所有匹配结果（仅type=3/4/5支持，自动去重矩形）
            show_viewer (bool, optional): 识别后是否打开查看器
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含所有匹配点
        """
        return self.HCFI_FindImageTemByFile(window_index, source_image.encode('utf-8'), target_images.encode('utf-8'), sim, type, is_gray, return_all, show_viewer)
        
    def find_range_image_tem_by_file(self, window_index, source_image, x, y, w, h, target_images, sim=0.9, type=5, is_gray=False, return_all=False, show_viewer=False):
        """
        从文件加载原图，在指定区域内使用多种算法识别子图，支持返回全部结果
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            source_image (str): 本地原图路径（支持绝对/相对路径）
            x, y (int): 原图内识别区域左上角坐标
            w, h (int): 原图内识别区域宽度和高度
            target_images (str): 待识别的子图（用`|`分隔）
            sim (float, optional): 相似度（0~1，默认0.9）
            type (int, optional): 算法类型（0-5，推荐3或5，其他效率较低）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            return_all (bool, optional): TRUE表示返回所有匹配结果（仅type=3/4/5支持，自动去重矩形）
            show_viewer (bool, optional): 识别后是否打开查看器
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含所有匹配点
        """
        return self.HCFI_FindRangeImageTemByFile(window_index, source_image.encode('utf-8'), x, y, w, h, target_images.encode('utf-8'), sim, type, is_gray, return_all, show_viewer)
        
    def find_image_by_mem(self, window_index, data, data_size, target_images, sim=0.8, is_gray=False, show_viewer=False):
        """
        从内存加载原图数据（BMP格式），识别子图，返回矩形坐标
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            data (bytes): 内存中BMP图片数据
            data_size (int): 数据大小（字节）
            target_images (str): 待识别的子图（用`|`分隔）
            sim (float, optional): 相似度（0~1，默认0.8）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            show_viewer (bool, optional): 识别后是否打开查看器
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含矩形坐标
        """
        # 将Python bytes转换为ctypes POINTER(ctypes.c_ubyte)
        buffer_type = ctypes.c_ubyte * data_size
        buffer = buffer_type.from_buffer_copy(data)
        return self.HCFI_FindImageByMem(window_index, buffer, data_size, target_images.encode('utf-8'), sim, is_gray, show_viewer)
        
    def find_image_tem_by_mem(self, window_index, data, data_size, target_images, sim=0.9, type=5, is_gray=False, return_all=False, show_viewer=False):
        """
        从内存加载原图数据，使用多种算法识别子图，支持返回全部结果
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            data (bytes): 内存中BMP图片数据
            data_size (int): 数据大小（字节）
            target_images (str): 待识别的子图（用`|`分隔）
            sim (float, optional): 相似度（0~1，默认0.9）
            type (int, optional): 算法类型（0-5，推荐3或5，其他效率较低）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            return_all (bool, optional): TRUE表示返回所有匹配结果（仅type=3/4/5支持，自动去重矩形）
            show_viewer (bool, optional): 识别后是否打开查看器
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含所有匹配点
        """
        # 将Python bytes转换为ctypes POINTER(ctypes.c_ubyte)
        buffer_type = ctypes.c_ubyte * data_size
        buffer = buffer_type.from_buffer_copy(data)
        return self.HCFI_FindImageTemByMem(window_index, buffer, data_size, target_images.encode('utf-8'), sim, type, is_gray, return_all, show_viewer)
        
    def find_range_image_tem_by_mem(self, window_index, data, data_size, x, y, w, h, target_images, sim=0.9, type=5, is_gray=False, return_all=False, show_viewer=False):
        """
        从内存加载原图数据，在指定区域内使用多种算法识别子图，支持返回全部结果
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            data (bytes): 内存中BMP图片数据
            data_size (int): 数据大小（字节）
            x, y (int): 原图内识别区域左上角坐标
            w, h (int): 原图内识别区域宽度和高度
            target_images (str): 待识别的子图（用`|`分隔）
            sim (float, optional): 相似度（0~1，默认0.9）
            type (int, optional): 算法类型（0-5，推荐3或5，其他效率较低）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            return_all (bool, optional): TRUE表示返回所有匹配结果（仅type=3/4/5支持，自动去重矩形）
            show_viewer (bool, optional): 识别后是否打开查看器
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含所有匹配点
        """
        # 将Python bytes转换为ctypes POINTER(ctypes.c_ubyte)
        buffer_type = ctypes.c_ubyte * data_size
        buffer = buffer_type.from_buffer_copy(data)
        return self.HCFI_FindRangeImageTemByMem(window_index, buffer, data_size, x, y, w, h, target_images.encode('utf-8'), sim, type, is_gray, return_all, show_viewer)
        
    def find_image_tem_from_mem(self, window_index, subimage_mem_info, sim=0.9, type=5, is_gray=False, return_all=False, show_viewer=False):
        """
        子图数据从内存加载（而非文件），识别目标窗口
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            subimage_mem_info (str): 子图内存地址集合字符串，格式为"地址1,长度1|地址2,长度2|..."（十进制表示）
            sim (float, optional): 相似度（0~1，默认0.9）
            type (int, optional): 算法类型（0-5，推荐3或5，其他效率较低）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            return_all (bool, optional): TRUE表示返回所有匹配结果（仅type=3/4/5支持，自动去重矩形）
            show_viewer (bool, optional): 识别后是否打开查看器
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含所有匹配点
        """
        return self.HCFI_FindImageTemFromMem(window_index, subimage_mem_info.encode('utf-8'), sim, type, is_gray, return_all, show_viewer)
        
    def find_range_image_tem_from_mem(self, window_index, x, y, w, h, subimage_mem_info, sim=0.9, type=5, is_gray=False, return_all=False, show_viewer=False):
        """
        子图数据从内存加载（而非文件），识别目标窗口指定区域
        
        参数:
            window_index (int): 目标窗口序号（从1开始）
            x, y (int): 识别区域左上角坐标
            w, h (int): 识别区域宽度和高度
            subimage_mem_info (str): 子图内存地址集合字符串，格式为"地址1,长度1|地址2,长度2|..."（十进制表示）
            sim (float, optional): 相似度（0~1，默认0.9）
            type (int, optional): 算法类型（0-5，推荐3或5，其他效率较低）
            is_gray (bool, optional): 是否以灰度图处理（推荐开启）
            return_all (bool, optional): TRUE表示返回所有匹配结果（仅type=3/4/5支持，自动去重矩形）
            show_viewer (bool, optional): 识别后是否打开查看器
        
        返回值:
            int: 1表示找到，≤0表示未找到或错误；JSON格式结果包含所有匹配点
        """
        return self.HCFI_FindRangeImageTemFromMem(window_index, x, y, w, h, subimage_mem_info.encode('utf-8'), sim, type, is_gray, return_all, show_viewer)


def create_fi(dll_path=None, is_debug=False):
    """
    创建HCFI模块实例
    
    参数:
        dll_path (str, optional): DLL文件路径，如果为None则使用默认路径
        is_debug (bool, optional): 是否使用调试版DLL，默认为False
    
    返回值:
        HCFI: HCFI模块实例
    """
    return HDModuleFactory.create_instance(HCFI, dll_path, is_debug)