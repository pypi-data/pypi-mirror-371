from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCHDPP_Protect(int pid);
def HD盾_保护(进程PID: int) -> int:
    """
    一键保护进程（隐藏等）
    
    Args:
        进程PID: 需要保护的进程PID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数3来安装保护盾HDPP驱动
    """
    hd = Config.get_hd()
    
    HCHDPP_Protect = hd.HCHDPP_Protect
    HCHDPP_Protect.restype = ctypes.c_int64
    HCHDPP_Protect.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCHDPP_Protect(ctypes.c_int32(进程PID))
    return ret

# INT64 __stdcall HCHDPW_OnProtect(INT64 hwnd);
def HD盾_开启窗口保护(窗口句柄: int) -> int:
    """
    打开窗口保护以及子窗口
    
    Args:
        窗口句柄: 目标窗口句柄，一般为父窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数5来安装保护盾HDPW驱动
        可以多次指定，内部会把指定的保护窗口句柄以及所属子窗口一起保护
    """
    hd = Config.get_hd()
    
    HCHDPW_OnProtect = hd.HCHDPW_OnProtect
    HCHDPW_OnProtect.restype = ctypes.c_int64
    HCHDPW_OnProtect.argtypes = [
        ctypes.c_int64
    ]
    
    ret = HCHDPW_OnProtect(ctypes.c_int64(窗口句柄))
    return ret

# INT64 __stdcall HCHDPW_OffProtect();
def HD盾_关闭窗口保护() -> int:
    """
    取消所有窗口保护（指定保护过的）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数5来安装保护盾HDPW驱动
        可以取消调用过HCHDPW_OnProtect所有保护的窗口句柄
    """
    hd = Config.get_hd()
    
    HCHDPW_OffProtect = hd.HCHDPW_OffProtect
    HCHDPW_OffProtect.restype = ctypes.c_int64
    HCHDPW_OffProtect.argtypes = []
    
    ret = HCHDPW_OffProtect()
    return ret
