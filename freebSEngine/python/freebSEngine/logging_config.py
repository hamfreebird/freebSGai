"""
freebSEngine 日志配置模块

提供统一的日志记录配置，支持：
1. 控制台输出
2. 文件日志
3. 日志级别控制
4. 结构化日志格式
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# 默认日志配置
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 结构化日志格式（JSON）
JSON_LOG_FORMAT = {
    "timestamp": "%(asctime)s",
    "name": "%(name)s",
    "level": "%(levelname)s",
    "message": "%(message)s",
    "module": "%(module)s",
    "function": "%(funcName)s",
    "line": "%(lineno)d",
}


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def __init__(self, fmt_dict: Optional[Dict[str, str]] = None, datefmt: Optional[str] = None):
        super().__init__(datefmt=datefmt)
        self.fmt_dict = fmt_dict or JSON_LOG_FORMAT
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为结构化字符串"""
        record_dict = {}
        for key, fmt in self.fmt_dict.items():
            if hasattr(record, key):
                record_dict[key] = getattr(record, key)
            else:
                record_dict[key] = fmt % record.__dict__
        
        # 添加额外字段
        record_dict["timestamp"] = self.formatTime(record)
        
        # 转换为字符串
        import json
        return json.dumps(record_dict, ensure_ascii=False)


def setup_logging(
    log_level: int = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = None,
    console_output: bool = True,
    structured: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    设置日志记录配置
    
    Args:
        log_level: 日志级别 (logging.DEBUG, logging.INFO, etc.)
        log_file: 日志文件路径，如果为 None 则不记录到文件
        console_output: 是否输出到控制台
        structured: 是否使用结构化日志格式
        max_bytes: 日志文件最大大小（字节）
        backup_count: 备份文件数量
    
    Returns:
        配置好的根日志记录器
    """
    # 获取根日志记录器
    logger = logging.getLogger("freebSEngine")
    logger.setLevel(log_level)
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 创建格式化器
    if structured:
        formatter = StructuredFormatter(datefmt=DEFAULT_DATE_FORMAT)
    else:
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用 RotatingFileHandler 进行日志轮转
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 添加过滤器以添加额外上下文
    class ContextFilter(logging.Filter):
        """添加上下文信息的过滤器"""
        
        def filter(self, record: logging.LogRecord) -> bool:
            # 添加进程ID和线程ID
            record.process_id = os.getpid()
            record.thread_id = getattr(record, "thread", 0)
            
            # 添加时间戳
            record.timestamp_iso = datetime.now().isoformat()
            
            return True
    
    logger.addFilter(ContextFilter())
    
    return logger


def get_logger(name: str = "freebSEngine") -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        配置好的日志记录器
    """
    # 如果根日志记录器尚未配置，使用默认配置
    root_logger = logging.getLogger("freebSEngine")
    if not root_logger.handlers:
        setup_logging()
    
    # 返回指定名称的子日志记录器
    return logging.getLogger(name)


def configure_from_env() -> logging.Logger:
    """
    从环境变量配置日志
    
    环境变量:
        FREEBSE_LOG_LEVEL: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        FREEBSE_LOG_FILE: 日志文件路径
        FREEBSE_LOG_CONSOLE: 是否输出到控制台 (true/false)
        FREEBSE_LOG_STRUCTURED: 是否使用结构化日志 (true/false)
    
    Returns:
        配置好的日志记录器
    """
    # 解析日志级别
    log_level_str = os.getenv("FREEBSE_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, DEFAULT_LOG_LEVEL)
    
    # 解析其他参数
    log_file = os.getenv("FREEBSE_LOG_FILE")
    console_output = os.getenv("FREEBSE_LOG_CONSOLE", "true").lower() == "true"
    structured = os.getenv("FREEBSE_LOG_STRUCTURED", "false").lower() == "true"
    
    return setup_logging(
        log_level=log_level,
        log_file=log_file,
        console_output=console_output,
        structured=structured,
    )


def log_performance(
    operation: str,
    duration: float,
    details: Optional[Dict[str, Any]] = None,
    level: int = logging.INFO,
):
    """
    记录性能指标
    
    Args:
        operation: 操作名称
        duration: 持续时间（秒）
        details: 额外详细信息
        level: 日志级别
    """
    logger = get_logger("freebSEngine.performance")
    
    message = f"性能指标 - {operation}: {duration:.6f} 秒"
    if details:
        details_str = ", ".join(f"{k}={v}" for k, v in details.items())
        message += f" [{details_str}]"
    
    logger.log(level, message)


def log_error_with_context(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    operation: Optional[str] = None,
):
    """
    记录错误及其上下文信息
    
    Args:
        error: 异常对象
        context: 上下文信息
        operation: 操作名称
    """
    logger = get_logger("freebSEngine.error")
    
    error_type = type(error).__name__
    error_msg = str(error)
    
    message = f"错误: {error_type} - {error_msg}"
    if operation:
        message = f"{operation}: {message}"
    
    # 记录错误
    logger.error(message, exc_info=True)
    
    # 记录上下文信息
    if context:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        logger.debug(f"错误上下文: {context_str}")


def log_warning_with_suggestion(
    warning: str,
    suggestion: str,
    context: Optional[Dict[str, Any]] = None,
):
    """
    记录警告并提供建议
    
    Args:
        warning: 警告信息
        suggestion: 建议
        context: 上下文信息
    """
    logger = get_logger("freebSEngine.warning")
    
    message = f"警告: {warning} | 建议: {suggestion}"
    logger.warning(message)
    
    if context:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        logger.debug(f"警告上下文: {context_str}")


# 预配置的日志记录器
def get_core_logger() -> logging.Logger:
    """获取核心模块日志记录器"""
    return get_logger("freebSEngine.core")


def get_utils_logger() -> logging.Logger:
    """获取工具模块日志记录器"""
    return get_logger("freebSEngine.utils")


def get_visualization_logger() -> logging.Logger:
    """获取可视化模块日志记录器"""
    return get_logger("freebSEngine.visualization")


def get_simulation_logger() -> logging.Logger:
    """获取模拟模块日志记录器"""
    return get_logger("freebSEngine.simulation")


# 示例使用
if __name__ == "__main__":
    # 示例1: 基本配置
    logger = setup_logging(
        log_level=logging.DEBUG,
        log_file="freebSEngine.log",
        console_output=True,
    )
    
    logger.info("freebSEngine 日志系统已初始化")
    logger.debug("调试信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    
    # 示例2: 性能记录
    import time
    start_time = time.time()
    time.sleep(0.1)
    log_performance("示例操作", time.time() - start_time, {"steps": 100})
    
    # 示例3: 错误记录
    try:
        raise ValueError("示例错误")
    except ValueError as e:
        log_error_with_context(
            e,
            context={"param1": "value1", "param2": 42},
            operation="示例函数"
        )
    
    print("日志配置示例完成")