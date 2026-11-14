import asyncio
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The potato that escaped the kitchen")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

bg_song = pygame.mixer.music.load("songs/bg.wav")
pygame.mixer.music.play(-1, 0.0)
jump_sound = pygame.mixer.Sound("songs/jumpwav.wav")
chefhit_sound = pygame.mixer.Sound("songs/chefhit.wav")
lose_sound = pygame.mixer.Sound("songs/lose.wav")
chefjump_sound = pygame.mixer.Sound("songs/chefjump.wav")
potatowin_sound = pygame.mixer.Sound("songs/potatowin.wav")

GRAVITY = 3600
JUMP = -970
MOVE = 350
MOVE_P = 300

state = "start"


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WIDTH / 2)

        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)


class Potato(pygame.sprite.Sprite):
    def __init__(self, pos, groups, platforms):
        super().__init__(groups)
        potato1 = pygame.transform.scale_by(pygame.image.load("images/potato1.png"), 4)
        potato2 = pygame.transform.scale_by(pygame.image.load("images/potato2.png"), 4)
        potato3 = pygame.transform.scale_by(pygame.image.load("images/potato3.png"), 4)
        self.frames = [
            potato1,
            potato2,
            potato3,
        ]
        self.frame_index = 0
        self.flip = False
        self.image = self.frames[0]
        self.rect = self.image.get_frect(midbottom=pos)
        self.platforms = platforms
        self.direction = pygame.Vector2()
        self.on_floor = False
        self.direction.y = 0
        self.jump_count = 2

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.rect.x += self.direction.x * MOVE_P * dt
        self.rect.x = max(0, min(self.rect.x, 5000 - self.rect.width))

        space_pressed = pygame.key.get_just_pressed()

        if space_pressed[pygame.K_w] and self.jump_count > 0:
            self.direction.y = JUMP
            self.jump_count -= 1
            jump_sound.play()

        old_bottom = self.rect.bottom
        self.direction.y += GRAVITY * dt
        self.rect.y += self.direction.y * dt
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))
        self.on_floor = False

        hits = pygame.sprite.spritecollide(self, self.platforms, False)

        for platform in hits:
            if self.direction.y >= 0 and old_bottom <= platform.rect.top:
                self.rect.bottom = platform.rect.top
                self.direction.y = 0
                self.jump_count = 2
                self.on_floor = True

        self.animate(dt)

    def animate(self, dt):
        if self.direction.x:
            self.frame_index += 10 * dt
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0
        if not self.on_floor:
            self.frame_index = 1
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)


class Chef(pygame.sprite.Sprite):
    def __init__(self, pos, groups, platforms):
        super().__init__(groups)
        chef1 = pygame.transform.scale_by(pygame.image.load("images/chef1.png"), 3)
        chef2 = pygame.transform.scale_by(pygame.image.load("images/chef2.png"), 3)
        chef3 = pygame.transform.scale_by(pygame.image.load("images/chef3.png"), 3)
        self.frames = [
            chef1,
            chef2,
            chef3,
        ]
        self.frame_index = 0
        self.flip = False
        self.image = self.frames[0]
        self.rect = self.image.get_frect(midbottom=pos)
        self.platforms = platforms
        self.direction = pygame.Vector2()
        self.on_floor = False
        self.direction.y = 0
        self.jump_count = 2

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.rect.x += self.direction.x * MOVE * dt
        self.rect.x = max(0, min(self.rect.x, 5000 - self.rect.width))

        space_pressed = pygame.key.get_just_pressed()

        if space_pressed[pygame.K_UP] and self.on_floor:
            self.direction.y = JUMP
            chefjump_sound.play()

        old_bottom = self.rect.bottom
        self.direction.y += GRAVITY * dt
        self.rect.y += self.direction.y * dt
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))
        self.on_floor = False

        hits = pygame.sprite.spritecollide(self, self.platforms, False)

        for platform in hits:
            if self.direction.y >= 0 and old_bottom <= platform.rect.top:
                self.rect.bottom = platform.rect.top
                self.direction.y = 0
                self.on_floor = True

        self.animate(dt)

    def animate(self, dt):
        if self.direction.x:
            self.frame_index += 10 * dt
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0
        if not self.on_floor:
            self.frame_index = 1
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, groups):
        super().__init__(groups)
        self.image = pygame.Surface((w, h))
        self.image.fill("sienna")
        self.rect = self.image.get_frect(topleft=(x, y))


