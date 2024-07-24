import jsonlines
from pathlib import Path
from config import MONLAM_AI_OCR_BUCKET, monlam_ai_ocr_s3_client

s3_client = monlam_ai_ocr_s3_client
bucket_name = MONLAM_AI_OCR_BUCKET


def upload_to_s3_and_return_data(local_path, final_jsonl):
    local_directory = Path(local_path)
    files_to_upload = list(local_directory.rglob('*'))
    for image_path in files_to_upload:
        if image_path.is_file():
            relative_path = image_path.relative_to(local_directory)
            s3_key = f"glyph/derge_opf/batch_1/{relative_path}".replace("\\", "/")

            try:
                with open(image_path, "rb") as image_file:
                    s3_client.upload_fileobj(image_file, bucket_name, s3_key)
                print(f"uploaded {relative_path} to {s3_key}")

                image_id = image_path.name
                text = image_path.stem  

                final_jsonl.append({"id": image_id, "image_url": s3_key, "text": text})
            except Exception as e:
                print(f"failed to upload {relative_path}: {e}")

    return final_jsonl

def write_jsonl(final_jsonl, jsonl_base_path):
    # Calculate split point
    split_index = len(final_jsonl) // 2

    # First half
    jsonl_path_1 = f"{jsonl_base_path}_part1.jsonl"
    with jsonlines.open(jsonl_path_1, mode="w") as writer:
        writer.write_all(final_jsonl[:split_index])
    print(f"jsonl created at {jsonl_path_1}")

    # Second half
    jsonl_path_2 = f"{jsonl_base_path}_part2.jsonl"
    with jsonlines.open(jsonl_path_2, mode="w") as writer:
        writer.write_all(final_jsonl[split_index:])
    print(f"jsonl created at {jsonl_path_2}")


def main():
    local_path = Path(r"C:\Users\tenka\monlam\project\image-cropping-prodigy\data\cropped_images")
    final_jsonl = []

    final_jsonl = upload_to_s3_and_return_data(local_path, final_jsonl)
    jsonl_base_path = "../../data/prodigy_jsonl/derge_opf_glyphs"
    write_jsonl(final_jsonl, jsonl_base_path)


if __name__ == "__main__":
    main()
