from rembg import remove
from PIL import Image

input_image = Image.open("logo.png")
output_image = remove(input_image)
output_image.save("logo_transparent.png")
print("✅ Done! logo_transparent.png created")