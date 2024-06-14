import codecs

def read_file(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    with codecs.open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def convert_to_unicode(text):
    return [ord(char) for line in text.splitlines() for char in line.strip()]

def convert_from_unicode(unicode_list):
    return ''.join([chr(code) for code in unicode_list])

def find_common_characters(text1, text2):
    unicode_text1 = convert_to_unicode(text1)
    unicode_text2 = convert_to_unicode(text2)

    common_unicode = set(unicode_text2).intersection(set(unicode_text1))

    return convert_from_unicode(common_unicode)

def main():
    txt1_content = read_file('../../data/derge_found_glyphs.txt')
    txt2_content = read_file('../../data/subjoined_glyphs.txt')

    common_characters = find_common_characters(txt1_content, txt2_content)
    write_file('common_characters.txt', common_characters)

if __name__ == "__main__":
    main()
