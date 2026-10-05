main_path = r"C:\Users\ardak\Desktop\vucut-oyun-temiz\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    code = f.read()

replacements = {
    "s.blit(_goomba_cache[key], (x, y + int(bob)))": "if s is not None:\n        s.blit(_goomba_cache[key], (x, y + int(bob)))",
    "s.blit(_koopa_cache[key], (x, y + int(bob)))": "if s is not None:\n        s.blit(_koopa_cache[key], (x, y + int(bob)))",
    "s.blit(_piranha_cache['base'], (x, y + int(bob)))": "if s is not None:\n        s.blit(_piranha_cache['base'], (x, y + int(bob)))",
    "s.blit(_mushroom_cache[key], (x, y + int(bob)))": "if s is not None:\n        s.blit(_mushroom_cache[key], (x, y + int(bob)))",
    "s.blit(_mario_cache[key], (x, y))": "if s is not None:\n        s.blit(_mario_cache[key], (x, y))",
    "s.blit(_shadow_cache[key], (x - w // 2, y - max(1, w // 3) // 2))": "if s is not None:\n        s.blit(_shadow_cache[key], (x - w // 2, y - max(1, w // 3) // 2))",
    "s.blit(_coin_cache[key], (x - 8, y - 8))": "if s is not None:\n        s.blit(_coin_cache[key], (x - 8, y - 8))",
    "s.blit(_brick_cache['base'], (x, y - bounce))": "if s is not None:\n        s.blit(_brick_cache['base'], (x, y - bounce))",
    "s.blit(_qblock_cache[key], (x, y - bounce))": "if s is not None:\n        s.blit(_qblock_cache[key], (x, y - bounce))",
    "s.blit(_pipe_cache[key], (x - 4, y))": "if s is not None:\n        s.blit(_pipe_cache[key], (x - 4, y))",
    "s.blit(_pixel_heart_cache[key], (x, y))": "if s is not None:\n        s.blit(_pixel_heart_cache[key], (x, y))",
    "s.blit(_pixel_clock_cache[key], (x, y))": "if s is not None:\n        s.blit(_pixel_clock_cache[key], (x, y))",
    "s.blit(_pixel_star_cache[key], (x, y))": "if s is not None:\n        s.blit(_pixel_star_cache[key], (x, y))",
    "s.blit(_menu_mushroom_cache[key], (x, y))": "if s is not None:\n        s.blit(_menu_mushroom_cache[key], (x, y))"
}

# Also check if there are other s.blit in the draw_mario rainbow mode
# s.blit(pygame.transform.scale(surf, (w, h)), (x, y))
# We should guard this too just in case:
code = code.replace("s.blit(pygame.transform.scale(surf, (w, h)), (x, y))",
                    "if s is not None:\n            s.blit(pygame.transform.scale(surf, (w, h)), (x, y))")

for old, new in replacements.items():
    code = code.replace(old, new)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Blit guards successfully applied to all drawing functions!")
