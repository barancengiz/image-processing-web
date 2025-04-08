import cv2
import numpy as np
import pandas as pd
import sqlite3
from functools import lru_cache
import time
from .kmeans_utils import kmeans_quantize

def load_all_dmc_colors() -> tuple[list[str], np.ndarray, list[str]]:
    conn = sqlite3.connect("/app/assets/dmc_colors.db")
    cursor = conn.cursor()
    query = "SELECT DMC_CODE, R, G, B, HEX FROM dmc_colors"
    cursor.execute(query)
    rows = cursor.fetchall()
    # Create three arrays with DMC codes, RGB values, and HEX values
    dmc_codes = [row[0] for row in rows]
    dmc_colors = np.array([[row[1], row[2], row[3]] for row in rows])
    hex_values = [row[4] for row in rows]
    conn.close()
    return dmc_codes, dmc_colors, hex_values

def load_specific_dmc_colors(dmc_codes_query: list[str]) -> tuple[list[str], np.ndarray]:
    conn = sqlite3.connect("/app/assets/dmc_colors.db")
    cursor = conn.cursor()
    placeholders = ", ".join("?" * len(dmc_codes_query))
    query = f"SELECT DMC_CODE, R, G, B, HEX FROM dmc_colors WHERE DMC_CODE IN ({placeholders})"
    cursor.execute(query, dmc_codes_query)

    rows = cursor.fetchall()
    # Create three arrays with DMC codes, RGB values, and HEX values
    dmc_codes = [row[0] for row in rows]
    dmc_colors = np.array([[row[1], row[2], row[3]] for row in rows])
    hex_values = [row[4] for row in rows]
    conn.close()
    # If not all DMC codes are found, raise an error
    if len(set(dmc_codes_query) - set(dmc_codes)):
        raise ValueError(f"Not all DMC codes were found in the database. Missing codes: {set(dmc_codes_query) - set(dmc_codes)}")
    return dmc_codes, dmc_colors, hex_values

def rgb_to_hsv(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    rgb_array = np.array(rgb).astype(np.uint8).reshape(1, 1, 3)
    hsv_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)
    return tuple(hsv_array[0, 0])

