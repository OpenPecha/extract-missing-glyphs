import yaml
import shutil
from pathlib import Path


def read_text(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def read_char(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.readlines()


def load_yaml(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def find_spans(text, characters):
    spans = {char: [] for char in characters}
    for char in characters:
        index = text.find(char)
        while index != -1:
            index = text.find(char, index + 1)
            spans[char].append(index)
        return spans


def check_spans_against_yaml(spans, yaml_data):
    references = {}
    if 'annotations' in yaml_data:
        for char, span_list in spans.items():
            for span in span_list:
                for annotation in yaml_data['annotations'].values():
                    start = annotation['span']['start']
                    end = annotation['span']['end']
                    if start <= span < end:
                        references[annotation['reference']] = char
    return references


def read_missing_glyphs(file_path):
    characters = read_char(file_path)
    return [char.strip() for char in characters]


def find_and_check_spans(base_dir, layers_dir, characters):
    all_spans = {}
    all_references = {}

    for txt_file in base_dir.glob('*.txt'):
        opf_text = read_text(txt_file)
        spans = find_spans(opf_text, characters)
        for char, span_list in spans.items():
            if char not in all_spans:
                all_spans[char] = []
            all_spans[char] += span_list

    for yml_dir in layers_dir.glob('*/'):
        for yml_file in yml_dir.glob('*.yml'):
            if yml_file.name == 'Pagination.yml':
                yaml_data = load_yaml(yml_file)
                references = check_spans_against_yaml(all_spans, yaml_data)
                all_references.update(references)

    return all_references


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


def main():
    base_dir = Path('../../data/opf/P000001.opf/base/v001.txt')
    missing_glyph_txt = Path('../../data/derge_glyphs_missing.txt')
    layers_dir = Path('../../data/opf/P000001.opf/layers/v001')
    image_dir = Path('../../data/source_images/W2KG209989')
    output_dir = Path('../../data/sorted_images')

    characters = read_missing_glyphs(missing_glyph_txt)
    all_references = find_and_check_spans(base_dir, layers_dir, characters)
    copy_images_based_on_references(image_dir, all_references, output_dir)

if __name__ == "__main__":
    main()
