import numpy as np
import pandas as pd
import skimage as ski
import matplotlib.pyplot as plt
from PIL import Image

from app.image.Image_Sharpening import unsharp_mask

lego_df, lego_rgb, lego_lab = load_lego_colors("lego_colors.csv")

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


def map_image_to_nearest_lego_color(input_image, lego_df, lego_rgb, lego_lab):
    image_rgb = input_image[:, :, :3]

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

def legoify_image(input_image):
    if isinstance(input_image, Image.Image):
        input_image = np.array(input_image)
    
    _, _, mapped_rgb, _ = map_image_to_nearest_lego_color(
        input_image,
        lego_df,
        lego_rgb,
        lego_lab
    )

    plt.imshow(mapped_rgb)
    plt.title("Obraz zmapowany do najbliższych kolorów LEGO")
    plt.axis("off")
    plt.show()
    
    