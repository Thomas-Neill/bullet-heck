import pygame
import copy
import math
import random
import colorsys
from object import GameObject

MOVE_SPEED = 300

def sign(x):
    if x > 0:
        return 1
    if x < 0:
        return -1

class CaptainViridian(GameObject):
    def __init__(self,game):
        self.draw_rect = pygame.rect.Rect(0,0,50,105)
        self.draw_rect.centerx = game.screen_rect.centerx
        self.hitbox = copy.copy(self.draw_rect)
        GameObject.__init__(self)
        self.start_pos = self.hitbox.center

        self.sprite = pygame.image.load("assets/6V/viridian.png")
        self.sprite = pygame.transform.scale(self.sprite,self.draw_rect.size)
        LieGun.sprite = pygame.image.load("assets/6V/liegun.png")
        Lie.sprite = pygame.image.load("assets/6V/lies.png")
        Friend.sprites = [pygame.image.load(f"assets/6V/friend{i}.png") for i in range(5)]

        self.bullets = []
        self.friends = []
        self.hp = 1

        self.current_gravity = 200 * random.choice([-1,1])
        self.gravity_vertical = random.choice([True,False])
        self.delta = 0

        self.attack_type = None
        self.attack_counter = 1
        self.gravity_switch_counter = 2
        self.counter = 0

        self.fdx = None
        self.fdy = None
        self.fmoves = []

        self.dead = False
        self.dead_counter = None

        self.music = pygame.mixer.Sound("assets/mario/ground_theme.wav")
        self.music.play(loops=-1)
    def stop_music(self):
        self.music.stop()
    def damage(self,x):
        self.hp -= x
        if self.hp <= 0:
            if not self.dead:
                self.dead = True
                self.dead_counter = 5
                self.friends = []
                self.bullets = []
                self.fmoves = []
                self.sprite = pygame.image.load("assets/6V/sad.png")
                self.sprite = pygame.transform.scale(self.sprite,self.draw_rect.size)
                self.attack_type = None
                self.set_center(*self.start_pos)
    def draw(self,display):
        toggle = True
        for i in range(-10,100):
            if toggle:
                color = (0,0,255)
            else:
                color = (0,100,255)
            if self.gravity_vertical:
                pygame.draw.rect(display,color,(0,i*10+80*self.delta*sign(self.current_gravity),400,10))
            else:
                pygame.draw.rect(display,color,(i*10+80*self.delta*sign(self.current_gravity),0,10,700))
            toggle = not toggle
        tx = self.start_pos[0]
        ty = self.start_pos[1]
        if len(self.fmoves) > 0:
            pygame.draw.circle(display,(175,0,0),(int(tx),int(ty)),2)
        for i in self.fmoves:
            t = i[2] - .5
            tx += i[0]*t
            ty += i[1]*t
            pygame.draw.line(display,(175,0,0),(int(tx-i[0]*t),int(ty-i[1]*t)),(int(tx),int(ty)))
            pygame.draw.circle(display,(175,0,0),(int(tx),int(ty)),2)
        for i in self.bullets:
            i.draw(display)
        for i in self.friends:
            i.draw(display)
        display.blit(self.sprite,self.draw_rect)
    def draw_hud(self,display):
        pygame.draw.rect(display,(255,0,0),(0,0,400,30))
        if self.hp > 0:
            pygame.draw.rect(display,(0,255,0),(0,0,self.hp*400/225,30))
    def update(self,dt,game):
        self.delta += dt
        self.delta %= 1

        if self.dead:
            self.move(-50*dt,0)
            self.dead_counter -= dt
            if self.dead_counter <= 0:
                game.next_boss()
        self.attack_counter -= dt
        if self.attack_counter <= 0 and not self.dead:
            if self.attack_type == "friends":
                dx = self.start_pos[0] - self.hitbox.centerx
                dy = self.start_pos[1] - self.hitbox.centery
                dist = (dx**2 + dy**2)**.5
                self.attack_type = "friends2"
                self.attack_counter = dist/MOVE_SPEED + .5
                self.counter = self.attack_counter
                self.fdx = dx/dist*MOVE_SPEED
                self.fdy = dy/dist*MOVE_SPEED
                for i in self.friends:
                    i.move_now(*self.start_pos)
                self.fmoves = []
            else:
                if self.attack_type == "gravity_switch":
                    old = (self.current_gravity,self.gravity_vertical)
                    while (self.current_gravity,self.gravity_vertical) == old:
                        self.current_gravity = random.choice([-200,200])
                        self.gravity_vertical = random.choice([False,True])
                if self.attack_type == "friends2":
                    self.friends = []
                    self.fdx = None
                    self.fdy = None
                self.gravity_switch_counter -= 1
                if self.gravity_switch_counter == 0:
                    self.gravity_switch_counter = 4
                    self.attack_type = "gravity_switch"
                    self.attack_counter = 2
                else:
                    self.attack_type = random.choice(["friends","squares","lies"])
                    if self.attack_type == "squares":
                        self.attack_counter = 10
                        self.counter = 1.25
                    if self.attack_type == "lies":
                        self.gravity_vertical = True
                        self.attack_counter = 15/2 + 1
                        self.counter = 1
                    if self.attack_type == "friends":
                        self.attack_counter = 8
                        self.counter = 1
                        self.fmoves = []

        if self.gravity_vertical:
            game.player.safe_move(game,0,dt*self.current_gravity)
        else:
            game.player.safe_move(game,dt*self.current_gravity,0)

        if self.attack_type == "squares":
            self.counter -= dt
            if self.counter <= 0:
                self.counter += 1.25
                hole = random.randint(0,8)
                for i in range(10):
                    if hole <= i <= hole+1:
                        continue
                    else:
                        self.bullets.append(SpinnyBox(i*40+20,120,0,100))
        elif self.attack_type == "lies":
            if self.counter > 0:
                self.counter -= dt
                if self.counter <= 0:
                    delta = 1
                    for i in range(10):
                        self.bullets.append(LieGun(self,20 + (delta == -1)*360,100 + 50*i*10/8,delta))
                        delta = -delta
        elif self.attack_type == "friends" or self.attack_type == "friends2":
            self.counter -= dt
            if self.counter <= 0 and self.attack_type == "friends":
                dx = game.player.hitbox.centerx - self.hitbox.centerx
                dy = game.player.hitbox.centery - self.hitbox.centery
                dist = (dx**2 + dy**2)**.5
                self.counter = dist/MOVE_SPEED + .5
                if dist != 0:
                    self.fdx = dx/dist*MOVE_SPEED
                    self.fdy = dy/dist*MOVE_SPEED
                else:
                    self.fdx = 0
                    self.fdy = 0
                new = Friend(game)
                for i in self.fmoves:
                    new.next(*i)
                self.friends.append(new)
                for i in self.friends:
                    i.next(self.fdx,self.fdy,self.counter)
                self.fmoves.append((self.fdx,self.fdy,self.counter))
            if self.fdx != None and self.counter > 0.5:
                self.move(self.fdx*dt,self.fdy*dt)
        b2 = []
        for i in self.bullets:
            alive = i.update(dt,game)
            if alive:
                b2.append(i)
        self.bullets = b2

        f2 = []
        for i in self.friends:
            alive = i.update(dt,game)
            if alive:
                f2.append(i)
        self.friends = f2

        if self.hitbox.colliderect(game.player.hitbox):
            game.player.hit(game)

    def more_hitboxes(self):
        for i in self.friends:
            yield (i.hitbox,i.damage)

