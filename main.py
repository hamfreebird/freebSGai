"""
2D宇宙太空战游戏物理模拟 - 主程序示例
"""
import numpy as np
import time as real_time

from physics.simulation import UniverseSimulation, SimulationConfig
from utils.helpers import create_star, create_planet, create_spaceship, create_asteroid
from entities.entity import Object, Entity


def demo_basic_simulation():
    """演示基本模拟"""
    print("=== 2D宇宙太空战物理模拟演示 ===")
    
    # 创建模拟配置
    config = SimulationConfig(
        time_step=60.0,  # 1分钟步长
        max_time_scale=100.0,
        simulation_boundary=1e12,  # 1万亿米
        screen_width=1920,
        screen_height=1080
    )
    
    # 创建模拟引擎
    sim = UniverseSimulation(config)
    
    # 创建天体
    print("创建天体中...")
    star = create_star(name="太阳")
    planet = create_planet(name="地球")
    asteroid = create_asteroid(name="小行星带")
    
    sim.add_entity(star)
    sim.add_entity(planet)
    sim.add_entity(asteroid)
    
    # 创建飞船
    print("创建飞船中...")
    spaceship = create_spaceship(label="探索者号")
    sim.add_object(spaceship)
    
    # 设置相机跟随飞船
    sim.set_camera_to_object(spaceship.id)
    
    # 运行模拟
    print("\n开始模拟...")
    print("时间倍速: 10x")
    sim.set_time_scale(10.0)
    
    for i in range(10):
        result = sim.update(apply_thrust=False)
        
        print(f"\n更新 {i+1}:")
        print(f"  模拟时间: {result['timestamp']/3600:.2f} 小时")
        print(f"  对象数量: {result['objects_count']}")
        print(f"  实体数量: {result['entities_count']}")
        
        if result['event_flags']['collision_detected']:
            print("  ⚠️ 检测到碰撞!")
        
        # 获取飞船状态
        ship_state = sim.get_object_state(spaceship.id)
        if ship_state:
            pos = ship_state['position']
            vel = np.linalg.norm(ship_state['velocity'])
            print(f"  飞船位置: ({pos[0]/1e11:.2f}, {pos[1]/1e11:.2f}) x10^11 m")
            print(f"  飞船速度: {vel/1000:.2f} km/s")
    
    # 执行观测
    print("\n执行观测...")
    observation = sim.observe()
    print(f"可见对象: {observation['visible_objects']}/{observation['total_objects']}")
    print(f"可见实体: {observation['visible_entities']}/{observation['total_entities']}")
    
    # 预测轨道
    print("\n预测飞船轨道...")
    orbit = sim.predict_orbit(spaceship.id, steps=100)
    if orbit:
        print(f"轨道预测完成，共 {len(orbit)} 个点")
    
    # 获取模拟状态
    state = sim.get_simulation_state()
    print(f"\n模拟统计:")
    print(f"  总更新次数: {state['stats']['total_updates']}")
    print(f"  总碰撞次数: {state['stats']['total_collisions']}")
    print(f"  平均更新时间: {state['stats']['average_update_time']*1000:.2f} ms")
    
    return sim


def demo_thrust_maneuver():
    """演示推力机动"""
    print("\n=== 推力机动演示 ===")
    
    config = SimulationConfig(time_step=1.0)
    sim = UniverseSimulation(config)
    
    # 创建简单场景
    star = create_star(position=(0, 0), name="恒星")
    sim.add_entity(star)
    
    # 创建飞船
    ship = Object(
        position=np.array([1e11, 0]),
        velocity=np.array([0, 30000]),
        label="机动飞船",
        attributes={'mass': 1000.0},
        max_acceleration=5.0,
        remaining_dv=1000.0
    )
    sim.add_object(ship)
    
    print("初始状态:")
    state = sim.get_object_state(ship.id)
    if state:
        print(f"  位置: ({state['position'][0]/1e11:.2f}, {state['position'][1]/1e11:.2f}) x10^11 m")
        print(f"  速度: {np.linalg.norm(state['velocity'])/1000:.2f} km/s")
        print(f"  剩余dv: {state['remaining_dv']:.1f} m/s")
    
    # 设置推力
    print("\n启动发动机...")
    ship.set_throttle(0.5)  # 50%节流
    
    # 执行机动
    for i in range(5):
        result = sim.update(apply_thrust=True)
        
        if result['event_flags']['thrust_applied']:
            print(f"更新 {i+1}: 推力已应用")
        
        state = sim.get_object_state(ship.id)
        if state:
            print(f"  剩余dv: {state['remaining_dv']:.1f} m/s")
            print(f"  速度: {np.linalg.norm(state['velocity'])/1000:.2f} km/s")
    
    print("\n机动完成")


