#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD GDK 模块级API接口
提供模块级别的导入和调用功能，用户可以一次性导入整个模块并直接调用其中的函数
"""

import sys
import importlib
from .api_manager import get_hdgdk_manager

# 模块名称映射关系，用于动态导入模块
_MODULE_NAME_MAPPING = {
    'login': 'hd_login',
    'ip': 'hd_ip',
    'basic': 'hd_basic',
    'inject': 'hd_inject',
    'env': 'hd_env',
    'mt': 'hd_mt',
    'hk': 'hd_hk',
    'common': 'hd_common',
    'shell_code': 'hd_shell_code',
    'yolo': 'hd_yolo',
    'vnc': 'hd_vnc',
    'win': 'hd_win',
    'vt': 'hd_vt',
    'lua': 'hd_lua',
    'normal': 'hd_normal',
    'pp': 'hd_pp',
    'target': 'hd_target',
    'nt': 'hd_nt',
    'hd': 'hd_hd',
    'm': 'hd_m',
    'fp': 'hd_fp',
    'fs': 'hd_fs',
    'com': 'hd_com',
    'cs': 'hd_cs',
    'fi': 'hd_fi',
    'sc': 'hd_sc',
    'bs': 'hd_bs',
    'mkb': 'hd_mkb',
    'rc': 'hd_rc',
    'vm': 'hd_vm',
    'vmdma': 'hd_vmdma',
    'gb': 'hd_gb',
    'ds': 'hd_ds',
    'res': 'hd_res',
    'json': 'hd_json',
    'dw': 'hd_dw',
    'sys': 'hd_sys',
    'status': 'hd_status'
}

class HDGDKModuleWrapper:
    """HD GDK模块包装器，用于延迟加载和调用模块方法"""
    def __init__(self, module_name):
        """
        初始化模块包装器
        
        Args:
            module_name (str): 模块名称
        """
        self._module_name = module_name
        self._actual_module = None
        self._manager = None

    def _ensure_manager(self):
        """确保管理器已初始化"""
        if self._manager is None:
            self._manager = get_hdgdk_manager()
            # 初始化DLL（如果尚未初始化）
            if not self._manager._initialized:
                self._manager.initialize_dll(None)

    def _ensure_module(self):
        """确保模块已加载"""
        if self._actual_module is None:
            self._ensure_manager()
            try:
                # 尝试通过管理器获取模块实例
                self._actual_module = self._manager.get_module(self._module_name)
            except Exception as e:
                # 如果通过管理器获取失败，尝试直接导入模块文件
                try:
                    # 构建模块导入路径
                    module_path = f"hdgdk.{self._module_name}"
                    imported_module = importlib.import_module(module_path)
                    
                    # 查找模块创建函数（create_hd_xxx模式）
                    module_class_name = f"HD{self._module_name.capitalize()}"
                    if hasattr(imported_module, module_class_name):
                        module_class = getattr(imported_module, module_class_name)
                        # 尝试创建模块实例
                        self._actual_module = module_class()
                except Exception:
                    raise RuntimeError(f"无法加载 '{self._module_name}' 模块")

    def __getattr__(self, name):
        """动态获取并调用模块方法"""
        def method_wrapper(*args, **kwargs):
            # 确保模块已加载
            self._ensure_module()
            # 调用实际模块的方法
            if hasattr(self._actual_module, name):
                method = getattr(self._actual_module, name)
                return method(*args, **kwargs)
            else:
                raise AttributeError(f"模块 '{self._module_name}' 没有方法 '{name}'")
        
        # 设置方法名称和文档
        method_wrapper.__name__ = name
        method_wrapper.__doc__ = f"HD GDK {self._module_name}模块的{name}方法"
        
        return method_wrapper

# 创建模块实例缓存
_module_instances = {}

# 动态创建模块包装器
for module_name in _MODULE_NAME_MAPPING.keys():
    try:
        _module_instances[module_name] = HDGDKModuleWrapper(module_name)
        setattr(sys.modules[__name__], module_name, _module_instances[module_name])
    except Exception as e:
        # 如果创建失败，继续处理其他模块
        pass

# 为login模块特殊处理，避免与函数名冲突
def get_login_module():
    """获取login模块实例（避免与login函数名冲突）"""
    if 'login' not in _module_instances:
        _module_instances['login'] = HDGDKModuleWrapper('login')
    return _module_instances['login']

# 提供login_module别名，方便用户使用
login_module = get_login_module()

def get_module(module_name):
    """
    获取指定名称的模块实例
    
    Args:
        module_name (str): 模块名称
        
    Returns:
        HDGDKModuleWrapper: 模块包装器实例
        
    Raises:
        ValueError: 当模块不存在时
    """
    if module_name not in _MODULE_NAME_MAPPING:
        raise ValueError(f"不支持的模块: {module_name}")
    
    if module_name not in _module_instances:
        _module_instances[module_name] = HDGDKModuleWrapper(module_name)
    
    return _module_instances[module_name]