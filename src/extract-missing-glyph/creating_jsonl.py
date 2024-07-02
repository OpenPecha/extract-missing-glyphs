import jsonlines
from pathlib import Path
from config import MONLAM_AI_OCR_BUCKET, monlam_ai_ocr_s3_client

s3_client = monlam_ai_ocr_s3_client
bucket_name = MONLAM_AI_OCR_BUCKET


def upload_to_s3_and_return_data(local_path, pub_type, final_jsonl):
    local_directory = Path(local_path)
    files_to_upload = list(local_directory.rglob('*'))
    for image_path in files_to_upload:
        if image_path.is_file():
            relative_path = image_path.relative_to(local_directory)
            s3_key = f"glyph/subjoined_glyphs/{pub_type}/{relative_path}".replace("\\", "/")

            try:
                with open(image_path, "rb") as image_file:
                    s3_client.upload_fileobj(image_file, bucket_name, s3_key)
                print(f"uploaded {relative_path} to {s3_key}")

                text = relative_path.parts[0]
                image_id = image_path.name

                final_jsonl.append({"id": image_id, "image_url": s3_key, "text": text})
            except Exception as e:
                print(f"failed to upload {relative_path}: {e}")

    return final_jsonl


def write_jsonl(final_jsonl, jsonl_path):
    with jsonlines.open(jsonl_path, mode="w") as writer:
        writer.write_all(final_jsonl)
    print(f"jsonl created at {jsonl_path}")


def main():
    pub_type = "derge"
    local_path = Path("../../data/subjoined_glyphs/derge")
    final_jsonl = []

    final_jsonl = upload_to_s3_and_return_data(local_path, pub_type, final_jsonl)
    jsonl_path = Path("../../data/prodigy_jsonl/derge_subjoined_glyphs.jsonl")
    write_jsonl(final_jsonl, jsonl_path)


if __name__ == "__main__":
    main()
