#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 全函数导入模块
提供一次性导入所有HD GDK函数的功能
用户可以通过 `from hdgdk.all_functions import *` 导入所有函数
"""

# 从direct_api模块导入所有DLL函数
try:
    from .direct_api import *
except ImportError:
    # 如果direct_api模块不可用，提供一个明确的错误信息
    raise ImportError("无法导入direct_api模块。请确保HD GDK已正确安装。")

# 定义模块的公共接口
__all__ = []

# 构建可导入的函数列表
try:
    import sys
    # 获取direct_api模块对象
    direct_api_module = sys.modules['hdgdk.direct_api']
    
    # 获取direct_api模块的__all__列表
    if hasattr(direct_api_module, '__all__'):
        __all__ = direct_api_module.__all__
    else:
        # 如果__all__不存在，尝试获取所有非私有属性
        __all__ = [name for name in dir(direct_api_module) if not name.startswith('_')]
        
    # 确保init_hdgdk函数被包含在内
    if 'init_hdgdk' not in __all__:
        __all__.append('init_hdgdk')

except Exception as e:
    # 如果自动获取失败，手动定义主要DLL函数列表
    __all__ = [
        # 初始化函数
        'init_hdgdk',
        # Login模块DLL函数
        'HCHD_Login', 'HCHD_GetLastLoginFYI', 'HCHD_GetExpiredTimeStamp', 'HCHD_GetFYI', 'HCHD_GetOpenMaxNum',
        # IP模块DLL函数
        'HCIP_YMSetRootPath', 'HCIP_YMAddIP', 'HCIP_YMAddProcess', 'HCIP_YMOpen', 'HCIP_YMIsOpen', 'HCIP_YMClose',
        # 其他模块DLL函数
        'HD_EX_SetPath', 'HD_EX_GetPath', 'HD_EX_Open', 'HD_EX_Close',
        'HD_Basic_GetVersion', 'HD_Basic_GetBuildDate', 'HD_Basic_GetPlatformInfo',
        'HD_Inject_DLL', 'HD_Inject_EjectDLL',
        'HD_Env_GetVar', 'HD_Env_SetVar',
        'HD_MT_CreateThread', 'HD_MT_TerminateThread',
        'HD_HK_Function', 'HD_HK_UnhookFunction',
        'HD_Common_StringToWString', 'HD_Common_WStringToString',
        'HD_SH_ExecuteShellCode',
        'HD_YOLO_DetectObjects',
        'HD_VNC_CreateSession', 'HD_VNC_CloseSession',
        'HD_WIN_GetWindowInfo', 'HD_WIN_SendMessage',
        'HD_VT_Query', 'HD_VT_Protect',
        'HD_LUA_ExecuteScript', 'HD_LUA_CallFunction'
    ]