def convert_image_to_dmc_colors(img: np.ndarray, 
                               selected_dmc_codes: list[str] = None, 
                               replaced_colors_dict: dict = {}, 
                               n_colors: int = 50, 
                               image_width: int = 1000, 
                               use_grid_filter: bool = False) -> tuple[np.ndarray, set[str], set[str]]:
    @lru_cache(maxsize=2048)  # Cache the results of this function
    def find_closest_dmc_color_idx(selected_rgb_color: tuple[int, int, int]) -> int:
        # Calculate Euclidean distance to each DMC color
        distances = np.linalg.norm(dmc_colors - np.array(selected_rgb_color), axis=1)
        # Return the index of the closest color
        return np.argmin(distances)
    time_start = time.time()
    height, width = img.shape[:2]
    # Bilateral filter to smooth image
    img = cv2.bilateralFilter(img, 5, 75, 75)
    if use_grid_filter:
        img = cv2.medianBlur(img, 3)        
    # Resize image
    img = cv2.resize(img, (image_width, int(image_width * height / width)), interpolation=cv2.INTER_NEAREST)
    height, width = img.shape[:2]

    # Convert image to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Quantize colors (Cuts down processing time, utilizes cache better)
    img = img // 32 * 32
    # Flatten image to a list of RGB colors
    img = img.reshape(-1, 3)
    img = kmeans_quantize(img, n_colors)

    # Get unique DMC numbers and their numeric values
    dmc_codes, dmc_colors, hex_values = load_all_dmc_colors() if selected_dmc_codes is None else load_specific_dmc_colors(selected_dmc_codes)
    # For each dmc code in replaced colors dict, get dmc_color and hex value
    if replaced_colors_dict is None:
        dmc_codes_rep, dmc_colors_rep, hex_values_rep = None, None, None
        replaced_colors_dict = {}
    else:
        dmc_codes_rep, dmc_colors_rep, hex_values_rep = load_specific_dmc_colors(list(replaced_colors_dict.values()))

    # Save used unique colors and their hex values
    used_dmc_codes = []
    used_dmc_colors = []
    used_hex_values = []
    used_hsv_values = []
    # Count the number of times each DMC color is used
    used_color_counts = {}

    # Find closest DMC color for each pixel
    for i, rgb_color in enumerate(img):
        color_idx = find_closest_dmc_color_idx(tuple(rgb_color))
        # If the color is in the replaced colors dict, use the replaced color
        if dmc_codes[color_idx] in replaced_colors_dict.keys():
            dmc_code = replaced_colors_dict[dmc_codes[color_idx]]
            color_idx_rep = dmc_codes_rep.index(dmc_code)
            img[i] = dmc_colors_rep[color_idx_rep]
            if dmc_code not in used_dmc_codes:
                used_dmc_codes.append(dmc_code)
                used_hex_values.append(hex_values_rep[color_idx_rep])
                used_dmc_colors.append(dmc_colors_rep[color_idx_rep])
                used_hsv_values.append(rgb_to_hsv(dmc_colors_rep[color_idx_rep]))
                used_color_counts[dmc_code] = 1
            else:
                used_color_counts[dmc_code] += 1
        # If the color is not in the replaced colors dict, use the original DMC color
        else:
            img[i] = dmc_colors[color_idx]
            if dmc_codes[color_idx] not in used_dmc_codes:
                used_dmc_codes.append(dmc_codes[color_idx])
                used_hex_values.append(hex_values[color_idx])
                used_dmc_colors.append(dmc_colors[color_idx])
                used_hsv_values.append(rgb_to_hsv(dmc_colors[color_idx]))
                used_color_counts[dmc_codes[color_idx]] = 1
            else:
                used_color_counts[dmc_codes[color_idx]] += 1
    # Sort by hue values
    hsv_value_sorted_idxs = np.argsort([hsv[0] for hsv in used_hsv_values])
    # Get the sorted DMC codes, hex values, and color counts
    used_dmc_codes = [used_dmc_codes[i] for i in hsv_value_sorted_idxs]
    used_hex_values = [used_hex_values[i] for i in hsv_value_sorted_idxs]
    used_color_counts = [used_color_counts[used_dmc_codes[i]] for i in hsv_value_sorted_idxs]

    time_elapsed = time.time() - time_start
    print(f"Processed {len(img)} pixels in {time_elapsed:.2} seconds")
    
    # Reshape to original image dimensions
    img = img.reshape(height, width, 3)
    # Convert image back to BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # Resize into displayable size
    display_width = 1024
    img = cv2.resize(img, (display_width, int(display_width * height / width)), interpolation=cv2.INTER_NEAREST)
    
    return img, used_dmc_codes, used_hex_values, used_color_counts

def process_image(file_path: str, operation: str) -> str:
    output_path = f"processed/{operation}_{file_path}"
    if operation == "resize":
        img = cv2.imread(file_path)
        width_height_ratio = img.shape[1] / img.shape[0]
        resize_large_side = 240
        # Resize larger dimension to given value and maintain the aspect ratio
        if width_height_ratio > 1:
            img = cv2.resize(img, (resize_large_side, int(resize_large_side / width_height_ratio)))
        else:
            img = cv2.resize(img, (int(resize_large_side * width_height_ratio), resize_large_side))
        cv2.imwrite(output_path, img)
    elif operation == "grayscale":
        # Grayscale example with OpenCV
        img = cv2.imread(file_path)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(output_path, gray_img)
    else:
        raise ValueError(f"Unsupported operation: {operation}. Supported operations: 'resize', 'grayscale'")
    return output_path

def convert_to_dmc(file_path: str, 
                  selected_dmc_codes: list[str] = None, 
                  replaced_colors_dict: dict = {}, 
                  n_colors: int = 50, 
                  image_width: int = 1000, 
                  use_grid_filter: bool = False) -> tuple[str, list[str], list[str]]:
    img = cv2.imread(file_path)
    img, dmc_codes, hex_values, color_counts = convert_image_to_dmc_colors(img, 
                                                                          selected_dmc_codes, 
                                                                          replaced_colors_dict,
                                                                          n_colors, 
                                                                          image_width, 
                                                                          use_grid_filter)

    dmc_image_path = f"processed/dmc_{file_path}"
    cv2.imwrite(dmc_image_path, img)
    return dmc_image_path, dmc_codes, hex_values, color_counts