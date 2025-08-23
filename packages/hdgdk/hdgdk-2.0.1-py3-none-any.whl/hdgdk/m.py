# HD RPG引擎框架(GDK)内存操作模块(M)的Python封装
# 本模块用于学习交流完全合规

import ctypes
from .base_module import HDModuleBase, HDModuleFactory

class HDM(HDModuleBase):
    """
    HD内存操作模块
    提供内存读写、特征码查找、模块信息获取、浮点数转换及汇编执行等功能
    """
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化HDM实例
        
        Args:
            dll_path (str, optional): DLL文件所在路径
            is_debug (bool, optional): 是否使用调试版DLL
        """
        super().__init__(dll_path, is_debug)
        # 存储回调函数引用，防止被Python垃圾回收器回收
        self._callbacks = {}
    
    def _initialize_functions(self):
        """初始化DLL中的函数"""
        # 特征码查找函数
        self.dll.HCM_FindCode = self.dll.HCM_FindCode
        self.dll.HCM_FindCode.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, 
                                         ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
        self.dll.HCM_FindCode.restype = ctypes.c_int64
        
        self.dll.HCM_FindCodeEx = self.dll.HCM_FindCodeEx
        self.dll.HCM_FindCodeEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, 
                                           ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.HCM_FindCodeEx.restype = ctypes.c_int64
        
        # 内存读写（按偏移表达式）- 整数读写
        self.dll.HCM_Read = self.dll.HCM_Read
        self.dll.HCM_Read.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, 
                                     ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_Read.restype = ctypes.c_int64
        
        self.dll.HCM_Write = self.dll.HCM_Write
        self.dll.HCM_Write.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int64, 
                                      ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_Write.restype = ctypes.c_int64
        
        # 内存读写（按偏移表达式）- 字节流读写
        self.dll.HCM_ReadData = self.dll.HCM_ReadData
        self.dll.HCM_ReadData.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.POINTER(ctypes.c_ubyte), 
                                         ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_ReadData.restype = ctypes.c_int64
        
        self.dll.HCM_WriteData = self.dll.HCM_WriteData
        self.dll.HCM_WriteData.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, 
                                          ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_WriteData.restype = ctypes.c_int64
        
        # 内存读写（按偏移表达式）- 浮点数读写
        self.dll.HCM_ReadFD = self.dll.HCM_ReadFD
        self.dll.HCM_ReadFD.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, 
                                       ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_ReadFD.restype = ctypes.c_int64
        
        self.dll.HCM_WriteF = self.dll.HCM_WriteF
        self.dll.HCM_WriteF.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_float, 
                                       ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_WriteF.restype = ctypes.c_int64
        
        self.dll.HCM_WriteD = self.dll.HCM_WriteD
        self.dll.HCM_WriteD.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, 
                                       ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_WriteD.restype = ctypes.c_int64
        
        # 内存读写（按直接地址）
        self.dll.HCM_ReadAddr = self.dll.HCM_ReadAddr
        self.dll.HCM_ReadAddr.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_bool]
        self.dll.HCM_ReadAddr.restype = ctypes.c_int64
        
        self.dll.HCM_WriteAddr = self.dll.HCM_WriteAddr
        self.dll.HCM_WriteAddr.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, 
                                          ctypes.c_int32, ctypes.c_bool]
        self.dll.HCM_WriteAddr.restype = ctypes.c_int64
        
        self.dll.HCM_ReadDataAddr = self.dll.HCM_ReadDataAddr
        self.dll.HCM_ReadDataAddr.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.POINTER(ctypes.c_ubyte), 
                                             ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
        self.dll.HCM_ReadDataAddr.restype = ctypes.c_int64
        
        self.dll.HCM_WriteDataAddr = self.dll.HCM_WriteDataAddr
        self.dll.HCM_WriteDataAddr.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, 
                                              ctypes.c_int32, ctypes.c_bool]
        self.dll.HCM_WriteDataAddr.restype = ctypes.c_int64
        
        self.dll.HCM_ReadFDAddr = self.dll.HCM_ReadFDAddr
        self.dll.HCM_ReadFDAddr.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_bool]
        self.dll.HCM_ReadFDAddr.restype = ctypes.c_int64
        
        self.dll.HCM_WriteAddrF = self.dll.HCM_WriteAddrF
        self.dll.HCM_WriteAddrF.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_float, ctypes.c_bool]
        self.dll.HCM_WriteAddrF.restype = ctypes.c_int64
        
        self.dll.HCM_WriteAddrD = self.dll.HCM_WriteAddrD
        self.dll.HCM_WriteAddrD.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_double, ctypes.c_bool]
        self.dll.HCM_WriteAddrD.restype = ctypes.c_int64
        
        # 模块信息获取
        self.dll.HCM_GetModuleBase = self.dll.HCM_GetModuleBase
        self.dll.HCM_GetModuleBase.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_GetModuleBase.restype = ctypes.c_int64
        
        self.dll.HCM_GetModuleFunAddr = self.dll.HCM_GetModuleFunAddr
        self.dll.HCM_GetModuleFunAddr.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
        self.dll.HCM_GetModuleFunAddr.restype = ctypes.c_int64
        
        # 地址有效性判断
        self.dll.HCM_IsBadReadAddr = self.dll.HCM_IsBadReadAddr
        self.dll.HCM_IsBadReadAddr.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_bool]
        self.dll.HCM_IsBadReadAddr.restype = ctypes.c_int64
        
        # 浮点数转换
        self.dll.HCM_FloatTakeInt = self.dll.HCM_FloatTakeInt
        self.dll.HCM_FloatTakeInt.argtypes = [ctypes.c_float]
        self.dll.HCM_FloatTakeInt.restype = ctypes.c_int64
        
        self.dll.HCM_FloatIntTakeFloat = self.dll.HCM_FloatIntTakeFloat
        self.dll.HCM_FloatIntTakeFloat.argtypes = [ctypes.c_int64]
        self.dll.HCM_FloatIntTakeFloat.restype = ctypes.c_float
        
        self.dll.HCM_DoubleIntTakeDouble = self.dll.HCM_DoubleIntTakeDouble
        self.dll.HCM_DoubleIntTakeDouble.argtypes = [ctypes.c_int64]
        self.dll.HCM_DoubleIntTakeDouble.restype = ctypes.c_double
        
        # 汇编执行
        self.dll.HCM_AsmCallX86 = self.dll.HCM_AsmCallX86
        self.dll.HCM_AsmCallX86.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, 
                                           ctypes.c_bool, ctypes.c_bool]
        self.dll.HCM_AsmCallX86.restype = ctypes.c_int64
        
        self.dll.HCM_AsmCallX64 = self.dll.HCM_AsmCallX64
        self.dll.HCM_AsmCallX64.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, 
                                           ctypes.c_bool, ctypes.c_bool]
        self.dll.HCM_AsmCallX64.restype = ctypes.c_int64
    
    # 特征码查找相关方法
    def find_code(self, window_index, pattern, offset=0, count=1, result_type=1, module_name=None):
        """
        根据特征码在指定模块中查找地址
        
        Args:
            window_index (int): 目标窗口序号（从1开始）
            pattern (str): 特征码字符串，支持"??"模糊匹配
            offset (int): 正负偏移值
            count (int): 查找的第N次结果（从1开始）
            result_type (int): 返回类型（1：地址；2：基地址；3：CALL地址；4：地址中的值）
            module_name (str, optional): 指定模块名，默认主模块
        
        Returns:
            int: 查找结果
        """
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        return self.dll.HCM_FindCode(window_index, pattern.encode('utf-8'), offset, count, result_type, module_name_ptr)
    
    def find_code_ex(self, window_index, start_addr, scan_size, pattern, offset=0, count=1, result_type=1):
        """
        通过指定地址范围查找特征码
        
        Args:
            window_index (int): 目标窗口序号（从1开始）
            start_addr (int): 开始地址
            scan_size (int): 扫描范围大小
            pattern (str): 特征码字符串
            offset (int): 正负偏移值
            count (int): 查找的第N次结果（从1开始）
            result_type (int): 返回类型
        
        Returns:
            int: 查找结果
        """
        return self.dll.HCM_FindCodeEx(window_index, start_addr, scan_size, pattern.encode('utf-8'), offset, count, result_type)
    
    # 内存读写（按偏移表达式）相关方法
    def read(self, window_index, expression, size, module_name=None, is_main_thread=False):
        """
        按偏移表达式读整数数据
        
        Args:
            window_index (int): 目标窗口序号
            expression (str): 偏移表达式
            size (int): 读取大小（1/2/4/8字节）
            module_name (str, optional): 指定模块名
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 读取的整数值
        """
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        return self.dll.HCM_Read(window_index, expression.encode('utf-8'), size, module_name_ptr, is_main_thread)
    
    def write(self, window_index, expression, value, size, module_name=None, is_main_thread=False):
        """
        按偏移表达式写整数数据
        
        Args:
            window_index (int): 目标窗口序号
            expression (str): 偏移表达式（最后需加"]"）
            value (int): 要写入的整数值
            size (int): 写入大小（最大8字节）
            module_name (str, optional): 指定模块名
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 操作结果（0表示失败，其他表示成功）
        """
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        return self.dll.HCM_Write(window_index, expression.encode('utf-8'), value, size, module_name_ptr, is_main_thread)
    
    def read_data(self, window_index, expression, buffer_size, read_size, module_name=None, is_main_thread=False):
        """
        按偏移表达式读字节流
        
        Args:
            window_index (int): 目标窗口序号
            expression (str): 偏移表达式（最后需加"]"）
            buffer_size (int): 缓冲区大小
            read_size (int): 读取大小（最大100KB）
            module_name (str, optional): 指定模块名
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            tuple: (操作结果, 读取的字节流)
        """
        buffer = (ctypes.c_ubyte * buffer_size)()
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        result = self.dll.HCM_ReadData(window_index, expression.encode('utf-8'), buffer, buffer_size, read_size, module_name_ptr, is_main_thread)
        
        # 提取实际读取的字节流
        if result > 0:
            actual_read_size = min(read_size, buffer_size)
            data = bytes(buffer[:actual_read_size])
        else:
            data = bytes()
            
        return result, data
    
    def write_data(self, window_index, expression, data, module_name=None, is_main_thread=False):
        """
        按偏移表达式写字节流
        
        Args:
            window_index (int): 目标窗口序号
            expression (str): 偏移表达式（最后需加"]"）
            data (bytes): 要写入的字节流（最大100KB）
            module_name (str, optional): 指定模块名
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 操作结果
        """
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        return self.dll.HCM_WriteData(window_index, expression.encode('utf-8'), data, len(data), module_name_ptr, is_main_thread)
    
    def read_float(self, window_index, expression, is_double=False, module_name=None, is_main_thread=False):
        """
        按偏移表达式读浮点数
        
        Args:
            window_index (int): 目标窗口序号
            expression (str): 偏移表达式（最后需加"]"）
            is_double (bool): 是否为双浮点数
            module_name (str, optional): 指定模块名
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            float: 读取的浮点数值
        """
        size = 8 if is_double else 4
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        result = self.dll.HCM_ReadFD(window_index, expression.encode('utf-8'), size, module_name_ptr, is_main_thread)
        
        # 转换结果为浮点数
        if is_double:
            return ctypes.c_double.from_buffer(ctypes.create_string_buffer(result.to_bytes(8, byteorder='little'))).value
        else:
            return ctypes.c_float.from_buffer(ctypes.create_string_buffer(result.to_bytes(4, byteorder='little'))).value
    
    def write_float(self, window_index, expression, value, is_double=False, module_name=None, is_main_thread=False):
        """
        按偏移表达式写浮点数
        
        Args:
            window_index (int): 目标窗口序号
            expression (str): 偏移表达式（最后需加"]"）
            value (float): 要写入的浮点数值
            is_double (bool): 是否为双浮点数
            module_name (str, optional): 指定模块名
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 操作结果
        """
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        
        if is_double:
            return self.dll.HCM_WriteD(window_index, expression.encode('utf-8'), value, module_name_ptr, is_main_thread)
        else:
            return self.dll.HCM_WriteF(window_index, expression.encode('utf-8'), value, module_name_ptr, is_main_thread)
    
    # 内存读写（按直接地址）相关方法
    def read_addr(self, window_index, address, size, is_main_thread=False):
        """
        按直接地址读整数
        
        Args:
            window_index (int): 目标窗口序号
            address (int): 内存地址
            size (int): 读取大小
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 读取的整数值
        """
        return self.dll.HCM_ReadAddr(window_index, address, size, is_main_thread)
    
    def write_addr(self, window_index, address, value, size, is_main_thread=False):
        """
        按直接地址写整数
        
        Args:
            window_index (int): 目标窗口序号
            address (int): 内存地址
            value (int): 要写入的整数值
            size (int): 写入大小
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCM_WriteAddr(window_index, address, value, size, is_main_thread)
    
    def read_data_addr(self, window_index, address, buffer_size, read_size, is_main_thread=False):
        """
        按直接地址读字节流
        
        Args:
            window_index (int): 目标窗口序号
            address (int): 内存地址
            buffer_size (int): 缓冲区大小
            read_size (int): 读取大小
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            tuple: (操作结果, 读取的字节流)
        """
        buffer = (ctypes.c_ubyte * buffer_size)()
        result = self.dll.HCM_ReadDataAddr(window_index, address, buffer, buffer_size, read_size, is_main_thread)
        
        if result > 0:
            actual_read_size = min(read_size, buffer_size)
            data = bytes(buffer[:actual_read_size])
        else:
            data = bytes()
            
        return result, data
    
    def write_data_addr(self, window_index, address, data, is_main_thread=False):
        """
        按直接地址写字节流
        
        Args:
            window_index (int): 目标窗口序号
            address (int): 内存地址
            data (bytes): 要写入的字节流
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 操作结果
        """
        return self.dll.HCM_WriteDataAddr(window_index, address, data, len(data), is_main_thread)
    
    def read_float_addr(self, window_index, address, is_double=False, is_main_thread=False):
        """
        按直接地址读浮点数
        
        Args:
            window_index (int): 目标窗口序号
            address (int): 内存地址
            is_double (bool): 是否为双浮点数
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            float: 读取的浮点数值
        """
        size = 8 if is_double else 4
        result = self.dll.HCM_ReadFDAddr(window_index, address, size, is_main_thread)
        
        if is_double:
            return ctypes.c_double.from_buffer(ctypes.create_string_buffer(result.to_bytes(8, byteorder='little'))).value
        else:
            return ctypes.c_float.from_buffer(ctypes.create_string_buffer(result.to_bytes(4, byteorder='little'))).value
    
    def write_float_addr(self, window_index, address, value, is_double=False, is_main_thread=False):
        """
        按直接地址写浮点数
        
        Args:
            window_index (int): 目标窗口序号
            address (int): 内存地址
            value (float): 要写入的浮点数值
            is_double (bool): 是否为双浮点数
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 操作结果
        """
        if is_double:
            return self.dll.HCM_WriteAddrD(window_index, address, value, is_main_thread)
        else:
            return self.dll.HCM_WriteAddrF(window_index, address, value, is_main_thread)
    
    # 模块信息获取相关方法
    def get_module_base(self, window_index, module_name=None, is_main_thread=False):
        """
        获取模块基地址
        
        Args:
            window_index (int): 目标窗口序号
            module_name (str, optional): 模块名，默认主模块
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 模块基地址
        """
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        return self.dll.HCM_GetModuleBase(window_index, module_name_ptr, is_main_thread)
    
    def get_module_fun_addr(self, window_index, module_name=None, function_name=None, is_main_thread=False):
        """
        获取模块导出函数地址
        
        Args:
            window_index (int): 目标窗口序号
            module_name (str, optional): 模块名
            function_name (str, optional): 函数名
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 函数地址
        """
        module_name_ptr = ctypes.c_char_p(module_name.encode('utf-8')) if module_name else None
        function_name_ptr = ctypes.c_char_p(function_name.encode('utf-8')) if function_name else None
        return self.dll.HCM_GetModuleFunAddr(window_index, module_name_ptr, function_name_ptr, is_main_thread)
    
    # 地址有效性判断相关方法
    def is_bad_read_addr(self, window_index, address, size, is_main_thread=False):
        """
        判断地址是否有效可读
        
        Args:
            window_index (int): 目标窗口序号
            address (int): 内存地址
            size (int): 检查大小（32位一般4字节，64位一般8字节）
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 0表示地址有效，非0表示无效
        """
        return self.dll.HCM_IsBadReadAddr(window_index, address, size, is_main_thread)
    
    # 浮点数转换相关方法
    def float_to_int(self, value):
        """
        浮点数转整数形式（如1.0→0x3F800000）
        
        Args:
            value (float): 浮点数
        
        Returns:
            int: 整数形式的浮点数
        """
        return self.dll.HCM_FloatTakeInt(value)
    
    def int_to_float(self, int_value):
        """
        整数形式浮点数转浮点数（如0x3F800000→1.0）
        
        Args:
            int_value (int): 整数形式的浮点数
        
        Returns:
            float: 浮点数
        """
        return self.dll.HCM_FloatIntTakeFloat(int_value)
    
    def int_to_double(self, int_value):
        """
        长整数形式双浮点数转双浮点数（如0x3FF0000000000000→1.0）
        
        Args:
            int_value (int): 长整数形式的双浮点数
        
        Returns:
            float: 双浮点数
        """
        return self.dll.HCM_DoubleIntTakeDouble(int_value)
    
    # 汇编执行相关方法
    def asm_call_x86(self, window_index, execute_addr=0, asm_text=None, free_addr=False, is_main_thread=False):
        """
        执行X86汇编
        
        Args:
            window_index (int): 目标窗口序号
            execute_addr (int): 执行地址（0表示在目标进程申请内存执行）
            asm_text (str): 汇编文本
            free_addr (bool): 是否释放申请的内存
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 执行结果（execute_addr=0时返回格式：地址|返回值）
        """
        asm_text_ptr = ctypes.c_char_p(asm_text.encode('utf-8')) if asm_text else None
        return self.dll.HCM_AsmCallX86(window_index, execute_addr, asm_text_ptr, free_addr, is_main_thread)
    
    def asm_call_x64(self, window_index, execute_addr=0, asm_text=None, free_addr=False, is_main_thread=False):
        """
        执行X64汇编
        
        Args:
            window_index (int): 目标窗口序号
            execute_addr (int): 执行地址（0表示在目标进程申请内存执行）
            asm_text (str): 汇编文本
            free_addr (bool): 是否释放申请的内存
            is_main_thread (bool): 是否主线程调用
        
        Returns:
            int: 执行结果（execute_addr=0时返回格式：地址|返回值）
        """
        asm_text_ptr = ctypes.c_char_p(asm_text.encode('utf-8')) if asm_text else None
        return self.dll.HCM_AsmCallX64(window_index, execute_addr, asm_text_ptr, free_addr, is_main_thread)

# 工厂函数
def create_m(dll_path=None, is_debug=False):
    """
    创建HDM实例的工厂函数
    
    Args:
        dll_path (str, optional): DLL文件所在路径
        is_debug (bool, optional): 是否使用调试版DLL
    
    Returns:
        HDM: HDM实例
    """
    return HDModuleFactory.create_instance(HDM, dll_path, is_debug)