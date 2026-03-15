"""天体物理引擎 Python 前端

freebSEngine 是一个高性能的天体物理模拟引擎，提供轨道计算、N体模拟和可视化功能。
"""

import sys
import functools
import traceback
from typing import List, Tuple, Optional, Any, Callable
import numpy as np

# 导入日志配置
from .logging_config import (
    get_logger,
    log_error_with_context,
    log_performance,
    configure_from_env,
)

# 设置默认日志配置
_logger = configure_from_env()
_logger.info(f"freebSEngine {__version__} 已加载")

# 导入 Rust 核心模块
from .freebSEngine import (
    propagate_orbit,
    compute_keplerian_elements,
    orbital_period,
    nbody_simulation,
    circular_orbit_velocity,
    escape_velocity,
    GRAVITATIONAL_CONSTANT,
    SPEED_OF_LIGHT,
    ASTRONOMICAL_UNIT,
    SOLAR_MASS,
    EARTH_MASS,
)

# 导入图形模块
from . import demo
from . import utils
from . import celestial_objects

# 重新导出主要功能
__all__ = [
    "propagate_orbit",
    "compute_keplerian_elements",
    "orbital_period",
    "nbody_simulation",
    "circular_orbit_velocity",
    "escape_velocity",
    "demo",
    "utils",
    "celestial_objects",
    "GRAVITATIONAL_CONSTANT",
    "SPEED_OF_LIGHT",
    "ASTRONOMICAL_UNIT",
    "SOLAR_MASS",
    "EARTH_MASS",
]

# 版本信息
__version__ = "0.1.0"
__author__ = "freebSEngine Team"
__description__ = "High-performance astrophysics simulation engine"

# 类型提示
from typing import List, Tuple, Optional
import numpy as np

def propagate_orbit_typed(
    r0: List[float],
    v0: List[float],
    epoch: float,
    step_seconds: float,
    num_steps: int,
) -> np.ndarray:
    """计算天体轨道位置（类型提示版本）
    
    Args:
        r0: 初始位置向量 [x, y, z] (米)
        v0: 初始速度向量 [vx, vy, vz] (米/秒)
        epoch: 起始时间（Unix时间戳）
        step_seconds: 时间步长（秒）
        num_steps: 步数
        
    Returns:
        numpy.ndarray: 形状为 (num_steps, 3) 的位置数组
    """
    return propagate_orbit(r0, v0, epoch, step_seconds, num_steps)

def compute_keplerian_elements_typed(
    r: List[float],
    v: List[float],
    epoch: float,
) -> np.ndarray:
    """计算轨道根数（开普勒元素）
    
    Args:
        r: 位置向量 [x, y, z] (米)
        v: 速度向量 [vx, vy, vz] (米/秒)
        epoch: 时间（Unix时间戳）
        
    Returns:
        numpy.ndarray: [a, e, i, Ω, ω, ν] 数组
                      (半长轴, 偏心率, 倾角, 升交点赤经, 近地点幅角, 真近点角)
    """
    return compute_keplerian_elements(r, v, epoch)


# 错误处理装饰器
def handle_errors(func: Callable) -> Callable:
    """错误处理装饰器，用于包装函数并提供统一的错误处理"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 记录错误上下文
            context = {
                "function": func.__name__,
                "module": func.__module__,
                "args": str(args),
                "kwargs": str(kwargs),
            }
            
            log_error_with_context(e, context, operation=func.__name__)
            
            # 重新抛出异常
            raise
    
    return wrapper


def log_execution_time(func: Callable) -> Callable:
    """记录函数执行时间的装饰器"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # 记录性能指标
            details = {
                "args_count": len(args),
                "kwargs_count": len(kwargs),
                "function": func.__name__,
            }
            
            log_performance(func.__name__, duration, details)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"函数 {func.__name__} 执行失败，耗时 {duration:.6f} 秒")
            raise
    
    return wrapper


# 包装核心函数以添加错误处理和性能监控
@handle_errors
@log_execution_time
def propagate_orbit_safe(
    r0: List[float],
    v0: List[float],
    epoch: float,
    step_seconds: float,
    num_steps: int,
) -> np.ndarray:
    """安全的轨道传播函数，包含错误处理和性能监控"""
    _logger.debug(f"开始轨道传播: steps={num_steps}, dt={step_seconds}s")
    return propagate_orbit(r0, v0, epoch, step_seconds, num_steps)


@handle_errors
@log_execution_time
def nbody_simulation_safe(
    positions: List[List[float]],
    velocities: List[List[float]],
    masses: List[float],
    epoch: float,
    dt: float,
    steps: int,
) -> np.ndarray:
    """安全的 N 体模拟函数，包含错误处理和性能监控"""
    _logger.debug(f"开始 N 体模拟: bodies={len(masses)}, steps={steps}, dt={dt}s")
    return nbody_simulation(positions, velocities, masses, epoch, dt, steps)


# 更新 __all__ 列表以包含新函数
__all__.extend([
    "handle_errors",
    "log_execution_time",
    "propagate_orbit_safe",
    "nbody_simulation_safe",
    "get_logger",
    "log_performance",
    "log_error_with_context",
])


