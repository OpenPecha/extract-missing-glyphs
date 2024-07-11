import io
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from google.cloud import vision
from sklearn.cluster import DBSCAN
import json
import shutil

# Set up the Google Cloud Vision client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\tenka\pecha-ocr-423911-4c5c034b11e4.json"
client = vision.ImageAnnotatorClient()

def detect_vertical_lines(image):
    """Detect vertical lines in the image using Hough Line Transform."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    return lines

def find_vertical_line_bounds(lines, image_width):
    """Find the leftmost and rightmost vertical lines."""
    left_bound = 0
    right_bound = image_width
    if lines is not None:
        x_coords = [line[0][0] for line in lines] + [line[0][2] for line in lines]
        left_bound = max(0, min(x_coords))
        right_bound = min(image_width, max(x_coords))
    return left_bound, right_bound

def crop_image(image, left_bound, right_bound):
    """Crop the image between the left and right bounds."""
    return image[:, left_bound:right_bound]

def detect_text(image_path):
    """Detects text in the file using Google Cloud Vision API."""
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(f'{response.error.message}')

    return response.full_text_annotation

def extract_words(text_annotation):
    """Extracts words and their bounding boxes from the text annotation."""
    words = []
    for page in text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    words.append(word)
    return words

def group_words_by_lines(words, y_threshold=10):
    """Groups words into lines based on their y-coordinates using DBSCAN clustering."""
    if not words:
        print("No words detected.")
        return []

    word_centers = [(word.bounding_box.vertices[0].x, word.bounding_box.vertices[0].y) for word in words]
    y_coordinates = np.array([center[1] for center in word_centers]).reshape(-1, 1)

    dbscan = DBSCAN(eps=y_threshold, min_samples=1)
    clusters = dbscan.fit_predict(y_coordinates)

    lines = [[] for _ in range(max(clusters) + 1)]
    for word, cluster_id in zip(words, clusters):
        lines[cluster_id].append(word)

    return lines

def adjust_bounding_boxes(words, left_bound):
    """Adjust bounding boxes of words to fit the cropped image."""
    for word in words:
        for vertex in word.bounding_box.vertices:
            vertex.x += left_bound
    return words

def save_lines_to_jsonl(image_name, lines, output_path):
    """Saves the lines information to a JSONL file."""
    data = []
    for line_number, line in enumerate(lines, start=1):
        min_x = min([vertex.x for word in line for vertex in word.bounding_box.vertices])
        max_x = max([vertex.x for word in line for vertex in word.bounding_box.vertices])
        min_y = min([vertex.y for word in line for vertex in word.bounding_box.vertices])
        max_y = max([vertex.y for word in line for vertex in word.bounding_box.vertices])

        bounding_box = {
            "left": min_x,
            "top": min_y,
            "width": max_x - min_x,
            "height": max_y - min_y
        }

        data.append({
            "image": image_name,
            "line_number": line_number,
            "bounding_box": bounding_box
        })

    with open(output_path, 'w') as f:
        for entry in data:
            f.write(json.dumps(entry) + '\n')

def main():
    base_dir = '../../data/source_images/derge'
    output_dir = '../../data/ocr_jsonl/'
    temp_dir = 'temp_cropped_image'
    os.makedirs(temp_dir, exist_ok=True)

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
                image_path = os.path.join(root, file)
                image_name = os.path.splitext(os.path.basename(image_path))[0]
                output_filename = f"{image_name}_line_mapping.jsonl"
                output_path = os.path.join(output_dir, output_filename)

                # Check if the JSONL file already exists
                if os.path.exists(output_path):
                    print(f"Skipping {image_name}: JSONL file already exists.")
                    continue

                print(f"Processing image: {image_name}")

                image = cv2.imread(image_path)

                # Detect vertical lines and find bounds
                lines = detect_vertical_lines(image)
                left_bound, right_bound = find_vertical_line_bounds(lines, image.shape[1])

                # Crop the image to the region of interest
                cropped_image = crop_image(image, left_bound, right_bound)
                cropped_image_path = os.path.join(temp_dir, 'cropped_image.jpg')
                cv2.imwrite(cropped_image_path, cropped_image)

                # Detect text in the cropped image
                text_annotation = detect_text(cropped_image_path)
                words = extract_words(text_annotation)

                if not words:
                    print(f"No words detected in image: {image_name}")
                    continue

                words = adjust_bounding_boxes(words, left_bound)  

                lines = group_words_by_lines(words, y_threshold=10)

                save_lines_to_jsonl(image_name, lines, output_path)

    # Clean up: delete the temporary directory
    shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()
