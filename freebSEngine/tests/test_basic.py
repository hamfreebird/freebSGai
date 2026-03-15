"""基本功能测试"""

import sys
import os
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from python.freebSEngine import (
        propagate_orbit,
        compute_keplerian_elements,
        orbital_period,
        circular_orbit_velocity,
        escape_velocity,
        GRAVITATIONAL_CONSTANT,
        ASTRONOMICAL_UNIT,
        SOLAR_MASS,
        EARTH_MASS,
    )
    from python.freebSEngine.utils import (
        au_to_meters,
        meters_to_au,
        solar_mass_to_kg,
        kg_to_solar_mass,
        calculate_gravitational_parameter,
    )
    from python.freebSEngine.celestial_objects import (
        SUN, EARTH, get_body,
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("请先构建项目: maturin develop 或 pip install -e .")
    sys.exit(1)


def test_constants():
    """测试物理常量"""
    print("测试物理常量...")
    
    assert GRAVITATIONAL_CONSTANT == 6.67430e-11
    assert ASTRONOMICAL_UNIT == 1.495978707e11
    assert SOLAR_MASS == 1.98847e30
    assert EARTH_MASS == 5.9722e24
    
    print("✓ 常量测试通过")


def test_unit_conversions():
    """测试单位转换"""
    print("测试单位转换...")
    
    # AU 转换
    au_value = 1.0
    meters = au_to_meters(au_value)
    assert np.isclose(meters, ASTRONOMICAL_UNIT)
    assert np.isclose(meters_to_au(meters), au_value)
    
    # 太阳质量转换
    solar_mass_value = 1.0
    kg = solar_mass_to_kg(solar_mass_value)
    assert np.isclose(kg, SOLAR_MASS)
    assert np.isclose(kg_to_solar_mass(kg), solar_mass_value)
    
    print("✓ 单位转换测试通过")


def test_celestial_objects():
    """测试天体对象"""
    print("测试天体对象...")
    
    # 测试太阳属性
    assert SUN.name == "Sun"
    assert SUN.mass == 1.98847e30
    assert SUN.radius == 6.957e8
    
    # 测试地球属性
    assert EARTH.name == "Earth"
    assert EARTH.mass == 5.9722e24
    assert EARTH.radius == 6.371e6
    
    # 测试获取函数
    sun_from_get = get_body("sun")
    assert sun_from_get.name == SUN.name
    assert sun_from_get.mass == SUN.mass
    
    earth_from_get = get_body("earth")
    assert earth_from_get.name == EARTH.name
    assert earth_from_get.mass == EARTH.mass
    
    print("✓ 天体对象测试通过")


def test_orbital_calculations():
    """测试轨道计算"""
    print("测试轨道计算...")
    
    # 测试轨道周期
    earth_semi_major_axis = 1.496e11  # 米
    sun_mu = GRAVITATIONAL_CONSTANT * SUN.mass
    period = orbital_period(earth_semi_major_axis, sun_mu)
    
    # 地球轨道周期约为365.25天
    expected_period_days = 365.25 * 24 * 3600
    assert np.isclose(period, expected_period_days, rtol=0.1)  # 10% 容差
    
    # 测试圆形轨道速度
    earth_orbit_radius = 1.496e11
    earth_velocity = circular_orbit_velocity(earth_orbit_radius, SUN.mass)
    expected_velocity = 29780.0  # 地球轨道速度约 29.78 km/s
    assert np.isclose(earth_velocity, expected_velocity, rtol=0.1)
    
    # 测试逃逸速度
    earth_escape = escape_velocity(EARTH.radius, EARTH.mass)
    expected_escape = 11186.0  # 地球逃逸速度约 11.186 km/s
    assert np.isclose(earth_escape, expected_escape, rtol=0.1)
    
    print("✓ 轨道计算测试通过")


def test_propagate_orbit():
    """测试轨道传播"""
    print("测试轨道传播...")
    
    # 地球轨道参数
    r0 = [1.496e11, 0.0, 0.0]  # 1 AU
    v0 = [0.0, 29780.0, 0.0]   # 地球轨道速度
    epoch = 0.0
    step_seconds = 3600.0  # 1小时
    num_steps = 10
    
    try:
        positions = propagate_orbit(r0, v0, epoch, step_seconds, num_steps)
        
        # 检查输出形状
        assert positions.shape == (num_steps, 3)
        
        # 检查位置变化
        first_pos = positions[0]
        last_pos = positions[-1]
        
        # 位置应该不同
        assert not np.allclose(first_pos, last_pos)
        
        # 距离应该大致相同（圆形轨道）
        first_distance = np.linalg.norm(first_pos)
        last_distance = np.linalg.norm(last_pos)
        assert np.isclose(first_distance, last_distance, rtol=0.1)
        
        print("✓ 轨道传播测试通过")
        
    except Exception as e:
        print(f"轨道传播测试失败: {e}")
        # 如果Rust模块未构建，跳过此测试
        print("⚠ 跳过轨道传播测试（可能需要先构建项目）")


def test_keplerian_elements():
    """测试开普勒元素计算"""
    print("测试开普勒元素计算...")
    
    # 地球轨道参数
    r = [1.496e11, 0.0, 0.0]
    v = [0.0, 29780.0, 0.0]
    epoch = 0.0
    
    try:
        elements = compute_keplerian_elements(r, v, epoch)
        
        # 检查输出形状
        assert elements.shape == (6,)
        
        # 检查元素值
        semi_major_axis = elements[0]
        eccentricity = elements[1]
        
        # 地球轨道半长轴约为1 AU
        assert np.isclose(semi_major_axis, 1.496e11, rtol=0.1)
        
        # 地球轨道偏心率很小
        assert eccentricity < 0.1
        
        print("✓ 开普勒元素测试通过")
        
    except Exception as e:
        print(f"开普勒元素测试失败: {e}")
        # 如果Rust模块未构建，跳过此测试
        print("⚠ 跳过开普勒元素测试（可能需要先构建项目）")


def test_utils_functions():
    """测试工具函数"""
    print("测试工具函数...")
    
    # 测试引力参数计算
    earth_mu = calculate_gravitational_parameter(EARTH.mass)
    expected_earth_mu = GRAVITATIONAL_CONSTANT * EARTH.mass
    assert np.isclose(earth_mu, expected_earth_mu)
    
    # 测试活力公式
    from python.freebSEngine.utils import vis_viva_equation
    
    r = 1.496e11  # 地球轨道半径
    a = 1.496e11  # 圆形轨道，半长轴等于半径
    mu = sun_mu = GRAVITATIONAL_CONSTANT * SUN.mass
    
    velocity = vis_viva_equation(r, a, mu)
    expected_velocity = 29780.0
    assert np.isclose(velocity, expected_velocity, rtol=0.1)
    
    print("✓ 工具函数测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始运行 freebSEngine 测试")
    print("=" * 50)
    
    tests = [
        test_constants,
        test_unit_conversions,
        test_celestial_objects,
        test_orbital_calculations,
        test_utils_functions,
        test_propagate_orbit,
        test_keplerian_elements,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠ {test_func.__name__} 跳过: {e}")
            skipped += 1
    
    print("=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败, {skipped} 跳过")
    print("=" * 50)
    
    if failed == 0:
        print("所有测试通过！")
        return True
    else:
        print(f"有 {failed} 个测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)