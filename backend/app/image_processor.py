import cv2
import numpy as np
import pandas as pd
from functools import lru_cache
import time

def load_dmc_palette() -> tuple[pd.DataFrame, np.ndarray]:
    dmc_palette = pd.read_csv("/app/assets/dmc_colors.csv", header=0)
    if 'RGB_COLOR' not in dmc_palette.columns:
        raise ValueError("The CSV file does not contain 'RGB_COLOR' column")
    rgb_colors = dmc_palette['RGB_COLOR']
    # Third column is in #hex values, convert to RGB
    dmc_palette["R"] = rgb_colors.apply(lambda x: int(x[1:3], 16))
    dmc_palette["G"] = rgb_colors.apply(lambda x: int(x[3:5], 16))
    dmc_palette["B"] = rgb_colors.apply(lambda x: int(x[5:7], 16))
    dmc_palette_rgb = np.array(dmc_palette[["R", "G", "B"]])
    return dmc_palette, dmc_palette_rgb

@lru_cache(maxsize=1024)  # Cache the results of this function
def find_closest_dmc_color(rgb_color: tuple[int, int, int]) -> dict:
    dmc_palette, dmc_palette_rgb = load_dmc_palette()
    # Calculate Euclidean distance to each DMC color
    distances = np.linalg.norm(dmc_palette_rgb - rgb_color, axis=1)
    # Return the index of the closest color
    idx = np.argmin(distances)
    info = {"index": idx, "dmc_color": dmc_palette["DMC_COLOR"][idx], "rgb": dmc_palette_rgb[idx], }
    return info

def convert_image_to_dmc_colors(img: np.ndarray) -> tuple[np.ndarray, set[str]]:
    time_start = time.time()
    # Load DMC color palette if not already loaded
    dmc_palette, dmc_palette_rgb = load_dmc_palette()
    load_time = time.time() - time_start
    print(f"Loading DMC palette took {load_time * 1000:.2f} ms")
    width, height = img.shape[:2]
    # Convert image to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Quantize colors (Cuts down processing time, utilizes cache better)
    img = img // 32 * 32

    # Flatten image to a list of RGB colors
    img = img.reshape(-1, 3)
    # Find closest DMC color for each pixel
    intervals = 1000
    used_dmc_colors = set()
    time_interval = time.time()
    for i, rgb_color in enumerate(img):
        dmc_info = find_closest_dmc_color(tuple(rgb_color))
        img[i] = dmc_info["rgb"]
        used_dmc_colors.add(dmc_info["dmc_color"])
        if i % intervals == 0:
            time_elapsed = time.time() - time_interval
            print(f"Processed {i} pixels in {time_elapsed:.2f} seconds")
            time_interval = time.time()
    time_elapsed = time.time() - time_start
    print(f"Processed {len(img)} pixels in {time_elapsed:.2} seconds")
    # Reshape to original image dimensions
    img = img.reshape(width, height, 3)
    # Convert image back to BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img, used_dmc_colors

def process_image(file_path: str, operation: str) -> str:
    output_path = f"processed/{operation}_{file_path}"
    if operation == "resize":
        # Resize example with Pillow
        img = cv2.imread(file_path)
        width_height_ratio = img.shape[1] / img.shape[0]
        # Resize larger dimension to 300px and maintain the aspect ratio
        if width_height_ratio > 1:
            img = cv2.resize(img, (300, int(300 / width_height_ratio)))
        else:
            img = cv2.resize(img, (int(300 * width_height_ratio), 300))
        cv2.imwrite(output_path, img)
    elif operation == "grayscale":
        # Grayscale example with OpenCV
        img = cv2.imread(file_path)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(output_path, gray_img)
    else:
        raise ValueError(f"Unsupported operation: {operation}. Supported operations: 'resize', 'grayscale'")
    return output_path

def convert_to_dmc(file_path: str) -> tuple[str, set[str]]:
    img = cv2.imread(file_path)
    img, dmc_colors = convert_image_to_dmc_colors(img)
    dmc_image_path = f"processed/dmc_{file_path}"
    cv2.imwrite(dmc_image_path, img)
    return dmc_image_path, dmc_colors