"""freebSEngine 基本使用示例"""

import numpy as np
import freebSEngine as fse
from freebSEngine.celestial_objects import SUN, EARTH, MARS
from freebSEngine.utils import au_to_meters, meters_to_au, solar_mass_to_kg


def demo_constants():
    """演示物理常量"""
    print("=== 物理常量 ===")
    print(f"引力常数 G: {fse.GRAVITATIONAL_CONSTANT:.3e} m³/kg/s²")
    print(f"光速 c: {fse.SPEED_OF_LIGHT:.3e} m/s")
    print(f"天文单位 AU: {fse.ASTRONOMICAL_UNIT:.3e} m")
    print(f"太阳质量 M☉: {fse.SOLAR_MASS:.3e} kg")
    print(f"地球质量 M⊕: {fse.EARTH_MASS:.3e} kg")
    print()


def demo_unit_conversions():
    """演示单位转换"""
    print("=== 单位转换 ===")
    
    # AU 转换
    au_value = 1.5
    meters = au_to_meters(au_value)
    print(f"{au_value} AU = {meters:.3e} m")
    print(f"{meters:.3e} m = {meters_to_au(meters):.3f} AU")
    
    # 太阳质量转换
    solar_mass_value = 0.5
    kg = solar_mass_to_kg(solar_mass_value)
    print(f"{solar_mass_value} M☉ = {kg:.3e} kg")
    
    print()


def demo_celestial_objects():
    """演示天体对象"""
    print("=== 天体对象 ===")
    
    print(f"太阳:")
    print(f"  质量: {SUN.mass:.3e} kg")
    print(f"  半径: {SUN.radius:.3e} m")
    print(f"  表面重力: {SUN.surface_gravity:.2f} m/s²")
    print(f"  逃逸速度: {SUN.escape_velocity/1000:.2f} km/s")
    
    print(f"\n地球:")
    print(f"  质量: {EARTH.mass:.3e} kg")
    print(f"  半径: {EARTH.radius:.3e} m")
    print(f"  表面重力: {EARTH.surface_gravity:.2f} m/s²")
    print(f"  逃逸速度: {EARTH.escape_velocity/1000:.2f} km/s")
    
    print(f"\n火星:")
    print(f"  质量: {MARS.mass:.3e} kg")
    print(f"  半径: {MARS.radius:.3e} m")
    print(f"  表面重力: {MARS.surface_gravity:.2f} m/s²")
    print(f"  逃逸速度: {MARS.escape_velocity/1000:.2f} km/s")
    
    print()


def demo_orbital_calculations():
    """演示轨道计算"""
    print("=== 轨道计算 ===")
    
    # 地球轨道参数
    earth_orbit_radius = 1.496e11  # 1 AU
    sun_mu = SUN.gravitational_parameter
    
    # 计算圆形轨道速度
    earth_velocity = fse.circular_orbit_velocity(earth_orbit_radius, SUN.mass)
    print(f"地球圆形轨道速度: {earth_velocity/1000:.2f} km/s")
    
    # 计算轨道周期
    earth_period = fse.orbital_period(earth_orbit_radius, sun_mu)
    print(f"地球轨道周期: {earth_period/(24*3600):.2f} 天")
    
    # 计算逃逸速度
    earth_escape = fse.escape_velocity(EARTH.radius, EARTH.mass)
    print(f"地球逃逸速度: {earth_escape/1000:.2f} km/s")
    
    # 火星轨道
    mars_orbit_radius = 2.279e11  # 1.52 AU
    mars_velocity = fse.circular_orbit_velocity(mars_orbit_radius, SUN.mass)
    mars_period = fse.orbital_period(mars_orbit_radius, sun_mu)
    print(f"\n火星圆形轨道速度: {mars_velocity/1000:.2f} km/s")
    print(f"火星轨道周期: {mars_period/(24*3600):.2f} 天")
    
    print()


