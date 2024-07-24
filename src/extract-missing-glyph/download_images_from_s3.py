import hashlib
import csv
import boto3
from pathlib import Path
import json
import re


def get_hash(work_id):
    md5 = hashlib.md5(str.encode(work_id))
    two = md5.hexdigest()[:2]
    return two


def clean_reference_string(reference):
    reference = re.sub(r'([a-zA-Z0-9._]+):', r'"\1":', reference)
    return reference


def download_images_from_s3(csv_file, bucket_name, download_dir):
    s3 = boto3.client('s3')

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        next(reader, None)

        for row in reader:
            work_id = row['work_id']
            image_group_id = row['image_group_id']
            reference_str = row['reference']
            clean_reference_str = clean_reference_string(reference_str)

            try:
                references = json.loads(clean_reference_str)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in reference field: {clean_reference_str}")
                print(f"Error: {e}")
                continue

            if not (image_group_id[2].isalpha() or image_group_id[3].isalpha()):
                image_group_id = image_group_id[1:]

            hash_two = get_hash(work_id)

            for image_filename in references:
                s3_key = f"Works/{hash_two}/{work_id}/images/{work_id}-{image_group_id}/{image_filename}"
                try:
                    download_path = Path(download_dir) / work_id / image_filename
                    download_path.parent.mkdir(parents=True, exist_ok=True)
                    s3.download_file(bucket_name, s3_key, str(download_path))
                    print(f"Downloaded {s3_key} to {download_path}")
                except Exception as e:
                    print(f"Failed to download {s3_key}: {e}")


def main():
    csv_file = "derge_variant_opf_char_mapping.csv"
    bucket_name = "archive.tbrc.org"
    download_dir = "../../data/downloaded_images/derge_opf/variant_images"
    download_images_from_s3(csv_file, bucket_name, download_dir)


if __name__ == "__main__":
    main()
