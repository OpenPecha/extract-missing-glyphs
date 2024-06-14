import jsonlines
import csv
from pathlib import Path
import boto3
from config import MONLAM_AI_OCR_BUCKET, monlam_ai_ocr_s3_client

s3_client = monlam_ai_ocr_s3_client
bucket_name = MONLAM_AI_OCR_BUCKET

org_name = "MonlamAI"


def upload_to_s3_and_return_data(local_path, pub_type, final_jsonl, bucket_name):
    done_glyphs = ""
    s3_client = boto3.client('s3')
    local_directory = Path(local_path)

    for image_path in local_directory.iterdir():
        if image_path.is_file():
            filename = image_path.name
            s3_key = f"glyph/subjoined_glyphs/{pub_type}/{filename}"
            s3_url = f"s3://monlam.ai.ocr/{s3_key}"

            with open(image_path, "rb") as image_file:
                s3_client.upload_fileobj(image_file, bucket_name, s3_key)

            final_jsonl.append({"id": filename, "image_url": s3_url, "text": pub_type})
            print(f"{filename} uploaded to S3")

            done_glyphs += filename + "\n"
    print("All files uploaded to S3")
    with open('../data/done_list_for_s3/subjoined_glyphs.txt', 'w', encoding='utf-8') as file:
        file.write(done_glyphs)

    return final_jsonl, done_glyphs


def write_jsonl(final_jsonl, jsonl_path):
    with jsonlines.open(jsonl_path, mode="w") as writer:
        writer.write_all(final_jsonl)
    print(f"JSONL file created at {jsonl_path}")


def get_coordinates(csv_dir, jsonl_path, output_csv_name):
    final_dict = {}
    image_ids = []
    combined_csv_data = []

    with jsonlines.open(jsonl_path) as reader:
        for jsonl in reader:
            image_ids.append(jsonl["id"])

    for csv_path in Path(csv_dir).glob("*.csv"):
        with open(csv_path, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                id = row[0]
                final_dict[id] = row

    for id in image_ids:
        if id in final_dict:
            combined_csv_data.append(final_dict[id])

    output_csv_path = Path(csv_dir) / output_csv_name

    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(combined_csv_data)

    print(f"csv file created at {output_csv_path}")


def main():
    final_jsonl = []
    pub_type = "derge"
    local_path = Path("../data/")

    final_jsonl, _ = upload_to_s3_and_return_data(
        local_path, pub_type, final_jsonl, bucket_name)

    jsonl_path = Path(f"../data/jsonl/subjoined_glyphs.jsonl")
    write_jsonl(final_jsonl, jsonl_path)

    csv_input_path = Path(f"*")  # this should be the path to the csv files
    get_coordinates(csv_input_path, jsonl_path, f"subjoied_glyphs_coordinates.csv")


if __name__ == "__main__":
    main()
