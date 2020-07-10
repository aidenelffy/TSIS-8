import random
import pygame

RED = (255, 0, 0)
AQUA = (0, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 153, 51)

main_menu_music_path =  'music/JeffSpeed68_-_Bossa_Noir_for_Nights.mp3'
game_music = 'music/JeffSpeed68_-_Bossa_Noir_for_Nights.mp3'

class SceneBase:

    def __init__(self):
        self.next = self

    def process_input(self, pressed_keys: tuple):
        print("you didn't override process_input in the child class")

    def update(self):
       print("you didn't override update in the child class")

    def render(self, screen: pygame.Surface):
      print("you didn't override render in the child class")

    def switch_to_scene(self, next_scene):
        pygame.mixer.music.stop()
        self.next = next_scene

    def terminate(self):
      self.switch_to_scene(None)


class TextScene(SceneBase):
  
    def __init__(self, text: str):
        SceneBase.__init__(self)
        self.text = text
        self.background = pygame.image.load('background.jpg')

    def update(self):
        pass

    def render(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))

        font = pygame.font.SysFont("comicsansms", 20)
        text = font.render(self.text, True, BLACK)
        screen.blit(text, (150 - text.get_width() //
                           2, 240 - text.get_height() // 2))


class TitleScene(TextScene):
  
    def __init__(self):
        TextScene.__init__(self, "Press Enter for begining")
        pygame.mixer.init()
        pygame.mixer.music.load(
            main_menu_music_path)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.2)

    def process_input(self, pressed_keys: tuple):
        if pressed_keys[pygame.K_RETURN]:
            self.switch_to_scene(GameScene())


class GameOverScene(TextScene):
  
    def __init__(self, score: int):
        TextScene.__init__(self, f"Game over! Your score:{score}")

    def process_input(self, pressed_keys: tuple):
        if pressed_keys[pygame.K_RETURN]:
            self.switch_to_scene(TitleScene())


class Food:
   
    def __init__(self, pos: tuple):
        self.pos = pos
        self.color = GREEN

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            self.pos[0], self.pos[1], 10, 10))


class Snake:
 
    def __init__(self):
        self.head_pos = [100, 50]
        self.body_list = [self.head_pos.copy(), [90, 50], [80, 50]]
        self.angle = 0
        self.next_angle = 0

        self.speed = 10

    def change_angle(self):
        if self.angle % 180 != self.next_angle % 180:
            self.angle = self.next_angle

    def change_head_pos(self):
        if self.angle == 0:
            self.head_pos[0] += self.speed
        elif self.angle == 180:
            self.head_pos[0] -= self.speed
        elif self.angle == 90:
            self.head_pos[1] -= self.speed
        elif self.angle == 270:
            self.head_pos[1] += self.speed
        self.head_pos[0] %= 400
        self.head_pos[1] %= 300

    def move(self, food_pos: tuple) -> bool:
        self.body_list.insert(0, list(self.head_pos))

        if list(food_pos) == self.head_pos:
            return True
        else:
            self.body_list.pop()
        return False

    def draw(self, screen: pygame.Surface):
        for pos in self.body_list:
            pygame.draw.rect(screen, RED, pos+[10, 10])

    def check_collision(self, walls: list) -> bool:
        for body in self.body_list[1:]:
            if body == self.head_pos:
                return True
        for wall in walls:
            if list(wall) == self.head_pos:
                return True
        return False

    def can_change_level(self) -> bool:
        return len(self.body_list) == 7  # length of snake = 3


class Wall:
    
    def __init__(self, level: int):
        self.body = []
        self.color = ORANGE
        file = open(f"levels/level{level}.txt", "r")
        row_number = -1
        for row in file:
            row_number += 1
            for colum_number in range(len(row)):
                if row[colum_number] == '#':
                    brick = (colum_number * 10, row_number * 10)
                    self.body.append(brick)

    def draw(self, screen: pygame.Surface):
        for wall in self.body:
            pygame.draw.rect(screen, self.color, (wall[0], wall[1], 10, 10))


class GameScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

        self.snake = Snake()
        self.food = Food((30, 140))
        self.currentLevel = 1
        self.maxLevels = 3

        self.food_sound = pygame.mixer.Sound('sounds/food.wav')
        self.game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')

        self.score = 0

        self.wall = Wall(self.currentLevel)

    def process_input(self, pressed_keys: tuple):
        if pressed_keys[pygame.K_UP]:
            self.snake.next_angle = 90
        elif pressed_keys[pygame.K_DOWN]:
            self.snake.next_angle = 270
        elif pressed_keys[pygame.K_LEFT]:
            self.snake.next_angle = 180
        elif pressed_keys[pygame.K_RIGHT]:
            self.snake.next_angle = 0
        self.snake.change_angle()

    def update(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(
                game_music)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play()
        self.snake.change_head_pos()

        if self.snake.move(self.food.pos):
            self.food_sound.play()
            self.food.pos = (random.randrange(40) * 10,
                             random.randrange(30) * 10)
            self.score += 1
            if self.food.pos in self.snake.body_list or tuple(self.food.pos) in self.wall.body:
                self.food.pos = (30, 140)

        if self.snake.check_collision(self.wall.body):
            self.game_over_sound.play()
            self.switch_to_scene(GameOverScene(self.score))
        else:
            if self.snake.can_change_level():
                self.currentLevel += 1

                if self.currentLevel > self.maxLevels:
                    self.currentLevel = 1

                self.wall = Wall(self.currentLevel)
                self.snake = Snake()
                self.food = Food((30,140))

    def render(self, screen: pygame.Surface):
        screen.fill(BLUE)

        self.wall.draw(screen)
        self.snake.draw(screen)
        self.food.draw(screen)

        font = pygame.font.SysFont("comicsansms", 20)
        text = font.render(str(self.score), True, AQUA)
        screen.blit(text, (400 - text.get_width(), 0))


def run_game(width: int, height: int, fps: int, starting_scene):
    pygame.init()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Snake game")
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene is not None:
        pressed_keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT \
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                active_scene.terminate()

        active_scene.process_input(pressed_keys)
        active_scene.update()
        active_scene.render(screen)

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)


run_game(400, 300, 30, TitleScene())
