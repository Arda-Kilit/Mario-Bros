"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║  MARIO ULTIMATE - TAM ÇÖZÜM EXE DERLEME ARACI v2                                 ║
║  matplotlib hatası ÇÖZÜLDÜ • MediaPipe TAM uyumlu                                ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
import shutil

# Windows konsolunda utf-8 karakter desteği sağla
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def run_cmd(cmd, show_output=True):
    """Komut çalıştır ve sonucu göster"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if show_output:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Hata: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("  🍄 MARIO ULTIMATE EXE DERLEME ARACI v2")
    print("  matplotlib hatası ÇÖZÜLDÜ")
    print("=" * 70 + "\n")
    
    GAME_NAME = "MarioBros"
    MAIN_FILE = "main.py"
    
    # 1. Dosya kontrolü
    if not os.path.exists(MAIN_FILE):
        print(f"❌ {MAIN_FILE} bulunamadı!")
        sys.exit(1)
    
    print(f"✅ Oyun dosyası: {MAIN_FILE}")
    print(f"✅ Çıkacak EXE: {GAME_NAME}.exe")
    
    # 2. Gerekli paketleri yükle
    print("\n📦 Gerekli paketler kontrol ediliyor...")
    
    packages = [
        'pyinstaller',
        'pygame', 
        'mediapipe', 
        'opencv-python', 
        'numpy',
        'matplotlib'  # BU ÇOK ÖNEMLİ!
    ]
    
    for pkg in packages:
        print(f"   Kontrol: {pkg}...", end=" ")
        try:
            __import__(pkg.replace('-', '_').split('[')[0])
            print("✅")
        except:
            print("📥 Yükleniyor...")
            run_cmd(f'"{sys.executable}" -m pip install {pkg} --quiet')
            print("   ✅ Yüklendi")
    
    # 3. Temizlik
    print("\n🧹 Temizlik yapılıyor...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
            print(f"   ✅ {folder} silindi")
    for f in os.listdir('.'):
        if f.endswith('.spec'):
            os.remove(f)
            print(f"   ✅ {f} silindi")
    
    # 4. ÖNEMLİ: MediaPipe modül yolunu bul
    print("\n🔍 MediaPipe modül yolu aranıyor...")
    
    try:
        import mediapipe
        mp_path = os.path.dirname(mediapipe.__file__)
        print(f"   ✅ MediaPipe: {mp_path}")
        
        # modules klasörünü bul
        modules_path = os.path.join(mp_path, 'modules')
        if os.path.exists(modules_path):
            print(f"   ✅ Modules: {modules_path}")
        else:
            print(f"   ⚠️  Modules klasörü bulunamadı!")
    except:
        print("   ❌ MediaPipe import edilemedi!")
        mp_path = None
    
    # 5. DERLEME - KESİN ÇÖZÜM
    print(f"\n🔨 {GAME_NAME}.exe DERLENİYOR...")
    print("⏳ Bu işlem 3-5 dakika sürebilir...\n")
    
    # ÖNEMLİ: Tüm hidden import'ları ekle
    hidden_imports = [
        'matplotlib',
        'matplotlib.backends',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends.backend_svg',
        'matplotlib.figure',
        'matplotlib.axes',
        'matplotlib.artist',
        'mediapipe',
        'mediapipe.python',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.hands',
        'mediapipe.python.solutions.hands_connections',
        'mediapipe.python.solutions.drawing_utils',
        'mediapipe.python.solutions.drawing_styles',
        'mediapipe.python.solutions.face_detection',
        'mediapipe.python.solutions.face_mesh',
        'mediapipe.python.solutions.pose',
        'cv2',
        'cv2.data',
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'pygame',
        'pygame.mixer',
        'pygame.surfarray',
        'pygame.sndarray',
        'pygame.locals',
        'pygame.display',
        'pygame.event',
        'pygame.draw',
        'pygame.font',
        'pygame.image',
        'pygame.key',
        'pygame.mouse',
        'pygame.rect',
        'pygame.surface',
        'pygame.time',
        'pygame.transform',
    ]
    
    # Derleme komutunu oluştur
    cmd_parts = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        f'--name={GAME_NAME}',
        '--clean',
        '--noconfirm',
        '--log-level=INFO',
    ]
    
    # Hidden import'ları ekle
    for hi in hidden_imports:
        cmd_parts.extend(['--hidden-import', hi])
    
    # Collect-all'ları ekle
    for module in ['mediapipe', 'cv2', 'pygame', 'numpy', 'matplotlib']:
        cmd_parts.append(f'--collect-all={module}')
    
    # MediaPipe data dosyalarını ekle
    if mp_path:
        cmd_parts.extend(['--add-data', f'{mp_path}{os.pathsep}mediapipe'])
    
    # Ana dosyayı ekle
    cmd_parts.append(MAIN_FILE)
    
    # Komutu göster
    print("📋 Derleme komutu:")
    print(" ".join(cmd_parts[:10]) + " ... (devamı var)")
    print()
    
    # Derlemeyi başlat
    result = subprocess.run(cmd_parts)
    
    # 6. Sonuç kontrolü
    print("\n" + "=" * 70)
    
    dist_path = os.path.join(os.getcwd(), 'dist')
    exe_path = os.path.join(dist_path, f'{GAME_NAME}.exe')
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ DERLEME BAŞARILI!")
        print(f"📁 {exe_path}")
        print(f"📏 Boyut: {size_mb:.1f} MB")
        
        # Masaüstüne MARIO_BROS klasörü oluştur
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        mario_folder = os.path.join(desktop, 'MARIO_BROS')
        os.makedirs(mario_folder, exist_ok=True)
        
        # EXE'yi kopyala
        dest_exe = os.path.join(mario_folder, f'{GAME_NAME}.exe')
        shutil.copy2(exe_path, dest_exe)
        print(f"📋 Kopyalandı: {dest_exe}")
        
        # Klasörü aç
        os.startfile(mario_folder)
        
        print(f"\n🎉 OYUNUNUZ HAZIR!")
        print(f"📂 {mario_folder}\\{GAME_NAME}.exe")
        print(f"   Çift tıklayarak başlatabilirsiniz!")
    else:
        print("❌ DERLEME BAŞARISIZ!")
        print("   Lütfen yukarıdaki hata mesajlarını kontrol edin.")
        print("\n   Alternatif çözüm için şu komutu deneyin:")
        print(f"   {sys.executable} -m PyInstaller --onefile --windowed --name {GAME_NAME} --hidden-import matplotlib --collect-all mediapipe --collect-all matplotlib {MAIN_FILE}")
    print("\n👋 Çıkış yapılıyor...")

if __name__ == '__main__':
    main()