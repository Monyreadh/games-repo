import asyncio
import json
import random

import pygame
import sys

if sys.platform == "emscripten":
    import platform

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bok-Bok")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 42)
big_font = pygame.font.Font(None, 75)
title_font = pygame.font.Font(None, 110)
HIGHSCORE_FILE = "highscore.json"

# Settings
GRAVITY = 1500
JUMP = -500
HORIZON = 145
FOCAL = 280
CAM_H = 4
Z_PLAYER = 3
Z_NEAR = 2.5
Z_FAR = 60
LANE_X = [-1.6, 0, 1.6]
ROAD_HALF = 3.5
SEG = 2
START_SPEED = 14
MAX_SPEED = 28
lanes = [-1, 0, 1]

# Colors
SKY = (115, 195, 245)
GRASS = (85, 165, 65)
ROAD = (165, 115, 70)
ROAD_ALT = (150, 103, 63)
ROAD_EDGE = (225, 190, 120)
WHITE = (255, 255, 255)

# Buttons
start_button = pygame.Rect(WIDTH // 2 - 140, 365, 280, 75)
again_button = pygame.Rect(WIDTH // 2 - 140, 420, 280, 70)


# High score
def load_high_score():
    try:
        if sys.platform == "emscripten":
            return int(platform.window.localStorage.getItem("tka.bok-bok.high-score") or 0)
        with open(HIGHSCORE_FILE, "r") as file:
            return int(json.load(file).get("high_score", 0))
    except Exception:
        return 0


def save_high_score(value):
    try:
        if sys.platform == "emscripten":
            platform.window.localStorage.setItem("tka.bok-bok.high-score", str(value))
        else:
            with open(HIGHSCORE_FILE, "w") as file:
                json.dump({"high_score": value}, file)
    except Exception:
        pass  # Restricted browser storage must not interrupt a game.


high_score = load_high_score()


# Load images
def load_gif(path, max_width, max_height):
    # GIFs are expanded to PNG frames before deployment; Pillow is not needed in-browser.
    with open("animations.json", encoding="utf-8") as file:
        manifest = json.load(file)
    frames = []
    for filename, duration in manifest[path]:
        surface = pygame.image.load(filename).convert_alpha()
        width, height = surface.get_size()
        scale = min(max_width / width, max_height / height)
        size = (max(1, int(width * scale)), max(1, int(height * scale)))
        frames.append((pygame.transform.smoothscale(surface, size), duration))
    return frames


def load_image(path):
    return pygame.image.load(path).convert_alpha()


# Chicken animations
chicken_frames = load_gif("New Piskel.gif", 100, 110)
jump_frames = load_gif("New Piskel (4).gif", 100, 110)

# Monster and animal animations
monster_frames = load_gif("New Piskel (2).gif", 100, 100)
animal_frames = load_gif("New Piskel (3).gif", 100, 100)

# Other images
egg_image = load_image("New Piskel (6).png")
tree_image = load_image("New Piskel (1).png")
rock_image = load_image("New Piskel (1) (1).png")


# Fake 3D projection
def project(x, z):
    z = max(Z_NEAR, z)
    scale = FOCAL / z
    screen_x = WIDTH / 2 + x * scale
    screen_y = HORIZON + CAM_H * scale
    return screen_x, screen_y, scale


def fade(color, z):
    amount = min(1, z / Z_FAR) * 0.8
    return pygame.Color(color).lerp(SKY, amount)


def lane_position(lane, z):
    return project(LANE_X[lane + 1], z)


def draw_image(image, x, y, width, height):
    width = max(1, int(width))
    height = max(1, int(height))
    scaled_image = pygame.transform.smoothscale(image, (width, height))
    rect = scaled_image.get_rect()
    rect.midbottom = (int(x), int(y))
    screen.blit(scaled_image, rect)


# Draw buttons
def draw_button(rect, text, mouse_pos):
    color = (235, 190, 85) if rect.collidepoint(mouse_pos) else (210, 155, 60)
    pygame.draw.rect(screen, color, rect, border_radius=16)
    pygame.draw.rect(screen, (100, 65, 35), rect, 4, border_radius=16)
    button_text = button_font.render(text, True, (65, 40, 25))
    screen.blit(
        button_text,
        (
            rect.centerx - button_text.get_width() // 2,
            rect.centery - button_text.get_height() // 2,
        ),
    )


def draw_centered_text(text, text_font, color, y):
    rendered = text_font.render(text, True, color)
    screen.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, y))


