import pygame
import os
import random

S_WIDTH ,S_HEIGHT = 768,591
pygame.init()
pygame.display.set_caption("Generic Space Shooter GSS")
icon = pygame.image.load("graphics/icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((S_WIDTH,S_HEIGHT))



class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.x = S_WIDTH//2 
        self.y = S_HEIGHT - 50
        self.image = pygame.image.load("graphics/player/ship_I.png").convert_alpha()
        
        self.orginal = self.image.copy()
        self.image = pygame.transform.scale_by(self.orginal,0.7)
        self.rect = self.image.get_rect(center = (self.x,self.y))

        self.acceleration = 2
        self.resistance = 0.6
        
        self.direction = pygame.math.Vector2()

        self.vx = self.vy = 0
        self.pull = 0

        self.shoot_cooldown = 0.3
        self.last_shot_time = pygame.time.get_ticks()
        self.score = 0
        self.health = 10

    
    
    def inputs(self):
        keys = pygame.key.get_pressed()
        self.direction.y = -(keys[pygame.K_UP] or keys[pygame.K_w]) + (keys[pygame.K_DOWN] or keys[pygame.K_s])
        self.direction.x = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])

        current_time = pygame.time.get_ticks()

        
        if (keys[pygame.K_SPACE] or keys[pygame.MOUSEBUTTONDOWN]) and current_time - self.last_shot_time > self.shoot_cooldown * 1000:
            bullets_group.add(Bullets(self.rect.centerx, self.rect.centery))
            self.last_shot_time = current_time  

    
    def update(self):
        self.inputs()
        if self.direction.length() != 0:
            self.direction.normalize_ip()
        self.vx = (self.resistance * self.vx) + (self.acceleration * self.direction.x)
        self.vy = (self.resistance * self.vy) + (self.acceleration * self.direction.y)  
        # self.vx = 5 * self.direction.x      
        # self.vy = 5 * self.direction.y      

        self.rect.x += round(self.vx,3)
        self.rect.y += round(self.vy,3)
        if self.direction.y < 0:
            self.pull = (self.pull * 0.3) + 0.01
        else:
            self.pull = 0

        self.image = pygame.transform.scale_by(self.orginal,0.7 + round(self.vy,2) * 0.007)
        self.image = pygame.transform.rotozoom( self.image, -self.vx,0.9 )
        self.bounds()

        ui_group.addtext(text = f"P({self.score})",position = (S_WIDTH - 5,S_HEIGHT - 5),istemp = True,place= "bottomright")
        ui_group.addtext(text = f"H({self.health})",position = (5,S_HEIGHT - 5),istemp = True,place= "bottomleft")
    def bounds(self):
        if self.rect.x + self.rect.width < 0:
            self.rect.x = S_WIDTH
        elif self.rect.x - self.rect.width > S_WIDTH:
            self.rect.x = 0



class Enemy(pygame.sprite.Sprite):
    def __init__(self,x = None,y = None):
        super().__init__()
        weights = [5,4,3,2,1]
        myimg = os.listdir("graphics/enemys")
        assert len(weights) == len(myimg) ,"error image weight background"
        new = []
        for i in range(len(weights)):
            new.extend([myimg[i]] * weights[i])
        self.myimg = random.choice(new)
        self.image = pygame.image.load("graphics/enemys/" + self.myimg).convert_alpha()
        self.image = pygame.transform.flip(self.image,flip_x=False,flip_y= True)

        if x == None or y == None:
            self.rect = self.image.get_rect(center = (random.randint(0,S_WIDTH),random.randint(-500,-10)))
        else:
            self.rect = self.image.get_rect(center = (x,y))

        self.speed = random.randint(10,15)/10
    
    def update(self):
        # self.speed = (self.speed * 0.8) + 2
        self.rect.y += self.speed + player.pull
        self.remove()
    
    def remove(self):
        if self.rect.y > S_HEIGHT + 200:
            player.health -= 1
            self.kill()
        for bullet in bullets_group:
            if self.rect.colliderect(bullet.rect):
                # Collision based on the rectangles' bounding boxes (centers)
                bullet.kill()
                player.score += 1
                self.kill()
                



    



