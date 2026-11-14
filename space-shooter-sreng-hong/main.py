import asyncio

import pygame
import random
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('SPACE SHOOTER')
state = 'start'

blue=(255,255,255)
clock = pygame.time.Clock()

class Gun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50,20))

        self.image.fill("blue")
        self.rect = self.image.get_rect()
        self.rect.center=(WIDTH//2,HEIGHT-50)
        self.speed=500
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.rect.x +=  self.speed * dt
        if keys[pygame.K_UP]:
            self.rect.y -=  self.speed * dt
        if keys[pygame.K_DOWN]:
            self.rect.y +=  self.speed * dt

        self.rect.clamp_ip(screen.get_rect())

class Bullet(pygame.sprite.Sprite):
    def __init__(self ,x,y):
        super().__init__()
        self.image = pygame.Surface((5,10))
        self.image.fill("white")
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.speed= -1000
    def update(self,dt):
        self.rect.y += self.speed*dt
        if self.rect.bottom<0:
            self.kill()
class Enemy(pygame.sprite.Sprite):
    def __init__(self ):
        super().__init__()
        self.image = pygame.Surface((40,40))
        color=(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.image.fill(color)
        self.rect=self.image.get_rect()
        self.rect.x = random.randint(0,WIDTH-40)
        self.rect.y=random.randint(-100,-40)
        self.speed = random.randint(200,300)
    def update(self,dt):
        self.rect.y +=self.speed*dt
        if self.rect.top >HEIGHT:
            self.kill()

gun=Gun()
bullets=pygame.sprite.Group()
enemies=pygame.sprite.Group()
all_sprites=pygame.sprite.Group()
all_sprites.add(gun)


score=0
gun_hit=0
font = pygame.font.Font('freesansbold.ttf', 20)
SPAWN_ENEMY= pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY,1000)
def reset_game():
    global score, gun_hit, gun, bullets, enemies, all_sprites, state
    score = 0
    gun_hit = 0
    bullets.empty()
    enemies.empty()
    all_sprites.empty()
    gun = Gun()
    all_sprites.add(gun)
    state = 'playing'


running = True
async def main():
    global bullet, dt, enemy, event, gun_collision, gun_hit, gun_hit_surf, hint, hit, hits, msg, restart_hint, running, score, score_surf, state, title
    while running:
        await asyncio.sleep(0)
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if state == 'start' and event.key == pygame.K_SPACE :
                    state = 'playing'
            if event.type == pygame.QUIT:
                running = False
            elif event.type== SPAWN_ENEMY:
                enemy=Enemy()
                enemies.add(enemy)
                all_sprites.add(enemy)
            elif event.type == pygame.KEYDOWN:
                if event.key== pygame.K_SPACE:
                    bullet = Bullet(gun.rect.centerx, gun.rect.top)
                    bullets.add(bullet)
                    all_sprites.add(bullet)
                elif event.key== pygame.K_r:
                    reset_game()

        if state == 'playing':
            gun.update(dt)
            bullets.update(dt)
            enemies.update(dt)

        hits = pygame.sprite.groupcollide(enemies, bullets, True,True )
        for hit in hits:
            score+=10

        gun_collision= pygame.sprite.spritecollide(gun, enemies , True )

        if gun_collision:
            gun_hit += len(gun_collision)
            if gun_hit >= 5:
                state = 'game over'

        screen.fill("black")
        all_sprites.draw(screen)
        if state == 'start':
            title = font.render('SPACE SHOOTER ', True, "white")
            hint = font.render("Press space to start", True, 'white')

            screen.blit(title, title.get_frect(center=(WIDTH // 2, 250)))
            screen.blit(hint, hint.get_frect(center=(WIDTH // 2, 350)))
        elif state == 'playing':
            all_sprites.draw(screen)

            score_surf = font.render(f"Score: {score}", True, "white")
            gun_hit_surf = font.render(f"Heart breaking:{gun_hit}/5", True, "white")
            screen.blit(score_surf, (20, 20))
            screen.blit(gun_hit_surf, (20,40))
        elif state == 'game over':
            all_sprites.draw(screen)
            msg = font.render(f"GAME OVER", True, 'white')
            screen.blit(msg, msg.get_frect(center=(WIDTH // 2, 250)))
            restart_hint = font.render("Press 'R' to Play Again", True, 'white')
            screen.blit(restart_hint, restart_hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        pygame.display.update()

    pygame.quit()


asyncio.run(main())
