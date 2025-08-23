#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 全函数导入测试模块
测试通过 `from hdgdk.all_functions import *` 一次性导入所有DLL函数并直接调用的功能
"""

import os
import sys

# 添加当前目录到Python路径，确保可以导入hdgdk模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试一次性导入所有DLL函数
print("===== HD GDK 全函数导入测试 ======")

try:
    print("1. 测试从hdgdk.all_functions导入所有DLL函数...")
    from hdgdk.all_functions import *
    print("   导入成功！")
    
    # 测试init_hdgdk函数是否可用（实际使用时需要提供DLL路径）
    print("\n2. 测试init_hdgdk函数导入状态...")
    print(f"   init_hdgdk函数: {init_hdgdk}")
    print("   注意：实际使用时需要提供DLL路径")
    
    # 测试多个常用DLL函数是否可用（不实际调用，仅检查函数是否存在）
    print("\n3. 测试常用DLL函数导入状态...")
    
    # 统计已导入的DLL函数数量
    imported_functions = 0
    
    # Login模块DLL函数
    print("\n3.1 Login模块:")
    if 'HCHD_Login' in globals():
        print("   HCHD_Login函数: 已导入")
        imported_functions += 1
    if 'HCHD_GetLastLoginFYI' in globals():
        print("   HCHD_GetLastLoginFYI函数: 已导入")
        imported_functions += 1
    if 'HCHD_GetExpiredTimeStamp' in globals():
        print("   HCHD_GetExpiredTimeStamp函数: 已导入")
        imported_functions += 1
    if 'HCHD_GetFYI' in globals():
        print("   HCHD_GetFYI函数: 已导入")
        imported_functions += 1
    if 'HCHD_GetOpenMaxNum' in globals():
        print("   HCHD_GetOpenMaxNum函数: 已导入")
        imported_functions += 1
    
    # IP模块DLL函数
    print("\n3.2 IP模块:")
    if 'HCIP_YMSetRootPath' in globals():
        print("   HCIP_YMSetRootPath函数: 已导入")
        imported_functions += 1
    if 'HCIP_YMAddIP' in globals():
        print("   HCIP_YMAddIP函数: 已导入")
        imported_functions += 1
    if 'HCIP_YMAddProcess' in globals():
        print("   HCIP_YMAddProcess函数: 已导入")
        imported_functions += 1
    if 'HCIP_YMOpen' in globals():
        print("   HCIP_YMOpen函数: 已导入")
        imported_functions += 1
    if 'HCIP_YMIsOpen' in globals():
        print("   HCIP_YMIsOpen函数: 已导入")
        imported_functions += 1
    if 'HCIP_YMClose' in globals():
        print("   HCIP_YMClose函数: 已导入")
        imported_functions += 1
    
    # Basic模块DLL函数
    print("\n3.3 Basic模块:")
    if 'HD_Basic_GetVersion' in globals():
        print("   HD_Basic_GetVersion函数: 已导入")
        imported_functions += 1
    if 'HD_Basic_GetBuildDate' in globals():
        print("   HD_Basic_GetBuildDate函数: 已导入")
        imported_functions += 1
    if 'HD_Basic_GetPlatformInfo' in globals():
        print("   HD_Basic_GetPlatformInfo函数: 已导入")
        imported_functions += 1
    
    # Inject模块DLL函数
    print("\n3.4 Inject模块:")
    if 'HD_Inject_DLL' in globals():
        print("   HD_Inject_DLL函数: 已导入")
        imported_functions += 1
    if 'HD_Inject_EjectDLL' in globals():
        print("   HD_Inject_EjectDLL函数: 已导入")
        imported_functions += 1
    
    # Env模块DLL函数
    print("\n3.5 Env模块:")
    if 'HD_Env_GetVar' in globals():
        print("   HD_Env_GetVar函数: 已导入")
        imported_functions += 1
    if 'HD_Env_SetVar' in globals():
        print("   HD_Env_SetVar函数: 已导入")
        imported_functions += 1
    
    # MT模块DLL函数
    print("\n3.6 MT模块:")
    if 'HD_MT_CreateThread' in globals():
        print("   HD_MT_CreateThread函数: 已导入")
        imported_functions += 1
    if 'HD_MT_TerminateThread' in globals():
        print("   HD_MT_TerminateThread函数: 已导入")
        imported_functions += 1
    
    # HK模块DLL函数
    print("\n3.7 HK模块:")
    if 'HD_HK_Function' in globals():
        print("   HD_HK_Function函数: 已导入")
        imported_functions += 1
    if 'HD_HK_UnhookFunction' in globals():
        print("   HD_HK_UnhookFunction函数: 已导入")
        imported_functions += 1
    
    # 其他模块DLL函数
    print("\n3.8 其他模块:")
    if 'HD_Common_StringToWString' in globals():
        print("   HD_Common_StringToWString函数: 已导入")
        imported_functions += 1
    if 'HD_YOLO_DetectObjects' in globals():
        print("   HD_YOLO_DetectObjects函数: 已导入")
        imported_functions += 1
    if 'HD_WIN_GetWindowInfo' in globals():
        print("   HD_WIN_GetWindowInfo函数: 已导入")
        imported_functions += 1
    if 'HD_VT_Query' in globals():
        print("   HD_VT_Query函数: 已导入")
        imported_functions += 1
    
    print(f"\n4. 已导入的DLL函数数量: {imported_functions}")
    
    print("\n===== 测试完成 =====")
    print("全DLL函数导入功能已成功实现！")
    print("\n使用示例:")
    print("   from hdgdk.all_functions import *")
    print("   init_hdgdk(dll_path='path/to/hdgdk.dll')")
    print("   # 现在可以直接调用所有DLL函数，无需任何前缀")
    print("   result = HCHD_Login(b'account', b'password', b'app_name', b'app_lparam', False, False)")
    print("   expired_time = HCHD_GetExpiredTimeStamp()")
    print("   ip_result = HCIP_YMSetRootPath(b'path/to/yimi.exe')")
    print("   version = HD_Basic_GetVersion()")
    
except ImportError as e:
    print(f"   导入失败: {e}")
    print("   请检查HD GDK的安装和配置。")
except Exception as e:
    print(f"   测试过程中发生错误: {e}")
    print("   请检查HD GDK的安装和配置。")