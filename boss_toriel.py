import pygame
import copy
import math
import random
from object import GameObject

class Toriel(GameObject):
    def __init__(self,game):
        self.sprite = pygame.image.load("assets/toriel/toriel.png")
        self.draw_rect = pygame.rect.Rect(0,0,142,192)
        self.draw_rect.centerx = game.screen_rect.centerx
        self.sprite = pygame.transform.scale(self.sprite,self.draw_rect.size)
        self.hitbox = copy.copy(self.draw_rect)
        self.bullets = []

        self.hp = 400
        self.dying = False
        self.dying_t = 0
        self.dead = False

        self.attack_type = None
        self.attack_counter = 3
        self.counter = 3
        self.linex = 0
        self.delayed_fire = False

        self.music = pygame.mixer.Sound("assets/toriel/Heartache.wav")
        self.music.play(loops=-1)
        GameObject.__init__(self)
    def stop_music(self):
        self.music.stop()
    def damage(self,x):
        if self.dying:
            return
        self.hp -= x
        if self.hp <= 0:
            self.dying = True
            self.sprite = pygame.image.load("assets/toriel/toriel_die.png")
            self.sprite = pygame.transform.scale(self.sprite,self.draw_rect.size)
            self.music.stop()
            self.bullets = []
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
        for i in self.bullets:
            i.draw(display)
    def draw_hud(self,display):
        pygame.draw.rect(display,(255,0,0),(0,0,500,30))
        if not self.dying:
            pygame.draw.rect(display,(0,255,0),(0,0,self.hp,30))
    def spawn_delayed_bullet(self,game,x,y):
        dx = game.player.hitbox.centerx - x
        dy = game.player.hitbox.centery - y
        mg = (dx**2 + dy**2)**0.5
        vx = 400*dx/mg
        vy = 400*dy/mg
        self.bullets.append(DelayedBullet(x,y,vx,vy))
    def update(self,dt,game):
        if self.dying:
            self.move(math.sin(game.t)*dt*100,math.sin(game.t + 1)*dt*100)
            self.dying_t += dt
            if self.dying_t > 4 and not self.dead:
                for i in range(100):
                    self.bullets.append(DustParticle(self.hitbox.centerx,self.hitbox.centery,random.uniform(-500,500),random.uniform(-500,500)))
                self.set_center(-500,0)
                self.dead = True
            if self.dying_t > 4:
                for i in self.bullets:
                    i.update(dt,game)
            if self.dying_t > 8:
                game.next_boss()
            return
        self.attack_counter -= dt
        if self.attack_counter <= 0:
            self.counter = 0.5
            self.attack_type = random.choice(["spray","sway","line","storm"])
            if self.attack_type == "spray" or self.attack_type == "sway":
                self.attack_counter = 5
            elif self.attack_type == "line":
                self.attack_counter = 1.5
                self.linex = 0
                self.delayed_fire = False
            elif self.attack_type == "storm":
                self.attack_counter = 5
            self.attack_counter += 0.5

        if self.attack_type == "spray" or self.attack_type == "sway":
            self.counter -= dt
            while self.counter <= 0:
                choice = random.randint(1,2)
                if choice == 1:
                    bull = SquiggleBullet(self.hitbox.centerx+70,self.hitbox.centery+50)
                    if self.attack_type == "sway":
                        bull.delta += math.pi
                    self.bullets.append(bull)
                else:
                    self.bullets.append(SquiggleBullet(self.hitbox.centerx-70,self.hitbox.centery+50))
                if self.attack_type == "spray":
                    self.counter += random.uniform(0.05,0.1)
                if self.attack_type == "sway":
                    self.counter += random.uniform(0.1,0.15)
        elif self.attack_type == "line":
            if self.attack_counter < 0.5:
                self.delayed_fire = True
            else:
                self.counter -= dt
                while self.counter <= 0:
                    self.spawn_delayed_bullet(game,self.linex,self.hitbox.bottom + 10)
                    self.spawn_delayed_bullet(game,400-self.linex,game.screen_rect.bottom - 10)
                    self.linex += 20
                    self.counter += 0.05
        elif self.attack_type == "storm":
            self.counter -= dt
            while self.counter <= 0:
                x = random.uniform(0,400)
                if x < game.player.hitbox.centerx:
                    vx = 10
                else:
                    vx = -10
                self.bullets.append(NormalBullet(x,self.hitbox.bottom + 10,vx,random.uniform(150,400)))
                self.counter += 0.12

        b2 = []
        for i in self.bullets:
            alive = i.update(dt,game)
            if alive:
                b2.append(i)
        self.bullets = b2

        if self.hitbox.colliderect(game.player.hitbox):
            game.player.hit(game)
    def more_hitboxes(self):
        return []

class SquiggleBullet(GameObject):
    def __init__(self,x,y):
        self.draw_rect = pygame.rect.Rect(0,0,10,10)
        self.hitbox = pygame.rect.Rect(2,2,6,6)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.delta = random.uniform(0,0.5)
        self.amplitude = random.uniform(100,200)
    def draw(self,display):
        pygame.draw.circle(display,(255,0,0),self.draw_rect.center,self.draw_rect.w//2)
    def update(self,dt,game):
        dx = math.sin(game.t/400 + self.delta)*dt*self.amplitude
        dy = dt*400
        self.move(dx,dy)
        if not game.screen_rect.colliderect(self.hitbox):
            return False
        if game.player.hitbox.colliderect(self.hitbox):
            game.player.hit(game)
            return False
        return True

class DelayedBullet(GameObject):
    def __init__(self,x,y,vx,vy):
        self.draw_rect = pygame.rect.Rect(0,0,14,14)
        self.hitbox = pygame.rect.Rect(2,2,10,10)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.vx = vx
        self.vy = vy
        self.go = False
    def draw(self,display):
        pygame.draw.circle(display,(255,0,0),self.draw_rect.center,self.draw_rect.w//2)
    def update(self,dt,game):
        if game.boss.delayed_fire:
            self.go = True
        if self.go:
            dx = self.vx*dt
            dy = self.vy*dt
            self.move(dx,dy)
            if not game.screen_rect.colliderect(self.hitbox):
                return False
            if game.player.hitbox.colliderect(self.hitbox):
                game.player.hit(game)
                return False
        return True

class NormalBullet(GameObject):
    def __init__(self,x,y,vx,vy):
        self.draw_rect = pygame.rect.Rect(0,0,10,10)
        self.hitbox = pygame.rect.Rect(2,2,6,6)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.vx = vx
        self.vy = vy
    def draw(self,display):
        pygame.draw.circle(display,(255,0,0),self.draw_rect.center,self.draw_rect.w//2)
    def update(self,dt,game):
        dx = self.vx*dt
        dy = self.vy*dt
        self.move(dx,dy)
        if not game.screen_rect.colliderect(self.hitbox):
            return False
        if game.player.hitbox.colliderect(self.hitbox):
            game.player.hit(game)
            return False
        return True

class DustParticle(GameObject):
    def __init__(self,x,y,vx,vy):
        self.draw_rect = pygame.rect.Rect(0,0,5,5)
        self.hitbox = pygame.rect.Rect(2,2,1,1)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.vx = vx
        self.vy = vy
    def draw(self,display):
        pygame.draw.circle(display,(255,255,255),self.draw_rect.center,self.draw_rect.w//2)
    def update(self,dt,game):
        dx = self.vx*dt
        dy = self.vy*dt
        self.move(dx,dy)
        if not game.screen_rect.colliderect(self.hitbox):
            return False
        return True
