"""
HD GDK Python封装模块
提供对HD RPG引擎框架(GDK)的Python调用支持
"""

# 导入DLL管理器（优先导入，确保DLL只加载一次）
from .dll_manager import init_dll_manager, get_dll_manager, get_dll

# 导入各模块的工厂函数和主要类
from .login import create_hd_login, HDLogin
from .ip import create_hd_ip, HDIP
from .ex import create_hd_ex, HDEx, HDExCallback
from .basic import create_hd_basic, HDBasic
from .inject import create_hd_inject, HDInject
from .env import create_hd_env, HDEnv
from .mt import create_hd_mt, HDMT, HDMTCallback
from .hk import create_hd_hk, HDHK, HDHKCallback
from .common import create_hd_common, HDCommon
from .sh import create_hd_shell_code, HDShellCode
from .yolo import create_yolo, HDYOLO
from .vnc import create_vnc, HDVNC
from .win import create_win, HDWIN
from .vt import create_vt, HDVT
from .lua import create_hd_lua, HDLua
from .normal import create_normal, HDNormal
from .pp import create_pp, HDPP
from .target import create_target, HDTARGET
from .nt import create_nt, HDNT
from .hd import create_hd, HD
from .m import create_m, HDM
from .fp import create_fp, HDFP
from .fs import create_fs, HDFS
from .com import create_hd_com, HDCOM
from .cs import create_hd_cs, HCCS
from .fi import create_fi, HCFI
from .sc import create_hd_sc, HDSC
from .bs import create_hd_bs, HDBS
from .mkb import create_hd_mkb, HDMKB
from .rc import create_rc, HCRC
from .vm import create_hd_vm, HDVM
from .vmdma import create_hd_vmdma, HDVMDMA
from .gb import create_hd_gb, HDSC
from .ds import create_hd_ds, HCDS
from .res import create_hd_res, HCRES
from .json_module import create_hd_json, HDJSON
from .dw import create_hd_dw, HDDW
from .sys import create_hd_sys, HDSYS
from .status import create_hd_status, HDStatusModule

# 定义包的公共接口

# 导入新的API管理器
from .api_manager import HDGDKManager, get_hdgdk_manager, HDGDK

# 导入直接API功能 - 使用DLL函数名
from .direct_api import (
    # 初始化函数
    init_hdgdk,
    
    # Login模块DLL函数
    HCHD_Login, HCHD_GetLastLoginFYI, HCHD_GetExpiredTimeStamp, HCHD_GetFYI, HCHD_GetOpenMaxNum,
    
    # IP模块DLL函数
    HCIP_YMSetRootPath, HCIP_YMAddIP, HCIP_YMAddProcess, HCIP_YMOpen, HCIP_YMIsOpen, HCIP_YMClose,
    
    # Basic模块DLL函数
    HD_Basic_GetVersion, HD_Basic_GetBuildDate, HD_Basic_GetPlatformInfo,
    
    # Inject模块DLL函数
    HD_Inject_DLL, HD_Inject_EjectDLL,
    
    # Env模块DLL函数
    HD_Env_GetVar, HD_Env_SetVar,
    
    # MT模块DLL函数
    HD_MT_CreateThread, HD_MT_TerminateThread,
    
    # HK模块DLL函数
    HD_HK_Function, HD_HK_UnhookFunction,
    
    # Common模块DLL函数
    HD_Common_StringToWString, HD_Common_WStringToString,
    
    # ShellCode模块DLL函数
    HD_SH_ExecuteShellCode,
    
    # Yolo模块DLL函数
    HD_YOLO_DetectObjects,
    
    # VNC模块DLL函数
    HD_VNC_CreateSession, HD_VNC_CloseSession,
    
    # Win模块DLL函数
    HD_WIN_GetWindowInfo, HD_WIN_SendMessage,
    
    # VT模块DLL函数
    HD_VT_Query, HD_VT_Protect,
    
    # Lua模块DLL函数
    HD_LUA_ExecuteScript, HD_LUA_CallFunction,
    
    # 其他模块DLL函数
    HD_Normal_Operation,
    HD_PP_ProcessProtection,
    HD_TARGET_GetInfo, HD_TARGET_Set,
    HD_NT_APICall,
    HD_Core_Operation,
    HD_Memory_Operation,
    HD_File_Operation,
    HD_FS_Operation,
    HD_COM_Operation,
    HD_CS_Operation,
    HD_FI_FileInfo,
    HD_SC_SystemCall,
    HD_BS_Operation,
    HD_MKB_Operation,
    HD_RC_Operation,
    HD_VM_Operation,
    HD_VMDMA_Operation,
    HD_GB_Operation,
    HD_DS_Operation,
    HD_RES_Operation,
    HD_JSON_Operation,
    HD_DW_Operation,
    HD_SYS_Operation,
    HD_STATUS_Operation
)

# 导入模块级API功能
from .module_api import (
    # 主要模块实例
    login_module,
    
    # 模块获取函数（推荐使用）
    get_module
)

# 导入全函数导入模块
from . import all_functions

