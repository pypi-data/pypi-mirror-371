#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD RPG引擎框架(GDK)窗口模块(WIN)封装

该模块提供窗口排序、进程伪装、窗口状态操作、信息获取及枚举等功能
支持对窗口句柄、进程ID、窗口位置、大小等进行管理和查询
"""
from ctypes import c_int64, c_int32, c_void_p, c_char_p, byref
from .base_module import HDModuleBase


class HDWIN(HDModuleBase):
    """窗口模块封装类"""
    
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化窗口模块
        
        Args:
            dll_path: DLL文件所在路径
            is_debug: 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        self._bind_functions()
        
    def _initialize_functions(self):
        """初始化DLL中的函数"""
        self._bind_functions()
        
    def _bind_functions(self):
        """绑定DLL函数"""
        # 窗口排序相关函数
        try:
            self._sort_windows = getattr(self.dll, "HCWIN_SortWindows")
            self._sort_windows.argtypes = [c_int32, c_int32, c_int32, c_int32]
            self._sort_windows.restype = c_int64
        except AttributeError:
            self._sort_windows = None
        
        # 进程伪装相关函数
        try:
            self._camouflage_process = getattr(self.dll, "HCWIN_CamouflageProcess")
            self._camouflage_process.argtypes = [c_char_p, c_char_p, c_int32]
            self._camouflage_process.restype = c_int64
        except AttributeError:
            self._camouflage_process = None
        
        # 窗口状态操作相关函数
        try:
            self._set_window_state = getattr(self.dll, "HCWIN_SetWindowState")
            self._set_window_state.argtypes = [c_int64, c_int32]
            self._set_window_state.restype = c_int64
        except AttributeError:
            self._set_window_state = None
        
        try:
            self._set_window_size = getattr(self.dll, "HCWIN_SetWindowSize")
            self._set_window_size.argtypes = [c_int64, c_int32, c_int32, c_int32]
            self._set_window_size.restype = c_int64
        except AttributeError:
            self._set_window_size = None
        
        try:
            self._move_window = getattr(self.dll, "HCWIN_MoveWindow")
            self._move_window.argtypes = [c_int64, c_int32, c_int32]
            self._move_window.restype = c_int64
        except AttributeError:
            self._move_window = None
        
        try:
            self._set_foreground_focus = getattr(self.dll, "HCWIN_SetForegroundFocus")
            self._set_foreground_focus.argtypes = [c_int64]
            self._set_foreground_focus.restype = c_int64
        except AttributeError:
            self._set_foreground_focus = None
        
        # 窗口信息获取相关函数
        try:
            self._is_wow64_process = getattr(self.dll, "HCWIN_IsWow64Process")
            self._is_wow64_process.argtypes = [c_int64, c_int32]
            self._is_wow64_process.restype = c_int64
        except AttributeError:
            self._is_wow64_process = None
        
        try:
            self._get_window_title = getattr(self.dll, "HCWIN_GetWindowTitle")
            self._get_window_title.argtypes = [c_int64]
            self._get_window_title.restype = c_int64
        except AttributeError:
            self._get_window_title = None
        
        try:
            self._get_window_thread_process_id = getattr(self.dll, "HCWIN_GetWindowThreadProcessId")
            self._get_window_thread_process_id.argtypes = [c_int64]
            self._get_window_thread_process_id.restype = c_int64
        except AttributeError:
            self._get_window_thread_process_id = None
        
        try:
            self._get_window_process_id = getattr(self.dll, "HCWIN_GetWindowProcessId")
            self._get_window_process_id.argtypes = [c_int64]
            self._get_window_process_id.restype = c_int64
        except AttributeError:
            self._get_window_process_id = None
        
        try:
            self._get_window_process_path = getattr(self.dll, "HCWIN_GetWindowProcessPath")
            self._get_window_process_path.argtypes = [c_int64]
            self._get_window_process_path.restype = c_int64
        except AttributeError:
            self._get_window_process_path = None
        
        try:
            self._get_window_rect = getattr(self.dll, "HCWIN_GetWindowRect")
            self._get_window_rect.argtypes = [c_int64, c_void_p]
            self._get_window_rect.restype = c_int64
        except AttributeError:
            self._get_window_rect = None
        
        try:
            self._get_window_class = getattr(self.dll, "HCWIN_GetWindowClass")
            self._get_window_class.argtypes = [c_int64]
            self._get_window_class.restype = c_int64
        except AttributeError:
            self._get_window_class = None
        
        try:
            self._get_window_state = getattr(self.dll, "HCWIN_GetWindowState")
            self._get_window_state.argtypes = [c_int64, c_int32]
            self._get_window_state.restype = c_int64
        except AttributeError:
            self._get_window_state = None
        
        try:
            self._get_special_window = getattr(self.dll, "HCWIN_GetSpecialWindow")
            self._get_special_window.argtypes = [c_int32]
            self._get_special_window.restype = c_int64
        except AttributeError:
            self._get_special_window = None
        
        try:
            self._get_window = getattr(self.dll, "HCWIN_GetWindow")
            self._get_window.argtypes = [c_int64, c_int32]
            self._get_window.restype = c_int64
        except AttributeError:
            self._get_window = None
        
        try:
            self._get_mouse_point_window = getattr(self.dll, "HCWIN_GetMousePointWindow")
            self._get_mouse_point_window.argtypes = []
            self._get_mouse_point_window.restype = c_int64
        except AttributeError:
            self._get_mouse_point_window = None
        
        try:
            self._get_point_window = getattr(self.dll, "HCWIN_GetPointWindow")
            self._get_point_window.argtypes = [c_int32, c_int32]
            self._get_point_window.restype = c_int64
        except AttributeError:
            self._get_point_window = None
        
        try:
            self._get_foreground_window = getattr(self.dll, "HCWIN_GetForegroundWindow")
            self._get_foreground_window.argtypes = []
            self._get_foreground_window.restype = c_int64
        except AttributeError:
            self._get_foreground_window = None
        
        try:
            self._get_foreground_focus = getattr(self.dll, "HCWIN_GetForegroundFocus")
            self._get_foreground_focus.argtypes = []
            self._get_foreground_focus.restype = c_int64
        except AttributeError:
            self._get_foreground_focus = None
        
        try:
            self._get_client_size = getattr(self.dll, "HCWIN_GetClientSize")
            self._get_client_size.argtypes = [c_int64, c_void_p, c_void_p]
            self._get_client_size.restype = c_int64
        except AttributeError:
            self._get_client_size = None
        
        try:
            self._get_client_rect_in_window = getattr(self.dll, "HCWIN_GetClientRectInWindow")
            self._get_client_rect_in_window.argtypes = [c_int64, c_void_p]
            self._get_client_rect_in_window.restype = c_int64
        except AttributeError:
            self._get_client_rect_in_window = None
        
        # 窗口枚举相关函数
        try:
            self._find_window_ex = getattr(self.dll, "HCWIN_FindWindowEx")
            self._find_window_ex.argtypes = [c_int64, c_char_p, c_char_p, c_int32]
            self._find_window_ex.restype = c_int64
        except AttributeError:
            self._find_window_ex = None
        
        try:
            self._find_top_window = getattr(self.dll, "HCWIN_FindTopWindow")
            self._find_top_window.argtypes = [c_char_p, c_char_p, c_int32]
            self._find_top_window.restype = c_int64
        except AttributeError:
            self._find_top_window = None
        
        try:
            self._enum_window_by_process = getattr(self.dll, "HCWIN_EnumWindowByProcess")
            self._enum_window_by_process.argtypes = [c_char_p, c_char_p, c_char_p, c_int32, c_int32]
            self._enum_window_by_process.restype = c_int64
        except AttributeError:
            self._enum_window_by_process = None
        
        try:
            self._enum_window_by_process_id = getattr(self.dll, "HCWIN_EnumWindowByProcessId")
            self._enum_window_by_process_id.argtypes = [c_int32, c_char_p, c_char_p, c_int32, c_int32]
            self._enum_window_by_process_id.restype = c_int64
        except AttributeError:
            self._enum_window_by_process_id = None
        
        try:
            self._enum_process = getattr(self.dll, "HCWIN_EnumProcess")
            self._enum_process.argtypes = [c_char_p, c_int32]
            self._enum_process.restype = c_int64
        except AttributeError:
            self._enum_process = None
        
        try:
            self._enum_window = getattr(self.dll, "HCWIN_EnumWindow")
            self._enum_window.argtypes = [c_int64, c_char_p, c_char_p, c_int32, c_int32, c_int32]
            self._enum_window.restype = c_int64
        except AttributeError:
            self._enum_window = None
    
    def sort_windows(self, offset_w, offset_h, width, height):
        """
        排序安装过插件的进程
        
        Args:
            offset_w: 水平偏移距离（相邻窗口左上角水平距离）
            offset_h: 垂直偏移距离（相邻窗口左上角垂直距离）
            width: 窗口宽度
            height: 窗口高度
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._sort_windows:
            raise NotImplementedError("HCWIN_SortWindows 函数未实现")
            
        return self._sort_windows(offset_w, offset_h, width, height)
    
    def camouflage_process(self, run_name, target_path, type_):
        """
        伪装进程（防止检查到实际进程存在）
        
        Args:
            run_name: 伪装进程的别名（如hd.dat）
            target_path: 需伪装的进程全路径（含.exe，如c:\\game.exe）
            type_: 伪装进程的位数（32或64）
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._camouflage_process:
            raise NotImplementedError("HCWIN_CamouflageProcess 函数未实现")
            
        run_name_ptr = c_char_p(run_name.encode('utf-8')) if run_name else None
        target_path_ptr = c_char_p(target_path.encode('utf-8')) if target_path else None
        
        return self._camouflage_process(run_name_ptr, target_path_ptr, type_)
    
    def set_window_state(self, hwnd, type_):
        """
        设置或操作窗口状态
        
        Args:
            hwnd: 窗口句柄（type为18/19时可设为0，用于刷新桌面）
            type_: 窗口状态类型（1-19）
                1：激活指定窗口（顶层窗口）
                2：显示最小化窗口（不激活）
                3：显示最小化窗口（激活）
                4：显示最大化窗口（激活）
                5：显示窗口（不激活）
                6：隐藏窗口
                7：显示窗口（激活）
                8：置顶窗口（顶层窗口）
                9：取消置顶窗口
                10：禁止窗口
                11：取消禁止窗口
                12：恢复并激活窗口（顶层窗口）
                13：强制结束窗口所在进程
                14：闪烁窗口
                15：窗口获取输入焦点
                16：发消息关闭窗口（非强制）
                17：强制刷新指定窗口
                18：强制刷新桌面窗口
                19：强制刷新桌面窗口+任务栏
                
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._set_window_state:
            raise NotImplementedError("HCWIN_SetWindowState 函数未实现")
            
        return self._set_window_state(hwnd, type_)
    
    def set_window_size(self, hwnd, width, height, b_center=False):
        """
        设置窗口大小
        
        Args:
            hwnd: 窗口句柄
            width: 宽度
            height: 高度
            b_center: 窗口是否居中（居中会改变窗口位置）
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._set_window_size:
            raise NotImplementedError("HCWIN_SetWindowSize 函数未实现")
            
        return self._set_window_size(hwnd, width, height, 1 if b_center else 0)
    
    def move_window(self, hwnd, x, y):
        """
        移动窗口
        
        Args:
            hwnd: 窗口句柄
            x: 屏幕坐标x
            y: 屏幕坐标y
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._move_window:
            raise NotImplementedError("HCWIN_MoveWindow 函数未实现")
            
        return self._move_window(hwnd, x, y)
    
    def is_wow64_process(self, hwnd, pid=0):
        """
        判断目标窗口句柄/进程是否为64位
        
        Args:
            hwnd: 窗口句柄
            pid: 进程PID（窗口句柄或PID任意指定一个，均指定时以PID为准）
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._is_wow64_process:
            raise NotImplementedError("HCWIN_IsWow64Process 函数未实现")
            
        return self._is_wow64_process(hwnd, pid)
    
    def get_window_title(self, hwnd):
        """
        获取目标窗口标题
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_window_title:
            raise NotImplementedError("HCWIN_GetWindowTitle 函数未实现")
            
        return self._get_window_title(hwnd)
    
    def get_window_thread_process_id(self, hwnd):
        """
        获取目标窗口句柄的线程ID
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_window_thread_process_id:
            raise NotImplementedError("HCWIN_GetWindowThreadProcessId 函数未实现")
            
        return self._get_window_thread_process_id(hwnd)
    
    def get_window_process_id(self, hwnd):
        """
        获取目标窗口句柄的进程ID
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_window_process_id:
            raise NotImplementedError("HCWIN_GetWindowProcessId 函数未实现")
            
        return self._get_window_process_id(hwnd)
    
    def get_window_process_path(self, hwnd):
        """
        获取目标窗口句柄的路径
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_window_process_path:
            raise NotImplementedError("HCWIN_GetWindowProcessPath 函数未实现")
            
        return self._get_window_process_path(hwnd)
    
    def get_window_rect(self, hwnd, p_rect=None):
        """
        获取窗口在屏幕上的位置
        
        Args:
            hwnd: 窗口句柄
            p_rect: 指向RECT结构体的地址（C/C++用），其他语言通过HCEnv_GetRetJson获取字符串
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_window_rect:
            raise NotImplementedError("HCWIN_GetWindowRect 函数未实现")
            
        return self._get_window_rect(hwnd, p_rect)
    
    def get_window_class(self, hwnd):
        """
        获取目标窗口句柄的窗口类名
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_window_class:
            raise NotImplementedError("HCWIN_GetWindowClass 函数未实现")
            
        return self._get_window_class(hwnd)
    
    def get_window_state(self, hwnd, flag):
        """
        获取目标窗口句柄的窗口状态
        
        Args:
            hwnd: 窗口句柄
            flag: 判断类型：0（窗口是否存在）、1（是否激活）、2（是否可见）、3（是否最小化）、4（是否最大化）、5（是否置顶）、6（是否无响应）、7（是否可用）、8（是否无响应，6无效时用）、9（进程是否64位）
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_window_state:
            raise NotImplementedError("HCWIN_GetWindowState 函数未实现")
            
        return self._get_window_state(hwnd, flag)
    
    def get_special_window(self, flag):
        """
        获取特殊窗口（桌面、Shell_TrayWnd）
        
        Args:
            flag: 0（桌面）、1（Shell_TrayWnd）
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_special_window:
            raise NotImplementedError("HCWIN_GetSpecialWindow 函数未实现")
            
        return self._get_special_window(flag)
    
    def get_window(self, hwnd, flag):
        """
        获取目标窗口句柄的关联窗口句柄
        
        Args:
            hwnd: 窗口句柄
            flag: 关联类型：0（父窗口）、1（第一个子窗口）、2（第一个窗口）、3（最后一个窗口）、4（下一个窗口）、5（上一个窗口）、6（拥有者窗口）、7（顶层窗口）
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_window:
            raise NotImplementedError("HCWIN_GetWindow 函数未实现")
            
        return self._get_window(hwnd, flag)
    
    def get_mouse_point_window(self):
        """
        获取当前鼠标下指向的窗口句柄
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_mouse_point_window:
            raise NotImplementedError("HCWIN_GetMousePointWindow 函数未实现")
            
        return self._get_mouse_point_window()
    
    def get_point_window(self, x, y):
        """
        获取指定坐标指向的窗口句柄
        
        Args:
            x: 屏幕坐标x
            y: 屏幕坐标y
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_point_window:
            raise NotImplementedError("HCWIN_GetPointWindow 函数未实现")
            
        return self._get_point_window(x, y)
    
    def get_foreground_window(self):
        """
        获取顶层活动窗口（可获取按键插件无法获取的句柄）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_foreground_window:
            raise NotImplementedError("HCWIN_GetForegroundWindow 函数未实现")
            
        return self._get_foreground_window()
    
    def get_foreground_focus(self):
        """
        获取顶层活动窗口中具有输入焦点的窗口句柄
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_foreground_focus:
            raise NotImplementedError("HCWIN_GetForegroundFocus 函数未实现")
            
        return self._get_foreground_focus()
    
    def set_foreground_focus(self, hwnd):
        """
        设置输入焦点到窗口
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._set_foreground_focus:
            raise NotImplementedError("HCWIN_SetForegroundFocus 函数未实现")
            
        return self._set_foreground_focus(hwnd)
    
    def get_client_size(self, hwnd, p_w=None, p_h=None):
        """
        获取窗口客户区域的宽度和高度
        
        Args:
            hwnd: 窗口句柄
            p_w: 指向宽度整数的地址（C/C++用），其他语言通过HCEnv_GetRetJson获取字符串
            p_h: 指向高度整数的地址（C/C++用），其他语言通过HCEnv_GetRetJson获取字符串
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_client_size:
            raise NotImplementedError("HCWIN_GetClientSize 函数未实现")
            
        return self._get_client_size(hwnd, p_w, p_h)
    
    def get_client_rect_in_window(self, hwnd, p_rect=None):
        """
        获取窗口客户区域在屏幕上的位置
        
        Args:
            hwnd: 窗口句柄
            p_rect: 指向RECT结构体的地址（C/C++用），其他语言通过HCEnv_GetRetJson获取字符串
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._get_client_rect_in_window:
            raise NotImplementedError("HCWIN_GetClientRectInWindow 函数未实现")
            
        return self._get_client_rect_in_window(hwnd, p_rect)
    
    def find_window_ex(self, parent_hwnd, class_name=None, title=None, b_type=False):
        """
        查找符合类名或标题名的顶层可见窗口（指定父窗口则在其第一层子窗口中查找）
        
        Args:
            parent_hwnd: 父窗口句柄（不指定则从桌面窗口搜索）
            class_name: 窗口类名（不指定为None/0）
            title: 窗口标题（不指定为None/0）
            b_type: 1（模糊匹配）、0（完全匹配）
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._find_window_ex:
            raise NotImplementedError("HCWIN_FindWindowEx 函数未实现")
            
        class_name_ptr = c_char_p(class_name.encode('utf-8')) if class_name else None
        title_ptr = c_char_p(title.encode('utf-8')) if title else None
        
        return self._find_window_ex(parent_hwnd, class_name_ptr, title_ptr, 1 if b_type else 0)
    
    def find_top_window(self, class_name=None, title=None, b_type=False):
        """
        查找顶层窗口句柄（父窗口句柄为NULL）
        
        Args:
            class_name: 窗口类名（不指定为None/0/""）
            title: 窗口标题（不指定为None/0/""）
            b_type: 1（模糊匹配）、0（完全匹配）
            
        Returns:
            int: 操作结果，参考HD返回值表
        """
        if not self._find_top_window:
            raise NotImplementedError("HCWIN_FindTopWindow 函数未实现")
            
        class_name_ptr = c_char_p(class_name.encode('utf-8')) if class_name else None
        title_ptr = c_char_p(title.encode('utf-8')) if title else None
        
        return self._find_top_window(class_name_ptr, title_ptr, 1 if b_type else 0)
    
    def enum_window_by_process(self, process_name, class_name=None, title=None, filter_=0, b_type=False):
        """
        根据指定进程及条件枚举符合条件的窗口
        
        Args:
            process_name: 进程名（完全匹配加.exe，模糊匹配自行判断）
            class_name: 窗口类名（不指定为None/0）
            title: 窗口标题（不指定为None/0）
            filter_: 筛选标识（1标题、2类名、4第一个PID、8无父窗口、16窗口显示、32检索多PID，可累加）
            b_type: 1（模糊匹配）、0（完全匹配）
            
        Returns:
            int: 操作结果，参考HD返回值表（0表示未找到；单PID返回hwnd字符串；多PID返回`hwnd1|hwnd2|...`）
        """
        if not self._enum_window_by_process:
            raise NotImplementedError("HCWIN_EnumWindowByProcess 函数未实现")
            
        process_name_ptr = c_char_p(process_name.encode('utf-8')) if process_name else None
        class_name_ptr = c_char_p(class_name.encode('utf-8')) if class_name else None
        title_ptr = c_char_p(title.encode('utf-8')) if title else None
        
        return self._enum_window_by_process(process_name_ptr, class_name_ptr, title_ptr, filter_, 1 if b_type else 0)
    
    def enum_window_by_process_id(self, pid, class_name=None, title=None, filter_=0, b_type=False):
        """
        根据指定进程PID及条件枚举符合条件的窗口（可枚举按键插件无法枚举的窗口）
        
        Args:
            pid: 进程PID
            class_name: 窗口类名（不指定为None/0）
            title: 窗口标题（不指定为None/0）
            filter_: 筛选标识（1标题、2类名、8无父窗口、16窗口显示，可累加）
            b_type: 1（模糊匹配）、0（完全匹配）
            
        Returns:
            int: 操作结果，参考HD返回值表（0表示未找到；1表示找到，返回json字符串）
        """
        if not self._enum_window_by_process_id:
            raise NotImplementedError("HCWIN_EnumWindowByProcessId 函数未实现")
            
        class_name_ptr = c_char_p(class_name.encode('utf-8')) if class_name else None
        title_ptr = c_char_p(title.encode('utf-8')) if title else None
        
        return self._enum_window_by_process_id(pid, class_name_ptr, title_ptr, filter_, 1 if b_type else 0)
    
    def enum_process(self, process_name, b_type=False):
        """
        根据指定进程名枚举符合条件的进程PID
        
        Args:
            process_name: 进程名（完全匹配加.exe，模糊匹配自行判断）
            b_type: 1（模糊匹配）、0（完全匹配）
            
        Returns:
            int: 操作结果，参考HD返回值表（0表示未找到；返回字符串格式：`pid1|pid2|...`）
        """
        if not self._enum_process:
            raise NotImplementedError("HCWIN_EnumProcess 函数未实现")
            
        process_name_ptr = c_char_p(process_name.encode('utf-8')) if process_name else None
        
        return self._enum_process(process_name_ptr, 1 if b_type else 0)
    
    def enum_window(self, parent_hwnd=0, class_name=None, title=None, filter_=0, b_type=False, b_child=False):
        """
        根据指定条件枚举符合条件的窗口（可枚举按键插件无法枚举的窗口）
        
        Args:
            parent_hwnd: 父窗口句柄（可不指定为NULL）
            class_name: 窗口类名（不指定为None/0）
            title: 窗口标题（不指定为None/0）
            filter_: 筛选标识（1标题、2类名、4父窗口是否指定、8无父窗口、16窗口显示，可累加）
            b_type: 1（模糊匹配）、0（完全匹配）
            b_child: 是否枚举指定父句柄的子窗口
            
        Returns:
            int: 操作结果，参考HD返回值表（0表示未找到；多句柄返回`hwnd1|hwnd2|...`）
        """
        if not self._enum_window:
            raise NotImplementedError("HCWIN_EnumWindow 函数未实现")
            
        class_name_ptr = c_char_p(class_name.encode('utf-8')) if class_name else None
        title_ptr = c_char_p(title.encode('utf-8')) if title else None
        
        return self._enum_window(parent_hwnd, class_name_ptr, title_ptr, filter_, 1 if b_type else 0, 1 if b_child else 0)


def create_win(dll_path=None, is_debug=None):
    """
    创建WIN模块实例的工厂函数
    
    Args:
        dll_path: DLL文件所在路径
        is_debug: 是否使用调试版本的DLL
        
    Returns:
        HDWIN: WIN模块实例
    """
    from .base_module import HDModuleFactory
    return HDModuleFactory.create_instance(HDWIN, dll_path, is_debug)