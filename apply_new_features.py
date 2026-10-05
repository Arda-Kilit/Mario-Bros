import re
main_path = r"C:\Users\ardak\Desktop\vucut-oyun-temiz\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Replace prepopulate_all_caches with progress bar loading screen version
new_prepopulate_func = """
def prepopulate_all_caches(game=None):
    print("[Info] Cizim onbellekleri yukleniyor...")
    
    # Helper to pre-render coin directly into cache
    def draw_coin_direct(w, pos_cos):
        key = (w, pos_cos)
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        if pos_cos:
            for py in range(8):
                for px in range(w // 2):
                    c = GOLD if (px + py) % 2 == 0 else (216, 176, 0)
                    pygame.draw.rect(surf, c, (8 - w // 2 + px * 2, py * 2, 2, 2))
        else:
            for py in range(8):
                pygame.draw.rect(surf, GOLD, (7, py * 2, 2, 2))
        _coin_cache[key] = surf

    # Helper to pre-render Mario
    def pre_render_mario():
        for is_big in [True, False]:
            for ducking in [True, False]:
                for gnd in [True, False]:
                    for frame_idx in [0, 1]:
                        for direction in [Dir.LEFT, Dir.RIGHT]:
                            for power in [PowerUp.NONE, PowerUp.FIRE, PowerUp.SHIELD, PowerUp.SPEED]:
                                w = 32
                                if is_big:
                                    h = 28 if ducking else 48
                                else:
                                    h = 16 if ducking else 32
                                draw_mario(None, 0, 0, w, h, direction, frame_idx / 8.0, gnd, False, 0, power, ducking)

    steps = [
        ("YUKLENIYOR: Golge Efektleri...", lambda: [draw_shadow(None, 0, 0, w, alpha) for w in [24, 40, 60, 80, 112] for alpha in [30, 40, 60, 80]]),
        ("YUKLENIYOR: Goomba Karakterleri...", lambda: [draw_goomba(None, 0, 0, b / 10.0) for b in range(-20, 21)]),
        ("YUKLENIYOR: Koopa Karakterleri...", lambda: [draw_koopa(None, 0, 0, b / 10.0) for b in range(-20, 21)]),
        ("YUKLENIYOR: Boru Canavarlari...", lambda: draw_piranha(None, 0, 0, 0)),
        ("YUKLENIYOR: Altin Animasyonlari...", lambda: [draw_coin_direct(w, pos_cos) for w in range(1, 17) for pos_cos in [True, False]]),
        ("YUKLENIYOR: Mucize Mantarlar...", lambda: [draw_mushroom(None, 0, 0, 0, t) for t in ["super", "1up", "shield", "speed", "fire"]]),
        ("YUKLENIYOR: Tuglalar ve Bloklar...", lambda: [draw_brick(None, 0, 0, 0), draw_qblock(None, 0, 0, False, 0), draw_qblock(None, 0, 0, True, 0)]),
        ("YUKLENIYOR: Yesil Borular...", lambda: [draw_pipe(None, 0, 0, w, h) for w in [64, 96, 128] for h in [32, 64, 96]]),
        ("YUKLENIYOR: Arayuz Ogeleri...", lambda: [draw_pixel_heart(None, 0, 0, 3), draw_pixel_clock(None, 0, 0, 3), draw_pixel_star(None, 0, 0, 3), draw_menu_mushroom(None, 0, 0, 28)]),
        ("YUKLENIYOR: Mario Karakteri...", lambda: pre_render_mario())
    ]
    
    total_steps = len(steps)
    for idx, (label, action) in enumerate(steps):
        action()
        if game is not None and game.s is not None:
            # Draw professional loading screen
            game.s.fill((12, 12, 20))
            
            # Draw double-line retro dialog box in the center
            dw, dh = 500, 160
            dx, dy = SW // 2 - dw // 2, SH // 2 - dh // 2
            pygame.draw.rect(game.s, (0, 0, 0), (dx, dy, dw, dh))
            pygame.draw.rect(game.s, WHITE, (dx, dy, dw, dh), 4)
            pygame.draw.rect(game.s, (0, 0, 0), (dx + 6, dy + 6, dw - 12, dh - 12))
            pygame.draw.rect(game.s, WHITE, (dx + 6, dy + 6, dw - 12, dh - 12), 1)
            
            # Text label
            draw_retro_text(game.s, "SUPER MARIO BROS - ULTIMATE", game.fs, dx + 40, dy + 25, GOLD, BLACK)
            draw_retro_text(game.s, label, game.ft, dx + 40, dy + 65, WHITE, BLACK)
            
            # Progress bar
            bar_w = dw - 80
            bar_h = 16
            bar_x = dx + 40
            bar_y = dy + 105
            progress = (idx + 1) / total_steps
            pygame.draw.rect(game.s, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(game.s, GREEN, (bar_x, bar_y, int(bar_w * progress), bar_h))
            pygame.draw.rect(game.s, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
            
            pygame.display.flip()
            pygame.time.wait(20)  # Subtle delay to show progress beautifully
            
    print("[OK] Tum onbellekler basariyla yuklendi!")
"""

# Let's replace the old prepopulate_all_caches block completely
# Find prepopulate_all_caches start and replace up to class MarioUltimate
code = re.sub(
    r"def prepopulate_all_caches\(\):.*?class MarioUltimate:",
    new_prepopulate_func + "\nclass MarioUltimate:",
    code,
    flags=re.DOTALL
)

# 2. Call prepopulate_all_caches with `self` passed as argument
code = code.replace("prepopulate_all_caches()", "prepopulate_all_caches(self)")

