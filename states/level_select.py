from pgzero.actor import Actor
import pygame
import states.global_state as global_state
WIDTH, HEIGHT = 550, 400

bk = Actor('141')
help_page = Actor('141')  # 假设是同一个背景图
help_page.x = WIDTH // 2
help_page.y = HEIGHT // 2

cloud1 = Actor('154')
cloud2 = Actor('154')
cloud1.x = WIDTH // 2
cloud2.x = cloud1.x + cloud1.width
CLOUD_SPEED = 0.5
CLOUD_ALPHA = 128

back1 = Actor('back_1')
back2 = Actor('back_2')
back1.x = WIDTH // 2
back1.y = HEIGHT // 2 + 140
back2.x = back1.x
back2.y = back1.y
back1.visible = True
back2.visible = False

instruct_bk = Actor('instruct_bk')
instruct_bk.x = WIDTH // 2
instruct_bk.y = 170

select_level = Actor('select_level')
select_level.x = WIDTH // 2
select_level.y = 50

level1 = Actor('level1')
level1_1= Actor('level1_1')
level1.x= WIDTH // 2 - 100
level1.y = HEIGHT // 2 - 50
level1_1.x = level1.x
level1_1.y = level1.y
level1.visible = True
level1_1.visible = False

level2 = Actor('level2')
level2_2 = Actor('level2_2')
level2.x = WIDTH // 2
level2.y = HEIGHT // 2 - 50
level2_2.x = level2.x
level2_2.y = level2.y
level2.visible = True
level2_2.visible = False

level3 = Actor('level3')
level3_3 = Actor('level3_3')
level3.x = WIDTH // 2 + 100
level3.y = HEIGHT // 2 - 50
level3_3.x = level3.x
level3_3.y = level3.y
level3.visible = True
level3_3.visible = False

# 音乐按钮相关
music0 = Actor('music0') # 按钮，音乐播放状态
music1 = Actor('music1') # 当鼠标悬停时，切换到另一个按钮，中间状态
music2 = Actor('music2')  # 当音乐关闭时，显示的按钮
music0.x = music1.x = music2.x = WIDTH - music0.width // 2 - 10
music0.y = music1.y = music2.y =10

# states/level1.py
def init_music_button():
    global music0, music1, music2
    music0 = Actor('music0')
    music1 = Actor('music1')
    music2 = Actor('music2')
    music0.x = music1.x = music2.x = WIDTH - music0.width // 2 - 10
    music0.y = music1.y = music2.y = 10
    music0.visible = True
    music1.visible = False
    music2.visible = False

init_music_button()


def draw():
    help_page.draw()
    cloud1._surf.set_alpha(CLOUD_ALPHA)
    cloud2._surf.set_alpha(CLOUD_ALPHA)
    cloud1.draw()
    cloud2.draw()

    instruct_bk.draw()
    select_level.draw()
    if back1.visible:
        back1.draw()
    if back2.visible:
        back2.draw()

    if level1.visible:
        level1.draw()
    elif level1_1.visible:
        level1_1.draw()

    if level2.visible:
        level2.draw()
    elif level2_2.visible:
        level2_2.draw()

    if level3.visible:
        level3.draw()
    elif level3_3.visible:
        level3_3.draw()

    # 绘制音乐按钮
    if music0.visible:
        music0.draw()
    if music1.visible:
        music1.draw()
    if music2.visible:
        music2.draw()


def update():
    cloud1.x -= CLOUD_SPEED
    cloud2.x -= CLOUD_SPEED
    if cloud1.x <= -cloud1.width / 2:
        cloud1.x = cloud2.x + cloud1.width
    if cloud2.x <= -cloud2.width / 2:
        cloud2.x = cloud1.x + cloud2.width

def on_mouse_move(pos):
    # 鼠标悬停在返回按钮上时切换按钮状态
    if back1.collidepoint(pos):
        back1.visible = False
        back2.visible = True
    else:
        back1.visible = True
        back2.visible = False

    # 鼠标悬停在关卡按钮上时切换按钮状态
    if level1.collidepoint(pos):
        level1.visible = False
        level1_1.visible = True
    else:
        level1.visible = True
        level1_1.visible = False

    if level2.collidepoint(pos):
        level2.visible = False
        level2_2.visible = True
    else:
        level2.visible = True
        level2_2.visible = False

    if level3.collidepoint(pos):
        level3.visible = False
        level3_3.visible = True
    else:
        level3.visible = True
        level3_3.visible = False

    # 音乐按钮状态处理
    if global_state.music_state == 'on':
        if music0.collidepoint(pos):
            music0.visible = False
            music1.visible = True
            music2.visible = False
        else:
            music0.visible = True
            music1.visible = False
            music2.visible = False
    else:  # 音乐关闭状态
        if music2.collidepoint(pos):  # 鼠标悬停在音乐按钮上
            music0.visible = False
            music1.visible = True  # 显示可点击状态
            music2.visible = False
        else:
            music0.visible = False
            music1.visible = False
            music2.visible = True

def on_mouse_down(pos, switch_state):
    if back2.collidepoint(pos):
        switch_state("main_menu", use_transition=False)
    elif level1_1.collidepoint(pos):
        switch_state("level1", use_transition=False)
    elif level2_2.collidepoint(pos):
        switch_state("level2", use_transition=False)
    elif level3_3.collidepoint(pos):
        switch_state("level3", use_transition=False)

    # 音乐按钮的点击事件
    if music1.collidepoint(pos):
        if global_state.music_state == 'on':
            global_state.music_state = 'off'
            music0.visible = False
            music1.visible = False
            music2.visible = True
            pygame.mixer.music.pause()  # 暂停音乐
        else:
            global_state.music_state = 'on'
            music0.visible = True
            music1.visible = False
            music2.visible = False
            # 检查音乐是否真的在播放
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)  # 直接开始播放
            else:
                pygame.mixer.music.unpause()  # 恢复已暂停的音乐