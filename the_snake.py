from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 8
MIN_SPEED = 5
MAX_SPEED = 25

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для всех объектов"""

    """Инициализация позиции и цвета объекта"""
    def __init__(self, position=None, body_color=APPLE_COLOR):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовка объекта. Переопределяется в дочерних классах"""
        pass

    @staticmethod
    def draw_cell(position, body_color):
        """Отрисовка одной ячейки заданного цвета + рамка"""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока"""

    """Создания яблока определенного цвета в случайной позиции"""
    def __init__(self, position=None, body_color=APPLE_COLOR):
        if position is None:
            position = self._get_random_position()
        super().__init__(position, body_color)

    def _get_random_position(self):
        """Генерация случайных координат для размещения яблока"""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        return (x, y)

    def randomize_position(self, snake_position=None):
        """Перемещение яблока в случайную позицию, избегая занятых ячеек"""
        while True:
            new_position = self._get_random_position()
            if snake_position is None or new_position not in snake_position:
                self.position = new_position
                break

    def draw(self):
        """Рисует яблоко на игровом поле"""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки"""

    """Инициализация змейки в ценрте поля с заданным цветом"""
    def __init__(self, position=None, body_color=SNAKE_COLOR):
        if position is None:
            position = START_POSITION
        super().__init__(position, body_color)
        self.reset()

    def get_head_position(self):
        """Возврат координат головы змеи"""
        return self.positions[0]

    def update_direction(self):
        """Принимает направление движения"""
        if self.next_direction:
            opposite = (self.next_direction[0] * -1,
                        self.next_direction[1] * -1
                        )
            if opposite != self.direction:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновление координат змейки. Добавление головы и удаление хвоста"""
        head = self.get_head_position()
        x, y = head
        dx, dy = self.direction
        new_head = (
            (head[0] + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head[1] + dy * GRID_SIZE) % SCREEN_HEIGHT
        )

        if len(self.positions) == self.length:
            self.last = self.positions[-1]
        else:
            self.last = None

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self):
        """Отрисовка головы и затирание позиции старого хвоста"""
        self.draw_cell(self.positions[0], self.body_color)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сброс змейки в начальное состояние после столкновения"""
        self.length = 1
        self.positions = [START_POSITION]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object, current_speed, min_speed, max_speed):
    """Обработка нажатия клавиш для управления"""
    new_speed = current_speed
    speed_change = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if event.key == pygame.K_q and current_speed > min_speed:
                new_speed -= 1
                speed_change = True
            elif event.key == pygame.K_w and current_speed < max_speed:
                new_speed += 1
                speed_change = True

            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT

    return new_speed, speed_change


def main():
    """Основной игровой цикл"""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apples = []
    for _ in range(3):
        new_apple = Apple()
        occupied = snake.positions + [a.position for a in apples]
        new_apple.randomize_position(occupied)
        apples.append(new_apple)

    record_length = 1
    current_speed = SPEED
    pygame.display.set_caption(
        f'Змейка | Скорость: {current_speed} | Рекорд: {record_length}'
    )

    for apple in apples:
        apple.draw()

    for pos in snake.positions:
        snake.draw_cell(pos, snake.body_color)
    pygame.display.update()

    while True:
        current_speed, speed_change = handle_keys(
            snake,
            current_speed,
            MIN_SPEED,
            MAX_SPEED
        )
        if speed_change:
            pygame.display.set_caption(
                f'Змейка | Скорость: {current_speed} | Рекорд: {record_length}'
            )
        clock.tick(current_speed)

        # Тут опишите основную логику игры.

        snake.update_direction()
        snake.move()
        for apple in apples:
            if snake.get_head_position() == apple.position:
                snake.length += 1
                occupied = snake.positions + [
                    a.position for a in apples if a != apple
                ]
                apple.randomize_position(occupied)
                break

        if (
            snake.length > 3
            and snake.get_head_position() in snake.positions[1:]
        ):
            if snake.length > record_length:
                record_length = snake.length
                pygame.display.set_caption
                (
                    'Змейка | Скорость: '
                    f'{current_speed} | Рекорд: {record_length}'
                )
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apples.clear()

            for _ in range(3):
                new_apple = Apple()
                occupied = snake.positions + [a.position for a in apples]
                new_apple.randomize_position(occupied)
                apples.append(new_apple)
            for apple in apples:
                apple.draw()
            snake.draw()
            pygame.display.update()
            continue

        for apple in apples:
            apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
