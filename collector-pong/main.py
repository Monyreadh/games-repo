import asyncio
import pygame
from random import choice
from random import randint

pygame.init()
w, h = 1000, 600
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)
large_font = pygame.font.Font(None, 80)
all_sprites = pygame.sprite.Group()
paddles = pygame.sprite.Group()
coins = pygame.sprite.Group()


class Coin(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/coin.png")
        self.rect = self.image.get_frect(topleft=(200, 150))

    def respawn(self):
        self.rect.x = randint(0, w - int(self.rect.width))
        self.rect.y = randint(0, h - int(self.rect.height) - 100)


class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed, left_key, right_key, groups):
        super().__init__(groups)
        self.image = pygame.Surface((width, height))
        self.image.fill("blue")
        self.rect = self.image.get_frect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = speed
        self.left_key = left_key
        self.right_key = right_key

    def reset_position(self, x):
        self.pos.x = x
        self.rect.centerx = round(self.pos.x)

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(int(keys[self.right_key]) - int(keys[self.left_key]), 0)

        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed * delta_time
        self.rect.centerx = round(self.pos.x)

        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
        if self.rect.right > w:
            self.rect.right = w
            self.pos.x = self.rect.centerx


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/ball.png")
        self.rect = self.image.get_frect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = speed
        self.velocity = pygame.Vector2(0, 0)
        self.reset()

    def reset(self):
        self.pos = pygame.Vector2(w / 2, h / 2)
        self.rect.center = round(self.pos.x), round(self.pos.y)
        direction = pygame.Vector2(choice((1, -1)), choice((1, -1))).normalize()
        self.velocity = direction * self.speed

    def update(self, delta_time):
        global state

        self.pos += self.velocity * delta_time
        self.rect.center = round(self.pos.x), round(self.pos.y)

        if self.rect.top <= 0 and self.velocity.y < 0:
            self.velocity.y *= -1
        if self.rect.left <= 0 and self.velocity.x < 0:
            self.velocity.x *= -1
        elif self.rect.right >= w and self.velocity.x > 0:
            self.velocity.x *= -1

        for sprite in pygame.sprite.spritecollide(self, paddles, False):
            if self.velocity.y > 0 and self.rect.bottom >= sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.pos.y = self.rect.centery

                offset = (self.rect.centerx - sprite.rect.centerx) / (sprite.rect.width / 2)
                offset = max(-1.0, min(1.0, offset))

                direction = pygame.Vector2(offset, -1).normalize()
                self.velocity = direction * self.speed

        if self.rect.bottom >= h:
            state = "game over"



def reset_game():
    global score
    score = 0
    paddle.reset_position(w / 2)
    ball.reset()


for _ in range(20):
    new_coin = Coin((all_sprites, coins))
    new_coin.respawn()

paddle = Paddle(w / 2, h - 50, 150, 20, 600, pygame.K_a, pygame.K_d, (all_sprites, paddles))
ball = Ball(w / 2, h / 2, 400.0, all_sprites)

score = 0
state = "start"
running = True

async def main():
    global coin, dt, event, msg, msg_2, running, score, state, sub_msg, text, title
    while running:
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if state == "start" and event.key == pygame.K_SPACE:
                    reset_game()
                    state = "playing"
                elif state in ("game over", "win") and event.key == pygame.K_r:
                    reset_game()
                    state = "playing"
                elif state in ("game over", "win") and event.key == pygame.K_q:
                    running = False

        dt = clock.tick(60) / 1000.0
        screen.fill("black")

        if state == "start":
            title = large_font.render("Collector Pong", True, "white")
            msg = font.render("Press SPACE to Start", True, "white")
            msg_2 = font.render("Collect 25 coins to win", True, "white")
            screen.blit(title, (w / 2 - title.get_width() / 2, h / 2 - 100))
            screen.blit(msg, (w / 2 - msg.get_width() / 2, h / 2))
            screen.blit(msg_2, (w / 2 - msg_2.get_width() / 2, h / 2 + 50))

        elif state == "playing":
            all_sprites.update(dt)
            text = font.render(f"Coins Collected:{str(score)}", True, "white")

            for coin in pygame.sprite.spritecollide(ball, coins, False):
                score += 1
                coin.respawn()

            if score >= 25:
                state = "win"

            all_sprites.draw(screen)
            screen.blit(text, (w / 2 - text.get_width() / 2, 20))

        elif state == "win":
            msg = large_font.render("You Win!", True, "green")
            sub_msg = font.render("Press 'Q' to Quit and 'R' to Restart", True, "white")
            all_sprites.draw(screen)
            screen.blit(msg, (w / 2 - msg.get_width() / 2, h / 2 - 50))
            screen.blit(sub_msg, (w / 2 - sub_msg.get_width() / 2, h / 2 + 20))

        elif state == "game over":
            msg = large_font.render("Game Over!", True, "red")
            sub_msg = font.render("Press 'Q' to Quit and 'R' to Restart", True, "white")
            all_sprites.draw(screen)
            screen.blit(msg, (w / 2 - msg.get_width() / 2, h / 2 - 50))
            screen.blit(sub_msg, (w / 2 - sub_msg.get_width() / 2, h / 2 + 20))

        pygame.display.update()

    pygame.quit()

asyncio.run(main())
