import pygame
import copy
import math
import random
import colorsys
from object import GameObject

class Mario(GameObject):
    def __init__(self,game):
        self.draw_rect = pygame.rect.Rect(0,0,52,64)
        self.draw_rect.centerx = game.screen_rect.centerx
        self.hitbox = copy.copy(self.draw_rect)
        GameObject.__init__(self)

        self.sprite = pygame.image.load("assets/mario/small_mario.png")
        self.sprite = pygame.transform.scale(self.sprite,self.draw_rect.size)

        self.bullets = []

        self.hp = 150

        self.attack_type = None
        self.attack_counter = 2
        self.counter = 0

        self.music = pygame.mixer.Sound("assets/mario/ground_theme.wav")
        self.music.play(loops=-1)
    def stop_music(self):
        self.music.stop()
    def damage(self,x):
        self.hp -= x
        if self.hp <= 0:
            print("dead")
            quit()
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
        for i in self.bullets:
            i.draw(display)
    def draw_hud(self,display):
        pygame.draw.rect(display,(255,0,0),(0,0,400,30))
        if self.hp > 0:
            pygame.draw.rect(display,(0,255,0),(0,0,self.hp*400/150,30))
    def update(self,dt,game):
        self.attack_counter -= dt
        if self.attack_counter <= 0:
            pass

        b2 = []
        for i in self.bullets:
            alive = i.update(dt,game)
            if alive:
                b2.append(i)
        self.bullets = b2

        if self.hitbox.colliderect(game.player.hitbox):
            game.player.hit(game)

    def more_hitboxes(self):
        for i in self.toads:
            yield (i.hitbox,i.damage)
