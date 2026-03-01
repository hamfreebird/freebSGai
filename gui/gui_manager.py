"""
GUI管理器
主界面控制器，整合模拟引擎和用户界面
"""
import pygame
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

from physics.simulation import UniverseSimulation, SimulationConfig
from entities.entity import Entity, Object
from observation.observer import Observer
from utils.helpers import create_star, create_planet, create_spaceship, create_asteroid


@dataclass
class GUIConfig:
    """GUI配置"""
    # 窗口设置
    width: int = 1920
    height: int = 1080
    fullscreen: bool = False
    title: str = "2D Space Combat Physics Simulator"
    
    # 颜色
    background_color: Tuple[int, int, int] = (0, 0, 20)
    grid_color: Tuple[int, int, int] = (30, 30, 60)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    highlight_color: Tuple[int, int, int] = (255, 200, 50)
    
    # UI设置
    font_size_small: int = 16
    font_size_medium: int = 20
    font_size_large: int = 24
    panel_width: int = 300
    panel_margin: int = 10
    info_panel_height: int = 200
    
    # 相机控制
    move_speed: float = 1e9  # 米/秒
    zoom_speed: float = 1.2
    min_zoom: float = 0.0001
    max_zoom: float = 100.0
    
    # 时间控制
    time_scales: List[float] = field(default_factory=lambda: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0])
    default_time_scale: float = 1.0
    
    @classmethod
    def from_json(cls, config_path: str) -> 'GUIConfig':
        """从JSON文件加载配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(
            width=data['window']['width'],
            height=data['window']['height'],
            fullscreen=data['window']['fullscreen'],
            title=data['window']['title'],
            background_color=tuple(data['colors']['background']),
            grid_color=tuple(data['colors']['grid']),
            text_color=tuple(data['colors']['ui_text']),
            highlight_color=tuple(data['colors']['ui_highlight']),
            font_size_small=data['ui']['font_size_small'],
            font_size_medium=data['ui']['font_size_medium'],
            font_size_large=data['ui']['font_size_large'],
            panel_width=data['ui']['panel_width'],
            panel_margin=data['ui']['panel_margin'],
            info_panel_height=data['ui']['info_panel_height'],
            move_speed=data['camera']['move_speed'],
            zoom_speed=data['camera']['zoom_speed'],
            min_zoom=data['camera']['min_zoom'],
            max_zoom=data['camera']['max_zoom'],
            time_scales=data['time_controls']['time_scales'],
            default_time_scale=data['time_controls']['default_time_scale']
        )


class GUIManager:
    """GUI管理器"""
    
    def __init__(self, config_path: str = "config.json"):
        # 加载配置
        self.config = GUIConfig.from_json(config_path)
        
        # 初始化Pygame
        pygame.init()
        if self.config.fullscreen:
            self.screen = pygame.display.set_mode((self.config.width, self.config.height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        pygame.display.set_caption(self.config.title)
        
        # 加载字体（尝试多种字体，确保至少有一种可用）
        font_names = ['consolas', 'arial', 'couriernew', 'cour', 'dejavusansmono', 'freesans']
        self.font_small = None
        self.font_medium = None
        self.font_large = None
        
        for font_name in font_names:
            try:
                self.font_small = pygame.font.SysFont(font_name, self.config.font_size_small)
                self.font_medium = pygame.font.SysFont(font_name, self.config.font_size_medium)
                self.font_large = pygame.font.SysFont(font_name, self.config.font_size_large)
                print(f"Using font: {font_name}")
                break
            except:
                continue
        
        # 如果所有字体都失败，使用默认字体
        if self.font_small is None:
            print("Warning: Unable to load system fonts, using default font")
            self.font_small = pygame.font.Font(None, self.config.font_size_small)
            self.font_medium = pygame.font.Font(None, self.config.font_size_medium)
            self.font_large = pygame.font.Font(None, self.config.font_size_large)
        
        # 创建模拟引擎
        sim_config = SimulationConfig(
            screen_width=self.config.width,
            screen_height=self.config.height
        )
        self.simulation = UniverseSimulation(sim_config)
        
        # 相机状态
        self.camera_position = np.array([0.0, 0.0])  # 相机中心位置 (米)
        self.camera_zoom = 1e-9  # 像素/米 (更小的值以便看到整个太阳系)
        self.camera_move_speed = self.config.move_speed
        self.target_camera_zoom = self.camera_zoom  # 目标缩放级别（用于平滑缩放）
        self.zoom_smoothness = 0.1  # 缩放平滑度（0-1，越小越平滑）
        
        # 时间控制
        self.time_scale_index = 2  # 默认1.0倍速
        self.is_paused = False
        
        # 界面状态
        self.current_interface = "observation"  # "observation" 或 "maneuver"
        self.selected_object_id = None
        self.selected_entity_id = None
        
        # 机动界面状态
        self.maneuver_dv = 100.0  # 总dv (m/s)
        self.maneuver_angle = 0.0  # 角度 (度)
        self.maneuver_throttle = 0.5  # 节流深度 (0-1)
        self.maneuver_mouse_pos = None  # 鼠标位置用于选择方向
        
        # 性能统计
        self.fps = 60
        self.last_frame_time = pygame.time.get_ticks()
        self.frame_count = 0
        
        # 加载初始场景
        self._load_initial_scenario(config_path)
        
        # 为所有对象和实体创建参考系
        self._create_reference_frames()
        
        # 如果场景中有对象，选择第一个作为默认
        if self.simulation.objects:
            self.selected_object_id = self.simulation.objects[0].id
    
    def _load_initial_scenario(self, config_path: str):
        """从配置文件加载初始场景"""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scenario = data['initial_scenario']
        print(f"Loading scenario: {scenario['name']}")
        
        # 创建实体
        for entity_data in scenario['entities']:
            if entity_data['type'] == 'star':
                entity = create_star(
                    name=entity_data['name'],
                    position=tuple(entity_data['position']),
                    velocity=tuple(entity_data['velocity'])
                )
                # 设置颜色
                entity.color = tuple(entity_data['color'])
            elif entity_data['type'] == 'planet':
                # 注意：create_planet使用distance和orbital_speed参数，而不是直接的位置和速度
                # 这里我们需要直接创建Entity
                entity = Entity(
                    mass=entity_data.get('mass', 5.972e24),
                    density=entity_data.get('density', 5515),
                    radius=entity_data.get('radius', 6.371e6),
                    position=np.array(entity_data['position']),
                    velocity=np.array(entity_data['velocity']),
                    name=entity_data['name']
                )
                entity.color = tuple(entity_data['color'])
            elif entity_data['type'] == 'asteroid':
                entity = create_asteroid(
                    name=entity_data['name'],
                    position=tuple(entity_data['position']),
                    velocity=tuple(entity_data['velocity'])
                )
                entity.color = tuple(entity_data['color'])
            else:
                continue
            
            self.simulation.add_entity(entity)
        
        # 创建对象
        for object_data in scenario['objects']:
            if object_data['type'] == 'spaceship':
                # 直接创建Object对象
                obj = Object(
                    position=np.array(object_data['position']),
                    velocity=np.array(object_data['velocity']),
                    label=object_data['label'],
                    max_acceleration=object_data.get('max_acceleration', 5.0),
                    remaining_dv=object_data.get('remaining_dv', 1000.0)
                )
                # 设置颜色属性
                obj.color = tuple(object_data['color'])
                self.simulation.add_object(obj)
    
    def _create_reference_frames(self):
        """为所有对象和实体创建参考系"""
        # 为所有实体创建参考系
        for entity in self.simulation.entities:
            self.simulation.frame_manager.create_entity_frame(entity)
        
        # 为所有对象创建参考系
        for obj in self.simulation.objects:
            self.simulation.frame_manager.create_object_frame(obj)
        
        print(f"Created {len(self.simulation.entities)} entity reference frames and {len(self.simulation.objects)} object reference frames")
    
    def world_to_screen(self, world_pos: np.ndarray) -> Tuple[float, float]:
        """将世界坐标转换为屏幕坐标（浮点数）"""
        # 计算相对于相机的位置
        relative_x = world_pos[0] - self.camera_position[0]
        relative_y = world_pos[1] - self.camera_position[1]
        
        # 应用缩放
        screen_x = self.config.width // 2 + relative_x * self.camera_zoom
        screen_y = self.config.height // 2 + relative_y * self.camera_zoom
        
        return screen_x, screen_y
    
    def world_to_screen_int(self, world_pos: np.ndarray) -> Tuple[int, int]:
        """将世界坐标转换为屏幕坐标（整数，用于绘制）"""
        screen_x, screen_y = self.world_to_screen(world_pos)
        # 确保返回Python整数，而不是numpy整数
        return int(float(screen_x)), int(float(screen_y))
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> np.ndarray:
        """将屏幕坐标转换为世界坐标"""
        screen_x, screen_y = screen_pos
        
        # 计算相对于屏幕中心的位置
        relative_x = screen_x - self.config.width // 2
        relative_y = screen_y - self.config.height // 2
        
        # 应用逆缩放
        world_x = self.camera_position[0] + relative_x / self.camera_zoom
        world_y = self.camera_position[1] + relative_y / self.camera_zoom
        
        return np.array([world_x, world_y])
    
    def draw_grid(self):
        """绘制网格"""
        # 计算网格间距（根据缩放级别调整）
        grid_spacing_meters = 10 ** (round(np.log10(100 / self.camera_zoom)))
        grid_spacing_pixels = int(grid_spacing_meters * self.camera_zoom)
        
        if grid_spacing_pixels < 10:  # 网格太密则不绘制
            return
        
        # 计算网格起点
        world_center = self.camera_position
        screen_center_x, screen_center_y = self.config.width // 2, self.config.height // 2
        
        # 计算第一个网格线的位置
        offset_x = world_center[0] % grid_spacing_meters
        offset_y = world_center[1] % grid_spacing_meters
        
        start_x_pixel = screen_center_x - int(offset_x * self.camera_zoom)
        start_y_pixel = screen_center_y - int(offset_y * self.camera_zoom)
        
        # 绘制垂直线
        x = start_x_pixel
        while x < self.config.width:
            pygame.draw.line(self.screen, self.config.grid_color, 
                           (x, 0), (x, self.config.height), 1)
            x += grid_spacing_pixels
        
        x = start_x_pixel - grid_spacing_pixels
        while x >= 0:
            pygame.draw.line(self.screen, self.config.grid_color, 
                           (x, 0), (x, self.config.height), 1)
            x -= grid_spacing_pixels
        
        # 绘制水平线
        y = start_y_pixel
        while y < self.config.height:
            pygame.draw.line(self.screen, self.config.grid_color, 
                           (0, y), (self.config.width, y), 1)
            y += grid_spacing_pixels
        
        y = start_y_pixel - grid_spacing_pixels
        while y >= 0:
            pygame.draw.line(self.screen, self.config.grid_color, 
                           (0, y), (self.config.width, y), 1)
            y -= grid_spacing_pixels
    
    def draw_entities(self):
        """绘制所有实体"""
        for entity in self.simulation.entities:
            screen_pos = self.world_to_screen_int(entity.position)
            
            # 计算实体在屏幕上的半径
            # 对于非常大的实体（如太阳），使用对数缩放使其在屏幕上看起来合理
            if entity.radius > 1e7:  # 大型天体（太阳、行星）
                # 使用对数缩放：log10(radius) * 缩放因子
                log_radius = np.log10(entity.radius)
                base_radius = 5  # 基础半径
                # 移除1e9因子，让缩放正常工作
                scaled_radius = base_radius * log_radius * self.camera_zoom
            else:
                scaled_radius = entity.radius * self.camera_zoom
            
            radius = max(2, int(scaled_radius))
            
            # 限制最大半径，避免实体过大覆盖整个屏幕
            max_radius = min(self.config.width, self.config.height) // 4
            radius = min(radius, max_radius)
            
            # 绘制实体
            pygame.draw.circle(self.screen, entity.color, (screen_pos[0], screen_pos[1]), radius)
            
            # 绘制名称标签
            if radius > 5 and radius < max_radius:  # 实体足够大且不太大时才显示名称
                try:
                    name_text = self.font_small.render(entity.name, True, self.config.text_color)
                    text_rect = name_text.get_rect(center=(screen_pos[0], screen_pos[1] - radius - 10))
                    self.screen.blit(name_text, text_rect)
                except:
                    pass  # 如果字体渲染失败，跳过标签绘制
    
    def draw_objects(self):
        """绘制所有对象"""
        for obj in self.simulation.objects:
            screen_pos = self.world_to_screen_int(obj.position)
            
            # 绘制对象（三角形表示飞船）
            color = getattr(obj, 'color', (255, 100, 100))
            size = max(3, int(5 * np.sqrt(self.camera_zoom)))
            
            # 计算速度方向
            speed = np.linalg.norm(obj.velocity)
            if speed > 0:
                direction = obj.velocity / speed
                angle = np.arctan2(direction[1], direction[0])
            else:
                angle = 0
            
            # 绘制三角形
            points = []
            for i in range(3):
                point_angle = angle + i * 2 * np.pi / 3
                px = screen_pos[0] + size * np.cos(point_angle)
                py = screen_pos[1] + size * np.sin(point_angle)
                points.append((px, py))
            
            pygame.draw.polygon(self.screen, color, points)
            
            # 如果被选中，绘制高亮
            if obj.id == self.selected_object_id:
                pygame.draw.circle(self.screen, self.config.highlight_color, 
                                 (screen_pos[0], screen_pos[1]), size + 3, 2)
            
            # 绘制标签
            label_text = self.font_small.render(obj.label, True, self.config.text_color)
            text_rect = label_text.get_rect(center=(screen_pos[0], screen_pos[1] - size - 10))
            self.screen.blit(label_text, text_rect)
    
    def draw_trajectories(self):
        """绘制轨道"""
        if not self.selected_object_id:
            return
        
        # 获取选中的对象
        selected_obj = None
        for obj in self.simulation.objects:
            if obj.id == self.selected_object_id:
                selected_obj = obj
                break
        
        if not selected_obj:
            return
        
        # 预测轨道
        orbit = self.simulation.predict_orbit(selected_obj.id, steps=100)
        if not orbit:
            return
        
        # 绘制轨道点
        points = []
        for point in orbit:
            screen_pos = self.world_to_screen_int(point)
            points.append(screen_pos)
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, (100, 255, 100), False, points, 2)
    
    def draw_edge_indicators(self):
        """在屏幕边缘绘制箭头指示实体或对象的位置"""
        margin = 20  # 距离屏幕边缘的边距
        arrow_size = 15  # 箭头大小
        
        # 检查所有实体
        for entity in self.simulation.entities:
            screen_pos = self.world_to_screen(entity.position)
            screen_x, screen_y = screen_pos
            
            # 检查实体是否在屏幕外
            if (screen_x < -margin or screen_x > self.config.width + margin or 
                screen_y < -margin or screen_y > self.config.height + margin):
                
                # 计算箭头位置（限制在屏幕边缘）
                arrow_x = max(margin, min(self.config.width - margin, screen_x))
                arrow_y = max(margin, min(self.config.height - margin, screen_y))
                
                # 计算箭头方向（指向实体位置）
                dx = screen_x - arrow_x
                dy = screen_y - arrow_y
                angle = np.arctan2(dy, dx)
                
                # 绘制箭头
                color = entity.color if hasattr(entity, 'color') else (255, 255, 255)
                self.draw_arrow((arrow_x, arrow_y), angle, arrow_size, color)
                
                # 在箭头旁边显示实体名称
                name_text = self.font_small.render(entity.name, True, color)
                text_x = arrow_x + np.cos(angle) * (arrow_size + 10)
                text_y = arrow_y + np.sin(angle) * (arrow_size + 10)
                self.screen.blit(name_text, (int(text_x), int(text_y)))
        
        # 检查所有对象
        for obj in self.simulation.objects:
            screen_pos = self.world_to_screen(obj.position)
            screen_x, screen_y = screen_pos
            
            # 检查对象是否在屏幕外
            if (screen_x < -margin or screen_x > self.config.width + margin or 
                screen_y < -margin or screen_y > self.config.height + margin):
                
                # 计算箭头位置（限制在屏幕边缘）
                arrow_x = max(margin, min(self.config.width - margin, screen_x))
                arrow_y = max(margin, min(self.config.height - margin, screen_y))
                
                # 计算箭头方向（指向对象位置）
                dx = screen_x - arrow_x
                dy = screen_y - arrow_y
                angle = np.arctan2(dy, dx)
                
                # 绘制箭头
                color = getattr(obj, 'color', (255, 100, 100))
                self.draw_arrow((arrow_x, arrow_y), angle, arrow_size, color)
                
                # 在箭头旁边显示对象标签
                name_text = self.font_small.render(obj.label, True, color)
                text_x = arrow_x + np.cos(angle) * (arrow_size + 10)
                text_y = arrow_y + np.sin(angle) * (arrow_size + 10)
                self.screen.blit(name_text, (int(text_x), int(text_y)))
    
    def draw_arrow(self, pos, angle, size, color):
        """绘制箭头"""
        x, y = pos
        
        # 计算箭头的三个点
        points = []
        for i in range(3):
            point_angle = angle + i * 2 * np.pi / 3
            px = x + size * np.cos(point_angle)
            py = y + size * np.sin(point_angle)
            points.append((px, py))
        
        pygame.draw.polygon(self.screen, color, points)
    
    def draw_info_panel(self):
        """绘制信息面板"""
        # 左侧面板 - 选中对象信息
        left_panel_rect = pygame.Rect(
            self.config.panel_margin,
            self.config.panel_margin,
            self.config.panel_width,
            self.config.info_panel_height
        )
        
        # 绘制面板背景
        pygame.draw.rect(self.screen, (0, 0, 0, 200), left_panel_rect)
        pygame.draw.rect(self.screen, self.config.highlight_color, left_panel_rect, 2)
        
        # 面板标题
        title_text = self.font_medium.render("Selected Object Info", True, self.config.highlight_color)
        self.screen.blit(title_text, (left_panel_rect.x + 10, left_panel_rect.y + 10))
        
        # 显示选中对象或实体信息
        y_offset = 40
        if self.selected_object_id:
            for obj in self.simulation.objects:
                if obj.id == self.selected_object_id:
                    # 获取对象状态
                    state = self.simulation.get_object_state(obj.id)
                    if state:
                        info_lines = [
                            f"Name: {obj.label} (Object)",
                            f"Pos: ({state['position'][0]/1e11:.2f}, {state['position'][1]/1e11:.2f}) ×10¹¹ m",
                            f"Vel: {np.linalg.norm(state['velocity'])/1000:.2f} km/s",
                            f"Remaining dv: {state['remaining_dv']:.1f} m/s",
                            f"Health: {state['health']:.1f}"
                        ]
                        
                        for line in info_lines:
                            text = self.font_small.render(line, True, self.config.text_color)
                            self.screen.blit(text, (left_panel_rect.x + 10, left_panel_rect.y + y_offset))
                            y_offset += 20
                    break
        elif self.selected_entity_id:
            for entity in self.simulation.entities:
                if entity.id == self.selected_entity_id:
                    info_lines = [
                        f"Name: {entity.name} (Entity)",
                        f"Pos: ({entity.position[0]/1e11:.2f}, {entity.position[1]/1e11:.2f}) ×10¹¹ m",
                        f"Radius: {entity.radius/1e6:.1f} ×10⁶ m",
                        f"Mass: {entity.mass/1e30:.3f} ×10³⁰ kg",
                        f"Type: Entity"
                    ]
                    
                    for line in info_lines:
                        text = self.font_small.render(line, True, self.config.text_color)
                        self.screen.blit(text, (left_panel_rect.x + 10, left_panel_rect.y + y_offset))
                        y_offset += 20
                    break
        else:
            # 没有选中任何对象或实体时显示提示
            text = self.font_small.render("No object/entity selected", True, self.config.text_color)
            self.screen.blit(text, (left_panel_rect.x + 10, left_panel_rect.y + y_offset))
            y_offset += 20
            text = self.font_small.render("Press TAB to select", True, self.config.text_color)
            self.screen.blit(text, (left_panel_rect.x + 10, left_panel_rect.y + y_offset))
        
        # 右侧面板 - 模拟状态
        right_panel_rect = pygame.Rect(
            self.config.width - self.config.panel_width - self.config.panel_margin,
            self.config.panel_margin,
            self.config.panel_width,
            self.config.info_panel_height
        )
        
        pygame.draw.rect(self.screen, (0, 0, 0, 200), right_panel_rect)
        pygame.draw.rect(self.screen, self.config.highlight_color, right_panel_rect, 2)
        
        # 面板标题
        title_text = self.font_medium.render("Simulation Status", True, self.config.highlight_color)
        self.screen.blit(title_text, (right_panel_rect.x + 10, right_panel_rect.y + 10))
        
        # 显示模拟状态
        sim_state = self.simulation.get_simulation_state()
        time_scale = self.config.time_scales[self.time_scale_index]
        
        # 获取时间信息
        time_info = sim_state.get('time', {})
        current_time = time_info.get('current_time', 0.0)
        
        status_lines = [
            f"Sim Time: {current_time/3600:.2f} h",
            f"Time Scale: {time_scale:.1f}x",
            f"Status: {'Paused' if self.is_paused else 'Running'}",
            f"Objects: {sim_state.get('objects', 0)}",
            f"Entities: {sim_state.get('entities', 0)}",
            f"FPS: {self.fps:.1f}"
        ]
        
        y_offset = 40
        for line in status_lines:
            text = self.font_small.render(line, True, self.config.text_color)
            self.screen.blit(text, (right_panel_rect.x + 10, right_panel_rect.y + y_offset))
            y_offset += 20
    
    def draw_maneuver_interface(self):
        """绘制机动界面"""
        if self.current_interface != "maneuver":
            return
        
        # 获取选中的对象
        selected_obj = None
        for obj in self.simulation.objects:
            if obj.id == self.selected_object_id:
                selected_obj = obj
                break
        
        if not selected_obj:
            return
        
        # 绘制机动界面背景
        maneuver_panel_rect = pygame.Rect(
            self.config.width // 2 - 200,
            self.config.height - 150,
            400,
            140
        )
        pygame.draw.rect(self.screen, (0, 0, 0, 220), maneuver_panel_rect)
        pygame.draw.rect(self.screen, self.config.highlight_color, maneuver_panel_rect, 2)
        
        # 标题
        title_text = self.font_medium.render("Maneuver Control", True, self.config.highlight_color)
        self.screen.blit(title_text, (maneuver_panel_rect.x + 10, maneuver_panel_rect.y + 10))
        
        # 显示机动参数
        y_offset = 40
        params = [
            f"Total dv: {self.maneuver_dv:.1f} m/s (O increase, - decrease)",
            f"Angle: {self.maneuver_angle:.1f}° (P increase, [ decrease)",
            f"Throttle: {self.maneuver_throttle:.2f} (] increase, [ decrease)",
            "Click screen to select direction, press Enter to execute"
        ]
        
        for param in params:
            text = self.font_small.render(param, True, self.config.text_color)
            self.screen.blit(text, (maneuver_panel_rect.x + 10, maneuver_panel_rect.y + y_offset))
            y_offset += 20
        
        # 绘制方向指示器
        if self.maneuver_mouse_pos:
            obj_screen_pos = self.world_to_screen_int(selected_obj.position)
            pygame.draw.line(self.screen, (255, 100, 100), 
                           obj_screen_pos, self.maneuver_mouse_pos, 2)
            
            # 绘制方向箭头
            dx = self.maneuver_mouse_pos[0] - obj_screen_pos[0]
            dy = self.maneuver_mouse_pos[1] - obj_screen_pos[1]
            distance = np.sqrt(dx*dx + dy*dy)
            
            if distance > 20:
                angle = np.arctan2(dy, dx)
                arrow_size = 10
                
                # 箭头点
                arrow_x = obj_screen_pos[0] + dx * 0.8
                arrow_y = obj_screen_pos[1] + dy * 0.8
                
                # 绘制箭头
                points = []
                for i in range(3):
                    point_angle = angle + (i-1) * np.pi/6
                    px = arrow_x + arrow_size * np.cos(point_angle)
                    py = arrow_y + arrow_size * np.sin(point_angle)
                    points.append((px, py))
                
                pygame.draw.polygon(self.screen, (255, 100, 100), points)
    
    def draw_controls_help(self):
        """绘制控制帮助"""
        help_panel_rect = pygame.Rect(
            self.config.width // 2 - 250,
            10,
            500,
            100
        )
        
        pygame.draw.rect(self.screen, (0, 0, 0, 180), help_panel_rect)
        
        # 根据当前界面显示不同的帮助
        if self.current_interface == "observation":
            help_lines = [
                "WASD: Move view | Q/E: Zoom | ,/.: Time scale | Space: Pause/Resume",
                "G: Toggle ref frame | T: Toggle maneuver | Tab: Cycle target"
            ]
        else:  # maneuver界面
            help_lines = [
                "鼠标: 选择方向 | O/-: 调整总dv | P/[: 调整角度 | ]/[: 调整节流",
                "Enter: 确认机动 | T: 返回观测界面 | Space: 暂停/继续"
            ]
        
        y_offset = 10
        for line in help_lines:
            text = self.font_small.render(line, True, self.config.text_color)
            text_rect = text.get_rect(center=(help_panel_rect.centerx, help_panel_rect.y + y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25
    
    def handle_input(self):
        """处理用户输入"""
        keys = pygame.key.get_pressed()
        
        # 相机移动 (WASD) - 基于屏幕像素的移动
        move_vector = np.array([0.0, 0.0])
        if keys[pygame.K_w]:
            move_vector[1] -= 1
        if keys[pygame.K_s]:
            move_vector[1] += 1
        if keys[pygame.K_a]:
            move_vector[0] -= 1
        if keys[pygame.K_d]:
            move_vector[0] += 1
        
        # 归一化对角线移动
        if np.linalg.norm(move_vector) > 0:
            move_vector = move_vector / np.linalg.norm(move_vector)
        
        # 应用移动速度（基于屏幕像素，与缩放级别成反比）
        # 移动速度：每秒移动屏幕宽度的1/4，与缩放级别成反比
        screen_move_speed = (self.config.width / 4) / self.camera_zoom  # 每秒移动的世界距离
        move_distance = screen_move_speed * (1/60)  # 每帧移动距离
        self.camera_position += move_vector * move_distance
        
        # 缩放 (QE) - 平滑缩放
        if keys[pygame.K_q]:
            self.target_camera_zoom *= self.config.zoom_speed
            self.target_camera_zoom = min(self.target_camera_zoom, self.config.max_zoom)
        if keys[pygame.K_e]:
            self.target_camera_zoom /= self.config.zoom_speed
            self.target_camera_zoom = max(self.target_camera_zoom, self.config.min_zoom)
        
        # 应用平滑缩放
        if abs(self.camera_zoom - self.target_camera_zoom) > 1e-12:
            self.camera_zoom += (self.target_camera_zoom - self.camera_zoom) * self.zoom_smoothness
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # 时间控制
                if event.key == pygame.K_SPACE:
                    self.is_paused = not self.is_paused
                
                elif event.key == pygame.K_COMMA:  # , 减少时间倍速
                    if self.time_scale_index > 0:
                        self.time_scale_index -= 1
                        self.simulation.set_time_scale(self.config.time_scales[self.time_scale_index])
                
                elif event.key == pygame.K_PERIOD:  # . 增加时间倍速
                    if self.time_scale_index < len(self.config.time_scales) - 1:
                        self.time_scale_index += 1
                        self.simulation.set_time_scale(self.config.time_scales[self.time_scale_index])
                
                # 参考系切换 (G)
                elif event.key == pygame.K_g:
                    self._toggle_reference_frame()
                
                # 界面切换 (T)
                elif event.key == pygame.K_t:
                    if self.current_interface == "observation":
                        self.current_interface = "maneuver"
                        self.is_paused = True  # 机动界面自动暂停
                        print("Switched to maneuver interface")
                    else:
                        self.current_interface = "observation"
                        print("Switched to observation interface")
                
                # 切换选中对象或实体 (Tab 或 B)
                elif event.key == pygame.K_TAB or event.key == pygame.K_b:
                    # 优先切换对象，如果没有对象则切换实体
                    if self.simulation.objects:
                        current_index = 0
                        if self.selected_object_id:
                            for i, obj in enumerate(self.simulation.objects):
                                if obj.id == self.selected_object_id:
                                    current_index = i
                                    break
                        
                        next_index = (current_index + 1) % len(self.simulation.objects)
                        self.selected_object_id = self.simulation.objects[next_index].id
                        self.selected_entity_id = None  # 清除实体选择
                        print(f"Switched to object: {self.simulation.objects[next_index].label}")
                    elif self.simulation.entities:
                        current_index = 0
                        if self.selected_entity_id:
                            for i, entity in enumerate(self.simulation.entities):
                                if entity.id == self.selected_entity_id:
                                    current_index = i
                                    break
                        
                        next_index = (current_index + 1) % len(self.simulation.entities)
                        self.selected_entity_id = self.simulation.entities[next_index].id
                        self.selected_object_id = None  # 清除对象选择
                        print(f"Switched to entity: {self.simulation.entities[next_index].name}")
                
                # 机动界面控制
                elif self.current_interface == "maneuver":
                    if event.key == pygame.K_o:  # 增加总dv
                        self.maneuver_dv = min(self.maneuver_dv + 10, 1000)
                    elif event.key == pygame.K_MINUS:  # 减少总dv
                        self.maneuver_dv = max(self.maneuver_dv - 10, 0)
                    elif event.key == pygame.K_p:  # 增加角度
                        self.maneuver_angle = (self.maneuver_angle + 5) % 360
                    elif event.key == pygame.K_LEFTBRACKET:  # 减少角度
                        self.maneuver_angle = (self.maneuver_angle - 5) % 360
                    elif event.key == pygame.K_RIGHTBRACKET:  # 增加节流
                        self.maneuver_throttle = min(self.maneuver_throttle + 0.1, 1.0)
                    elif event.key == pygame.K_LEFTBRACKET and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # 减少节流
                        self.maneuver_throttle = max(self.maneuver_throttle - 0.1, 0.0)
                    elif event.key == pygame.K_RETURN:  # 确认机动
                        self._execute_maneuver()
            
            # 鼠标事件（机动界面）
            if self.current_interface == "maneuver" and event.type == pygame.MOUSEMOTION:
                self.maneuver_mouse_pos = event.pos
        
        return True
    
    def _execute_maneuver(self):
        """执行机动"""
        if not self.selected_object_id:
            return
        
        # 找到选中的对象
        selected_obj = None
        for obj in self.simulation.objects:
            if obj.id == self.selected_object_id:
                selected_obj = obj
                break
        
        if not selected_obj:
            return
        
        # 计算方向
        if self.maneuver_mouse_pos:
            obj_screen_pos = self.world_to_screen_int(selected_obj.position)
            dx = self.maneuver_mouse_pos[0] - obj_screen_pos[0]
            dy = self.maneuver_mouse_pos[1] - obj_screen_pos[1]
            
            # 计算角度（弧度）
            angle_rad = np.arctan2(dy, dx)
            
            # 设置推力方向
            thrust_vector = np.array([np.cos(angle_rad), np.sin(angle_rad)])
            
            # 应用节流
            thrust_magnitude = self.maneuver_dv * self.maneuver_throttle
            
            # TODO: 在实际模拟中应用推力
            print(f"执行机动: dv={self.maneuver_dv:.1f}m/s, 角度={self.maneuver_angle:.1f}°, 节流={self.maneuver_throttle:.2f}")
            
            # 重置机动参数
            self.maneuver_dv = 100.0
            self.maneuver_angle = 0.0
            self.maneuver_throttle = 0.5
            self.maneuver_mouse_pos = None
    
    def _toggle_reference_frame(self):
        """切换参考系"""
        frame_manager = self.simulation.frame_manager
        frame_ids = list(frame_manager.frames.keys())
        
        if not frame_ids:
            return
        
        # 获取当前活动参考系索引
        current_index = 0
        if frame_manager.active_frame_id:
            try:
                current_index = frame_ids.index(frame_manager.active_frame_id)
            except ValueError:
                current_index = 0
        
        # 切换到下一个参考系
        next_index = (current_index + 1) % len(frame_ids)
        next_frame_id = frame_ids[next_index]
        frame_manager.set_active_frame(next_frame_id)
        
        active_frame = frame_manager.get_active_frame()
        print(f"Switched to reference frame: {active_frame.name}")
        
        # 如果切换到对象参考系，将相机对准该对象
        if next_frame_id.startswith("object_") and self.selected_object_id:
            # 找到对应的对象
            for obj in self.simulation.objects:
                if f"object_{obj.id}" == next_frame_id:
                    self.camera_position = obj.position.copy()
                    break
        elif next_frame_id.startswith("entity_"):
            # 找到对应的实体
            for entity in self.simulation.entities:
                if f"entity_{entity.id}" == next_frame_id:
                    self.camera_position = entity.position.copy()
                    break
    
    def update_simulation(self):
        """更新模拟状态"""
        if not self.is_paused:
            # 计算实际时间步长（考虑时间倍速）
            time_scale = self.config.time_scales[self.time_scale_index]
            
            # 更新模拟
            result = self.simulation.update(apply_thrust=(self.current_interface == "maneuver"))
            
            # 处理事件
            if result['event_flags']['collision_detected']:
                print("检测到碰撞!")
    
    def update_fps(self):
        """更新FPS计算"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.last_frame_time
        
        self.frame_count += 1
        
        if elapsed >= 1000:  # 每秒钟更新一次FPS
            self.fps = self.frame_count * 1000 / elapsed
            self.frame_count = 0
            self.last_frame_time = current_time
    
    def render(self):
        """渲染整个场景"""
        # 清屏
        self.screen.fill(self.config.background_color)
        
        # 绘制网格
        self.draw_grid()
        
        # 绘制实体和对象
        self.draw_entities()
        self.draw_objects()
        
        # 绘制轨道
        self.draw_trajectories()
        
        # 绘制UI
        self.draw_info_panel()
        self.draw_controls_help()
        
        # 绘制屏幕边缘箭头指示
        self.draw_edge_indicators()
        
        if self.current_interface == "maneuver":
            self.draw_maneuver_interface()
        
        # 更新显示
        pygame.display.flip()
    
    def run(self):
        """运行主循环"""
        clock = pygame.time.Clock()
        running = True
        
        print("GUI模拟启动")
        print("控制说明:")
        print("  WASD: 移动视野")
        print("  Q/E: 缩放")
        print("  ,/.: 调整时间倍速")
        print("  Space: 暂停/继续")
        print("  G: 切换参考系")
        print("  T: 切换观测/机动界面")
        print("  Tab: 切换选中对象")
        
        while running:
            # 处理输入
            running = self.handle_input()
            
            # 更新模拟
            self.update_simulation()
            
            # 渲染
            self.render()
            
            # 更新FPS
            self.update_fps()
            
            # 控制帧率
            clock.tick(60)
        
        pygame.quit()
        print("模拟结束")