# 3. Clean webcam scan inside _enter_settings
old_enter_settings = """    def _enter_settings(self):
        # Scan active webcams ONLY if control mode is El Takibi
        available = []
        if self.control_mode == 1:
            for i in range(4):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW if sys.platform.startswith('win') else None)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        available.append(i)
                    cap.release()
        if not available:
            available = [0]
        self.available_cams = available"""

new_enter_settings = """    def _enter_settings(self):
        # Professional hardcoded available cameras list (no slow webcam scan opening!)
        self.available_cams = [0, 1, 2, 3]"""

code = code.replace(old_enter_settings, new_enter_settings)

# 4. Enhance camera HUD with active gesture indicators & crosshair
old_camera_body = """    def _camera(self):
        if self.control_mode == 0 or self.hand is None: return
        frame = self.hand.get_frame()
        if frame is None: return
        try:
            f = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (180, 135))
            sf = pygame.surfarray.make_surface(f.swapaxes(0, 1))
            px, py = SW - 195, SH - 150
            pygame.draw.rect(self.s, BLACK, (px-3, py-3, 186, 141))
            pygame.draw.rect(self.s, WHITE, (px-3, py-3, 186, 141), 1)
            self.s.blit(sf, (px, py))
            
            lbl = self.ft.render("KAMERA", True, WHITE)
            lbl_bg = pygame.Surface((lbl.get_width()+6, 20))
            lbl_bg.fill(BLACK)
            self.s.blit(lbl_bg, (px+2, py-22))
            self.s.blit(lbl, (px+5, py-21))
        except: pass"""

new_camera_body = """    def _camera(self):
        if self.control_mode == 0 or self.hand is None: return
        frame = self.hand.get_frame()
        if frame is None: return
        try:
            f = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (180, 135))
            sf = pygame.surfarray.make_surface(f.swapaxes(0, 1))
            px, py = SW - 195, SH - 150
            
            # Premium retro camera panel container
            pygame.draw.rect(self.s, BLACK, (px-3, py-3, 186, 141))
            pygame.draw.rect(self.s, WHITE, (px-3, py-3, 186, 141), 2)
            self.s.blit(sf, (px, py))
            
            # Draw subtle blue crosshair grid showing steering center
            pygame.draw.line(self.s, (0, 120, 255, 128), (px, py + 135//2), (px + 180, py + 135//2), 1)
            pygame.draw.line(self.s, (0, 120, 255, 128), (px + 180//2, py), (px + 180//2, py + 135), 1)
            
            # Draw active hand steering target position crosshair
            hx = int(self.hand.sx * 180)
            hy = int(self.hand.sy * 135)
            if 0 <= hx <= 180 and 0 <= hy <= 135:
                pygame.draw.circle(self.s, (0, 255, 255), (px + hx, py + hy), 6, 1)
                pygame.draw.circle(self.s, (0, 255, 255), (px + hx, py + hy), 2)
                
            # Draw label
            lbl = self.ft.render("EL TAKIBI", True, GOLD)
            lbl_bg = pygame.Surface((lbl.get_width()+6, 20))
            lbl_bg.fill(BLACK)
            self.s.blit(lbl_bg, (px+2, py-22))
            self.s.blit(lbl, (px+5, py-21))
            
            # Gesture Indicators
            gest_y = py + 145
            if self.hand.peace:
                draw_retro_text(self.s, "ZIPLA", self.ft, px + 5, gest_y, GREEN, BLACK)
            elif self.hand.fist:
                draw_retro_text(self.s, "ATES ET", self.ft, px + 5, gest_y, RED, BLACK)
            else:
                draw_retro_text(self.s, "HAZIR", self.ft, px + 5, gest_y, WHITE, BLACK)
                
        except: pass"""

code = code.replace(old_camera_body, new_camera_body)

# 5. Let's add C key indicator to menu screen to switch control mode easily!
old_menu_hint = 'info = self.ft.render("YON TUSLARI: Sec | ENTER: Onayla | ESC: Cikis | R: Yeniden Baslat", True, WHITE)'
new_menu_hint = 'info = self.ft.render("YON TUSLARI: Sec | ENTER: Onayla | ESC: Cikis | R: Yeniden Baslat | C: Kontrol Degistir", True, WHITE)'
code = code.replace(old_menu_hint, new_menu_hint)

# Let's handle C key toggle inside the main menu loop
old_menu_key_detection = """                    elif e.key == pygame.K_UP:
                        if self.state == State.MENU:"""

new_menu_key_detection = """                    elif e.key == pygame.K_c:
                        if self.state == State.MENU:
                            self.control_mode = 1 - self.control_mode
                            if self.control_mode == 0:
                                if self.hand is not None:
                                    self.hand.release()
                                    self.hand = None
                            else:
                                if self.hand is None:
                                    self.hand = HandTracker(self.selected_cam_index)
                            SoundGenerator.click_sound(self.master_volume)
                            
                    elif e.key == pygame.K_UP:
                        if self.state == State.MENU:"""

code = code.replace(old_menu_key_detection, new_menu_key_detection)

# Let's display the active control mode as a nice text directly on the menu board
old_menu_logo = """        # 2. Premium Retro Menu Board
        bx, by, bw, bh = SW//2 - 230, 240, 460, 310"""

new_menu_logo = """        # 2. Premium Retro Menu Board
        bx, by, bw, bh = SW//2 - 230, 240, 460, 310
        ctrl_label = f"KONTROL: {'EL TAKIBI' if self.control_mode == 1 else 'KLAVYE'}"
        draw_retro_text(self.s, ctrl_label, self.ft, bx + 50, by - 24, GOLD, BLACK)"""

code = code.replace(old_menu_logo, new_menu_logo)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Professional loading progress bar, menu control labels, easily toggleable C-key binding, and enhanced camera indicators successfully applied!")
