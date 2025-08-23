import ctypes
import os
import sys

# 全局DLL管理器单例
global_dll_manager = None

class HD_DLLManager:
    """
    HD引擎DLL管理器，负责统一加载和管理DLL，避免重复加载
    所有模块通过此管理器获取已加载的DLL实例
    """
    def __init__(self):
        """初始化DLL管理器"""
        self.dll_cache = {}
        self.default_dll = None
        self.default_dll_path = None
        self.default_is_debug = False
        
    def initialize(self, dll_path, is_debug=False):
        """
        初始化并加载DLL
        :param dll_path: DLL文件所在路径
        :param is_debug: 是否使用调试版DLL
        :return: 加载的DLL对象
        :raises FileNotFoundError: 当找不到DLL文件时抛出
        """
        try:
            # 保存默认配置
            self.default_dll_path = dll_path
            self.default_is_debug = is_debug
            
            # 加载默认DLL
            self.default_dll = self.load_dll(dll_path, is_debug)
            return self.default_dll
        except FileNotFoundError:
            # 传递FileNotFoundError异常，让上层处理
            raise
        except Exception as e:
            # 包装其他异常，提供更明确的错误信息
            raise RuntimeError(f"DLL管理器初始化失败: {str(e)}") from e
    
    def load_dll(self, dll_path, is_debug=False):
        """
        加载指定路径的DLL，如果已加载则返回缓存中的实例
        :param dll_path: DLL文件所在路径
        :param is_debug: 是否使用调试版DLL
        :return: 加载的DLL对象
        :raises FileNotFoundError: 当找不到DLL文件时抛出
        """
        # 规范化路径，确保一致性
        normalized_path = os.path.normpath(dll_path)
        
        # 生成缓存键
        cache_key = (normalized_path, is_debug)
        
        # 检查缓存中是否已加载
        if cache_key in self.dll_cache:
            print(f"从缓存加载DLL: {normalized_path}, debug: {is_debug}")
            return self.dll_cache[cache_key]
        
        # 确定要加载的DLL文件名
        dll_names = []
        if is_debug:
            # 优先尝试login模块的调试DLL名称
            dll_names = ['hddebug64.dll', 'hddebug64a.dll', 'hddebug.dll', 'hddebuga.dll', 'HDDebug.dll']
        else:
            # 优先尝试login模块的正式DLL名称
            dll_names = ['hd64.dll', 'hd64a.dll', 'hd.dll', 'hda.dll', 'HD.dll']
        
        # 尝试加载DLL
        loaded_dll = None
        attempted_paths = []
        for dll_name in dll_names:
            full_path = os.path.join(normalized_path, dll_name)
            attempted_paths.append(full_path)
            if os.path.exists(full_path):
                try:
                    loaded_dll = ctypes.WinDLL(full_path)
                    print(f"成功加载DLL: {full_path}")
                    # 将加载的DLL存入缓存
                    self.dll_cache[cache_key] = loaded_dll
                    return loaded_dll
                except Exception as e:
                    print(f"加载DLL失败: {full_path}, 错误: {str(e)}")
                    continue
        
        # 所有DLL都加载失败，抛出异常而不是直接退出
        error_msg = f"无法找到DLL文件，已尝试路径: {', '.join(attempted_paths)}"
        print(error_msg)
        raise FileNotFoundError(error_msg)
    
    def get_dll(self, dll_path=None, is_debug=None):
        """
        获取已加载的DLL实例
        :param dll_path: DLL文件所在路径（默认使用初始化时的路径）
        :param is_debug: 是否使用调试版DLL（默认使用初始化时的设置）
        :return: DLL对象
        """
        # 如果未提供参数，使用默认值
        if dll_path is None:
            dll_path = self.default_dll_path
        if is_debug is None:
            is_debug = self.default_is_debug
        
        # 如果没有默认DLL或者请求的参数与默认不同，尝试加载或返回缓存
        if not self.default_dll or dll_path != self.default_dll_path or is_debug != self.default_is_debug:
            return self.load_dll(dll_path, is_debug)
        
        return self.default_dll

# 获取全局DLL管理器实例
def get_dll_manager():
    """\获取全局DLL管理器实例"""
    global global_dll_manager
    if global_dll_manager is None:
        global_dll_manager = HD_DLLManager()
    return global_dll_manager

# 初始化全局DLL管理器
def init_dll_manager(dll_path, is_debug=False):
    """
    初始化全局DLL管理器（只需要调用一次）
    :param dll_path: DLL文件所在路径
    :param is_debug: 是否使用调试版DLL
    :return: DLL管理器实例
    """
    manager = get_dll_manager()
    manager.initialize(dll_path, is_debug)
    return manager

# 获取已加载的DLL
def get_dll(dll_path=None, is_debug=None):
    """
    获取已加载的DLL实例（简化接口）
    :param dll_path: DLL文件所在路径
    :param is_debug: 是否使用调试版DLL
    :return: DLL对象
    """
    return get_dll_manager().get_dll(dll_path, is_debug)