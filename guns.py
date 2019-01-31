import pygame
import copy
from object import GameObject

class BasicGun:
    def __init__(self,owner):
        self.cooldown = 0
        self.owner = owner
        self.laser_sound = pygame.mixer.Sound("assets/laser_shoot.wav")
        self.laser_sound.set_volume(0.1)
    def update(self,dt):
        if self.cooldown > 0:
            self.cooldown -= dt
    def fire(self,vx,vy):
        if self.cooldown <= 0:
            self.owner.bullets.append(BasicGun.Bullet(self.owner,vx,vy))
            self.cooldown = 0.1
            self.laser_sound.play()

    class Bullet(GameObject):
        def __init__(self,owner,vx,vy):
            self.draw_rect = pygame.rect.Rect(owner.draw_rect.centerx,owner.draw_rect.centery + owner.draw_rect.h*vy/abs(vy),1,10)
            self.hitbox = copy.copy(self.draw_rect)
            GameObject.__init__(self)
            self.vx = vx
            self.vy = vy
        def draw(self,display):
            pygame.draw.rect(display,(255,255,255),self.draw_rect)
        def update(self,dt,game):
            self.move(self.vx*dt,self.vy*dt)
            if not game.screen_rect.colliderect(self.hitbox):
                return False
            if game.boss.hitbox.colliderect(self.hitbox):
                game.boss.damage(1)
                return False
            for hitbox,damage in game.boss.more_hitboxes():
                if hitbox.colliderect(self.hitbox):
                    damage(1)
                    return False
            return True
