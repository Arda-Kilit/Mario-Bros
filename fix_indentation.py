import re

main_path = r"C:\Users\ardak\Desktop\vucut-oyun-temiz\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    code = f.read()

# Let's fix duplicate `if s is not None:` and fix indentation for all functions
# We can use a regex replacement to clean up the double if s is not None:
# Example:
#     if s is not None:
#         if s is not None:
#         s.blit(...)
# should become:
#     if s is not None:
#         s.blit(...)

# We can search for:
#     if s is not None:
#         if s is not None:
#         s.blit
# and replace it with:
#     if s is not None:
#         s.blit

code = re.sub(
    r"(\s+)if s is not None:\s+if s is not None:\s+s\.blit",
    r"\1if s is not None:\n\1    s.blit",
    code
)

# Also let's clean up any:
#     if s is not None:
#     s.blit
# and make it:
#     if s is not None:
#         s.blit

code = re.sub(
    r"(\s+)if s is not None:\s+s\.blit",
    r"\1if s is not None:\n\1    s.blit",
    code
)

# Let's double check if there are other indentation errors with s.blit
# We can print or write this first and check compile
with open(main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Indentation cleaned up!")
