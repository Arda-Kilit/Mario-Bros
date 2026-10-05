main_path = r"C:\Users\ardak\Desktop\vucut-oyun-temiz\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    code = f.read()

old_block = """def draw_menu_mushroom(s, x, y, size=24):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    grid = [
        "......RRRR......",
        "....RRRRRRRR....",
        "...RRWWRRRRWWR..",
        "..RRWWRRRRRRWWR.",
        ".RRRRRRWWRRRRRRR",
        ".RRRRRRWWRRRRRRR",
        "RRRWRRRRRRRRWRRR",
        "RRRWRRRRRRRRWRRR",
        "RRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRR",
        "....SSSSSSSS....",
        "...SSKSKSSKSS...",
        "...SSKSKSSKSS...",
        "...SSSSSSSSSS...",
        "....SSSSSSSS....",
        ".....SSSSSS....."
    ]
    colors = {
        '.': (0,0,0,0),
        'R': (220, 20, 20),
        'W': (255, 255, 255),
        'S': (255, 220, 180),
        'K': (0, 0, 0)
    }
    for py, row in enumerate(grid):
        for px, char in enumerate(row):
            surf.set_at((px, py), colors[char])
    scaled = pygame.transform.scale(surf, (size, size))
    s.blit(scaled, (x, y))"""

new_block = """def draw_menu_mushroom(s, x, y, size=24):
    key = size
    if key not in _menu_mushroom_cache:
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        grid = [
            "......RRRR......",
            "....RRRRRRRR....",
            "...RRWWRRRRWWR..",
            "..RRWWRRRRRRWWR.",
            ".RRRRRRWWRRRRRRR",
            ".RRRRRRWWRRRRRRR",
            "RRRWRRRRRRRRWRRR",
            "RRRWRRRRRRRRWRRR",
            "RRRRRRRRRRRRRRRR",
            "RRRRRRRRRRRRRRRR",
            "....SSSSSSSS....",
            "...SSKSKSSKSS...",
            "...SSKSKSSKSS...",
            "...SSSSSSSSSS...",
            "....SSSSSSSS....",
            ".....SSSSSS....."
        ]
        colors = {
            '.': (0,0,0,0),
            'R': (220, 20, 20),
            'W': (255, 255, 255),
            'S': (255, 220, 180),
            'K': (0, 0, 0)
        }
        for py, row in enumerate(grid):
            for px, char in enumerate(row):
                surf.set_at((px, py), colors[char])
        _menu_mushroom_cache[key] = pygame.transform.scale(surf, (size, size))
    if s is not None:
        s.blit(_menu_mushroom_cache[key], (x, y))"""

code = code.replace(old_block, new_block)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("draw_menu_mushroom replacement completed!")
