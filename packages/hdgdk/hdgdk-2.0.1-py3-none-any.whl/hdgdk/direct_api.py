#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 直接API模块
提供无需类名前缀的DLL函数直接调用功能
"""

from .api_manager import HDGDK, get_hdgdk_manager
import inspect

# 全局DLL路径配置
_global_dll_path = None
_global_is_debug = False

# 已初始化的标志
_initialized = False

# 缓存已包装的函数
_wrapped_functions = {}

# 模块与DLL函数名映射关系
def _get_module_dll_function_map():
    """返回模块与DLL函数名的映射关系"""
    return {
        'login': ['HCHD_Login', 'HCHD_GetLastLoginFYI', 'HCHD_GetExpiredTimeStamp', 'HCHD_GetFYI', 'HCHD_GetOpenMaxNum'],
        'ip': ['HCIP_YMSetRootPath', 'HCIP_YMAddIP', 'HCIP_YMAddProcess', 'HCIP_YMOpen', 'HCIP_YMIsOpen', 'HCIP_YMClose'],
        'ex': ['HD_EX_SetPath', 'HD_EX_GetPath', 'HD_EX_Open', 'HD_EX_Close'],
        'basic': ['HD_Basic_GetVersion', 'HD_Basic_GetBuildDate', 'HD_Basic_GetPlatformInfo'],
        'inject': ['HD_Inject_DLL', 'HD_Inject_EjectDLL'],
        'env': ['HD_Env_GetVar', 'HD_Env_SetVar'],
        'mt': ['HD_MT_CreateThread', 'HD_MT_TerminateThread'],
        'hk': ['HD_HK_Function', 'HD_HK_UnhookFunction'],
        'common': ['HD_Common_StringToWString', 'HD_Common_WStringToString'],
        'sh': ['HD_SH_ExecuteShellCode'],
        'yolo': ['HD_YOLO_DetectObjects'],
        'vnc': ['HD_VNC_CreateSession', 'HD_VNC_CloseSession'],
        'win': ['HD_WIN_GetWindowInfo', 'HD_WIN_SendMessage'],
        'vt': ['HD_VT_Query', 'HD_VT_Protect'],
        'lua': ['HD_LUA_ExecuteScript', 'HD_LUA_CallFunction'],
        'normal': ['HD_Normal_Operation'],
        'pp': ['HD_PP_ProcessProtection'],
        'target': ['HD_TARGET_GetInfo', 'HD_TARGET_Set'],
        'nt': ['HD_NT_APICall'],
        'hd': ['HD_Core_Operation'],
        'm': ['HD_Memory_Operation'],
        'fp': ['HD_File_Operation'],
        'fs': ['HD_FS_Operation'],
        'com': ['HD_COM_Operation'],
        'cs': ['HD_CS_Operation'],
        'fi': ['HD_FI_FileInfo'],
        'sc': ['HD_SC_SystemCall'],
        'bs': ['HD_BS_Operation'],
        'mkb': ['HD_MKB_Operation'],
        'rc': ['HD_RC_Operation'],
        'vm': ['HD_VM_Operation'],
        'vmdma': ['HD_VMDMA_Operation'],
        'gb': ['HD_GB_Operation'],
        'ds': ['HD_DS_Operation'],
        'res': ['HD_RES_Operation'],
        'json': ['HD_JSON_Operation'],
        'dw': ['HD_DW_Operation'],
        'sys': ['HD_SYS_Operation'],
        'status': ['HD_STATUS_Operation']
    }

# Python函数名到DLL函数名的映射
def _get_python_to_dll_map():
    """返回Python函数名到DLL函数名的映射"""
    return {
        # Login模块
        'login': 'HCHD_Login',
        'get_last_login_fyi': 'HCHD_GetLastLoginFYI',
        'get_expired_time_stamp': 'HCHD_GetExpiredTimeStamp',
        'get_fyi': 'HCHD_GetFYI',
        'get_open_max_num': 'HCHD_GetOpenMaxNum',
        
        # IP模块
        'ym_set_root_path': 'HCIP_YMSetRootPath',
        'ym_add_ip': 'HCIP_YMAddIP',
        'ym_add_process': 'HCIP_YMAddProcess',
        'ym_open': 'HCIP_YMOpen',
        'ym_is_open': 'HCIP_YMIsOpen',
        'ym_close': 'HCIP_YMClose',
        
        # Basic模块
        'get_version': 'HD_Basic_GetVersion',
        'get_build_date': 'HD_Basic_GetBuildDate',
        'get_platform_info': 'HD_Basic_GetPlatformInfo',
        
        # Inject模块
        'inject_dll': 'HD_Inject_DLL',
        'eject_dll': 'HD_Inject_EjectDLL',
        
        # Env模块
        'get_env_var': 'HD_Env_GetVar',
        'set_env_var': 'HD_Env_SetVar',
        
        # MT模块
        'create_thread': 'HD_MT_CreateThread',
        'terminate_thread': 'HD_MT_TerminateThread',
        
        # HK模块
        'hook_function': 'HD_HK_Function',
        'unhook_function': 'HD_HK_UnhookFunction',
        
        # Common模块
        'string_to_wstring': 'HD_Common_StringToWString',
        'wstring_to_string': 'HD_Common_WStringToString',
        
        # ShellCode模块
        'execute_shell_code': 'HD_SH_ExecuteShellCode',
        
        # Yolo模块
        'detect_objects': 'HD_YOLO_DetectObjects',
        
        # VNC模块
        'create_vnc_session': 'HD_VNC_CreateSession',
        'close_vnc_session': 'HD_VNC_CloseSession',
        
        # Win模块
        'get_window_info': 'HD_WIN_GetWindowInfo',
        'send_message': 'HD_WIN_SendMessage',
        
        # VT模块
        'virtual_query': 'HD_VT_Query',
        'virtual_protect': 'HD_VT_Protect',
        
        # Lua模块
        'execute_lua_script': 'HD_LUA_ExecuteScript',
        'call_lua_function': 'HD_LUA_CallFunction',
        
        # 其他模块
        'normal_operation': 'HD_Normal_Operation',
        'process_protection': 'HD_PP_ProcessProtection',
        'get_target_info': 'HD_TARGET_GetInfo',
        'set_target': 'HD_TARGET_Set',
        'nt_api_call': 'HD_NT_APICall',
        'hd_core_operation': 'HD_Core_Operation',
        'memory_operation': 'HD_Memory_Operation',
        'file_operation': 'HD_File_Operation',
        'file_system_operation': 'HD_FS_Operation',
        'com_operation': 'HD_COM_Operation',
        'cs_operation': 'HD_CS_Operation',
        'file_info': 'HD_FI_FileInfo',
        'system_call': 'HD_SC_SystemCall'
    }

def _ensure_initialized():
    """确保HD GDK已初始化"""
    global _initialized, _global_dll_path, _global_is_debug
    if not _initialized:
        if _global_dll_path:
            HDGDK.init(_global_dll_path, _global_is_debug)
        else:
            # 尝试使用默认路径初始化
            HDGDK.init(None)
        _initialized = True

def _wrap_dll_function(module_name, dll_func_name):
    """包装DLL函数为直接调用的函数"""
    func_key = f"{module_name}_{dll_func_name}"
    
    if func_key not in _wrapped_functions:
        def wrapped_func(*args, **kwargs):
            _ensure_initialized()
            module = getattr(HDGDK, module_name)
            # 尝试直接获取DLL函数
            try:
                dll_func = getattr(module, dll_func_name)
                return dll_func(*args, **kwargs)
            except AttributeError:
                # 如果直接调用DLL函数失败，尝试通过Python函数名调用
                python_to_dll_map = _get_python_to_dll_map()
                # 查找反向映射
                for py_name, dll_name in python_to_dll_map.items():
                    if dll_name == dll_func_name:
                        method = getattr(module, py_name)
                        return method(*args, **kwargs)
                raise AttributeError(f"无法在{module_name}模块中找到函数{dll_func_name}")
        
        # 设置文档字符串
        wrapped_func.__doc__ = f"HD GDK {module_name}模块的DLL函数{dll_func_name}"
        wrapped_func.__name__ = dll_func_name
        wrapped_func.__module__ = __name__
        
        _wrapped_functions[func_key] = wrapped_func
    
    return _wrapped_functions[func_key]

def init_hdgdk(dll_path=None, is_debug=False):
    """
    初始化HD GDK API
    
    Args:
        dll_path (str): DLL文件所在路径
        is_debug (bool): 是否使用调试版DLL
    """
    global _global_dll_path, _global_is_debug, _initialized
    _global_dll_path = dll_path
    _global_is_debug = is_debug
    HDGDK.init(dll_path, is_debug)
    _initialized = True

# 动态生成所有DLL函数的直接调用
def _generate_dll_functions():
    """动态生成所有DLL函数的直接调用"""
    module_dll_functions = _get_module_dll_function_map()
    global_symbols = {}
    
    for module_name, dll_func_names in module_dll_functions.items():
        for dll_func_name in dll_func_names:
            try:
                func = _wrap_dll_function(module_name, dll_func_name)
                global_symbols[dll_func_name] = func
            except Exception as e:
                # 如果无法创建包装函数，记录错误但继续
                pass
    
    return global_symbols

# 生成并导出DLL函数
def _export_dll_functions():
    """导出DLL函数到模块命名空间"""
    import sys
    module_symbols = _generate_dll_functions()
    module = sys.modules[__name__]
    
    for name, func in module_symbols.items():
        setattr(module, name, func)
    
    # 更新模块的__all__列表
    module.__all__ = list(module_symbols.keys()) + ['init_hdgdk', '_get_module_dll_function_map']

# 如果用户需要更灵活地获取函数，可以使用这个函数
def get_dll_function(module_name, dll_func_name):
    """
    获取指定模块的DLL函数
    
    Args:
        module_name (str): 模块名称
        dll_func_name (str): DLL函数名称
    
    Returns:
        function: 包装后的DLL函数
    
    Raises:
        ValueError: 当请求的模块或函数不存在时
    """
    try:
        return _wrap_dll_function(module_name, dll_func_name)
    except Exception as e:
        raise ValueError(f"无法获取DLL函数 '{module_name}.{dll_func_name}': {str(e)}")

# 添加自定义DLL函数映射
def add_custom_dll_function_map(module_name, dll_func_names):
    """
    添加自定义DLL函数映射
    
    Args:
        module_name (str): 模块名称
        dll_func_names (list): DLL函数名称列表
    """
    module_map = _get_module_dll_function_map()
    if module_name in module_map:
        module_map[module_name].extend(dll_func_names)
    else:
        module_map[module_name] = dll_func_names
    
    # 重新生成并导出函数
    _create_all_dll_functions()
    _export_dll_functions()

# 为常用模块的DLL函数创建快捷方式
def _create_common_dll_shortcuts():
    """为常用模块的DLL函数创建快捷方式"""
    import sys
    module = sys.modules[__name__]
    
    # 获取所有模块的DLL函数映射
    module_dll_functions = _get_module_dll_function_map()
    
    # 优先为login模块创建快捷方式
    if 'login' in module_dll_functions:
        for dll_func_name in module_dll_functions['login']:
            try:
                setattr(module, dll_func_name, _wrap_dll_function('login', dll_func_name))
            except:
                pass
    
    # 为ip模块创建快捷方式
    if 'ip' in module_dll_functions:
        for dll_func_name in module_dll_functions['ip']:
            try:
                setattr(module, dll_func_name, _wrap_dll_function('ip', dll_func_name))
            except:
                pass

# 为所有支持的模块DLL函数创建直接调用函数
def _create_all_dll_functions():
    """为所有模块的所有DLL函数创建直接调用函数"""
    import sys
    module = sys.modules[__name__]
    module_dll_functions = _get_module_dll_function_map()
    
    # 存储已创建的函数名，用于检测冲突
    created_functions = set()
    
    # 首先创建常用模块的快捷方式（确保优先性）
    _create_common_dll_shortcuts()
    
    # 为所有模块创建DLL函数
    for module_name, dll_func_names in module_dll_functions.items():
        for dll_func_name in dll_func_names:
            # 检查函数名是否已存在（避免冲突）
            if dll_func_name not in created_functions:
                try:
                    # 创建DLL函数
                    dll_func = _wrap_dll_function(module_name, dll_func_name)
                    setattr(module, dll_func_name, dll_func)
                    created_functions.add(dll_func_name)
                except Exception as e:
                    # 如果创建失败，记录错误但继续
                    pass

# 创建所有模块的DLL函数直接调用
_create_all_dll_functions()

# 在模块加载时生成并导出DLL函数
_export_dll_functions()