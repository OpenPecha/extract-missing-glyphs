import cv2
import pytesseract
import json
import os
from pathlib import Path

os.environ['TESSDATA_PREFIX'] = "C:\\Users\\tenka\\tessdata"


def load_image(image_path):
    return cv2.imread(str(image_path))


def extract_image_name(image_path):
    return os.path.basename(image_path)


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
    contours, _ = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        cv2.drawContours(binary, [contour], -1, (255, 255, 255), 2)

    # remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    detect_vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
    contours, _ = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        cv2.drawContours(binary, [contour], -1, (255, 255, 255), 2)

    return binary


def get_ocr_data(binary_image):
    custom_config = r'--oem 3 --psm 6 -l bod'
    return pytesseract.image_to_data(binary_image, config=custom_config, output_type=pytesseract.Output.DICT)


def collect_line_info(data):
    lines = []
    current_line = []
    current_line_number = None

    for i in range(len(data['level'])):
        if data['level'][i] == 5: 
            line_number = data['line_num'][i]
            if line_number != current_line_number:
                if current_line:
                    lines.append(current_line)
                current_line = []
                current_line_number = line_number

            left = data['left'][i]
            top = data['top'][i]
            width = data['width'][i]
            height = data['height'][i]

            current_line.append({
                "left": left,
                "top": top,
                "width": width,
                "height": height
            })

    if current_line:
        lines.append(current_line)

    line_info = []
    for line_number, line in enumerate(lines, 1):
        if line:
            left = min(item['left'] for item in line)
            top = min(item['top'] for item in line)
            right = max(item['left'] + item['width'] for item in line)
            bottom = max(item['top'] + item['height'] for item in line)
            line_info.append({
                "line_number": line_number,
                "left": left,
                "top": top,
                "width": right - left,
                "height": bottom - top
            })

    return line_info


def create_jsonl_output(image_name, lines):
    output = []
    for line in lines:
        output.append({
            "image": image_name,
            "line_number": line['line_number'],
            "bounding_box": {
                "left": line['left'],
                "top": line['top'],
                "width": line['width'],
                "height": line['height']
            }
        })
    return output


def save_to_jsonl(output, output_path):
    with open(output_path, 'w') as f:
        for entry in output:
            f.write(json.dumps(entry) + '\n')


def process_image(image_path, output_dir):
    image = load_image(image_path)
    image_name = extract_image_name(image_path)
    image_name_without_ext = os.path.splitext(image_name)[0]
    binary_image = preprocess_image(image)
    ocr_data = get_ocr_data(binary_image)
    lines = collect_line_info(ocr_data)
    jsonl_output = create_jsonl_output(image_name_without_ext, lines)
    output_path = output_dir / f"{image_name_without_ext}.jsonl"
    save_to_jsonl(jsonl_output, output_path)


def main():
    images_dir = Path("../../data/source_images")
    output_dir = Path("../../data/ocr_jsonl")
    output_dir.mkdir(parents=True, exist_ok=True)

    for image_path in images_dir.rglob("*"):
        if image_path.suffix.lower() in ['.tif', '.jpg']:
            process_image(image_path, output_dir)


if __name__ == "__main__":
    main()
