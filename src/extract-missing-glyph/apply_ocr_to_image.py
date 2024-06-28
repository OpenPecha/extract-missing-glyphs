import pytesseract
from pytesseract import Output
import cv2
import json
import os

os.environ['TESSDATA_PREFIX'] = "C:\\Users\\tenka\\tessdata"

def extract_tibetan_text_indices(image_path, output_path):
    image_name = os.path.basename(image_path)
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    custom_config = r'--oem 3 --psm 6 -l bod'
    data = pytesseract.image_to_data(gray, config=custom_config, output_type=Output.DICT)

    extracted_data = []
    n_boxes = len(data['level'])
    unique_index = 0

    for i in range(n_boxes):
        if int(data['conf'][i]) > 0:
            word = data['text'][i]
            word_box = {
                'left': data['left'][i],
                'top': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i]
            }

            if word.strip():
                char_width = word_box['width'] / len(word)
                for j, char in enumerate(word):
                    char_info = {
                        'image_name': image_name,
                        'text': char,
                        'bounding_box': {
                            'left': int(word_box['left'] + j * char_width),
                            'top': word_box['top'],
                            'width': int(char_width),
                            'height': word_box['height']
                        },
                        'index': unique_index
                    }
                    extracted_data.append(char_info)
                    unique_index += 1

                # Add a space if it's not the last word
                if i < n_boxes - 1:
                    space_width = 10 
                    char_info = {
                        'image_name': image_name,
                        'text': ' ',
                        'bounding_box': {
                            'left': int(word_box['left'] + word_box['width']),
                            'top': word_box['top'],
                            'width': space_width,
                            'height': word_box['height']
                        },
                        'index': unique_index
                    }
                    extracted_data.append(char_info)
                    unique_index += 1

    # Add handling for new lines by checking the y-coordinates
    for i in range(n_boxes - 1):
        current_bottom = data['top'][i] + data['height'][i]
        next_top = data['top'][i + 1]
        if next_top > current_bottom + 10:  # Arbitrary threshold for new line
            new_line_info = {
                'image_name': image_name,
                'text': '\n',
                'bounding_box': {
                    'left': 0,
                    'top': current_bottom,
                    'width': 0,
                    'height': next_top - current_bottom
                },
                'index': unique_index
            }
            extracted_data.append(new_line_info)
            unique_index += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in extracted_data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')

    print(f"JSONL saved at {output_path}")

image_path = '../../data/source_images/W22084/08860015.tif'
output_path = '../../data/ocr_jsonl/extracted_text_indices.jsonl'

extract_tibetan_text_indices(image_path, output_path)
