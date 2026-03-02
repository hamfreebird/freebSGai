"""
物理模拟引擎
整合所有模块，提供完整的API接口
"""
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
import time as real_time

from entities.entity import Entity, Object
from physics.gravity import calculate_total_force_on_object, predict_orbit, calculate_orbital_parameters
from physics.motion import update_entities, update_objects, calculate_trajectory
from physics.collision import process_all_collisions, find_all_collisions
from time_manager.time_manager import TimeManager, ReferenceFrameManager
from observation.observer import Observer


@dataclass
class SimulationConfig:
    """模拟配置"""
    # 物理参数
    time_step: float = 1.0  # 物理更新步长 (s)
    max_time_scale: float = 1000.0  # 最大时间倍速
    simulation_boundary: float = 1e6  # 模拟范围 (m)
    
    # 性能参数
    max_objects: int = 1000  # 最大对象数量
    max_entities: int = 100  # 最大实体数量
    history_size: int = 1000  # 历史记录大小
    
    # 渲染参数
    screen_width: int = 1920
    screen_height: int = 1080
    pixels_per_meter: float = 0.01
    
    # 物理常数
    gravitational_constant: float = 6.67430e-11  # G


class UniverseSimulation:
    """宇宙模拟引擎"""
    
    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        
        # 初始化管理器
        self.time_manager = TimeManager(
            time_step=self.config.time_step,
            max_time_scale=self.config.max_time_scale,
            simulation_boundary=self.config.simulation_boundary
        )
        
        self.frame_manager = ReferenceFrameManager()
        self.observer = Observer(
            screen_width=self.config.screen_width,
            screen_height=self.config.screen_height
        )
        self.observer.set_zoom(self.config.pixels_per_meter)
        
        # 模拟状态
        self.objects: List[Object] = []
        self.entities: List[Entity] = []
        
        # 历史记录
        self.object_history: Dict[str, List[Dict[str, Any]]] = {}
        self.entity_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # 性能统计
        self.stats = {
            'total_updates': 0,
            'total_collisions': 0,
            'objects_created': 0,
            'entities_created': 0,
            'objects_destroyed': 0,
            'entities_destroyed': 0,
            'total_simulation_time': 0.0,
            'average_update_time': 0.0
        }
        
        # 事件标志
        self.event_flags = {
            'collision_detected': False,
            'object_destroyed': False,
            'entity_merged': False,
            'out_of_bounds': False,
            'thrust_applied': False
        }
        
        # 性能优化
        self._last_update_time = real_time.time()
        self._update_times = []
    
    def add_object(self, obj: Object) -> bool:
        """添加对象到模拟"""
        if len(self.objects) >= self.config.max_objects:
            return False
        
        self.objects.append(obj)
        self.stats['objects_created'] += 1
        self.object_history[obj.id] = []
        return True
    
    def add_entity(self, entity: Entity) -> bool:
        """添加实体到模拟"""
        if len(self.entities) >= self.config.max_entities:
            return False
        
        self.entities.append(entity)
        self.stats['entities_created'] += 1
        self.entity_history[entity.id] = []
        return True
    
    def remove_object(self, object_id: str) -> bool:
        """移除对象"""
        for i, obj in enumerate(self.objects):
            if obj.id == object_id:
                self.objects.pop(i)
                self.stats['objects_destroyed'] += 1
                if object_id in self.object_history:
                    del self.object_history[object_id]
                return True
        return False
    
    def remove_entity(self, entity_id: str) -> bool:
        """移除实体"""
        for i, entity in enumerate(self.entities):
            if entity.id == entity_id:
                self.entities.pop(i)
                self.stats['entities_destroyed'] += 1
                if entity_id in self.entity_history:
                    del self.entity_history[entity_id]
                return True
        return False
    
    def get_object(self, object_id: str) -> Optional[Object]:
        """获取对象"""
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None
    
    def update(self, apply_thrust: bool = True) -> Dict[str, Any]:
        """
        执行一次模拟更新
        
        Args:
            apply_thrust: 是否应用推力（机动）
            
        Returns:
            更新结果
        """
        start_time = real_time.time()
        
        # 重置事件标志
        self._reset_event_flags()
        
        # 更新时间
        self.time_manager.update()
        current_time = self.time_manager.current_time
        
        # 更新参考系
        self.frame_manager.update_frames(self.time_manager.get_effective_dt())
        
        # 更新实体位置（基于引力）
        self.entities = update_entities(self.entities, self.time_manager.get_effective_dt())
        
        # 更新对象位置（基于引力和可能的推力）
        self.objects, thrust_infos = update_objects(
            self.objects, self.entities, 
            self.time_manager.get_effective_dt(),
            apply_thrust=apply_thrust
        )
        
        # 检查并处理推力事件
        if any(info['thrust_applied'] for info in thrust_infos):
            self.event_flags['thrust_applied'] = True
        
        # 处理碰撞（暂时禁用，因为天文距离下不应该有碰撞）
        # self.objects, self.entities, collision_stats = process_all_collisions(
        #     self.objects, self.entities
        # )
        
        # 创建空的碰撞统计
        collision_stats = {
            'total_collisions': 0,
            'object_entity_collisions': 0,
            'entity_entity_collisions': 0,
            'object_object_collisions': 0,
            'objects_destroyed': 0,
            'entities_merged': 0,
            'objects_remaining': len(self.objects),
            'entities_remaining': len(self.entities)
        }
        
        # 更新碰撞事件标志
        if collision_stats['total_collisions'] > 0:
            self.event_flags['collision_detected'] = True
        if collision_stats['objects_destroyed'] > 0:
            self.event_flags['object_destroyed'] = True
        if collision_stats['entities_merged'] > 0:
            self.event_flags['entity_merged'] = True
        
        # 检查边界
        self._check_boundaries()
        
        # 记录历史
        self._record_history(current_time)
        
        # 更新统计
        self.stats['total_updates'] += 1
        self.stats['total_collisions'] += collision_stats['total_collisions']
        self.stats['total_simulation_time'] = current_time
        
        # 计算性能
        update_time = real_time.time() - start_time
        self._update_times.append(update_time)
        if len(self._update_times) > 100:
            self._update_times.pop(0)
        
        self.stats['average_update_time'] = np.mean(self._update_times) if self._update_times else 0
        
        # 返回更新结果
        return {
            'timestamp': current_time,
            'objects_count': len(self.objects),
            'entities_count': len(self.entities),
            'collision_stats': collision_stats,
            'thrust_infos': thrust_infos,
            'event_flags': self.event_flags.copy(),
            'performance': {
                'update_time': update_time,
                'average_update_time': self.stats['average_update_time']
            }
        }
    
    def update_multiple(self, steps: int, apply_thrust: bool = True) -> List[Dict[str, Any]]:
        """
        执行多次模拟更新
        
        Args:
            steps: 更新步数
            apply_thrust: 是否应用推力
            
        Returns:
            每次更新的结果列表
        """
        results = []
        for _ in range(steps):
            result = self.update(apply_thrust)
            results.append(result)
        return results
    
    def observe(self) -> Dict[str, Any]:
        """执行观测"""
        current_time = self.time_manager.current_time
        observation = self.observer.observe_all(self.objects, self.entities, current_time)
        return observation
    
    def predict_orbit(self, object_id: str, steps: int = 1000) -> List[np.ndarray]:
        """预测对象轨道"""
        obj = self.get_object(object_id)
        if not obj:
            return []
        
        return predict_orbit(obj, self.entities, self.time_manager.get_effective_dt(), steps)
    
    def calculate_trajectory(self, object_id: str, total_time: float) -> List[np.ndarray]:
        """计算对象轨迹"""
        obj = self.get_object(object_id)
        if not obj:
            return []
        
        return calculate_trajectory(obj, self.entities, total_time, self.time_manager.get_effective_dt())
    
    def get_orbital_parameters(self, object_id: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """计算对象相对于实体的轨道参数"""
        obj = self.get_object(object_id)
        entity = self.get_entity(entity_id)
        
        if not obj or not entity:
            return None
        
        return calculate_orbital_parameters(obj, entity)
    
    def set_time_scale(self, scale: float):
        """设置时间倍速"""
        self.time_manager.set_time_scale(scale)
    
    def set_active_frame(self, frame_id: str):
        """设置活动参考系"""
        self.frame_manager.set_active_frame(frame_id)
    
    def create_entity_frame(self, entity_id: str) -> Optional[str]:
        """创建以实体为中心的参考系"""
        entity = self.get_entity(entity_id)
        if not entity:
            return None
        
        frame = self.frame_manager.create_entity_frame(entity)
        return frame.id
    
    def create_object_frame(self, object_id: str) -> Optional[str]:
        """创建以对象为中心的参考系"""
        obj = self.get_object(object_id)
        if not obj:
            return None
        
        frame = self.frame_manager.create_object_frame(obj)
        return frame.id
    
    def set_camera_to_object(self, object_id: str):
        """将相机对准对象"""
        obj = self.get_object(object_id)
        if not obj:
            return
        
        self.observer.set_camera(obj.position, obj.velocity)
    
    def set_camera_to_entity(self, entity_id: str):
        """将相机对准实体"""
        entity = self.get_entity(entity_id)
        if not entity:
            return
        
        self.observer.set_camera(entity.position, entity.velocity)
    
    def get_simulation_state(self) -> Dict[str, Any]:
        """获取模拟状态"""
        return {
            'time': self.time_manager.get_time_info(),
            'frames': self.frame_manager.get_frame_info(),
            'objects': len(self.objects),
            'entities': len(self.entities),
            'stats': self.stats.copy(),
            'event_flags': self.event_flags.copy(),
            'observer': self.observer.get_stats()
        }
    
    def get_object_state(self, object_id: str) -> Optional[Dict[str, Any]]:
        """获取对象状态"""
        obj = self.get_object(object_id)
        if not obj:
            return None
        
        # 计算受力
        total_force = calculate_total_force_on_object(obj, self.entities)
        obj_mass = obj.attributes.get('mass', 1.0)
        acceleration = total_force / obj_mass
        
        return {
            'id': obj.id,
            'position': obj.position.tolist(),
            'velocity': obj.velocity.tolist(),
            'acceleration': acceleration.tolist(),
            'health': obj.health,
            'remaining_dv': obj.remaining_dv,
            'throttle_depth': obj.throttle_depth,
            'is_throttling': obj._is_throttling,
            'attributes': obj.attributes
        }
    
    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """获取实体状态"""
        entity = self.get_entity(entity_id)
        if not entity:
            return None
        
        return {
            'id': entity.id,
            'position': entity.position.tolist(),
            'velocity': entity.velocity.tolist(),
            'mass': entity.mass,
            'density': entity.density,
            'radius': entity.radius,
            'momentum': entity.get_momentum().tolist(),
            'kinetic_energy': entity.get_kinetic_energy()
        }
    
    def _reset_event_flags(self):
        """重置事件标志"""
        for key in self.event_flags:
            self.event_flags[key] = False
    
    def _check_boundaries(self):
        """检查边界并移除超出范围的对象和实体"""
        objects_to_remove = []
        entities_to_remove = []
        
        # 检查对象
        for obj in self.objects:
            if self.time_manager.is_object_out_of_bounds(obj):
                objects_to_remove.append(obj.id)
                self.event_flags['out_of_bounds'] = True
        
        # 检查实体
        for entity in self.entities:
            if self.time_manager.is_entity_out_of_bounds(entity):
                entities_to_remove.append(entity.id)
                self.event_flags['out_of_bounds'] = True
        
        # 移除超出边界的对象和实体
        for obj_id in objects_to_remove:
            self.remove_object(obj_id)
        
        for entity_id in entities_to_remove:
            self.remove_entity(entity_id)
    
    def _record_history(self, timestamp: float):
        """记录历史"""
        # 记录对象历史
        for obj in self.objects:
            if obj.id not in self.object_history:
                self.object_history[obj.id] = []
            
            state = {
                'timestamp': timestamp,
                'position': obj.position.tolist(),
                'velocity': obj.velocity.tolist(),
                'health': obj.health,
                'remaining_dv': obj.remaining_dv
            }
            
            self.object_history[obj.id].append(state)
            
            # 限制历史大小
            if len(self.object_history[obj.id]) > self.config.history_size:
                self.object_history[obj.id].pop(0)
        
        # 记录实体历史
        for entity in self.entities:
            if entity.id not in self.entity_history:
                self.entity_history[entity.id] = []
            
            state = {
                'timestamp': timestamp,
                'position': entity.position.tolist(),
                'velocity': entity.velocity.tolist(),
                'mass': entity.mass,
                'radius': entity.radius
            }
            
            self.entity_history[entity.id].append(state)
            
            # 限制历史大小
            if len(self.entity_history[entity.id]) > self.config.history_size:
                self.entity_history[entity.id].pop(0)
    
    def clear_history(self):
        """清空历史记录"""
        self.object_history.clear()
        self.entity_history.clear()
        self.observer.clear_history()
    
    def reset(self):
        """重置模拟"""
        self.objects.clear()
        self.entities.clear()
        self.object_history.clear()
        self.entity_history.clear()
        self.observer.clear_history()
        
        self.time_manager = TimeManager(
            time_step=self.config.time_step,
            max_time_scale=self.config.max_time_scale,
            simulation_boundary=self.config.simulation_boundary
        )
        
        self.frame_manager = ReferenceFrameManager()
        
        # 重置统计
        self.stats = {
            'total_updates': 0,
            'total_collisions': 0,
            'objects_created': 0,
            'entities_created': 0,
            'objects_destroyed': 0,
            'entities_destroyed': 0,
            'total_simulation_time': 0.0,
            'average_update_time': 0.0
        }
        
        self._update_times.clear()