from __future__ import annotations
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> #
#           < IN THE NAME OF GOD >           #
# ------------------------------------------ #
__AUTHOR__ = "ToorajJahangiri"
__EMAIL__ = "Toorajjahangiri@gmail.com"
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< #


# IMPORT
import os
import random

from concurrent.futures import ThreadPoolExecutor

# IMPORT FRAMEWORK
import pygame

# IMPORT TYPING
from typing import NamedTuple

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\^////////////////////////////// #

# Get Center Of Size
def get_center(inp: Size) -> Position:
    return Position(inp.Width/2, inp.Height/2)

# 2D Position Object
class Position(NamedTuple):
    X: float | int
    Y: float | int

# 2D Size
class Size(NamedTuple):
    Width: float | int
    Height: float | int

# 2D Speed
class SpeedPos(NamedTuple):
    X: float | int
    Y: float | int


# Base Sprit Object
class Object(pygame.sprite.Sprite):
    SCREEN_SIZE = None

    def __init__(self, img_path: str, position: Position) -> None:
        super(Object, self).__init__()
        img_path = os.path.realpath(img_path)
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect(center= position)

        if self.SCREEN_SIZE is None:
            self.SCREEN_SIZE = self.get_screen_size()

    @property
    def position(self) -> Position:
        return Position(self.rect.x, self.rect.y)

    @staticmethod
    def get_screen_size() -> Size:
        return Size(*pygame.display.get_window_size())

    @staticmethod
    def get_screen() -> pygame.surface.Surface:
        return pygame.display.get_surface()


# Player - Object
class Player(Object):

    def __init__(
        self,
        img_path: str,
        position: Position,
        speed: int | float,
        ) -> None:
        super(Player, self).__init__(img_path, position)
        self.speed = speed
        self.movement = 0

    def screen_limit(self) -> None:
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= self.SCREEN_SIZE.Height:
            self.rect.bottom = self.SCREEN_SIZE.Height

    def update(self, _) -> None:
        self.rect.y += self.movement
        self.screen_limit()


