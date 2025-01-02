import cv2

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