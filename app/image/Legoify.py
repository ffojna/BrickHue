import pandas as pd
import numpy as np
import skimage as ski
import customtkinter as ctk
from PIL import Image

from .Image_Sharpening import unsharp_mask

class Legoify:
    def __init__(self, colors_csv_path):
        df, lego_rgb, lego_lab = self.load_lego_colors(colors_csv_path)
        
        self.colors_df = df
        self.lego_rgb = lego_rgb
        self.lego_lab = lego_lab
    
    
    def load_lego_colors(self, csv_path="all_colors.csv"):
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
    
    
    def map_image_to_nearest_lego_color(self, input_array):
        if isinstance(input_array, Image.Image):
            image_array = np.asarray(input_array).astype(np.float32) / 255.0
        
        image_rgb = image_array[:, :, :3]

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
                    self.lego_lab.reshape(1, -1, 3)
                ).ravel()

                best_idx = np.argmin(distances)

                mapped_ids[y, x] = int(self.colors_df.iloc[best_idx]["id"])
                mapped_hex[y, x] = self.colors_df.iloc[best_idx]["hex"]
                mapped_rgb[y, x] = self.lego_rgb[best_idx]
                delta_map[y, x] = distances[best_idx]

        return mapped_ids, mapped_hex, mapped_rgb, delta_map
    
    
    def generate_lego_image(self, input_image, sigma, amount, target_size: tuple):
        
        if isinstance(input_image, np.ndarray):
            input_image = Image.fromarray((input_image * 255).astype(np.uint8))
        
        # wyostrz
        _, sharpened_array = unsharp_mask(input_image, sigma=sigma, amount=amount)
        sharpened_image = Image.fromarray((sharpened_array * 255).astype(np.uint8))
        
        # przeskaluj
        sharpened_resized_image = sharpened_image.resize(target_size, resample=Image.Resampling.BICUBIC)
        
        # zmapuj na lego kolory
        mapped_ids, mapped_hex, mapped_rgb, _ = self.map_image_to_nearest_lego_color(sharpened_resized_image)
        
        return mapped_ids, mapped_hex, mapped_rgb
    
    
    def decode_color_from_id(self, id: int):
        
        row = self.colors_df.loc[self.colors_df["id"] == id].iloc[0]

        return {
            "id": row["id"],
            "name": row["name"],
            "hex": row["hex"],
        }