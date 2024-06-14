import codecs

def read_file(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    with codecs.open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def find_common_characters(text1, text2, output_file_path):
    unicode_text1 = [ord(char) for line in text1.splitlines() for char in line.strip()]
    unicode_text2 = [ord(char) for line in text2.splitlines() for char in line.strip()]

    common_unicode = set(unicode_text2).intersection(set(unicode_text1))
    common_characters = ''.join([chr(code) for code in common_unicode])

    with codecs.open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(common_characters)

def main():
    found_glyphs = read_file('../../data/derge_found_glyphs.txt')
    subjoined_glyphs = read_file('../../data/subjoined_glyphs.txt')
    find_common_characters(found_glyphs, subjoined_glyphs, '../../data/common_glyphs.txt')

if __name__ == "__main__":
    main()
