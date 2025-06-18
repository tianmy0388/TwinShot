import pygame

WIDTH, HEIGHT = 550, 400

anim_alpha = 0
anim_speed = 5
target_state = None

def start_transition(state_name):
    global anim_alpha, target_state
    anim_alpha = 0
    target_state = state_name

def draw(screen):
    # 用一个白色 Surface 叠加在屏幕上，alpha 从 0→255
    s = pygame.Surface((WIDTH, HEIGHT))
    s.fill((255, 255, 255))
    s.set_alpha(anim_alpha)
    screen.surface.blit(s, (0, 0))

def update():
    global anim_alpha
    from main import switch_state  # 在函数里导入，防止循环引用

    if anim_alpha < 255:
        anim_alpha += anim_speed
    else:
        switch_state(target_state)

