from random import randint
from typing import List, Optional, Tuple

import pygame as pg

# Псевдонимы для аннотации типов
Position = Tuple[int, int]
Color = Tuple[int, int]

SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

UP: Position = (0, -1)
DOWN: Position = (0, 1)
LEFT: Position = (-1, 0)
RIGHT: Position = (1, 0)

BOARD_BACKGROUND_COLOR: Color = (0, 0, 0)
BORDER_COLOR: Color = (93, 216, 228)
APPLE_COLOR: Color = (255, 0, 0)
SNAKE_COLOR: Color = (0, 255, 0)
SPEED: int = 20

screen: pg.Surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock: pg.time.Clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color: Color = BOARD_BACKGROUND_COLOR) -> None:
        self.position: Position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color: Color = body_color

    def draw(self) -> None:
        """Метод отрисовки (переопределяется в дочерних классах)."""
        raise NotImplementedError(
            'Метод draw должен быть реализован в дочернем классе.'
        )


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле."""

    def __init__(
        self,
        body_color: Color = APPLE_COLOR,
        occupied_cells: Optional[List[Position]] = None
    ) -> None:
        super().__init__(body_color=body_color)
        if occupied_cells is None:
            occupied_cells = []
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells: List[Position]) -> None:
        """Устанавливает случайное положение яблока на поле, избегая змейку."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_cells:
                break

    def draw(self) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self, body_color: Color = SNAKE_COLOR) -> None:
        super().__init__(body_color=body_color)
        self.reset()

    def get_head_position(self) -> Position:
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        new_head = (
            (head_x + (dir_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (dir_y * GRID_SIZE)) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def draw(self) -> None:
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions[:-1]:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self) -> None:
        """Сбрасывает змейку в исходное состояние."""
        self.length: int = 1
        self.positions: List[Position] = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ]
        self.direction: Position = RIGHT
        self.next_direction: Optional[Position] = None
        self.last: Optional[Position] = None


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Основная функция игры."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_cells=snake.positions)

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка столкновения змейки с самой собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        # Проверка поедания яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
