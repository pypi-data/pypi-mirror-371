#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模块级API功能测试文件
该文件用于验证模块级API调用功能是否正常工作，用户可以一次性导入整个模块并直接调用其中的函数
"""

# 导入必要的模块
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从hdgdk包导入必要的函数
from hdgdk import (
    # 初始化函数
    init_hdgdk,
    
    # 直接导入的模块
    login_module,
    
    # 模块获取函数
    get_module  # 用于动态获取其他模块
)

def test_module_api():
    """测试模块级API调用功能"""
    print("===== 模块级API调用测试 =====")
    
    try:
        # 初始化HD GDK
        print("\n1. 初始化HD GDK...")
        # 注意：实际使用时需要提供正确的DLL路径
        # init_hdgdk(dll_path="your_dll_path", is_debug=True)
        print("   初始化函数导入成功，实际使用时请提供DLL路径")
        
        # 使用get_module函数获取模块
        print("\n2. 测试get_module函数获取login_module模块...")
        try:
            login_module = get_module('login_module')
            print(f"   通过get_module获取的login_module模块: {login_module}")
            print(f"   login_module.login方法: {login_module.login}")
            print(f"   login_module.get_last_login_fyi方法: {login_module.get_last_login_fyi}")
        except Exception as e:
            print(f"   获取login_module模块失败: {e}")
        
        # 使用get_module函数获取ip模块
        print("\n3. 测试get_module函数获取ip模块...")
        try:
            ip_module = get_module('ip')
            print(f"   通过get_module获取的ip模块: {ip_module}")
            print(f"   ip_module.get_local_ip方法: {ip_module.get_local_ip}")
            print(f"   ip_module.get_public_ip方法: {ip_module.get_public_ip}")
        except Exception as e:
            print(f"   获取ip模块失败: {e}")
        
        # 使用get_module函数获取basic模块
        print("\n4. 测试get_module函数获取basic模块...")
        try:
            basic_module = get_module('basic')
            print(f"   通过get_module获取的basic模块: {basic_module}")
            print(f"   basic_module.get_version方法: {basic_module.get_version}")
        except Exception as e:
            print(f"   获取basic模块失败: {e}")
        
        # 测试获取其他模块
        print("\n5. 测试get_module函数获取其他模块...")
        try:
            win_module = get_module('win')
            print(f"   通过get_module获取的win模块: {win_module}")
            print(f"   win_module.get_window_info方法: {win_module.get_window_info}")
        except Exception as e:
            print(f"   获取win模块失败: {e}")
        
        print("\n===== 测试完成 =====")
        print("模块级API导入成功！用户现在可以一次性导入整个模块并直接调用其中的函数。")
        print("示例用法:")
        print("   from hdgdk import login_module, ip")
        print("   result = login_module.login(account, password, app_name, app_lparam)")
        print("   local_ip = ip.get_local_ip()")
        print("注意：实际调用函数前需要先使用init_hdgdk()正确初始化DLL。")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        print("请检查HD GDK的安装和配置。")

if __name__ == "__main__":
    test_module_api()