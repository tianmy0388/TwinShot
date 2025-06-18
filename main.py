import pgzrun
import pygame
from states import main_menu, help_page, level_select, level1, level2, level3 #transition,
from states import global_state

WIDTH, HEIGHT = 550, 400

# 当前游戏状态，初始为主菜单
game_state = "main_menu"
next_state = None  # 用于存储转场时的目标状态

# 初始化音乐
pygame.mixer.init()
MENU_MUSIC = 'sounds/MenuMusic.mp3'
GAME_MUSIC = 'sounds/GameMusic.mp3'
current_music = None  # 当前播放的音乐文件路径

def play_music(music_path):
    global current_music
    if current_music != music_path:
        pygame.mixer.music.load(music_path)
        if global_state.music_state == 'on':
            pygame.mixer.music.play(-1)  # 只有在音乐状态为"开"时才播放
        current_music = music_path

# 先播放主菜单音乐
play_music(MENU_MUSIC)


def switch_state(new_state, use_transition=False):
    global game_state, next_state

    # 判断目标界面需要的音乐
    new_music = None
    if new_state in ["main_menu", "help_page", "level_select"]:
        new_music = MENU_MUSIC
    elif new_state in ["level1", "level2","level3"]:
        new_music = GAME_MUSIC

    # 如果需要切换音乐或音乐状态为'on'但没有播放
    if new_music != current_music or (global_state.music_state == 'on' and not pygame.mixer.music.get_busy()):
        play_music(new_music)

    # 根据全局音乐状态确保音乐播放状态正确
    if global_state.music_state == 'off':
        pygame.mixer.music.pause()
    else:
        # 如果没有播放，则重新开始播放
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.unpause()

    if use_transition:
        transition.start_transition(new_state)
        game_state = "transition"
    else:
        game_state = new_state

def draw():
    # screen.clear()
    if game_state == "main_menu":
        main_menu.draw()
    elif game_state == "help_page":
        help_page.draw()
    elif game_state == "transition":
        # 这里只是绘制转场遮罩，背景等要在子模块里绘制
        transition.draw(screen)
    elif game_state == "level_select":
        level_select.draw()
    elif game_state == "level1":
        level1.draw(screen)
    elif game_state == "level2":
        level2.draw(screen)
    elif game_state == "level3":
        level3.draw(screen)

def update():
    if game_state == "main_menu":
        main_menu.update()
    elif game_state == "help_page":
        help_page.update()
    elif game_state == "transition":
        transition.update()
    elif game_state == "level_select":
        level_select.update()
    elif game_state == "level1":
        level1.update()
    elif game_state == "level2":
        level2.update()
    elif game_state == "level3":
        level3.update()

def on_mouse_move(pos, rel, buttons):
    if game_state == "main_menu":
        main_menu.on_mouse_move(pos)
    elif game_state == "help_page":
        help_page.on_mouse_move(pos)
    elif game_state == "level_select":
        level_select.on_mouse_move(pos)
    elif game_state == "level1":
        level1.on_mouse_move(pos)
    elif game_state == "level2":
        level2.on_mouse_move(pos)
    elif game_state == "level3":
        level3.on_mouse_move(pos)


def on_mouse_down(pos):
    if game_state == "main_menu":
        # 在主菜单里按下去时，把 switch_state 作为回调传进去
        main_menu.on_mouse_down(pos, switch_state)
    elif game_state == "help_page":
        help_page.on_mouse_down(pos, switch_state)
    elif game_state == "level_select":
        level_select.on_mouse_down(pos, switch_state)
    elif game_state == "level1":
        level1.on_mouse_down(pos, switch_state)
    elif game_state == "level2":
        level2.on_mouse_down(pos, switch_state)
    elif game_state == "level3":
        level3.on_mouse_down(pos, switch_state)

pgzrun.go()
