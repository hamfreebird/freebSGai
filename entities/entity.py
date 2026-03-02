"""
实体定义模块
包含大质量圆形物体（Entity）和无大小点对象（Object）
"""
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any
import uuid


@dataclass
class Entity:
    """大质量圆形实体，具有质量、密度、半径、位置和速度"""
    mass: float  # 质量 (kg)
    density: float  # 密度 (kg/m^3)
    radius: float  # 半径 (m)
    position: np.ndarray  # 2D位置 (x, y) (m)
    velocity: np.ndarray  # 2D速度 (vx, vy) (m/s)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    color: Tuple[int, int, int] = (255, 255, 255)  # 显示颜色
    name: str = ""  # 实体名称
    
    def __post_init__(self):
        # 确保numpy数组是float类型
        self.position = np.array(self.position, dtype=np.float64)
        self.velocity = np.array(self.velocity, dtype=np.float64)
        
        # 如果半径未提供，根据质量和密度计算
        if self.radius <= 0:
            self.radius = self.calculate_radius()
    
    def calculate_radius(self) -> float:
        """根据质量和密度计算半径"""
        # 体积 V = m / ρ
        # 球体体积 V = (4/3)πr³
        volume = self.mass / self.density
        radius = (3 * volume / (4 * np.pi)) ** (1/3)
        return radius
    
    def calculate_mass(self) -> float:
        """根据密度和半径计算质量"""
        volume = (4/3) * np.pi * self.radius ** 3
        return self.density * volume
    
    def get_momentum(self) -> np.ndarray:
        """获取动量 p = m * v"""
        return self.mass * self.velocity
    
    def get_kinetic_energy(self) -> float:
        """获取动能 KE = 0.5 * m * v²"""
        v_squared = np.dot(self.velocity, self.velocity)
        return 0.5 * self.mass * v_squared
    
    def distance_to(self, other: 'Entity') -> float:
        """计算到另一个实体的距离"""
        return np.linalg.norm(self.position - other.position)
    
    def copy(self) -> 'Entity':
        """创建实体的副本（生成新的ID）"""
        import uuid
        return Entity(
            id=str(uuid.uuid4()),  # 生成新的UUID
            mass=self.mass,
            density=self.density,
            radius=self.radius,
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            color=self.color,
            name=self.name + " (copy)"
        )


@dataclass
class Object:
    """无大小点对象，具有位置、速度、属性和机动能力"""
    position: np.ndarray  # 2D位置 (x, y) (m)
    velocity: np.ndarray  # 2D速度 (vx, vy) (m/s)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""  # 标签
    attributes: Dict[str, Any] = field(default_factory=dict)  # 属性字典
    
    # 物理属性
    health: float = 100.0  # 生命值
    max_acceleration: float = 10.0  # 最大加速度 (m/s²)
    remaining_dv: float = 1000.0  # 剩余速度变化量 (m/s)
    throttle_depth: float = 0.0  # 发动机节流深度 (0-1)
    throttle_precision: float = 1.0  # 节流精度 (0-1)
    
    # 武器属性
    weapon_range: float = 1000.0  # 武器射程 (m)
    weapon_damage: float = 10.0  # 武器伤害
    weapon_cooldown: float = 1.0  # 武器冷却时间 (s)
    
    # 内部状态
    _last_throttle_change: float = 0.0  # 上次节流变化时间
    _is_throttling: bool = False  # 是否正在机动
    
    def __post_init__(self):
        self.position = np.array(self.position, dtype=np.float64)
        self.velocity = np.array(self.velocity, dtype=np.float64)
        
        # 初始化默认属性
        if 'max_health' not in self.attributes:
            self.attributes['max_health'] = self.health
        if 'engine_efficiency' not in self.attributes:
            self.attributes['engine_efficiency'] = 0.8
        if 'fuel_mass' not in self.attributes:
            self.attributes['fuel_mass'] = 100.0
    
    def set_throttle(self, depth: float, precision: float = None):
        """设置发动机节流"""
        self.throttle_depth = max(0.0, min(1.0, depth))
        if precision is not None:
            self.throttle_precision = max(0.0, min(1.0, precision))
        self._is_throttling = self.throttle_depth > 0.0
    
    def apply_thrust(self, direction: np.ndarray, dt: float) -> Tuple[np.ndarray, float]:
        """
        应用推力，返回速度增量和消耗的dv
        
        Args:
            direction: 推力方向 (单位向量)
            dt: 时间间隔 (s)
            
        Returns:
            (delta_v, dv_used): 速度增量 (m/s) 和消耗的dv (m/s)
        """
        if not self._is_throttling or self.remaining_dv <= 0:
            return np.zeros(2), 0.0
        
        # 计算可用加速度
        available_acc = self.max_acceleration * self.throttle_depth
        
        # 考虑节流精度
        if self.throttle_precision < 1.0:
            # 添加随机误差
            error_angle = np.random.uniform(-np.pi, np.pi) * (1 - self.throttle_precision)
            error_rot = np.array([
                [np.cos(error_angle), -np.sin(error_angle)],
                [np.sin(error_angle), np.cos(error_angle)]
            ])
            direction = error_rot @ direction
        
        # 归一化方向
        if np.linalg.norm(direction) > 0:
            direction = direction / np.linalg.norm(direction)
        else:
            direction = np.array([1.0, 0.0])
        
        # 计算速度增量
        delta_v = available_acc * dt * direction
        
        # 计算消耗的dv
        dv_used = np.linalg.norm(delta_v)
        
        # 如果剩余dv不足，按比例缩放
        if dv_used > self.remaining_dv:
            scale = self.remaining_dv / dv_used
            delta_v *= scale
            dv_used = self.remaining_dv
        
        # 更新剩余dv
        self.remaining_dv -= dv_used
        
        return delta_v, dv_used
    
    def update_position(self, acceleration: np.ndarray, dt: float):
        """更新位置和速度（基于加速度）"""
        # v = v0 + a * dt
        self.velocity += acceleration * dt
        # x = x0 + v * dt + 0.5 * a * dt²
        self.position += self.velocity * dt + 0.5 * acceleration * dt ** 2
    
    def take_damage(self, damage: float):
        """承受伤害"""
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def is_alive(self) -> bool:
        """检查对象是否存活"""
        return self.health > 0
    
    def distance_to(self, other: 'Object') -> float:
        """计算到另一个对象的距离"""
        return np.linalg.norm(self.position - other.position)
    
    def distance_to_entity(self, entity: Entity) -> float:
        """计算到实体的距离"""
        return np.linalg.norm(self.position - entity.position)
    
    def copy(self) -> 'Object':
        """创建对象的副本（生成新的ID）"""
        import uuid
        return Object(
            id=str(uuid.uuid4()),  # 生成新的UUID
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            label=self.label,
            attributes=self.attributes.copy(),
            health=self.health,
            max_acceleration=self.max_acceleration,
            remaining_dv=self.remaining_dv,
            throttle_depth=self.throttle_depth,
            throttle_precision=self.throttle_precision,
            weapon_range=self.weapon_range,
            weapon_damage=self.weapon_damage,
            weapon_cooldown=self.weapon_cooldown
        )