class SpinnyBox(GameObject):
    def __init__(self,x,y,vx,vy):
        self.draw_rect = pygame.rect.Rect(0,0,20,20)
        self.hitbox = pygame.rect.Rect(2,2,16,16)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.vx = vx
        self.vy = vy
        self.rot = 0
    def draw(self,display):
        delta = self.draw_rect.w / (2**.5)
        theta = self.rot
        dx = delta*math.cos(theta)
        dy = delta*math.sin(theta)
        cx = self.draw_rect.centerx
        cy = self.draw_rect.centery
        pygame.draw.polygon(display,(0,0,0),((cx+dx,cy+dy),(cx+dy,cy-dx),(cx-dx,cy-dy),(cx-dy,cy+dx)),4)
    def update(self,dt,game):
        self.rot += dt*(math.pi)
        self.move(self.vx*dt,self.vy*dt)
        if not game.screen_rect.colliderect(self.hitbox):
            return False
        if game.player.hitbox.colliderect(self.hitbox):
            game.player.hit(game)
            return False
        return True

class LieGun(GameObject):
    def __init__(self,owner,x,y,dir):
        self.owner = owner
        self.draw_rect = pygame.rect.Rect(0,0,29,31)
        self.hitbox = pygame.rect.Rect(2,2,25,27)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.sprite = pygame.transform.flip(LieGun.sprite,dir < 0,False)
        self.life = 15/2
        self.counter = 3/2
        self.dir = dir
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
    def update(self,dt,game):
        self.counter -= dt
        if self.counter <= 0:
            self.counter += 3/2
            self.owner.bullets.append(Lie(self.hitbox.centerx + 30*self.dir,self.hitbox.centery, self.dir*200, 0))
        self.life -= dt
        if self.life < 0:
            return False
        if game.player.hitbox.colliderect(self.hitbox):
            game.player.hit(game)
        return True
