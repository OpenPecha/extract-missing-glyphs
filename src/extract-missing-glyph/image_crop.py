import json
import cv2
import pandas as pd
from pathlib import Path
from PIL import Image


def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]


def load_csv(file_path):
    return pd.read_csv(file_path)


def save_cropped_image(char, count, cropped_image, output_dir):
    char_dir = Path(output_dir) / char
    char_dir.mkdir(parents=True, exist_ok=True)
    output_path = char_dir / f"{char}_{count}.png"

    try:
        pil_image = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
        pil_image.save(str(output_path))
    except Exception as e:
        print(f"Error while saving image: {e}")


def process_image_span_data(image_span_data, image_line_data, img_dir, output_dir, global_char_counter):
    line_data_dict = {
        item['image']: {item['line_number']: item['bounding_box'] for item in image_line_data}
        for item in image_line_data
    }

    for _, span in image_span_data.iterrows():
        char = span['char']
        references = json.loads(span['reference'])

        for image_name_with_ext, lines in references.items():
            image_name = Path(image_name_with_ext).stem
            for _, line_number in lines:
                if image_name in line_data_dict and line_number in line_data_dict[image_name]:
                    bbox = line_data_dict[image_name][line_number]
                    image_path = Path(img_dir) / image_name_with_ext

                    if image_path.exists():
                        image = cv2.imread(str(image_path))
                        if image is not None:
                            print(f"Cropping image: {image_name_with_ext}")
                            left, top, width, height = bbox['left'], bbox['top'], bbox['width'], bbox['height']

                            expanded_height = int(height * 3)
                            top = max(0, top - (expanded_height - height) // 2)
                            height = expanded_height

                            cropped_image = image[top:top + height, left:left + width]

                            resized_image = cv2.resize(
                                cropped_image, (cropped_image.shape[1] * 2, cropped_image.shape[0] * 2), interpolation=cv2.INTER_LINEAR)

                            global_char_counter[char] += 1
                            save_cropped_image(char, global_char_counter[char], resized_image, output_dir)


def process_all_images_and_jsonl(image_span_data_path, jsonl_dir, img_dir, output_dir):
    image_span_data = load_csv(image_span_data_path)

    jsonl_files = list(Path(jsonl_dir).glob('*.jsonl'))
    global_char_counter = {}

    for _, span in image_span_data.iterrows():
        char = span['char']
        if char not in global_char_counter:
            global_char_counter[char] = 0

    for jsonl_file in jsonl_files:
        image_line_data = load_jsonl(jsonl_file)
        for image_subdir in Path(img_dir).iterdir():
            if image_subdir.is_dir():
                process_image_span_data(image_span_data, image_line_data, image_subdir, output_dir, global_char_counter)


def main():
    image_span_data_path = '../../data/mapping_csv/derge_char_mapping.csv'
    jsonl_dir = '../../data/ocr_jsonl'
    img_dir = '../../data/source_images/derge'
    output_dir = '../../data/cropped_images'

    process_all_images_and_jsonl(image_span_data_path, jsonl_dir, img_dir, output_dir)


if __name__ == "__main__":
    main()
