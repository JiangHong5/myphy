from myphy.phyobj import *

import pygame as pg
pg.init()
obj1 = PhyObj(5 * kg.value, (1 * m.value, 2 * m.value))
obj2 = PhyObj(6 * kg.value, (2 * m.value, 1 * m.value))
FPS = 60
screen = pg.display.set_mode((800, 600))
running = True
clock = pg.time.Clock()
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    screen.fill((255, 255, 255))
    obj1.force((0 * N.value, 9.8 * N.value))
    obj2.force((0 * N.value, 9.8 * N.value))
    obj1.update(1 * frame) # type: ignore
    obj2.update(1 * frame) # type: ignore
    obj1.draw(screen)
    obj2.draw(screen)
    pg.display.flip()
    clock.tick(FPS)
pg.quit()
