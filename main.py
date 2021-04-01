import os
import sys
import random

import pygame
import pickle
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT
)

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 600
SCREEN_RECT = (0, 0, WINDOW_WIDTH, WINDOW_WIDTH)
TIMER_EVENT_TYPE = 30
DATA_DIR = "data"
GRAVITY = 0
BOMB_SPRITES = pygame.sprite.Group()
STAR_SPRITES = pygame.sprite.Group()
ALL_SPRITES = pygame.sprite.Group()
TORP_SPRITES = pygame.sprite.Group()
# создадим группу, содержащую все спрайты
all_sprites = pygame.sprite.Group()
# инициализация
size = WINDOW_SIZE
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((1, 1))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Submarine(pygame.sprite.Sprite):

    def __init__(self):
        super(Submarine, self).__init__()
        self.lives = 9
        self.width = 200
        self.height = 60
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = random.randint(0, WINDOW_HEIGHT - self.height)
        self.delay = 1000
        self.score = 0
        self.is_paused = False
        self.pic = AnimatedSprite(load_image("submarine4.png", -1), 1, 5, 1, 1, 18)
        self.surf = self.pic.surf
        self.rect = self.pic.rect
        self.rect.center = (200, 400)
        # self.pic.update()
        pygame.time.set_timer(TIMER_EVENT_TYPE, self.delay)

    def render(self, screen):
        font = pygame.font.Font(None, 30)
        """
        text = font.render("Click me!", True, (50, 70, 0))
        pygame.draw.rect(screen, (200, 150, 50), (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + (self.width - text.get_width()) // 2,
                    self.y + (self.height - text.get_height()) // 2))
        """
        text = font.render(f"Очков: {self.score}", True, (200, 200, 200))
        screen.blit(text, (20, 20))
        text = font.render(f"Жизней: {self.lives}", True, (200, 200, 200))
        screen.blit(text, (400, 20))

    def update_(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -1)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 1)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-1, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(1, 0)
        # проверяем чтобы лодка была на экране
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

    def update(self):
        pass
        # self.pic.update()

    def move(self):
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = random.randint(0, WINDOW_HEIGHT - self.height)

    def check_click(self, pos):
        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            self.move()
            self.delay = max(50, self.delay - 50)
            self.score += 1
            pygame.time.set_timer(TIMER_EVENT_TYPE, self.delay)

    def collect(self):
        self.score += 1

    def boom(self):
        create_particles(self.rect.center)
        self.lives -= 1

    def switch_pause(self):
        self.is_paused = not self.is_paused
        pygame.time.set_timer(TIMER_EVENT_TYPE, self.delay if not self.is_paused else 0)


class Bomb(pygame.sprite.Sprite):

    def __init__(self):
        super(Bomb, self).__init__()
        self.surf = load_image("bomb.png", -1)
        # Начальная позиция генерируется случайным образом, как и скорость
        self.rect = self.surf.get_rect(
            center=(
                WINDOW_WIDTH,
                random.randint(0, WINDOW_HEIGHT),
            )
        )
        self.speed = 1

    def boom(self):
        create_particles(self.rect.center)
        self.kill()

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class Torp(pygame.sprite.Sprite):

    def __init__(self, pos):
        super(Torp, self).__init__()
        self.pic = AnimatedSprite(load_image("torpeda4.png", -1), 3, 2, 320, 113, 1)
        self.surf = self.pic.surf
        self.rect = self.pic.rect
        # Начальная позиция генерируется случайным образом, как и скорость
        self.rect.center = pos
        self.speed = 1

    def boom(self):
        create_particles(self.rect.center)
        self.pic.live = False

    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.left > WINDOW_WIDTH:
            self.pic.live = False
            self.kill()


class Star(pygame.sprite.Sprite):

    def __init__(self):
        super(Star, self).__init__()
        self.surf = load_image("star.png", -1)
        # Начальная позиция генерируется случайным образом, как и скорость
        self.rect = self.surf.get_rect(
            center=(
                WINDOW_WIDTH,
                random.randint(0, WINDOW_HEIGHT),
            )
        )
        self.speed = 1

    def boom(self):
        self.kill()

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


