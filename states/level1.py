# 文件：states/level1.py
from pgzero.actor import Actor
from pgzero.keyboard import keyboard, keys
import pygame
from pytmx.util_pygame import load_pygame
import pytmx
import time
import states.global_state as global_state

# ========== 一、常量与地图数据 ==========
WIDTH, HEIGHT = 550, 400
TILE_SIZE = 24
GRAVITY = 0.5
HORIZ_SPEED = 4
JUMP_SPEED = -8.5
jump_pressed = False
attack_pressed = False
max_player_vy = 5  # 玩家最大下落速度
life_num = 3  # 玩家生命数量

level_failed = Actor('level_failed')
level_failed.x = WIDTH // 2
level_failed.y = HEIGHT // 2 - 50

is_pause = False  # 是否暂停游戏
pause_label = Actor('pause_label')
pause_label.x = WIDTH // 2
pause_label.y = HEIGHT // 2 - 50

level_finished = False
level_finished_label = Actor('level_finished')
level_finished_label.x = WIDTH // 2
level_finished_label.y = HEIGHT // 2 - 50
lever_clear_time = None

continue0 = Actor('continue0')
continue1 = Actor('continue1')
continue0.x = WIDTH // 2
continue0.y = HEIGHT // 2 + 50
continue1.x = continue0.x
continue1.y = continue0.y
# 初始显示 continue0
continue0.visible = True
continue1.visible = False

# 加载 Tiled 地图，请确保该路径指向你的 .tmx 文件
tmx_data = load_pygame('images/Twin_shot_map1.tmx')

# 收集所有可见的 TileLayer（图块层），供碰撞检测使用
tile_layers = [layer for layer in tmx_data.visible_layers if isinstance(layer, pytmx.TiledTileLayer)]
if not tile_layers:
    raise Exception("未在 .tmx 文件中找到任何瓦片图层，请检查地图文件是否正确。")

