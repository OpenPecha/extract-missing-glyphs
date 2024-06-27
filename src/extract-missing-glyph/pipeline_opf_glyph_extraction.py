import yaml
import json
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


def check_spans_against_yaml(spans, yaml_data, base_index=0):
    references = {char: [] for char in spans.keys()}
    if 'annotations' in yaml_data:
        for char, span_list in spans.items():
            for span in span_list:
                adjusted_span = span + base_index
                for annotation in yaml_data['annotations'].values():
                    start = annotation['span']['start']
                    end = annotation['span']['end']
                    if start <= adjusted_span < end:
                        if annotation['reference'] not in references[char]:
                            references[char].append(annotation['reference'])
    return references


def read_missing_glyphs(file_path):
    characters = read_char(file_path)
    return [char.strip() for char in characters]


def find_and_check_spans(base_dir, layers_dir, characters, meta_data):
    all_spans = []
    text_files = sorted(base_dir.glob('*.txt'))
    yaml_dirs = sorted(layers_dir.glob('*/'))

    for txt_file, yml_dir in zip(text_files, yaml_dirs):
        opf_text = read_text(txt_file)
        spans = find_spans(opf_text, characters)
        base_file_name = txt_file.name
        image_group_id = None
        for volume in meta_data['source_metadata']['volumes'].values():
            if volume['base_file'] == base_file_name:
                image_group_id = volume['image_group_id']
                break

        for char, span_list in spans.items():
            all_spans.append({
                "character": char,
                "text_file": txt_file.name,
                "span": span_list,
                "references": [],
                "image_group_id": image_group_id
            })

        for yml_file in yml_dir.glob('*.yml'):
            if yml_file.name == 'Pagination.yml':
                yaml_data = load_yaml(yml_file)
                references = check_spans_against_yaml(spans, yaml_data)
                for char, ref_list in references.items():
                    for span_dict in all_spans:
                        if span_dict["character"] == char and span_dict["text_file"] == txt_file.name:
                            span_dict["references"] = list(set(span_dict["references"]).union(ref_list))

    return all_spans


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    base_dir = Path('../../data/opf/P000001.opf/base/')
    missing_glyph_txt = Path('../../data/derge_glyphs_missing.txt')
    layers_dir = Path('../../data/opf/P000001.opf/layers/')
    meta_file = Path('../../data/opf/P000001.opf/meta.yml')

    characters = read_missing_glyphs(missing_glyph_txt)
    meta_data = load_yaml(meta_file)
    all_spans = find_and_check_spans(base_dir, layers_dir, characters, meta_data)

    span_path = "../../data/span/span.json"
    save_to_json(all_spans, span_path)


if __name__ == "__main__":
    main()