__all__ = [
    # DLL管理器（优先公开，便于用户初始化）
    'init_dll_manager', 'get_dll_manager', 'get_dll',
    # 基础模块
    'create_hd_basic', 'HDBasic',
    # 登录模块
    'create_hd_login', 'HDLogin',
    # IP模块
    'create_hd_ip', 'HDIP',
    # 扩展模块
    'create_hd_ex', 'HDEx', 'HDExCallback',
    # 注入模块
    'create_hd_inject', 'HDInject',
    # 环境模块
    'create_hd_env', 'HDEnv',
    # 多线程模块
    'create_hd_mt', 'HDMT', 'HDMTCallback',
    # Hook模块
    'create_hd_hk', 'HDHK', 'HDHKCallback',
    # 通用模块
    'create_hd_common', 'HDCommon',
    # ShellCode模块
    'create_hd_shell_code', 'HDShellCode',
    # YOLO模块
    'create_yolo', 'HDYOLO',
    # VNC模块
    'create_vnc', 'HDVNC',
    # WIN模块
    'create_win', 'HDWIN',
    # VT模块
    'create_vt', 'HDVT',
    # LUA模块
    'create_hd_lua', 'HDLua',
    # Normal模块
    'create_normal', 'HDNormal',
    # PP模块
    'create_pp', 'HDPP',
    # TARGET模块
    'create_target', 'HDTARGET',
    # NT模块
    'create_nt', 'HDNT',
    # HD模块
    'create_hd', 'HD',
    # M模块
    'create_m', 'HDM',
    # FP模块
    'create_fp', 'HDFP',
    # FS模块
    'create_fs', 'HDFS',
    # COM模块
    'create_hd_com', 'HDCOM',
    # CS模块
    'create_hd_cs', 'HCCS',
    # FI模块
    'create_fi', 'HCFI',
    # SC模块
    'create_hd_sc', 'HDSC',
    # BS模块
    'create_hd_bs', 'HDBS',
    # MKB模块
    'create_hd_mkb', 'HDMKB',
    # RC模块
    'create_rc', 'HCRC',
    # VM模块
    'create_hd_vm', 'HDVM',
    # VMDMA模块
    'create_hd_vmdma', 'HDVMDMA',
    # GB模块
    'create_hd_gb', 'HDSC',
    # DS模块
    'create_hd_ds', 'HCDS',
    # RES模块
    'create_hd_res', 'HCRES',
    # JSON模块
    'create_hd_json', 'HDJSON',
    # DW模块
    'create_hd_dw', 'HDDW',
    # SYS模块
    'create_hd_sys', 'HDSYS',
    # STATUS模块
    'create_hd_status', 'HDStatusModule',
    
    # API管理器相关
    'HDGDKManager', 'get_hdgdk_manager', 'HDGDK',
    
    # 直接API功能 - 使用DLL函数名
    'init_hdgdk',
    # Login模块DLL函数
    'HCHD_Login', 'HCHD_GetLastLoginFYI', 'HCHD_GetExpiredTimeStamp', 'HCHD_GetFYI', 'HCHD_GetOpenMaxNum',
    # IP模块DLL函数
    'HCIP_YMSetRootPath', 'HCIP_YMAddIP', 'HCIP_YMAddProcess', 'HCIP_YMOpen', 'HCIP_YMIsOpen', 'HCIP_YMClose',
    # Basic模块DLL函数
    'HD_Basic_GetVersion', 'HD_Basic_GetBuildDate', 'HD_Basic_GetPlatformInfo',
    # Inject模块DLL函数
    'HD_Inject_DLL', 'HD_Inject_EjectDLL',
    # Env模块DLL函数
    'HD_Env_GetVar', 'HD_Env_SetVar',
    # MT模块DLL函数
    'HD_MT_CreateThread', 'HD_MT_TerminateThread',
    # HK模块DLL函数
    'HD_HK_Function', 'HD_HK_UnhookFunction',
    # Common模块DLL函数
    'HD_Common_StringToWString', 'HD_Common_WStringToString',
    # ShellCode模块DLL函数
    'HD_SH_ExecuteShellCode',
    # Yolo模块DLL函数
    'HD_YOLO_DetectObjects',
    # VNC模块DLL函数
    'HD_VNC_CreateSession', 'HD_VNC_CloseSession',
    # Win模块DLL函数
    'HD_WIN_GetWindowInfo', 'HD_WIN_SendMessage',
    # VT模块DLL函数
    'HD_VT_Query', 'HD_VT_Protect',
    # Lua模块DLL函数
    'HD_LUA_ExecuteScript', 'HD_LUA_CallFunction',
    # 其他模块DLL函数
    'HD_Normal_Operation',
    'HD_PP_ProcessProtection',
    'HD_TARGET_GetInfo', 'HD_TARGET_Set',
    'HD_NT_APICall',
    'HD_Core_Operation',
    'HD_Memory_Operation',
    'HD_File_Operation',
    'HD_FS_Operation',
    'HD_COM_Operation',
    'HD_CS_Operation',
    'HD_FI_FileInfo',
    'HD_SC_SystemCall',
    'HD_BS_Operation',
    'HD_MKB_Operation',
    'HD_RC_Operation',
    'HD_VM_Operation',
    'HD_VMDMA_Operation',
    'HD_GB_Operation',
    'HD_DS_Operation',
    'HD_RES_Operation',
    'HD_JSON_Operation',
    'HD_DW_Operation',
    'HD_SYS_Operation',
    'HD_STATUS_Operation',
    
    # 模块级API功能
    'login_module',
    'get_module',
    
    # 全函数导入模块
    'all_functions'
]