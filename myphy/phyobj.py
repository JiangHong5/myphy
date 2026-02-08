import pygame as pgm
from .units import *

def check(val: PhyValue, unit: AllUnit):
    if not same_dimension(val.unit, unit):
        raise DimensionError(val.unit, unit)

class PhyObj:
    _instances = []
    
    def __init__(
        self,
        mass: PhyValue,
        pos: tuple[PhyValue, PhyValue],
        v: tuple[PhyValue, PhyValue] = (build_value(0, m_p_s), build_value(0, m_p_s)),
        a: tuple[PhyValue, PhyValue] = (build_value(0, m_p_s2), build_value(0, m_p_s2)),
        color=(255, 0, 0),
        radius: PhyValue = dm.value * 1, # type: ignore
    ):
        self.mass = mass
        print(pos)
        self.pos = [pos[0], pos[1]]
        self.v = [v[0], v[1]]
        self.a = [a[0], a[1]]
        self.color = color
        self.radius = radius
        self.check()
        self._instances.append(self)


    @property
    def surface(self):
        # 转换半径为像素值
        radius_px = int(self.radius.to_unit(px).value)
        # 创建一个表面来绘制圆形
        surface = pgm.Surface((radius_px * 2, radius_px * 2), pgm.SRCALPHA)
        return surface
    
    @property
    def mask(self):
        return pgm.mask.from_surface(self.surface)
    
    def force(self, F: tuple[PhyValue, PhyValue]):
        self.a[0] += F[0] / self.mass
        self.a[1] += F[1] / self.mass
    
    def check(self):
        check(self.mass, kg)
        check(self.pos[0], m)
        check(self.pos[1], m)
        check(self.v[0], m_p_s)
        check(self.v[1], m_p_s)
        check(self.a[0], m_p_s2)
        check(self.a[1], m_p_s2)
        check(self.radius, m)
        

    def update(self, dt: PhyValue):
        self.v[0] += self.a[0] * dt
        self.v[1] += self.a[1] * dt
        self.pos[0] += self.v[0] * dt
        self.pos[1] += self.v[1] * dt
        for other in self._instances:
            if other is not self:
                self.resolve_collision(other)

    def draw(self, screen: pgm.Surface, offset: tuple[float, float] = (0, 0)):
        # print(f"Drawing object at position: ({self.pos[0]}, {self.pos[1]}) with radius: {self.radius}")
        pgm.draw.circle(
            screen,
            self.color,
            (int(self.pos[0].to_unit(px).value + offset[0]), int(self.pos[1].to_unit(px).value + offset[1])),
            int(self.radius.to_unit(px).value),
        )
    
    def get_mask_offset(self):
        radius_px = int(self.radius.to_unit(px).value)
        return (-radius_px, -radius_px)
    
    def collide_with(self, other: "PhyObj"):
        self_pos = (
            int(self.pos[0].to_unit(px).value),
            int(self.pos[1].to_unit(px).value)
        )
        other_pos = (
            int(other.pos[0].to_unit(px).value),
            int(other.pos[1].to_unit(px).value)
        )
        
        # 计算两个掩码之间的偏移量
        offset = (
            other_pos[0] - self_pos[0] + self.get_mask_offset()[0] - other.get_mask_offset()[0],
            other_pos[1] - self_pos[1] + self.get_mask_offset()[1] - other.get_mask_offset()[1]
        )
        
        # 检查掩码是否重叠
        overlap = self.mask.overlap(other.mask, offset)
        return overlap is not None
    
    def resolve_collision(self, other: "PhyObj"):
        """处理与另一个物体的碰撞，应用动量守恒"""
        # 仅当确实发生碰撞时才处理
        if not self.collide_with(other):
            return
            
        # 计算碰撞后的速度 (一维简化版动量守恒)
        # 保存当前速度
        v1 = self.v
        v2 = other.v
        
        # 计算新速度 (弹性碰撞)
        self.v[0] = (v1[0] * (self.mass - other.mass) + 2 * other.mass * v2[0]) / (self.mass + other.mass)
        self.v[1] = (v1[1] * (self.mass - other.mass) + 2 * other.mass * v2[1]) / (self.mass + other.mass)
        
        other.v[0] = (v2[0] * (other.mass - self.mass) + 2 * self.mass * v1[0]) / (self.mass + other.mass)
        other.v[1] = (v2[1] * (other.mass - self.mass) + 2 * self.mass * v1[1]) / (self.mass + other.mass)
        
        # 轻微分离物体以防止持续碰撞
        overlap = 0.1 * m.value  # 10厘米的分离距离
        self.pos[0] += overlap * (self.pos[0] - other.pos[0]).value / abs((self.pos[0] - other.pos[0]).value + 1e-10)
        self.pos[1] += overlap * (self.pos[1] - other.pos[1]).value / abs((self.pos[1] - other.pos[1]).value + 1e-10)

if __name__ == "__main__":
    pass
