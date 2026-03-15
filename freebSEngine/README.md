# freebSEngine

[![CI](https://github.com/yourusername/freebSEngine/actions/workflows/CI.yml/badge.svg)](https://github.com/yourusername/freebSEngine/actions/workflows/CI.yml)
[![PyPI version](https://img.shields.io/pypi/v/freebSEngine.svg)](https://pypi.org/project/freebSEngine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**freebSEngine** 是一个高性能的天体物理模拟引擎，采用 Rust + Python 混合架构，专门用于天体轨道计算和可视化。

## 特性

- 🚀 **高性能计算**: 使用 Rust 实现核心算法，接近 C/C++ 的性能
- 🐍 **易用接口**: 提供完整的 Python API，支持 NumPy 数组
- 🌌 **丰富功能**: 轨道传播、N体模拟、开普勒元素计算等
- 🎨 **现代可视化**: 基于 WebGPU 的 3D 可视化
- 📊 **科学准确**: 使用真实的天体物理数据和算法
- 🔧 **跨平台**: 支持 Windows、Linux、macOS

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install freebSEngine
```

### 从源码构建

1. 安装 Rust 工具链:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. 安装 maturin:
   ```bash
   pip install maturin
   ```

3. 构建并安装:
   ```bash
   cd freebSEngine
   maturin develop  # 开发模式
   # 或
   maturin build --release  # 构建发布版
   ```

## 快速开始

### 基本使用

```python
import freebSEngine as fse
import numpy as np

# 计算地球轨道
r0 = [1.496e11, 0.0, 0.0]  # 初始位置 (米)
v0 = [0.0, 29780.0, 0.0]   # 初始速度 (米/秒)

# 轨道传播
positions = fse.propagate_orbit(r0, v0, epoch=0.0, step_seconds=3600.0, num_steps=1000)
print(f"轨道位置形状: {positions.shape}")  # (1000, 3)

# 计算开普勒元素
elements = fse.compute_keplerian_elements(r0, v0, epoch=0.0)
print(f"半长轴: {elements[0]:.2e} m")
print(f"偏心率: {elements[1]:.3f}")

# 使用工具函数
from freebSEngine.utils import au_to_meters, meters_to_au
distance_au = 1.0
distance_m = au_to_meters(distance_au)
print(f"{distance_au} AU = {distance_m:.2e} m")
```

### 可视化演示

```python
from freebSEngine.demo import interactive_demo

# 运行交互式演示
interactive_demo()
```

## 核心功能

### 1. 轨道计算

```python
import freebSEngine as fse

# 轨道传播
positions = fse.propagate_orbit(r0, v0, epoch, step_seconds, num_steps)

# 轨道周期计算
period = fse.orbital_period(semi_major_axis, gravitational_parameter)

# 圆形轨道速度
velocity = fse.circular_orbit_velocity(radius, central_mass)

# 逃逸速度
escape_vel = fse.escape_velocity(radius, central_mass)
```

### 2. N体模拟

```python
# 创建多体系统
positions = [[1.0e11, 0, 0], [2.0e11, 0, 0]]
velocities = [[0, 30000, 0], [0, 25000, 0]]
masses = [5.9722e24, 1.8982e27]  # 地球和木星质量

# 运行N体模拟
all_positions = fse.nbody_simulation(
    positions, velocities, masses,
    epoch=0.0, dt=3600.0, steps=1000
)
```

### 3. 天体对象

```python
from freebSEngine.celestial_objects import SUN, EARTH, MARS, get_body

# 使用预定义天体
print(f"太阳质量: {SUN.mass:.2e} kg")
print(f"地球半径: {EARTH.radius:.2e} m")
print(f"火星表面重力: {MARS.surface_gravity:.2f} m/s²")

# 获取天体对象
body = get_body("jupiter")
print(f"木星逃逸速度: {body.escape_velocity:.2f} m/s")
```

### 4. 工具函数

```python
from freebSEngine.utils import (
    au_to_meters, meters_to_au,
    solar_mass_to_kg, kg_to_solar_mass,
    orbital_elements_to_cartesian,
    vis_viva_equation,
)

# 单位转换
distance_m = au_to_meters(1.5)  # 1.5 AU 转换为米
mass_kg = solar_mass_to_kg(0.5)  # 0.5 太阳质量转换为千克

# 轨道计算
position, velocity = orbital_elements_to_cartesian(
    a=1.496e11, e=0.0167, i=0.0, raan=0.0, argp=0.0, nu=0.0,
    mu=SUN.gravitational_parameter
)
```

## 可视化

freebSEngine 提供基于 pygfx (WebGPU) 的 3D 可视化:

```python
from freebSEngine.demo import OrbitVisualizer

# 创建可视化器
visualizer = OrbitVisualizer(width=1200, height=800)

# 添加太阳系
visualizer.visualize_solar_system(num_planets=4)

# 运行可视化
visualizer.run(duration=20.0)
```

## API 文档

### 主要函数

#### `propagate_orbit(r0, v0, epoch, step_seconds, num_steps)`
计算天体轨道位置。

**参数:**
- `r0`: 初始位置向量 [x, y, z] (米)
- `v0`: 初始速度向量 [vx, vy, vz] (米/秒)
- `epoch`: 起始时间 (Unix 时间戳)
- `step_seconds`: 时间步长 (秒)
- `num_steps`: 步数

**返回:** NumPy 数组，形状为 (num_steps, 3)

#### `compute_keplerian_elements(r, v, epoch)`
计算开普勒轨道根数。

**返回:** [a, e, i, Ω, ω, ν] 数组
- a: 半长轴 (米)
- e: 偏心率
- i: 倾角 (度)
- Ω: 升交点赤经 (度)
- ω: 近地点幅角 (度)
- ν: 真近点角 (度)

#### `nbody_simulation(positions, velocities, masses, epoch, dt, steps)`
运行 N 体模拟。

**参数:**
- `positions`: 初始位置列表
- `velocities`: 初始速度列表
- `masses`: 质量列表
- `epoch`: 起始时间
- `dt`: 时间步长
- `steps`: 步数

**返回:** NumPy 数组，形状为 (steps, n_bodies, 3)

### 常量

- `GRAVITATIONAL_CONSTANT`: 引力常数 (6.67430e-11 m³/kg/s²)
- `SPEED_OF_LIGHT`: 光速 (299792458 m/s)
- `ASTRONOMICAL_UNIT`: 天文单位 (1.495978707e11 m)
- `SOLAR_MASS`: 太阳质量 (1.98847e30 kg)
- `EARTH_MASS`: 地球质量 (5.9722e24 kg)

## 开发

### 项目结构

```
freebSEngine/
├── Cargo.toml          # Rust 项目配置
├── pyproject.toml      # Python 项目配置
├── src/
│   └── lib.rs          # Rust 核心库
├── python/
│   └── freebSEngine/
│       ├── __init__.py # Python 包入口
│       ├── demo.py     # 可视化演示
│       ├── utils.py    # 工具函数
│       └── celestial_objects.py  # 天体对象
├── tests/              # 测试文件
└── .github/workflows/  # CI/CD 配置
```

### 运行测试

```bash
# 运行 Python 测试
cd freebSEngine
python -m pytest tests/

# 运行 Rust 测试
cargo test
```

### 构建发布

```bash
# 构建轮子
maturin build --release

# 发布到 PyPI
maturin publish
```

## 示例

查看 `examples/` 目录获取更多使用示例:

1. **地球轨道模拟**: 计算和可视化地球绕太阳的轨道
2. **太阳系模拟**: 完整的太阳系行星运动
3. **N体问题**: 多天体引力相互作用模拟
4. **轨道转移**: 霍曼转移轨道计算

## 依赖

### 必需依赖
- Rust ≥ 1.70
- Python ≥ 3.8
- maturin ≥ 1.0

### Python 依赖
- numpy ≥ 1.21
- pygfx ≥ 0.3.0 (用于可视化)
- pylinalg ≥ 0.2
- glfw ≥ 2.5

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 引用

如果您在科研中使用 freebSEngine，请引用:

```bibtex
@software{freebSEngine2026,
  title = {freebSEngine: High-performance astrophysics simulation engine},
  author = {freebSEngine Team},
  year = {2026},
  url = {https://github.com/yourusername/freebSEngine},
  version = {0.1.0}
}
```

## 支持

- 📖 [文档](https://freebSEngine.readthedocs.io/)
- 🐛 [问题追踪](https://github.com/yourusername/freebSEngine/issues)
- 💬 [讨论区](https://github.com/yourusername/freebSEngine/discussions)

## 致谢

感谢以下开源项目:
- [PyO3](https://pyo3.rs/) - Rust-Python 绑定
- [astrora](https://github.com/astrora/astrora) - 天体力学库
- [pygfx](https://pygfx.github.io/) - WebGPU 图形库
- [maturin](https://www.maturin.rs/) - Rust-Python 包构建工具