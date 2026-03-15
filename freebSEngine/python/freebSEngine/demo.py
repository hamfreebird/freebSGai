"""freebSEngine 可视化演示模块

提供多种天体物理模拟的可视化演示。
"""

import pygfx as gfx
import numpy as np
import pylinalg as la
from typing import List, Optional
import time

from . import propagate_orbit, nbody_simulation, compute_keplerian_elements
from .celestial_objects import (
    SUN, EARTH, MARS, JUPITER, get_solar_system_bodies,
    CelestialBody, create_solar_system_simulation
)
from .utils import au_to_meters, meters_to_au


class OrbitVisualizer:
    """轨道可视化器"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        """
        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        self.width = width
        self.height = height
        
        # 创建渲染器
        self.renderer = gfx.renderers.WgpuRenderer(width=width, height=height)
        self.scene = gfx.Scene()
        self.camera = gfx.PerspectiveCamera(45, width / height)
        self.controller = gfx.OrbitController(self.camera, register_events=self.renderer)
        
        # 存储可视化对象
        self.orbit_traces = {}
        self.celestial_bodies = {}
        
        # 添加坐标轴
        self._add_coordinate_axes()
        
    def _add_coordinate_axes(self):
        """添加坐标轴"""
        # X轴 (红色)
        x_axis = gfx.Line(
            gfx.Geometry(positions=[[0, 0, 0], [1e12, 0, 0]]),
            gfx.LineMaterial(color=(1, 0, 0), thickness=2)
        )
        self.scene.add(x_axis)
        
        # Y轴 (绿色)
        y_axis = gfx.Line(
            gfx.Geometry(positions=[[0, 0, 0], [0, 1e12, 0]]),
            gfx.LineMaterial(color=(0, 1, 0), thickness=2)
        )
        self.scene.add(y_axis)
        
        # Z轴 (蓝色)
        z_axis = gfx.Line(
            gfx.Geometry(positions=[[0, 0, 0], [0, 0, 1e12]]),
            gfx.LineMaterial(color=(0, 0, 1), thickness=2)
        )
        self.scene.add(z_axis)
        
        # 坐标轴标签
        self._add_axis_labels()
    
    def _add_axis_labels(self):
        """添加坐标轴标签"""
        # 这里可以添加文本标签，但pygfx的文本支持有限
        # 暂时省略，可以使用标记点代替
        pass
    
    def add_celestial_body(self, body: CelestialBody, position: List[float], scale: float = 1.0):
        """添加天体
        
        Args:
            body: 天体对象
            position: 位置 [x, y, z]
            scale: 缩放因子（用于可视化）
        """
        # 计算可视化半径（对数缩放以适应不同大小）
        visual_radius = max(body.radius * scale, 1e6)  # 最小半径
        
        # 创建球体
        sphere = gfx.Mesh(
            gfx.sphere_geometry(radius=visual_radius),
            gfx.MeshPhongMaterial(color=body.color, shininess=30)
        )
        sphere.position.set(*position)
        
        self.scene.add(sphere)
        self.celestial_bodies[body.name] = {
            'mesh': sphere,
            'body': body,
            'position': position
        }
        
        # 添加标签
        self._add_body_label(body.name, position, visual_radius)
    
    def _add_body_label(self, name: str, position: List[float], radius: float):
        """添加天体标签（使用标记点）"""
        # 在球体上方添加一个标记点
        label_pos = [position[0], position[1] + radius * 1.5, position[2]]
        marker = gfx.Mesh(
            gfx.box_geometry(radius * 0.1, radius * 0.1, radius * 0.1),
            gfx.MeshBasicMaterial(color=(1, 1, 1))
        )
        marker.position.set(*label_pos)
        self.scene.add(marker)
    
    def add_orbit_trace(self, positions: np.ndarray, color: tuple = (0.8, 0.8, 0.8), name: str = "orbit"):
        """添加轨道轨迹
        
        Args:
            positions: 位置数组，形状为 (n, 3)
            color: 轨道颜色
            name: 轨道名称
        """
        # 创建线
        line = gfx.Line(
            gfx.Geometry(positions=positions),
            gfx.LineMaterial(color=color, thickness=1)
        )
        self.scene.add(line)
        
        self.orbit_traces[name] = line
        
        # 添加轨迹起点标记
        start_marker = gfx.Mesh(
            gfx.sphere_geometry(radius=positions[0].max() * 0.01),
            gfx.MeshBasicMaterial(color=color)
        )
        start_marker.position.set(*positions[0])
        self.scene.add(start_marker)
    
    def visualize_single_orbit(self, r0: List[float], v0: List[float], 
                               central_body: CelestialBody = SUN,
                               duration_days: float = 365.25,
                               steps_per_day: int = 10):
        """可视化单个轨道
        
        Args:
            r0: 初始位置 [x, y, z] (米)
            v0: 初始速度 [vx, vy, vz] (米/秒)
            central_body: 中心天体
            duration_days: 模拟天数
            steps_per_day: 每天步数
        """
        # 计算轨道
        step_seconds = 24 * 3600 / steps_per_day
        num_steps = int(duration_days * steps_per_day)
        
        print(f"计算轨道: {duration_days} 天, {num_steps} 步, 步长 {step_seconds} 秒")
        
        positions = propagate_orbit(r0, v0, 0.0, step_seconds, num_steps)
        
        # 添加中心天体
        self.add_celestial_body(central_body, [0, 0, 0], scale=0.1)
        
        # 添加轨道轨迹
        self.add_orbit_trace(positions, color=(0.2, 0.6, 1.0), name="orbit")
        
        # 计算轨道根数
        keplerian = compute_keplerian_elements(r0, v0, 0.0)
        print(f"轨道根数: 半长轴={keplerian[0]:.2e}m, 偏心率={keplerian[1]:.3f}")
        
        # 调整相机
        max_distance = np.max(np.linalg.norm(positions, axis=1))
        self.camera.show_pos([0, 0, 0], distance=max_distance * 2)
        
        return positions
    
    def visualize_solar_system(self, num_planets: int = 4, duration_years: float = 1.0):
        """可视化太阳系
        
        Args:
            num_planets: 显示的行星数量（从内到外）
            duration_years: 模拟年数
        """
        # 获取太阳系天体
        bodies = get_solar_system_bodies()
        
        # 添加太阳
        self.add_celestial_body(SUN, [0, 0, 0], scale=0.05)
        
        # 选择前几个行星
        planet_order = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
        selected_planets = planet_order[:num_planets]
        
        for planet_name in selected_planets:
            if planet_name in bodies:
                body = bodies[planet_name]
                if body.semi_major_axis is not None:
                    # 计算圆形轨道速度
                    orbital_velocity = np.sqrt(SUN.gravitational_parameter / body.semi_major_axis)
                    
                    # 初始条件
                    r0 = [body.semi_major_axis, 0.0, 0.0]
                    v0 = [0.0, orbital_velocity, 0.0]
                    
                    # 计算轨道
                    steps_per_year = 100
                    step_seconds = 365.25 * 24 * 3600 / steps_per_year
                    num_steps = int(duration_years * steps_per_year)
                    
                    positions = propagate_orbit(r0, v0, 0.0, step_seconds, num_steps)
                    
                    # 添加行星
                    self.add_celestial_body(body, r0, scale=5.0)
                    
                    # 添加轨道
                    color = body.color
                    self.add_orbit_trace(positions, color=color, name=planet_name)
        
        # 调整相机
        max_distance = bodies[selected_planets[-1]].semi_major_axis * 1.5
        self.camera.show_pos([0, 0, 0], distance=max_distance)
    
    def visualize_nbody_simulation(self, num_bodies: int = 3, steps: int = 500):
        """可视化N体模拟
        
        Args:
            num_bodies: 天体数量
            steps: 模拟步数
        """
        # 创建随机初始条件
        np.random.seed(42)
        
        positions = []
        velocities = []
        masses = []
        colors = []
        
        for i in range(num_bodies):
            # 随机位置（在1e11米范围内）
            pos = np.random.uniform(-1e11, 1e11, 3)
            positions.append(pos.tolist())
            
            # 随机速度
            vel = np.random.uniform(-10000, 10000, 3)
            velocities.append(vel.tolist())
            
            # 随机质量（地球质量量级）
            mass = np.random.uniform(0.1, 10.0) * 5.9722e24
            masses.append(mass)
            
            # 随机颜色
            color = np.random.uniform(0.3, 1.0, 3)
            colors.append(tuple(color))
        
        # 运行N体模拟
        print(f"运行 {num_bodies} 体模拟，{steps} 步...")
        start_time = time.time()
        all_positions = nbody_simulation(positions, velocities, masses, 0.0, 3600.0, steps)
        elapsed = time.time() - start_time
        print(f"模拟完成，耗时 {elapsed:.2f} 秒")
        
        # 重塑位置数组为 [body, step, coordinate]
        positions_by_body = np.transpose(all_positions, (1, 0, 2))
        
        # 添加天体和轨迹
        for i in range(num_bodies):
            # 创建虚拟天体
            body = CelestialBody(
                name=f"Body_{i}",
                mass=masses[i],
                radius=6.371e6 * (masses[i] / 5.9722e24) ** (1/3),
                color=colors[i]
            )
            
            # 添加初始位置的天体
            initial_pos = positions_by_body[i, 0]
            self.add_celestial_body(body, initial_pos.tolist(), scale=2.0)
            
            # 添加轨迹
            self.add_orbit_trace(positions_by_body[i], color=colors[i], name=f"body_{i}")
        
        # 调整相机
        all_positions_flat = all_positions.reshape(-1, 3)
        max_distance = np.max(np.linalg.norm(all_positions_flat, axis=1))
        self.camera.show_pos([0, 0, 0], distance=max_distance * 1.5)
        
        return all_positions
    
    def run(self, fps: int = 60, duration: float = 10.0):
        """运行可视化
        
        Args:
            fps: 帧率
            duration: 运行时间（秒）
        """
        print("开始可视化...")
        print("控制说明:")
        print("  - 鼠标左键拖拽: 旋转视角")
        print("  - 鼠标右键拖拽: 平移视角")
        print("  - 鼠标滚轮: 缩放")
        print("  - 按ESC键退出")
        
        num_frames = int(fps * duration)
        
        for frame in range(num_frames):
            # 更新场景（这里可以添加动画）
            self._update_animation(frame)
            
            # 渲染
            self.renderer.render(self.scene, self.camera)
            
            # 处理事件
            self.renderer.flush()
            
            # 简单帧率控制
            time.sleep(1.0 / fps)
        
        print("可视化结束")
    
    def _update_animation(self, frame: int):
        """更新动画（可以被子类重写）"""
        # 这里可以添加动态效果，比如旋转天体
        pass


