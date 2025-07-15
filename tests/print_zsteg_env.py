import os
import shutil

print("PYTHON PATH:", os.environ["PATH"])
print("ZSTEG FOUND AT:", shutil.which("zsteg"))
print(shutil.which("zsteg"))
