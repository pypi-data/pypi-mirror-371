#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 主板机模块(SC)封装
提供管理HDScrcpy投屏软件与设备的连接功能，基于adb服务实现设备投屏、通讯及控制
"""

import ctypes
from typing import Optional, List, Tuple, Dict

from .base_module import HDModuleBase, HDModuleFactory


# 设备类型常量
class DEVICE_TYPE:
    """设备类型常量定义"""
    EMULATOR = 1  # 模拟器 (-s)
    USB_DEVICE = 2  # USB设备 (-d)
    NETWORK_DEVICE = 3  # 网络设备 (-e)


# 默认常量
DEFAULT_SCRCPY_PATH = "C:\\hdscrcpy2.7\\"  # 默认投屏软件路径
DEFAULT_TIMEOUT = 10000  # 默认连接超时时间(毫秒)


class HDSC(HDModuleBase):
    """
    HD GDK 主板机模块(SC)类
    提供设备管理与投屏功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化SC模块
        
        Args:
            dll_path (str, optional): DLL文件路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 设置投屏软件路径函数
        self._hcsc_set_path = self.dll.HCSC_SetPath
        self._hcsc_set_path.argtypes = [ctypes.c_char_p]
        self._hcsc_set_path.restype = ctypes.c_int64
        
        # 重置adb服务函数
        self._hcsc_reset_adb = self.dll.HCSC_ResetAdb
        self._hcsc_reset_adb.argtypes = [ctypes.c_char_p]
        self._hcsc_reset_adb.restype = ctypes.c_int64
        
        # 查询可用设备函数
        self._hcsc_query_devices = self.dll.HCSC_QueryDevices
        self._hcsc_query_devices.argtypes = []
        self._hcsc_query_devices.restype = ctypes.c_int64
        
        # 连接设备并初始化通讯函数
        self._hcsc_connect_devices = self.dll.HCSC_ConnectDevices
        self._hcsc_connect_devices.argtypes = [
            ctypes.c_int32,  # winIndex
            ctypes.c_char_p,  # devicesName
            ctypes.c_char_p,  # cmdLparam
            ctypes.c_int32,  # type
            ctypes.c_int32,  # w
            ctypes.c_int32,  # h
            ctypes.c_int32   # timeOut
        ]
        self._hcsc_connect_devices.restype = ctypes.c_int64
    
    def set_scrcpy_path(self, root_path: str) -> int:
        """
        设置HDScrcpy投屏软件根目录，并重启adb服务（重置adb环境）
        
        Args:
            root_path (str): HDScrcpy根目录（包含hdscrcpy.exe、adb.exe的目录）
        
        Returns:
            int: 操作结果，参考HD返回值表
        """
        try:
            # 将Python字符串转换为C字符串
            c_root_path = ctypes.c_char_p(root_path.encode('utf-8'))
            
            # 调用DLL函数
            result = self._hcsc_set_path(c_root_path)
            return result
        except Exception as e:
            raise Exception(f"设置投屏软件路径失败: {str(e)}")
    
    def reset_adb(self, ip_info: Optional[str] = None) -> int:
        """
        重置adb服务，可同时连接指定IP端口的设备
        
        Args:
            ip_info (str, optional): IP端口信息（格式`IP:端口|IP:端口|...`），为None时仅重启adb
        
        Returns:
            int: 
                - 若ip_info为None：返回adb重启是否成功（JSON格式）
                - 若ip_info有效：返回成功连接的设备数量（0表示连接失败或重启失败，JSON格式）
        """
        try:
            # 准备IP信息参数
            c_ip_info = ctypes.c_char_p(ip_info.encode('utf-8')) if ip_info else None
            
            # 调用DLL函数
            result = self._hcsc_reset_adb(c_ip_info)
            return result
        except Exception as e:
            raise Exception(f"重置adb服务失败: {str(e)}")
    
    def query_devices(self) -> List[str]:
        """
        查询当前所有可用的设备（模拟器、手机等）
        
        Returns:
            List[str]: 设备名列表
        """
        try:
            # 调用DLL函数
            result_ptr = self._hcsc_query_devices()
            
            # 检查返回值是否有效
            if result_ptr <= 0:
                raise Exception(f"查询设备失败，错误码: {result_ptr}")
            
            # 将返回的指针转换为Python字符串
            try:
                devices_str = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode('utf-8')
            except:
                # 尝试使用系统默认编码
                devices_str = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode()
            
            # 解析设备列表（用|分隔）
            devices = devices_str.split('|') if devices_str else []
            
            # 过滤空字符串
            devices = [device for device in devices if device.strip()]
            
            return devices
        except Exception as e:
            # 检查是否返回的是JSON格式错误信息
            if isinstance(e, UnicodeDecodeError) or 'JSON' in str(e):
                # 尝试将结果视为整数错误码
                return []
            raise Exception(f"查询设备失败: {str(e)}")
    
    def connect_device(
        self,
        window_index: int,
        device_name: str,
        device_type: int,
        width: int = 800,
        height: int = 450,
        timeout: int = DEFAULT_TIMEOUT,
        extra_cmd: Optional[str] = None
    ) -> int:
        """
        连接指定设备并初始化通讯窗口（需先调用HCHD_Login和HCEnv_Init/HCEnv_InitEx）
        
        Args:
            window_index (int): 窗口序号
            device_name (str): 设备号（如emulator-5554、01aa8320032fe731）
            device_type (int): 设备类型（1：模拟器；2：USB设备；3：网络设备）
            width (int, optional): 投屏窗口宽度，默认800
            height (int, optional): 投屏窗口高度，默认450
            timeout (int, optional): 连接超时时间（毫秒），默认10000
            extra_cmd (str, optional): 额外命令参数（参考hdscrcpy命令行）
        
        Returns:
            int: 成功返回打开的窗口PID，失败返回错误码
        """
        try:
            # 检查设备类型是否有效
            if device_type not in [DEVICE_TYPE.EMULATOR, DEVICE_TYPE.USB_DEVICE, DEVICE_TYPE.NETWORK_DEVICE]:
                raise ValueError(f"无效的设备类型: {device_type}，有效值为1(模拟器)、2(USB设备)、3(网络设备)")
            
            # 准备参数
            c_device_name = ctypes.c_char_p(device_name.encode('utf-8'))
            c_extra_cmd = ctypes.c_char_p(extra_cmd.encode('utf-8')) if extra_cmd else ctypes.c_char_p(b"")
            
            # 调用DLL函数
            result = self._hcsc_connect_devices(
                window_index,
                c_device_name,
                c_extra_cmd,
                device_type,
                width,
                height,
                timeout
            )
            
            return result
        except Exception as e:
            raise Exception(f"连接设备失败: {str(e)}")
    
    def get_device_type_name(self, device_type: int) -> str:
        """
        获取设备类型的名称
        
        Args:
            device_type (int): 设备类型
        
        Returns:
            str: 设备类型名称
        """
        device_types = {
            DEVICE_TYPE.EMULATOR: "模拟器",
            DEVICE_TYPE.USB_DEVICE: "USB设备",
            DEVICE_TYPE.NETWORK_DEVICE: "网络设备"
        }
        return device_types.get(device_type, f"未知设备类型({device_type})")
    
    def parse_ip_info(self, ip_info: str) -> List[Tuple[str, int]]:
        """
        解析IP端口信息字符串为IP和端口的列表
        
        Args:
            ip_info (str): IP端口信息字符串（格式`IP:端口|IP:端口|...`）
        
        Returns:
            List[Tuple[str, int]]: IP和端口的列表
        """
        result = []
        if not ip_info:
            return result
        
        # 分割IP端口信息
        ip_port_pairs = ip_info.split('|')
        
        for pair in ip_port_pairs:
            if ':' in pair:
                try:
                    ip, port_str = pair.split(':', 1)
                    port = int(port_str)
                    result.append((ip.strip(), port))
                except ValueError:
                    # 忽略格式错误的IP端口对
                    continue
        
        return result
    
    def build_cmd_param(self, **kwargs) -> str:
        """
        根据传入的参数构建hdscrcpy命令行参数
        
        Args:
            **kwargs: 命令行参数键值对
        
        Returns:
            str: 构建的命令行参数字符串
        """
        cmd_params = []
        
        for key, value in kwargs.items():
            # 将下划线转换为连字符
            param_name = key.replace('_', '-')
            
            # 构建参数
            if isinstance(value, bool):
                # 布尔类型参数（如--no-control）
                if value:
                    cmd_params.append(f"--{param_name}")
            else:
                # 值类型参数（如--max-fps 15）
                cmd_params.append(f"--{param_name}={value}")
        
        return ' '.join(cmd_params)


