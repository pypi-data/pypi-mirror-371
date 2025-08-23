#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HD GDK 虚拟机[VM]模块封装
提供管理VMware系列虚拟机（Workstation/Player）的运行、重启、关闭及状态查询功能
"""

import ctypes
from typing import Optional, List, Tuple, Dict

from .base_module import HDModuleBase, HDModuleFactory


# 虚拟机类型常量
class VM_TYPE:
    """虚拟机类型常量定义"""
    VMWARE_WORKSTATION = 0  # VMware Workstation
    VMWARE_PLAYER = 1       # VMware Player


# 默认常量
DEFAULT_VMWARE_PATH = "D:\\vm16\\"  # 默认VMware安装路径


class HDVM(HDModuleBase):
    """
    HD GDK 虚拟机[VM]模块类
    提供虚拟机的运行、重启、关闭及状态查询功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化VM模块
        
        Args:
            dll_path (str, optional): DLL文件路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
        
    def _initialize_functions(self):
        """
        初始化DLL中的函数
        """
        # 运行虚拟机函数
        self._hcvm_run = self.dll.HCVM_Run
        self._hcvm_run.argtypes = [
            ctypes.c_int32,    # windowsIndex
            ctypes.c_char_p,   # vmPath
            ctypes.c_char_p,   # vmxSysPath
            ctypes.c_bool,     # bGui
            ctypes.c_char_p,   # lparam
            ctypes.c_long,     # vmType
            ctypes.c_long      # type
        ]
        self._hcvm_run.restype = ctypes.c_int64
        
        # 重启虚拟机函数
        self._hcvm_rerun = self.dll.HCVM_Rerun
        self._hcvm_rerun.argtypes = [
            ctypes.c_int32,    # windowsIndex
            ctypes.c_char_p,   # vmPath
            ctypes.c_char_p,   # vmxSysPath
            ctypes.c_bool,     # bForceRoot
            ctypes.c_bool,     # bGui
            ctypes.c_char_p,   # lparam
            ctypes.c_long,     # vmType
            ctypes.c_long      # type
        ]
        self._hcvm_rerun.restype = ctypes.c_int64
        
        # 关闭虚拟机函数
        self._hcvm_close = self.dll.HCVM_Close
        self._hcvm_close.argtypes = [
            ctypes.c_int32,    # windowsIndex
            ctypes.c_char_p,   # vmPath
            ctypes.c_char_p,   # vmxSysPath
            ctypes.c_bool,     # bForceRoot
            ctypes.c_long,     # vmType
            ctypes.c_long      # type
        ]
        self._hcvm_close.restype = ctypes.c_int64
        
        # 查询运行中的虚拟机列表函数
        self._hcvm_list = self.dll.HCVM_List
        self._hcvm_list.argtypes = [ctypes.c_char_p]  # vmPath
        self._hcvm_list.restype = ctypes.c_int64
        
        # 检查虚拟机是否已启动函数
        self._hcvm_is_start = self.dll.HCVM_IsStart
        self._hcvm_is_start.argtypes = [
            ctypes.c_char_p,   # vmPath
            ctypes.c_char_p    # vmxSysPath
        ]
        self._hcvm_is_start.restype = ctypes.c_int64
    
    def run_vm(
        self,
        vmware_path: str,
        vmx_file_path: str,
        window_index: int = 0,
        with_gui: bool = False,
        extra_params: Optional[str] = None,
        vm_type: int = VM_TYPE.VMWARE_WORKSTATION,
        type_param: int = 0
    ) -> int:
        """
        启动指定虚拟机（需管理员权限）
        
        Args:
            vmware_path (str): VMware安装路径（如"D:\\vm16\\"）
            vmx_file_path (str): 虚拟机配置文件（.vmx）路径
            window_index (int, optional): 窗口序号（>0时重置对应窗口的DMA环境）
            with_gui (bool, optional): 是否以GUI界面启动
            extra_params (str, optional): 额外命令参数
            vm_type (int, optional): 虚拟机类型（0：Workstation；1：Player）
            type_param (int, optional): 保留参数
        
        Returns:
            int: 执行结果（0/1表示执行结果，其他为错误码）
        """
        try:
            # 准备参数
            c_vmware_path = ctypes.c_char_p(vmware_path.encode('utf-8'))
            c_vmx_file_path = ctypes.c_char_p(vmx_file_path.encode('utf-8'))
            c_extra_params = ctypes.c_char_p(extra_params.encode('utf-8')) if extra_params else None
            
            # 调用DLL函数
            result = self._hcvm_run(
                window_index,
                c_vmware_path,
                c_vmx_file_path,
                with_gui,
                c_extra_params,
                vm_type,
                type_param
            )
            
            return result
        except Exception as e:
            raise Exception(f"启动虚拟机失败: {str(e)}")
    
    def rerun_vm(
        self,
        vmware_path: str,
        vmx_file_path: str,
        force_restart: bool = True,
        window_index: int = 0,
        with_gui: bool = False,
        extra_params: Optional[str] = None,
        vm_type: int = VM_TYPE.VMWARE_WORKSTATION,
        type_param: int = 0
    ) -> int:
        """
        重启指定虚拟机（需管理员权限）
        
        Args:
            vmware_path (str): VMware安装路径
            vmx_file_path (str): 虚拟机配置文件路径
            force_restart (bool, optional): 是否强制重启（TRUE为断电式重启）
            window_index (int, optional): 窗口序号
            with_gui (bool, optional): 是否以GUI界面启动
            extra_params (str, optional): 额外命令参数
            vm_type (int, optional): 虚拟机类型
            type_param (int, optional): 保留参数
        
        Returns:
            int: 执行结果（0/1表示执行结果，其他为错误码）
        """
        try:
            # 准备参数
            c_vmware_path = ctypes.c_char_p(vmware_path.encode('utf-8'))
            c_vmx_file_path = ctypes.c_char_p(vmx_file_path.encode('utf-8'))
            c_extra_params = ctypes.c_char_p(extra_params.encode('utf-8')) if extra_params else None
            
            # 调用DLL函数
            result = self._hcvm_rerun(
                window_index,
                c_vmware_path,
                c_vmx_file_path,
                force_restart,
                with_gui,
                c_extra_params,
                vm_type,
                type_param
            )
            
            return result
        except Exception as e:
            raise Exception(f"重启虚拟机失败: {str(e)}")
    
    def close_vm(
        self,
        vmware_path: str,
        vmx_file_path: str,
        force_close: bool = True,
        window_index: int = 0,
        vm_type: int = VM_TYPE.VMWARE_WORKSTATION,
        type_param: int = 0
    ) -> int:
        """
        关闭指定虚拟机（需管理员权限）
        
        Args:
            vmware_path (str): VMware安装路径
            vmx_file_path (str): 虚拟机配置文件路径
            force_close (bool, optional): 是否强制关闭（TRUE为强制断电）
            window_index (int, optional): 窗口序号
            vm_type (int, optional): 虚拟机类型
            type_param (int, optional): 保留参数
        
        Returns:
            int: 执行结果（0/1表示执行结果，其他为错误码）
        """
        try:
            # 准备参数
            c_vmware_path = ctypes.c_char_p(vmware_path.encode('utf-8'))
            c_vmx_file_path = ctypes.c_char_p(vmx_file_path.encode('utf-8'))
            
            # 调用DLL函数
            result = self._hcvm_close(
                window_index,
                c_vmware_path,
                c_vmx_file_path,
                force_close,
                vm_type,
                type_param
            )
            
            return result
        except Exception as e:
            raise Exception(f"关闭虚拟机失败: {str(e)}")
    
    def list_vms(self, vmware_path: str) -> List[str]:
        """
        获取当前运行中的所有虚拟机路径
        
        Args:
            vmware_path (str): VMware安装路径
        
        Returns:
            List[str]: 运行中的虚拟机配置文件路径列表
        """
        try:
            # 准备参数
            c_vmware_path = ctypes.c_char_p(vmware_path.encode('utf-8'))
            
            # 调用DLL函数
            result_ptr = self._hcvm_list(c_vmware_path)
            
            # 检查返回值是否有效
            if result_ptr <= 0:
                raise Exception(f"查询虚拟机列表失败，错误码: {result_ptr}")
            
            # 将返回的指针转换为Python字符串
            try:
                vms_str = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode('utf-8')
            except:
                # 尝试使用系统默认编码
                vms_str = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode()
            
            # 解析虚拟机列表（用|分隔）
            vms = vms_str.split('|') if vms_str else []
            
            # 过滤空字符串
            vms = [vm for vm in vms if vm.strip()]
            
            return vms
        except Exception as e:
            # 检查是否返回的是JSON格式错误信息
            if isinstance(e, UnicodeDecodeError) or 'JSON' in str(e):
                # 尝试将结果视为整数错误码
                return []
            raise Exception(f"查询虚拟机列表失败: {str(e)}")
    
    def is_vm_running(self, vmware_path: str, vmx_file_path: str) -> bool:
        """
        检查指定虚拟机是否已启动
        
        Args:
            vmware_path (str): VMware安装路径
            vmx_file_path (str): 虚拟机配置文件路径
        
        Returns:
            bool: True表示已启动，False表示未启动
        """
        try:
            # 准备参数
            c_vmware_path = ctypes.c_char_p(vmware_path.encode('utf-8'))
            c_vmx_file_path = ctypes.c_char_p(vmx_file_path.encode('utf-8'))
            
            # 调用DLL函数
            result = self._hcvm_is_start(c_vmware_path, c_vmx_file_path)
            
            # 1表示已启动，0表示未启动，其他为错误值
            return result == 1
        except Exception as e:
            raise Exception(f"检查虚拟机状态失败: {str(e)}")
    
    def get_vm_type_name(self, vm_type: int) -> str:
        """
        获取虚拟机类型的名称
        
        Args:
            vm_type (int): 虚拟机类型
        
        Returns:
            str: 虚拟机类型名称
        """
        vm_types = {
            VM_TYPE.VMWARE_WORKSTATION: "VMware Workstation",
            VM_TYPE.VMWARE_PLAYER: "VMware Player"
        }
        return vm_types.get(vm_type, f"未知虚拟机类型({vm_type})")
    
    def check_vmware_path(self, vmware_path: str) -> bool:
        """
        检查VMware安装路径是否有效
        
        Args:
            vmware_path (str): VMware安装路径
        
        Returns:
            bool: True表示路径有效，False表示路径无效
        """
        # 确保路径以反斜杠结尾
        if not vmware_path.endswith('\\') and not vmware_path.endswith('/'):
            vmware_path += '\\'
        
        # 检查vmrun.exe是否存在
        vmrun_path = os.path.join(vmware_path, 'vmrun.exe')
        return os.path.exists(vmrun_path)
    
    def check_vmx_file(self, vmx_file_path: str) -> bool:
        """
        检查虚拟机配置文件是否有效
        
        Args:
            vmx_file_path (str): 虚拟机配置文件路径
        
        Returns:
            bool: True表示文件有效，False表示文件无效
        """
        # 检查文件是否存在且扩展名为.vmx
        return os.path.exists(vmx_file_path) and vmx_file_path.lower().endswith('.vmx')


