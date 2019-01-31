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

        self.sprite_cover = pygame.surface.Surface((self.hitbox.w,self.hitbox.h))
        self.sprite_cover.set_alpha(0)

        self.flower_sprite = pygame.image.load("assets/mario/flower.png")
        self.flower_sprite = pygame.transform.scale(self.flower_sprite,(32,32))

        self.star_sprite = pygame.image.load("assets/mario/star.png")
        self.star_sprite = pygame.transform.scale(self.star_sprite,(32,32))

        Shell.sprite = pygame.image.load("assets/mario/shell.png")
        Toad.sprite = pygame.image.load("assets/mario/toad.png")
        Mushroom.sprite = pygame.image.load("assets/mario/mushroom.png")

        self.bullets = []
        self.toads = []

        self.hp = 150
        self.dying = False

        self.star_counter = 4
        self.attack_type = None
        self.attack_counter = 2
        self.counter = 0
        self.flower_theta = 0
        self.star_color = 0

        self.music = pygame.mixer.Sound("assets/mario/ground_theme.wav")
        self.music.play(loops=-1)
        self.star_music = pygame.mixer.Sound("assets/mario/star_theme.wav")
        self.kick = pygame.mixer.Sound("assets/mario/shell_kick.wav")
        self.fire = pygame.mixer.Sound("assets/mario/fireball.wav")
        self.death_jingle = pygame.mixer.Sound("assets/mario/death_theme.wav")
    def stop_music(self):
        self.music.stop()
        self.star_music.stop()
    def damage(self,x):
        if not ((self.attack_type == "star" and self.counter <= 0) or self.dying):
            self.hp -= x
            if self.hp <= 0:
                self.dying = True
                self.bullets = []
                self.toads = []
                self.sprite = pygame.image.load("assets/mario/dead_mario.gif")
                self.draw_rect.h = 52
                self.hitbox.h = 52
                GameObject.__init__(self)
                self.sprite = pygame.transform.scale(self.sprite,self.draw_rect.size)
                self.fall_v = 100
                self.stop_music()
                self.death_jingle.play()
                self.attack_type = None
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
        display.blit(self.sprite_cover,self.draw_rect)
        if self.attack_type == "fire":
            flower_x = self.draw_rect.centerx + 70*math.cos(self.flower_theta)
            flower_y = self.draw_rect.centery + 70*math.sin(self.flower_theta)
            display.blit(self.flower_sprite,(flower_x-16,flower_y-16))
        if self.attack_type == "star" and self.counter > 0:
            star_x = self.draw_rect.centerx + 70*math.cos(self.star_theta)
            star_y = self.draw_rect.centery + 70*math.sin(self.star_theta)
            display.blit(self.star_sprite,(star_x-16,star_y-16))
        for i in self.bullets:
            i.draw(display)
        for i in self.toads:
            i.draw(display)
    def draw_hud(self,display):
        pygame.draw.rect(display,(255,0,0),(0,0,400,30))
        if self.hp > 0:
            pygame.draw.rect(display,(0,255,0),(0,0,self.hp*400/150,30))
    def update(self,dt,game):
        if self.dying:
            dy = self.fall_v*dt
            self.move(0,-dy)
            if self.hitbox.colliderect(game.player.hitbox):
                game.player.hit(game)
            if self.fall_v > -400:
                self.fall_v -= dt*200
            else:
                if not self.hitbox.colliderect(game.screen_rect):
                    game.next_boss()
            return
        #calculate values used to track player before anything else
        x = self.hitbox.centerx
        y = self.hitbox.centery
        dx = game.player.hitbox.centerx - x
        dy = game.player.hitbox.centery - y
        mg = (dx**2+dy**2)**0.5
        if mg>0:
            dx /= mg
            dy /= mg
        self.attack_counter -= dt
        if self.attack_counter <= 0:
            old_atk = self.attack_type
            atk_list = ["shells","fire"]
            if len(self.toads) == 0:
                atk_list.append("toads")
            if old_atk == "star":
                self.star_music.stop()
                self.music.play(loops=-1)
                self.sprite_cover.set_alpha(0)
            else:
                atk_list.append("star")
            if old_atk == "toads":
                for i in self.toads:
                    i.go = True

            self.attack_type = random.choice(atk_list)
            self.star_counter -= 1
            if self.star_counter == 0:
                self.attack_type = "star"
            if self.attack_type == "shells":
                self.attack_counter = 6.6
            elif self.attack_type == "fire":
                self.attack_counter = 4
                self.flower_theta = math.atan2(dy,dx)
            elif self.attack_type == "star":
                self.star_counter = 4
                self.counter = 0.5
                self.attack_counter = 4.5
                self.star_theta = math.atan2(dy,dx)
            elif self.attack_type == "toads":
                self.attack_counter = 4
                self.counter = 0

        #self.move(dx*dt*25,dy*dt*25)

        if self.attack_type == "shells":
            self.counter -= dt
            if self.counter < 0:
                x += dx*30
                y += dy*30

                self.bullets.append(Shell(x,y,dx*400,dy*400))
                self.counter += 0.75
                self.kick.play()
            while self.counter < 0:
                self.counter += 0.75
        elif self.attack_type == "fire":
            player_theta = math.atan2(dy,dx)
            d = abs(player_theta - self.flower_theta)
            if d > math.pi:
                k = -1
            else:
                k = 1
            if self.flower_theta < player_theta:
                self.flower_theta += dt*k
            else:
                self.flower_theta -= dt*k
            self.counter -= dt
            if self.counter < 0:
                for theta in [self.flower_theta,self.flower_theta + 0.25,self.flower_theta - 0.25]:
                    x = math.cos(theta)
                    y = math.sin(theta)
                    self.bullets.append(Fireball(self.hitbox.centerx + x*80,self.hitbox.centery + y*80,x*400,y*400))
                self.counter += 0.4
                self.fire.play()
            while self.counter < 0:
                self.counter += 0.2
        elif self.attack_type == "star":
            if self.counter > 0:
                self.counter -= dt
                if self.counter <= 0:
                    self.star_music.play()
                    self.music.stop()
                    self.sprite_cover.set_alpha(128)
            if self.counter <= 0:
                self.star_color += dt
                self.star_color %= 1
                self.sprite_cover.fill(colorsys.hsv_to_rgb(self.star_color,1,255))
                self.move(dx*250*dt,dy*250*dt)
        elif self.attack_type == "toads":
            self.counter -= dt
            if self.counter <= 0:
                self.counter = 0.5
                self.toads.append(Toad(self.attack_counter*math.pi/2,self))

        b2 = []
        for i in self.bullets:
            alive = i.update(dt,game)
            if alive:
                b2.append(i)
        self.bullets = b2

        t2 = []
        for i in self.toads:
            alive = i.update(dt,game)
            if alive:
                t2.append(i)
        self.toads = t2

        if self.hitbox.colliderect(game.player.hitbox):
            game.player.hit(game)

    def more_hitboxes(self):
        for i in self.toads:
            yield (i.hitbox,i.damage)

