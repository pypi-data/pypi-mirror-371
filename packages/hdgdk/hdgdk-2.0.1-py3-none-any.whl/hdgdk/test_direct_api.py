#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接API功能测试文件
该文件用于验证直接API函数调用功能是否正常工作，用户可以无需类名前缀直接使用各种函数
"""

# 导入必要的模块
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从hdgdk包直接导入函数
from hdgdk import (
    # 初始化函数
    init_hdgdk,
    
    # Login模块函数
    login, get_last_login_fyi,
    
    # Basic模块函数
    get_version,
    
    # IP模块函数
    get_local_ip,
    
    # Common模块函数
    string_to_wstring,
    
    # 其他常用函数
    get_window_info
)

def test_direct_api():
    """测试直接API函数调用功能"""
    print("===== 直接API函数调用测试 =====")
    
    try:
        # 初始化HD GDK
        print("\n1. 初始化HD GDK...")
        # 注意：实际使用时需要提供正确的DLL路径
        # init_hdgdk(dll_path="your_dll_path", is_debug=True)
        print("   初始化函数导入成功，实际使用时请提供DLL路径")
        
        # 测试Login模块函数
        print("\n2. 测试Login模块函数...")
        print(f"   login函数: {login}")
        print(f"   get_last_login_fyi函数: {get_last_login_fyi}")
        
        # 测试Basic模块函数
        print("\n3. 测试Basic模块函数...")
        print(f"   get_version函数: {get_version}")
        
        # 测试IP模块函数
        print("\n4. 测试IP模块函数...")
        print(f"   get_local_ip函数: {get_local_ip}")
        
        # 测试Common模块函数
        print("\n5. 测试Common模块函数...")
        print(f"   string_to_wstring函数: {string_to_wstring}")
        
        # 测试其他函数
        print("\n6. 测试其他函数...")
        print(f"   get_window_info函数: {get_window_info}")
        
        print("\n===== 测试完成 =====")
        print("直接API函数导入成功！用户现在可以直接使用这些函数，无需类名前缀。")
        print("注意：实际调用函数前需要先使用init_hdgdk()正确初始化DLL。")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        print("请检查HD GDK的安装和配置。")

if __name__ == "__main__":
    test_direct_api()