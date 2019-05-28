import pygame
from pygame.locals import *

import player
import boss_toriel
import boss_mario
import boss_captain

boss_cons = boss_captain.CaptainViridian

class Game:
    def __init__(self):
        pygame.mixer.pre_init(48000, -16, 2, 1024)
        pygame.init()
        self.display = pygame.display.set_mode((400,700))
        self.hud = pygame.surface.Surface((400,100))
        self.play_area = pygame.surface.Surface((400,600))
        self.screen_rect = pygame.rect.Rect(0,0,400,600)
        self.t = pygame.time.get_ticks()
        self.restart_flag = False

        self.player = player.Player()
        self.player.set_center(200,400)

        self.boss = boss_cons(self)
    def restart(self):
        self.restart_flag = True
    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.inputs()
            self.update()
            self.draw()
            clock.tick(60)
            if self.restart_flag:
                self.player = player.Player()
                self.player.set_center(200,400)

                self.boss.stop_music()
                self.boss = boss_cons(self)
                self.restart_flag = False
    def inputs(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                quit()
    def draw(self):
        self.play_area.fill((0,0,0))
        self.boss.draw(self.play_area)
        self.player.draw(self.play_area)
        self.display.blit(self.play_area,(0,100))

        self.hud.fill((125,125,125))
        self.boss.draw_hud(self.hud)
        self.player.draw_hud(self.hud)
        self.display.blit(self.hud,(0,0))
        pygame.display.update()
    def update(self):
        dt = pygame.time.get_ticks() - self.t
        dt /= 1000
        self.t = pygame.time.get_ticks()

        self.player.update(dt,self)
        self.boss.update(dt,self)
    def next_boss(self):
        print("YOU ARE WINNER")
        quit()