# Player
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.run_frames = chicken_frames
        self.jump_frames = jump_frames
        self.frames = self.run_frames
        self.frame_index = 0
        self.animation_timer = 0
        self.image = self.frames[0][0]
        self.rect = self.image.get_frect()
        self.lane = 0
        self.jump_height = 0
        self.jump_velocity = 0
        self.on_ground = True

    def move_left(self):
        self.lane = max(-1, self.lane - 1)

    def move_right(self):
        self.lane = min(1, self.lane + 1)

    def jump(self):
        if self.on_ground:
            self.jump_velocity = JUMP
            self.on_ground = False
            self.frames = self.jump_frames
            self.frame_index = 0
            self.animation_timer = 0
            self.image = self.frames[0][0]

    def update(self, dt):
        if not self.on_ground:
            self.jump_height += -self.jump_velocity * dt
            self.jump_velocity += GRAVITY * dt
            if self.jump_height <= 0:
                self.jump_height = 0
                self.jump_velocity = 0
                self.on_ground = True
                self.frames = self.run_frames
                self.frame_index = 0
                self.animation_timer = 0
                self.image = self.frames[0][0]

        self.animation_timer += dt
        if self.animation_timer >= self.frames[self.frame_index][1]:
            self.animation_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[self.frame_index][0]

    def draw(self):
        x, y, scale = project(LANE_X[self.lane + 1], Z_PLAYER)
        y -= self.jump_height
        width = 0.95 * scale
        height = 1.15 * scale
        draw_image(self.image, x, y, width, height)


# Moving objects
class MovingObject(pygame.sprite.Sprite):
    def __init__(self, kind, lane, z, groups):
        super().__init__(groups)
        self.kind = kind
        self.lane = lane
        self.z = z
        self.previous_z = z
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_frect()

    def update(self, dt, speed):
        self.previous_z = self.z
        self.z -= speed * dt


# Scenery
class SceneryObject(pygame.sprite.Sprite):
    def __init__(self, kind, side, z, groups):
        super().__init__(groups)
        self.kind = kind
        self.side = side
        self.z = z
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_frect()

    def update(self, dt, speed):
        self.z -= speed * dt


# Bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, lane, z, groups):
        super().__init__(groups)
        self.lane = lane
        self.z = z
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_frect()

    def update(self, dt):
        self.z += 35 * dt


# Farm scenery
def scenery_position(item):
    x = item.side * (ROAD_HALF + 2.2)
    return project(x, item.z)


