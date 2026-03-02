import pygfx as gfx
import numpy as np
import pylinalg as la
from . import propagate_orbit


def main():
    """简单的轨道可视化示例"""
    # 调用 Rust 核心计算轨道
    r0 = [1.0e11, 0.0, 0.0]  # 初始位置（单位：米）
    v0 = [0.0, 30000.0, 0.0]  # 初始速度
    epoch = 0.0  # 起始时间
    step = 3600.0  # 1小时步长
    num_steps = 1000

    positions = propagate_orbit(r0, v0, epoch, step, num_steps)

    # 设置 pygfx 场景
    renderer = gfx.renderers.WgpuRenderer()
    scene = gfx.Scene()

    # 创建轨道点云
    points = gfx.Points(
        gfx.Geometry(positions=positions),
        gfx.PointsMaterial(color=(0.8, 0.8, 0.8), size=1.0)
    )
    scene.add(points)

    # 添加中心星体
    sun = gfx.Mesh(
        gfx.sphere_geometry(radius=1.0e9),
        gfx.MeshPhongMaterial(color=(1.0, 0.8, 0.2))
    )
    scene.add(sun)

    # 设置相机
    camera = gfx.PerspectiveCamera(45, 16 / 9)
    camera.show_object(scene, scale=3)

    # 动画循环
    controller = gfx.OrbitController(camera, register_events=renderer)

    for _ in range(num_steps):
        renderer.render(scene, camera)
        renderer.flush()


if __name__ == "__main__":
    main()