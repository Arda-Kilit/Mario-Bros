main_path = r"C:\Users\ardak\Desktop\vucut-oyun-temiz\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    code = f.read()

# Let's replace the draw_goomba function completely using regex or exact string replacement
old_goomba_block = """def draw_goomba(s, x, y, bob):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    # Head mushroom shape
    for py in range(2, 10):
        for px in range(2, 14):
            surf.set_at((px, py), GMBODY)
    # Eyes
    for px in [4, 5, 10, 11]:
        surf.set_at((px, 5), WHITE)
        surf.set_at((px, 6), BLACK)
    # Mouth
    for px in range(5, 11):
        surf.set_at((px, 8), BLACK)
    # Stem
    for py in range(10, 13):
        for px in range(4, 12):
            surf.set_at((px, py), GMHEAD)
    # Feet
    for py in range(13, 16):
        for px in range(2, 6):
            surf.set_at((px, py), BLACK)
        for px in range(10, 14):
            surf.set_at((px, py), BLACK)
            
    scaled = pygame.transform.scale(surf, (32, 32))
    s.blit(scaled, (x, y + int(bob)))"""

new_goomba_block = """def draw_goomba(s, x, y, bob):
    key = round(bob, 1)
    if key not in _goomba_cache:
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        for py in range(2, 10):
            for px in range(2, 14):
                surf.set_at((px, py), GMBODY)
        for px in [4, 5, 10, 11]:
            surf.set_at((px, 5), WHITE)
            surf.set_at((px, 6), BLACK)
        for px in range(5, 11):
            surf.set_at((px, 8), BLACK)
        for py in range(10, 13):
            for px in range(4, 12):
                surf.set_at((px, py), GMHEAD)
        for py in range(13, 16):
            for px in range(2, 6):
                surf.set_at((px, py), BLACK)
            for px in range(10, 14):
                surf.set_at((px, py), BLACK)
        _goomba_cache[key] = pygame.transform.scale(surf, (32, 32))
    if s is not None:
        s.blit(_goomba_cache[key], (x, y + int(bob)))"""

code = code.replace(old_goomba_block, new_goomba_block)

# Let's clean up any double 'if s is not None:' that might have occurred anywhere
code = code.replace("    if s is not None:\n\n        s.blit", "    if s is not None:\n        s.blit")
code = code.replace("    if s is not None:\n        if s is not None:\n        s.blit", "    if s is not None:\n        s.blit")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Goomba function successfully cached and protected!")
