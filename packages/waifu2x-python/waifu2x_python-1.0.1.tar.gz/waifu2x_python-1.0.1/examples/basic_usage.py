# Depois de instalada
from waifu2x_python import Waifu2x

# Configurar
upscaler = Waifu2x(
    executable_path="/path/to/waifu2x-ncnn-vulkan",
    model="models-cunet",
    scale=2,
    noise=1
)

# Usar
result = upscaler.upscale_folder("input_frames", "output_frames")
print(f"Processados {len(result)} frames")