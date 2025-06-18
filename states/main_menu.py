from pgzero.actor import Actor
import states.global_state as global_state
import pygame
WIDTH, HEIGHT = 550, 400

bk = Actor('141')
cloud1 = Actor('154')
cloud2 = Actor('154')
cloud1.x = WIDTH // 2
cloud2.x = cloud1.x + cloud1.width
CLOUD_SPEED = 0.5
CLOUD_ALPHA = 128

start_no = Actor('play1')
start_yes = Actor('play2')
start_no.x = start_yes.x = WIDTH // 2
start_no.y = start_yes.y = HEIGHT // 2 + 70

help1 = Actor('help1')
help2 = Actor('help2')
help1.x = help2.x = WIDTH // 2
help1.y = help2.y = HEIGHT // 2 + 120

title_image = Actor('1621')
title_image.x = WIDTH // 2
title_image.y = HEIGHT // 2 - 75

start_no.visible = True
start_yes.visible = False
help1.visible = True
help2.visible = False

# 音乐按钮相关
music0 = Actor('music0') # 按钮，音乐播放状态
music1 = Actor('music1') # 当鼠标悬停时，切换到另一个按钮，中间状态
music2 = Actor('music2')  # 当音乐关闭时，显示的按钮
music0.x = music1.x = music2.x = WIDTH - music0.width // 2 - 10
music0.y = music1.y = music2.y =10

# 只在初始化和切换音乐状态时设置一次初始可见性
def init_music_button():
    if global_state.music_state == 'on':
        music0.visible = True
        music1.visible = False
        music2.visible = False
    else:
        music0.visible = False
        music1.visible = False
        music2.visible = True

init_music_button()  # 初始化音乐按钮状态

def draw():
    bk.draw()
    cloud1._surf.set_alpha(CLOUD_ALPHA)
    cloud2._surf.set_alpha(CLOUD_ALPHA)
    cloud1.draw()
    cloud2.draw()
    if start_no.visible:
        start_no.draw()
    if start_yes.visible:
        start_yes.draw()
    if help1.visible:
        help1.draw()
    if help2.visible:
        help2.draw()
    title_image.draw()
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
    global music_state
    if start_no.collidepoint(pos):
        start_no.visible = False
        start_yes.visible = True
    else:
        start_no.visible = True
        start_yes.visible = False

    if help1.collidepoint(pos):
        help1.visible = False
        help2.visible = True
    else:
        help1.visible = True
        help2.visible = False

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
    global music_state
    if start_yes.collidepoint(pos):
        switch_state("level_select", use_transition=False)  # 你可以先跳转到关卡选择界面
    elif help2.collidepoint(pos):
        switch_state("help_page", use_transition=False)

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