def draw_scenery(item):
    x, y, scale = scenery_position(item)
    color = fade((35, 120, 45), item.z)

    if item.kind == "tree":
        trunk_width = max(2, int(0.15 * scale))
        trunk_height = max(3, int(0.7 * scale))
        crown_size = max(3, int(0.55 * scale))
        pygame.draw.rect(
            screen,
            fade((110, 70, 35), item.z),
            (
                int(x - trunk_width / 2),
                int(y - trunk_height),
                trunk_width,
                trunk_height,
            ),
        )
        pygame.draw.circle(
            screen, color, (int(x), int(y - trunk_height - crown_size // 2)), crown_size
        )

    elif item.kind == "barn":
        width = max(4, int(0.9 * scale))
        height = max(4, int(0.7 * scale))
        pygame.draw.rect(
            screen,
            fade((165, 65, 45), item.z),
            (int(x - width / 2), int(y - height), width, height),
        )
        pygame.draw.polygon(
            screen,
            fade((100, 45, 35), item.z),
            [
                (int(x - width / 2 - 0.1 * scale), int(y - height)),
                (int(x), int(y - height - 0.4 * scale)),
                (int(x + width / 2 + 0.1 * scale), int(y - height)),
            ],
        )


# Side-of-road decorative fences
def draw_side_fence(side):
    points = []
    z = Z_NEAR
    while z <= Z_FAR:
        x = side * ROAD_HALF
        screen_x, screen_y, scale = project(x, z)
        points.append((screen_x, screen_y, scale, z))
        z += 2

    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        for level in [0.35, 0.8]:
            start = (int(p1[0]), int(p1[1] - p1[2] * 0.35 * level))
            end = (int(p2[0]), int(p2[1] - p2[2] * 0.35 * level))
            pygame.draw.line(
                screen,
                fade((115, 70, 35), p2[3]),
                start,
                end,
                max(1, int(0.06 * p2[2])),
            )

    for x, y, scale, z in points:
        pygame.draw.line(
            screen,
            fade((95, 55, 30), z),
            (int(x), int(y)),
            (int(x), int(y - 0.35 * scale)),
            max(1, int(0.06 * scale)),
        )


# Road
travel = 0


def draw_road():
    z = Z_NEAR
    while z < Z_FAR:
        segment_position = (z + travel) % SEG
        slice_length = SEG - segment_position
        if slice_length < 0.001:
            slice_length = SEG
        next_z = min(z + slice_length, Z_FAR)
        band = int((z + travel) // SEG) % 2
        road_color = ROAD if band == 0 else ROAD_ALT

        left_near = project(-ROAD_HALF, z)
        right_near = project(ROAD_HALF, z)
        left_far = project(-ROAD_HALF, next_z)
        right_far = project(ROAD_HALF, next_z)

        pygame.draw.polygon(
            screen,
            fade(road_color, z),
            [
                (int(left_far[0]), int(left_far[1])),
                (int(right_far[0]), int(right_far[1])),
                (int(right_near[0]), int(right_near[1])),
                (int(left_near[0]), int(left_near[1])),
            ],
        )
        pygame.draw.line(
            screen,
            fade(ROAD_EDGE, z),
            (int(left_far[0]), int(left_far[1])),
            (int(left_near[0]), int(left_near[1])),
            max(1, int(0.07 * left_near[2])),
        )
        pygame.draw.line(
            screen,
            fade(ROAD_EDGE, z),
            (int(right_far[0]), int(right_far[1])),
            (int(right_near[0]), int(right_near[1])),
            max(1, int(0.07 * right_near[2])),
        )

        if band == 0:
            for boundary in [-0.8, 0.8]:
                near = project(boundary, z)
                far = project(boundary, next_z)
                pygame.draw.line(
                    screen,
                    fade((235, 205, 155), z),
                    (int(near[0]), int(near[1])),
                    (int(far[0]), int(far[1])),
                    max(1, int(0.025 * near[2])),
                )
        z = next_z


# Background
def draw_background():
    screen.fill(SKY)
    pygame.draw.circle(screen, (255, 225, 100), (760, 75), 40)
    pygame.draw.ellipse(screen, (100, 175, 85), (-150, 100, 500, 160))
    pygame.draw.ellipse(screen, (90, 160, 75), (400, 100, 650, 170))
    pygame.draw.rect(screen, GRASS, (0, HORIZON, WIDTH, HEIGHT - HORIZON))
    draw_road()
    draw_side_fence(-1)
    draw_side_fence(1)


# Short wooden obstacle fence
def draw_obstacle_fence(lane, z):
    center = LANE_X[lane + 1]
    left_x = center - 0.45
    right_x = center + 0.45
    left = project(left_x, z)
    right = project(right_x, z)
    color = fade((115, 70, 35), z)
    dark_color = fade((85, 50, 25), z)

    for level in [0.25, 0.55]:
        left_point = (int(left[0]), int(left[1] - left[2] * level))
        right_point = (int(right[0]), int(right[1] - right[2] * level))
        pygame.draw.line(
            screen, color, left_point, right_point, max(1, int(0.08 * left[2]))
        )

    for point in [left, right]:
        pygame.draw.line(
            screen,
            dark_color,
            (int(point[0]), int(point[1])),
            (int(point[0]), int(point[1] - point[2] * 0.7)),
            max(1, int(0.09 * point[2])),
        )


def draw_object(obj):
    x, y, scale = lane_position(obj.lane, obj.z)

    if obj.kind == "rock":
        width = 0.95 * scale
        height = 0.65 * scale
        draw_image(rock_image, x, y, width, height)

    elif obj.kind == "tree":
        width = max(1, int(1.4 * scale))
        height = max(1, int(1.8 * scale))
        draw_image(tree_image, x, y, width, height)

    elif obj.kind == "fence":
        draw_obstacle_fence(obj.lane, obj.z)

    elif obj.kind == "egg":
        draw_image(egg_image, x, y, 0.42 * scale, 0.58 * scale)

    elif obj.kind == "animal":
        animal_image = animal_frames[animal_animation_index][0]
        draw_image(animal_image, x, y, 0.9 * scale, 0.9 * scale)

    elif obj.kind == "monster":
        monster_image = monster_frames[monster_animation_index][0]
        draw_image(monster_image, x, y, 1.5 * scale, 1.7 * scale)


# Bullets
def draw_bullet(bullet):
    x, y, scale = lane_position(bullet.lane, bullet.z)
    draw_image(egg_image, x, y, 0.22 * scale, 0.3 * scale)


# Spawn objects
def spawn_wave():
    occupied_lanes = random.sample(lanes, 2)
    monster_chance = min(0.55, 0.35 + score / 20000)

    for lane in occupied_lanes:
        if random.random() < monster_chance:
            kind = "monster"
        else:
            kind = random.choices(
                ["rock", "tree", "fence", "egg", "animal"], weights=[30, 18, 20, 17, 15]
            )[0]
        MovingObject(kind, lane, Z_FAR, objects)


def spawn_scenery():
    for side in [-1, 1]:
        kind = random.choices(["tree", "barn"], weights=[65, 35])[0]
        SceneryObject(kind, side, Z_FAR, scenery)


# Shooting
def shoot():
    global eggs
    if eggs > 0:
        eggs -= 1
        Bullet(player.lane, Z_PLAYER, bullets)


# Reset game
def reset_game():
    global score, eggs, rescues
    global game_over, game_state, game_speed
    global spawn_timer, scenery_timer
    global shoot_cooldown
    global monster_animation_index, monster_animation_timer
    global animal_animation_index, animal_animation_timer
    global travel

    player.lane = 0
    player.jump_height = 0
    player.jump_velocity = 0
    player.on_ground = True
    player.frames = player.run_frames
    player.frame_index = 0
    player.animation_timer = 0
    player.image = player.frames[0][0]

    objects.empty()
    bullets.empty()
    scenery.empty()

    score = 0
    eggs = 0
    rescues = 0
    game_over = False
    game_state = "playing"
    game_speed = START_SPEED
    spawn_timer = 0
    scenery_timer = 0
    shoot_cooldown = 0
    monster_animation_index = 0
    monster_animation_timer = 0
    animal_animation_index = 0
    animal_animation_timer = 0
    travel = 0

    for i in range(8):
        for side in [-1, 1]:
            kind = random.choice(["tree", "barn"])
            SceneryObject(kind, side, Z_FAR - i * 7, scenery)


# Game groups
all_sprites = pygame.sprite.Group()
objects = pygame.sprite.Group()
bullets = pygame.sprite.Group()
scenery = pygame.sprite.Group()
player = Player(all_sprites)

# Initial scenery
for i in range(8):
    for side in [-1, 1]:
        kind = random.choice(["tree", "barn"])
        SceneryObject(kind, side, Z_FAR - i * 7, scenery)

# Game variables
score = 0
eggs = 0
rescues = 0
game_over = False
game_state = "menu"
game_speed = START_SPEED
spawn_timer = 0
scenery_timer = 0
shoot_cooldown = 0
monster_animation_index = 0
monster_animation_timer = 0
animal_animation_index = 0
animal_animation_timer = 0

# Main loop
running = True
async def main():
    global animal_animation_index, animal_animation_timer, behind, bullet, crossed_player, dt, eggs, event, game_over, game_speed, game_state, high_score, hint, in_front, item, monster_animation_index, monster_animation_timer, mouse_pos, obj, overlay, rescues, running, scenery_timer, score, shoot_cooldown, spawn_timer, travel
    while running:
        await asyncio.sleep(0)
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "menu" and start_button.collidepoint(event.pos):
                    reset_game()
                elif game_state == "game_over" and again_button.collidepoint(event.pos):
                    reset_game()

            if event.type == pygame.KEYDOWN:
                if game_state == "menu":
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        reset_game()

                elif game_state == "game_over":
                    if event.key in [pygame.K_r, pygame.K_RETURN, pygame.K_SPACE]:
                        reset_game()

                elif game_state == "playing":
                    if event.key in [pygame.K_a, pygame.K_LEFT]:
                        player.move_left()
                    if event.key in [pygame.K_d, pygame.K_RIGHT]:
                        player.move_right()
                    if event.key in [pygame.K_w, pygame.K_UP]:
                        player.jump()
                    if event.key == pygame.K_SPACE and shoot_cooldown <= 0:
                        shoot()
                        shoot_cooldown = 0.35

        # Update game
        if game_state == "playing":
            score += 20 * dt
            game_speed = min(MAX_SPEED, START_SPEED + score / 1000)
            travel += game_speed * dt
            player.update(dt)

            spawn_timer -= dt
            if spawn_timer <= 0:
                spawn_wave()
                spawn_timer = max(0.45, random.uniform(0.65, 0.9) - score / 30000)

            scenery_timer -= dt
            if scenery_timer <= 0:
                spawn_scenery()
                scenery_timer = random.uniform(0.65, 1.0)

            objects.update(dt, game_speed)
            scenery.update(dt, game_speed)
            bullets.update(dt)

            for obj in objects.copy():
                if obj.z <= Z_NEAR:
                    obj.kill()

            for item in scenery.copy():
                if item.z <= Z_NEAR:
                    item.kill()

            for bullet in bullets.copy():
                if bullet.z >= Z_FAR:
                    bullet.kill()

            shoot_cooldown = max(0, shoot_cooldown - dt)

            # Collision checks
            for obj in objects.copy():
                crossed_player = obj.previous_z > Z_PLAYER and obj.z <= Z_PLAYER

                if crossed_player and obj.lane == player.lane:
                    if obj.kind == "egg":
                        eggs += 1
                        score += 100
                        obj.kill()
                    elif obj.kind == "animal":
                        rescues += 1
                        score += 200
                        obj.kill()
                    elif obj.kind == "monster":
                        game_over = True
                    elif obj.kind == "tree":
                        game_over = True
                    elif obj.kind in ["rock", "fence"]:
                        if player.jump_height < 65:
                            game_over = True

            # Bullet hits
            for bullet in bullets.copy():
                for obj in objects.copy():
                    if (
                        obj.kind == "monster"
                        and obj.lane == bullet.lane
                        and abs(obj.z - bullet.z) < 0.6
                    ):
                        obj.kill()
                        bullet.kill()
                        score += 150
                        break

            # Monster animation
            monster_animation_timer += dt
            if monster_animation_timer >= monster_frames[monster_animation_index][1]:
                monster_animation_timer = 0
                monster_animation_index += 1
                if monster_animation_index >= len(monster_frames):
                    monster_animation_index = 0

            # Animal animation
            animal_animation_timer += dt
            if animal_animation_timer >= animal_frames[animal_animation_index][1]:
                animal_animation_timer = 0
                animal_animation_index += 1
                if animal_animation_index >= len(animal_frames):
                    animal_animation_index = 0

            # Save high score when the player loses
            if game_over:
                game_state = "game_over"
                if int(score) > high_score:
                    high_score = int(score)
                    save_high_score(high_score)

        # Draw everything
        draw_background()

        behind = sorted(
            [obj for obj in objects if obj.z > Z_PLAYER], key=lambda obj: -obj.z
        )
        in_front = sorted(
            [obj for obj in objects if obj.z <= Z_PLAYER], key=lambda obj: -obj.z
        )

        for item in sorted(scenery, key=lambda item: -item.z):
            draw_scenery(item)

        for obj in behind:
            draw_object(obj)

        player.draw()

        for obj in in_front:
            draw_object(obj)

        for bullet in bullets:
            draw_bullet(bullet)

        # Game UI
        screen.blit(font.render(f"Score: {int(score)}", True, WHITE), (20, 20))
        draw_image(egg_image, 45, 110, 32, 38)
        screen.blit(font.render(f"Egg Ammo: {eggs}", True, WHITE), (70, 82))
        screen.blit(font.render(f"Chick Rescues: {rescues}", True, WHITE), (20, 145))

        # Start screen
        if game_state == "menu":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((65, 65, 65, 165))
            screen.blit(overlay, (0, 0))

            draw_centered_text("BOK-BOK", title_font, WHITE, 185)
            draw_centered_text("OPERATION: SAVE THE FARM", font, WHITE, 285)
            draw_button(start_button, "START GAME", mouse_pos)

            hint = font.render("Press ENTER to start", True, WHITE)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 465))

        # Game-over screen
        elif game_state == "game_over":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((45, 45, 45, 190))
            screen.blit(overlay, (0, 0))

            draw_centered_text("YOU DIED", title_font, WHITE, 105)
            draw_centered_text(f"High Score: {high_score}", font, WHITE, 230)
            draw_centered_text(f"Score: {int(score)}", font, WHITE, 275)
            draw_centered_text(f"Chick Rescued: {rescues}", font, WHITE, 320)
            draw_button(again_button, "PLAY AGAIN", mouse_pos)

            hint = font.render("Press R to play again", True, WHITE)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 510))

        pygame.display.flip()

    pygame.quit()


asyncio.run(main())
