#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD RPG引擎框架(GDK)找图模块(FP)Python封装
提供截图、找色、找图、卡屏检测等功能
"""

import ctypes
from .base_module import HDModuleBase, HDModuleFactory

class HDFP(HDModuleBase):
    """
    HD RPG引擎框架找图模块(FP)Python封装
    提供截图、找色、找图、卡屏检测等功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化找图模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
    
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 一、截图功能函数
        # HCFP_Capture - 截图并保存为.bmp文件
        self.HCFP_Capture = getattr(self.dll, 'HCFP_Capture', None)
        if self.HCFP_Capture:
            self.HCFP_Capture.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # fileNamePath
                ctypes.c_bool    # 是否打开查看器
            ]
            self.HCFP_Capture.restype = ctypes.c_int64
        
        # 二、找色功能函数
        # 1. 单点找色
        # HCFP_FindColor - 在指定区域内查找单个目标颜色
        self.HCFP_FindColor = getattr(self.dll, 'HCFP_FindColor', None)
        if self.HCFP_FindColor:
            self.HCFP_FindColor.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # deltaColor
                ctypes.c_double, # sim
                ctypes.c_int32   # dirType
            ]
            self.HCFP_FindColor.restype = ctypes.c_int64
        
        # 2. 多点找色
        # HCFP_FindColors - 在指定区域内查找多个目标颜色
        self.HCFP_FindColors = getattr(self.dll, 'HCFP_FindColors', None)
        if self.HCFP_FindColors:
            self.HCFP_FindColors.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # deltaColor
                ctypes.c_double, # sim
                ctypes.c_int32   # dirType
            ]
            self.HCFP_FindColors.restype = ctypes.c_int64
        
        # 3. 多点偏移找色
        # HCFP_FindColorsOffset - 先找首色，再匹配首色偏移位置的颜色
        self.HCFP_FindColorsOffset = getattr(self.dll, 'HCFP_FindColorsOffset', None)
        if self.HCFP_FindColorsOffset:
            self.HCFP_FindColorsOffset.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # firstDeltaColor
                ctypes.c_char_p, # deltaColor
                ctypes.c_double, # sim
                ctypes.c_int32,  # bALL
                ctypes.c_int32   # dirType
            ]
            self.HCFP_FindColorsOffset.restype = ctypes.c_int64
        
        # 4. 颜色比较
        # HCFP_CmpColors - 比较指定点颜色是否匹配目标颜色
        self.HCFP_CmpColors = getattr(self.dll, 'HCFP_CmpColors', None)
        if self.HCFP_CmpColors:
            self.HCFP_CmpColors.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_char_p  # deltaColor
            ]
            self.HCFP_CmpColors.restype = ctypes.c_int64
        
        # HCFP_CmpColorExs - 通过多个具体坐标点的颜色匹配确定图像块
        self.HCFP_CmpColorExs = getattr(self.dll, 'HCFP_CmpColorExs', None)
        if self.HCFP_CmpColorExs:
            self.HCFP_CmpColorExs.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_char_p  # deltaXYColor
            ]
            self.HCFP_CmpColorExs.restype = ctypes.c_int64
        
        # 5. 获取颜色值
        # HCFP_GetColor - 获取指定点的颜色值（ARGB格式）
        self.HCFP_GetColor = getattr(self.dll, 'HCFP_GetColor', None)
        if self.HCFP_GetColor:
            self.HCFP_GetColor.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32   # y
            ]
            self.HCFP_GetColor.restype = ctypes.c_int64
        
        # 三、找图功能函数
        # 1. 单图查找
        # HCFP_FindPic - 在指定区域内查找单张图片（.bmp）
        self.HCFP_FindPic = getattr(self.dll, 'HCFP_FindPic', None)
        if self.HCFP_FindPic:
            self.HCFP_FindPic.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # 图片名字
                ctypes.c_char_p, # deltaColor
                ctypes.c_double, # sim
                ctypes.c_int32   # dirType
            ]
            self.HCFP_FindPic.restype = ctypes.c_int64
        
        # 2. 多图查找（找到一个即返回）
        # HCFP_FindPicEx - 在指定区域内查找多张图片，找到其中一张即返回
        self.HCFP_FindPicEx = getattr(self.dll, 'HCFP_FindPicEx', None)
        if self.HCFP_FindPicEx:
            self.HCFP_FindPicEx.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # 图片名字集合
                ctypes.c_char_p, # deltaColor
                ctypes.c_double, # sim
                ctypes.c_int32   # dirType
            ]
            self.HCFP_FindPicEx.restype = ctypes.c_int64
        
        # 3. 多图查找（返回全部结果）
        # HCFP_FindPicExx - 在指定区域内查找多张图片，返回全部匹配结果
        self.HCFP_FindPicExx = getattr(self.dll, 'HCFP_FindPicExx', None)
        if self.HCFP_FindPicExx:
            self.HCFP_FindPicExx.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # 图片名字集合
                ctypes.c_char_p, # deltaColor
                ctypes.c_double, # sim
                ctypes.c_bool,   # bAll
                ctypes.c_int32   # dirType
            ]
            self.HCFP_FindPicExx.restype = ctypes.c_int64
        
        # 四、卡屏检测与校验函数
        # HCFP_IsDisplayDead - 检测指定区域在指定时间内是否卡屏
        self.HCFP_IsDisplayDead = getattr(self.dll, 'HCFP_IsDisplayDead', None)
        if self.HCFP_IsDisplayDead:
            self.HCFP_IsDisplayDead.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_int32   # mstime
            ]
            self.HCFP_IsDisplayDead.restype = ctypes.c_int64
        
        # HCFP_GetRangeCRC - 获取指定区域的像素CRC值，用于卡屏校验
        self.HCFP_GetRangeCRC = getattr(self.dll, 'HCFP_GetRangeCRC', None)
        if self.HCFP_GetRangeCRC:
            self.HCFP_GetRangeCRC.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32   # h
            ]
            self.HCFP_GetRangeCRC.restype = ctypes.c_int64
        
        # 五、从文件/内存中操作的扩展函数
        # 1. 找色扩展
        self.HCFP_FindColorByFile = getattr(self.dll, 'HCFP_FindColorByFile', None)
        if self.HCFP_FindColorByFile:
            self.HCFP_FindColorByFile.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # deltaColor
                ctypes.c_double, # sim
                ctypes.c_int32,  # dirType
                ctypes.c_char_p  # orgImageName
            ]
            self.HCFP_FindColorByFile.restype = ctypes.c_int64
        
        self.HCFP_FindColorByMem = getattr(self.dll, 'HCFP_FindColorByMem', None)
        if self.HCFP_FindColorByMem:
            self.HCFP_FindColorByMem.argtypes = [
                ctypes.c_int32,  # 窗口序号
                ctypes.c_int32,  # x
                ctypes.c_int32,  # y
                ctypes.c_int32,  # w
                ctypes.c_int32,  # h
                ctypes.c_char_p, # deltaColor
                ctypes.c_double, # sim
                ctypes.c_int32,  # dirType
                ctypes.c_void_p, # data
                ctypes.c_int32   # dataSize
            ]
            self.HCFP_FindColorByMem.restype = ctypes.c_int64
        
        # 其他扩展函数的绑定类似，这里省略...
    
    # 截图功能
    def capture(self, window_index, x, y, w, h, file_path, open_viewer=False):
        """
        截图并保存为.bmp文件
        
        Args:
            window_index (int): 目标窗口序号（从1开始，0表示全局全屏识别）
            x (int): 矩形范围左上角x坐标
            y (int): 矩形范围左上角y坐标
            w (int): 矩形范围宽度
            h (int): 矩形范围高度
            file_path (str): 保存路径+文件名（需带.bmp后缀）
            open_viewer (bool): 截图后是否打开查看器
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self.HCFP_Capture:
            raise NotImplementedError("HCFP_Capture函数未实现或DLL未正确加载")
        
        return self.HCFP_Capture(
            window_index,
            x, y, w, h,
            file_path.encode('utf-8'),
            open_viewer
        )
    
    # 找色功能
    def find_color(self, window_index, x, y, w, h, delta_color, sim=0.9, dir_type=0):
        """
        在指定区域内查找单个目标颜色
        
        Args:
            window_index (int): 目标窗口序号（0表示全局）
            x, y (int): 查找区域左上角坐标
            w, h (int): 查找区域宽度和高度
            delta_color (str): 偏色（格式XXXXXX-YYYYYY|...，RGB十六进制，支持多个颜色）
            sim (float): 相似度（0~1）
            dir_type (int): 排序/方向类型
            
        Returns:
            tuple or None: 找到返回(x, y)坐标元组，未找到返回None
        """
        if not self.HCFP_FindColor:
            raise NotImplementedError("HCFP_FindColor函数未实现或DLL未正确加载")
        
        result = self.HCFP_FindColor(
            window_index,
            x, y, w, h,
            delta_color.encode('utf-8'),
            sim,
            dir_type
        )
        
        if result > 0:
            # 高4字节为x，低4字节为y
            x_coord = (result >> 32) & 0xFFFFFFFF
            y_coord = result & 0xFFFFFFFF
            return (x_coord, y_coord)
        return None
    
    def find_colors(self, window_index, x, y, w, h, delta_color, sim=0.9, dir_type=0):
        """
        在指定区域内查找多个目标颜色
        
        Args:
            同find_color，delta_color支持多颜色组合
            
        Returns:
            int: 找到的数量
        """
        if not self.HCFP_FindColors:
            raise NotImplementedError("HCFP_FindColors函数未实现或DLL未正确加载")
        
        return self.HCFP_FindColors(
            window_index,
            x, y, w, h,
            delta_color.encode('utf-8'),
            sim,
            dir_type
        )
    
    def find_colors_offset(self, window_index, x, y, w, h, first_delta_color, delta_color, 
                          sim=0.9, find_all=False, dir_type=0):
        """
        先找首色，再匹配首色偏移位置的颜色
        
        Args:
            window_index (int): 目标窗口序号
            x, y, w, h (int): 查找区域
            first_delta_color (str): 首色（格式XXXXXX-YYYYYY）
            delta_color (str): 偏移色（格式x1|y1|XXXXXX-YYYYYY|...）
            sim (float): 相似度
            find_all (bool): False表示找到一个即返回，True表示返回全部结果
            dir_type (int): 方向类型
            
        Returns:
            tuple or int: find_all=False返回(x, y)坐标元组；find_all=True返回找到的数量
        """
        if not self.HCFP_FindColorsOffset:
            raise NotImplementedError("HCFP_FindColorsOffset函数未实现或DLL未正确加载")
        
        result = self.HCFP_FindColorsOffset(
            window_index,
            x, y, w, h,
            first_delta_color.encode('utf-8'),
            delta_color.encode('utf-8'),
            sim,
            1 if find_all else 0,
            dir_type
        )
        
        if not find_all and result > 0:
            # 高4字节为x，低4字节为y
            x_coord = (result >> 32) & 0xFFFFFFFF
            y_coord = result & 0xFFFFFFFF
            return (x_coord, y_coord)
        return result
    
    # 颜色比较
    def cmp_colors(self, window_index, x, y, delta_color):
        """
        比较指定点颜色是否匹配目标颜色
        
        Args:
            window_index (int): 目标窗口序号
            x, y (int): 目标点坐标
            delta_color (str): 目标颜色（格式XXXXXX-YYYYYY）
            
        Returns:
            bool: 匹配返回True，否则返回False
        """
        if not self.HCFP_CmpColors:
            raise NotImplementedError("HCFP_CmpColors函数未实现或DLL未正确加载")
        
        result = self.HCFP_CmpColors(
            window_index,
            x, y,
            delta_color.encode('utf-8')
        )
        
        return result == 1
    
    def cmp_color_exs(self, window_index, delta_xy_color):
        """
        通过多个具体坐标点的颜色匹配确定图像块
        
        Args:
            window_index (int): 目标窗口序号
            delta_xy_color (str): 格式x1|y1|XXXXXX-YYYYYY|...（多个坐标及对应颜色）
            
        Returns:
            tuple or None: 找到返回(x, y)坐标元组，未找到返回None
        """
        if not self.HCFP_CmpColorExs:
            raise NotImplementedError("HCFP_CmpColorExs函数未实现或DLL未正确加载")
        
        result = self.HCFP_CmpColorExs(
            window_index,
            delta_xy_color.encode('utf-8')
        )
        
        if result > 0:
            # 低4字节x1，高4字节y1
            x_coord = result & 0xFFFFFFFF
            y_coord = (result >> 32) & 0xFFFFFFFF
            return (x_coord, y_coord)
        return None
    
    # 获取颜色值
    def get_color(self, window_index, x, y):
        """
        获取指定点的颜色值（ARGB格式）
        
        Args:
            window_index (int): 目标窗口序号
            x, y (int): 目标点坐标
            
        Returns:
            int or None: 颜色值（4字节ARGB），获取失败返回None
        """
        if not self.HCFP_GetColor:
            raise NotImplementedError("HCFP_GetColor函数未实现或DLL未正确加载")
        
        result = self.HCFP_GetColor(window_index, x, y)
        
        if result > 0:
            return result
        return None
    
    # 找图功能
    def find_pic(self, window_index, x, y, w, h, pic_name, delta_color="", sim=0.9, dir_type=0):
        """
        在指定区域内查找单张图片（.bmp）
        
        Args:
            window_index (int): 目标窗口序号
            x, y, w, h (int): 查找区域
            pic_name (str): 图片文件名（路径通过HCRES_SetResPath设置）
            delta_color (str): 偏色（RGB十六进制）
            sim (float): 相似度（0~1）
            dir_type (int): 方向类型
            
        Returns:
            tuple or None: 找到返回(x, y)坐标元组，未找到返回None
        """
        if not self.HCFP_FindPic:
            raise NotImplementedError("HCFP_FindPic函数未实现或DLL未正确加载")
        
        result = self.HCFP_FindPic(
            window_index,
            x, y, w, h,
            pic_name.encode('utf-8'),
            delta_color.encode('utf-8'),
            sim,
            dir_type
        )
        
        if result > 0:
            # 低4字节x，高4字节y
            x_coord = result & 0xFFFFFFFF
            y_coord = (result >> 32) & 0xFFFFFFFF
            return (x_coord, y_coord)
        return None
    
    def find_pic_ex(self, window_index, x, y, w, h, pic_names, delta_color="", sim=0.9, dir_type=0):
        """
        在指定区域内查找多张图片，找到其中一张即返回
        
        Args:
            window_index (int): 目标窗口序号
            x, y, w, h (int): 查找区域
            pic_names (list or str): 多张图片名（列表或用|分隔的字符串，如"pic1.bmp|pic2.bmp"）
            delta_color (str): 偏色
            sim (float): 相似度
            dir_type (int): 方向类型
            
        Returns:
            tuple or None: 找到返回(x, y)坐标元组，未找到返回None
        """
        if not self.HCFP_FindPicEx:
            raise NotImplementedError("HCFP_FindPicEx函数未实现或DLL未正确加载")
        
        # 处理图片名参数
        if isinstance(pic_names, list):
            pic_names_str = "|".join(pic_names)
        else:
            pic_names_str = pic_names
        
        result = self.HCFP_FindPicEx(
            window_index,
            x, y, w, h,
            pic_names_str.encode('utf-8'),
            delta_color.encode('utf-8'),
            sim,
            dir_type
        )
        
        if result > 0:
            # 低4字节x，高4字节y
            x_coord = result & 0xFFFFFFFF
            y_coord = (result >> 32) & 0xFFFFFFFF
            return (x_coord, y_coord)
        return None
    
    def find_pic_exx(self, window_index, x, y, w, h, pic_names, delta_color="", sim=0.9, 
                     find_all_for_each=True, dir_type=0):
        """
        在指定区域内查找多张图片，返回全部匹配结果
        
        Args:
            window_index (int): 目标窗口序号
            x, y, w, h (int): 查找区域
            pic_names (list or str): 多张图片名
            delta_color (str): 偏色
            sim (float): 相似度
            find_all_for_each (bool): True表示每个图片找全部匹配，False表示每个图片找一次
            dir_type (int): 方向类型
            
        Returns:
            bool: 找到返回True，未找到返回False
        """
        if not self.HCFP_FindPicExx:
            raise NotImplementedError("HCFP_FindPicExx函数未实现或DLL未正确加载")
        
        # 处理图片名参数
        if isinstance(pic_names, list):
            pic_names_str = "|".join(pic_names)
        else:
            pic_names_str = pic_names
        
        result = self.HCFP_FindPicExx(
            window_index,
            x, y, w, h,
            pic_names_str.encode('utf-8'),
            delta_color.encode('utf-8'),
            sim,
            find_all_for_each,
            dir_type
        )
        
        return result == 1
    
    # 卡屏检测与校验
    def is_display_dead(self, window_index, x, y, w, h, ms_time=1000):
        """
        检测指定区域在指定时间内是否卡屏
        
        Args:
            window_index (int): 目标窗口序号
            x, y, w, h (int): 检测区域
            ms_time (int): 检测间隔时间（毫秒）
            
        Returns:
            bool: 卡屏返回True，否则返回False
        """
        if not self.HCFP_IsDisplayDead:
            raise NotImplementedError("HCFP_IsDisplayDead函数未实现或DLL未正确加载")
        
        result = self.HCFP_IsDisplayDead(window_index, x, y, w, h, ms_time)
        
        return result == 1
    
    def get_range_crc(self, window_index, x, y, w, h):
        """
        获取指定区域的像素CRC值，用于卡屏校验
        
        Args:
            window_index (int): 目标窗口序号
            x, y, w, h (int): 检测区域
            
        Returns:
            int: CRC值
        """
        if not self.HCFP_GetRangeCRC:
            raise NotImplementedError("HCFP_GetRangeCRC函数未实现或DLL未正确加载")
        
        return self.HCFP_GetRangeCRC(window_index, x, y, w, h)
    
    # 从文件/内存中操作的扩展函数
    def find_color_by_file(self, window_index, x, y, w, h, delta_color, sim=0.9, 
                          dir_type=0, org_image_name=None):
        """
        从指定图片文件中单点找色
        
        Args:
            同find_color，新增org_image_name（图片路径）
            
        Returns:
            tuple or None: 找到返回(x, y)坐标元组，未找到返回None
        """
        if not self.HCFP_FindColorByFile:
            raise NotImplementedError("HCFP_FindColorByFile函数未实现或DLL未正确加载")
        
        result = self.HCFP_FindColorByFile(
            window_index,
            x, y, w, h,
            delta_color.encode('utf-8'),
            sim,
            dir_type,
            org_image_name.encode('utf-8') if org_image_name else None
        )
        
        if result > 0:
            # 高4字节为x，低4字节为y
            x_coord = (result >> 32) & 0xFFFFFFFF
            y_coord = result & 0xFFFFFFFF
            return (x_coord, y_coord)
        return None
    
    def find_color_by_mem(self, window_index, x, y, w, h, delta_color, sim=0.9, 
                         dir_type=0, data=None, data_size=0):
        """
        从内存图片数据中单点找色
        
        Args:
            同find_color，新增data（数据地址）和data_size（数据大小）
            
        Returns:
            tuple or None: 找到返回(x, y)坐标元组，未找到返回None
        """
        if not self.HCFP_FindColorByMem:
            raise NotImplementedError("HCFP_FindColorByMem函数未实现或DLL未正确加载")
        
        result = self.HCFP_FindColorByMem(
            window_index,
            x, y, w, h,
            delta_color.encode('utf-8'),
            sim,
            dir_type,
            data,
            data_size
        )
        
        if result > 0:
            # 高4字节为x，低4字节为y
            x_coord = (result >> 32) & 0xFFFFFFFF
            y_coord = result & 0xFFFFFFFF
            return (x_coord, y_coord)
        return None

# 工厂函数
def create_fp(dll_path=None, is_debug=None):
    """
    创建找图模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HDFP: 找图模块实例
    """
    return HDModuleFactory.create_instance(HDFP, dll_path, is_debug)