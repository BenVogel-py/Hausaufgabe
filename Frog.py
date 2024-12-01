import pygame
import random
import sys

class Settings:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    PLAYER_SIZE = 30
    CAR_WIDTH = 60
    CAR_HEIGHT = 30
    FPS = 60
    START_SPEED = 5
    SAFE_ZONE_HEIGHT = 100  # Sichere Zonen an Anfang und Ende

    # Farben
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

# Initialisiere Pygame
pygame.init()

# Bildschirm einrichten
screen = pygame.display.set_mode((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT))
pygame.display.set_caption("Frosch-Spiel")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Bilder laden
player_image = pygame.image.load("Frosch.png")
player_image = pygame.transform.scale(player_image, (Settings.PLAYER_SIZE, Settings.PLAYER_SIZE))

car_image = pygame.image.load("Auto.png")  # Bild für die Autos
car_image = pygame.transform.scale(car_image, (Settings.CAR_WIDTH, Settings.CAR_HEIGHT))

safe_zone_image = pygame.image.load("Download.png")  # Bild für die sichere Zone
safe_zone_image = pygame.transform.scale(safe_zone_image, (Settings.SCREEN_WIDTH, Settings.SAFE_ZONE_HEIGHT))

# Spielerklasse
class Player:
    def __init__(self):
        self.x = Settings.SCREEN_WIDTH // 2
        self.y = Settings.SCREEN_HEIGHT - Settings.PLAYER_SIZE
        self.size = Settings.PLAYER_SIZE

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x = max(0, min(Settings.SCREEN_WIDTH - self.size, self.x))
        self.y = max(0, min(Settings.SCREEN_HEIGHT - self.size, self.y))

    def draw(self):
        screen.blit(player_image, (self.x, self.y))

    def reset_position(self):
        self.x = Settings.SCREEN_WIDTH // 2
        self.y = Settings.SCREEN_HEIGHT - Settings.PLAYER_SIZE

# Hindernisklasse
class Car:
    def __init__(self, x, y, speed, direction):
        self.x = x
        self.y = y
        self.width = Settings.CAR_WIDTH
        self.height = Settings.CAR_HEIGHT
        self.speed = speed
        self.direction = direction

    def update(self):
        self.x += self.speed * self.direction
        if self.direction == 1 and self.x > Settings.SCREEN_WIDTH:
            self.x = -self.width
        elif self.direction == -1 and self.x + self.width < 0:
            self.x = Settings.SCREEN_WIDTH

    def draw(self):
        screen.blit(car_image, (self.x, self.y))

# Initialisierung
player = Player()
cars = []
speed = Settings.START_SPEED
round_count = 1
score = 0
paused = False

# Zähler für ESC-Taste
exit_press_count = 0  # Zähler für ESC-Taste

# Hindernisse erzeugen
def spawn_cars(round_count):
    global cars
    cars = []
    for _ in range(round_count + 2):
        # Spawn-Höhe in Bereichen außerhalb der sicheren Zonen
        y = random.randint(Settings.SAFE_ZONE_HEIGHT, 
                           Settings.SCREEN_HEIGHT - Settings.SAFE_ZONE_HEIGHT - Settings.CAR_HEIGHT)
        direction = random.choice([-1, 1])
        x = 0 if direction == 1 else Settings.SCREEN_WIDTH
        car = Car(x, y, speed + random.randint(0, 2), direction)
        cars.append(car)

# Punktestand anzeigen
def draw_score():
    score_text = font.render(f"Score: {score}", True, Settings.BLACK)
    screen.blit(score_text, (10, 10))
    round_text = font.render(f"Round: {round_count}", True, Settings.BLACK)
    screen.blit(round_text, (10, 40))

# Sichere Bereiche zeichnen
def draw_safe_zones():
    screen.blit(safe_zone_image, (0, 0))  # Obere sichere Zone
    screen.blit(safe_zone_image, (0, Settings.SCREEN_HEIGHT - Settings.SAFE_ZONE_HEIGHT))  # Untere sichere Zone

# Pause-Modus anzeigen
def draw_pause_overlay():
    overlay = pygame.Surface((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((200, 200, 200, 128))  # Halbtransparentes Grau
    screen.blit(overlay, (0, 0))
    pause_text = font.render("PAUSE", True, Settings.BLACK)
    screen.blit(pause_text, (Settings.SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                             Settings.SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))

# Hindernisse erzeugen
spawn_cars(round_count)

# Hauptspielschleife
while True:
    screen.fill(Settings.WHITE)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Schließen durch "X"
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Pause-Taste
                paused = not paused
            elif event.key == pygame.K_ESCAPE:  # ESC gedrückt
                exit_press_count += 1
                if exit_press_count >= 2:  # Zweimal ESC gedrückt
                    pygame.quit()
                    sys.exit()
            else:
                exit_press_count = 0  # Zähler zurücksetzen, wenn andere Taste gedrückt wird

    if paused:
        draw_pause_overlay()
        pygame.display.flip()
        clock.tick(Settings.FPS)
        continue

    # Spielerbewegung
    dx = dy = 0
    if keys[pygame.K_LEFT]:
        dx = -5
    if keys[pygame.K_RIGHT]:
        dx = 5
    if keys[pygame.K_UP]:
        dy = -5
    if keys[pygame.K_DOWN]:
        dy = 5
    player.move(dx, dy)

    # Hindernisse bewegen
    for car in cars:
        car.update()

    # Kollision prüfen
    for car in cars:
        if (player.x < car.x + car.width and player.x + player.size > car.x and
            player.y < car.y + car.height and player.y + player.size > car.y):
            player.reset_position()
            score = max(0, score - 10)  # Punktabzug bei Kollision

    # Runde gewinnen
    if player.y <= 0:
        round_count += 1
        score += 100  # Punkte für das Erreichen der anderen Seite
        speed += 1
        spawn_cars(round_count)
        player.reset_position()

    # Zeichnen
    draw_safe_zones()  # Sichere Bereiche zeichnen
    player.draw()
    for car in cars:
        car.draw()
    draw_score()

    pygame.display.flip()
    clock.tick(Settings.FPS)
