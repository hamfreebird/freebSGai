#!/usr/bin/env python3
"""
高级使用示例 - 展示 freebSEngine 的高级功能

这个示例展示了：
1. 高级轨道力学计算
2. 多体系统模拟
3. 性能优化技巧
4. 自定义可视化
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# 导入 freebSEngine
import freebSEngine as fse
from freebSEngine.celestial_objects import (
    SUN, EARTH, MARS, JUPITER, SATURN,
    get_body, CelestialBody
)
from freebSEngine.utils import (
    au_to_meters, meters_to_au,
    days_to_seconds, seconds_to_days,
    cartesian_to_spherical, spherical_to_cartesian
)
from freebSEngine.advanced_mechanics import AdvancedOrbitalMechanics

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def demo_advanced_mechanics():
    """演示高级轨道力学功能"""
    print("=" * 60)
    print("高级轨道力学演示")
    print("=" * 60)
    
    # 创建高级轨道力学实例
    mechanics = AdvancedOrbitalMechanics()
    
    # 1. 霍曼转移计算
    print("\n1. 霍曼转移计算")
    print("-" * 40)
    
    # 地球轨道 (1 AU) 到火星轨道 (1.524 AU)
    r1 = 1.0 * fse.ASTRONOMICAL_UNIT  # 地球轨道半径
    r2 = 1.524 * fse.ASTRONOMICAL_UNIT  # 火星轨道半径
    
    dv1, dv2, total_dv, transfer_time = mechanics.hohmann_transfer(r1, r2, SUN.mass)
    
    print(f"初始轨道半径: {meters_to_au(r1):.3f} AU")
    print(f"目标轨道半径: {meters_to_au(r2):.3f} AU")
    print(f"第一次变轨 Δv: {dv1/1000:.2f} km/s")
    print(f"第二次变轨 Δv: {dv2/1000:.2f} km/s")
    print(f"总 Δv: {total_dv/1000:.2f} km/s")
    print(f"转移时间: {seconds_to_days(transfer_time):.1f} 天")
    
    # 2. 发射窗口计算
    print("\n2. 发射窗口计算")
    print("-" * 40)
    
    # 地球到火星的发射窗口
    launch_windows = mechanics.launch_window_analysis(
        departure_body=EARTH,
        arrival_body=MARS,
        start_date=0,  # 从今天开始
        analysis_days=365*2  # 分析两年
    )
    
    if launch_windows:
        best_window = launch_windows[0]
        print(f"找到 {len(launch_windows)} 个发射窗口")
        print(f"最佳窗口:")
        print(f"  出发日期: 第 {best_window['departure_day']:.0f} 天")
        print(f"  到达日期: 第 {best_window['arrival_day']:.0f} 天")
        print(f"  飞行时间: {best_window['flight_time_days']:.1f} 天")
        print(f"  总 Δv: {best_window['total_dv']/1000:.2f} km/s")
    else:
        print("未找到合适的发射窗口")
    
    # 3. 轨道摄动分析
    print("\n3. 轨道摄动分析")
    print("-" * 40)
    
    # 地球轨道参数
    earth_a = 1.0 * fse.ASTRONOMICAL_UNIT  # 半长轴
    earth_e = 0.0167  # 偏心率
    earth_i = np.radians(0.0)  # 倾角
    
    perturbations = mechanics.analyze_perturbations(
        semi_major_axis=earth_a,
        eccentricity=earth_e,
        inclination=earth_i,
        central_body=SUN,
        include_j2=False  # 简化计算
    )
    
    print("地球轨道摄动分析:")
    for key, value in perturbations.items():
        if 'rate' in key:
            # 转换为每年变化
            rate_per_year = value * 365.25 * 24 * 3600
            if 'Ω' in key or 'ω' in key:
                print(f"  {key}: {np.degrees(rate_per_year):.4f} °/年")
            else:
                print(f"  {key}: {rate_per_year:.4e} /年")
        else:
            print(f"  {key}: {value:.4e}")
    
    return mechanics


def demo_multi_body_system():
    """演示多体系统模拟"""
    print("\n" + "=" * 60)
    print("多体系统模拟演示")
    print("=" * 60)
    
    # 创建一个小型太阳系（太阳、地球、火星）
    bodies = [SUN, EARTH, MARS]
    
    # 初始位置和速度
    positions = []
    velocities = []
    masses = []
    
    for body in bodies:
        positions.append(body.position)
        velocities.append(body.velocity)
        masses.append(body.mass)
    
    print(f"模拟 {len(bodies)} 个天体:")
    for i, body in enumerate(bodies):
        print(f"  {i+1}. {body.name}: 质量={body.mass/fse.SOLAR_MASS:.6f} M☉")
    
    # 运行短期模拟
    print("\n运行 90 天模拟 (每天一步)...")
    start_time = time.time()
    
    all_positions = fse.nbody_simulation(
        positions, velocities, masses,
        epoch=0.0,
        dt=24*3600,  # 1天步长
        steps=90     # 90天
    )
    
    elapsed = time.time() - start_time
    print(f"模拟完成! 耗时: {elapsed:.3f} 秒")
    print(f"结果形状: {all_positions.shape}")
    
    return all_positions, bodies


def visualize_multi_body_system(all_positions, bodies):
    """可视化多体系统模拟结果"""
    print("\n" + "=" * 60)
    print("多体系统可视化")
    print("=" * 60)
    
    # 转换为 AU 单位
    positions_au = all_positions / fse.ASTRONOMICAL_UNIT
    
    # 创建 3D 图形
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 3D 轨迹图
    ax1 = fig.add_subplot(221, projection='3d')
    
    colors = ['orange', 'blue', 'red']
    labels = [body.name for body in bodies]
    
    for i in range(len(bodies)):
        ax1.plot(
            positions_au[:, i, 0],
            positions_au[:, i, 1],
            positions_au[:, i, 2],
            color=colors[i],
            alpha=0.7,
            linewidth=1.5,
            label=labels[i]
        )
        
        # 标记起点和终点
        ax1.scatter(
            positions_au[0, i, 0],
            positions_au[0, i, 1],
            positions_au[0, i, 2],
            color=colors[i],
            s=100,
            marker='o',
            edgecolors='black'
        )
        
        ax1.scatter(
            positions_au[-1, i, 0],
            positions_au[-1, i, 1],
            positions_au[-1, i, 2],
            color=colors[i],
            s=150,
            marker='*',
            edgecolors='black'
        )
    
    ax1.set_xlabel('X (AU)')
    ax1.set_ylabel('Y (AU)')
    ax1.set_zlabel('Z (AU)')
    ax1.set_title('多体系统 3D 轨迹')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. XY 平面投影
    ax2 = fig.add_subplot(222)
    
    for i in range(len(bodies)):
        ax2.plot(
            positions_au[:, i, 0],
            positions_au[:, i, 1],
            color=colors[i],
            alpha=0.7,
            linewidth=1.5,
            label=labels[i]
        )
    
    ax2.set_xlabel('X (AU)')
    ax2.set_ylabel('Y (AU)')
    ax2.set_title('XY 平面投影')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    
    # 3. 相对距离图
    ax3 = fig.add_subplot(223)
    
    # 计算地球-太阳距离
    earth_sun_dist = np.linalg.norm(
        positions_au[:, 1, :] - positions_au[:, 0, :],
        axis=1
    )
    
    # 计算火星-太阳距离
    mars_sun_dist = np.linalg.norm(
        positions_au[:, 2, :] - positions_au[:, 0, :],
        axis=1
    )
    
    days = np.arange(len(earth_sun_dist))
    
    ax3.plot(days, earth_sun_dist, 'b-', label='地球-太阳距离', linewidth=2)
    ax3.plot(days, mars_sun_dist, 'r-', label='火星-太阳距离', linewidth=2)
    
    ax3.set_xlabel('时间 (天)')
    ax3.set_ylabel('距离 (AU)')
    ax3.set_title('天体-太阳距离变化')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 速度变化图
    ax4 = fig.add_subplot(224)
    
    # 计算速度大小
    velocities_au_per_day = np.zeros_like(positions_au)
    for i in range(1, positions_au.shape[0]):
        velocities_au_per_day[i] = (positions_au[i] - positions_au[i-1])  # AU/天
    
    earth_speed = np.linalg.norm(velocities_au_per_day[:, 1, :], axis=1)
    mars_speed = np.linalg.norm(velocities_au_per_day[:, 2, :], axis=1)
    
    ax4.plot(days, earth_speed, 'b-', label='地球速度', linewidth=2)
    ax4.plot(days, mars_speed, 'r-', label='火星速度', linewidth=2)
    
    ax4.set_xlabel('时间 (天)')
    ax4.set_ylabel('速度 (AU/天)')
    ax4.set_title('天体速度变化')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return fig


def demo_performance_tips():
    """演示性能优化技巧"""
    print("\n" + "=" * 60)
    print("性能优化技巧")
    print("=" * 60)
    
    # 1. 批量计算 vs 循环计算
    print("\n1. 批量计算 vs 循环计算")
    print("-" * 40)
    
    # 创建多个轨道
    num_orbits = 1000
    semi_major_axes = np.linspace(0.5, 2.0, num_orbits) * fse.ASTRONOMICAL_UNIT
    
    # 方法1: 循环计算（较慢）
    print(f"计算 {num_orbits} 个轨道的周期...")
    
    start_time = time.time()
    periods_loop = []
    for a in semi_major_axes:
        period = fse.orbital_period(a, SUN.gravitational_parameter)
        periods_loop.append(period)
    loop_time = time.time() - start_time
    
    # 方法2: 向量化计算（较快）
    start_time = time.time()
    periods_vectorized = fse.orbital_period(semi_major_axes, SUN.gravitational_parameter)
    vector_time = time.time() - start_time
    
    print(f"循环计算时间: {loop_time:.4f} 秒")
    print(f"向量化计算时间: {vector_time:.4f} 秒")
    print(f"加速比: {loop_time/vector_time:.2f}x")
    
    # 2. 内存使用优化
    print("\n2. 内存使用优化")
    print("-" * 40)
    
    # 大型模拟的内存估计
    num_bodies = 10
    num_steps = 10000
    
    # 估计内存使用
    memory_bytes = num_bodies * num_steps * 3 * 8  # 双精度浮点数
    memory_mb = memory_bytes / (1024 * 1024)
    
    print(f"模拟配置:")
    print(f"  天体数量: {num_bodies}")
    print(f"  时间步数: {num_steps}")
    print(f"  估计内存: {memory_mb:.2f} MB")
    
    # 优化建议
    print("\n优化建议:")
    print("  1. 使用较小的步长进行长期模拟")
    print("  2. 定期保存结果到磁盘")
    print("  3. 使用稀疏输出（每 N 步保存一次）")
    print("  4. 考虑使用 GPU 加速（如果可用）")
    
    return periods_vectorized


def demo_custom_visualization():
    """演示自定义可视化"""
    print("\n" + "=" * 60)
    print("自定义可视化演示")
    print("=" * 60)
    
    # 创建一个简单的动画
    print("创建轨道动画...")
    
    # 地球轨道参数
    r0 = [1.496e11, 0.0, 0.0]
    v0 = [0.0, 29780.0, 0.0]
    
    # 计算一年的轨道（简化版，每10天一步）
    positions = fse.propagate_orbit(r0, v0, epoch=0.0, step_seconds=10*24*3600, num_steps=37)
    positions_au = positions / fse.ASTRONOMICAL_UNIT
    
    # 创建动画
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 初始化图形元素
    sun = ax.scatter([0], [0], c='orange', s=300, marker='*', edgecolors='red', linewidth=2)
    orbit_line, = ax.plot([], [], 'b-', alpha=0.5, linewidth=1.5)
    earth_point = ax.scatter([], [], c='blue', s=100, edgecolors='black')
    
    # 设置图形范围
    max_range = 1.2
    ax.set_xlim(-max_range, max_range)
    ax.set_ylim(-max_range, max_range)
    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_title('地球绕太阳轨道动画')
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    def init():
        """初始化动画"""
        orbit_line.set_data([], [])
        earth_point.set_offsets([[0, 0]])
        return orbit_line, earth_point
    
    def update(frame):
        """更新动画帧"""
        # 更新轨道线（显示到当前帧的轨迹）
        orbit_line.set_data(positions_au[:frame+1, 0], positions_au[:frame+1, 1])
        
        # 更新地球位置
        earth_point.set_offsets([positions_au[frame, :2]])
        
        # 更新标题
        ax.set_title(f'地球绕太阳轨道动画 (第 {frame*10} 天)')
        
        return orbit_line, earth_point
    
    # 创建动画
    anim = FuncAnimation(
        fig, update, frames=len(positions_au),
        init_func=init, blit=True, interval=100
    )
    
    print("动画创建完成!")
    print("提示: 要保存动画，请取消注释以下代码:")
    print("  anim.save('earth_orbit.gif', writer='pillow', fps=10)")
    
    plt.show()
    
    return anim


def main():
    """主函数"""
    print("freebSEngine 高级使用示例")
    print("=" * 60)
    
    try:
        # 演示高级轨道力学
        mechanics = demo_advanced_mechanics()
        
        # 演示多体系统模拟
        all_positions, bodies = demo_multi_body_system()
        
        # 演示性能优化技巧
        periods = demo_performance_tips()
        
        # 询问用户是否要可视化
        print("\n" + "=" * 60)
        response = input("是否要显示可视化图表? (y/n): ").strip().lower()
        
        if response == 'y':
            # 可视化多体系统
            fig = visualize_multi_body_system(all_positions, bodies)
            
            # 演示自定义可视化
            print("\n是否要显示轨道动画? (y/n): ")
            anim_response = input().strip().lower()
            if anim_response == 'y':
                anim = demo_custom_visualization()
        
        print("\n" + "=" * 60)
        print("示例运行完成!")
        print("\n更多功能:")
        print("  1. 运行可视化演示: python