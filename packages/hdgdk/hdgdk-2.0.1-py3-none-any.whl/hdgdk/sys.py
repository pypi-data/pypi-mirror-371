#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 系统模块(SYS)
提供系统环境配置、硬件信息获取、进程管理、时间控制等基础系统功能
"""

from .base_module import HDModuleBase, HDModuleFactory
import ctypes
from typing import Optional, Tuple, Union


class HDSYS(HDModuleBase):
    """
    HD GDK 系统模块(SYS)封装类
    提供系统环境配置、硬件信息获取、进程管理、时间控制等功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化系统模块
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
    
    def _initialize_functions(self):
        """
        初始化DLL中的系统模块函数
        """
        # 系统配置与控制函数
        self.dll.HCSYS_CheckFontSmooth = self.dll.HCSYS_CheckFontSmooth
        self.dll.HCSYS_CheckFontSmooth.restype = ctypes.c_int64
        
        self.dll.HCSYS_OpenFontSmooth = self.dll.HCSYS_OpenFontSmooth
        self.dll.HCSYS_OpenFontSmooth.restype = ctypes.c_int64
        
        self.dll.HCSYS_CloseFontSmooth = self.dll.HCSYS_CloseFontSmooth
        self.dll.HCSYS_CloseFontSmooth.restype = ctypes.c_int64
        
        self.dll.HCSYS_CheckUAC = self.dll.HCSYS_CheckUAC
        self.dll.HCSYS_CheckUAC.restype = ctypes.c_int64
        
        self.dll.HCSYS_SetUAC = self.dll.HCSYS_SetUAC
        self.dll.HCSYS_SetUAC.argtypes = [ctypes.c_int32]
        self.dll.HCSYS_SetUAC.restype = ctypes.c_int64
        
        self.dll.HCSYS_CloseScreenProtect = self.dll.HCSYS_CloseScreenProtect
        self.dll.HCSYS_CloseScreenProtect.restype = ctypes.c_int64
        
        self.dll.HCSYS_ClosePowerManager = self.dll.HCSYS_ClosePowerManager
        self.dll.HCSYS_ClosePowerManager.restype = ctypes.c_int64
        
        self.dll.HCSYS_DisableCloseDisplayAndSleep = self.dll.HCSYS_DisableCloseDisplayAndSleep
        self.dll.HCSYS_DisableCloseDisplayAndSleep.restype = ctypes.c_int64
        
        self.dll.HCSYS_ResumeSystemModify = self.dll.HCSYS_ResumeSystemModify
        self.dll.HCSYS_ResumeSystemModify.restype = ctypes.c_int64
        
        self.dll.HCSYS_ExitSys = self.dll.HCSYS_ExitSys
        self.dll.HCSYS_ExitSys.argtypes = [ctypes.c_int32]
        self.dll.HCSYS_ExitSys.restype = ctypes.c_int64
        
        # 延迟与时间控制函数
        self.dll.HCSYS_Delay = self.dll.HCSYS_Delay
        self.dll.HCSYS_Delay.argtypes = [ctypes.c_int32]
        self.dll.HCSYS_Delay.restype = ctypes.c_int64
        
        self.dll.HCSYS_DelayEx = self.dll.HCSYS_DelayEx
        self.dll.HCSYS_DelayEx.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCSYS_DelayEx.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetNetTime = self.dll.HCSYS_GetNetTime
        self.dll.HCSYS_GetNetTime.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetNetTimeByIp = self.dll.HCSYS_GetNetTimeByIp
        self.dll.HCSYS_GetNetTimeByIp.argtypes = [ctypes.c_char_p]
        self.dll.HCSYS_GetNetTimeByIp.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetTime = self.dll.HCSYS_GetTime
        self.dll.HCSYS_GetTime.restype = ctypes.c_int64
        
        # 硬件与系统信息函数
        self.dll.HCSYS_GetCpuType = self.dll.HCSYS_GetCpuType
        self.dll.HCSYS_GetCpuType.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetCpuUsage = self.dll.HCSYS_GetCpuUsage
        self.dll.HCSYS_GetCpuUsage.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetCpuUsageByPid = self.dll.HCSYS_GetCpuUsageByPid
        self.dll.HCSYS_GetCpuUsageByPid.argtypes = [ctypes.c_int32]
        self.dll.HCSYS_GetCpuUsageByPid.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetMemoryUsageByPid = self.dll.HCSYS_GetMemoryUsageByPid
        self.dll.HCSYS_GetMemoryUsageByPid.argtypes = [ctypes.c_int32]
        self.dll.HCSYS_GetMemoryUsageByPid.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetDiskSerial = self.dll.HCSYS_GetDiskSerial
        self.dll.HCSYS_GetDiskSerial.argtypes = [ctypes.c_int32]
        self.dll.HCSYS_GetDiskSerial.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetDisplayInfo = self.dll.HCSYS_GetDisplayInfo
        self.dll.HCSYS_GetDisplayInfo.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetSystemType = self.dll.HCSYS_GetSystemType
        self.dll.HCSYS_GetSystemType.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetSystemBuildNumber = self.dll.HCSYS_GetSystemBuildNumber
        self.dll.HCSYS_GetSystemBuildNumber.restype = ctypes.c_int64
        
        self.dll.HCSYS_Is64Bit = self.dll.HCSYS_Is64Bit
        self.dll.HCSYS_Is64Bit.restype = ctypes.c_int64
        
        self.dll.HCSYS_IsSurrpotVt = self.dll.HCSYS_IsSurrpotVt
        self.dll.HCSYS_IsSurrpotVt.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetScreenWidth = self.dll.HCSYS_GetScreenWidth
        self.dll.HCSYS_GetScreenWidth.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetScreenHeight = self.dll.HCSYS_GetScreenHeight
        self.dll.HCSYS_GetScreenHeight.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetScreenPixelDepth = self.dll.HCSYS_GetScreenPixelDepth
        self.dll.HCSYS_GetScreenPixelDepth.restype = ctypes.c_int64
        
        self.dll.HCSYS_SetScreenPixelDepth = self.dll.HCSYS_SetScreenPixelDepth
        self.dll.HCSYS_SetScreenPixelDepth.argtypes = [ctypes.c_int32]
        self.dll.HCSYS_SetScreenPixelDepth.restype = ctypes.c_int64
        
        self.dll.HCSYS_SetScreen = self.dll.HCSYS_SetScreen
        self.dll.HCSYS_SetScreen.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.dll.HCSYS_SetScreen.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetDPI = self.dll.HCSYS_GetDPI
        self.dll.HCSYS_GetDPI.restype = ctypes.c_int64
        
        # 路径与进程管理函数
        self.dll.HCSYS_GetDir = self.dll.HCSYS_GetDir
        self.dll.HCSYS_GetDir.argtypes = [ctypes.c_int32]
        self.dll.HCSYS_GetDir.restype = ctypes.c_int64
        
        self.dll.HCSYS_RunApp = self.dll.HCSYS_RunApp
        self.dll.HCSYS_RunApp.argtypes = [ctypes.c_char_p, ctypes.c_long]
        self.dll.HCSYS_RunApp.restype = ctypes.c_int64
        
        self.dll.HCSYS_RunAppEx = self.dll.HCSYS_RunAppEx
        self.dll.HCSYS_RunAppEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_long]
        self.dll.HCSYS_RunAppEx.restype = ctypes.c_int64
        
        self.dll.HCSYS_RunAppGetRet = self.dll.HCSYS_RunAppGetRet
        self.dll.HCSYS_RunAppGetRet.argtypes = [ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool]
        self.dll.HCSYS_RunAppGetRet.restype = ctypes.c_int64
        
        self.dll.HCSYS_RunAppGetRetEx = self.dll.HCSYS_RunAppGetRetEx
        self.dll.HCSYS_RunAppGetRetEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCSYS_RunAppGetRetEx.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetCmdRet = self.dll.HCSYS_GetCmdRet
        self.dll.HCSYS_GetCmdRet.argtypes = [ctypes.c_char_p]
        self.dll.HCSYS_GetCmdRet.restype = ctypes.c_int64
        
        # 机器码与特征信息函数
        self.dll.HCSYS_GetHDiskCode = self.dll.HCSYS_GetHDiskCode
        self.dll.HCSYS_GetHDiskCode.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetCpuCode = self.dll.HCSYS_GetCpuCode
        self.dll.HCSYS_GetCpuCode.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetBIOSInfo = self.dll.HCSYS_GetBIOSInfo
        self.dll.HCSYS_GetBIOSInfo.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetMachineCode = self.dll.HCSYS_GetMachineCode
        self.dll.HCSYS_GetMachineCode.restype = ctypes.c_int64
        
        self.dll.HCSYS_GetMachineCodeNoMac = self.dll.HCSYS_GetMachineCodeNoMac
        self.dll.HCSYS_GetMachineCodeNoMac.restype = ctypes.c_int64
        
    # 系统配置与控制方法
    def check_font_smooth(self) -> int:
        """检查系统是否开启字体平滑"""
        return self.dll.HCSYS_CheckFontSmooth()
        
    def open_font_smooth(self) -> int:
        """开启字体平滑"""
        return self.dll.HCSYS_OpenFontSmooth()
        
    def close_font_smooth(self) -> int:
        """关闭字体平滑"""
        return self.dll.HCSYS_CloseFontSmooth()
        
    def check_uac(self) -> int:
        """检查系统是否开启UAC"""
        return self.dll.HCSYS_CheckUAC()
        
    def set_uac(self, enable: int) -> int:
        """设置UAC开关（enable=1开启，0关闭）"""
        return self.dll.HCSYS_SetUAC(enable)
        
    def close_screen_protect(self) -> int:
        """关闭屏保"""
        return self.dll.HCSYS_CloseScreenProtect()
        
    def close_power_manager(self) -> int:
        """关闭电源管理（禁止睡眠）"""
        return self.dll.HCSYS_ClosePowerManager()
        
    def disable_close_display_and_sleep(self) -> int:
        """禁止关闭显示器、硬盘及睡眠"""
        return self.dll.HCSYS_DisableCloseDisplayAndSleep()
        
    def resume_system_modify(self) -> int:
        """恢复系统上次修改（建议程序退出时调用）"""
        return self.dll.HCSYS_ResumeSystemModify()
        
    def exit_system(self, exit_type: int) -> int:
        """关闭/重启系统或注销用户（type=0注销、1关机、2重启）"""
        return self.dll.HCSYS_ExitSys(exit_type)
        
    # 延迟与时间控制方法
    def delay(self, milliseconds: int) -> int:
        """固定延迟（不阻塞主线程）"""
        return self.dll.HCSYS_Delay(milliseconds)
        
    def delay_ex(self, min_milliseconds: int, max_milliseconds: int) -> int:
        """随机范围延迟（不阻塞主线程）"""
        return self.dll.HCSYS_DelayEx(min_milliseconds, max_milliseconds)
        
    def get_net_time(self) -> int:
        """获取网络时间（北京时间，内置服务器）"""
        return self.dll.HCSYS_GetNetTime()
        
    def get_net_time_by_ip(self, ip: str) -> int:
        """获取网络时间（指定服务器IP）"""
        return self.dll.HCSYS_GetNetTimeByIp(ip.encode('utf-8'))
        
    def get_time(self) -> int:
        """获取开机至当前的毫秒数"""
        return self.dll.HCSYS_GetTime()
        
    # 硬件与系统信息方法
    def get_cpu_type(self) -> int:
        """获取CPU类型（1=Intel，2=AMD）"""
        return self.dll.HCSYS_GetCpuType()
        
    def get_cpu_usage(self) -> int:
        """获取整体CPU使用率"""
        return self.dll.HCSYS_GetCpuUsage()
        
    def get_cpu_usage_by_pid(self, pid: int) -> int:
        """获取指定进程的CPU使用率"""
        return self.dll.HCSYS_GetCpuUsageByPid(pid)
        
    def get_memory_usage_by_pid(self, pid: int) -> int:
        """获取指定进程的内存使用率"""
        return self.dll.HCSYS_GetMemoryUsageByPid(pid)
        
    def get_disk_serial(self, index: int) -> int:
        """获取磁盘序列号（需管理员权限）"""
        return self.dll.HCSYS_GetDiskSerial(index)
        
    def get_display_info(self) -> int:
        """获取显卡信息"""
        return self.dll.HCSYS_GetDisplayInfo()
        
    def get_system_type(self) -> int:
        """获取操作系统类型（1=win95/98等，2=xp/2000，3=2003/xp-64，4=win7/2008 R2，5=vista/2008，6=win8/2012，7=win8.1/2012 R2，8=win10/2016/11，9=win11）"""
        return self.dll.HCSYS_GetSystemType()
        
    def get_system_build_number(self) -> int:
        """获取系统版本号"""
        return self.dll.HCSYS_GetSystemBuildNumber()
        
    def is_64_bit(self) -> int:
        """判断当前进程是否为64位"""
        return self.dll.HCSYS_Is64Bit()
        
    def is_support_vt(self) -> int:
        """检查系统是否支持VT（虚拟化技术）"""
        return self.dll.HCSYS_IsSurrpotVt()
        
    def get_screen_width(self) -> int:
        """获取屏幕宽度"""
        return self.dll.HCSYS_GetScreenWidth()
        
    def get_screen_height(self) -> int:
        """获取屏幕高度"""
        return self.dll.HCSYS_GetScreenHeight()
        
    def get_screen_pixel_depth(self) -> int:
        """获取屏幕色深"""
        return self.dll.HCSYS_GetScreenPixelDepth()
        
    def set_screen_pixel_depth(self, bits_per_pel: int) -> int:
        """设置屏幕色深"""
        return self.dll.HCSYS_SetScreenPixelDepth(bits_per_pel)
        
    def set_screen(self, width: int, height: int) -> int:
        """设置屏幕分辨率"""
        return self.dll.HCSYS_SetScreen(width, height)
        
    def get_dpi(self) -> int:
        """获取屏幕DPI"""
        return self.dll.HCSYS_GetDPI()
        
    # 路径与进程管理方法
    def get_dir(self, dir_type: int) -> int:
        """获取系统路径（type=0当前路径、1system32路径、2windows路径、3临时目录、4当前进程路径）"""
        return self.dll.HCSYS_GetDir(dir_type)
        
    def run_app(self, path: str, result_type: int) -> int:
        """运行指定EXE（不支持启动参数），result_type=0返回进程ID、1线程ID、2进程句柄、3线程句柄"""
        return self.dll.HCSYS_RunApp(path.encode('utf-8'), result_type)
        
    def run_app_ex(self, path: str, app_name: str, lparam: str, flag: int, result_type: int) -> int:
        """运行指定EXE（支持启动参数），flag=0直接运行、4挂起状态打开"""
        return self.dll.HCSYS_RunAppEx(
            path.encode('utf-8'),
            app_name.encode('utf-8') if app_name else None,
            lparam.encode('utf-8') if lparam else None,
            flag,
            result_type
        )
        
    def run_app_get_ret(self, cmd_app: str, show_console: bool = False, wait: bool = False) -> int:
        """运行进程并获取输出（支持CMD命令形式），wait=True阻塞至进程结束"""
        return self.dll.HCSYS_RunAppGetRet(cmd_app.encode('utf-8'), show_console, wait)
        
    def run_app_get_ret_ex(self, cmd_app: str, lparam: str, as_admin: bool = False) -> int:
        """运行进程并获取输出（支持CMD命令形式），as_admin=True以管理员权限运行"""
        return self.dll.HCSYS_RunAppGetRetEx(
            cmd_app.encode('utf-8'),
            lparam.encode('utf-8') if lparam else None,
            as_admin
        )
        
    def get_cmd_ret(self, cmd: str) -> int:
        """获取CMD命令的返回结果"""
        return self.dll.HCSYS_GetCmdRet(cmd.encode('utf-8'))
        
    # 机器码与特征信息方法
    def get_hdisk_code(self) -> int:
        """获取磁盘特征码"""
        return self.dll.HCSYS_GetHDiskCode()
        
    def get_cpu_code(self) -> int:
        """获取CPU特征码"""
        return self.dll.HCSYS_GetCpuCode()
        
    def get_bios_info(self) -> int:
        """获取BIOS制造日期"""
        return self.dll.HCSYS_GetBIOSInfo()
        
    def get_machine_code(self) -> int:
        """获取机器码（包含网卡信息）"""
        return self.dll.HCSYS_GetMachineCode()
        
    def get_machine_code_no_mac(self) -> int:
        """获取机器码（不包含网卡信息）"""
        return self.dll.HCSYS_GetMachineCodeNoMac()


