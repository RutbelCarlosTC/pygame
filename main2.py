import pygame
import math
import random
from pygame import mixer

# Initialize the pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))

# Background
# Backgrounds
backgrounds = [
    pygame.transform.scale(pygame.image.load('background1.jpg'), (800, 600)),
    pygame.transform.scale(pygame.image.load('background2.jpg'), (800, 600)),
    pygame.transform.scale(pygame.image.load('background3.jpg'), (800, 600)),
    pygame.transform.scale(pygame.image.load('background4.jpg'), (800, 600)),
    pygame.transform.scale(pygame.image.load('background5.jpg'), (800, 600))
]
current_background_index = 0


# Background Sound
mixer.music.load('background.mp3')
mixer.music.play(-1)

# Title and icon
pygame.display.set_caption("Space Invaders Enhanced")
icon = pygame.image.load('ufo.png')
icon = pygame.transform.scale(icon, (32, 32))
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('player.png')
playerImg = pygame.transform.scale(playerImg, (64, 64))

playerX = 370
playerY = 480
playerX_change = 0
player_speed = 4
player_lives = 3

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6
enemy_speed_multiplier = 1.0

for i in range(num_of_enemies):
    img = pygame.image.load('enemy.png')
    img = pygame.transform.scale(img, (60, 60))
    enemyImg.append(img)
    enemyX.append(random.randint(0, 735))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(2)
    enemyY_change.append(10)

# Multiple bullets system
bullets = []
max_bullets = 5
bulletImg = pygame.image.load('bullet.png')
bulletImg = pygame.transform.scale(bulletImg, (50, 50))
bullet_speed = 8

# Power-ups
powerups = []
powerup_types = ['multi_shot', 'speed_boost', 'extra_life']
powerup_colors = [(255, 255, 0), (0, 255, 255), (255, 0, 255)]  # Yellow, Cyan, Magenta
powerup_active_time = 0
powerup_type_active = None
multi_shot_active = False
speed_boost_active = False

# Score and level system
score_value = 0
level = 1
max_levels = len(backgrounds)
enemies_defeated_this_level = 0
enemies_per_level = 10

# Fonts
font = pygame.font.Font('freesansbold.ttf', 24)
small_font = pygame.font.Font('freesansbold.ttf', 18)
over_font = pygame.font.Font('freesansbold.ttf', 64)
textX = 10
textY = 10

# Game states
game_over = False
game_paused = False
game_won = False

def show_score(x, y):
    score = font.render(f"Puntaje: {score_value}", True, (0, 255, 0))
    screen.blit(score, (x, y))

def show_level(x, y):
    level_text = font.render(f"Nivel: {level}", True, (0, 255, 0))
    screen.blit(level_text, (x, y + 30))

def show_lives(x, y):
    lives_text = font.render(f"Vidas: {player_lives}", True, (255, 0, 0))
    screen.blit(lives_text, (x, y + 60))

def show_powerup_status():
    if powerup_type_active:
        remaining_time = max(0, 300 - powerup_active_time) // 60 + 1
        text = None
        if powerup_type_active == 'multi_shot':
            text = small_font.render(f"Multi-disparo: {remaining_time}s", True, (255, 255, 0))
        elif powerup_type_active == 'speed_boost':
            text = small_font.render(f"Velocidad: {remaining_time}s", True, (0, 255, 255))
        
        if text:
            screen.blit(text, (10, 100))

def game_over_text():
    over_text = over_font.render("FIN DEL JUEGO", True, (255, 0, 0))
    screen.blit(over_text, (150, 250))
    restart_text = font.render("Presiona R para reiniciar", True, (255, 255, 255))
    screen.blit(restart_text, (250, 320))

def victory_text():
    win_text = over_font.render("VICTORIA", True, (255, 215, 0))  # dorado
    screen.blit(win_text, (250, 250))

def pause_text():
    pause_text = over_font.render("PAUSA", True, (255, 255, 0))
    screen.blit(pause_text, (280, 250))
    continue_text = font.render("Presiona P para continuar", True, (255, 255, 255))
    screen.blit(continue_text, (250, 320))

