import os
import shutil
import re


def tibetan_char_to_codepoint(char):
    return ord(char)


def read_tibetan_char_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        characters = f.read()
    return [ord(char) for char in characters]


def copy_matching_images(source_dir, target_dir, tibetan_char_codepoints):
    tibetan_char_pattern = re.compile(r'[\u0F00-\u0FFF]')

    for filename in os.listdir(source_dir):
        matches = tibetan_char_pattern.findall(filename)
        if matches:
            for char in matches:
                if tibetan_char_to_codepoint(char) in tibetan_char_codepoints:
                    subdirectory = os.path.join(target_dir, char)
                    if not os.path.exists(subdirectory):
                        os.makedirs(subdirectory)

                    source_file = os.path.join(source_dir, filename)
                    target_file = os.path.join(subdirectory, filename)
                    shutil.copy2(source_file, target_file)
                    print(f"copied {filename} to {subdirectory}")
                    break


def main():
    source_directory = " "
    output_glyph_dir = "../../data/subjoined_glyphs/derge"
    input_txt_file = "../../data/subjoined_glyphs.txt"
    output_txt_file = os.path.join(output_glyph_dir, "found_subjoined_glyphs.txt")
    tibetan_codepoints = read_tibetan_char_from_file(input_txt_file)
    copy_matching_images(source_directory, output_glyph_dir, tibetan_codepoints)

    with open(output_txt_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(output_glyph_dir):
            f.write(f"{filename}\n")


if __name__ == "__main__":
    main()
