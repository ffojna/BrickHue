import pandas as pd
import skimage as ski

colors_df = pd.read_csv("lego_colors.csv", index_col=False)
color_map = dict(zip(colors_df["id"], colors_df["hex"]))


def hex2lab(color_hex):
    if color_hex is None:
        print("color_hex is none!")
        return

    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    return ski.color.rgb2lab(rgb)
        

lego_incorrect = color_map.get(320)
lego_correct = color_map.get(212)
image_px = (170, 200, 223)

img_px_lab = ski.color.rgb2lab(image_px)
lego_correct_lab = hex2lab(lego_correct)
lego_incorrect_lab = hex2lab(lego_incorrect)

print(ski.color.deltaE_cie76(img_px_lab, lego_correct_lab))
print(ski.color.deltaE_cie76(img_px_lab, lego_incorrect_lab))