def player(x, y):
    screen.blit(playerImg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def create_bullet(x, y, offset_x=0):
    bullets.append({
        'x': x + 16 + offset_x,
        'y': y + 10,
        'active': True
    })

def create_powerup(x, y):
    powerup_type = random.choices(
        powerup_types, 
        weights=[4, 4, 1],  # multi_shot=40%, speed_boost=40%, extra_life=10%
        k=1
    )[0]
    
    powerups.append({
        'x': x,
        'y': y,
        'type': powerup_type,
        'active': True
    })

def draw_powerup(powerup):
    color_index = powerup_types.index(powerup['type'])
    pygame.draw.circle(screen, powerup_colors[color_index], (int(powerup['x'] + 15), int(powerup['y'] + 15)), 15)
    # Draw power-up symbol
    if powerup['type'] == 'multi_shot':
        pygame.draw.rect(screen, (0, 0, 0), (powerup['x'] + 10, powerup['y'] + 10, 10, 10))
    elif powerup['type'] == 'speed_boost':
        pygame.draw.polygon(screen, (0, 0, 0), [(powerup['x'] + 15, powerup['y'] + 5), 
                                                 (powerup['x'] + 25, powerup['y'] + 15), 
                                                 (powerup['x'] + 15, powerup['y'] + 25), 
                                                 (powerup['x'] + 5, powerup['y'] + 15)])
    elif powerup['type'] == 'extra_life':
        pygame.draw.rect(screen, (0, 0, 0), (powerup['x'] + 12, powerup['y'] + 8, 6, 14))
        pygame.draw.rect(screen, (0, 0, 0), (powerup['x'] + 8, powerup['y'] + 12, 14, 6))

def isCollision(x1, y1, x2, y2, threshold=27):
    distance = math.sqrt((math.pow(x1 - x2, 2)) + (math.pow(y1 - y2, 2)))
    return distance < threshold

def reset_game():
    global playerX, playerY, playerX_change, player_lives, score_value, level
    global enemies_defeated_this_level, game_over, bullets, powerups
    global powerup_active_time, powerup_type_active, multi_shot_active, speed_boost_active
    global enemy_speed_multiplier, enemyX, enemyY
    
    playerX = 370
    playerY = 480
    playerX_change = 0
    player_lives = 3
    score_value = 0
    level = 1
    enemies_defeated_this_level = 0
    game_over = False
    bullets = []
    powerups = []
    powerup_active_time = 0
    powerup_type_active = None
    multi_shot_active = False
    speed_boost_active = False
    enemy_speed_multiplier = 1.0
    
    # Reset enemy positions
    for i in range(num_of_enemies):
        enemyX[i] = random.randint(0, 735)
        enemyY[i] = random.randint(50, 150)

def next_level():
    global level, enemies_defeated_this_level, enemy_speed_multiplier, current_background_index, game_won 
    level += 1
    enemies_defeated_this_level = 0
    enemy_speed_multiplier += 0.5
    
    # Si el jugador ya pasó el último nivel
    if level > max_levels:
        game_won = True
        return

    # Cambiar fondo (cicla entre los disponibles)
    current_background_index = (current_background_index + 1) % len(backgrounds)

    # Reset enemy positions for new level
    for i in range(num_of_enemies):
        enemyX[i] = random.randint(0, 735)
        enemyY[i] = random.randint(50, 150)
        enemyX_change[i] = int(2 * enemy_speed_multiplier)

# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)  # 60 FPS
    screen.fill((0, 0, 0))
    screen.blit(backgrounds[current_background_index], (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and not game_over and not game_paused:
                playerX_change = -player_speed if not speed_boost_active else -player_speed * 1.5
            if event.key == pygame.K_RIGHT and not game_over and not game_paused:
                playerX_change = player_speed if not speed_boost_active else player_speed * 1.5
            if event.key == pygame.K_SPACE and not game_over and not game_paused:
                if len(bullets) < max_bullets:
                    bullet_Sound = mixer.Sound('laser.mp3')
                    bullet_Sound.play()
                    if multi_shot_active:
                        create_bullet(playerX, playerY, -20)
                        create_bullet(playerX, playerY, 0)
                        create_bullet(playerX, playerY, 20)
                    else:
                        create_bullet(playerX, playerY)
            if event.key == pygame.K_p:
                game_paused = not game_paused
            if event.key == pygame.K_r and game_over:
                reset_game()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0
            
    if game_won:
        screen.blit(backgrounds[current_background_index], (0, 0))  # fondo final
        victory_text()
        pygame.display.update()
        continue   # Detiene la lógica del juego, solo muestra victoria

    if not game_paused and not game_over:
        # Player movement
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736


        # Enemy movement
        for i in range(num_of_enemies):
            if enemyY[i] > 440:
                player_lives -= 1
                if player_lives <= 0:
                    game_over = True
                else:
                    # Reset enemy position
                    enemyX[i] = random.randint(0, 735)
                    enemyY[i] = random.randint(50, 150)

            # movimiento clasico para enemigos pares
            enemyX[i] += enemyX_change[i]

            if enemyX[i] <= 0:
                enemyX_change[i] = abs(enemyX_change[i])
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -abs(enemyX_change[i])
                enemyY[i] += enemyY_change[i]
            
            # Movimiento perseguidor para enemigos impares
            if i %2 != 0:
                if playerX > enemyX[i]:
                    enemyX[i] += 0.5   # ajusta velocidad
                elif playerX < enemyX[i]:
                    enemyX[i] -= 0.5

                if playerY > enemyY[i]:
                    enemyY[i] += 0.5
                elif playerY < enemyY[i]:
                    enemyY[i] -= 0.5

        # Bullet movement and collision
        for bullet in bullets[:]:
            if bullet['active']:
                bullet['y'] -= bullet_speed
                
                if bullet['y'] <= 0:
                    bullets.remove(bullet)
                    continue

                # Check collision with enemies
                for i in range(num_of_enemies):
                    if isCollision(enemyX[i], enemyY[i], bullet['x'], bullet['y']):
                        explosion_Sound = mixer.Sound('explosion.mp3')
                        explosion_Sound.play()
                        bullets.remove(bullet)
                        score_value += 1
                        enemies_defeated_this_level += 1
                        
                        # Chance to drop power-up
                        if random.random() < 0.1:  # 30% chance
                            create_powerup(enemyX[i], enemyY[i])
                        
                        enemyX[i] = random.randint(0, 735)
                        enemyY[i] = random.randint(50, 150)
                        break

        # Power-up movement and collision
        for powerup in powerups[:]:
            powerup['y'] += 2
            
            if powerup['y'] > 600:
                powerups.remove(powerup)
                continue
            
            # Check collision with player
            if isCollision(playerX, playerY, powerup['x'], powerup['y'], 40):
                powerups.remove(powerup)
                powerup_type_active = powerup['type']
                powerup_active_time = 0
                
                if powerup['type'] == 'multi_shot':
                    multi_shot_active = True
                elif powerup['type'] == 'speed_boost':
                    speed_boost_active = True
                elif powerup['type'] == 'extra_life':
                    player_lives += 1

        # Power-up timer
        if powerup_type_active:
            powerup_active_time += 1
            if powerup_active_time > 300:  # 5 seconds at 60 FPS
                powerup_type_active = None
                multi_shot_active = False
                speed_boost_active = False

        # Level progression
        if enemies_defeated_this_level >= enemies_per_level:
            next_level()

    # Draw everything
    if not game_over:
        # Draw enemies
        for i in range(num_of_enemies):
            enemy(enemyX[i], enemyY[i], i)
        
        # Draw bullets
        for bullet in bullets:
            if bullet['active']:
                screen.blit(bulletImg, (bullet['x'], bullet['y']))
        
        # Draw power-ups
        for powerup in powerups:
            draw_powerup(powerup)
        
        player(playerX, playerY)
    
    # Draw UI
    show_score(textX, textY)
    show_level(textX + 200, textY)
    show_lives(textX + 400, textY)
    show_powerup_status()
    
    if game_over:
        game_over_text()
    elif game_paused:
        pause_text()
    
    pygame.display.update()

pygame.quit()