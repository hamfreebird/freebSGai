"""
观测模块
处理光速延迟、视线阻挡、屏幕坐标转换
"""
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
from entities.entity import Entity, Object
from physics.collision import check_object_entity_collision


C = 299792458.0  # 光速 (m/s)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


@dataclass
class ObservationRecord:
    """观测记录"""
    timestamp: float  # 记录时间 (s)
    position: np.ndarray  # 位置 (m)
    velocity: np.ndarray  # 速度 (m/s)
    is_visible: bool  # 是否可见
    
    def __post_init__(self):
        self.position = np.array(self.position, dtype=np.float64)
        self.velocity = np.array(self.velocity, dtype=np.float64)


@dataclass
class ObjectObservation:
    """对象观测数据"""
    object_id: str
    records: List[ObservationRecord] = field(default_factory=list)
    max_history: int = 1000  # 最大历史记录数
    
    def add_record(self, record: ObservationRecord):
        """添加观测记录"""
        self.records.append(record)
        # 保持历史记录不超过最大值
        if len(self.records) > self.max_history:
            self.records = self.records[-self.max_history:]
    
    def get_record_at_time(self, timestamp: float) -> Optional[ObservationRecord]:
        """获取指定时间的观测记录（最近的一个）"""
        if not self.records:
            return None
        
        # 找到时间最接近的记录
        closest_record = min(self.records, key=lambda r: abs(r.timestamp - timestamp))
        return closest_record
    
    def get_latest_record(self) -> Optional[ObservationRecord]:
        """获取最新的观测记录"""
        if not self.records:
            return None
        return self.records[-1]


@dataclass
class EntityObservation:
    """实体观测数据"""
    entity_id: str
    records: List[ObservationRecord] = field(default_factory=list)
    max_history: int = 1000
    
    def add_record(self, record: ObservationRecord):
        """添加观测记录"""
        self.records.append(record)
        if len(self.records) > self.max_history:
            self.records = self.records[-self.max_history:]
    
    def get_record_at_time(self, timestamp: float) -> Optional[ObservationRecord]:
        """获取指定时间的观测记录"""
        if not self.records:
            return None
        
        closest_record = min(self.records, key=lambda r: abs(r.timestamp - timestamp))
        return closest_record
    
    def get_latest_record(self) -> Optional[ObservationRecord]:
        """获取最新的观测记录"""
        if not self.records:
            return None
        return self.records[-1]


