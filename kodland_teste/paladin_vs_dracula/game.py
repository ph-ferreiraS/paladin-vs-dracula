# game.py
import pgzrun
import math
import random
from pygame import Rect 
from pgzero.keyboard import keys

# ------------------------
# CONFIGURAÇÕES
# ------------------------
WIDTH = 800
HEIGHT = 750 
TITLE = "Paladin vs Dracula - Roguelike Edition"

# Configuração da GRADE (Grid)
TILE_SIZE = 50 # Tamanho de cada quadrado
GRID_W = WIDTH // TILE_SIZE
GRID_H = HEIGHT // TILE_SIZE

game_state = "menu"
sound_on = True
current_music = None
enemies = []
boss_phase_active = False

# ------------------------
# LIMITES DO CENÁRIO
# ------------------------
OBSTACLES = [
    Rect(0, 0, WIDTH, 175),      
    Rect(0, 0, 50, HEIGHT),      
    Rect(WIDTH-50, 0, 50, HEIGHT), 
    Rect(0, HEIGHT-50, WIDTH, 50), 
    Rect(100, 650, 80, 50),      
    Rect(620, 650, 80, 50),      
    Rect(350, 650, 100, 50)      
]

CX, CY = WIDTH // 2, HEIGHT // 2

# Botões
btn_start = Rect(CX - 150, CY - 100, 300, 60)
btn_sound = Rect(CX - 150, CY, 300, 60)
btn_quit  = Rect(CX - 150, CY + 100, 300, 60)
btn_retry = Rect(CX - 150, CY + 50, 300, 60)
btn_go_quit = Rect(CX - 150, CY + 150, 300, 60)
btn_resume   = Rect(CX - 150, CY - 100, 300, 60)
btn_to_menu  = Rect(CX - 150, CY, 300, 60)
btn_p_quit   = Rect(CX - 150, CY + 100, 300, 60)
btn_win_menu = Rect(CX - 150, CY + 50, 300, 60)
btn_win_quit = Rect(CX - 150, CY + 150, 300, 60)

# ------------------------
# SISTEMA DE ÁUDIO
# ------------------------
def play_music_track(track_name):
    global current_music
    if not sound_on:
        if current_music: music.stop(); current_music = None
        return
    if current_music != track_name:
        try: music.play(track_name); current_music = track_name
        except: pass 

def stop_music_track():
    global current_music
    music.stop(); current_music = None

# ------------------------
# UTILITÁRIO
# ------------------------
def get_frames(folder, filename, cols, rows):
    try:
        folder_obj = getattr(images, folder)
        surf = getattr(folder_obj, filename)
        sw, sh = surf.get_width(), surf.get_height()
        frame_w, frame_h = sw // cols, sh // rows
        frames_matrix = []
        for r in range(rows):
            row_frames = []
            for c in range(cols):
                rect = Rect(c * frame_w, r * frame_h, frame_w, frame_h)
                row_frames.append(surf.subsurface(rect))
            frames_matrix.append(row_frames)
        return frames_matrix
    except: return None

def is_tile_free(x, y):
    test_rect = Rect(x - 20, y - 20, 40, 40)
    for wall in OBSTACLES:
        if test_rect.colliderect(wall):
            return False
    return True