def demo_collision_merging():
    """演示碰撞合并"""
    print("\n=== 碰撞合并演示 ===")
    
    config = SimulationConfig(time_step=3600.0)  # 1小时步长
    sim = UniverseSimulation(config)
    
    # 创建两个相向运动的小行星
    asteroid1 = create_asteroid(
        position=(1e10, 0),
        velocity=(-1000, 0),
        mass=1e12,
        name="小行星A"
    )
    
    asteroid2 = create_asteroid(
        position=(-1e10, 0),
        velocity=(1000, 0),
        mass=1e12,
        name="小行星B"
    )
    
    sim.add_entity(asteroid1)
    sim.add_entity(asteroid2)
    
    print(f"初始实体数量: {len(sim.entities)}")
    print(f"小行星A质量: {asteroid1.mass:.2e} kg")
    print(f"小行星B质量: {asteroid2.mass:.2e} kg")
    
    # 运行模拟直到碰撞
    max_steps = 20
    for i in range(max_steps):
        result = sim.update(apply_thrust=False)
        
        if result['event_flags']['entity_merged']:
            print(f"\n步骤 {i+1}: 检测到实体合并!")
            print(f"碰撞统计: {result['collision_stats']}")
            break
    
    print(f"\n最终实体数量: {len(sim.entities)}")
    if sim.entities:
        merged = sim.entities[0]
        print(f"合并后实体质量: {merged.mass:.2e} kg")
        print(f"合并后实体半径: {merged.radius:.2e} m")


def demo_reference_frames():
    """演示参考系切换"""
    print("\n=== 参考系演示 ===")
    
    config = SimulationConfig()
    sim = UniverseSimulation(config)
    
    # 创建场景
    star = create_star(name="恒星")
    planet = create_planet(name="行星")
    sim.add_entity(star)
    sim.add_entity(planet)
    
    # 创建飞船
    ship = create_spaceship(label="观测飞船")
    sim.add_object(ship)
    
    # 获取全局参考系状态
    state = sim.get_simulation_state()
    print(f"当前参考系: {state['frames']['active_frame_name']}")
    
    # 切换到行星参考系
    print("\n切换到行星参考系...")
    sim.create_entity_frame(planet.id)
    sim.set_active_frame(f"entity_{planet.id}")
    
    state = sim.get_simulation_state()
    print(f"当前参考系: {state['frames']['active_frame_name']}")
    print(f"参考系位置: {state['frames']['active_frame_position']}")
    
    # 获取飞船在行星参考系中的状态
    ship_state = sim.get_object_state(ship.id)
    if ship_state:
        print(f"飞船相对位置: {ship_state['position']}")
        print(f"飞船相对速度: {ship_state['velocity']}")
    
    # 切换回全局参考系
    print("\n切换回全局参考系...")
    sim.set_active_frame("global")
    
    state = sim.get_simulation_state()
    print(f"当前参考系: {state['frames']['active_frame_name']}")


