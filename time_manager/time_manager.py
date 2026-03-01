"""
时间管理和参考系系统
处理模拟时刻、时间倍速、参考系切换
"""
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
from entities.entity import Entity, Object


@dataclass
class TimeManager:
    """时间管理器，控制模拟时间和时间倍速"""
    current_time: float = 0.0  # 当前模拟时间 (s)
    time_step: float = 1.0  # 物理更新的最小间隔 (s)
    time_scale: float = 1.0  # 时间倍速 (1.0 = 实时)
    max_time_scale: float = 1000.0  # 最大时间倍速
    min_time_scale: float = 0.001  # 最小时间倍速
    is_paused: bool = False  # 是否暂停
    frame_rate: float = 60.0  # 画面帧率 (Hz)
    simulation_boundary: float = 1e6  # 模拟范围 (m)
    
    # 历史记录
    time_history: List[float] = field(default_factory=list)
    scale_history: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        # 初始化历史记录
        self.time_history.append(self.current_time)
        self.scale_history.append(self.time_scale)
    
    def update(self, dt: float = None):
        """
        更新时间
        
        Args:
            dt: 实际经过的时间 (s)，如果为None则使用time_step * time_scale
        """
        if self.is_paused:
            return
        
        if dt is None:
            # 根据时间倍速计算模拟时间增量
            dt = self.time_step * self.time_scale
        
        self.current_time += dt
        self.time_history.append(self.current_time)
    
    def set_time_scale(self, scale: float):
        """设置时间倍速"""
        self.time_scale = max(self.min_time_scale, min(self.max_time_scale, scale))
        self.scale_history.append(self.time_scale)
    
    def increase_time_scale(self, factor: float = 2.0):
        """增加时间倍速"""
        self.set_time_scale(self.time_scale * factor)
    
    def decrease_time_scale(self, factor: float = 2.0):
        """减少时间倍速"""
        self.set_time_scale(self.time_scale / factor)
    
    def pause(self):
        """暂停模拟"""
        self.is_paused = True
    
    def resume(self):
        """恢复模拟"""
        self.is_paused = False
    
    def toggle_pause(self):
        """切换暂停状态"""
        self.is_paused = not self.is_paused
    
    def get_effective_dt(self) -> float:
        """获取有效的物理更新时间步长"""
        return self.time_step
    
    def get_render_dt(self) -> float:
        """获取渲染时间步长"""
        return 1.0 / self.frame_rate
    
    def get_simulation_speed(self) -> float:
        """获取模拟速度（模拟时间/实际时间）"""
        return self.time_scale
    
    def is_object_out_of_bounds(self, obj: Object) -> bool:
        """检查对象是否超出模拟范围"""
        distance = np.linalg.norm(obj.position)
        return distance > self.simulation_boundary
    
    def is_entity_out_of_bounds(self, entity: Entity) -> bool:
        """检查实体是否超出模拟范围"""
        distance = np.linalg.norm(entity.position)
        return distance > self.simulation_boundary
    
    def get_time_info(self) -> Dict[str, Any]:
        """获取时间信息"""
        return {
            'current_time': self.current_time,
            'time_step': self.time_step,
            'time_scale': self.time_scale,
            'is_paused': self.is_paused,
            'frame_rate': self.frame_rate,
            'simulation_boundary': self.simulation_boundary,
            'effective_dt': self.get_effective_dt(),
            'render_dt': self.get_render_dt()
        }


@dataclass
class ReferenceFrame:
    """参考系定义"""
    id: str
    name: str
    position: np.ndarray  # 参考系原点位置 (m)
    velocity: np.ndarray  # 参考系速度 (m/s)
    rotation: float = 0.0  # 旋转角度 (rad)
    angular_velocity: float = 0.0  # 角速度 (rad/s)
    is_inertial: bool = True  # 是否为惯性参考系
    
    def __post_init__(self):
        self.position = np.array(self.position, dtype=np.float64)
        self.velocity = np.array(self.velocity, dtype=np.float64)
    
    def transform_position(self, global_position: np.ndarray) -> np.ndarray:
        """将全局位置转换到参考系局部位置"""
        # 平移
        local_pos = global_position - self.position
        
        # 旋转
        if self.rotation != 0:
            cos_theta = np.cos(-self.rotation)
            sin_theta = np.sin(-self.rotation)
            rotation_matrix = np.array([
                [cos_theta, -sin_theta],
                [sin_theta, cos_theta]
            ])
            local_pos = rotation_matrix @ local_pos
        
        return local_pos
    
    def transform_velocity(self, global_velocity: np.ndarray) -> np.ndarray:
        """将全局速度转换到参考系局部速度"""
        # 减去参考系速度
        local_vel = global_velocity - self.velocity
        
        # 旋转
        if self.rotation != 0:
            cos_theta = np.cos(-self.rotation)
            sin_theta = np.sin(-self.rotation)
            rotation_matrix = np.array([
                [cos_theta, -sin_theta],
                [sin_theta, cos_theta]
            ])
            local_vel = rotation_matrix @ local_vel
        
        return local_vel
    
    def inverse_transform_position(self, local_position: np.ndarray) -> np.ndarray:
        """将局部位置转换回全局位置"""
        # 逆旋转
        if self.rotation != 0:
            cos_theta = np.cos(self.rotation)
            sin_theta = np.sin(self.rotation)
            rotation_matrix = np.array([
                [cos_theta, -sin_theta],
                [sin_theta, cos_theta]
            ])
            local_position = rotation_matrix @ local_position
        
        # 平移
        global_pos = local_position + self.position
        
        return global_pos
    
    def inverse_transform_velocity(self, local_velocity: np.ndarray) -> np.ndarray:
        """将局部速度转换回全局速度"""
        # 逆旋转
        if self.rotation != 0:
            cos_theta = np.cos(self.rotation)
            sin_theta = np.sin(self.rotation)
            rotation_matrix = np.array([
                [cos_theta, -sin_theta],
                [sin_theta, cos_theta]
            ])
            local_velocity = rotation_matrix @ local_velocity
        
        # 加上参考系速度
        global_vel = local_velocity + self.velocity
        
        return global_vel
    
    def update(self, dt: float):
        """更新参考系状态"""
        # 更新位置
        self.position += self.velocity * dt
        
        # 更新旋转
        self.rotation += self.angular_velocity * dt
        # 归一化到 [0, 2π)
        self.rotation = self.rotation % (2 * np.pi)


