main_path = r"C:\Users\ardak\Desktop\vucut-oyun-temiz\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add stdout/stderr reconfiguration to the top of imports
old_imports = "import pygame, random, math, time, json, sys, cv2, numpy as np, threading"
new_imports = """import pygame, random, math, time, json, sys, cv2, numpy as np, threading
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')"""

code = code.replace(old_imports, new_imports)

# 2. Replace prints with clean ASCII equivalents
code = code.replace('print("  ⚡ Çizim önbellekleri önceden yükleniyor...")',
                    'print("[Info] Cizim onbellekleri yukleniyor...")')

code = code.replace('print("  ✅ Tüm önbellekler başarıyla yüklendi!")',
                    'print("[OK] Tum onbellekler basariyla yuklendi!")')

code = code.replace('print("  🍄 SUPER MARIO BROS - ULTIMATE EDITION v3.2.2")',
                    'print("  SUPER MARIO BROS - ULTIMATE EDITION v3.2.2")')

code = code.replace('print(f"  ✅ Oyun dunyasi olusturuldu. Mario X:{self.p.x:.0f} Y:{self.p.y:.0f} Ground:{self.p.ground}")',
                    'print(f"  Oyun dunyasi olusturuldu. Mario X:{self.p.x:.0f} Y:{self.p.y:.0f} Ground:{self.p.ground}")')

code = code.replace('print("  🍄 ULTIMATE MARIO v3.2.2 BASLATILIYOR...")',
                    'print("  ULTIMATE MARIO v3.2.2 BASLATILIYOR...")')

code = code.replace('print("  ✅ Tum hatalar duzeltildi - MUSH_S sorunu cozuldu\\n")',
                    'print("  Tum hatalar duzeltildi - MUSH_S sorunu cozuldu\\n")')

code = code.replace('print(f"\\n  👋 Oyun kapandi. En yuksek skor: {self.hs:,}\\n")',
                    'print(f"\\n  Oyun kapandi. En yuksek skor: {self.hs:,}\\n")')

code = code.replace('print("\\n  ⚠️ Oyun kullanici tarafindan durduruldu.")',
                    'print("\\n  [Warn] Oyun kullanici tarafindan durduruldu.")')

code = code.replace('print(f"\\n  ❌ Kritik hata: {e}")',
                    'print(f"\\n  [Error] Kritik hata: {e}")')

with open(main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Print statements successfully cleaned of Turkish characters and emojis!")