def main():

    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    start_screen()
    pygame.mixer.music.load('data/background_music.mp3')
    pygame.mixer.music.play(-1)
    size = WINDOW_SIZE
    screen = pygame.display.set_mode(size)
    ADDBOMB = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDBOMB, 500)
    # clickme = Submarine()
    sub = Submarine()
    # создадим группу, содержащую все спрайты
    # all_sprites = pygame.sprite.Group()
    # создадим спрайт
    # all_sprites.add(sub)

    running = True
    while running:


        running = True
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            if event.type == TIMER_EVENT_TYPE:
                sub.move()
            if event.type == pygame.MOUSEBUTTONDOWN:
                sub.check_click(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not TORP_SPRITES:
                    new_torp = Torp(sub.rect.center)
                    TORP_SPRITES.add(new_torp)
                    ALL_SPRITES.add(new_torp)
                    TORP_SPRITES.update()
                if event.key == pygame.K_p:
                    sub.switch_pause()
                if event.key == pygame.K_s:
                    with open(f"{DATA_DIR}/save.dat", "wb") as file:
                        pickle.dump(sub, file)
                if event.key == pygame.K_l:
                    with open(f"{DATA_DIR}/save.dat", "rb") as file:
                        sub = pickle.load(file)
            if event.type == ADDBOMB:
                # Создаем новую бомбу и добавляем ее в группы спрайтов
                new_bomb = Bomb()
                BOMB_SPRITES.add(new_bomb)
                ALL_SPRITES.add(new_bomb)
                BOMB_SPRITES.update()
                new_star = Star()
                STAR_SPRITES.add(new_star)
                ALL_SPRITES.add(new_star)
                STAR_SPRITES.update()
                pos = (sub.rect.center[0] - 50, sub.rect.center[1])
                create_booble(pos)

        # обновление подлодки
        pressed_keys = pygame.key.get_pressed()
        sub.update_(pressed_keys)
        # Обновление мин

        # отрисовка и изменение свойств объектов
        # ...
        # Обновление
        ALL_SPRITES.update()
        screen.fill((27, 148, 180))
        sub.render(screen)

        # BOMB_SPRITES.draw(screen)
        for entity in ALL_SPRITES:
            screen.blit(entity.surf, entity.rect)
        if pygame.sprite.spritecollide(sub, BOMB_SPRITES, True):
            sub.boom()
        if pygame.sprite.spritecollide(sub, STAR_SPRITES, True):
            sub.collect()
        if TORP_SPRITES and pygame.sprite.groupcollide(TORP_SPRITES, BOMB_SPRITES, True, True):
            new_torp.boom()

            # sub.render(screen)
        # обновление экрана
        pygame.display.flip()
    pygame.quit()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 100
    # возможные скорости
    numbers = [-3, -2, -1, 1, 2, 3]
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers), "star1.png", 0, 1)


def create_booble(position):
    # количество создаваемых частиц
    particle_count = 3
    # возможные скорости
    numbers = [-14, -13, -12, -11]
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers), "booble.png", -1, 25)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, delay):
        super().__init__(ALL_SPRITES)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.live = True
        self.delay = delay
        # self.image = self.frames[self.cur_frame]
        self.surf = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if pygame.time.get_ticks() % self.delay == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            # self.image = self.frames[self.cur_frame]
            self.surf = self.frames[self.cur_frame]
            if not self.live:
                self.kill()


class Particle(pygame.sprite.Sprite):

    def __init__(self, pos, dx, dy, name, gravity, delay):
        super().__init__(ALL_SPRITES)
        self.name = name
        self.fire = []
        f = load_image(self.name, -1)
        self.fire.append(f)
        for scale in (5, 10, 20):
            self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))

        self.delay = delay

        self.surf = random.choice(self.fire)
        self.rect = self.surf.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация
        self.gravity = gravity

        # сгенерируем частицы разного размера

    def update(self):
        if pygame.time.get_ticks() % self.delay == 0:
            # применяем гравитационный эффект:
            # движение с ускорением под действием гравитации
            self.velocity[1] += self.gravity
            # перемещаем частицу
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
            # убиваем, если частица ушла за экран
            if not self.rect.colliderect(SCREEN_RECT):
                self.kill()


# Заставка и экран конца игры
def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ПОДВИГ <<МАЛЮТКИ>>", "",
                  "Правила игры",
                  "Подводная лодка <<МАЛЮТКА>> должна собирать звездочки и уклоняться от мин.",
                  "Подрыв на мине уменьшает живучесть лодки."]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        # pygame.time.set_timer(TIMER_EVENT_TYPE, 50)


# Заставка и экран конца игры

if __name__ == '__main__':
    main()