# ========== 二、可选背景（如不需要可注释掉） ==========
bk = Actor('141')
bk.pos = (WIDTH // 2, HEIGHT // 2)
# 云初始化
cloud1 = Actor('154')
cloud2 = Actor('154')
cloud1.x = WIDTH // 2
cloud2.x = cloud1.x + cloud1.width
CLOUD_SPEED = 0.5
CLOUD_ALPHA = 128

# 导入暂停图片，可点击
pause0 = Actor('pause1')
pause1 = Actor('pause0')
# 设置在右上角
pause0.x = WIDTH - pause0.width // 2 - 38
pause0.y = pause1.y = 10
pause1.x = pause0.x
pause1.y = pause0.y
# 初始显示 pause0
pause0.visible = True
pause1.visible = False

restart0 = Actor('restart0')
restart1 = Actor('restart1')
restart0.x = WIDTH // 2
restart0.y = HEIGHT // 2 + 50
restart1.x = restart0.x
restart1.y = restart0.y
# 初始显示 restart0
restart0.visible = True
restart1.visible = False

endgame0 = Actor('endgame0')
endgame1 = Actor('endgame1')
endgame0.x = WIDTH // 2
endgame0.y = HEIGHT // 2 + 100
endgame1.x = endgame0.x
endgame1.y = endgame0.y
# 初始显示 endgame0
endgame0.visible = True
endgame1.visible = False

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

# 寻找第一层solid瓦片函数
def find_ground_y(col):
    for row in range(tmx_data.height):
        tile_x_mod = col % tmx_data.width
        tile_y_mod = row % tmx_data.height
        for layer in tile_layers:
            gid = layer.data[tile_y_mod][tile_x_mod]
            if gid == 0:
                continue
            props = tmx_data.get_tile_properties_by_gid(gid)
            if props and props.get('solid') in (True, 'true'):
                return row * TILE_SIZE - enemy_run_r[0].height // 2
    return HEIGHT - enemy_run_r[0].height // 2  # 找不到就放最底下
# ========== 敌人初始化 ==========
# 敌人设置
ENEMY_SPEED = 1  # 敌人移动速度
enemy_num = 3  # 初始敌人数量
enemy_run_l = [Actor(f'e_l{i}') for i in range(10)]
enemy_run_r = [Actor(f'e_r{i}') for i in range(10)]
enemy_dead = [Actor(f'e_dead{i}') for i in range(4)]

# 敌人类
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = ENEMY_SPEED
        self.vy = 0
        self.facing = 'r'
        self.state = 'alive'
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_interval = 6
        self.dead_timer = 0

    def update(self):
        if self.state == 'alive':
            # 使用更小的碰撞偏移量
            collision_offset = 5  # 改用小偏移量，原来是 half_w

            # 1. 水平移动尝试
            next_x = self.x + self.vx
            foot_y = self.y + enemy_run_r[0].height // 2 - 4  # 稍微上移检测点
            head_y = self.y - enemy_run_r[0].height // 3  # 头部检测点

            # 检查前方是否有solid柱子
            check_x = next_x + (collision_offset if self.vx > 0 else -collision_offset)

            # 只用脚底检测点，头部检测可能过于敏感
            if is_solid_at(check_x, foot_y):
                self.vx = -self.vx
                self.facing = 'l' if self.vx < 0 else 'r'
            else:
                self.x = next_x

            # 2. 重力
            self.vy += GRAVITY
            if self.vy > max_player_vy:
                self.vy = max_player_vy
            next_y = self.y + self.vy
            foot_y = next_y + enemy_run_r[0].height // 2
            if is_solid_at(self.x, foot_y):
                tile_row = int(foot_y // TILE_SIZE)
                self.y = tile_row * TILE_SIZE - enemy_run_r[0].height // 2
                self.vy = 0
            else:
                self.y = next_y

            # 上下左右环绕
            map_height_px = tmx_data.height * TILE_SIZE
            map_width_px = tmx_data.width * TILE_SIZE
            if self.y + enemy_run_r[0].height // 2 < 0:
                self.y += map_height_px
            elif self.y - enemy_run_r[0].height // 2 > map_height_px:
                self.y -= map_height_px
            if self.x + collision_offset < 0:
                self.x += map_width_px
            elif self.x - collision_offset > map_width_px:
                self.x -= map_width_px

            # 动画
            self.anim_timer += 1
            if self.anim_timer >= self.anim_interval:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 10
        elif self.state == 'dead':
            self.y += 4
            self.dead_timer += 1
            if self.dead_timer % 6 == 0:
                self.anim_frame = (self.anim_frame + 1) % 4

    def draw(self, screen, cam_x, cam_y):
        if self.state == 'alive':
            img = f'e_{self.facing}{self.anim_frame}'
        else:
            img = f'e_dead{self.anim_frame}'
        enemy_actor = Actor(img)
        enemy_actor.pos = (self.x - cam_x, self.y - cam_y)
        enemy_actor.draw()

# 敌人列表
enemies = [
    Enemy(5 * TILE_SIZE + TILE_SIZE // 2, find_ground_y(5)),
    Enemy(10 * TILE_SIZE + TILE_SIZE // 2, find_ground_y(10)),
    Enemy(15 * TILE_SIZE + TILE_SIZE // 2, find_ground_y(15))
]

# ========== 三、玩家初始化（使用“世界坐标”） ==========
player = Actor('player_r0')
was_on_ground = False  # 用于判断玩家是否从空中落地

# 玩家死亡状态
player_d_l = Actor('player_dead_l')
player_d_r = Actor('player_dead_r')
player_dead = False
player_death_anim = False
player_death_vy = 0
player_death_timer = 0
restart_level0 = Actor('restart_level0')
restart_level1 = Actor('restart_level1')
restart_level0.x = WIDTH // 2
restart_level0.y = HEIGHT // 2 + 50
restart_level1.x = restart_level0.x
restart_level1.y = restart_level0.y
restart_level0.visible = True
restart_level1.visible = False

# 玩家移动
run_l = [f'run_l{i}' for i in range(8)]
run_r = [f'run_r{i}' for i in range(8)]

# 玩家跳跃
up_l = [f'up_l{i}' for i in range(2)]
up_r = [f'up_r{i}' for i in range(2)]
down_l = [f'down_l{i}' for i in range(2)]
down_r = [f'down_r{i}' for i in range(2)]

# 玩家攻击（射箭）
shot_l = [f'shot_l{i}' for i in range(8)]
shot_r = [f'shot_r{i}' for i in range(8)]
# 箭
arrow_l = Actor('arrow_l')
arrow_r = Actor('arrow_r')

# 玩家生命值
player.life = life_num
player_life = Actor('life_3') # 初始生命值为3，生命值为2时为Actor('life_2')，生命值为1时为Actor('life_1'),生命值为0时为Actor('life_0')

# world_x/world_y 表示玩家在地图上的真实位置（以中心点为基准）
player.world_x = 2 * TILE_SIZE + TILE_SIZE // 2  # 第5列中心
player.world_y = 1 * TILE_SIZE + TILE_SIZE // 2  # 第2行中心（行索引从0开始）
player.vx = 0
player.vy = 0
player.on_ground = False
# 玩家动画相关变量
player.anim_frame = 0
player.anim_timer = 0
player.anim_interval = 6  # 每6帧切换一次
player.facing = 'r'  # 初始朝向

# 玩家状态相关变量
player.invincible = False
player.invincible_timer = 0

# 玩家攻击相关变量
player.attacking = False
player.attack_timer = 0
player.attack_interval = 8  # 攻击动画帧数

# 箭对象列表
arrows = []  # 用于存储玩家射出的箭

class Arrow:
    max_vy = 4.5
    def __init__(self, x, y, vx, vy, facing):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.facing = facing
        self.state = 'flying'
        self.actor = Actor('arrow_l' if facing == 'l' else 'arrow_r')
        self.width = self.actor.width
        self.height = self.actor.height
        self.embed_time = None  # 嵌入时间

    def update(self):
        if self.state == 'flying':
            self.vy += 0.15  # 应用重力
            if self.vy > self.max_vy:
                self.vy = self.max_vy
            if is_solid_at(self.x, self.y + self.height / 2 + 1):
                self.vy *= 0.2
            self.x += self.vx
            self.y += self.vy
            head_x = self.x + (self.width // 2 if self.facing == 'r' else -self.width // 2)
            if is_solid_at(head_x, self.y):
                self.state = 'embedded'
                self.vx = 0
                self.vy = 0
                self.embed_time = time.time()
        elif self.state == 'enemy_hit':  # 新增：击中敌人状态处理
            # 继续受重力影响
            self.vy += 0.15
            if self.vy > self.max_vy:
                self.vy = self.max_vy
            self.y += self.vy  # 只有垂直移动
            # 检查是否碰到地面
            if is_solid_at(self.x, self.y + self.height / 2 + 1):
                self.state = 'embedded'
                self.vy = 0
                self.embed_time = time.time()
        self.actor.pos = (self.x, self.y)

        # 地图左右环绕
        map_width_px = tmx_data.width * TILE_SIZE
        if self.x + self.width / 2 < 0:
            self.x += map_width_px
        elif self.x - self.width / 2 > map_width_px:
            self.x -= map_width_px

# ========== 四、摄像机变量 ==========
# camera_x/camera_y 表示摄像机左上角在“世界坐标”中的位置
# camera_target_x/Y 用于缓动目标
camera_x = player.world_x - WIDTH // 2
camera_y = player.world_y - HEIGHT // 2
camera_target_x = camera_x
camera_target_y = camera_y

# ========== 五、辅助函数：检测 world 坐标是否在 solid 瓦片处 ==========
def is_solid_at(world_x, world_y, for_standing=False):
    """
    判断给定“世界坐标”(world_x, world_y) 是否落在可站立(solid)的瓦片上。
    做法：
      1. 将 world 坐标转换为瓦片索引 (tile_x, tile_y)
      2. 通过 tile_y_mod = tile_y % tmx_data.height, tile_x_mod = tile_x % tmx_data.width 获得循环映射
      3. 遍历所有可见 TileLayer，如果在该图层对应位置
         tmx_data.get_tile_properties_by_gid(gid) 返回属性里有 'solid'=True，则返回 True
    """
    """
    for_standing=True 时，嵌入的箭作为平台可站立；否则只检测瓦片。
    """
    tile_x = int(world_x // TILE_SIZE)
    tile_y = int(world_y // TILE_SIZE)
    tile_x_mod = tile_x % tmx_data.width
    tile_y_mod = tile_y % tmx_data.height

    for layer in tile_layers:
        gid = layer.data[tile_y_mod][tile_x_mod]
        if gid == 0:
            continue
        props = tmx_data.get_tile_properties_by_gid(gid)
        if props and props.get('solid') in (True, 'true'):
            return True

    # 只有 for_standing=True 时，嵌入的箭才算 solid
    if for_standing:
        for arrow in arrows:
            if arrow.state == 'embedded':
                if (arrow.x - arrow.width / 2 <= world_x <= arrow.x + arrow.width / 2 and
                    arrow.y - arrow.height / 2 - 4 <= world_y <= arrow.y + arrow.height / 2 + 4):
                    return True
    return False

# ========== 六、玩家状态更新 ==========
def update_player():
    """
    每帧调用：
    1. 处理左右移动与跳跃输入
    2. 横向碰撞检测，避免深入 solid 瓦片
    3. 应用重力，并处理垂直方向的地面碰撞
    4. 当玩家完全越过上下边界时，给 world_y 加/减 map_height_px（Wrap）
    5. 更新摄像机目标位置，使玩家始终保持在窗口中央，并限制在地图范围
    """
    global camera_target_x, camera_target_y, jump_pressed, was_on_ground, attack_pressed, life_num

    # —— 1. 水平输入 ——
    if keyboard[keys.LEFT]:
        player.vx = -HORIZ_SPEED
        player.facing = 'l'
    elif keyboard[keys.RIGHT]:
        player.vx = HORIZ_SPEED
        player.facing = 'r'
    else:
        player.vx = 0

    # —— 跳跃 ——
    if keyboard[keys.UP]:
        if player.on_ground and not jump_pressed:
            player.vy = JUMP_SPEED
            jump_pressed = True
    else:
        jump_pressed = False

    # —— 2. 攻击 ——
    if keyboard[keys.SPACE]:
        if not player.attacking and not attack_pressed:
            player.attacking = True
            attack_pressed = True
            player.attack_timer = 0
            # 发射箭
            arrow_vx = -8 if player.facing == 'l' else 8
            arrows.append(Arrow(player.world_x, player.world_y+10, arrow_vx, -2, player.facing))
    else:
        attack_pressed = False

    # 记录落地瞬间
    just_landed = (not was_on_ground) and player.on_ground

    if player.attacking:
        player.attack_timer += 1
        frame = min(player.attack_timer // (player.attack_interval // 8), 7)
        if player.facing == 'l':
            player.image = shot_l[frame]
        else:
            player.image = shot_r[frame]
        if player.attack_timer >= player.attack_interval:
            player.attacking = False
    # —— 动画帧更新（静止时循环） ——
    elif player.vx == 0 and player.on_ground:
        if just_landed:
            player.anim_frame = 0
            player.anim_timer = 0
        player.anim_timer += 1
        if player.anim_timer >= player.anim_interval:
            player.anim_timer = 0
            player.anim_frame = (player.anim_frame + 1) % 8
        player.image = f'player_{player.facing}{player.anim_frame}'
    elif player.vx != 0 and player.on_ground:
        # 移动时显示 run 动画
        if just_landed:
            player.anim_frame = 0
            player.anim_timer = 0
        player.anim_timer += 1
        if player.anim_timer >= player.anim_interval:
            player.anim_timer = 0
            player.anim_frame = (player.anim_frame + 1) % 8
        if player.facing == 'l':
            player.image = run_l[player.anim_frame]
        else:
            player.image = run_r[player.anim_frame]
    elif not player.on_ground:
        # 跳跃动画
        if player.anim_frame>= 2:
            player.anim_frame = 0
        player.anim_timer += 1
        if player.anim_timer >= player.anim_interval:
            player.anim_timer = 0
            player.anim_frame = (player.anim_frame + 1) % 2  # 跳跃动画2帧
        if player.vy < 0:
            # 上升
            if player.facing == 'l':
                player.image = up_l[player.anim_frame]
            else:
                player.image = up_r[player.anim_frame]
        else:
            # 下降
            if player.facing == 'l':
                player.image = down_l[player.anim_frame]
            else:
                player.image = down_r[player.anim_frame]

    # —— 应用重力 ——
    player.vy += GRAVITY
    if player.vy > max_player_vy:
        player.vy = max_player_vy

    # —— 2. 横向移动与碰撞检测 ——
    if player.vx != 0:
        next_x = player.world_x + player.vx
        half_pw = player.width / 2
        # 右移时检查脚底和头顶右侧点
        if player.vx > 0:
            check_points = [
                (next_x + half_pw, player.world_y),
                (next_x + half_pw, player.world_y - player.height / 2 + 1)
            ]
        else:
            # 左移时检查脚底和头顶左侧点
            check_points = [
                (next_x - half_pw, player.world_y),
                (next_x - half_pw, player.world_y - player.height / 2 + 1)
            ]

        collision = False
        for (cx, cy) in check_points:
            if is_solid_at(cx, cy):
                collision = True
                break
        if not collision:
            player.world_x = next_x

    # —— 3. 垂直运动与地面碰撞检测 ——
    next_y = player.world_y + player.vy
    foot_x = player.world_x
    foot_y = next_y + player.height / 2

    # 修改垂直运动与地面碰撞检测部分
    if player.vy > 0 and is_solid_at(foot_x, foot_y, for_standing=True):
        # 检查是否站在箭上
        standing_on_arrow = False
        for arrow in arrows:
            if arrow.state == 'embedded':
                if (arrow.x - arrow.width / 2 <= foot_x <= arrow.x + arrow.width / 2 and
                        arrow.y - arrow.height / 2 - 4 <= foot_y <= arrow.y + arrow.height / 2 + 4):
                    # 站在箭上，直接设置到箭的顶部
                    player.world_y = arrow.y - arrow.height / 2 - player.height / 2
                    player.vy = 0
                    player.on_ground = True
                    standing_on_arrow = True
                    break

        # 如果不是站在箭上，则是站在普通瓦片上
        if not standing_on_arrow:
            tile_row = int(foot_y // TILE_SIZE)
            player.world_y = tile_row * TILE_SIZE - player.height / 2
            player.vy = 0
            player.on_ground = True

        # 判断是否刚落地
        if not was_on_ground:
            player.anim_frame = 0
            player.anim_timer = 0
    else:
        player.world_y = next_y
        player.on_ground = False

    # —— 4. 完全越过上下边界时的 Wrap 处理 ——
    map_height_px = tmx_data.height * TILE_SIZE
    # 如果玩家整个 sprite 都越过顶端：world_y + height/2 < 0
    if not player_dead:
        if player.world_y + player.height / 2 < 0:
            # 直接移动到底部对应位置：+ map_height_px
            player.world_y += map_height_px
        # 如果玩家整个 sprite 都越过底部：world_y - height/2 > map_height_px
        elif player.world_y - player.height / 2 > map_height_px:
            player.world_y -= map_height_px

    # —— 5. 更新摄像机目标位置 ——
    camera_target_x = player.world_x - WIDTH // 2
    camera_target_y = player.world_y - HEIGHT // 2

    # 限制摄像机目标不要超出地图边界
    max_cam_x = max(0, tmx_data.width * TILE_SIZE - WIDTH)
    max_cam_y = max(0, tmx_data.height * TILE_SIZE - HEIGHT)
    if camera_target_x < 0:
        camera_target_x = 0
    if camera_target_x > max_cam_x:
        camera_target_x = max_cam_x
    if camera_target_y < 0:
        camera_target_y = 0
    if camera_target_y > max_cam_y:
        camera_target_y = max_cam_y

    map_width_px = tmx_data.width * TILE_SIZE
    # 左右环绕
    if player.world_x + player.width / 2 < 0:
        player.world_x += map_width_px
    elif player.world_x - player.width / 2 > map_width_px:
        player.world_x -= map_width_px

    # 记录上一次是否在地面上
    was_on_ground = player.on_ground

    # 玩家无敌计时
    if player.invincible:
        player.invincible_timer -= 1
        if player.invincible_timer <= 0:
            player.invincible = False

    # 玩家与敌人碰撞检测
    if not player.invincible:
        for enemy in enemies:
            if enemy.state == 'alive':
                if abs(player.world_x - enemy.x) < 45 and abs(player.world_y - enemy.y) < 40:
                    player.life -= 1
                    life_num -= 1
                    player.invincible = True
                    player.invincible_timer = 180  # 3秒（60帧*3）
                    break

# ========== 箭的更新函数 ==========
def update_arrows():
    now = time.time()
    arrows[:] = [arrow for arrow in arrows if not (
        arrow.state == 'embedded' and arrow.embed_time and now - arrow.embed_time > 5
    )]
    for arrow in arrows:
        arrow.update()
# ========== 七、绘制函数 ==========
def draw_map(screen, cam_x, cam_y):
    """
    将地图中所有可见瓦片图层按照摄像机偏移 (cam_x, cam_y) 绘制到屏幕上。
    """
    for layer in tmx_data.visible_layers:
        if hasattr(layer, 'tiles'):
            for x, y, image in layer.tiles():
                screen.surface.blit(image, (x * TILE_SIZE - cam_x, y * TILE_SIZE - cam_y))

def draw(screen):
    """
    Pygame Zero 每帧调用此函数流程：
      1. 清空屏幕
      2. （可选）画背景
      3. 画地图
      4. 把玩家分两次绘制实现“部分上下环绕”
      5. 如果越过下边缘，也要同时绘制“上边缘”部分
    """
    global player_death_anim
    screen.clear()
    # 如果想要背景图，请取消下一行注释
    bk.draw()
    cloud1._surf.set_alpha(CLOUD_ALPHA)
    cloud2._surf.set_alpha(CLOUD_ALPHA)
    cloud1.draw()
    cloud2.draw()
    # 绘制地图
    draw_map(screen, camera_x, camera_y)

    if pause0.visible:
        pause0.draw()
    if pause1.visible:
        pause1.draw()

    # 绘制音乐按钮
    if music0.visible:
        music0.draw()
    if music1.visible:
        music1.draw()
    if music2.visible:
        music2.draw()

    # 绘制所有敌人
    for enemy in enemies:
        enemy.draw(screen, camera_x, camera_y)

    # 绘制箭
    for arrow in arrows:
        screen_x = arrow.x - camera_x - arrow.width / 2
        screen_y = arrow.y - camera_y - arrow.height / 2
        screen.surface.blit(arrow.actor._surf, (screen_x, screen_y))

    # 先算屏幕坐标
    screen_x = player.world_x - camera_x - player.width / 2
    screen_y = player.world_y - camera_y - player.height / 2

    # 玩家无敌时闪烁
    draw_player = True
    if player.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
        draw_player = False
    if draw_player:
        screen.surface.blit(player._surf, (screen_x, screen_y))
        if screen_y < 0:
            screen.surface.blit(player._surf, (screen_x, screen_y + HEIGHT))
        if screen_y + player.height > HEIGHT:
            screen.surface.blit(player._surf, (screen_x, screen_y - HEIGHT))

    # —— 主绘制：玩家在主屏幕坐标上 ——
    # screen.surface.blit(player._surf, (screen_x, screen_y))

    # —— 实现“部分越界”时的双重显示 ——
    # 如果玩家某部分穿过上边缘： screen_y < 0
    # if screen_y < 0:
    #     # 计算在屏幕下方对应位置
    #     screen.surface.blit(player._surf, (screen_x, screen_y + HEIGHT))
    # # 如果玩家某部分穿过下边缘： screen_y + player.height > HEIGHT
    # if screen_y + player.height > HEIGHT:
    #     # 计算在屏幕上方对应位置
    #     screen.surface.blit(player._surf, (screen_x, screen_y - HEIGHT))
    # 只在未死亡时绘制正常玩家及上下环绕
    if not player_dead:
        draw_player = True
        if player.invincible and (pygame.time.get_ticks()//100)%2==0:
            draw_player = False
        if draw_player:
            screen.surface.blit(player._surf, (screen_x, screen_y))
            if screen_y < 0:
                screen.surface.blit(player._surf, (screen_x, screen_y + HEIGHT))
            if screen_y + player.height > HEIGHT:
                screen.surface.blit(player._surf, (screen_x, screen_y - HEIGHT))

    # 右下角显示生命图片
    life_img = f'life_{player.life}'
    player_life.image = life_img
    player_life.pos = (WIDTH - player_life.width // 2 - 10, HEIGHT - player_life.height // 2 - 10)
    player_life.draw()

    if is_pause:  # 如果游戏处于暂停状态
        # 半透明遮罩
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        screen.surface.blit(s, (0, 0))
        # 绘制暂停标签
        pause_label.draw()
        # 绘制restart和endgame按钮
        if restart0.visible:
            restart0.draw()
        if restart1.visible:
            restart1.draw()
        if endgame0.visible:
            endgame0.draw()
        if endgame1.visible:
            endgame1.draw()

    if level_finished:  # 如果关卡已完成
        # 半透明遮罩
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        screen.surface.blit(s, (0, 0))
        # 绘制关卡完成标签
        level_finished_label.draw()
        # 绘制continue和endgame按钮
        if endgame0.visible:
            endgame0.draw()
        if endgame1.visible:
            endgame1.draw()
        if continue0.visible:
            continue0.draw()
        if continue1.visible:
            continue1.draw()

    # 玩家死亡后的绘制
    if player_dead:
        player_d = player_d_l if player.facing=='l' else player_d_r
        screen.surface.blit(player_d._surf, (screen_x, screen_y))
        if player.world_y - player.height/2 > tmx_data.height*TILE_SIZE:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0,128))
            screen.surface.blit(s, (0,0))
            level_failed.draw()
            restart_level0.draw() if restart_level0.visible else None
            restart_level1.draw() if restart_level1.visible else None
            endgame0.draw()    if endgame0.visible    else None
            endgame1.draw()    if endgame1.visible    else None
        return

# 敌人更新函数
def update_enemies():
    for enemy in enemies:
        enemy.update()
    # 移除掉出窗口的死亡敌人
    enemies[:] = [e for e in enemies if not (e.state == 'dead' and e.y > HEIGHT + 50)]

# 检查箭是否击中敌人
def check_arrow_hit_enemies():
    global enemy_num
    for arrow in arrows:
        if arrow.state != 'flying':
            continue
        for enemy in enemies:
            if enemy.state == 'alive':
                # 简单矩形碰撞
                if abs(arrow.x - enemy.x) < 20 and abs(arrow.y - enemy.y) < 20:
                    enemy.state = 'dead'
                    enemy_num-=1
                    enemy.anim_frame = 0
                    enemy.dead_timer = 0
                    arrow.state = 'enemy_hit'  # 击中敌人后进入特殊状态
                    arrow.vx = 0  # 只让水平速度为0
                    break

# ========== 八、Pygame Zero 钩子 ==========
def update():
    """
    每帧自动调用：
      1. 更新玩家的 world_x/world_y、碰撞、穿越逻辑
      2. 缓动摄像机位置，使其平滑跟随 camera_target
      3. 按 ESC 返回关卡选择
    """
    global camera_x, camera_y, level_clear_time, level_finished, is_pause
    global enemy_num, player_dead, life_num, player_death_anim, player_death_vy, player_death_timer
    if is_pause or level_finished:
        return # 暂停时不更新游戏逻辑, 如果关卡已完成，则不更新

    if player_dead:
        if not player_death_anim:
            player_death_anim = True
            player_death_vy = -8
            player_death_timer = 0
        else:
            # 根据朝向切换死亡图片
            if player.facing == 'l':
                player_d = player_d_l
            else:
                player_d = player_d_r

            player.image = player_d.image
            player.world_y += player_death_vy
            player_death_vy += GRAVITY
            player_death_timer += 1
            # 判断是否掉出窗口
            if player.world_y - player.height / 2 > tmx_data.height * TILE_SIZE:
                # 如果掉出窗口，显示重启按钮
                return
        return

    # 1. 更新玩家状态
    update_player()
    update_arrows()

    # 2. 云彩移动
    cloud1.x -= CLOUD_SPEED
    cloud2.x -= CLOUD_SPEED
    if cloud1.x <= -cloud1.width / 2:
        cloud1.x = cloud2.x + cloud1.width
    if cloud2.x <= -cloud2.width / 2:
        cloud2.x = cloud1.x + cloud2.width

    # 3. 平滑摄像机插值：每帧向目标靠近 10%
    camera_x += (camera_target_x - camera_x) * 0.1
    camera_y += (camera_target_y - camera_y) * 0.1

    # 检查箭是否击中敌人
    check_arrow_hit_enemies()
    # 更新敌人状态
    update_enemies()

    # 4. 检查玩家是否死亡
    if life_num == 0 and not player_dead:
        player_dead = True


    # 检查是否清除所有敌人
    if enemy_num == 0 and not level_finished:
        if level_clear_time is None:
            level_clear_time = time.time()
        elif time.time() - level_clear_time >= 5:
            level_finished = True
    else:
        level_clear_time = None  # 敌人没清空时重置

def on_mouse_move(pos):
    """处理鼠标移动事件"""
    # 这里可以添加鼠标悬停或点击的逻辑
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

    if not is_pause:
        if pause0.collidepoint(pos):
            pause0.visible = False
            pause1.visible = True
        else:
            pause0.visible = True
            pause1.visible = False
        if pause1.collidepoint(pos):
            pause0.visible = True
            pause1.visible = False
        else:
            pause0.visible = False
            pause1.visible = True
    else:
        if endgame0.collidepoint(pos):
            endgame0.visible = False
            endgame1.visible = True
        else:
            endgame0.visible = True
            endgame1.visible = False
        if restart0.collidepoint(pos):
            restart0.visible = False
            restart1.visible = True
        else:
            restart0.visible = True
            restart1.visible = False

    if level_finished:
        if continue0.collidepoint(pos):
            continue0.visible = False
            continue1.visible = True
        else:
            continue0.visible = True
            continue1.visible = False
        if endgame0.collidepoint(pos):
            endgame0.visible = False
            endgame1.visible = True
        else:
            endgame0.visible = True
            endgame1.visible = False

    if player_dead:
        if restart_level0.collidepoint(pos):
            restart_level0.visible = False
            restart_level1.visible = True
        else:
            restart_level0.visible = True
            restart_level1.visible = False
        if endgame0.collidepoint(pos):
            endgame0.visible = False
            endgame1.visible = True
        else:
            endgame0.visible = True
            endgame1.visible = False


def on_mouse_down(pos, switch_state):
    """处理鼠标点击事件"""
    global is_pause, level_finished, player_dead, player_death_anim
    if not is_pause:
        if pause1.collidepoint(pos):
            is_pause = True
    else:
        if endgame1.collidepoint(pos):
            is_pause = False
            switch_state("main_menu", use_transition=False)
            reset_level()
        elif restart1.collidepoint(pos):
            is_pause = False
    if level_finished:
        if continue1.collidepoint(pos):
            is_pause = False
            switch_state("level2", use_transition=False)
            reset_level()
        elif endgame1.collidepoint(pos):
            is_pause = False
            switch_state("main_menu", use_transition=False)
            reset_level()
    if player_dead :
        if restart_level1.collidepoint(pos):
            is_pause = False
            player_dead = False
            player_death_anim = False
            reset_level()
        elif endgame1.collidepoint(pos):
            is_pause = False
            player_dead = False
            player_death_anim = False
            switch_state("main_menu", use_transition=False)
            reset_level()

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


def reset_level():
    global player, enemies, arrows, camera_x, camera_y, camera_target_x, camera_target_y, is_pause, level_finished, level_clear_time, enemy_num, life_num
    global player_dead, player_death_anim, player_death_vy, player_death_timer
    # 重新初始化玩家
    player.world_x = 2 * TILE_SIZE + TILE_SIZE // 2
    player.world_y = 1 * TILE_SIZE + TILE_SIZE // 2
    player.vx = 0
    player.vy = 0
    player.on_ground = False
    player.anim_frame = 0
    player.anim_timer = 0
    player.facing = 'r'
    life_num = 3
    player.life = life_num
    player.invincible = False
    player.invincible_timer = 0
    player.attacking = False
    player.attack_timer = 0

    # 重新初始化敌人
    enemies[:] = [
        Enemy(5 * TILE_SIZE + TILE_SIZE // 2, find_ground_y(5)),
        Enemy(10 * TILE_SIZE + TILE_SIZE // 2, find_ground_y(10)),
        Enemy(15 * TILE_SIZE + TILE_SIZE // 2, find_ground_y(15))
    ]
    # 重置敌人数量
    enemy_num = 3
    # 重置关卡清除时间
    level_clear_time = None
    # 清空箭
    arrows.clear()
    # 摄像机重置
    camera_x = player.world_x - WIDTH // 2
    camera_y = player.world_y - HEIGHT // 2
    camera_target_x = camera_x
    camera_target_y = camera_y
    # 暂停状态重置
    is_pause = False
    # 关卡完成状态重置
    level_finished = False
    # 玩家死亡状态重置
    player_dead = False
    player_death_anim = False
    player_death_vy = 0
    player_death_timer = 0

