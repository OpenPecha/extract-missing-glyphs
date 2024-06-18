import yaml
import shutil
from pathlib import Path

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def read_lines(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.readlines()

def find_spans(text, characters):
    spans = {}
    for char in characters:
        spans[char] = []
        index = text.find(char)
        while index != -1:
            spans[char].append(index)
            index = text.find(char, index + 1)
    return spans

def check_spans_against_yaml(spans, yaml_data):
    references = {}
    for char, span_list in spans.items():
        for span in span_list:
            for annotation in yaml_data['annotations'].values():
                start = annotation['span']['start']
                end = annotation['span']['end']
                if start <= span < end:
                    if annotation['reference'] not in references:
                        references[annotation['reference']] = char
    return references

def load_yaml(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def copy_images_based_on_references(image_dir, references, output_dir):
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for img_name, char in references.items():
        source_img_path = image_dir / img_name
        if source_img_path.exists():
            char_dir = output_dir / char
            char_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(source_img_path, char_dir)
            print(f"copied {img_name} to {char_dir}")

def main():
    opf_txt_path = '../../data/opf/DF8F32338.opf/base/4A8C.txt'
    missing_glyph_txt = '../../data/derge_glyphs_missing.txt'
    yaml_file = '../../data/opf/DF8F32338.opf/layers/4A8C/Pagination.yml'
    image_dir = '../../data/source_images/W2KG209989'
    output_dir = '../../data/sorted_images'

    text1 = read_file(opf_txt_path)
    characters = read_lines(missing_glyph_txt)
    characters = [char.strip() for char in characters]
    yaml_data = load_yaml(yaml_file)

    spans = find_spans(text1, characters)
    references = check_spans_against_yaml(spans, yaml_data)

    copy_images_based_on_references(image_dir, references, output_dir)

if __name__ == "__main__":
    main()