# 工厂函数
def create_hd_sys(dll_path=None, is_debug=None) -> HDSYS:
    """
    创建系统模块实例
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
        
    Returns:
        HDSYS: 系统模块实例
    """
    return HDModuleFactory.create_instance(HDSYS, dll_path, is_debug)


# 模块常量定义
# 系统类型常量
sys_type = {
    1: "Windows 95/98",
    2: "Windows XP/2000",
    3: "Windows 2003/XP-64",
    4: "Windows 7/2008 R2",
    5: "Windows Vista/2008",
    6: "Windows 8/2012",
    7: "Windows 8.1/2012 R2",
    8: "Windows 10/2016/11",
    9: "Windows 11"
}

# 退出系统类型常量
exit_type = {
    0: "注销用户",
    1: "关闭系统",
    2: "重启系统"
}

# 路径类型常量
dir_type = {
    0: "当前路径",
    1: "System32路径",
    2: "Windows路径",
    3: "临时目录",
    4: "当前进程路径"
}

# 运行应用程序返回类型常量
run_app_result_type = {
    0: "进程ID",
    1: "线程ID",
    2: "进程句柄",
    3: "线程句柄"
}

# 运行应用程序标志常量
run_app_flag = {
    0: "直接运行",
    4: "挂起状态打开"
}