def demo_orbit_propagation():
    """演示轨道传播"""
    print("=== 轨道传播 ===")
    
    try:
        # 地球轨道参数
        r0 = [1.496e11, 0.0, 0.0]  # 初始位置
        v0 = [0.0, 29780.0, 0.0]   # 初始速度
        
        # 计算轨道
        positions = fse.propagate_orbit(r0, v0, epoch=0.0, step_seconds=3600.0, num_steps=10)
        
        print(f"轨道位置数组形状: {positions.shape}")
        print(f"前3个位置:")
        for i in range(3):
            pos = positions[i]
            distance = np.linalg.norm(pos)
            print(f"  步 {i}: 位置={pos/1e11:.3f}×10¹¹ m, 距离={distance/1e11:.3f} AU")
        
        # 计算开普勒元素
        elements = fse.compute_keplerian_elements(r0, v0, epoch=0.0)
        print(f"\n开普勒轨道根数:")
        print(f"  半长轴 a: {elements[0]/1e11:.3f}×10¹¹ m ({elements[0]/fse.ASTRONOMICAL_UNIT:.3f} AU)")
        print(f"  偏心率 e: {elements[1]:.4f}")
        print(f"  倾角 i: {elements[2]:.2f}°")
        print(f"  升交点赤经 Ω: {elements[3]:.2f}°")
        print(f"  近地点幅角 ω: {elements[4]:.2f}°")
        print(f"  真近点角 ν: {elements[5]:.2f}°")
        
    except Exception as e:
        print(f"轨道传播演示失败: {e}")
        print("可能需要先构建 Rust 模块: maturin develop")
    
    print()


def demo_nbody_simulation():
    """演示N体模拟"""
    print("=== N体模拟 ===")
    
    try:
        # 创建简单的三体系统（太阳、地球、木星简化版）
        positions = [
            [0.0, 0.0, 0.0],           # 太阳在原点
            [1.496e11, 0.0, 0.0],      # 地球在x轴
            [7.785e11, 0.0, 0.0],      # 木星在x轴
        ]
        
        velocities = [
            [0.0, 0.0, 0.0],           # 太阳静止
            [0.0, 29780.0, 0.0],       # 地球y方向速度
            [0.0, 13070.0, 0.0],       # 木星y方向速度
        ]
        
        masses = [
            SUN.mass,                   # 太阳质量
            EARTH.mass,                 # 地球质量
            0.001 * SUN.mass,           # 简化木星质量
        ]
        
        # 运行短时间模拟
        print("运行N体模拟（10步，步长1天）...")
        all_positions = fse.nbody_simulation(
            positions, velocities, masses,
            epoch=0.0, dt=24*3600.0, steps=10
        )
        
        print(f"模拟结果形状: {all_positions.shape}")  # (10, 3, 3)
        print("模拟完成")
        
    except Exception as e:
        print(f"N体模拟演示失败: {e}")
        print("可能需要先构建 Rust 模块: maturin develop")
    
    print()


def demo_utils_functions():
    """演示工具函数"""
    print("=== 工具函数 ===")
    
    from freebSEngine.utils import (
        orbital_elements_to_cartesian,
        vis_viva_equation,
        calculate_orbital_plane_normal,
    )
    
    # 地球轨道参数
    a = 1.496e11      # 半长轴
    e = 0.0167        # 偏心率
    i = 0.0           # 倾角
    raan = 0.0        # 升交点赤经
    argp = 0.0        # 近地点幅角
    nu = 0.0          # 真近点角
    mu = SUN.gravitational_parameter
    
    # 开普勒元素转笛卡尔坐标
    position, velocity = orbital_elements_to_cartesian(a, e, i, raan, argp, nu, mu)
    print(f"从开普勒元素转换:")
    print(f"  位置: {position/1e11:.3f}×10¹¹ m")
    print(f"  速度: {velocity/1000:.2f} km/s")
    
    # 活力公式
    r = np.linalg.norm(position)
    v_visviva = vis_viva_equation(r, a, mu)
    print(f"\n活力公式计算速度: {v_visviva/1000:.2f} km/s")
    
    # 轨道平面法向量
    normal = calculate_orbital_plane_normal(position, velocity)
    print(f"轨道平面法向量: {normal}")
    
    print()


def main():
    """运行所有演示"""
    print("=" * 60)
    print("freebSEngine 基本使用演示")
    print("=" * 60)
    
    demos = [
        demo_constants,
        demo_unit_conversions,
        demo_celestial_objects,
        demo_orbital_calculations,
        demo_orbit_propagation,
        demo_nbody_simulation,
        demo_utils_functions,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"演示 {demo.__name__} 出错: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)
    
    # 提示下一步
    print("\n下一步:")
    print("1. 运行可视化演示: python -m freebSEngine.demo")
    print("2. 查看更多示例: 查看 examples/ 目录")
    print("3. 阅读文档: 查看 README.md 和代码文档")


if __name__ == "__main__":
    main()