# 工厂函数
def create_hd_vm(dll_path=None, is_debug=None):
    """
    创建虚拟机[VM]模块实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDVM: 虚拟机模块实例
    """
    return HDModuleFactory.create_instance(HDVM, dll_path, is_debug)


# 虚拟机管理辅助函数
def validate_vm_params(
    vmware_path: str,
    vmx_file_path: str
) -> Tuple[bool, str]:
    """
    验证虚拟机参数
    
    Args:
        vmware_path (str): VMware安装路径
        vmx_file_path (str): 虚拟机配置文件路径
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    # 检查VMware路径
    if not vmware_path:
        return False, "VMware安装路径不能为空"
    
    # 检查VMware路径是否存在
    if not os.path.exists(vmware_path):
        return False, f"VMware安装路径不存在: {vmware_path}"
    
    # 检查vmrun.exe是否存在
    vmrun_path = os.path.join(vmware_path, 'vmrun.exe')
    if not os.path.exists(vmrun_path):
        return False, f"在指定路径未找到vmrun.exe: {vmrun_path}"
    
    # 检查虚拟机配置文件
    if not vmx_file_path:
        return False, "虚拟机配置文件路径不能为空"
    
    # 检查虚拟机配置文件是否存在
    if not os.path.exists(vmx_file_path):
        return False, f"虚拟机配置文件不存在: {vmx_file_path}"
    
    # 检查文件扩展名
    if not vmx_file_path.lower().endswith('.vmx'):
        return False, "虚拟机配置文件必须是.vmx文件"
    
    return True, ""