class Lie(GameObject):
    def __init__(self,x,y,vx,vy):
        self.draw_rect = pygame.rect.Rect(0,0,54,24)
        self.hitbox = pygame.rect.Rect(2,2,50,20)
        GameObject.__init__(self)
        self.set_center(x,y)
        self.vx = vx
        self.vy = vy
        self.sprite = pygame.transform.scale(Lie.sprite,self.draw_rect.size)
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
    def update(self,dt,game):
        self.move(self.vx*dt,self.vy*dt)
        if not game.screen_rect.colliderect(self.hitbox):
            return False
        if game.player.hitbox.colliderect(self.hitbox):
            game.player.hit(game)
            return False
        return True

class Friend(GameObject):
    def __init__(self,game):
        self.draw_rect = pygame.rect.Rect(0,0,50,105)
        self.draw_rect.centerx = game.screen_rect.centerx
        self.hitbox = copy.copy(self.draw_rect)
        GameObject.__init__(self)
        self.sprite = pygame.transform.scale(random.choice(Friend.sprites),self.draw_rect.size)
        self.counter = 1
        self.vx = None
        self.vy = None
        self.movement_queue = []
        self.hp = 3
    def draw(self,display):
        display.blit(self.sprite,self.draw_rect)
    def next(self,vx,vy,ctr):
        self.movement_queue.append((vx,vy,ctr))
    def move_now(self,x,y):
        dx = x - self.hitbox.centerx
        dy = y - self.hitbox.centery
        dist = (dx**2 + dy**2)**.5
        self.counter = dist/MOVE_SPEED + .5
        if dist > 0:
            self.vx = dx/dist*MOVE_SPEED
            self.vy = dy/dist*MOVE_SPEED
        else:
            self.vx = 0
            self.vy = 0
        self.movement_queue = []
    def update(self,dt,game):
        if self.hp <= 0:
            return False
        self.counter -= dt
        if self.counter <= 0:
            if len(self.movement_queue) == 0:
                return False
            self.vx,self.vy,self.counter = self.movement_queue.pop(0)
        if self.counter > 0.5 and self.vx != None:
            self.move(self.vx*dt,self.vy*dt)
        if not game.screen_rect.colliderect(self.hitbox):
            return False
        if game.player.hitbox.colliderect(self.hitbox):
            game.player.hit(game)
        if self.counter <= 0.5 and len(self.movement_queue) == 0:
            return False
        return True
    def damage(self,x):
        self.hp -= x
