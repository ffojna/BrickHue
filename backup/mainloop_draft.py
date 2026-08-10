import numpy as np
import pandas as pd
import skimage as ski
import matplotlib.pyplot as plt
from PIL import Image

from app.image.Image_Sharpening import unsharp_mask


def load_lego_colors(csv_path="all_colors.csv"):
    df = pd.read_csv(csv_path)

    lego_rgb = np.array([
        [
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        ]
        for hex_color in df["hex"]
    ], dtype=np.float32) / 255.0

    lego_lab = ski.color.rgb2lab(
        lego_rgb.reshape(1, -1, 3)
    ).reshape(-1, 3)

    return df, lego_rgb, lego_lab


def map_image_to_nearest_lego_color(image_rescaled, lego_df, lego_rgb, lego_lab):
    image_rgb = image_rescaled[:, :, :3]

    image_lab = ski.color.rgb2lab(image_rgb)

    h, w, _ = image_lab.shape

    mapped_ids = np.zeros((h, w), dtype=int)
    mapped_hex = np.empty((h, w), dtype=object)
    mapped_rgb = np.zeros((h, w, 3), dtype=np.float32)
    delta_map = np.zeros((h, w), dtype=np.float32)

    for y in range(h):
        for x in range(w):
            pixel_lab = image_lab[y, x]

            distances = ski.color.deltaE_ciede2000(
                pixel_lab.reshape(1, 1, 3),
                lego_lab.reshape(1, -1, 3)
            ).ravel()

            best_idx = np.argmin(distances)

            mapped_ids[y, x] = int(lego_df.iloc[best_idx]["id"])
            mapped_hex[y, x] = lego_df.iloc[best_idx]["hex"]
            mapped_rgb[y, x] = lego_rgb[best_idx]
            delta_map[y, x] = distances[best_idx]

    return mapped_ids, mapped_hex, mapped_rgb, delta_map


lego_df, lego_rgb, lego_lab = load_lego_colors("lego_colors.csv")

def create_downscaled_lego(image_array):
    if isinstance(image_array, Image.Image):
        image_array = np.array(image_array)
    
    mapped_ids, mapped_hex, mapped_rgb, delta_map = map_image_to_nearest_lego_color(
        image_array,
        lego_df,
        lego_rgb,
        lego_lab
    )

    plt.imshow(mapped_rgb)
    plt.title("Obraz zmapowany do najbliższych kolorów LEGO")
    plt.axis("off")
    plt.show()

image_pil = Image.open("test_assets/pacific_rim_sharp.png")
image_pil_rgb = image_pil.convert('RGB')

w, h = image_pil_rgb.size

new_h = 100
new_w = int(w * (new_h/h))
out = image_pil_rgb.resize((new_w, new_h), Image.BICUBIC)
out.show()

out.save("test_assets/jpeg_10_grey.jpeg", "JPEG", quality=10)

image_jpeg_10 = ski.io.imread("test_assets/jpeg_10_grey.jpeg")

plt.imshow(image_jpeg_10)
plt.title("Obraz JPEG, 10% quality")
plt.axis("off")
plt.show()

create_downscaled_lego(out)

