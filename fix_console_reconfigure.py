main_path = r"C:\Users\ardak\Desktop\vucut-oyun-temiz\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    code = f.read()

# Locate and replace the reconfigure logic
old_block = """if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')"""

new_block = """if sys.platform.startswith('win'):
    if sys.stdout is not None:
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    if sys.stderr is not None:
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass"""

code = code.replace(old_block, new_block)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Console reconfigure block successfully protected against None streams!")