# 工厂函数
def create_hd_sc(dll_path=None, is_debug=None):
    """
    创建主板机模块(SC)实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDSC: 主板机模块实例
    """
    return HDModuleFactory.create_instance(HDSC, dll_path, is_debug)


# 常用的hdscrcpy命令行参数辅助函数
def get_common_scrcpy_params(
    max_fps: Optional[int] = None,
    bit_rate: Optional[str] = None,
    window_width: Optional[int] = None,
    window_height: Optional[int] = None,
    crop: Optional[str] = None,
    lock_video_orientation: Optional[int] = None,
    no_control: bool = False
) -> str:
    """
    获取常用的hdscrcpy命令行参数
    
    Args:
        max_fps (int, optional): 最大帧率
        bit_rate (str, optional): 比特率（如"2M"）
        window_width (int, optional): 窗口宽度
        window_height (int, optional): 窗口高度
        crop (str, optional): 裁剪区域（格式"宽:高:偏移x:偏移y"）
        lock_video_orientation (int, optional): 锁定视频方向（0-3）
        no_control (bool, optional): 禁用设备控制
    
    Returns:
        str: 命令行参数字符串
    """
    params = []
    
    if max_fps is not None:
        params.append(f"--max-fps {max_fps}")
    
    if bit_rate is not None:
        params.append(f"--bit-rate {bit_rate}")
    
    if window_width is not None:
        params.append(f"--window-width={window_width}")
    
    if window_height is not None:
        params.append(f"--window-height={window_height}")
    
    if crop is not None:
        params.append(f"--crop {crop}")
    
    if lock_video_orientation is not None:
        params.append(f"--lock-video-orientation={lock_video_orientation}")
    
    if no_control:
        params.append("--no-control")
    
    return ' '.join(params)


# 设备连接辅助函数
def detect_device_type(device_name: str) -> int:
    """
    根据设备名自动检测设备类型
    
    Args:
        device_name (str): 设备名
    
    Returns:
        int: 设备类型（1-3）
    """
    device_name = device_name.lower()
    
    # 检查是否为模拟器
    if device_name.startswith('emulator-') or 'mumu' in device_name or 'leidian' in device_name:
        return DEVICE_TYPE.EMULATOR
    
    # 检查是否为网络设备（包含IP地址格式）
    if ':' in device_name and any(char.isdigit() for char in device_name):
        parts = device_name.split(':')
        if len(parts) == 2 and parts[0].replace('.', '').isdigit() and parts[1].isdigit():
            return DEVICE_TYPE.NETWORK_DEVICE
    
    # 默认认为是USB设备
    return DEVICE_TYPE.USB_DEVICE