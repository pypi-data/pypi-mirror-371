# HD RPG引擎框架(GDK)驱动模块(HD)的Python封装
# 本模块用于学习交流完全合规

import ctypes
from .base_module import HDModuleBase, HDModuleFactory

class HD(HDModuleBase):
    def __init__(self, dll_path=None, is_debug=False):
        super().__init__(dll_path, is_debug)
        # 存储回调函数引用，防止被Python垃圾回收器回收
        self._callbacks = {}

    def _initialize_functions(self):
        """初始化DLL中的函数"""
        # 驱动加载与初始化
        self.HCHD_LoadDrv = self.dll.HCHD_LoadDrv
        self.HCHD_LoadDrv.argtypes = []
        self.HCHD_LoadDrv.restype = ctypes.c_int64
        
        self.HCHD_LoadDrv2 = self.dll.HCHD_LoadDrv2
        self.HCHD_LoadDrv2.argtypes = [ctypes.c_int32]
        self.HCHD_LoadDrv2.restype = ctypes.c_int64
        
        self.HCHD_InitFastRW = self.dll.HCHD_InitFastRW
        self.HCHD_InitFastRW.argtypes = []
        self.HCHD_InitFastRW.restype = ctypes.c_int64
        
    def _call_function(self, func_name, *args):
        """
        调用DLL中的函数
        
        Args:
            func_name (str): 要调用的函数名
            *args: 传递给函数的参数
            
        Returns:
            函数的返回值
        """
        try:
            func = getattr(self.dll, func_name)
            return func(*args)
        except AttributeError:
            raise AttributeError(f"DLL中未找到函数: {func_name}")
        except Exception as e:
            raise Exception(f"调用函数 {func_name} 失败: {str(e)}")
        
        # DLL注入与插件管理
        self.HCHD_InjectX86X64 = self.dll.HCHD_InjectX86X64
        self.HCHD_InjectX86X64.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32,
                                          ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
        self.HCHD_InjectX86X64.restype = ctypes.c_int64
        
        self.HCHD_InjectX86X64ByFile = self.dll.HCHD_InjectX86X64ByFile
        self.HCHD_InjectX86X64ByFile.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32,
                                               ctypes.c_int32, ctypes.c_char_p]
        self.HCHD_InjectX86X64ByFile.restype = ctypes.c_int64
        
        self.HCHD_InstallPlugX86 = self.dll.HCHD_InstallPlugX86
        self.HCHD_InstallPlugX86.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
        self.HCHD_InstallPlugX86.restype = ctypes.c_int64
        
        self.HCHD_InstallPlugX64 = self.dll.HCHD_InstallPlugX64
        self.HCHD_InstallPlugX64.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
        self.HCHD_InstallPlugX64.restype = ctypes.c_int64
        
        self.HCHD_UnInstallPlug = self.dll.HCHD_UnInstallPlug
        self.HCHD_UnInstallPlug.argtypes = []
        self.HCHD_UnInstallPlug.restype = ctypes.c_int64
        
        # 输入模拟（鼠标/键盘）
        self.HCHD_SetMMTrackType = self.dll.HCHD_SetMMTrackType
        self.HCHD_SetMMTrackType.argtypes = [ctypes.c_int32]
        self.HCHD_SetMMTrackType.restype = ctypes.c_int64
        
        self.HCHD_MousePress = self.dll.HCHD_MousePress
        self.HCHD_MousePress.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                                        ctypes.c_int32]
        self.HCHD_MousePress.restype = ctypes.c_int64
        
        self.HCHD_MousePressEx = self.dll.HCHD_MousePressEx
        self.HCHD_MousePressEx.argtypes = [ctypes.c_int64, ctypes.c_int32, ctypes.c_int32,
                                          ctypes.c_int32, ctypes.c_int32]
        self.HCHD_MousePressEx.restype = ctypes.c_int64
        
        self.HCHD_MouseDown = self.dll.HCHD_MouseDown
        self.HCHD_MouseDown.argtypes = [ctypes.c_int64, ctypes.c_int32, ctypes.c_int32,
                                       ctypes.c_int32]
        self.HCHD_MouseDown.restype = ctypes.c_int64
        
        self.HCHD_MouseUp = self.dll.HCHD_MouseUp
        self.HCHD_MouseUp.argtypes = [ctypes.c_int64, ctypes.c_int32, ctypes.c_int32,
                                     ctypes.c_int32]
        self.HCHD_MouseUp.restype = ctypes.c_int64
        
        self.HCHD_KbPress = self.dll.HCHD_KbPress
        self.HCHD_KbPress.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.HCHD_KbPress.restype = ctypes.c_int64
        
        self.HCHD_KbDown = self.dll.HCHD_KbDown
        self.HCHD_KbDown.argtypes = [ctypes.c_int32]
        self.HCHD_KbDown.restype = ctypes.c_int64
        
        self.HCHD_KbUp = self.dll.HCHD_KbUp
        self.HCHD_KbUp.argtypes = [ctypes.c_int32]
        self.HCHD_KbUp.restype = ctypes.c_int64
        
        # 内存操作
        self.HCHD_RW = self.dll.HCHD_RW
        self.HCHD_RW.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p,
                                ctypes.c_int32, ctypes.c_int32]
        self.HCHD_RW.restype = ctypes.c_int64
        
        self.HCHD_RWExx = self.dll.HCHD_RWExx
        self.HCHD_RWExx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p,
                                   ctypes.c_int32, ctypes.c_int32]
        self.HCHD_RWExx.restype = ctypes.c_int64
        
        self.HCHD_BeginRWEx = self.dll.HCHD_BeginRWEx
        self.HCHD_BeginRWEx.argtypes = [ctypes.c_int32]
        self.HCHD_BeginRWEx.restype = ctypes.c_int64
        
        self.HCHD_RWEx = self.dll.HCHD_RWEx
        self.HCHD_RWEx.argtypes = [ctypes.c_int64, ctypes.c_void_p, ctypes.c_int32,
                                  ctypes.c_int32]
        self.HCHD_RWEx.restype = ctypes.c_int64
        
        self.HCHD_EndRWEx = self.dll.HCHD_EndRWEx
        self.HCHD_EndRWEx.argtypes = []
        self.HCHD_EndRWEx.restype = ctypes.c_int64
        
        self.HCHD_AddrIsRead = self.dll.HCHD_AddrIsRead
        self.HCHD_AddrIsRead.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
        self.HCHD_AddrIsRead.restype = ctypes.c_int64
        
        # 进程管理（保护/隐藏/杀死等）
        self.HCHD_PP = self.dll.HCHD_PP
        self.HCHD_PP.argtypes = [ctypes.c_int32, ctypes.c_bool]
        self.HCHD_PP.restype = ctypes.c_int64
        
        self.HCHD_PHide = self.dll.HCHD_PHide
        self.HCHD_PHide.argtypes = [ctypes.c_int32]
        self.HCHD_PHide.restype = ctypes.c_int64
        
        self.HCHD_PHideEx = self.dll.HCHD_PHideEx
        self.HCHD_PHideEx.argtypes = [ctypes.c_int32]
        self.HCHD_PHideEx.restype = ctypes.c_int64
        
        self.HCHD_PShow = self.dll.HCHD_PShow
        self.HCHD_PShow.argtypes = [ctypes.c_int32]
        self.HCHD_PShow.restype = ctypes.c_int64
        
        self.HCHD_PPKill = self.dll.HCHD_PPKill
        self.HCHD_PPKill.argtypes = [ctypes.c_char_p, ctypes.c_int32]
        self.HCHD_PPKill.restype = ctypes.c_int64
        
        # 内存管理（申请/释放/保护等）
        self.HCHD_MemoryAllocate = self.dll.HCHD_MemoryAllocate
        self.HCHD_MemoryAllocate.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32,
                                           ctypes.c_bool, ctypes.c_void_p]
        self.HCHD_MemoryAllocate.restype = ctypes.c_int64
        
        self.HCHD_MemoryAllocateEx = self.dll.HCHD_MemoryAllocateEx
        self.HCHD_MemoryAllocateEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64,
                                             ctypes.c_int32, ctypes.c_bool, ctypes.c_void_p]
        self.HCHD_MemoryAllocateEx.restype = ctypes.c_int64
        
        self.HCHD_MemoryFree = self.dll.HCHD_MemoryFree
        self.HCHD_MemoryFree.argtypes = [ctypes.c_int32, ctypes.c_int64]
        self.HCHD_MemoryFree.restype = ctypes.c_int64
        
        self.HCHD_MemoryProtect = self.dll.HCHD_MemoryProtect
        self.HCHD_MemoryProtect.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64,
                                          ctypes.c_int32]
        self.HCHD_MemoryProtect.restype = ctypes.c_int64
        
        self.HCHD_MemoryHide = self.dll.HCHD_MemoryHide
        self.HCHD_MemoryHide.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64]
        self.HCHD_MemoryHide.restype = ctypes.c_int64
        
        self.HCHD_MemoryQuery = self.dll.HCHD_MemoryQuery
        self.HCHD_MemoryQuery.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p]
        self.HCHD_MemoryQuery.restype = ctypes.c_int64
        
        # 模块与地址查询
        self.HCHD_MemoryFindCode = self.dll.HCHD_MemoryFindCode
        self.HCHD_MemoryFindCode.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p,
                                           ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p]
        self.HCHD_MemoryFindCode.restype = ctypes.c_int64
        
        self.HCHD_GetMainModuleBase = self.dll.HCHD_GetMainModuleBase
        self.HCHD_GetMainModuleBase.argtypes = [ctypes.c_int32, ctypes.c_void_p]
        self.HCHD_GetMainModuleBase.restype = ctypes.c_int64
        
        self.HCHD_GetModuleBase = self.dll.HCHD_GetModuleBase
        self.HCHD_GetModuleBase.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_void_p]
        self.HCHD_GetModuleBase.restype = ctypes.c_int64
        
        self.HCHD_GetModuleCallAddr = self.dll.HCHD_GetModuleCallAddr
        self.HCHD_GetModuleCallAddr.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p,
                                              ctypes.c_void_p]
        self.HCHD_GetModuleCallAddr.restype = ctypes.c_int64
        
        # 其他功能
        self.HCHD_ChangeMachineKey = self.dll.HCHD_ChangeMachineKey
        self.HCHD_ChangeMachineKey.argtypes = [ctypes.c_int32]
        self.HCHD_ChangeMachineKey.restype = ctypes.c_int64
        
        self.HCHD_NTNCaptureScreen = self.dll.HCHD_NTNCaptureScreen
        self.HCHD_NTNCaptureScreen.argtypes = [ctypes.c_int64, ctypes.c_bool]
        self.HCHD_NTNCaptureScreen.restype = ctypes.c_int64
        
        self.HCHD_NTThreadRunCall = self.dll.HCHD_NTThreadRunCall
        self.HCHD_NTThreadRunCall.argtypes = [ctypes.c_int32, ctypes.c_int64]
        self.HCHD_NTThreadRunCall.restype = ctypes.c_int64
        
        self.HCHD_ClearInject = self.dll.HCHD_ClearInject
        self.HCHD_ClearInject.argtypes = []
        self.HCHD_ClearInject.restype = ctypes.c_int64
        
        self.HCHD_PcrocessRoot = self.dll.HCHD_PcrocessRoot
        self.HCHD_PcrocessRoot.argtypes = [ctypes.c_int32]
        self.HCHD_PcrocessRoot.restype = ctypes.c_int64
        
        self.HCHD_HandleRoot = self.dll.HCHD_HandleRoot
        self.HCHD_HandleRoot.argtypes = [ctypes.c_int64]
        self.HCHD_HandleRoot.restype = ctypes.c_int64
    
    # 驱动加载与初始化相关方法
    def load_drv(self):
        """加载HD驱动（正式版本）"""
        return self._call_function("HCHD_LoadDrv")
    
    def load_drv2(self, type=0):
        """云下发加载不同版本驱动或组件"""
        return self._call_function("HCHD_LoadDrv2", type)
    
    def init_fast_rw(self):
        """初始化HD驱动快速读写"""
        return self._call_function("HCHD_InitFastRW")
    
    # DLL注入与插件管理相关方法
    def inject_x86_x64(self, inject_exe_name, dll_bits, inject_mode, memory_hide, inject_data, inject_size):
        """将DLL注入到指定进程（通过二进制数据）"""
        return self._call_function("HCHD_InjectX86X64", 
                                 inject_exe_name.encode('utf-8'), 
                                 dll_bits, 
                                 inject_mode, 
                                 memory_hide, 
                                 inject_data, 
                                 inject_size)
    
    def inject_x86_x64_by_file(self, inject_exe_name, dll_bits, inject_mode, memory_hide, dll_path):
        """将DLL注入到指定进程（通过文件路径）"""
        return self._call_function("HCHD_InjectX86X64ByFile", 
                                 inject_exe_name.encode('utf-8'), 
                                 dll_bits, 
                                 inject_mode, 
                                 memory_hide, 
                                 dll_path.encode('utf-8'))
    
    def install_plug_x86(self, inject_exe_name, inject_mode, memory_hide):
        """安装HD插件到指定32位进程"""
        return self._call_function("HCHD_InstallPlugX86", 
                                 inject_exe_name.encode('utf-8'), 
                                 inject_mode, 
                                 memory_hide)
    
    def install_plug_x64(self, inject_exe_name, inject_mode, memory_hide):
        """安装HD插件到指定64位进程"""
        return self._call_function("HCHD_InstallPlugX64", 
                                 inject_exe_name.encode('utf-8'), 
                                 inject_mode, 
                                 memory_hide)
    
    def uninstall_plug(self):
        """卸载插件（清除下次安装缓存）"""
        return self._call_function("HCHD_UnInstallPlug")
    
    # 输入模拟（鼠标/键盘）相关方法
    def set_mm_track_type(self, type):
        """设置鼠标移动轨迹类型"""
        return self._call_function("HCHD_SetMMTrackType", type)
    
    def mouse_press(self, x, y, m_but_code, mis):
        """前台驱动鼠标移动并点击"""
        return self._call_function("HCHD_MousePress", x, y, m_but_code, mis)
    
    def mouse_press_ex(self, hwnd, x, y, m_but_code, mis):
        """前台鼠标移动并点击（指定窗口句柄）"""
        return self._call_function("HCHD_MousePressEx", hwnd, x, y, m_but_code, mis)
    
    def mouse_down(self, hwnd, x, y, m_but_code):
        """鼠标按下（可指定窗口句柄）"""
        return self._call_function("HCHD_MouseDown", hwnd, x, y, m_but_code)
    
    def mouse_up(self, hwnd, x, y, m_but_code):
        """鼠标弹起（可指定窗口句柄）"""
        return self._call_function("HCHD_MouseUp", hwnd, x, y, m_but_code)
    
    def kb_press(self, virtual_key_code, mis):
        """键盘按下并弹起"""
        return self._call_function("HCHD_KbPress", virtual_key_code, mis)
    
    def kb_down(self, virtual_key_code):
        """键盘按下"""
        return self._call_function("HCHD_KbDown", virtual_key_code)
    
    def kb_up(self, virtual_key_code):
        """键盘弹起"""
        return self._call_function("HCHD_KbUp", virtual_key_code)
    
    # 内存操作相关方法
    def rw(self, pid, target_address, buffer_address, buffer_of_bytes, rw_type):
        """驱动读写内存"""
        return self._call_function("HCHD_RW", pid, target_address, buffer_address, buffer_of_bytes, rw_type)
    
    def rw_exx(self, pid, target_address, buffer_address, buffer_of_bytes, rw_type):
        """快速内存读写（单线程百万级别）"""
        return self._call_function("HCHD_RWExx", pid, target_address, buffer_address, buffer_of_bytes, rw_type)
    
    def begin_rw_ex(self, pid):
        """批量内存读写开始"""
        return self._call_function("HCHD_BeginRWEx", pid)
    
    def rw_ex(self, target_address, buffer_address, buffer_of_bytes, rw_type):
        """批量内存读写"""
        return self._call_function("HCHD_RWEx", target_address, buffer_address, buffer_of_bytes, rw_type)
    
    def end_rw_ex(self):
        """批量内存读写结束"""
        return self._call_function("HCHD_EndRWEx")
    
    def addr_is_read(self, pid, addr, size):
        """检查地址是否可读"""
        return self._call_function("HCHD_AddrIsRead", pid, addr, size)
    
    # 进程管理（保护/隐藏/杀死等）相关方法
    def pp(self, pid, b_open):
        """进程保护"""
        return self._call_function("HCHD_PP", pid, b_open)
    
    def p_hide(self, pid):
        """进程隐藏（一次一个，需先显示之前的）"""
        return self._call_function("HCHD_PHide", pid)
    
    def p_hide_ex(self, pid):
        """加强版进程隐藏（无法恢复）"""
        return self._call_function("HCHD_PHideEx", pid)
    
    def p_show(self, pid):
        """显示隐藏的进程"""
        return self._call_function("HCHD_PShow", pid)
    
    def pp_kill(self, process_name, pid):
        """杀死进程"""
        return self._call_function("HCHD_PPKill", process_name.encode('utf-8'), pid)
    
    # 内存管理（申请/释放/保护等）相关方法
    def memory_allocate(self, pid, memory_size, memory_protect, b_high_address, p_out_buffer):
        """驱动申请内存"""
        return self._call_function("HCHD_MemoryAllocate", pid, memory_size, memory_protect, b_high_address, p_out_buffer)
    
    def memory_allocate_ex(self, pid, memory_addr, memory_size, memory_protect, b_high_address, p_out_buffer):
        """驱动申请内存（可指定地址）"""
        return self._call_function("HCHD_MemoryAllocateEx", pid, memory_addr, memory_size, memory_protect, b_high_address, p_out_buffer)
    
    def memory_free(self, pid, memory_address):
        """驱动释放内存"""
        return self._call_function("HCHD_MemoryFree", pid, memory_address)
    
    def memory_protect(self, pid, memory_address, memory_of_bytes, new_protect):
        """修改内存保护属性"""
        return self._call_function("HCHD_MemoryProtect", pid, memory_address, memory_of_bytes, new_protect)
    
    def memory_hide(self, pid, memory_address, memory_of_bytes):
        """驱动内存隐藏"""
        return self._call_function("HCHD_MemoryHide", pid, memory_address, memory_of_bytes)
    
    def memory_query(self, pid, memory_address, p_out_buffer):
        """驱动内存查询"""
        return self._call_function("HCHD_MemoryQuery", pid, memory_address, p_out_buffer)
    
    # 模块与地址查询相关方法
    def memory_find_code(self, pid, address, sigin_code, sigin_code_size, i_protect, out_buffer):
        """通过特征码查找地址"""
        return self._call_function("HCHD_MemoryFindCode", pid, address, sigin_code, sigin_code_size, i_protect, out_buffer)
    
    def get_main_module_base(self, pid, out_buffer):
        """获取主模块（EXE）地址"""
        return self._call_function("HCHD_GetMainModuleBase", pid, out_buffer)
    
    def get_module_base(self, pid, module_name, out_buffer):
        """获取指定模块地址"""
        return self._call_function("HCHD_GetModuleBase", pid, module_name.encode('utf-8'), out_buffer)
    
    def get_module_call_addr(self, pid, module_name, call_name, out_buffer):
        """获取模块中指定函数地址"""
        return self._call_function("HCHD_GetModuleCallAddr", pid, module_name.encode('utf-8'), call_name.encode('utf-8'), out_buffer)
    
    # 其他功能相关方法
    def change_machine_key(self, type):
        """驱动修改机器码"""
        return self._call_function("HCHD_ChangeMachineKey", type)
    
    def nt_n_capture_screen(self, h_wnd, enable):
        """驱动内核反截图"""
        return self._call_function("HCHD_NTNCaptureScreen", h_wnd, enable)
    
    def nt_thread_run_call(self, pid, call_address):
        """驱动内存远线程执行函数"""
        return self._call_function("HCHD_NTThreadRunCall", pid, call_address)
    
    def clear_inject(self):
        """清除注入缓存（全局插件、DLL缓存）"""
        return self._call_function("HCHD_ClearInject")
    
    def process_root(self, pid):
        """进程提权（通过PID）"""
        return self._call_function("HCHD_PcrocessRoot", pid)
    
    def handle_root(self, handle):
        """进程提权（通过句柄）"""
        return self._call_function("HCHD_HandleRoot", handle)

# 工厂函数
def create_hd(dll_path=None, is_debug=None):
    """创建HD实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL（为None时使用DLL管理器的默认设置）
        
    Returns:
        HD: 创建的HD模块实例
    """
    return HDModuleFactory.create_instance(HD, dll_path, is_debug)