class Shell(GameObject):
    bottom_barrier = pygame.rect.Rect(0,600,400,1)
    top_barrier = pygame.rect.Rect(0,-1,400,1)
    left_barrier = pygame.rect.Rect(-1,0,1,600)
    right_barrier = pygame.rect.Rect(400,0,1,600)
    def __init__(self,x,y,vx,vy):
        self.draw_rect = pygame.rect.Rect(0,0,32,28)
        self.hitbox = pygame.rect.Rect(2,2,28,26)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.vx = vx
        self.vy = vy
        self.bounces = 2

        self.sprite = pygame.transform.scale(Shell.sprite,self.draw_rect.size)
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
    def update(self,dt,game):
        self.move(self.vx*dt,self.vy*dt)
        if not game.screen_rect.colliderect(self.hitbox):
            return False
        if self.bounces > 0:
            if self.hitbox.colliderect(Shell.left_barrier) or self.hitbox.colliderect(Shell.right_barrier):
                self.vx *= -1
                self.bounces -= 1
            if self.hitbox.colliderect(Shell.bottom_barrier) or self.hitbox.colliderect(Shell.top_barrier):
                self.vy *= -1
                self.bounces -= 1
        if game.player.hitbox.colliderect(self.hitbox):
            game.player.hit(game)
            return False
        return True

class Fireball(GameObject):
    def __init__(self,x,y,vx,vy):
        self.draw_rect = pygame.rect.Rect(0,0,20,20)
        self.hitbox = pygame.rect.Rect(2,2,16,16)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.vx = vx
        self.vy = vy
        self.mg = (vx**2 + vy**2)**.5
    def draw(self,display):
        pygame.draw.circle(display,(255,0,0),self.draw_rect.center,self.draw_rect.w//2)
    def update(self,dt,game):
        #offset = math.sin(game.t/100)*100
        dx = self.vx*dt #+ self.vy*dt*offset/self.mg
        dy = self.vy*dt #+ self.vx*dt*offset/self.mg
        self.move(dx,dy)
        if not game.screen_rect.colliderect(self.hitbox):
            return False
        if game.player.hitbox.colliderect(self.hitbox):
            game.player.hit(game)
            return False
        return True

class Toad(GameObject):
    def __init__(self,theta_initial,owner):
        self.draw_rect = pygame.rect.Rect(0,0,32,48)
        self.hitbox = copy.copy(self.draw_rect)
        self.sprite = pygame.transform.scale(Toad.sprite,self.draw_rect.size)
        GameObject.__init__(self)
        self.theta = theta_initial
        self.owner = owner
        self.update_pos()
        self.go = False
        self.hp = 4
        self.shoot_counter = 0
    def update_pos(self):
        self.set_center(self.owner.hitbox.centerx + 50*math.cos(self.theta),self.owner.hitbox.centery + 50*math.sin(self.theta))
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
    def damage(self,x):
        self.hp -= x
    def update(self,dt,game):
        if self.go:
            self.theta += dt
            self.update_pos()
            if self.shoot_counter <= 0:
                x = self.hitbox.centerx
                y = self.hitbox.centery
                dx = game.player.hitbox.centerx - x
                dy = game.player.hitbox.centery - y
                mg = (dx**2+dy**2)**0.5
                if mg>0:
                    dx /= mg
                    dy /= mg
                self.owner.bullets.append(Mushroom(x + dx*30,y + dy*30,dx*800,dy*800))
                self.shoot_counter = 1
            else:
                self.shoot_counter -= dt
        if self.hp < 0:
            return False
        return True

class Mushroom(GameObject):
    def __init__(self,x,y,vx,vy):
        self.draw_rect = pygame.rect.Rect(0,0,20,20)
        self.hitbox = pygame.rect.Rect(2,2,16,16)
        self.sprite = pygame.transform.scale(Mushroom.sprite,self.draw_rect.size)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.vx = vx
        self.vy = vy
        self.mg = (vx**2 + vy**2)**.5
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
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