class Bullets(pygame.sprite.Sprite):
	def __init__(self,xx,yy):
		super().__init__()
		self.image = pygame.image.load("graphics/bullet.png").convert_alpha()
		self.rect = self.image.get_rect(center = (xx,yy))
		self.speed = 0
	
	def update(self):
		self.speed = (self.speed * 0.8) + 2
		self.rect.y -= self.speed
		self.outscreenkill()
	
	def outscreenkill(self):
		if self.rect.y < -30:
			self.kill()

class UI(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
    
    def setuptext(self,font_name,font_size,font_color):
        self.font_size = font_size
        self.font_style = pygame.font.SysFont(font_name,font_size)
        self.font_color = font_color
        self.all_texts = []

    def addtext(self,text,position,size = None,place = None,istemp = False):
        if not size:
            size = self.font_size
        img = self.font_style.render(text,True,self.font_color)
        self.all_texts.append((img,position,place,istemp))

    def draw(self):
        texts_to_remove = []

        for text, position, place, istemp in self.all_texts:
            if istemp:
                texts_to_remove.append((text, position, place, istemp))

            trect = text.get_rect()

            place_attr = getattr(trect, place, None)
            if not place:
                trect.topleft = position
              
            else:
                setattr(trect,place, position)

            self.display_surface.blit(text, trect)

        
        for text_to_remove in texts_to_remove:
            self.all_texts.remove(text_to_remove)



class Background(pygame.sprite.Sprite):
    def __init__(self,x = None, y = None):
        super().__init__()
        weights = [7,10,1,2,1,1,1]
        myimg = os.listdir("graphics/background")
        assert len(weights) == len(myimg) ,"error image weight background"
        new = []
        for i in range(len(weights)):
            new.extend([myimg[i]] * weights[i])
        self.myimg = random.choice(new)
        self.image = pygame.image.load("graphics/background/" + self.myimg).convert_alpha()
    
        self.image = pygame.transform.scale_by(self.image,random.randint(30,80) * 0.01)

        if "station" in self.myimg:
            self.states = [pygame.transform.rotate(self.image,i) for i in range(1,360,random.randint(1,3))]
            if random.randint(0,1) == 1:
                self.states.reverse()

        if x == None or y == None:
            self.rect = self.image.get_rect(center = (random.randint(0,S_WIDTH),random.randint(-500,-10)))
        else:
            self.rect = self.image.get_rect(center = (x,y))

        self.speed = random.randint(10,15)/10

        self.count = 0
        
    
    def update(self):
        if "station" in self.myimg:
            self.image = self.states[self.count]
            self.rect = self.image.get_rect(center = self.rect.center)

            self.count  = int((self.count + 1) % len(self.states))

  
        self.rect.y += self.speed + player.pull
        self.remove()

    
    def remove(self):
        if self.rect.y > S_HEIGHT + 200:
            self.kill()



player = Player()
player_group = pygame.sprite.Group()
player_group.add(player)
bullets_group = pygame.sprite.Group()

enemy_group = pygame.sprite.Group()
for i in range(20):
    enemy_group.add(Enemy())

ui_group = UI()
ui_group.setuptext("Arial",30,(0,153,0))
ui_group.addtext("GSS",(S_WIDTH//2,20), size = 40,place = "center")


background_group = pygame.sprite.Group()
for i in range(20):
    background_group.add(Background(random.randint(0,S_WIDTH),random.randint(-50,S_HEIGHT + 20)))

while True:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        # elif event.type == pygame.KEYDOWN:
        #     player.update()
       
        
    # player_group.update()
    if len(background_group) < 30:
        background_group.add(Background())
    if len(enemy_group) < 10:
        enemy_group.add(Enemy())
    screen.fill((0,0,0))

    background_group.draw(screen)
    background_group.update()

    enemy_group.draw(screen)
    enemy_group.update()

    player_group.draw(screen)
    player_group.update()
    
    bullets_group.draw(screen)
    bullets_group.update()

    ui_group.draw()
    ui_group.update()

    pygame.display.flip()

    clock.tick(30)


# x,y, = 
 
#  draw 
#  update
#  fps = 30


# vx = (v * 0.1) + 2* input(up - down)
# 0.3
# vy = 

# 1 0
# 1 0

# v = 100
# v = 80
# v - 

