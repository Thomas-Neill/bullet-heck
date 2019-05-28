import pygame
from pygame.locals import *

from object import GameObject
import guns


class Player(GameObject):
    def __init__(self):
        self.draw_rect = pygame.rect.Rect(0,0,20,20)
        self.hitbox = pygame.rect.Rect(2,2,16,16)
        GameObject.__init__(self)
        self.bullets = []
        self.gun = guns.BasicGun(self)
        self.hurt = pygame.mixer.Sound("assets/hit.wav")
        self.hp = 3
        self.iframe_timer = 0
    def draw(self,display):
        s = int(self.iframe_timer*10)
        if s%2 == 0:
            pygame.draw.rect(display,(125,125,125),self.draw_rect)
        else:
            pass
        for i in self.bullets:
            i.draw(display)
    def draw_hud(self,hud):
        pygame.draw.rect(hud,(255,0,0),(0,40,90,30))
        pygame.draw.rect(hud,(0,0,255),(0,40,self.hp*30,30))
    def safe_move(self,game,dx,dy):
        self.move(dx,0)
        if not self.hitbox.colliderect(game.screen_rect):
            self.hit(game)
            self.move(-dx,0)
        self.move(0,dy)
        if not self.hitbox.colliderect(game.screen_rect):
            self.hit(game)
            self.move(0,-dy)
    def update(self,dt,game):
        keys = pygame.key.get_pressed()

        vx = 0
        vy = 0
        if keys[K_LEFT]:
            vx = -1
        elif keys[K_RIGHT]:
            vx = 1
        if keys[K_UP]:
            vy = -1
        elif keys[K_DOWN]:
            vy = 1
        mg = (vx**2 + vy**2)**.5
        if mg != 0:
            vx *= 400/mg
            vy *= 400/mg
        dx = vx*dt
        dy = vy*dt
        self.safe_move(game,dx,dy)

        self.gun.update(dt)
        if keys[K_w]:
            self.gun.fire(0,-1000)
        if keys[K_s]:
            self.gun.fire(0,1000)

        b2 = []
        for i in self.bullets:
            alive = i.update(dt,game)
            if alive:
                b2.append(i)
        self.bullets = b2

        if self.iframe_timer > 0:
            self.iframe_timer -= dt
            if self.iframe_timer < 0:
                self.iframe_timer = 0
    def hit(self,game):
        if self.iframe_timer == 0:
            self.iframe_timer = 1
            self.hurt.play()
            self.hp -= 1
            if self.hp == 0:
                game.restart()