class ReferenceFrameManager:
    """参考系管理器"""
    
    def __init__(self):
        self.frames: Dict[str, ReferenceFrame] = {}
        self.active_frame_id: Optional[str] = None
        
        # 创建默认参考系（全局惯性系）
        global_frame = ReferenceFrame(
            id="global",
            name="全局惯性系",
            position=np.zeros(2),
            velocity=np.zeros(2),
            is_inertial=True
        )
        self.add_frame(global_frame)
        self.set_active_frame("global")
    
    def add_frame(self, frame: ReferenceFrame):
        """添加参考系"""
        self.frames[frame.id] = frame
    
    def remove_frame(self, frame_id: str):
        """移除参考系"""
        if frame_id in self.frames and frame_id != "global":
            del self.frames[frame_id]
            if self.active_frame_id == frame_id:
                self.set_active_frame("global")
    
    def set_active_frame(self, frame_id: str):
        """设置活动参考系"""
        if frame_id in self.frames:
            self.active_frame_id = frame_id
    
    def get_active_frame(self) -> ReferenceFrame:
        """获取活动参考系"""
        return self.frames[self.active_frame_id]
    
    def create_entity_frame(self, entity: Entity, name: str = None) -> ReferenceFrame:
        """创建以实体为中心的参考系"""
        frame_id = f"entity_{entity.id}"
        frame_name = name or f"{entity.name}参考系"
        
        frame = ReferenceFrame(
            id=frame_id,
            name=frame_name,
            position=entity.position.copy(),
            velocity=entity.velocity.copy(),
            is_inertial=False  # 实体可能加速，所以是非惯性系
        )
        
        self.add_frame(frame)
        return frame
    
    def create_object_frame(self, obj: Object, name: str = None) -> ReferenceFrame:
        """创建以对象为中心的参考系"""
        frame_id = f"object_{obj.id}"
        frame_name = name or f"{obj.label}参考系"
        
        frame = ReferenceFrame(
            id=frame_id,
            name=frame_name,
            position=obj.position.copy(),
            velocity=obj.velocity.copy(),
            is_inertial=False
        )
        
        self.add_frame(frame)
        return frame
    
    def transform_to_active_frame(self, global_position: np.ndarray, 
                                 global_velocity: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """转换到活动参考系"""
        active_frame = self.get_active_frame()
        local_position = active_frame.transform_position(global_position)
        local_velocity = active_frame.transform_velocity(global_velocity)
        return local_position, local_velocity
    
    def transform_from_active_frame(self, local_position: np.ndarray,
                                   local_velocity: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """从活动参考系转换回全局"""
        active_frame = self.get_active_frame()
        global_position = active_frame.inverse_transform_position(local_position)
        global_velocity = active_frame.inverse_transform_velocity(local_velocity)
        return global_position, global_velocity
    
    def update_frames(self, dt: float):
        """更新所有参考系"""
        for frame in self.frames.values():
            frame.update(dt)
    
    def get_frame_info(self) -> Dict[str, Any]:
        """获取参考系信息"""
        active_frame = self.get_active_frame()
        return {
            'active_frame_id': self.active_frame_id,
            'active_frame_name': active_frame.name,
            'active_frame_position': active_frame.position.tolist(),
            'active_frame_velocity': active_frame.velocity.tolist(),
            'active_frame_rotation': active_frame.rotation,
            'is_inertial': active_frame.is_inertial,
            'total_frames': len(self.frames)
        }