"""天体物理引擎 Python 前端

freebSEngine 是一个高性能的天体物理模拟引擎，提供轨道计算、N体模拟和可视化功能。
"""

import functools
from typing import Any, Callable, List, Optional, Tuple

import numpy as np

# 导入日志配置
from .logging_config import (
    configure_from_env,
    get_logger,
    log_error_with_context,
    log_performance,
)

# 版本信息
__version__ = "0.1.0"
__author__ = "freebSEngine Team"
__description__ = "High-performance astrophysics simulation engine"

# 设置默认日志配置
_logger = configure_from_env()
_logger.info(f"freebSEngine {__version__} 已加载")

# 使用纯 Python 实现（Rust 扩展暂时不可用）
_logger.info("使用纯 Python 实现，性能可能较低")

# 定义常量
GRAVITATIONAL_CONSTANT = 6.67430e-11
SPEED_OF_LIGHT = 299792458.0
ASTRONOMICAL_UNIT = 1.495978707e11
SOLAR_MASS = 1.98847e30
EARTH_MASS = 5.9722e24

# 纯 Python 实现
from ._python_fallback import (
    circular_orbit_velocity,
    compute_keplerian_elements,
    escape_velocity,
    nbody_simulation,
    orbital_period,
    propagate_orbit,
)

_has_rust_extension = False

# 导入图形模块（可选）
try:
    from . import demo

    _has_visualization = True
except ImportError:
    _logger.warning("可视化模块不可用，请安装 pygfx 等依赖")
    demo = None
    _has_visualization = False

# 导入其他模块
from . import advanced_mechanics, celestial_objects, utils

# 重新导出主要功能
__all__ = [
    # 核心功能
    "propagate_orbit",
    "compute_keplerian_elements",
    "orbital_period",
    "nbody_simulation",
    "circular_orbit_velocity",
    "escape_velocity",
    # 常量
    "GRAVITATIONAL_CONSTANT",
    "SPEED_OF_LIGHT",
    "ASTRONOMICAL_UNIT",
    "SOLAR_MASS",
    "EARTH_MASS",
    # 模块
    "demo",
    "utils",
    "celestial_objects",
    "advanced_mechanics",
    # 工具函数
    "handle_errors",
    "log_execution_time",
    "propagate_orbit_safe",
    "nbody_simulation_safe",
    "get_logger",
    "log_performance",
    "log_error_with_context",
    # 状态信息
    "__version__",
    "__author__",
    "__description__",
    "_has_rust_extension",
    "_has_visualization",
]


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
                "args": str(args)[:100],  # 限制长度
                "kwargs": str(kwargs)[:100],
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
                "has_rust": _has_rust_extension,
            }

            log_performance(func.__name__, duration, details)

            return result
        except Exception:
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
    """安全的轨道传播函数，包含错误处理和性能监控

    Args:
        r0: 初始位置向量 [x, y, z] (米)
        v0: 初始速度向量 [vx, vy, vz] (米/秒)
        epoch: 起始时间（Unix时间戳）
        step_seconds: 时间步长（秒）
        num_steps: 步数

    Returns:
        numpy.ndarray: 形状为 (num_steps, 3) 的位置数组
    """
    _logger.debug(
        f"开始轨道传播: steps={num_steps}, dt={step_seconds}s, rust={_has_rust_extension}"
    )

    # 验证输入
    if len(r0) != 3 or len(v0) != 3:
        raise ValueError("位置和速度向量必须恰好有3个元素")
    if step_seconds <= 0:
        raise ValueError("时间步长必须为正数")
    if num_steps <= 0:
        raise ValueError("步数必须为正数")

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
    """安全的 N 体模拟函数，包含错误处理和性能监控

    Args:
        positions: 初始位置列表 [[x1,y1,z1], [x2,y2,z2], ...]
        velocities: 初始速度列表
        masses: 质量列表
        epoch: 起始时间
        dt: 时间步长
        steps: 步数

    Returns:
        numpy.ndarray: 形状为 (steps, n_bodies, 3) 的位置数组
    """
    _logger.debug(
        f"开始 N 体模拟: bodies={len(masses)}, steps={steps}, dt={dt}s, rust={_has_rust_extension}"
    )

    # 验证输入
    n = len(positions)
    if n != len(velocities) or n != len(masses):
        raise ValueError("位置、速度和质量列表必须具有相同的长度")
    if n == 0:
        raise ValueError("至少需要一个天体")

    for i, pos in enumerate(positions):
        if len(pos) != 3:
            raise ValueError(f"位置向量 {i} 必须恰好有3个元素")

    for i, vel in enumerate(velocities):
        if len(vel) != 3:
            raise ValueError(f"速度向量 {i} 必须恰好有3个元素")

    for i, mass in enumerate(masses):
        if mass <= 0:
            raise ValueError(f"质量 {i} 必须为正数")

    return nbody_simulation(positions, velocities, masses, epoch, dt, steps)


# 类型提示的包装函数
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
    return propagate_orbit_safe(r0, v0, epoch, step_seconds, num_steps)


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


# 添加类型提示的包装函数到 __all__
__all__.extend(
    [
        "propagate_orbit_typed",
        "compute_keplerian_elements_typed",
    ]
)

# 模块初始化时的信息
if __name__ == "__main__":
    print(f"freebSEngine v{__version__}")
    print(f"Rust 扩展可用: {_has_rust_extension}")
    print(f"可视化可用: {_has_visualization}")
    print(f"作者: {__author__}")
    print(f"描述: {__description__}")
