class GameObject:
    def __init__(self):
        self.fx = self.draw_rect.centerx
        self.fy = self.draw_rect.centery
    def move(self,dx,dy):
        self.fx += dx
        self.fy += dy
        self.sync()
    def set_center(self,x,y):
        self.fx = x
        self.fy = y
        self.sync()
    def sync(self):
        self.draw_rect.centerx = self.fx
        self.draw_rect.centery = self.fy
        self.hitbox.centerx = self.fx
        self.hitbox.centery = self.fy
