import pytesseract
from pytesseract import Output
import cv2
import json
import os

os.environ['TESSDATA_PREFIX'] = "C:\\Users\\tenka\\tessdata"

def extract_line_info(image_path, output_path):
    image_name = os.path.basename(image_path)
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    custom_config = r'--oem 3 --psm 6 -l bod'
    data = pytesseract.image_to_data(thresh, config=custom_config, output_type=Output.DICT)

    line_info = []
    n_boxes = len(data['level'])
    line_number = 0
    current_line_top = data['top'][0]
    current_line_bottom = data['top'][0] + data['height'][0]
    line_bounding_box = {
        'left': data['left'][0],
        'top': data['top'][0],
        'width': data['width'][0],
        'height': data['height'][0]
    }

    for i in range(n_boxes):
        word_box = {
            'left': data['left'][i],
            'top': data['top'][i],
            'width': data['width'][i],
            'height': data['height'][i]
        }

        # Update line boundaries if this word is on a new line
        if word_box['top'] > current_line_bottom + 5:  # Adjusted threshold for new line
            line_info.append({
                'line_number': line_number,
                'line_bounding_box': line_bounding_box.copy()
            })
            line_number += 1
            current_line_top = word_box['top']
            current_line_bottom = word_box['top'] + word_box['height']
            line_bounding_box = {
                'left': word_box['left'],
                'top': word_box['top'],
                'width': word_box['width'],
                'height': word_box['height']
            }
        else:
            current_line_bottom = max(current_line_bottom, word_box['top'] + word_box['height'])
            line_bounding_box['left'] = min(line_bounding_box['left'], word_box['left'])
            line_bounding_box['width'] = max(line_bounding_box['width'], word_box['left'] + word_box['width'] - line_bounding_box['left'])
            line_bounding_box['height'] = current_line_bottom - current_line_top

    # Append the last line info
    line_info.append({
        'line_number': line_number,
        'line_bounding_box': line_bounding_box.copy()
    })

    output_data = {
        'image_name': image_name,
        'total_lines': line_number + 1,
        'lines': line_info
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"JSON saved at {output_path}")

image_path = '../../data/source_images/W22084/08860015.tif'
output_path = '../../data/ocr_jsonl/extracted_line_info.json'

extract_line_info(image_path, output_path)
