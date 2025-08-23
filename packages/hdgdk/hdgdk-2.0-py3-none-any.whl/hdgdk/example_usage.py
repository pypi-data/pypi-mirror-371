#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK使用示例
演示如何使用新的API管理器来简化模块调用
"""

def old_usage_example():
    """
    旧的使用方式 - 每个模块都需要手动实例化
    """
    print("===== 旧的使用方式示例 =====")
    
    try:
        # 1. 首先需要初始化DLL管理器
        from hdgdk import init_dll_manager
        dll_path = "path/to/dll"
        init_dll_manager(dll_path)
        
        # 2. 手动实例化每个需要的模块
        from hdgdk import create_hd_login, create_hd_ip, create_hd_basic, create_hd_ex
        
        # 创建各模块实例
        login_module = create_hd_login()
        ip_module = create_hd_ip()
        basic_module = create_hd_basic()
        ex_module = create_hd_ex()
        
        # 使用各模块功能
        # login_module.login(...) 
        # ip_module.some_method()
        # 等等...
        
        print("手动创建了4个模块实例")
        print("优点: 精确控制每个模块的创建时机和参数")
        print("缺点: 繁琐，需要导入多个创建函数，手动管理多个实例")
        
    except Exception as e:
        print(f"错误: {e}")
        print("注意: 此示例仅用于演示调用流程，实际运行需要正确的DLL路径")


def new_usage_example():
    """
    新的使用方式 - 使用API管理器简化调用
    """
    print("\n===== 新的使用方式示例 =====")
    
    try:
        # 方式1: 使用HDGDKManager类
        from hdgdk import HDGDKManager
        
        # 初始化管理器（只需一次）
        dll_path = "path/to/dll"
        manager = HDGDKManager(dll_path)
        
        # 直接通过管理器访问需要的模块（延迟加载，只有在访问时才会创建实例）
        # 使用登录模块
        # manager.login.login(account, password, app_name, app_lparam)
        
        # 使用IP模块
        # manager.ip.some_method()
        
        # 使用其他模块
        # manager.basic.some_method()
        # manager.ex.some_method()
        # manager.win.some_method()
        # manager.vm.some_method()
        # ...等等
        
        print("通过HDGDKManager访问模块")
        print(f"可用模块列表: {', '.join(manager.list_available_modules())}")
        
        # 方式2: 使用全局管理器实例（单例模式）
        from hdgdk import get_hdgdk_manager
        
        # 获取全局管理器实例（会返回上面已创建的实例）
        global_manager = get_hdgdk_manager()
        
        # 检查是否是同一个实例
        print(f"是否是同一个管理器实例: {manager is global_manager}")
        
        # 方式3: 使用简化的HDGDK接口类
        from hdgdk import HDGDK
        
        # 初始化（如果之前没初始化过）
        # HDGDK.init(dll_path)
        
        # 直接通过HDGDK类访问模块
        # HDGDK.login.login(account, password, app_name, app_lparam)
        # HDGDK.ip.some_method()
        # ...等等
        
        print("通过HDGDK类访问模块")
        print("优点:")
        print("1. 简化了模块的导入和实例化过程")
        print("2. 支持延迟加载，只在需要时才创建模块实例")
        print("3. 统一管理所有模块实例，避免重复创建")
        print("4. 提供多种访问方式，适应不同的使用场景")
        print("5. 减少了样板代码，提高了开发效率")
        
    except Exception as e:
        print(f"错误: {e}")
        print("注意: 此示例仅用于演示调用流程，实际运行需要正确的DLL路径")


def comprehensive_example():
    """
    综合示例 - 展示更多高级用法
    """
    print("\n===== 综合示例 =====")
    
    try:
        from hdgdk import HDGDKManager
        
        # 初始化管理器
        manager = HDGDKManager("path/to/dll")
        
        # 检查模块是否存在
        module_name = "login"
        if manager.has_module(module_name):
            print(f"模块 '{module_name}' 存在")
        else:
            print(f"模块 '{module_name}' 不存在")
        
        # 动态获取模块
        module = manager.get_module("ip")
        print(f"动态获取了模块: {module.__class__.__name__}")
        
        # 预加载所有模块（一般不推荐，除非确实需要）
        # manager.initialize_all()
        # print("已预加载所有模块")
        
        # 使用模块链
        # 例如: 先登录，然后获取IP信息，再执行其他操作
        # result = manager.login.login(...) 
        # if result > 0:
        #     ip_info = manager.ip.get_ip_info()
        #     manager.basic.do_something(ip_info)
        #     # ...
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 运行所有示例
    old_usage_example()
    new_usage_example()
    comprehensive_example()
    
    print("\n===== 使用建议 =====")
    print("1. 对于新项目，建议使用HDGDK简化接口类")
    print("2. 对于已有项目，可以逐步迁移到新的API管理器")
    print("3. 对于需要精确控制的场景，可以使用HDGDKManager类")
    print("4. 所有旧的API仍然有效，可以混合使用")