# ------------------------
# CLASSE PLAYER (ROGUELIKE)
# ------------------------
class Player:
    def __init__(self, col, row):
        # Define posição baseada na grade
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = row * TILE_SIZE + TILE_SIZE // 2
        
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = False
        
        self.speed = 4 # Velocidade do deslize
        self.state = "idle"
        self.direction = "right" 
        self.frame = 0.0
        self.hp = 10 
        self.frame_counts = {"idle": 4, "run": 6, "attack": 7, "death": 9}
        self.attack_cooldown = 0.0
    
    def get_rect(self): return Rect(self.x - 16, self.y - 20, 32, 40)
    # Ataque pega o quadrado da frente
    def get_attack_rect(self): 
        atk_x, atk_y = self.x, self.y
        if self.direction == "left": atk_x -= TILE_SIZE
        elif self.direction == "right": atk_x += TILE_SIZE
        elif self.direction == "up": atk_y -= TILE_SIZE
        elif self.direction == "down": atk_y += TILE_SIZE
        return Rect(atk_x - 25, atk_y - 25, 50, 50)

    def move_grid(self, dx, dy):
        """Tenta mover para o próximo quadrado"""
        if self.is_moving: return # Só aceita comando se parou de deslizar
        
        next_x = self.x + (dx * TILE_SIZE)
        next_y = self.y + (dy * TILE_SIZE)
        
        # Atualiza direção
        if dx > 0: self.direction = "right"
        elif dx < 0: self.direction = "left"
        elif dy > 0: self.direction = "down"
        elif dy < 0: self.direction = "up"

        if is_tile_free(next_x, next_y):
            self.target_x = next_x
            self.target_y = next_y
            self.is_moving = True
            self.state = "run"

    def update(self, dt):
        if game_state != "game": return
        if self.attack_cooldown > 0: self.attack_cooldown -= dt

        if self.hp > 0:
            # 1. Lógica de Movimento Suave (Lerp)
            if self.is_moving:
                dx = self.target_x - self.x
                dy = self.target_y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist <= self.speed:
                    # Chegou no quadrado
                    self.x = self.target_x
                    self.y = self.target_y
                    self.is_moving = False
                    self.state = "idle"
                else:
                    # Desliza em direção ao quadrado
                    self.x += (dx / dist) * self.speed
                    self.y += (dy / dist) * self.speed

            # 2. Inputs (Só aceita se não estiver movendo)
            elif self.state != "attack":
                if keyboard.left: self.move_grid(-1, 0)
                elif keyboard.right: self.move_grid(1, 0)
                elif keyboard.up: self.move_grid(0, -1)
                elif keyboard.down: self.move_grid(0, 1)

            # 3. Ataque
            if keyboard.space and self.attack_cooldown <= 0 and not self.is_moving:
                self.state = "attack"
                self.frame = 0.0
                self.attack_cooldown = 0.5
                
                hitbox = self.get_attack_rect()
                if boss_phase_active and hitbox.colliderect(dracula.get_rect()) and dracula.state != "death":
                    dracula.take_damage(1)
                
                for enemy in enemies:
                    if hitbox.colliderect(enemy.get_rect()) and enemy.state not in ["death", "gone"]:
                        enemy.take_damage(1)
                
                if sound_on: 
                    try: sounds.slash.play()
                    except: pass
        else:
            self.state = "death"

        # Animação
        total = self.frame_counts.get(self.state, 4)
        self.frame += 10 * dt 
        if self.frame >= total:
            if self.state == "attack": self.state = "idle"; self.frame = 0.0
            elif self.state == "death": self.frame = total - 1
            else: self.frame = 0.0

    def draw(self):
        img_name = f"{self.state}_{self.direction}_40x40"
        try:
            folder = getattr(images, "hero")
            img_full = getattr(folder, img_name)
            frames = self.frame_counts.get(self.state, 4)
            fw = img_full.get_width() // frames
            rect = Rect(int(self.frame) * fw, 0, fw, img_full.get_height())
            screen.blit(img_full.subsurface(rect), (self.x - fw//2, self.y - img_full.get_height()//2))
            
        except: 
            screen.draw.filled_circle((self.x, self.y), 15, "white")

# ------------------------
# CLASSE VAMPIRE (ROGUELIKE AI)
# ------------------------
class Vampire:
    def __init__(self, col, row):
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = row * TILE_SIZE + TILE_SIZE // 2
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = False
        
        self.speed = 1.5 # Velocidade de deslize
        self.state, self.direction = "idle", "down"
        self.frame, self.hp = 0.0, 3
        self.damage_dealt = False
        self.death_timer = 0.0
        self.move_timer = 0.0 # Delay para pensar
        
        self.sheets = {}
        anim_files = {
            "idle": ("vampire", "idle", 4, 4), "walk": ("vampire", "walk", 6, 4),
            "run": ("vampire", "run", 8, 4), "attack": ("vampire", "attack", 12, 4),
            "hurt": ("vampire", "hurt", 4, 4), "death": ("vampire", "death", 11, 4)
        }
        for k, v in anim_files.items(): self.sheets[k] = get_frames(*v)

    def get_rect(self): return Rect(self.x - 20, self.y - 30, 40, 60)

    def take_damage(self, amount):
        if self.state in ["death", "gone"]: return
        self.hp -= amount
        self.state = "hurt"; self.frame = 0.0
        if self.hp <= 0: self.hp = 0; self.state = "death"; self.frame = 0.0

    def decide_move(self):
        # IA simples de grade: Tenta alinhar X, se não der, alinha Y
        if self.is_moving: return
        
        dx_grid = 0
        dy_grid = 0
        
        # Calcula distância em TILES
        diff_x = player.target_x - self.x
        diff_y = player.target_y - self.y
        
        if abs(diff_x) > abs(diff_y):
            if diff_x > TILE_SIZE: dx_grid = 1
            elif diff_x < -TILE_SIZE: dx_grid = -1
        else:
            if diff_y > TILE_SIZE: dy_grid = 1
            elif diff_y < -TILE_SIZE: dy_grid = -1
            
        if dx_grid == 0 and dy_grid == 0: return # Já está no mesmo tile

        next_x = self.x + (dx_grid * TILE_SIZE)
        next_y = self.y + (dy_grid * TILE_SIZE)
        
        # Atualiza direção visual
        if dx_grid > 0: self.direction = "right"
        elif dx_grid < 0: self.direction = "left"
        elif dy_grid > 0: self.direction = "down"
        elif dy_grid < 0: self.direction = "up"

        # Só move se estiver livre
        if is_tile_free(next_x, next_y):
            self.target_x = next_x
            self.target_y = next_y
            self.is_moving = True
            self.state = "run"

    def update(self, dt):
        if game_state != "game" or self.state == "gone": return

        if self.state == "death":
            self._animate(dt)
            if self.frame >= 10:
                self.death_timer += dt
                if self.death_timer > 2.0: self.state = "gone"
            return
        
        if player.hp <= 0: self.state = "idle"; self._animate(dt); return
        if self.state == "hurt": self._animate(dt); return

        # --- MOVIMENTO EM GRADE ---
        if self.is_moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist <= self.speed:
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
                self.state = "idle"
                self.move_timer = 0.0 # Reseta timer de pensamento
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        else:
            # Delay para não andar todo frame (vampiros pensam)
            self.move_timer += dt
            if self.move_timer > 0.5: # Move a cada 0.5s
                # Checa distância para atacar ou andar
                dist_player = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
                if dist_player <= TILE_SIZE * 1.5: # Ataque se estiver no quadrado vizinho
                     self.state = "attack"; self.frame = 0.0; self.damage_dealt = False; self.move_timer = -1.0
                else:
                    self.decide_move()

        # Ataque
        if self.state == "attack":
            if self.frame >= 6.0 and not self.damage_dealt:
                if math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2) <= TILE_SIZE * 1.8:
                    player.hp -= 1; 
                    if player.hp < 0: player.hp = 0
                self.damage_dealt = True
            self._animate(dt); return

        self._animate(dt)

    def _animate(self, dt):
        sheet = self.sheets.get(self.state)
        if not sheet: return
        self.frame += 10 * dt
        if self.frame >= len(sheet[0]):
            if self.state in ["attack", "hurt"]: self.state = "idle"; self.frame = 0.0; self.damage_dealt = False
            elif self.state == "death": self.frame = len(sheet[0]) - 1
            else: self.frame = 0.0

    def draw(self):
        if self.state == "gone": return
        sheet = self.sheets.get(self.state)
        if not sheet: 
            screen.draw.filled_circle((self.x, self.y), 20, "red"); return
        dir_idx = {"down": 0, "up": 1, "left": 2, "right": 3}.get(self.direction, 0)
        img = sheet[dir_idx][min(int(self.frame), len(sheet[dir_idx])-1)]
        screen.blit(img, (self.x - img.get_width()//2, self.y - img.get_height()//2))

# ------------------------
# CLASSE DRACULA (BOSS - GRID)
# ------------------------
class Dracula:
    def __init__(self, col, row):
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = row * TILE_SIZE + TILE_SIZE // 2
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = False
        
        self.speed = 2.0 # Mais rápido
        self.state, self.direction = "idle", "down"
        self.frame, self.hp = 0.0, 20
        self.damage_dealt = False
        self.death_timer = 0.0
        self.move_timer = 0.0
        self.sheets = {}
        
        anim_files = {
            "idle": ("dracula", "idle", 4, 4), "walk": ("dracula", "walk", 6, 4),
            "run": ("dracula", "run", 8, 4), "attack": ("dracula", "attack", 12, 4),
            "hurt": ("dracula", "hurt", 4, 4), "death": ("dracula", "death", 11, 4)
        }
        for k, v in anim_files.items(): self.sheets[k] = get_frames(*v)
        if self.sheets.get("hurt") is None: self.sheets["hurt"] = self.sheets.get("idle")

    def get_rect(self): return Rect(self.x - 24, self.y - 36, 48, 72)

    def take_damage(self, amount):
        if not boss_phase_active: return 
        if self.state in ["death", "gone"]: return
        self.hp -= amount
        if self.sheets.get("hurt"): self.state = "hurt"; self.frame = 0.0
        if self.hp <= 0: self.hp = 0; self.state = "death"; self.frame = 0.0

    def decide_move(self):
        if self.is_moving: return
        dx_grid, dy_grid = 0, 0
        diff_x = player.target_x - self.x
        diff_y = player.target_y - self.y
        
        # Boss persegue mais agressivamente
        if abs(diff_x) > abs(diff_y):
            if diff_x > 0: dx_grid = 1
            elif diff_x < 0: dx_grid = -1
        else:
            if diff_y > 0: dy_grid = 1
            elif diff_y < 0: dy_grid = -1

        next_x = self.x + (dx_grid * TILE_SIZE)
        next_y = self.y + (dy_grid * TILE_SIZE)
        
        if dx_grid > 0: self.direction = "right"
        elif dx_grid < 0: self.direction = "left"
        elif dy_grid > 0: self.direction = "down"
        elif dy_grid < 0: self.direction = "up"

        if is_tile_free(next_x, next_y):
            self.target_x = next_x
            self.target_y = next_y
            self.is_moving = True
            self.state = "run"

    def update(self, dt):
        global game_state, boss_phase_active
        if game_state != "game": return
        if self.state == "gone": return

        if not boss_phase_active:
            self.state = "idle"; self.direction = "up"; self._animate(dt); return
        
        if self.state == "death":
            play_music_track("game") 
            self._animate(dt)
            if self.frame >= 10:
                self.death_timer += dt
                if self.death_timer > 3.0: self.state = "gone" 
            return

        if player.hp <= 0: self.state = "idle"; self._animate(dt); return
        if self.state == "hurt": self._animate(dt); return

        # Movimento Grade
        if self.is_moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist <= self.speed:
                self.x, self.y = self.target_x, self.target_y
                self.is_moving = False
                self.state = "idle"
                self.move_timer = 0.0
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        else:
            self.move_timer += dt
            if self.move_timer > 0.3: # Boss pensa rápido (0.3s)
                dist_player = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
                if dist_player <= TILE_SIZE * 1.8:
                     self.state = "attack"; self.frame = 0.0; self.damage_dealt = False; self.move_timer = -1.5
                else:
                    self.decide_move()
        
        if self.state == "attack":
            if self.frame >= 6.0 and not self.damage_dealt:
                if math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2) <= TILE_SIZE * 2.5:
                    player.hp -= 2; 
                    if player.hp < 0: player.hp = 0
                self.damage_dealt = True
            self._animate(dt); return

        self._animate(dt)

    def _animate(self, dt):
        sheet = self.sheets.get(self.state)
        if not sheet: return
        self.frame += 10 * dt
        total_frames = len(sheet[0])
        if self.frame >= total_frames:
            if self.state in ["attack", "hurt"]: self.state = "idle"; self.frame = 0.0; self.damage_dealt = False
            elif self.state == "death": self.frame = total_frames - 1
            else: self.frame = 0.0

    def draw(self):
        if self.state == "gone": return
        sheet = self.sheets.get(self.state)
        if not sheet: sheet = self.sheets.get("idle")
        if not sheet: 
            screen.draw.filled_circle((self.x, self.y), 25, "red"); return

        dir_idx = {"down": 0, "up": 1, "left": 2, "right": 3}.get(self.direction, 0)
        try:
            current_frame = min(int(self.frame), len(sheet[dir_idx])-1)
            img = sheet[dir_idx][current_frame]
            screen.blit(img, (self.x - img.get_width()//2, self.y - img.get_height()//2))
        except: 
            screen.draw.filled_circle((self.x, self.y), 25, "red")

# ------------------------
# SETUP
# ------------------------
def reset_game():
    global player, dracula, enemies, boss_phase_active
    boss_phase_active = False
    
    # Coordenadas em GRID (Coluna, Linha)
    # (3, 5) -> Aprox 150, 250
    player = Player(3, 5) 
    
    # Boss no centro-baixo (Coluna 8, Linha 12)
    dracula = Dracula(8, 12)
    dracula.direction = "up"
    
    enemies = []
    # Posições do Grid para inimigos
    grid_positions = [
        (5, 7), (8, 7), (11, 7),
        (5, 9), (8, 9), (11, 9)
    ]
    for pos in grid_positions:
        enemies.append(Vampire(pos[0], pos[1]))
        
    play_music_track("game")

player = Player(0,0)
dracula = Dracula(0,0)

# ------------------------
# CORE LOOPS
# ------------------------
def update(dt):
    global game_state, enemies, boss_phase_active
    if game_state == "menu": play_music_track("menu")
    if game_state == "game":
        player.update(dt)
        dracula.update(dt)
        for e in enemies: e.update(dt)
        enemies[:] = [e for e in enemies if e.state != "gone"]
        if not boss_phase_active and len(enemies) == 0:
            boss_phase_active = True; play_music_track("boss")
        if player.hp <= 0 and player.state == "death" and player.frame >= 8:
            game_state = "game_over"; play_music_track("game_over")
        if dracula.state == "gone":
            game_state = "win"; play_music_track("win")

def draw():
    screen.clear()
    if game_state == "menu":
        screen.fill((20, 20, 30))
        screen.draw.text(TITLE, center=(CX, 100), fontsize=60, color="red")
        screen.draw.filled_rect(btn_start, (50, 200, 50)); screen.draw.text("START", center=btn_start.center, fontsize=30)
        screen.draw.filled_rect(btn_sound, (100,100,100)); screen.draw.text("MUSIC ON/OFF", center=btn_sound.center, fontsize=30)
        screen.draw.filled_rect(btn_quit, (200, 50, 50)); screen.draw.text("QUIT", center=btn_quit.center, fontsize=30)

    elif game_state == "game" or game_state == "paused":
        try: screen.blit(images.backgrounds.background, (0,0))
        except: screen.fill((50,50,50)) 
        
        all_chars = [p for p in enemies if p.state != "death"] + [player, dracula]
        dead_enemies = [p for p in enemies if p.state == "death"]
        for char in dead_enemies: char.draw()
        all_chars.sort(key=lambda c: c.y)
        for char in all_chars: char.draw()
            
        screen.draw.text(f"HP: {player.hp}", (20, 20), color="red" if player.hp < 4 else "white", fontsize=40, owidth=1.5, ocolor="black")
        if boss_phase_active:
            screen.draw.text(f"BOSS: {dracula.hp}", (WIDTH-180, 20), color="red", fontsize=40, owidth=1.5, ocolor="black")
        else:
            screen.draw.text(f"MINIONS: {len(enemies)}", (WIDTH-200, 20), color="yellow", fontsize=30, owidth=1.5, ocolor="black")

        if game_state == "paused":
            screen.draw.filled_rect(Rect(0,0,WIDTH,HEIGHT), (0,0,0, 0.7))
            screen.draw.text("PAUSED", center=(CX, CY - 150), fontsize=80, color="yellow")
            screen.draw.filled_rect(btn_resume, (50, 200, 200)); screen.draw.text("RESUME", center=btn_resume.center, fontsize=30)
            screen.draw.filled_rect(btn_to_menu, (150, 100, 200)); screen.draw.text("MENU", center=btn_to_menu.center, fontsize=30)
            screen.draw.filled_rect(btn_p_quit, (200, 50, 50)); screen.draw.text("QUIT", center=btn_p_quit.center, fontsize=30)
            
    elif game_state == "game_over":
        screen.fill((50, 0, 0))
        screen.draw.text("GAME OVER", center=(CX, 200), fontsize=80, color="red")
        screen.draw.filled_rect(btn_retry, (50, 50, 200)); screen.draw.text("RETRY", center=btn_retry.center, fontsize=30)
        screen.draw.filled_rect(btn_go_quit, (200, 50, 50)); screen.draw.text("QUIT", center=btn_go_quit.center, fontsize=30)

    elif game_state == "win":
        screen.fill((20, 50, 20))
        screen.draw.text("YOU WIN!", center=(CX, 150), fontsize=80, color="gold", owidth=2, ocolor="black")
        screen.draw.filled_rect(btn_win_menu, (150, 100, 200)); screen.draw.text("MENU", center=btn_win_menu.center, fontsize=30, color="white")
        screen.draw.filled_rect(btn_win_quit, (200, 50, 50)); screen.draw.text("QUIT", center=btn_win_quit.center, fontsize=30, color="white")

def on_mouse_down(pos):
    global game_state, sound_on
    if sound_on and game_state in ["menu", "paused", "game_over", "win"]:
        try: sounds.click.play()
        except: pass

    if game_state == "menu":
        if btn_start.collidepoint(pos): reset_game(); game_state = "game"
        if btn_sound.collidepoint(pos): sound_on = not sound_on; (stop_music_track() if not sound_on else play_music_track("menu"))
        if btn_quit.collidepoint(pos): quit()
    elif game_state == "paused":
        if btn_resume.collidepoint(pos): game_state = "game"
        if btn_to_menu.collidepoint(pos): game_state = "menu"; play_music_track("menu")
        if btn_p_quit.collidepoint(pos): quit()
    elif game_state == "game_over":
        if btn_retry.collidepoint(pos): reset_game(); game_state = "game"
        if btn_go_quit.collidepoint(pos): quit()
    elif game_state == "win":
        if btn_win_menu.collidepoint(pos): game_state = "menu"; play_music_track("menu")
        if btn_win_quit.collidepoint(pos): quit()

def on_key_down(key):
    global game_state
    if key == keys.ESCAPE:
        if game_state == "game": game_state = "paused"
        elif game_state == "paused": game_state = "game"

pgzrun.go()