def demo_single_orbit():
    """演示单个轨道"""
    print("=== 单个轨道演示 ===")
    
    visualizer = OrbitVisualizer()
    
    # 地球轨道参数
    r0 = [1.496e11, 0.0, 0.0]  # 1 AU
    v0 = [0.0, 29780.0, 0.0]   # 地球轨道速度
    
    visualizer.visualize_single_orbit(r0, v0, SUN, duration_days=365.25)
    visualizer.run(duration=15.0)


def demo_solar_system():
    """演示太阳系"""
    print("=== 太阳系演示 ===")
    
    visualizer = OrbitVisualizer()
    visualizer.visualize_solar_system(num_planets=4, duration_years=2.0)
    visualizer.run(duration=20.0)


def demo_nbody():
    """演示N体模拟"""
    print("=== N体模拟演示 ===")
    
    visualizer = OrbitVisualizer(width=1000, height=800)
    visualizer.visualize_nbody_simulation(num_bodies=3, steps=300)
    visualizer.run(duration=15.0)


def demo_comparison():
    """演示不同轨道类型的比较"""
    print("=== 轨道类型比较演示 ===")
    
    visualizer = OrbitVisualizer()
    
    # 添加太阳
    visualizer.add_celestial_body(SUN, [0, 0, 0], scale=0.05)
    
    # 圆形轨道（地球）
    r_circular = [1.496e11, 0.0, 0.0]
    v_circular = [0.0, 29780.0, 0.0]
    positions_circular = propagate_orbit(r_circular, v_circular, 0.0, 3600.0, 1000)
    visualizer.add_orbit_trace(positions_circular, color=(0.2, 0.6, 1.0), name="circular")
    
    # 椭圆轨道（彗星）
    r_elliptical = [1.496e11, 0.0, 0.0]
    v_elliptical = [0.0, 40000.0, 0.0]  # 更高速度
    positions_elliptical = propagate_orbit(r_elliptical, v_elliptical, 0.0, 3600.0, 2000)
    visualizer.add_orbit_trace(positions_elliptical, color=(0.8, 0.4, 0.2), name="elliptical")
    
    # 双曲线轨道（逃逸轨道）
    r_hyperbolic = [1.496e11, 0.0, 0.0]
    v_hyperbolic = [0.0, 50000.0, 0.0]  # 逃逸速度以上
    positions_hyperbolic = propagate_orbit(r_hyperbolic, v_hyperbolic, 0.0, 3600.0, 1500)
    visualizer.add_orbit_trace(positions_hyperbolic, color=(1.0, 0.3, 0.3), name="hyperbolic")
    
    visualizer.run(duration=15.0)


def interactive_demo():
    """交互式演示菜单"""
    print("=== freebSEngine 交互式演示 ===")
    print("请选择演示类型:")
    print("1. 单个轨道演示")
    print("2. 太阳系演示")
    print("3. N体模拟演示")
    print("4. 轨道类型比较")
    print("5. 退出")
    
    while True:
        try:
            choice = input("\n请输入选项 (1-5): ").strip()
            
            if choice == "1":
                demo_single_orbit()
            elif choice == "2":
                demo_solar_system()
            elif choice == "3":
                demo_nbody()
            elif choice == "4":
                demo_comparison()
            elif choice == "5":
                print("退出演示")
                break
            else:
                print("无效选项，请重新输入")
        except KeyboardInterrupt:
            print("\n用户中断")
            break
        except Exception as e:
            print(f"演示出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数 - 运行默认演示"""
    try:
        # 运行交互式演示
        interactive_demo()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所需依赖: pip install pygfx numpy pylinalg glfw")
    except Exception as e:
        print(f"演示运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()