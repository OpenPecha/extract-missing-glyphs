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
            spans[char].append(index)
            index = text.find(char, index + 1)
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


def find_and_check_spans(txt_file, yml_file, characters):
    all_spans = {}
    all_references = {}

    opf_text = read_text(txt_file)
    spans = find_spans(opf_text, characters)
    for char, span_list in spans.items():
        if char not in all_spans:
            all_spans[char] = []
        all_spans[char] += span_list

    yaml_data = load_yaml(yml_file)
    references = check_spans_against_yaml(all_spans, yaml_data)
    all_references.update(references)

    return all_spans, all_references

def main():
    txt_file = Path('../../data/opf/P000800.opf/base/v001.txt')
    missing_glyph_txt = Path('../../data/derge_glyphs_missing.txt')
    yml_file = Path('../../data/opf/P000800.opf/layers/v001/Pagination.yml')

    characters = read_missing_glyphs(missing_glyph_txt)
    all_spans, all_references = find_and_check_spans(txt_file, yml_file, characters)
    
    print("Spans for each character:")
    for char, spans in all_spans.items():
        print(f"Character: {char}, Spans: {spans}")
    
    print("\nReferences based on spans:")
    for ref, char in all_references.items():
        print(f"Reference: {ref}, Character: {char}")


if __name__ == "__main__":
    main()
