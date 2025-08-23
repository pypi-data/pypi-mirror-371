#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 直接API使用示例
展示如何使用直接函数调用而不需要类名前缀
"""

# 方式1: 使用直接导入的函数（推荐的最简方式）
from hdgdk import init_hdgdk, login, get_fyi

# 方式2: 导入整个直接API模块
import hdgdk.direct_api as api

# 方式3: 传统方式（用于对比）
from hdgdk import HDGDK


def demo_direct_function_calls():
    """
    演示直接函数调用方式
    """
    print("===== 直接函数调用示例 =====")
    
    try:
        # 初始化HD GDK（只需调用一次）
        # 注意：如果未指定dll_path，会尝试使用默认路径
        init_hdgdk(dll_path="path/to/hdgdk.dll")
        print("HD GDK初始化成功")
        
        # 直接调用login函数，不需要类名前缀
        account = "your_account"
        password = "your_password"
        app_name = "your_app"
        app_lparam = "your_params"
        
        print(f"执行登录: 账号={account}")
        # 这里是用户期望的简化调用方式
        result = login(account, password, app_name, app_lparam)
        print(f"登录结果: {result}")
        
        # 获取点数信息
        fyi_result = get_fyi()
        print(f"点数信息: {fyi_result}")
        
    except Exception as e:
        print(f"直接函数调用错误: {e}")
        print("提示: 确保HD GDK DLL文件路径正确")


def demo_direct_api_module():
    """
    演示通过direct_api模块调用
    """
    print("\n===== 通过direct_api模块调用示例 =====")
    
    try:
        # 初始化可以通过模块完成
        api.init_hdgdk(dll_path="path/to/hdgdk.dll")
        
        # 通过模块访问直接函数
        account = "your_account"
        password = "your_password"
        app_name = "your_app"
        app_lparam = "your_params"
        
        result = api.login(account, password, app_name, app_lparam)
        print(f"通过模块调用login结果: {result}")
        
    except Exception as e:
        print(f"模块调用错误: {e}")


def demo_traditional_method():
    """
    演示传统的调用方式（用于对比）
    """
    print("\n===== 传统调用方式示例（对比）=====")
    
    try:
        # 传统方式：先初始化HDGDK类
        HDGDK.init("path/to/hdgdk.dll")
        
        # 然后通过类访问模块，再调用方法
        account = "your_account"
        password = "your_password"
        app_name = "your_app"
        app_lparam = "your_params"
        
        result = HDGDK.login.login(account, password, app_name, app_lparam)
        print(f"传统方式调用结果: {result}")
        
        # 这是用户之前提到的复杂写法
        print("传统调用方式写法: HDGDK.login.login(...)")
        
    except Exception as e:
        print(f"传统方式调用错误: {e}")


def demo_real_world_usage():
    """
    演示实际应用场景中的使用方式
    """
    print("\n===== 实际应用场景示例 =====")
    
    # 应用配置
    app_config = {
        "dll_path": "path/to/hdgdk.dll",
        "account": "production_account",
        "password": "production_password",
        "app_name": "MyApplication",
        "app_params": "--mode=production"
    }
    
    try:
        # 初始化（通常在应用启动时执行一次）
        init_hdgdk(app_config["dll_path"])
        
        # 登录操作
        login_result = login(
            app_config["account"],
            app_config["password"],
            app_config["app_name"],
            app_config["app_params"]
        )
        
        if login_result > 0:
            print(f"登录成功! 版本号: {login_result}")
            
            # 登录成功后执行其他操作
            fyi_info = get_fyi()
            print(f"当前点数: {fyi_info}")
            
            # 更多业务逻辑...
        else:
            print(f"登录失败，错误码: {login_result}")
            
    except Exception as e:
        print(f"应用运行错误: {e}")


def demo_error_handling():
    """
    演示错误处理方式
    """
    print("\n===== 错误处理示例 =====")
    
    try:
        # 场景1: 未初始化就调用函数
        print("尝试不初始化就调用函数...")
        # 注意：直接API会自动尝试初始化，但最好显式调用init_hdgdk
        result = get_fyi()
        print(f"调用成功: {result}")
        
    except Exception as e:
        print(f"预期的错误: {e}")
        
    try:
        # 场景2: 初始化后处理错误
        init_hdgdk()
        print("初始化后，尝试使用无效的账号密码...")
        result = login("invalid_account", "invalid_password", "test_app", "test")
        print(f"登录结果: {result}")
        
        # 根据返回值处理不同情况
        if result <= 0:
            print("处理登录失败的情况...")
            
    except Exception as e:
        print(f"发生异常: {e}")


def main():
    """主函数"""
    print("HD GDK 直接API调用示例\n")
    
    # 运行各个演示
    demo_direct_function_calls()
    demo_direct_api_module()
    demo_traditional_method()
    demo_real_world_usage()
    demo_error_handling()
    
    print("\n=== 示例结束 ===")
    print("总结:")
    print("1. 直接函数调用: login(...)       # 最简洁的方式，推荐使用")
    print("2. 模块方式调用: api.login(...)    # 适合需要命名空间隔离的情况")
    print("3. 传统方式调用: HDGDK.login.login(...)  # 原有的复杂方式")


if __name__ == "__main__":
    main()