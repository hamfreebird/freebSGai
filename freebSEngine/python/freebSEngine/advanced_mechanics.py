"""高级轨道力学模块

提供高级轨道力学计算功能，包括轨道转移、摄动分析、轨道优化等。
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from .celestial_objects import CelestialBody, SUN, EARTH
from .utils import (
    au_to_meters, meters_to_au, 
    vis_viva_equation, calculate_gravitational_parameter,
    orbital_elements_to_cartesian,
)


@dataclass
class OrbitalManeuver:
    """轨道机动"""
    name: str
    delta_v: float  # Δv (m/s)
    duration: float  # 持续时间 (s)
    fuel_mass: float  # 燃料质量 (kg)
    
    @property
    def impulse(self) -> float:
        """冲量 (N·s)"""
        return self.delta_v * self.fuel_mass


@dataclass
class OrbitalTransfer:
    """轨道转移"""
    initial_orbit: Dict[str, float]  # 初始轨道参数
    final_orbit: Dict[str, float]    # 目标轨道参数
    maneuvers: List[OrbitalManeuver]  # 机动序列
    total_delta_v: float  # 总Δv (m/s)
    transfer_time: float  # 转移时间 (s)
    
    @property
    def efficiency(self) -> float:
        """转移效率（Δv/理论最小Δv）"""
        # 简化计算
        return 1.0 / (1.0 + 0.1 * len(self.maneuvers))


class AdvancedOrbitalMechanics:
    """高级轨道力学计算器"""
    
    def __init__(self, central_body: CelestialBody = SUN):
        """
        Args:
            central_body: 中心天体
        """
        self.central_body = central_body
        self.mu = central_body.gravitational_parameter
    
    def hohmann_transfer(self, r1: float, r2: float) -> Dict[str, float]:
        """计算霍曼转移轨道参数
        
        Args:
            r1: 初始轨道半径 (m)
            r2: 目标轨道半径 (m)
            
        Returns:
            包含转移参数的字典
        """
        # 确保 r2 > r1
        if r2 < r1:
            r1, r2 = r2, r1
        
        # 转移椭圆半长轴
        a_transfer = (r1 + r2) / 2.0
        
        # 第一次加速 Δv1
        v1_circular = np.sqrt(self.mu / r1)
        v1_transfer = np.sqrt(self.mu * (2/r1 - 1/a_transfer))
        delta_v1 = v1_transfer - v1_circular
        
        # 第二次加速 Δv2
        v2_circular = np.sqrt(self.mu / r2)
        v2_transfer = np.sqrt(self.mu * (2/r2 - 1/a_transfer))
        delta_v2 = v2_circular - v2_transfer
        
        # 总 Δv
        total_delta_v = abs(delta_v1) + abs(delta_v2)
        
        # 转移时间（半椭圆周期）
        transfer_time = np.pi * np.sqrt(a_transfer**3 / self.mu)
        
        return {
            'delta_v1': delta_v1,
            'delta_v2': delta_v2,
            'total_delta_v': total_delta_v,
            'transfer_time': transfer_time,
            'transfer_semi_major_axis': a_transfer,
            'eccentricity': (r2 - r1) / (r2 + r1),
        }
    
    def bielliptic_transfer(self, r1: float, r2: float, rb: float) -> Dict[str, float]:
        """计算双椭圆转移轨道参数
        
        Args:
            r1: 初始轨道半径 (m)
            r2: 目标轨道半径 (m)
            rb: 中间轨道半径 (rb > r2 > r1)
            
        Returns:
            包含转移参数的字典
        """
        # 第一次转移（r1 -> rb）
        transfer1 = self.hohmann_transfer(r1, rb)
        
        # 第二次转移（rb -> r2）
        transfer2 = self.hohmann_transfer(rb, r2)
        
        total_delta_v = transfer1['total_delta_v'] + transfer2['total_delta_v']
        total_time = transfer1['transfer_time'] + transfer2['transfer_time']
        
        return {
            'delta_v1': transfer1['delta_v1'],
            'delta_v2': transfer1['delta_v2'] + transfer2['delta_v1'],
            'delta_v3': transfer2['delta_v2'],
            'total_delta_v': total_delta_v,
            'total_time': total_time,
            'intermediate_radius': rb,
        }
    
    def orbital_rendezvous(self, 
                          chaser_orbit: Dict[str, float],
                          target_orbit: Dict[str, float],
                          phase_angle: float = 0.0) -> Dict[str, float]:
        """计算轨道交会参数
        
        Args:
            chaser_orbit: 追踪器轨道参数
            target_orbit: 目标器轨道参数
            phase_angle: 初始相位角 (度)
            
        Returns:
            包含交会参数的字典
        """
        # 简化计算：同平面圆轨道交会
        r_chaser = chaser_orbit.get('semi_major_axis', chaser_orbit.get('radius', 1.0))
        r_target = target_orbit.get('semi_major_axis', target_orbit.get('radius', 1.0))
        
        # 角速度
        omega_chaser = np.sqrt(self.mu / r_chaser**3)
        omega_target = np.sqrt(self.mu / r_target**3)
        
        # 相对角速度
        delta_omega = omega_target - omega_chaser
        
        # 相位角（弧度）
        phase_rad = np.deg2rad(phase_angle)
        
        # 交会时间（相位闭合时间）
        if abs(delta_omega) > 1e-10:
            rendezvous_time = (2*np.pi - phase_rad) / abs(delta_omega)
        else:
            rendezvous_time = float('inf')
        
        # 所需 Δv（简化）
        delta_v = 0.1 * abs(omega_target - omega_chaser) * (r_target + r_chaser) / 2
        
        return {
            'rendezvous_time': rendezvous_time,
            'required_delta_v': delta_v,
            'relative_angular_velocity': delta_omega,
            'phase_closure_rate': abs(delta_omega) / (2*np.pi),
        }
    
    def calculate_orbital_perturbations(self,
                                       orbit: Dict[str, float],
                                       perturbations: List[str] = None) -> Dict[str, float]:
        """计算轨道摄动
        
        Args:
            orbit: 轨道参数
            perturbations: 摄动类型列表，可选 ['J2', 'drag', 'solar_radiation', 'third_body']
            
        Returns:
            包含摄动参数的字典
        """
        if perturbations is None:
            perturbations = ['J2', 'drag']
        
        results = {}
        
        # 轨道参数
        a = orbit.get('semi_major_axis', 1.0)
        e = orbit.get('eccentricity', 0.0)
        i = np.deg2rad(orbit.get('inclination', 0.0))
        
        # J2 摄动（地球扁率）
        if 'J2' in perturbations and self.central_body.name.lower() == 'earth':
            J2 = 1.08262668e-3  # 地球 J2 系数
            R = self.central_body.radius
            
            # 升交点赤经变化率
            raan_dot = -1.5 * J2 * R**2 * np.sqrt(self.mu) * np.cos(i) / (a**3.5 * (1 - e**2)**2)
            
            # 近地点幅角变化率
            argp_dot = 1.5 * J2 * R**2 * np.sqrt(self.mu) * (2 - 2.5 * np.sin(i)**2) / (a**3.5 * (1 - e**2)**2)
            
            results['J2_raan_dot'] = np.rad2deg(raan_dot)  # 度/秒
            results['J2_argp_dot'] = np.rad2deg(argp_dot)  # 度/秒
        
        # 大气阻力摄动
        if 'drag' in perturbations:
            # 简化的大气阻力模型
            Cd = 2.2  # 阻力系数
            A = 10.0  # 横截面积 (m²)
            m = 1000.0  # 质量 (kg)
            rho = 1e-12  # 大气密度 (kg/m³)，在轨道高度
            
            v = np.sqrt(self.mu / a)  # 近似速度
            drag_acceleration = 0.5 * Cd * A * rho * v**2 / m
            
            # 半长轴衰减率
            da_dt = -2 * a**2 * drag_acceleration / np.sqrt(self.mu * a)
            
            results['drag_acceleration'] = drag_acceleration
            results['semi_major_axis_decay'] = da_dt
        
        # 太阳辐射压
        if 'solar_radiation' in perturbations:
            # 简化太阳辐射压模型
            P_solar = 4.56e-6  # 太阳辐射压 (N/m²)
            Cr = 1.2  # 反射系数
            A = 10.0  # 横截面积 (m²)
            m = 1000.0  # 质量 (kg)
            
            srp_acceleration = Cr * P_solar * A / m
            results['solar_radiation_acceleration'] = srp_acceleration
        
        return results
    
    def optimize_orbit(self,
                      initial_orbit: Dict[str, float],
                      constraints: Dict[str, Tuple[float, float]],
                      objective: str = 'fuel') -> Dict[str, float]:
        """优化轨道参数
        
        Args:
            initial_orbit: 初始轨道参数
            constraints: 约束条件，格式为 {参数: (最小值, 最大值)}
            objective: 优化目标，'fuel'（燃料最小）或 'time'（时间最小）
            
        Returns:
            优化后的轨道参数
        """
        # 简化优化：梯度下降的简化版本
        optimized = initial_orbit.copy()
        
        if objective == 'fuel':
            # 燃料优化：倾向于使用霍曼转移
            if 'eccentricity' in constraints:
                e_min, e_max = constraints['eccentricity']
                optimized['eccentricity'] = max(e_min, min(0.1, e_max))  # 偏好低偏心率
        
        elif objective == 'time':
            # 时间优化：倾向于使用高能量转移
            if 'eccentricity' in constraints:
                e_min, e_max = constraints['eccentricity']
                optimized['eccentricity'] = max(e_min, min(0.3, e_max))  # 可接受较高偏心率
        
        # 确保在约束范围内
        for param, (min_val, max_val) in constraints.items():
            if param in optimized:
                optimized[param] = max(min_val, min(optimized[param], max_val))
        
        return optimized
    
    def calculate_launch_window(self,
                               launch_site_lat: float,
                               launch_site_lon: float,
                               target_inclination: float,
                               launch_date: Optional[str] = None) -> Dict[str, float]:
        """计算发射窗口
        
        Args:
            launch_site_lat: 发射场纬度 (度)
            launch_site_lon: 发射场经度 (度)
            target_inclination: 目标轨道倾角 (度)
            launch_date: 发射日期（YYYY-MM-DD），可选
            
        Returns:
            包含发射窗口参数的字典
        """
        # 简化计算
        launch_lat_rad = np.deg2rad(launch_site_lat)
        target_inc_rad = np.deg2rad(target_inclination)
        
        # 发射方位角
        cos_azimuth = np.cos(target_inc_rad) / np.cos(launch_lat_rad)
        cos_azimuth = np.clip(cos_azimuth, -1, 1)
        
        azimuth1 = np.rad2deg(np.arccos(cos_azimuth))
        azimuth2 = 360 - azimuth1
        
        # 发射窗口时间（简化：每天两次机会）
        window_duration = 1200.0  # 秒
        daily_windows = 2
        
        return {
            'azimuth_1': azimuth1,
            'azimuth_2': azimuth2,
            'window_duration': window_duration,
            'daily_windows': daily_windows,
            'max_inclination': np.rad2deg(np.arccos(np.cos(launch_lat_rad))),  # 最小倾角
        }
    
    def analyze_orbit_stability(self,
                               orbit: Dict[str, float],
                               duration_years: float = 10.0) -> Dict[str, float]:
        """分析轨道稳定性
        
        Args:
            orbit: 轨道参数
            duration_years: 分析时长 (年)
            
        Returns:
            包含稳定性参数的字典
        """
        a = orbit.get('semi_major_axis', 1.0)
        e = orbit.get('eccentricity', 0.0)
        i = orbit.get('inclination', 0.0)
        
        # 稳定性指标（简化）
        stability_score = 100.0
        
        # 半长轴稳定性
        if a < self.central_body.radius * 1.1:
            stability_score -= 30  # 太低，可能再入
        elif a > self.central_body.radius * 10:
            stability_score -= 10  # 太高，可能逃逸
        
        # 偏心率稳定性
        if e > 0.9:
            stability_score -= 40  # 高偏心率不稳定
        elif e > 0.5:
            stability_score -= 20
        
        # 倾角稳定性（对地球同步轨道等特殊轨道）
        if 60 < i < 120:
            stability_score += 10  # 极轨道相对稳定
        
        # 摄动影响
        perturbations = self.calculate_orbital_perturbations(orbit)
        if 'J2_raan_dot' in perturbations:
            raan_dot = abs(perturbations['J2_raan_dot'])
            if raan_dot > 10:  # 度/天
                stability_score -= raan_dot / 2
        
        return {
            'stability_score': max(0, min(100, stability_score)),
            'estimated_lifetime': duration_years * (stability_score / 100),
            'major_risks': self._identify_orbit_risks(orbit),
        }
    
    def _identify_orbit_risks(self, orbit: Dict[str, float]) -> List[str]:
        """识别轨道风险"""
        risks = []
        
        a = orbit.get('semi_major_axis', 1.0)
        e = orbit.get('eccentricity', 0.0)
        i = orbit.get('inclination', 0.0)
        
        # 碰撞风险
        if a < self.central_body.radius * 1.2:
            risks.append("大气阻力导致轨道衰减")
        
        if e > 0.9:
            risks.append("高偏心率导致近地点过低")
        
        # 共振风险（简化）
        if abs(i - 63.4) < 5:  # 莫尔尼亚轨道倾角
            risks.append("临界倾角可能导致轨道不稳定")
        
        return risks


def demo_advanced_mechanics():
    """演示高级轨道力学功能"""
    print("=== 高级轨道力学演示 ===")
    
    # 创建计算器
    mechanics = AdvancedOrbitalMechanics(EARTH)
    
    # 霍曼转移示例
    print("\n1. 霍曼转移计算:")
    r1 = EARTH.radius + 400e3  # 400 km 低轨道
    r2 = EARTH.radius + 35786e3  # 地球同步轨道
    hohmann = mechanics.hohmann_transfer(r1, r2)
    
    print(f"  初始轨道半径: {meters_to_au(r1):.6f} AU ({r1/1000:.0f} km)")
    print(f"  目标轨道半径: {meters_to_au(r2):.6f} AU ({r2/1000:.0f} km)")
    print(f"  第一次 Δv: {hohmann['delta_v1']/1000:.2f} km/s")
    print(f"  第二次 Δv: {hohmann['delta_v2']/1000:.2f} km/s")
    print(f"  总 Δv: {hohmann['total_delta_v']/1000:.2f} km/s")
    print(f"  转移时间: {hohmann['transfer_time']/3600:.1f} 小时")
    
    # 轨道摄动分析
    print("\n2. 轨道摄动分析:")
    orbit = {
        'semi_major_axis': EARTH.radius + 500e3,
        'eccentricity': 0.01,
        'inclination': 45.0,
    }
    perturbations = mechanics.calculate_orbital_perturbations(orbit)
    
    for key, value in perturbations.items():
        if 'dot' in key:
            print(f"  {key}: {value:.6f} 度/秒")
        else:
            print(f"  {key}: {value:.6e}")
    
    # 轨道稳定性分析
    print("\n3. 轨道稳定性分析:")
    stability = mechanics.analyze_orbit_stability(orbit)
    print(f"  稳定性评分: {stability['stability_score']:.1f}/100")
    print(f"  预计寿命: {stability['estimated_lifetime']:.1f} 年")
    print(f"  主要风险: {', '.join(stability['major_risks'])}")
    
    # 发射窗口计算
    print("\n4. 发射窗口计算:")
    launch_window = mechanics.calculate_launch_window(
        launch_site_lat=28.5,  # 卡纳维拉尔角纬度
        launch_site_lon=-80.5,  # 卡纳维拉尔角经度
        target_inclination=28.5,  # 国际空间站倾角
    )
    print(f"  发射方位角1: {launch_window['azimuth_1']:.1f}°")
    print(f"  发射方位角2: {launch_window['azimuth_2']:.1f}°")
    print(f"  窗口持续时间: {launch_window['window_duration']/60:.0f} 分钟")
    print(f"  每天窗口数: {launch_window['daily_windows']}")
    
    print("\n演示完成！")


if __name__ == "__main__":
    demo_advanced_mechanics()