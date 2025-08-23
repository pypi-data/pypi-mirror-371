"""
HD RPG引擎框架(GDK)YOLOV(HDYOLOV)模块封装

该模块支持ncnn模型，兼容yolov5、8、10、11版本，可运行于CPU和GPU
使用前需调用HCHD_LoadDrv2并传递参数4来安装YOLOV组件模块
"""
from ctypes import c_int64, c_int32, c_void_p, c_float, c_char_p, byref, POINTER
from .base_module import HDModuleBase
from .dll_manager import DLLManager


class HDYOLO(HDModuleBase):
    """YOLOV模块封装类"""
    
    def __init__(self, dll_path=None, is_debug=None):
        """
        初始化YOLOV模块
        
        Args:
            dll_path: DLL文件所在路径
            is_debug: 是否使用调试版本的DLL
        """
        super().__init__(dll_path, is_debug)
        self._bind_functions()
        
    def _initialize_functions(self):
        """初始化DLL中的函数"""
        self._bind_functions()
        
    def _bind_functions(self):
        """绑定DLL函数"""
        # 从内存中加载YOLOV模型
        try:
            self._add_model = getattr(self.dll, "HCYOLO_AddModel")
            self._add_model.argtypes = [c_int32, c_void_p, c_int32, c_void_p, c_int32, c_int32, c_int32, c_char_p]
            self._add_model.restype = c_int64
        except AttributeError:
            self._add_model = None
        
        # 从文件中加载YOLOV模型
        try:
            self._add_model_file = getattr(self.dll, "HCYOLO_AddModelFile")
            self._add_model_file.argtypes = [c_int32, c_char_p, c_char_p, c_int32, c_int32, c_char_p]
            self._add_model_file.restype = c_int64
        except AttributeError:
            self._add_model_file = None
        
        # 从后台截图缓存识别目标
        try:
            self._identify = getattr(self.dll, "HCYOLO_Identify")
            self._identify.argtypes = [c_int32, c_float, c_float, c_int32]
            self._identify.restype = c_int64
        except AttributeError:
            self._identify = None
        
        # 从指定图片文件识别目标
        try:
            self._identify_by_file = getattr(self.dll, "HCYOLO_IdentifyByFile")
            self._identify_by_file.argtypes = [c_int32, c_char_p, c_float, c_float, c_int32]
            self._identify_by_file.restype = c_int64
        except AttributeError:
            self._identify_by_file = None
        
        # 从指定图片内存数据识别目标
        try:
            self._identify_by_mem = getattr(self.dll, "HCYOLO_IdentifyByMem")
            self._identify_by_mem.argtypes = [c_int32, c_void_p, c_int32, c_float, c_float, c_int32]
            self._identify_by_mem.restype = c_int64
        except AttributeError:
            self._identify_by_mem = None
    
    def add_model(self, ver, mode_data, mode_data_size, mode_lparam, mode_lparam_size, size=640, use_gpu=False, password=None):
        """
        从内存中加载YOLOV（ncnn.bin和ncnn.param）模型文件
        
        Args:
            ver: yolov版本（支持5、8、10、11）
            mode_data: ncnn.bin模型文件的二进制数据
            mode_data_size: ncnn.bin模型文件的二进制数据大小
            mode_lparam: ncnn.param模型文件的二进制数据
            mode_lparam_size: ncnn.param模型文件的二进制数据大小
            size: 训练时的图片大小（默认640）
            use_gpu: 是否使用GPU识别（默认False）
            password: 密码（默认None；调试版本无法使用，需用原始模型；发布版本可使用加密模型）
            
        Returns:
            int: 操作结果，参考HD返回值表
            
        Notes:
            - 一个进程仅同时支持一个版本的模型
            - 使用前需调用HCHD_LoadDrv2并传递参数4来安装YOLOV组件模块
        """
        if not isinstance(mode_data, bytes):
            raise TypeError("mode_data must be bytes")
        if not isinstance(mode_lparam, bytes):
            raise TypeError("mode_lparam must be bytes")
        
        password_ptr = c_char_p(password.encode('utf-8')) if password else None
        
        return self._add_model(
            ver, 
            mode_data, 
            mode_data_size, 
            mode_lparam, 
            mode_lparam_size, 
            size, 
            1 if use_gpu else 0, 
            password_ptr
        )
    
    def add_model_file(self, ver, model_file_name, model_param_name, size=640, use_gpu=False, password=None):
        """
        从文件中加载YOLOV（ncnn.bin和ncnn.param）模型文件
        
        Args:
            ver: yolov版本（支持5、8、10、11）
            model_file_name: ncnn.bin模型文件名（支持绝对路径或相对路径）
            model_param_name: ncnn.param模型文件名（支持绝对路径或相对路径）
            size: 训练时的图片大小（默认640）
            use_gpu: 是否使用GPU识别（默认False）
            password: 密码（默认None；调试版本无法使用，需用原始模型；发布版本可使用加密模型）
            
        Returns:
            int: 操作结果，参考HD返回值表
            
        Notes:
            - 一个进程仅同时支持一个版本的模型
            - 使用前需调用HCHD_LoadDrv2并传递参数4来安装YOLOV组件模块
            - 相对路径需调用HCRES_SetResPath设置路径
        """
        password_ptr = c_char_p(password.encode('utf-8')) if password else None
        
        return self._add_model_file(
            ver, 
            model_file_name.encode('utf-8'), 
            model_param_name.encode('utf-8'), 
            size, 
            1 if use_gpu else 0, 
            password_ptr
        )
    
    def identify(self, window_index, conf=0.7, iou=0.4, debug=False):
        """
        从后台截图缓存识别目标
        
        Args:
            window_index: 窗口序号（从1开始）
            conf: 置信度（默认0.7）
            iou: 交并比（默认0.4，一般在0.4~0.6之间）
            debug: 是否弹窗调试标注查看（默认False）
            
        Returns:
            int: 操作结果，参考HD返回值表
            
        Notes:
            - 识别信息需调用HCEnv_GetRetJson获取，字符串以"|"分割，格式为"类别,X1,Y1,X2,Y2,置信度,耗时|..."
            - 需安装YOLOV组件模块
        """
        return self._identify(window_index, conf, iou, 1 if debug else 0)
    
    def identify_by_file(self, window_index, image_path, conf=0.7, iou=0.4, debug=False):
        """
        从指定图片文件识别目标
        
        Args:
            window_index: 窗口序号（从1开始）
            image_path: 图片文件名（支持绝对路径或相对路径，支持png、jpg、bmp等格式）
            conf: 置信度（默认0.7）
            iou: 交并比（默认0.4）
            debug: 是否弹窗调试标注查看（默认False）
            
        Returns:
            int: 操作结果，参考HD返回值表
            
        Notes:
            - 识别信息格式同HCYOLO_Identify
            - 需安装YOLOV组件模块
            - 相对路径需调用HCRES_SetResPath设置路径
        """
        return self._identify_by_file(
            window_index, 
            image_path.encode('utf-8'), 
            conf, 
            iou, 
            1 if debug else 0
        )
    
    def identify_by_mem(self, window_index, img_data, img_data_size, conf=0.7, iou=0.4, debug=False):
        """
        从指定图片内存数据识别目标
        
        Args:
            window_index: 窗口序号（从1开始）
            img_data: 图片文件二进制数据（支持png、jpg、bmp等格式）
            img_data_size: 图片文件二进制数据大小
            conf: 置信度（默认0.7）
            iou: 交并比（默认0.4）
            debug: 是否弹窗调试标注查看（默认False）
            
        Returns:
            int: 操作结果，参考HD返回值表
            
        Notes:
            - 识别信息格式同HCYOLO_Identify
            - 需安装YOLOV组件模块
        """
        if not isinstance(img_data, bytes):
            raise TypeError("img_data must be bytes")
        
        return self._identify_by_mem(
            window_index, 
            img_data, 
            img_data_size, 
            conf, 
            iou, 
            1 if debug else 0
        )


# 工厂函数
def create_yolo(dll_path=None, is_debug=None) -> HDYOLO:
    """
    创建YOLOV模块实例
    
    Args:
        dll_path: DLL文件所在路径
        is_debug: 是否使用调试版本的DLL
        
    Returns:
        HDYOLO: YOLOV模块实例
    """
    return HDYOLO(dll_path, is_debug)