"""基本性能基准测试"""

import time
import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from python.freebSEngine import (
        propagate_orbit,
        nbody_simulation,
        compute_keplerian_elements,
    )
    HAS_RUST = True
except ImportError:
    print("警告: 无法导入 Rust 模块，将使用 Python 模拟进行基准测试")
    HAS_RUST = False


class Timer:
    """简单的计时器"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.elapsed = 0.0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start_time
    
    def __str__(self):
        return f"{self.name}: {self.elapsed:.6f} 秒"


def benchmark_propagate_orbit():
    """基准测试轨道传播函数"""
    print("=== 轨道传播性能基准测试 ===")
    
    # 测试参数
    r0 = [1.496e11, 0.0, 0.0]  # 地球轨道
    v0 = [0.0, 29780.0, 0.0]
    epoch = 0.0
    
    test_cases = [
        ("小规模", 100, 3600.0),
        ("中等规模", 1000, 3600.0),
        ("大规模", 10000, 3600.0),
    ]
    
    results = []
    
    for name, num_steps, step_seconds in test_cases:
        if HAS_RUST:
            with Timer(f"Rust {name} ({num_steps} 步)") as timer:
                try:
                    positions = propagate_orbit(r0, v0, epoch, step_seconds, num_steps)
                    rust_time = timer.elapsed
                except Exception as e:
                    print(f"Rust 测试失败: {e}")
                    rust_time = float('inf')
        else:
            rust_time = float('inf')
        
        # Python 实现作为对比
        with Timer(f"Python {name} ({num_steps} 步)") as timer:
            positions_py = _python_propagate_orbit(r0, v0, epoch, step_seconds, num_steps)
            python_time = timer.elapsed
        
        speedup = python_time / rust_time if rust_time > 0 else float('inf')
        
        results.append({
            'name': name,
            'num_steps': num_steps,
            'rust_time': rust_time,
            'python_time': python_time,
            'speedup': speedup,
        })
        
        print(f"{name}: Rust={rust_time:.6f}s, Python={python_time:.6f}s, 加速比={speedup:.2f}x")
    
    return results


def _python_propagate_orbit(r0, v0, epoch, step_seconds, num_steps):
    """Python 实现的轨道传播（用于对比）"""
    # 简化实现：使用开普勒运动近似
    import numpy as np
    
    positions = np.zeros((num_steps, 3))
    
    # 简化：假设圆形轨道
    radius = np.linalg.norm(r0)
    velocity = np.linalg.norm(v0)
    
    # 角速度
    omega = velocity / radius
    
    for i in range(num_steps):
        t = i * step_seconds
        angle = omega * t
        
        # 在 xy 平面内旋转
        positions[i, 0] = radius * np.cos(angle)
        positions[i, 1] = radius * np.sin(angle)
        positions[i, 2] = 0.0
    
    return positions


def benchmark_nbody_simulation():
    """基准测试 N 体模拟"""
    print("\n=== N 体模拟性能基准测试 ===")
    
    test_cases = [
        ("2体问题", 2, 100),
        ("3体问题", 3, 100),
        ("5体问题", 5, 100),
        ("10体问题", 10, 50),
    ]
    
    results = []
    
    for name, num_bodies, steps in test_cases:
        # 生成随机测试数据
        np.random.seed(42)
        positions = np.random.uniform(-1e11, 1e11, (num_bodies, 3)).tolist()
        velocities = np.random.uniform(-10000, 10000, (num_bodies, 3)).tolist()
        masses = np.random.uniform(1e24, 1e27, num_bodies).tolist()
        
        if HAS_RUST:
            with Timer(f"Rust {name} ({num_bodies} 体, {steps} 步)") as timer:
                try:
                    all_positions = nbody_simulation(
                        positions, velocities, masses, 0.0, 3600.0, steps
                    )
                    rust_time = timer.elapsed
                except Exception as e:
                    print(f"Rust N体测试失败: {e}")
                    rust_time = float('inf')
        else:
            rust_time = float('inf')
        
        # Python 实现
        with Timer(f"Python {name} ({num_bodies} 体, {steps} 步)") as timer:
            all_positions_py = _python_nbody_simulation(
                positions, velocities, masses, 0.0, 3600.0, steps
            )
            python_time = timer.elapsed
        
        speedup = python_time / rust_time if rust_time > 0 else float('inf')
        
        results.append({
            'name': name,
            'num_bodies': num_bodies,
            'steps': steps,
            'rust_time': rust_time,
            'python_time': python_time,
            'speedup': speedup,
        })
        
        print(f"{name}: Rust={rust_time:.6f}s, Python={python_time:.6f}s, 加速比={speedup:.2f}x")
    
    return results


def _python_nbody_simulation(positions, velocities, masses, epoch, dt, steps):
    """Python 实现的 N 体模拟（用于对比）"""
    import numpy as np
    
    n = len(positions)
    G = 6.67430e-11
    
    # 转换为 numpy 数组
    pos = np.array(positions, dtype=np.float64)
    vel = np.array(velocities, dtype=np.float64)
    mass = np.array(masses, dtype=np.float64)
    
    # 存储所有位置
    all_positions = np.zeros((steps, n, 3))
    
    for step in range(steps):
        # 计算加速度
        acc = np.zeros_like(pos)
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    r_vec = pos[j] - pos[i]
                    r_mag = np.linalg.norm(r_vec)
                    
                    if r_mag > 0:
                        acc[i] += G * mass[j] / r_mag**3 * r_vec
        
        # 更新速度和位置（欧拉方法）
        vel += acc * dt
        pos += vel * dt
        
        # 存储位置
        all_positions[step] = pos.copy()
    
    return all_positions


def benchmark_memory_usage():
    """基准测试内存使用"""
    print("\n=== 内存使用基准测试 ===")
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # 测试不同规模的数据
    test_sizes = [100, 1000, 10000]
    
    for size in test_sizes:
        # 创建大型数组
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建测试数据
        data = np.random.randn(size, size)  # size x size 的矩阵
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # 理论内存使用
        theoretical_mb = (data.size * data.itemsize) / 1024 / 1024
        
        print(f"数组大小 {size}x{size}:")
        print(f"  实际内存使用: {memory_used:.2f} MB")
        print(f"  理论内存使用: {theoretical_mb:.2f} MB")
        print(f"  效率: {(theoretical_mb / memory_used * 100):.1f}%")
        
        # 清理
        del data
        import gc
        gc.collect()


def benchmark_accuracy():
    """基准测试计算精度"""
    print("\n=== 计算精度基准测试 ===")
    
    # 测试用例：地球轨道
    r0 = [1.496e11, 0.0, 0.0]
    v0 = [0.0, 29780.0, 0.0]
    epoch = 0.0
    step_seconds = 3600.0  # 1小时
    num_steps = 10
    
    if HAS_RUST:
        # Rust 计算
        positions_rust = propagate_orbit(r0, v0, epoch, step_seconds, num_steps)
        
        # Python 计算
        positions_python = _python_propagate_orbit(r0, v0, epoch, step_seconds, num_steps)
        
        # 计算误差
        error = np.abs(positions_rust - positions_python)
        max_error = np.max(error)
        mean_error = np.mean(error)
        relative_error = mean_error / np.linalg.norm(positions_rust[0])
        
        print(f"最大绝对误差: {max_error:.6e} m")
        print(f"平均绝对误差: {mean_error:.6e} m")
        print(f"相对误差: {relative_error:.6e}")
        
        # 验证能量守恒（简化）
        initial_energy = _calculate_orbital_energy(r0, v0)
        final_energy_rust = _calculate_orbital_energy(
            positions_rust[-1], 
            _estimate_velocity(positions_rust[-2], positions_rust[-1], step_seconds)
        )
        energy_error = abs(final_energy_rust - initial_energy) / abs(initial_energy)
        
        print(f"能量守恒误差: {energy_error:.6e}")
        
        return {
            'max_error': max_error,
            'mean_error': mean_error,
            'relative_error': relative_error,
            'energy_error': energy_error,
        }
    else:
        print("无法进行精度测试：Rust 模块未加载")
        return None


def _calculate_orbital_energy(r, v, mu=1.32712440018e20):
    """计算轨道比机械能"""
    r_norm = np.linalg.norm(r)
    v_norm = np.linalg.norm(v)
    return v_norm**2 / 2 - mu / r_norm


def _estimate_velocity(r1, r2, dt):
    """估计速度（有限差分）"""
    return (np.array(r2) - np.array(r1)) / dt


def run_all_benchmarks():
    """运行所有基准测试"""
    print("=" * 60)
    print("freebSEngine 性能基准测试")
    print("=" * 60)
    
    results = {}
    
    try:
        results['propagation'] = benchmark_propagate_orbit()
    except Exception as e:
        print(f"轨道传播基准测试失败: {e}")
    
    try:
        results['nbody'] = benchmark_nbody_simulation()
    except Exception as e:
        print(f"N体模拟基准测试失败: {e}")
    
    try:
        benchmark_memory_usage()
    except ImportError:
        print("内存使用测试跳过: 需要 psutil 库")
    except Exception as e:
        print(f"内存使用测试失败: {e}")
    
    try:
        results['accuracy'] = benchmark_accuracy()
    except Exception as e:
        print(f"精度测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("基准测试完成")
    print("=" * 60)
    
    # 生成总结报告
    if results.get('propagation'):
        print("\n性能总结:")
        for test in results['propagation']:
            if test['speedup'] < float('inf'):
                print(f"  {test['name']}: Rust 比 Python 快 {test['speedup']:.1f} 倍")
    
    return results


if __name__ == "__main__":
    run_all_benchmarks()