class Observer:
    """观测器"""
    
    def __init__(self, camera_position: np.ndarray = None, 
                 camera_velocity: np.ndarray = None,
                 screen_width: int = SCREEN_WIDTH,
                 screen_height: int = SCREEN_HEIGHT):
        # 相机（观测者）状态
        self.camera_position = camera_position if camera_position is not None else np.zeros(2)
        self.camera_velocity = camera_velocity if camera_velocity is not None else np.zeros(2)
        
        # 屏幕参数
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pixels_per_meter = 0.01  # 默认缩放比例
        
        # 观测数据存储
        self.object_observations: Dict[str, ObjectObservation] = {}
        self.entity_observations: Dict[str, EntityObservation] = {}
        
        # 视线阻挡检查
        self.occlusion_check_enabled = True
        
    def set_camera(self, position: np.ndarray, velocity: np.ndarray = None):
        """设置相机位置和速度"""
        self.camera_position = np.array(position, dtype=np.float64)
        if velocity is not None:
            self.camera_velocity = np.array(velocity, dtype=np.float64)
    
    def set_zoom(self, pixels_per_meter: float):
        """设置缩放比例（像素/米）"""
        self.pixels_per_meter = max(0.001, pixels_per_meter)
    
    def calculate_light_travel_time(self, target_position: np.ndarray) -> float:
        """
        计算光从目标到相机的传播时间
        
        Args:
            target_position: 目标位置 (m)
            
        Returns:
            光传播时间 (s)
        """
        distance = np.linalg.norm(target_position - self.camera_position)
        return distance / C
    
    def check_line_of_sight(self, target_position: np.ndarray, 
                           entities: List[Entity]) -> bool:
        """
        检查视线是否被实体阻挡
        
        Args:
            target_position: 目标位置
            entities: 可能阻挡的实体列表
            
        Returns:
            视线是否畅通
        """
        if not self.occlusion_check_enabled:
            return True
        
        camera_pos = self.camera_position
        target_pos = target_position
        
        # 检查每个实体是否在视线路径上
        for entity in entities:
            # 计算点到直线的距离
            line_vec = target_pos - camera_pos
            line_len = np.linalg.norm(line_vec)
            
            if line_len == 0:
                continue
            
            line_dir = line_vec / line_len
            
            # 实体中心到直线的向量
            entity_to_camera = entity.position - camera_pos
            projection = np.dot(entity_to_camera, line_dir)
            
            # 如果投影在线段外，跳过
            if projection < 0 or projection > line_len:
                continue
            
            # 计算垂足
            closest_point = camera_pos + projection * line_dir
            
            # 计算距离
            distance = np.linalg.norm(entity.position - closest_point)
            
            # 如果距离小于实体半径，则视线被阻挡
            if distance < entity.radius:
                return False
        
        return True
    
    def observe_object(self, obj: Object, current_time: float, 
                      entities: List[Entity]) -> Dict[str, Any]:
        """
        观测对象
        
        Args:
            obj: 对象
            current_time: 当前模拟时间
            entities: 实体列表（用于视线检查）
            
        Returns:
            观测结果
        """
        # 计算光传播时间
        light_time = self.calculate_light_travel_time(obj.position)
        
        # 计算观测时间
        observation_time = current_time - light_time
        
        # 检查视线
        is_visible = self.check_line_of_sight(obj.position, entities)
        
        # 创建观测记录
        record = ObservationRecord(
            timestamp=observation_time,
            position=obj.position.copy(),
            velocity=obj.velocity.copy(),
            is_visible=is_visible
        )
        
        # 存储观测数据
        if obj.id not in self.object_observations:
            self.object_observations[obj.id] = ObjectObservation(obj.id)
        
        self.object_observations[obj.id].add_record(record)
        
        # 计算屏幕坐标
        screen_pos = self.world_to_screen(obj.position, observation_time)
        
        return {
            'object_id': obj.id,
            'observation_time': observation_time,
            'light_travel_time': light_time,
            'is_visible': is_visible,
            'world_position': obj.position.tolist(),
            'screen_position': screen_pos,
            'velocity': obj.velocity.tolist(),
            'health': obj.health if is_visible else None,
            'attributes': obj.attributes if is_visible else {}
        }
    
    def observe_entity(self, entity: Entity, current_time: float,
                      entities: List[Entity]) -> Dict[str, Any]:
        """
        观测实体
        
        Args:
            entity: 实体
            current_time: 当前模拟时间
            entities: 其他实体列表（用于视线检查）
            
        Returns:
            观测结果
        """
        # 计算光传播时间
        light_time = self.calculate_light_travel_time(entity.position)
        
        # 计算观测时间
        observation_time = current_time - light_time
        
        # 检查视线（排除自身）
        other_entities = [e for e in entities if e.id != entity.id]
        is_visible = self.check_line_of_sight(entity.position, other_entities)
        
        # 创建观测记录
        record = ObservationRecord(
            timestamp=observation_time,
            position=entity.position.copy(),
            velocity=entity.velocity.copy(),
            is_visible=is_visible
        )
        
        # 存储观测数据
        if entity.id not in self.entity_observations:
            self.entity_observations[entity.id] = EntityObservation(entity.id)
        
        self.entity_observations[entity.id].add_record(record)
        
        # 计算屏幕坐标
        screen_pos = self.world_to_screen(entity.position, observation_time)
        
        return {
            'entity_id': entity.id,
            'observation_time': observation_time,
            'light_travel_time': light_time,
            'is_visible': is_visible,
            'world_position': entity.position.tolist(),
            'screen_position': screen_pos,
            'velocity': entity.velocity.tolist(),
            'mass': entity.mass if is_visible else None,
            'radius': entity.radius if is_visible else None,
            'color': entity.color if is_visible else (128, 128, 128)
        }
    
    def world_to_screen(self, world_position: np.ndarray, 
                       observation_time: float) -> Tuple[int, int]:
        """
        将世界坐标转换为屏幕坐标
        
        Args:
            world_position: 世界坐标 (m)
            observation_time: 观测时间（用于补偿相机运动）
            
        Returns:
            屏幕坐标 (x, y)
        """
        # 计算相对位置（考虑相机位置）
        relative_pos = world_position - self.camera_position
        
        # 转换为像素坐标
        pixel_x = relative_pos[0] * self.pixels_per_meter
        pixel_y = relative_pos[1] * self.pixels_per_meter
        
        # 转换为屏幕坐标（原点在屏幕中心）
        screen_x = int(self.screen_width / 2 + pixel_x)
        screen_y = int(self.screen_height / 2 - pixel_y)  # Y轴反向
        
        # 确保在屏幕范围内
        screen_x = max(0, min(self.screen_width - 1, screen_x))
        screen_y = max(0, min(self.screen_height - 1, screen_y))
        
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> np.ndarray:
        """
        将屏幕坐标转换为世界坐标
        
        Args:
            screen_x: 屏幕X坐标
            screen_y: 屏幕Y坐标
            
        Returns:
            世界坐标 (m)
        """
        # 转换为相对于屏幕中心的像素坐标
        pixel_x = screen_x - self.screen_width / 2
        pixel_y = self.screen_height / 2 - screen_y  # Y轴反向
        
        # 转换为世界坐标
        world_x = pixel_x / self.pixels_per_meter
        world_y = pixel_y / self.pixels_per_meter
        
        # 加上相机位置
        world_position = np.array([world_x, world_y]) + self.camera_position
        
        return world_position
    
    def observe_all(self, objects: List[Object], entities: List[Entity],
                   current_time: float) -> Dict[str, Any]:
        """
        观测所有对象和实体
        
        Args:
            objects: 对象列表
            entities: 实体列表
            current_time: 当前模拟时间
            
        Returns:
            所有观测结果
        """
        object_observations = []
        entity_observations = []
        
        # 观测所有对象
        for obj in objects:
            obs = self.observe_object(obj, current_time, entities)
            object_observations.append(obs)
        
        # 观测所有实体
        for entity in entities:
            obs = self.observe_entity(entity, current_time, entities)
            entity_observations.append(obs)
        
        return {
            'timestamp': current_time,
            'camera_position': self.camera_position.tolist(),
            'camera_velocity': self.camera_velocity.tolist(),
            'objects': object_observations,
            'entities': entity_observations,
            'total_objects': len(object_observations),
            'total_entities': len(entity_observations),
            'visible_objects': sum(1 for obs in object_observations if obs['is_visible']),
            'visible_entities': sum(1 for obs in entity_observations if obs['is_visible'])
        }
    
    def get_object_history(self, object_id: str, 
                          start_time: float = None, 
                          end_time: float = None) -> List[ObservationRecord]:
        """获取对象的历史观测记录"""
        if object_id not in self.object_observations:
            return []
        
        obs = self.object_observations[object_id]
        records = obs.records
        
        # 时间过滤
        if start_time is not None:
            records = [r for r in records if r.timestamp >= start_time]
        if end_time is not None:
            records = [r for r in records if r.timestamp <= end_time]
        
        return records
    
    def get_entity_history(self, entity_id: str,
                          start_time: float = None,
                          end_time: float = None) -> List[ObservationRecord]:
        """获取实体的历史观测记录"""
        if entity_id not in self.entity_observations:
            return []
        
        obs = self.entity_observations[entity_id]
        records = obs.records
        
        # 时间过滤
        if start_time is not None:
            records = [r for r in records if r.timestamp >= start_time]
        if end_time is not None:
            records = [r for r in records if r.timestamp <= end_time]
        
        return records
    
    def clear_history(self):
        """清空所有观测历史"""
        self.object_observations.clear()
        self.entity_observations.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取观测统计信息"""
        total_object_records = sum(len(obs.records) for obs in self.object_observations.values())
        total_entity_records = sum(len(obs.records) for obs in self.entity_observations.values())
        
        return {
            'total_objects_observed': len(self.object_observations),
            'total_entities_observed': len(self.entity_observations),
            'total_object_records': total_object_records,
            'total_entity_records': total_entity_records,
            'occlusion_check_enabled': self.occlusion_check_enabled,
            'pixels_per_meter': self.pixels_per_meter,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height
        }