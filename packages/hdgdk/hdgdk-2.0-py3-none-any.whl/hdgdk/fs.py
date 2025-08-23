#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD RPG引擎框架(GDK)找字模块(FS)Python封装
提供字库管理、文字查找和OCR识别等功能
"""

import ctypes
from .base_module import HDModuleBase, HDModuleFactory


class HDFS(HDModuleBase):
    """HD RPG引擎框架找字模块(FS)的Python封装类"""
    
    def _initialize_functions(self):
        """初始化DLL函数绑定"""
        # 字库管理函数
        self.HCFS_SetDictFile = self.dll.HCFS_SetDictFile
        self.HCFS_SetDictFile.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
        self.HCFS_SetDictFile.restype = ctypes.c_int64
        
        self.HCFS_SetDictFileEx = self.dll.HCFS_SetDictFileEx
        self.HCFS_SetDictFileEx.argtypes = [ctypes.c_int32, ctypes.c_char_p]
        self.HCFS_SetDictFileEx.restype = ctypes.c_int64
        
        self.HCFS_SetDictFileExx = self.dll.HCFS_SetDictFileExx
        self.HCFS_SetDictFileExx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p]
        self.HCFS_SetDictFileExx.restype = ctypes.c_int64
        
        self.HCFS_SwitchCurDictFile = self.dll.HCFS_SwitchCurDictFile
        self.HCFS_SwitchCurDictFile.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.HCFS_SwitchCurDictFile.restype = ctypes.c_int64
        
        self.HCFS_GetCurDictInfo = self.dll.HCFS_GetCurDictInfo
        self.HCFS_GetCurDictInfo.argtypes = [ctypes.c_int32]
        self.HCFS_GetCurDictInfo.restype = ctypes.c_int64
        
        self.HCFS_GetCurDictIndex = self.dll.HCFS_GetCurDictIndex
        self.HCFS_GetCurDictIndex.argtypes = [ctypes.c_int32]
        self.HCFS_GetCurDictIndex.restype = ctypes.c_int64
        
        # 文字查找函数
        self.HCFS_FindStr = self.dll.HCFS_FindStr
        self.HCFS_FindStr.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                      ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                      ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.HCFS_FindStr.restype = ctypes.c_int64
        
        self.HCFS_FindStrEx = self.dll.HCFS_FindStrEx
        self.HCFS_FindStrEx.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                        ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.HCFS_FindStrEx.restype = ctypes.c_int64
        
        self.HCFS_FindStrExx = self.dll.HCFS_FindStrExx
        self.HCFS_FindStrExx.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                         ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                         ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.HCFS_FindStrExx.restype = ctypes.c_int64
        
        self.HCFS_FindStrMutilVPoints = self.dll.HCFS_FindStrMutilVPoints
        self.HCFS_FindStrMutilVPoints.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                                  ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                                  ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.HCFS_FindStrMutilVPoints.restype = ctypes.c_int64
        
        self.HCFS_FindStrMutilHVPoints = self.dll.HCFS_FindStrMutilHVPoints
        self.HCFS_FindStrMutilHVPoints.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                                   ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                                   ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.HCFS_FindStrMutilHVPoints.restype = ctypes.c_int64
        
        # 从文件/内存找字的扩展函数
        self.HCFS_FindStrMutilVPointsByFile = self.dll.HCFS_FindStrMutilVPointsByFile
        self.HCFS_FindStrMutilVPointsByFile.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                                        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                                        ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool, 
                                                        ctypes.c_char_p]
        self.HCFS_FindStrMutilVPointsByFile.restype = ctypes.c_int64
        
        self.HCFS_FindStrMutilVPointsByMem = self.dll.HCFS_FindStrMutilVPointsByMem
        self.HCFS_FindStrMutilVPointsByMem.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                                       ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                                       ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool, 
                                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32]
        self.HCFS_FindStrMutilVPointsByMem.restype = ctypes.c_int64
        
        self.HCFS_FindStrMutilHVPointsByFile = self.dll.HCFS_FindStrMutilHVPointsByFile
        self.HCFS_FindStrMutilHVPointsByFile.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                                         ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                                         ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool, 
                                                         ctypes.c_char_p]
        self.HCFS_FindStrMutilHVPointsByFile.restype = ctypes.c_int64
        
        self.HCFS_FindStrMutilHVPointsByMem = self.dll.HCFS_FindStrMutilHVPointsByMem
        self.HCFS_FindStrMutilHVPointsByMem.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                                        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long, 
                                                        ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool, 
                                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32]
        self.HCFS_FindStrMutilHVPointsByMem.restype = ctypes.c_int64
        
        # OCR识别函数
        self.HCFS_Ocr = self.dll.HCFS_Ocr
        self.HCFS_Ocr.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                 ctypes.c_char_p, ctypes.c_double, ctypes.c_long, ctypes.c_int32, 
                                 ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.HCFS_Ocr.restype = ctypes.c_int64
        
        self.HCFS_OcrByFile = self.dll.HCFS_OcrByFile
        self.HCFS_OcrByFile.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                       ctypes.c_char_p, ctypes.c_double, ctypes.c_char_p, ctypes.c_int32, 
                                       ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.HCFS_OcrByFile.restype = ctypes.c_int64
        
        self.HCFS_OcrByMem = self.dll.HCFS_OcrByMem
        self.HCFS_OcrByMem.argtypes = [ctypes.c_int32, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, 
                                      ctypes.c_char_p, ctypes.c_double, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, 
                                      ctypes.c_int32, ctypes.c_int32, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.HCFS_OcrByMem.restype = ctypes.c_int64
        
    def set_dict_file(self, window_index, dict_index, file_path):
        """
        设置当前像素识字的字库文件（为提高识别效率，不支持多线程）
        
        参数:
            window_index (int): 窗口序号
            dict_index (int): 字库序号（≥0，<0用于错误返回值）
            file_path (str): 字库文件名字（可加路径）
        
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        
        备注:
            - 字库文件在资源路径下寻找，需调用`HCRES_SetResPath`设置路径
            - 设置后自动解析字库数据，初始化需全部设置好，运行中不可修改
        """
        return self.HCFS_SetDictFile(window_index, dict_index, file_path.encode('utf-8'))
        
    def set_dict_file_ex(self, dict_index, file_path):
        """
        设置当前像素识字的字库文件（不支持多线程）
        
        参数:
            dict_index (int): 字库序号（≥0，<0用于错误返回值）
            file_path (str): 字库文件名字（可加路径）
        
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        return self.HCFS_SetDictFileEx(dict_index, file_path.encode('utf-8'))
        
    def set_dict_file_exx(self, window_index, dict_index, file_path, password=None):
        """
        设置当前像素识字的字库文件（不支持多线程）
        
        参数:
            window_index (int): 窗口序号
            dict_index (int): 字库序号（≥0，<0用于错误返回值）
            file_path (str): 字库文件名字（可加路径）
            password (str, optional): 密码（使用综合工具加密）
        
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        password_ptr = password.encode('utf-8') if password else None
        return self.HCFS_SetDictFileExx(window_index, dict_index, file_path.encode('utf-8'), password_ptr)
        
    def switch_cur_dict_file(self, window_index, dict_index):
        """
        切换当前像素识字的字库文件（支持多线程）
        
        参数:
            window_index (int): 窗口序号
            dict_index (int): 字库序号
        
        返回值:
            int: 操作结果，具体错误码参考HD返回值表
        """
        return self.HCFS_SwitchCurDictFile(window_index, dict_index)
        
    def get_cur_dict_info(self, window_index):
        """
        获取当前线程的加载后的字库文件信息（支持多线程）
        
        参数:
            window_index (int): 窗口序号
        
        返回值:
            int: 操作结果，返回JSON格式信息，具体错误码参考HD返回值表
        """
        return self.HCFS_GetCurDictInfo(window_index)
        
    def get_cur_dict_index(self, window_index):
        """
        获取当前线程绑定的字库索引（支持多线程）
        
        参数:
            window_index (int): 窗口序号
        
        返回值:
            int: 操作结果，返回≥0的值为当前线程绑定的字库索引
        """
        return self.HCFS_GetCurDictIndex(window_index)
        
    def find_str(self, window_index, find_x, find_y, find_w, find_h, search_str, delta_color,
                sim=0.8, bfx=1, dir_type=0, space_h=11, space_v=11, ground_rate=0.1, b_one11=True):
        """
        在客户区范围内找字（只支持单字符串且字库为单字符字库）
        
        参数:
            window_index (int): 窗口序号（从1开始，0表示全局全屏识别）
            find_x/find_y (int): 矩形范围左上角x/y坐标
            find_w/find_h (int): 矩形范围宽度/高度
            search_str (str): 需要找的字符串
            delta_color (str): 偏色（如`ffffff-000000|1c1c1c-000000`，RGB十六进制）
            sim (float, optional): 整个像素矩阵的相似度，默认为0.8
            bfx (int, optional): 是否开启反向相似度，默认为1（开启）
            dir_type (int, optional): 排序类型/方向类型，默认为0
            space_h (int, optional): 字体水平间距，默认为11像素
            space_v (int, optional): 字体垂直间距，默认为11像素
            ground_rate (float, optional): 一个字的周围占比，默认为0.1
            b_one11 (bool, optional): 一个字是否独占11像素，默认为True
        
        返回值:
            int: 操作结果，>0表示找到（高4字节为y，低4字节为x）
        """
        return self.HCFS_FindStr(window_index, find_x, find_y, find_w, find_h,
                                search_str.encode('utf-8'), delta_color.encode('utf-8'),
                                sim, bfx, dir_type, space_h, space_v, ground_rate, b_one11)
        
    def find_str_ex(self, window_index, find_x, find_y, find_w, find_h, search_str, delta_color,
                   sim=0.8, bfx=1, dir_type=0, space_h=11, space_v=11, ground_rate=0.1, b_one11=True):
        """
        在客户区范围内找字（支持多字符串且字库为单字符字库）
        
        参数:
            window_index (int): 窗口序号
            find_x/find_y (int): 矩形范围左上角x/y坐标
            find_w/find_h (int): 矩形范围宽度/高度
            search_str (str): 需要找的字符串（支持多字符串，如"大理|无量山|溶洞"）
            delta_color (str): 偏色
            sim (float, optional): 相似度，默认为0.8
            bfx (int, optional): 是否开启反向相似度，默认为1
            dir_type (int, optional): 排序类型，默认为0
            space_h (int, optional): 字体水平间距，默认为11
            space_v (int, optional): 字体垂直间距，默认为11
            ground_rate (float, optional): 字周围占比，默认为0.1
            b_one11 (bool, optional): 一个字是否独占11像素，默认为True
        
        返回值:
            int: 操作结果，1表示找到，<0表示错误或未找到
        """
        return self.HCFS_FindStrEx(window_index, find_x, find_y, find_w, find_h,
                                  search_str.encode('utf-8'), delta_color.encode('utf-8'),
                                  sim, bfx, dir_type, space_h, space_v, ground_rate, b_one11)
        
    # 其他函数的封装类似，这里省略部分实现
    
    def ocr(self, window_index, find_x, find_y, find_w, find_h, delta_color,
           sim=0.8, bfx=1, dir_type=0, space_h=11, space_v=11, ground_rate=0.1, b_one11=True):
        """
        在客户区范围内识别字（字库为字符串或单字，支持拼接+字符串）
        
        参数:
            window_index (int): 窗口序号
            find_x/find_y (int): 矩形范围左上角x/y坐标
            find_w/find_h (int): 矩形范围宽度/高度
            delta_color (str): 偏色
            sim (float, optional): 相似度，默认为0.8
            bfx (int, optional): 是否开启反向相似度，默认为1
            dir_type (int, optional): 排序类型，默认为0
            space_h (int, optional): 字体水平间距，默认为11
            space_v (int, optional): 字体垂直间距，默认为11
            ground_rate (float, optional): 字周围占比，默认为0.1
            b_one11 (bool, optional): 一个字是否独占11像素，默认为True
        
        返回值:
            int: 操作结果，1表示找到，<0表示错误或未找到
        """
        return self.HCFS_Ocr(window_index, find_x, find_y, find_w, find_h,
                            delta_color.encode('utf-8'), sim, bfx, dir_type,
                            space_h, space_v, ground_rate, b_one11)
        
    def ocr_by_file(self, window_index, find_x, find_y, find_w, find_h, color_format,
                   sim=0.8, image_name=None, bfx=1, dir_type=0, space_h=11, space_v=11, ground_rate=0.1, b_one11=True):
        """
        在客户区范围内识别字（从指定图片文件获取数据）
        
        参数:
            window_index (int): 窗口序号
            find_x/find_y (int): 矩形范围左上角x/y坐标
            find_w/find_h (int): 矩形范围宽度/高度
            color_format (str): 偏色
            sim (float, optional): 相似度，默认为0.8
            image_name (str, optional): 指定识字的图片文件，.bmp格式
            bfx (int, optional): 是否开启反向相似度，默认为1
            dir_type (int, optional): 排序类型，默认为0
            space_h (int, optional): 字体水平间距，默认为11
            space_v (int, optional): 字体垂直间距，默认为11
            ground_rate (float, optional): 字周围占比，默认为0.1
            b_one11 (bool, optional): 一个字是否独占11像素，默认为True
        
        返回值:
            int: 操作结果，1表示找到，<0表示错误或未找到
        """
        return self.HCFS_OcrByFile(window_index, find_x, find_y, find_w, find_h,
                                  color_format.encode('utf-8'), sim,
                                  image_name.encode('utf-8') if image_name else None,
                                  bfx, dir_type, space_h, space_v, ground_rate, b_one11)
        


def create_fs(dll_path=None, is_debug=False):
    """
    创建HDFS模块实例
    
    参数:
        dll_path (str, optional): DLL文件路径，如果为None则使用默认路径
        is_debug (bool, optional): 是否使用调试版DLL，默认为False
    
    返回值:
        HDFS: HDFS模块实例
    """
    return HDModuleFactory.create_instance(HDFS, dll_path, is_debug)