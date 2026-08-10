import skimage as ski
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from image.Legoify import Legoify
from image.Image_Sharpening import unsharp_mask

# załaduj właściwe kolory do instancji klasy Legoify oraz zdjęcie do testów
lego = Legoify("C:/Users/ff53721/Desktop/LegoHue/assets/lego_colors.csv")
start_image = Image.open("C:/Users/ff53721/Desktop/LegoHue/test_assets/pacific_rim.jpg")                           # oryginalne zdjęcie

_, sharpened_array = unsharp_mask(start_image, sigma=6, amount=3)
sharpen_unsharp = Image.fromarray((sharpened_array * 255).astype(np.uint8))    # wyostrzone oryginalne


# przeskalowanie oryginalnego zdjęcia w dół
w, h = start_image.size
new_h = int(100)
new_w = int(w * (new_h / h))

# rescaled_image = start_image.resize((new_w, new_h), resample=Image.Resampling.BICUBIC) # przeskalopwane orygilane

sharpen_resized = sharpen_unsharp.resize((new_w, new_h), resample=Image.Resampling.BICUBIC) # wyostrzone->przeskalowane

# _, rescaled_shapened_array = unsharp_mask(rescaled_image, sigma=6, amount=3)
# rescaled_sharpened = Image.fromarray((rescaled_shapened_array * 255).astype(np.uint8)) # przeskalowane->wyostrzone


mapped_ids, mapped_hex, mapped_rgb_sharpen_resized, delta_map = lego.map_image_to_nearest_lego_color(sharpen_resized)
# _, _, mapped_rgb_resized_sharpen, _ = lego.map_image_to_nearest_lego_color(rescaled_sharpened)

fig, axes = plt.subplots(1, 2)

axes[0].imshow(mapped_rgb_sharpen_resized)
axes[0].set_title("Wyostrzone->przeskalowane")
axes[0].axis("off")

axes[1].imshow(mapped_rgb_resized_sharpen)
axes[1].set_title("Przeskalowane->wyostrzone")
axes[1].axis("off")

plt.tight_layout()
plt.show()

with open("image_data.txt", "w") as txt_file:
    txt_file.write("mapped_ids:\n")
    for line in mapped_ids:
        txt_file.write("   ".join(str(line)) + " \n ")
        
    txt_file.write("\n\nmapped_hex:\n")
    for line in mapped_hex:
        txt_file.write("   ".join(str(line)) + " \n ")
        
    txt_file.write("\n\nmapped_rgb:\n")
    for line in mapped_rgb_sharpen_resized:
        txt_file.write("   ".join(str(line)) + " \n ")
        
    txt_file.write("\n\ndelta_map:\n")
    for line in delta_map:
        txt_file.write("   ".join(str(line)) + " \n ")
        