class House(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/house.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect = self.image.get_frect(topleft=(x, y))


all_sprites = AllSprites()
platforms = pygame.sprite.Group()

Platform(0, 670, 5200, 80, (all_sprites, platforms))
house = House(4900, 170, 300, 500, all_sprites)
potato = Potato((200, 625), all_sprites, platforms)
chef = Chef((600, 625), all_sprites, platforms)
Platform(0, 370, 170, 24, (all_sprites, platforms))
Platform(250, 440, 150, 24, (all_sprites, platforms))
Platform(540, 430, 150, 24, (all_sprites, platforms))
Platform(200, 280, 150, 24, (all_sprites, platforms))
Platform(70, 200, 150, 24, (all_sprites, platforms))
Platform(350, 200, 150, 24, (all_sprites, platforms))
Platform(550, 280, 150, 24, (all_sprites, platforms))
Platform(500, 120, 150, 24, (all_sprites, platforms))
Platform(250, 100, 150, 24, (all_sprites, platforms))
Platform(750, 550, 150, 24, (all_sprites, platforms))
Platform(770, 250, 150, 24, (all_sprites, platforms))
Platform(1000, 370, 170, 24, (all_sprites, platforms))
Platform(1250, 440, 150, 24, (all_sprites, platforms))
Platform(1540, 430, 150, 24, (all_sprites, platforms))
Platform(1200, 280, 150, 24, (all_sprites, platforms))
Platform(1070, 200, 150, 24, (all_sprites, platforms))
Platform(1350, 200, 150, 24, (all_sprites, platforms))
Platform(1550, 280, 150, 24, (all_sprites, platforms))
Platform(1500, 120, 150, 24, (all_sprites, platforms))
Platform(1250, 100, 150, 24, (all_sprites, platforms))
Platform(1750, 550, 150, 24, (all_sprites, platforms))
Platform(1770, 250, 150, 24, (all_sprites, platforms))
Platform(2000, 370, 170, 24, (all_sprites, platforms))
Platform(2250, 440, 150, 24, (all_sprites, platforms))
Platform(2540, 430, 150, 24, (all_sprites, platforms))
Platform(2200, 280, 150, 24, (all_sprites, platforms))
Platform(2070, 200, 150, 24, (all_sprites, platforms))
Platform(2350, 200, 150, 24, (all_sprites, platforms))
Platform(2550, 280, 150, 24, (all_sprites, platforms))
Platform(2500, 120, 150, 24, (all_sprites, platforms))
Platform(2250, 100, 150, 24, (all_sprites, platforms))
Platform(2750, 550, 150, 24, (all_sprites, platforms))
Platform(2770, 250, 150, 24, (all_sprites, platforms))
Platform(3000, 370, 170, 24, (all_sprites, platforms))
Platform(3250, 440, 150, 24, (all_sprites, platforms))
Platform(3540, 430, 150, 24, (all_sprites, platforms))
Platform(3200, 280, 150, 24, (all_sprites, platforms))
Platform(3070, 200, 150, 24, (all_sprites, platforms))
Platform(3350, 200, 150, 24, (all_sprites, platforms))
Platform(3550, 280, 150, 24, (all_sprites, platforms))
Platform(3500, 120, 150, 24, (all_sprites, platforms))
Platform(3250, 100, 150, 24, (all_sprites, platforms))
Platform(3750, 550, 150, 24, (all_sprites, platforms))
Platform(3770, 250, 150, 24, (all_sprites, platforms))
Platform(4000, 370, 170, 24, (all_sprites, platforms))
Platform(4250, 440, 150, 24, (all_sprites, platforms))
Platform(4540, 430, 150, 24, (all_sprites, platforms))
Platform(4200, 280, 150, 24, (all_sprites, platforms))
Platform(4070, 200, 150, 24, (all_sprites, platforms))
Platform(4350, 200, 150, 24, (all_sprites, platforms))
Platform(4550, 280, 150, 24, (all_sprites, platforms))
Platform(4500, 120, 150, 24, (all_sprites, platforms))
Platform(4250, 100, 150, 24, (all_sprites, platforms))
Platform(4750, 550, 150, 24, (all_sprites, platforms))
Platform(4770, 250, 150, 24, (all_sprites, platforms))


running = True


async def main():
    global chef_game, dt, event, hint, potato_game, restart_text, running, state, title, win_text
    while running:
        await asyncio.sleep(0)
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "start" and event.key == pygame.K_SPACE:
                    state = "playing"

                if state == "chef_wins" and event.key == pygame.K_r:
                    potato.rect.midbottom = (200, 625)
                    chef.rect.midbottom = (600, 625)

                    state = "playing"

                if state == "potato_wins" and event.key == pygame.K_r:
                    potato.rect.midbottom = (200, 625)
                    chef.rect.midbottom = (600, 625)

                    state = "playing"

        screen.fill("mediumturquoise")

        if state == "start":
            title = font.render("POTATO AND THE CHEF", True, "darkgreen")
            potato_game = font.render(
                "you are the potato:make chef to going out of the screen(can doublejump)",
                True,
                "darkgoldenrod4",
            )
            chef_game = font.render(
                "you are the chef:touch the potato to eat him (bad eyesight)",
                True,
                "navajowhite4",
            )
            hint = font.render("Press SPACE to start", True, "black")

            screen.blit(title, title.get_frect(center=(WIDTH // 2, 250)))
            screen.blit(hint, hint.get_frect(center=(WIDTH // 2, 320)))
            screen.blit(potato_game, potato_game.get_frect(center=(WIDTH // 2, 450)))
            screen.blit(chef_game, chef_game.get_frect(center=(WIDTH // 2, 520)))

        elif state == "playing":
            all_sprites.update(dt)
            all_sprites.draw(potato.rect.center)

            if chef.rect.colliderect(potato.rect):
                chefhit_sound.play()
                state = "chef_wins"
            elif chef.rect.x < potato.rect.x - WIDTH / 2:
                state = "potato_wins"
                lose_sound.play()
            elif potato.rect.colliderect(house.rect):
                potatowin_sound.play()
                state = "potato_wins"

        elif state == "chef_wins":
            win_text = font.render("THE CHEF CAUGHT THE POTATO!", True, "red")
            restart_text = font.render("Press R to restart", True, "black")

            screen.blit(win_text, win_text.get_frect(center=(WIDTH // 2, 300)))
            screen.blit(restart_text, restart_text.get_frect(center=(WIDTH // 2, 400)))

        elif state == "potato_wins":
            win_text = font.render("THE POTATO ESCAPED!", True, "darkgreen")
            restart_text = font.render("Press R to restart", True, "black")

            screen.blit(win_text, win_text.get_frect(center=(WIDTH // 2, 300)))
            screen.blit(restart_text, restart_text.get_frect(center=(WIDTH // 2, 400)))

        pygame.display.update()

    pygame.quit()


asyncio.run(main())