def demo_observation_delay():
    """演示观测延迟"""
    print("\n=== 光速延迟观测演示 ===")
    
    config = SimulationConfig(time_step=1.0)
    sim = UniverseSimulation(config)
    
    # 创建远距离目标
    distant_star = Entity(
        mass=2e30,
        density=1408,
        radius=7e8,
        position=np.array([1e16, 0]),  # 1光年 ≈ 9.46e15 m
        velocity=np.zeros(2),
        name="遥远恒星"
    )
    
    sim.add_entity(distant_star)
    
    # 创建观测者（相机在原点）
    sim.observer.set_camera(np.zeros(2))
    
    # 执行观测
    observation = sim.observe()
    
    if observation['entities']:
        entity_obs = observation['entities'][0]
        light_time = entity_obs['light_travel_time']
        
        print(f"目标距离: {np.linalg.norm(distant_star.position):.2e} m")
        print(f"光传播时间: {light_time:.2f} 秒")
        print(f"光传播距离: {light_time / 3600:.2f} 小时")
        print(f"观测时间比实际时间延迟: {light_time:.2f} 秒")
        
        # 计算光年
        light_year = 9.461e15  # 米
        distance_ly = np.linalg.norm(distant_star.position) / light_year
        print(f"距离: {distance_ly:.2f} 光年")


def performance_test():
    """性能测试"""
    print("\n=== 性能测试 ===")
    
    config = SimulationConfig(
        time_step=60.0,
        max_objects=500,
        max_entities=50
    )
    
    sim = UniverseSimulation(config)
    
    # 创建大量对象和实体
    print("创建测试场景...")
    for i in range(100):
        # 创建随机位置的小行星
        angle = np.random.uniform(0, 2*np.pi)
        distance = np.random.uniform(1e10, 1e11)
        x = distance * np.cos(angle)
        y = distance * np.sin(angle)
        
        asteroid = create_asteroid(
            position=(x, y),
            velocity=(np.random.uniform(-1000, 1000), 
                     np.random.uniform(-1000, 1000)),
            mass=np.random.uniform(1e10, 1e12)
        )
        sim.add_entity(asteroid)
    
    for i in range(50):
        # 创建随机位置的飞船
        angle = np.random.uniform(0, 2*np.pi)
        distance = np.random.uniform(1e10, 5e10)
        x = distance * np.cos(angle)
        y = distance * np.sin(angle)
        
        ship = Object(
            position=np.array([x, y]),
            velocity=np.array([np.random.uniform(-5000, 5000),
                             np.random.uniform(-5000, 5000)]),
            label=f"飞船_{i}",
            attributes={'mass': 1000.0}
        )
        sim.add_object(ship)
    
    print(f"场景创建完成: {len(sim.entities)} 个实体, {len(sim.objects)} 个对象")
    
    # 运行性能测试
    print("\n运行性能测试 (100次更新)...")
    start_time = real_time.time()
    
    for i in range(100):
        sim.update(apply_thrust=False)
        
        if (i + 1) % 20 == 0:
            elapsed = real_time.time() - start_time
            print(f"  完成 {i+1}/100 次更新, 用时 {elapsed:.2f} 秒")
    
    total_time = real_time.time() - start_time
    state = sim.get_simulation_state()
    
    print(f"\n性能测试完成:")
    print(f"  总时间: {total_time:.2f} 秒")
    print(f"  平均更新时间: {state['stats']['average_update_time']*1000:.2f} ms")
    print(f"  总碰撞次数: {state['stats']['total_collisions']}")
    print(f"  每秒更新次数: {100/total_time:.2f} Hz")


def main():
    """主函数"""
    print("2D宇宙太空战游戏物理模拟系统")
    print("=" * 50)
    
    try:
        # 运行各个演示
        sim = demo_basic_simulation()
        demo_thrust_maneuver()
        demo_collision_merging()
        demo_reference_frames()
        demo_observation_delay()
        
        # 性能测试（可选，可能需要较长时间）
        run_perf_test = False
        if run_perf_test:
            performance_test()
        
        print("\n" + "=" * 50)
        print("所有演示完成!")
        print("\nAPI接口已就绪，可用于后续游戏开发:")
        print("1. UniverseSimulation - 主模拟引擎")
        print("2. Entity/Object - 实体和对象类")
        print("3. 物理计算模块 (gravity, motion, collision)")
        print("4. 时间管理和参考系系统")
        print("5. 观测模块 (光速延迟、视线阻挡)")
        print("6. 工具函数和辅助类")
        
    except Exception as e:
        print(f"运行演示时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()