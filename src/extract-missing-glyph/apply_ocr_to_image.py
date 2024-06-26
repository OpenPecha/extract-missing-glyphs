import pytesseract
from pytesseract import Output
import cv2
import json
import os

os.environ['TESSDATA_PREFIX'] = "C:\\Users\\tenka\\tessdata"

def extract_tibetan_text_indices(image_path, output_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    custom_config = r'--oem 3 --psm 6 -l bod'
    data = pytesseract.image_to_data(gray, config=custom_config, output_type=Output.DICT)

    extracted_data = []
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > 0: 
            word = data['text'][i]
            word_box = {
                'left': data['left'][i],
                'top': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i]
            }
            word_confidence = data['conf'][i]

            if word:  
                char_width = word_box['width'] / len(word)
                for j, char in enumerate(word):
                    char_info = {
                        'text': char,
                        'confidence': word_confidence,
                        'bounding_box': {
                            'left': int(word_box['left'] + j * char_width),
                            'top': word_box['top'],
                            'width': int(char_width),
                            'height': word_box['height']
                        },
                        'index': i
                    }
                    extracted_data.append(char_info)

    json_data = json.dumps(extracted_data, ensure_ascii=False, indent=4)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_data)

    print(f"json saved at {output_path}")

image_path = '../../data/source_images/W2KG209989/I2KG2100520029.jpg'
output_path = '../../data/index_json/extracted_text_indices.json'

extract_tibetan_text_indices(image_path, output_path)
