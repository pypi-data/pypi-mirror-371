#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK API管理器
提供对所有HD GDK模块的统一访问和管理，简化模块实例化和调用过程
"""

from .dll_manager import init_dll_manager, get_dll_manager
from .base_module import HDModuleBase

class HDGDKManager:
    """
    HD GDK API管理器
    负责统一管理所有HD GDK模块的实例化和访问
    """
    def __init__(self, dll_path=None, is_debug=False):
        """
        初始化API管理器
        
        Args:
            dll_path (str): DLL文件所在路径
            is_debug (bool): 是否使用调试版DLL
        """
        # 初始化DLL管理器
        if dll_path:
            init_dll_manager(dll_path, is_debug)
        else:
            # 确保DLL管理器已初始化
            get_dll_manager()
            
        # 存储模块实例的字典
        self._modules = {}
        
        # 存储DLL路径和调试模式
        self.dll_path = dll_path
        self.is_debug = is_debug
        
        # 模块创建函数映射表
        self._module_factories = {
            'login': self._import_and_create('create_hd_login', 'login'),
            'ip': self._import_and_create('create_hd_ip', 'ip'),
            'ex': self._import_and_create('create_hd_ex', 'ex'),
            'basic': self._import_and_create('create_hd_basic', 'basic'),
            'inject': self._import_and_create('create_hd_inject', 'inject'),
            'env': self._import_and_create('create_hd_env', 'env'),
            'mt': self._import_and_create('create_hd_mt', 'mt'),
            'hk': self._import_and_create('create_hd_hk', 'hk'),
            'common': self._import_and_create('create_hd_common', 'common'),
            'shell_code': self._import_and_create('create_hd_shell_code', 'sh'),
            'yolo': self._import_and_create('create_yolo', 'yolo'),
            'vnc': self._import_and_create('create_vnc', 'vnc'),
            'win': self._import_and_create('create_win', 'win'),
            'vt': self._import_and_create('create_vt', 'vt'),
            'lua': self._import_and_create('create_hd_lua', 'lua'),
            'normal': self._import_and_create('create_normal', 'normal'),
            'pp': self._import_and_create('create_pp', 'pp'),
            'target': self._import_and_create('create_target', 'target'),
            'nt': self._import_and_create('create_nt', 'nt'),
            'hd': self._import_and_create('create_hd', 'hd'),
            'm': self._import_and_create('create_m', 'm'),
            'fp': self._import_and_create('create_fp', 'fp'),
            'fs': self._import_and_create('create_fs', 'fs'),
            'com': self._import_and_create('create_hd_com', 'com'),
            'cs': self._import_and_create('create_hd_cs', 'cs'),
            'fi': self._import_and_create('create_fi', 'fi'),
            'sc': self._import_and_create('create_hd_sc', 'sc'),
            'bs': self._import_and_create('create_hd_bs', 'bs'),
            'mkb': self._import_and_create('create_hd_mkb', 'mkb'),
            'rc': self._import_and_create('create_rc', 'rc'),
            'vm': self._import_and_create('create_hd_vm', 'vm'),
            'vmdma': self._import_and_create('create_hd_vmdma', 'vmdma'),
            'gb': self._import_and_create('create_hd_gb', 'gb'),
            'ds': self._import_and_create('create_hd_ds', 'ds'),
            'res': self._import_and_create('create_hd_res', 'res'),
            'json': self._import_and_create('create_hd_json', 'json_module'),
            'dw': self._import_and_create('create_hd_dw', 'dw'),
            'sys': self._import_and_create('create_hd_sys', 'sys'),
            'status': self._import_and_create('create_hd_status', 'status')
        }
    
    def _import_and_create(self, factory_name, module_name):
        """
        动态导入模块并创建工厂函数
        
        Args:
            factory_name (str): 工厂函数名
            module_name (str): 模块名
        
        Returns:
            function: 包装后的工厂函数
        """
        def factory_func():
            module = __import__(f'.{module_name}', globals=globals(), locals=locals(), fromlist=[factory_name], level=1)
            create_func = getattr(module, factory_name)
            return create_func(self.dll_path, self.is_debug)
        return factory_func
    
    def __getattr__(self, name):
        """
        延迟加载模块实例
        
        Args:
            name (str): 模块名称
        
        Returns:
            HDModuleBase: 模块实例
        
        Raises:
            AttributeError: 当请求的模块不存在时
        """
        # 如果模块实例已存在，直接返回
        if name in self._modules:
            return self._modules[name]
        
        # 检查模块名称是否在工厂映射表中
        if name in self._module_factories:
            # 创建模块实例并缓存
            self._modules[name] = self._module_factories[name]()
            return self._modules[name]
        
        # 如果找不到模块，抛出属性错误
        raise AttributeError(f"模块 '{name}' 不存在")
    
    def initialize_all(self):
        """
        预初始化所有模块（可选，一般不推荐除非确实需要）
        
        Returns:
            self: 返回自身以支持链式调用
        """
        for module_name in self._module_factories:
            if module_name not in self._modules:
                self._modules[module_name] = self._module_factories[module_name]()
        return self
    
    def get_module(self, module_name):
        """
        获取指定的模块实例
        
        Args:
            module_name (str): 模块名称
        
        Returns:
            HDModuleBase: 模块实例
        
        Raises:
            ValueError: 当请求的模块不存在时
        """
        if not hasattr(self, module_name):
            raise ValueError(f"模块 '{module_name}' 不存在")
        return getattr(self, module_name)
    
    def has_module(self, module_name):
        """
        检查是否存在指定的模块
        
        Args:
            module_name (str): 模块名称
        
        Returns:
            bool: 是否存在该模块
        """
        return module_name in self._module_factories
    
    def list_available_modules(self):
        """
        列出所有可用的模块
        
        Returns:
            list: 模块名称列表
        """
        return list(self._module_factories.keys())

# 创建默认的API管理器实例（懒加载）
_default_manager = None

def get_hdgdk_manager(dll_path=None, is_debug=False):
    """
    获取或创建HD GDK管理器实例
    
    Args:
        dll_path (str): DLL文件所在路径
        is_debug (bool): 是否使用调试版DLL
    
    Returns:
        HDGDKManager: 管理器实例
    """
    global _default_manager
    if _default_manager is None or (dll_path and dll_path != _default_manager.dll_path):
        _default_manager = HDGDKManager(dll_path, is_debug)
    return _default_manager

# 提供一个简化的接口类，用于更方便地访问常用功能
class HDGDK:
    """
    HD GDK简化接口类
    提供对HD GDK功能的直接访问，无需手动管理管理器实例
    """
    _manager = None
    
    @classmethod
    def init(cls, dll_path, is_debug=False):
        """
        初始化HD GDK
        
        Args:
            dll_path (str): DLL文件所在路径
            is_debug (bool): 是否使用调试版DLL
        """
        cls._manager = get_hdgdk_manager(dll_path, is_debug)
        
    @classmethod
    def __getattr__(cls, name):
        """
        转发属性访问到管理器实例
        """
        if cls._manager is None:
            raise RuntimeError("HD GDK尚未初始化，请先调用init()方法")
        return getattr(cls._manager, name)
    
    @classmethod
    def get_manager(cls):
        """
        获取底层的管理器实例
        
        Returns:
            HDGDKManager: 管理器实例
        """
        if cls._manager is None:
            raise RuntimeError("HD GDK尚未初始化，请先调用init()方法")
        return cls._manager