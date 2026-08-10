import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# =========================================================
# CHANGE THIS PATH TO YOUR TEST IMAGE
# =========================================================
IMAGE_PATH = "test_assets/pacific_rim.jpg"   


from skimage.filters import gaussian

@staticmethod
def unsharp_mask(img, sigma=2.0, amount=1.5):
    """
    Unsharp masking.

    Parameters
    ----------
    img : ndarray
        Obraz jako tablica NumPy (float w zakresie [0, 1]).
    sigma : float
        Odchylenie standardowe filtru Gaussa.
    amount : float
        Siła wyostrzania.

    Returns
    -------
    blur : ndarray
        Rozmyty obraz.
    sharpened : ndarray
        Wyostrzony obraz.
    """
    
    if isinstance(img, Image.Image):
        img = np.asarray(img).astype(np.float32) / 255.0
    
    blur = gaussian(img, sigma=sigma, channel_axis=-1)
    detail = img - blur
    sharpened = np.clip(img + amount * detail, 0.0, 1.0)

    return blur, sharpened


def laplacian_sharpen(img, alpha=0.5):
    """
    Laplacian-based sharpening:
    - Compute Laplacian (second derivative)
    - Subtract scaled Laplacian from the image
    """
    lap = cv2.Laplacian(img, cv2.CV_32F, ksize=3)
    sharpened = img - alpha * lap
    sharpened = np.clip(sharpened, 0.0, 1.0)
    return sharpened


def kernel_sharpen(img):
    """
    Sharpening with a simple 3x3 kernel.
    This is a classic '5-center' sharpening filter.
    """
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]], dtype=np.float32)
    sharpened = cv2.filter2D(img, ddepth=-1, kernel=kernel)
    sharpened = np.clip(sharpened, 0.0, 1.0)
    return sharpened


def to_uint8(img_float):
    """Convert float32 [0,1] image to uint8 [0,255]."""
    return (np.clip(img_float, 0.0, 1.0) * 255).astype(np.uint8)


def main():
    # -----------------------------------------------------
    # Load image (BGR) and convert to float32 [0,1]
    # -----------------------------------------------------
    bgr = cv2.imread(IMAGE_PATH)
    if bgr is None:
        raise FileNotFoundError(f"Could not read image: {IMAGE_PATH}")

    img = bgr.astype(np.float32) / 255.0  # work in float

    # =====================================================
    # 1. UNSHARP MASKING
    # =====================================================
    blur, sharpen_unsharp = unsharp_mask(img, sigma=2.0, amount=1.5)

    # =====================================================
    # 2. LAPLACIAN SHARPENING
    # =====================================================
    sharpen_laplacian = laplacian_sharpen(img, alpha=2.5)

    # =====================================================
    # 3. KERNEL-BASED SHARPENING
    # =====================================================
    sharpen_kernel = kernel_sharpen(img)

    # -----------------------------------------------------
    # Prepare for display (convert to RGB uint8 for matplotlib)
    # -----------------------------------------------------
    orig_rgb = cv2.cvtColor(to_uint8(img), cv2.COLOR_BGR2RGB)
    blur_rgb = cv2.cvtColor(to_uint8(blur), cv2.COLOR_BGR2RGB)
    unsharp_rgb = cv2.cvtColor(to_uint8(sharpen_unsharp), cv2.COLOR_BGR2RGB)
    laplacian_rgb = cv2.cvtColor(to_uint8(sharpen_laplacian), cv2.COLOR_BGR2RGB)
    kernel_rgb = cv2.cvtColor(to_uint8(sharpen_kernel), cv2.COLOR_BGR2RGB)

    # -----------------------------------------------------
    # Show original, blurred, and sharpened images together
    # -----------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))

    # Row 1
    axes[0, 0].imshow(orig_rgb)
    axes[0, 0].set_title("Original")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(blur_rgb)
    axes[0, 1].set_title("Blurred (Gaussian)")
    axes[0, 1].axis("off")

    axes[0, 2].imshow(unsharp_rgb)
    axes[0, 2].set_title("Unsharp Masking")
    axes[0, 2].axis("off")

    # Row 2
    axes[1, 0].imshow(laplacian_rgb)
    axes[1, 0].set_title("Laplacian Sharpening")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(kernel_rgb)
    axes[1, 1].set_title("3×3 Kernel Sharpening")
    axes[1, 1].axis("off")

    # Last slot empty or reused (optional)
    axes[1, 2].axis("off")

    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------
    # Save results
    # -----------------------------------------------------
    cv2.imwrite("output_blur.png", to_uint8(blur))
    cv2.imwrite("output_unsharp.png", to_uint8(sharpen_unsharp))
    cv2.imwrite("output_laplacian.png", to_uint8(sharpen_laplacian))
    cv2.imwrite("output_kernel.png", to_uint8(sharpen_kernel))
    print("Saved blurred and sharpened images to current folder.")


if __name__ == "__main__":
    main()