# Ball - Object
class Ball(Object):
    PONG_SOUND: pygame.mixer.Sound
    SCORE_SOUND: pygame.mixer.Sound
    HIT_SOUND: pygame.mixer.Sound

    def __init__(
        self,
        img_path: str,
        position: Position,
        speed: SpeedPos | float | int,
        paddles: pygame.sprite.Group,
        ) -> None:
        super(Ball, self).__init__(img_path, position)
        if isinstance(speed, (float, int)):
            self.speed_x = speed
            self.speed_y = speed
        else:
            self.speed_x, self.speed_y = speed
        self.paddles = paddles
        self.active = False
        self.score_time = 0

        self.font = pygame.font.Font('freesansbold.ttf', 70)
        self.timer_color = (200, 200, 200, 255)
        self.timer_bg_color = '#2F373F00'

    @property
    def speed(self) -> SpeedPos:
        return SpeedPos(self.speed_x, self.speed_y)

    @speed.setter
    def speed(self, speed: SpeedPos | float | int) -> None:
        if isinstance(speed, (float, int)):
            self.speed_x = speed * random.choice((-1, 1))
            self.speed_y = speed * random.choice((-1, 1))
        else:
            self.speed_x, self.speed_y = speed

    def collisions(self) -> None:
        if self.rect.top <= 0 or self.rect.bottom >= self.SCREEN_SIZE.Height:
            pygame.mixer.Sound.play(self.PONG_SOUND)
            self.speed_y *= -1

        if colide := pygame.sprite.spritecollide(self, self.paddles, False):
            pygame.mixer.Sound.play(self.HIT_SOUND)
            collision_paddle = colide[0].rect
            if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0:
                self.speed_x *= -1
            if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
                self.speed_x *= -1

            if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
                self.speed_y *= -1
            if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
                self.speed_y *= -1

    def reset_ball(self) -> None:
        self.active = False
        self.speed_x *= random.choice((-1, 1))
        self.speed_y *= random.choice((-1, 1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = get_center(self.SCREEN_SIZE)
        pygame.mixer.Sound.play(self.SCORE_SOUND)

    def restart_counter(self) -> None:
        current_time = pygame.time.get_ticks()
        countdown = 3

        diffrent = current_time - self.score_time

        if diffrent <= 700:
            countdown = 3
        elif 700 < diffrent <= 1400:
            countdown = 2
        elif 1400 < diffrent <= 2100:
            countdown = 1
        elif diffrent >= 2100:
            self.active = True

        center_scr = get_center(self.SCREEN_SIZE)
        timer_pos = Position(center_scr.X, center_scr.Y/2)

        time_counter = self.font.render(f'{countdown}', True, self.timer_color)
        time_counter_rect = time_counter.get_rect(center=timer_pos)

        screen = self.get_screen()

        pygame.draw.rect(
            screen,
            self.timer_bg_color, time_counter_rect,
            )

        screen.blit(time_counter, time_counter_rect)

    def update(self) -> None:
        if self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.collisions()
        else:
            self.restart_counter()


# Opponent - Object
class Opponent(Object):

    def __init__(self, img_path: str, position: Position, speed: float|int) -> None:
        super(Opponent, self).__init__(img_path, position)
        self.speed = speed

    def screen_limit(self) -> None:
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= self.SCREEN_SIZE.Height:
            self.rect.bottom = self.SCREEN_SIZE.Height

    def update(self, ball_group: pygame.sprite.GroupSingle) -> None:
        if self.rect.top < ball_group.sprite.rect.y:
            self.rect.y += self.speed
        if self.rect.bottom > ball_group.sprite.rect.y:
            self.rect.y -= self.speed

        self.screen_limit()


# Game Manage
class GameManage:
    SCORE_COLOR = None
    TIMER_COLOR = None

    def __init__(
        self,
        ball_group: pygame.sprite.GroupSingle,
        paddles_group: pygame.sprite.Group,
        ) -> None:
        self.right_score = 0
        self.left_score = 0
        self.ball_group = ball_group
        self.paddles_group = paddles_group

        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.score_color = self.SCORE_COLOR or (255, 255, 255, 255)
        self.timer_color = self.TIMER_COLOR or (4, 10, 17, 255)

        self.screen = self.get_screen()
        self.scr_size = self.get_screen_size()

        self.start_time = 0

        self.theread = ThreadPoolExecutor(3, 'PONG_')

    def start_timer(self) -> None:
        self.start_time = self.get_ticks()

    def reset_ball(self) -> None:
        if self.ball_group.sprite.rect.right >= self.scr_size.Width:
            self.left_score += 1
            self.ball_group.sprite.reset_ball()
            self.start_timer()
        if self.ball_group.sprite.rect.left <= 0:
            self.right_score += 1
            self.ball_group.sprite.reset_ball()
            self.start_timer()

    def draw_score(self) -> None:
        right_score = self.font.render(f'{self.right_score}', True, self.score_color)
        left_score = self.font.render(f'{self.left_score}', True, self.score_color)

        center_scr = get_center(self.scr_size)

        right_score_rect = right_score.get_rect(midleft= (center_scr.X + 20, center_scr.Y))
        left_score_rect = left_score.get_rect(midleft= (center_scr.X - 40, center_scr.Y))

        self.screen.blit(right_score, right_score_rect)
        self.screen.blit(left_score, left_score_rect)

    def draw_timer(self) -> None:
        passed = self.get_ticks() - self.start_time
        center_scr = get_center(self.scr_size)
        timer_pos = Position(center_scr.X, self.scr_size.Height - 25)

        if not passed <= 2100:
            passed -= 2100
            timer = self.font.render(f"{passed//(120 * 5)}", True, self.timer_color)
            timer_rect = timer.get_rect(center=timer_pos)
            self.screen.blit(timer, timer_rect)

    def run_game(self) -> None:
        # Drawing
        self.paddles_group.draw(self.screen)
        self.ball_group.draw(self.screen)

        # Updating Game Object
        self.paddles_group.update(self.ball_group)
        self.ball_group.update()

        # --- Multi Thereading
        # Theread > Reset Ball
        self.theread.submit(self.reset_ball)
        # Theread > Draw Score
        self.theread.submit(self.draw_score)
        # Theread > Draw Timer
        self.theread.submit(self.draw_timer)

    @staticmethod
    def get_ticks() -> int:
        return pygame.time.get_ticks()

    @staticmethod
    def get_screen_size() -> Size:
        return Size(*pygame.display.get_window_size())

    @staticmethod
    def get_screen() -> pygame.surface.Surface:
        return pygame.display.get_surface()



__dir__ = (
    'Position',
    'Size',
    'SpeedPos',
    'get_center',
    'Object',
    'Player',
    'Ball',
    'Opponent',
    'GameManage',
)
