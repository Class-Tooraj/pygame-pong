from __future__ import annotations
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> #
#           < IN THE NAME OF GOD >           #
# ------------------------------------------ #
__AUTHOR__ = "ToorajJahangiri"
__EMAIL__ = "Toorajjahangiri@gmail.com"
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< #


# IMPORT FRAMEWORK
import pygame

# IMPORT OBJECTS
from objects import get_center, Size, Position, SpeedPos, Ball, Player, Opponent, GameManage

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\^////////////////////////////// #

# General Setup
pygame.mixer.pre_init(44100, -16, 256)
pygame.init()
clock = pygame.time.Clock()

# Main Window
WIDTH = 1000
HEIGHT = 600

SCR_SIZE = Size(WIDTH, HEIGHT)
SCR_CENTER = get_center(SCR_SIZE)

ICON = pygame.image.load('./icon.png')

INFO = pygame.image.load('./resource/info.png')
INFO_RECT = INFO.get_rect(center=SCR_CENTER)

pygame.display.set_icon(ICON)
pygame.display.set_caption('! PonG !')

SCR = pygame.display.set_mode(SCR_SIZE)

BG_TITLE = pygame.image.load('./resource/pong.png').convert_alpha()
BG_TITLE_RECT = BG_TITLE.get_rect(center= SCR_CENTER)


BG_COLOR = pygame.Color('#2F373F')
ACCENT_COLOR = pygame.Color('#1b232b')

PONG_SOUND = pygame.mixer.Sound('./resource/pong.wav')
SCORE_SOUND = pygame.mixer.Sound('./resource/score.wav')
HIT_SOUND = pygame.mixer.Sound('./resource/hit.wav')
SCR_SPLIT = pygame.Rect(SCR_CENTER.X - 2, 0, 4, SCR_SIZE.Height)

# GAME OBJECT
RIGHT = Position(SCR_SIZE.Width - 20, SCR_SIZE.Height / 2)
LEFT = Position(20, SCR_SIZE.Height/2)

PLAYER_SPEED = 7
OPPONENT_SPEED = 8

BALL_SPEED = SpeedPos(6, 4)

player = Player('./resource/Player-Paddle.png', RIGHT, PLAYER_SPEED)
opponent = Opponent('./resource/Opponent-Paddle.png', LEFT, OPPONENT_SPEED)

paddle_group = pygame.sprite.Group(player, opponent)

ball = Ball
ball.PONG_SOUND = PONG_SOUND
ball.SCORE_SOUND = SCORE_SOUND
ball.HIT_SOUND = HIT_SOUND
ball = ball('./resource/ball.png', SCR_CENTER, BALL_SPEED, paddle_group)
ball_group = pygame.sprite.GroupSingle(ball)

game_manage = GameManage
game_manage.SCORE_COLOR = ACCENT_COLOR
game_manage = game_manage(ball_group, paddle_group)


pause = False

# MainLoop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pause = not pause
                continue

            if event.key == pygame.K_UP:
                player.movement -= player.speed
            if event.key == pygame.K_DOWN:
                player.movement += player.speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player.movement += player.speed
            if event.key == pygame.K_DOWN:
                player.movement -= player.speed

    if pause:
        SCR.blit(INFO, INFO_RECT)
        pygame.display.flip()
        continue

    # Background Stuff
    SCR.fill(BG_COLOR)
    SCR.blit(BG_TITLE, BG_TITLE_RECT)
    pygame.draw.rect(SCR,ACCENT_COLOR,SCR_SPLIT)

    # Run the game
    game_manage.run_game()

    # Rendering
    pygame.display.flip()
    clock.tick(120)

