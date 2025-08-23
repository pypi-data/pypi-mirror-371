#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 所有调用方式对比示例
展示从最原始到最新的所有API调用方式，帮助选择最适合的方法
"""

# 配置信息（请根据实际情况修改）
CONFIG = {
    "dll_path": "path/to/hdgdk.dll",  # HD GDK DLL文件路径
    "account": "your_account",        # 账号
    "password": "your_password",      # 密码
    "app_name": "your_application",   # 应用名称
    "app_lparam": "--mode=demo"        # 应用参数
}


# ========== 方式1: 原始调用方式（最繁琐） ==========

def demo_original_method():
    """
    演示最原始的调用方式
    特点：步骤繁琐，代码冗余
    """
    print("===== 方式1: 原始调用方式 ======")
    print("特点：需要手动导入、创建实例、调用方法")
    print("语法：create_hd_login(...).login(...)")
    
    try:
        # 1. 手动导入所需模块
        from hdgdk import create_hd_login
        
        # 2. 手动创建模块实例
        login_module = create_hd_login(CONFIG["dll_path"])
        
        # 3. 调用实例的方法
        result = login_module.login(
            CONFIG["account"],
            CONFIG["password"],
            CONFIG["app_name"],
            CONFIG["app_lparam"]
        )
        
        print(f"登录结果: {result}")
        
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 这是最原始的调用方式，已不推荐使用")


# ========== 方式2: HDGDKManager类调用方式 ==========

def demo_manager_class_method():
    """
    演示使用HDGDKManager类的调用方式
    特点：提供完全控制，适合需要自定义配置的场景
    """
    print("\n===== 方式2: HDGDKManager类调用方式 ======")
    print("特点：统一管理，完全控制，适合自定义配置")
    print("语法：manager.login.login(...)")
    
    try:
        # 1. 导入HDGDKManager类
        from hdgdk import HDGDKManager
        
        # 2. 创建管理器实例（可自定义配置）
        manager = HDGDKManager(
            dll_path=CONFIG["dll_path"],
            is_debug=False  # 可自定义调试模式
        )
        
        # 3. 通过管理器访问模块并调用方法
        result = manager.login.login(
            CONFIG["account"],
            CONFIG["password"],
            CONFIG["app_name"],
            CONFIG["app_lparam"]
        )
        
        print(f"登录结果: {result}")
        
        # 额外功能：检查模块是否存在
        if manager.has_module("ip"):
            print("IP模块可用，可以获取IP信息")
        
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 适合需要完全控制模块生命周期的场景")


# ========== 方式3: get_hdgdk_manager函数调用方式 ==========

def demo_manager_function_method():
    """
    演示使用get_hdgdk_manager函数的调用方式
    特点：提供全局单例，适合多模块协作场景
    """
    print("\n===== 方式3: get_hdgdk_manager函数调用方式 ======")
    print("特点：全局单例，统一管理，适合多模块协作")
    print("语法：manager.login.login(...)")
    
    try:
        # 1. 导入get_hdgdk_manager函数
        from hdgdk import get_hdgdk_manager
        
        # 2. 获取全局管理器实例（自动处理单例）
        manager = get_hdgdk_manager(CONFIG["dll_path"])
        
        # 3. 通过管理器访问模块并调用方法
        result = manager.login.login(
            CONFIG["account"],
            CONFIG["password"],
            CONFIG["app_name"],
            CONFIG["app_lparam"]
        )
        
        print(f"登录结果: {result}")
        
        # 可以在多处获取同一实例
        another_manager = get_hdgdk_manager()
        print(f"是否为同一实例: {manager is another_manager}")
        
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 适合需要在多处共享模块实例的场景")


# ========== 方式4: HDGDK简化接口类调用方式 ==========

def demo_hdgdk_class_method():
    """
    演示使用HDGDK简化接口类的调用方式
    特点：结构化组织，无需管理实例
    """
    print("\n===== 方式4: HDGDK简化接口类调用方式 ======")
    print("特点：结构化，组织清晰，无需手动管理实例")
    print("语法：HDGDK.login.login(...)")
    
    try:
        # 1. 导入HDGDK类
        from hdgdk import HDGDK
        
        # 2. 初始化（只需一次）
        HDGDK.init(CONFIG["dll_path"])
        
        # 3. 直接通过类访问模块和方法
        result = HDGDK.login.login(
            CONFIG["account"],
            CONFIG["password"],
            CONFIG["app_name"],
            CONFIG["app_lparam"]
        )
        
        print(f"登录结果: {result}")
        
        # 可以方便地使用多个模块
        try:
            ip_info = HDGDK.ip.get_local_ip()
            print(f"本地IP信息: {ip_info}")
        except:
            print("获取IP信息示例")
        
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 适合需要清晰模块组织的场景")


# ========== 方式5: 直接函数调用方式（最新，最简洁） ==========

def demo_direct_function_method():
    """
    演示使用直接函数调用的方式
    特点：最简洁，无需类名前缀
    """
    print("\n===== 方式5: 直接函数调用方式 ======")
    print("特点：最简洁，无需类名前缀，最新特性")
    print("语法：login(...)")
    
    try:
        # 1. 直接导入所需函数
        from hdgdk import init_hdgdk, login, get_fyi
        
        # 2. 初始化（只需一次）
        init_hdgdk(CONFIG["dll_path"])
        
        # 3. 直接调用函数，无需任何类名前缀
        # 这正是用户期望的简化调用方式！
        result = login(
            CONFIG["account"],
            CONFIG["password"],
            CONFIG["app_name"],
            CONFIG["app_lparam"]
        )
        
        print(f"登录结果: {result}")
        
        # 直接调用其他函数
        try:
            fyi_info = get_fyi()
            print(f"点数信息: {fyi_info}")
        except:
            print("获取点数信息示例")
        
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 这是最简洁的调用方式，推荐日常使用")


# ========== 方式6: 直接API模块调用方式 ==========

def demo_direct_api_module_method():
    """
    演示通过direct_api模块调用的方式
    特点：通过模块名调用，适合需要命名空间隔离的情况
    """
    print("\n===== 方式6: 直接API模块调用方式 ======")
    print("特点：通过模块调用，保持命名空间隔离")
    print("语法：api.login(...)")
    
    try:
        # 1. 导入direct_api模块
        import hdgdk.direct_api as api
        
        # 2. 初始化（只需一次）
        api.init_hdgdk(CONFIG["dll_path"])
        
        # 3. 通过模块调用函数
        result = api.login(
            CONFIG["account"],
            CONFIG["password"],
            CONFIG["app_name"],
            CONFIG["app_lparam"]
        )
        
        print(f"登录结果: {result}")
        
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 适合需要命名空间隔离的场景")


# ========== 综合对比与性能考量 ==========

def demo_comparison_summary():
    """
    综合对比所有调用方式
    """
    print("\n\n===== 调用方式综合对比 ======")
    print("\n各调用方式优缺点总结:")
    print("\n1. 原始调用方式:")
    print("   ✅ 完全向后兼容")
    print("   ❌ 步骤繁琐，代码冗余")
    print("   ❌ 容易创建重复实例")
    
    print("\n2. HDGDKManager类方式:")
    print("   ✅ 完全控制，灵活配置")
    print("   ✅ 统一管理模块生命周期")
    print("   ❌ 多了一层实例管理")
    
    print("\n3. get_hdgdk_manager函数方式:")
    print("   ✅ 全局单例，避免重复创建")
    print("   ✅ 多模块协作更方便")
    print("   ❌ 语法仍有一定复杂度")
    
    print("\n4. HDGDK简化接口类方式:")
    print("   ✅ 结构化，组织清晰")
    print("   ✅ 无需手动管理实例")
    print("   ❌ 仍需使用类名前缀")
    
    print("\n5. 直接函数调用方式:")
    print("   ✅ 最简洁，代码最干净")
    print("   ✅ 使用门槛最低")
    print("   ✅ 减少记忆负担")
    print("   ❌ 函数名可能冲突（需注意命名）")
    
    print("\n6. direct_api模块调用方式:")
    print("   ✅ 保持命名空间隔离")
    print("   ✅ 避免函数名冲突")
    print("   ❌ 比直接函数调用多了一层模块引用")
    
    print("\n\n===== 性能与内存考量 ======")
    print("- 所有优化方式都使用了延迟加载和实例缓存机制")
    print("- 内存占用方面差异很小，主要是代码风格和使用便捷性的区别")
    print("- 直接函数调用在首次调用时有极轻微的包装开销，但后续调用与其他方式无异")


def main():
    """
    主函数，运行所有演示
    """
    print("HD GDK 所有调用方式对比演示\n")
    print("本示例展示了从最原始到最新的所有API调用方式，帮助您选择最适合的方法\n")
    
    # 运行所有演示
    demo_original_method()
    demo_manager_class_method()
    demo_manager_function_method()
    demo_hdgdk_class_method()
    demo_direct_function_method()
    demo_direct_api_module_method()
    demo_comparison_summary()
    
    print("\n\n===== 推荐使用方式 ======")
    print("1. 对于新开发的项目：优先使用【直接函数调用方式】")
    print("2. 对于需要模块组织的场景：使用【HDGDK简化接口类方式】")
    print("3. 对于复杂应用：根据需求选择【get_hdgdk_manager函数方式】或【HDGDKManager类方式】")
    print("4. 对于旧代码：保持【原始调用方式】或逐步迁移到新方式")


if __name__ == "__main__":
    main()