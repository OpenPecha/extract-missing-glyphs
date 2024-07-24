import os
from PIL import Image

def convert_images_to_jpg(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                file_path = os.path.join(root, file)
                output_file_name = f"{os.path.splitext(file)[0]}.jpg"
                output_file_path = os.path.join(output_dir, output_file_name)
                
                with Image.open(file_path) as img:
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        img = img.convert("RGBA")
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    else:
                        img = img.convert("RGB")
                    img.save(output_file_path, format='JPEG')
                print(f"Converted {file_path} to {output_file_path}")

if __name__ == "__main__":
    input_dir = "../../data/opf_images"  
    output_dir = "../../data/opf_converted_source_images"  

    convert_images_to_jpg(input_dir, output_dir)
