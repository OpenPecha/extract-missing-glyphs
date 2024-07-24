import os
import shutil
import re
from collections import defaultdict


def tibetan_char_to_codepoint(char):
    return ord(char)


def read_tibetan_char_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        characters = f.read()
    return [ord(char) for char in characters]


def copy_matching_images(source_dir, target_dir, tibetan_char_codepoints):
    tibetan_char_pattern = re.compile(r'[\u0F00-\u0FFF]')
    copied_images_count = defaultdict(int)
    image_counts = defaultdict(int)

    for filename in os.listdir(source_dir):
        matches = tibetan_char_pattern.findall(filename)
        if matches:
            for char in matches:
                codepoint = tibetan_char_to_codepoint(char)
                if codepoint in tibetan_char_codepoints:
                    if copied_images_count[char] < 10:
                        subdirectory = os.path.join(target_dir, char)
                        if not os.path.exists(subdirectory):
                            os.makedirs(subdirectory)

                        source_file = os.path.join(source_dir, filename)
                        image_counts[char] += 1
                        target_filename = f"{char}_{image_counts[char]}.jpg"
                        target_file = os.path.join(subdirectory, target_filename)
                        shutil.copy2(source_file, target_file)
                        copied_images_count[char] += 1
                        print(f"Copied {filename} to {target_file}")
                    else:
                        print(f"Skipping {filename} for character {char}, limit reached")
                    break


def main():
    source_directory = r"C:\Users\tenka\monlam\project\create-font-from-glyph\data\font_data\derge_font\Derge_test_ten_glyphs\downloaded_images"
    output_glyph_dir = "../../data/subjoined_glyphs/derge"
    input_txt_file = "../../data/subjoined_glyphs.txt"
    output_txt_file = os.path.join(output_glyph_dir, "found_subjoined_glyphs.txt")
    tibetan_codepoints = read_tibetan_char_from_file(input_txt_file)
    copy_matching_images(source_directory, output_glyph_dir, tibetan_codepoints)

    with open(output_txt_file, 'w', encoding='utf-8') as f:
        for subdir, _, files in os.walk(output_glyph_dir):
            for file in files:
                f.write(f"{file}\n")


if __name__ == "__main__":
    main()
