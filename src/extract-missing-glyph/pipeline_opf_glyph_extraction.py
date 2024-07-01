import yaml
import json
from pathlib import Path


def read_text(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def read_char(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [char.strip() for char in file.readlines()]


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
                    start, end = annotation['span']['start'], annotation['span']['end']
                    if start <= adjusted_span < end:
                        if annotation['reference'] not in references[char]:
                            references[char].append(annotation['reference'])
    return references


def find_relative_spans(base_dir, layers_dir, characters, meta_data):
    img_span_data = []
    text_files = sorted(base_dir.glob('*.txt'))
    yaml_dirs = sorted(layers_dir.glob('*/'))

    for txt_file, yml_dir in zip(text_files, yaml_dirs):
        opf_text = read_text(txt_file)
        spans = find_spans(opf_text, characters)
        image_group_id = next((volume['image_group_id'] for volume in meta_data['source_metadata']
                              ['volumes'].values() if volume['base_file'] == txt_file.name), None)

        lines = opf_text.split('\n')
        line_number = 1
        line_break_positions = []
        for i, line in enumerate(lines):
            if line == '' and i > 0 and lines[i-1] == '':
                line_break_positions.append((i, 'image_break'))
            else:
                line_break_positions.append((i, line_number))
                if line != '':
                    line_number += 1
                else:
                    line_number = 1

        for yml_file in yml_dir.glob('Pagination.yml'):
            yaml_data = load_yaml(yml_file)
            for annotation in yaml_data['annotations'].values():
                start, end, reference = annotation['span']['start'], annotation['span']['end'], annotation['reference']
                relative_spans = {char: [] for char in characters}
                for char, span_list in spans.items():
                    for span in span_list:
                        if start <= span < end:
                            relative_span = span - start
                            char_position = 0
                            for position, line_num in line_break_positions:
                                if char_position <= span < char_position + len(lines[position]) + 1:
                                    relative_line_number = 1 if line_num == 'image_break' else line_num
                                    break
                                char_position += len(lines[position]) + 1
                            relative_spans[char].append((relative_span, relative_line_number))
                for char, rel_span_list in relative_spans.items():
                    if rel_span_list:
                        img_span_data.append({
                            "char": char,
                            "txt_file": txt_file.name,
                            "image_group_id": image_group_id,
                            "reference": {reference: rel_span_list}
                        })

    return img_span_data


def save_to_jsonl(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for entry in data:
            file.write(json.dumps(entry, ensure_ascii=False) + '\n')


def main():
    base_dir = Path('../../data/opf/P000001.opf/base/')
    missing_glyph_txt = Path('../../data/derge_glyphs_missing.txt')
    layers_dir = Path('../../data/opf/P000001.opf/layers/')
    meta_file = Path('../../data/opf/P000001.opf/meta.yml')
    jsonl_span_file = Path('../../data/span/img_span.jsonl')  # output file

    characters = read_char(missing_glyph_txt)
    meta_data = load_yaml(meta_file)
    img_span_data = find_relative_spans(base_dir, layers_dir, characters, meta_data)
    save_to_jsonl(img_span_data, jsonl_span_file)


if __name__ == "__main__":
    main()
